#!/bin/bash
# selftest.sh — assert every rule in rules/default.txt actually SCANS SOMETHING.
#
# Why this exists: the scanner fails OPEN, and it does so in two ways.
#   1. LOUD  — an invalid regex is dropped with a warning (scan.sh already prints it).
#   2. SILENT — a regex that is perfectly VALID but matches nothing. `\|` inside a group
#      is a LITERAL pipe in ERE, not alternation, so `(api[_-]?key\|secret[_-]?key)` only
#      ever matched the text "api_key|secret_key". The rule sat in the file looking like
#      coverage while scanning nothing, with no warning of any kind. That is the failure
#      mode this file exists to catch: a rule is only real if it fires on a known positive.
#
# Usage: scripts/selftest.sh                    # default.txt + THIS repo's per-repo rules
#        scripts/selftest.sh RULES_FILE...      # also check the given per-repo rule files
#
# 🔴 Per-repo rules (.security-precommit-rules.txt) are checked too, and by default, because
# scan.sh loads them with exactly the same weight as the defaults — a dead rule there is just
# as blind. They are held to a WEAKER standard on purpose: two of these repos are public, and
# a positive control for "known-leaked proxy password" or "founder's real name" would mean
# committing the very string the rule exists to keep out. So per-repo rules get regex validity
# + the dead-alternation lint + the benign negative controls, and get the full positive-control
# check only for those descriptions a companion .security-precommit-samples.txt covers.
#
# Parsing below MIRRORS scan.sh exactly (SEV = first field, DESC = last field, PATTERN =
# everything between). If scan.sh's parser changes, change it here too — a selftest that
# parses differently from the scanner is testing a fiction.

set -uo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RULES="$SCRIPT_DIR/../rules/default.txt"
SAMPLES="$SCRIPT_DIR/../rules/selftest-samples.txt"

# Same discovery scan.sh does, so selftest sees the same rule set the scanner will.
REPO_ROOT="$(cd "$SCRIPT_DIR" && git rev-parse --show-toplevel 2>/dev/null || true)"
EXTRA_RULES=()
[ -n "$REPO_ROOT" ] && [ -f "$REPO_ROOT/.security-precommit-rules.txt" ] \
  && EXTRA_RULES+=("$REPO_ROOT/.security-precommit-rules.txt")
for arg in "$@"; do
  [ -f "$arg" ] || { echo "selftest: no such rules file: $arg" >&2; exit 2; }
  EXTRA_RULES+=("$arg")
done

for f in "$RULES" "$SAMPLES"; do
  [ -f "$f" ] || { echo "selftest: missing $f" >&2; exit 2; }
done

# Samples store repeated bodies as <REP:c:n> so no credential-shaped literal sits in the
# file (GitHub push protection blocks those on sight — see the samples-file header).
# Expansion happens HERE, at match time, so the rules are still tested against the real shape.
rep() { printf "%${2}s" '' | tr ' ' "$1"; }
expand() {
  local s="$1" out="" pre rest rest2 c n
  while case "$s" in *"<REP:"*) true ;; *) false ;; esac; do
    pre="${s%%<REP:*}"; rest="${s#*<REP:}"
    c="${rest%%:*}"; rest2="${rest#*:}"; n="${rest2%%>*}"; s="${rest2#*>}"
    out="$out$pre$(rep "$c" "$n")"
  done
  printf '%s%s' "$out" "$s"
}

# bash 3.2 (macOS default) has no associative arrays → parallel arrays, like scan.sh.
S_DESCS=(); S_VALS=()
load_samples() {          # replaces the sample table; empty/absent file = no samples
  S_DESCS=(); S_VALS=()
  [ -f "${1:-}" ] || return 0
  local line
  while IFS= read -r line || [ -n "$line" ]; do
    [ -z "$line" ] && continue
    case "$line" in \#*) continue ;; *"|"*) ;; *) continue ;; esac
    S_DESCS+=("${line%%|*}")
    S_VALS+=("$(expand "${line#*|}")")
  done < "$1"
}
load_samples "$SAMPLES"

sample_for() {           # echo the sample for a description, empty if none
  local want="$1" i
  [ ${#S_DESCS[@]} -eq 0 ] && return 1     # set -u: ${!arr[@]} on an empty array aborts
  for i in "${!S_DESCS[@]}"; do
    [ "${S_DESCS[$i]}" = "$want" ] && { printf '%s' "${S_VALS[$i]}"; return 0; }
  done
  return 1
}

PASS=0; FAIL=0; SEEN_DESCS=()
fail() { printf '  ✗ %s\n' "$1"; FAIL=$((FAIL+1)); }
pass() { PASS=$((PASS+1)); }

echo "selftest: every rule in rules/default.txt must fire on a known-positive sample"
echo

# ---------- 1. every rule: valid regex + has a sample + matches it ----------
while IFS= read -r line || [ -n "$line" ]; do
  [ -z "$line" ] && continue
  case "$line" in \#*) continue ;; *"|"*) ;; *) continue ;; esac

  sev="${line%%|*}"; rest="${line#*|}"; dsc="${rest##*|}"
  if [ "$rest" = "$dsc" ]; then pat="$rest"; dsc=""; else pat="${rest%|*}"; fi
  [ -z "$pat" ] && continue
  [ "$sev" != "BLOCK" ] && [ "$sev" != "WARN" ] && continue

  SEEN_DESCS+=("$dsc")

  # (a) regex must be valid — same probe scan.sh uses to drop rules
  rx_err=$(printf 'probe' | grep -E -e "$pat" 2>&1 >/dev/null)
  if [ -n "$rx_err" ]; then fail "[$sev] $dsc — INVALID REGEX (scan.sh drops it): $pat"; continue; fi

  # (b) must have a positive control
  if ! smp=$(sample_for "$dsc"); then
    fail "[$sev] $dsc — no positive control in $(basename "$SAMPLES") (add one: DESCRIPTION|SAMPLE)"
    continue
  fi

  # (c) the rule must actually match it — this is what catches the silent-dead class
  if printf '%s' "$smp" | grep -qE -e "$pat" 2>/dev/null; then pass
  else fail "[$sev] $dsc — DEAD: valid regex that does not match its own sample"; fi
done < "$RULES"

# ---------- 2. stale samples (a rule was renamed/removed) ----------
for i in "${!S_DESCS[@]}"; do
  found=0
  for d in "${SEEN_DESCS[@]}"; do [ "$d" = "${S_DESCS[$i]}" ] && { found=1; break; }; done
  [ "$found" -eq 0 ] && fail "sample '${S_DESCS[$i]}' matches no rule — stale, rename or drop it"
done

# ---------- 3. negative controls: benign lines must trip NO block rule ----------
# Guards the other direction: an over-broad rule that blocks ordinary code is a rule people
# will start bypassing with --no-verify, which costs more than it saves.
BENIGN=(
  'const apiKey = process.env.OPENAI_API_KEY;'
  'password = os.environ["DB_PASSWORD"]'
  'https://github.com/noique/theme-to-astro-clone.git'
  'import { spawn } from "node:child_process";'
  'dGhpcyBpcyBqdXN0IGJhc2U2NCBkYXRhIGZvciB0ZXN0aW5nIHB1cnBvc2Vz'
  'See the docs for sk- style keys and how to rotate them.'
)
while IFS= read -r line || [ -n "$line" ]; do
  [ -z "$line" ] && continue
  case "$line" in \#*) continue ;; *"|"*) ;; *) continue ;; esac
  sev="${line%%|*}"; [ "$sev" = "BLOCK" ] || continue
  rest="${line#*|}"; dsc="${rest##*|}"
  if [ "$rest" = "$dsc" ]; then pat="$rest"; else pat="${rest%|*}"; fi
  printf 'probe' | grep -E -e "$pat" >/dev/null 2>&1
  [ $? -gt 1 ] && continue                      # invalid regex already reported above
  for b in "${BENIGN[@]}"; do
    if printf '%s' "$b" | grep -qE -e "$pat" 2>/dev/null; then
      fail "[BLOCK] $dsc — FALSE POSITIVE on benign line: $b"
    fi
  done
done < "$RULES"

# ---------- 4. the vendor-prefix rules must not shadow each other ----------
# Regression for the generic sk- rule: it is deliberately written WITHOUT a negative
# lookahead (ERE has none), relying on `-` being outside [a-zA-Z0-9] to skip sk-ant- /
# sk-proj- keys, which own dedicated rules. If someone "fixes" it to sk-[A-Za-z0-9_-]{40,}
# every Anthropic key would report twice under the wrong name.
GENERIC_SK=$(grep -E '^BLOCK\|sk-\[' "$RULES" | head -1)
if [ -n "$GENERIC_SK" ]; then
  rest="${GENERIC_SK#*|}"; gpat="${rest%|*}"
  for d in "Anthropic API key" "OpenAI project API key"; do
    if smp=$(sample_for "$d"); then
      if printf '%s' "$smp" | grep -qE -e "$gpat" 2>/dev/null; then
        fail "generic sk- rule also matches the $d sample — it should leave that to the dedicated rule"
      else pass; fi
    fi
  done
fi

# ---------- 5. per-repo rule files (.security-precommit-rules.txt) ----------
# scan.sh gives these the same weight as the defaults, so they get checked too. Weaker
# standard, for the reason in the header: some positive controls cannot exist in a public
# repo. What IS enforced everywhere: valid regex, no dead alternation, no benign false
# positive. Rules with no positive control are counted and reported as UNPROVEN, never
# silently folded into the pass count — an unproven rule is not a passing rule.
UNPROVEN=0
if [ ${#EXTRA_RULES[@]} -gt 0 ]; then
  for rf in "${EXTRA_RULES[@]}"; do
    echo "per-repo rules: $rf"
    load_samples "${rf%.txt}"".samples.txt"   # .security-precommit-rules.samples.txt
    [ ${#S_DESCS[@]} -eq 0 ] && load_samples "$(dirname "$rf")/.security-precommit-samples.txt"

    while IFS= read -r line || [ -n "$line" ]; do
      [ -z "$line" ] && continue
      case "$line" in \#*) continue ;; *"|"*) ;; *) continue ;; esac

      sev="${line%%|*}"; rest="${line#*|}"; dsc="${rest##*|}"
      if [ "$rest" = "$dsc" ]; then pat="$rest"; dsc=""; else pat="${rest%|*}"; fi
      [ -z "$pat" ] && continue
      [ "$sev" != "BLOCK" ] && [ "$sev" != "WARN" ] && continue

      # (a) valid regex — scan.sh would drop it loudly
      rx_err=$(printf 'probe' | grep -E -e "$pat" 2>&1 >/dev/null)
      if [ -n "$rx_err" ]; then fail "[$sev] $dsc — INVALID REGEX (scan.sh drops it): $pat"; continue; fi

      # (b) dead alternation — the exact bug that shipped here. `\|` is a LITERAL pipe in
      #     ERE, so (a\|b) matches only the text "a|b". Valid regex, zero coverage, silent.
      #     A bare `|` parses fine (SEV is first field, DESC is last); for a genuine literal
      #     pipe write [|], which is unambiguous.
      case "$pat" in
        *'\|'*) fail "[$sev] $dsc — DEAD ALTERNATION: \\| is a literal pipe in ERE, so this only matches the text with a pipe in it. Use (a|b), or [|] for a real literal pipe: $pat"
                continue ;;
      esac

      # (c) BLOCK rules must not fire on ordinary code
      if [ "$sev" = "BLOCK" ]; then
        for b in "${BENIGN[@]}"; do
          printf '%s' "$b" | grep -qE -e "$pat" 2>/dev/null \
            && fail "[BLOCK] $dsc — FALSE POSITIVE on benign line: $b"
        done
      fi

      # (d) positive control when one exists.
      #     🔴 Per-repo descriptions are NOT unique — this file has 9 rules all described
      #     "Competitor brand name". Keying on the FIRST sample with that description would
      #     test all 9 against one brand and report the other 8 dead. So the rule passes if
      #     it fires on ANY sample carrying its description; a genuinely dead rule (typo'd
      #     pattern) still matches none of them and is still caught.
      hit=0; have=0
      if [ ${#S_DESCS[@]} -gt 0 ]; then
        for si in "${!S_DESCS[@]}"; do
          [ "${S_DESCS[$si]}" = "$dsc" ] || continue
          have=1
          printf '%s' "${S_VALS[$si]}" | grep -qE -e "$pat" 2>/dev/null && { hit=1; break; }
        done
      fi
      if [ "$have" -eq 0 ]; then UNPROVEN=$((UNPROVEN+1))
      elif [ "$hit" -eq 1 ]; then pass
      else fail "[$sev] $dsc — DEAD: valid regex, matches no sample carrying its description: $pat"; fi
    done < "$rf"
  done
  echo
fi

echo
if [ "$UNPROVEN" -gt 0 ]; then
  printf 'selftest: ⚠ %d per-repo rule(s) have no positive control — checked for validity, NOT proven to fire.\n' "$UNPROVEN"
  printf '          Add controls in .security-precommit-samples.txt (DESCRIPTION|SAMPLE) for any whose sample is safe to store.\n'
fi
if [ "$FAIL" -gt 0 ]; then
  printf 'selftest: %d passed · %d FAILED — a failing rule scans nothing; fix it or the gate is theatre.\n' "$PASS" "$FAIL"
  exit 1
fi
printf 'selftest: ✅ %d checks passed — every rule fires on its positive control.\n' "$PASS"
exit 0
