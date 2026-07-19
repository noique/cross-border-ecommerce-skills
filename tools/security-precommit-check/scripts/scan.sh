#!/bin/bash
# scan.sh — Security pre-commit scanner.
#
# Scans target files against rule files (universal default + per-repo custom)
# and reports BLOCK / WARN matches. Exits non-zero if any BLOCK match found
# (rejects commit when invoked from .git/hooks/pre-commit).
#
# Usage:
#   scan.sh                        # scan staged files (default; use from git hook)
#   scan.sh --staged               # same as above
#   scan.sh --all                  # scan all tracked files
#   scan.sh --files PATH [PATH...] # scan specific files
#
# Rules format (rules/default.txt + .security-precommit-rules.txt):
#   SEVERITY|PATTERN|DESCRIPTION
#   SEVERITY: BLOCK or WARN
#   PATTERN: extended-regex (passed to grep -E)
#   Lines starting with # are comments.

set -uo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEFAULT_RULES="$SCRIPT_DIR/../rules/default.txt"

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
PROJECT_RULES="$REPO_ROOT/.security-precommit-rules.txt"

# -------------------- determine target files --------------------

# 🔴 File lists are read NUL-separated into an array. An earlier version used an
# unquoted `for f in $FILES`, which word-split any path containing a space into
# non-existent fragments; those silently failed the -f test and the file was never
# scanned — a secret in "my file.txt" passed the gate with exit 0. Demonstrated, not
# theoretical: this repo set contains paths like "建站 skill" and
# "kristikay-diary GitHub Actions deploy API .txt".
MODE="${1:---staged}"
FILES=()
case "$MODE" in
  --staged)
    while IFS= read -r -d '' f; do FILES+=("$f"); done \
      < <(git diff --cached --name-only --diff-filter=ACM -z 2>/dev/null) ;;
  --all)
    while IFS= read -r -d '' f; do FILES+=("$f"); done \
      < <(git ls-files -z 2>/dev/null) ;;
  --files)
    shift
    FILES=("$@") ;;
  *)
    echo "scan.sh: unknown mode '$MODE' (expected --staged | --all | --files PATH...)" >&2
    exit 2 ;;
esac

if [ ${#FILES[@]} -eq 0 ]; then
  exit 0
fi

# -------------------- collect rules --------------------

RULE_FILES=()
[ -f "$DEFAULT_RULES" ] && RULE_FILES+=("$DEFAULT_RULES")
[ -f "$PROJECT_RULES" ] && RULE_FILES+=("$PROJECT_RULES")

if [ ${#RULE_FILES[@]} -eq 0 ]; then
  echo "scan.sh: no rule files found (looked at $DEFAULT_RULES and $PROJECT_RULES)" >&2
  exit 2
fi

# -------------------- scan --------------------
#
# 🔴 Performance note. The original shape was `for rule; do for file; do file+grep`,
# i.e. one `file(1)` and one `grep(1)` subprocess per (rule × file) pair. Measured at
# 540 ms/file — kristikay-diary (1775 tracked files × 33 rules) would have taken ~16
# minutes, so --all and any CI use were effectively impossible.
#
# Restructured to: filter the file list ONCE, then run ONE grep per severity over all
# files at once (`grep -nE -f patterns -- file...`). Rule attribution happens only on
# the handful of lines that actually matched. Same rules, same output, same exit codes.

ISSUES_BLOCK=()
ISSUES_WARN=()

# --- 1. filter the file list once (binary / self / rules-file exclusions) ---
SAFE=()
for f in "${FILES[@]}"; do
  [ -f "$f" ] || continue
  case "$f" in *"security-precommit-check/"*) continue ;; esac
  [ "$(basename "$f")" = ".security-precommit-rules.txt" ] && continue
  # binary check runs ONCE per file now, not once per (rule × file)
  case "$(file --brief --mime "$f" 2>/dev/null)" in *charset=binary*) continue ;; esac
  SAFE+=("$f")
done
[ ${#SAFE[@]} -eq 0 ] && exit 0

# --- 2. load rules into parallel arrays ---
#
# 🔴 Rule format is SEV|PATTERN|DESC, but several PATTERNS legitimately contain `|`
# (alternation). Splitting on field 2 truncated them — e.g. one rule was being read as
# the fragment `sk-(?!ant-\` . So: SEV is the FIRST field, DESC is the LAST field, and
# PATTERN is everything in between, rejoined.
#
# 🔴 Every pattern is then VALIDATED. Combining patterns into one `grep -f` file means a
# single invalid regex makes grep exit 2 and print nothing — the whole scan silently
# passes. That is a fail-open, so a bad rule is dropped loudly instead of taken on trust.
SEVS=(); PATS=(); DESCS=(); DROPPED=0
for rule_file in "${RULE_FILES[@]}"; do
  while IFS= read -r line || [ -n "$line" ]; do
    [ -z "$line" ] && continue
    case "$line" in \#*) continue ;; esac
    case "$line" in *"|"*) ;; *) continue ;; esac

    sev="${line%%|*}"                 # first field
    rest="${line#*|}"                 # everything after it
    dsc="${rest##*|}"                 # last field
    if [ "$rest" = "$dsc" ]; then pat="$rest"; dsc=""; else pat="${rest%|*}"; fi

    [ -z "$pat" ] && continue
    [ "$sev" != "BLOCK" ] && [ "$sev" != "WARN" ] && continue

    # Valid patterns simply do not match the probe (exit 1, no stderr).
    # An invalid regex writes to stderr — that is the only reliable signal.
    rx_err=$(printf 'probe' | grep -E -e "$pat" 2>&1 >/dev/null)
    if [ -n "$rx_err" ]; then
      printf 'scan.sh: WARNING dropping invalid rule regex: %s\n' "$pat" >&2
      DROPPED=$((DROPPED+1)); continue
    fi
    SEVS+=("$sev"); PATS+=("$pat"); DESCS+=("${dsc:-unnamed rule}")
  done < "$rule_file"
done
[ ${#PATS[@]} -eq 0 ] && { echo "scan.sh: no usable rules" >&2; exit 2; }
[ "$DROPPED" -gt 0 ] && printf 'scan.sh: %d invalid rule(s) dropped — fix them, they are scanning nothing.\n' "$DROPPED" >&2

TMPD=$(mktemp -d); trap 'rm -rf "$TMPD"' EXIT
: > "$TMPD/block.pat"; : > "$TMPD/warn.pat"
for idx in "${!PATS[@]}"; do
  if [ "${SEVS[$idx]}" = "BLOCK" ]; then printf '%s\n' "${PATS[$idx]}" >> "$TMPD/block.pat"
  else printf '%s\n' "${PATS[$idx]}" >> "$TMPD/warn.pat"; fi
done

# --- 3. one grep pass per severity across ALL files ---
# attribute() finds which rule a matched line belongs to — only runs on real hits.
attribute() {
  local want_sev="$1" text="$2" k
  for k in "${!PATS[@]}"; do
    [ "${SEVS[$k]}" = "$want_sev" ] || continue
    if printf '%s' "$text" | grep -qE -e "${PATS[$k]}" 2>/dev/null; then
      printf '%s' "${DESCS[$k]}"; return
    fi
  done
  printf 'unclassified'
}

scan_severity() {
  local sev="$1" patfile="$2" line loc text desc
  [ -s "$patfile" ] || return 0
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    loc=$(printf '%s' "$line" | cut -d: -f1,2)
    text=$(printf '%s' "$line" | cut -d: -f3-)
    desc=$(attribute "$sev" "$text")
    local entry="$loc:$(printf '%s' "$text" | cut -c1-180)  ← [$desc]"
    if [ "$sev" = "BLOCK" ]; then ISSUES_BLOCK+=("$entry"); else ISSUES_WARN+=("$entry"); fi
  done < <(printf '%s\0' "${SAFE[@]}" | xargs -0 grep -nHE -f "$patfile" -- 2>/dev/null || true)
}

scan_severity BLOCK "$TMPD/block.pat"
scan_severity WARN  "$TMPD/warn.pat"

# -------------------- report --------------------

if [ ${#ISSUES_WARN[@]} -gt 0 ]; then
  echo
  echo "[WARN] ${#ISSUES_WARN[@]} project-specific keyword match(es):"
  for entry in "${ISSUES_WARN[@]}"; do
    echo "  $entry"
  done
fi

if [ ${#ISSUES_BLOCK[@]} -gt 0 ]; then
  echo
  echo "[BLOCK] ${#ISSUES_BLOCK[@]} potential secret/credential match(es):"
  for entry in "${ISSUES_BLOCK[@]}"; do
    echo "  $entry"
  done
  echo
  echo "Commit blocked. Fix the issues above, OR bypass intentionally with:"
  echo "  git commit --no-verify"
  exit 1
fi

if [ ${#ISSUES_WARN[@]} -gt 0 ]; then
  echo
  echo "Warnings only (non-blocking). Use --no-verify to skip warnings entirely."
fi

exit 0
