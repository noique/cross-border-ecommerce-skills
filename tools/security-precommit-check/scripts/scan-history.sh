#!/bin/bash
# scan-history.sh — scan every blob reachable from any commit, not just the current tree.
#
# Different question from scan.sh --all. A credential committed last month and "removed"
# in a later commit is absent from the working tree and still sits in history, still
# valid until rotated. This is the check that sees it.
#
# Usage:
#   scan-history.sh              # scan this repo's history, exit 1 on any un-allowed hit
#   scan-history.sh --list       # print matching blobs and exit 0 (for triage)
#
# 🔴 Lives here, as a script, and NOT inlined in secret-scan.yml. The first version was
# 60 lines of bash inside a YAML `run:` block, which meant it could only ever be tested
# by pushing and watching CI. Both of the bugs below survived review in that form.

set -uo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RULES="${SECRET_SCAN_RULES:-$SCRIPT_DIR/../rules/default.txt}"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "scan-history.sh: not a git repo" >&2; exit 2; }
ALLOWFILE="$REPO_ROOT/.secret-scan-history-allow.txt"
MODE="${1:-}"
MAXSIZE="${SECRET_SCAN_MAX_BLOB:-1048576}"

[ -f "$RULES" ] || { echo "scan-history.sh: no rules at $RULES" >&2; exit 2; }

# ---------- BLOCK patterns (same parse as scan.sh: SEV first, DESC last) ----------
PATS=$(mktemp); trap 'rm -f "$PATS" "$OBJS" "$BLOBS"' EXIT
n_pat=0
while IFS= read -r line || [ -n "$line" ]; do
  case "$line" in ''|\#*) continue ;; esac
  case "$line" in *"|"*) ;; *) continue ;; esac
  sev="${line%%|*}"; rest="${line#*|}"; dsc="${rest##*|}"
  if [ "$rest" = "$dsc" ]; then pat="$rest"; else pat="${rest%|*}"; fi
  [ "$sev" = "BLOCK" ] || continue
  err=$(printf 'probe' | grep -E -e "$pat" 2>&1 >/dev/null) || true
  if [ -n "$err" ]; then echo "scan-history.sh: dropping invalid rule regex: $pat" >&2; continue; fi
  printf '%s\n' "$pat" >> "$PATS"; n_pat=$((n_pat+1))
done < "$RULES"
# Zero patterns would make every blob "clean" — a green run that proves nothing.
[ "$n_pat" -eq 0 ] && { echo "scan-history.sh: 0 usable BLOCK patterns — refusing to report success" >&2; exit 2; }

# ---------- 🔴 bug 1: the scanner's own fixtures are credential-shaped BY DESIGN ----------
# rules/selftest-samples.txt exists to hold known-positive credential shapes, and
# rules/default.txt spells out the patterns. Scanning them finds them, every single run,
# forever. A gate that is red on its own test fixtures is a gate people learn to ignore.
# So: keep the PATH that `git rev-list --objects` prints (the old version threw it away
# with `awk '{print $1}'`) and skip blobs whose every path is a scanner fixture.
is_fixture() {
  case "$1" in
    */security-precommit-check/rules/*) return 0 ;;
    */security-precommit-check/templates/*) return 0 ;;
    *) return 1 ;;
  esac
}

OBJS=$(mktemp); BLOBS=$(mktemp)
git rev-list --objects --all > "$OBJS"

# blob sha -> is any of its paths a non-fixture path?
awk '{ sha=$1; path=substr($0, length($1)+2); if (path != "") print sha "\t" path }' "$OBJS" \
  | while IFS=$'\t' read -r sha path; do
      if is_fixture "$path"; then printf '%s\tFIXTURE\n' "$sha"; else printf '%s\tREAL\n' "$sha"; fi
    done | sort -u > "$BLOBS"

# ---------- known + reviewed historical leaks ----------
# Format: <blob-sha> <whitespace> # reason. A blob only belongs here after the credential
# has been ROTATED — this file records "we know, it is dead", never "hide it".
declare -a ALLOW_SHAS=() ALLOW_WHY=()
if [ -f "$ALLOWFILE" ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in ''|\#*) continue ;; esac
    sha="${line%%[[:space:]]*}"; why="${line#*#}"
    [ "$why" = "$line" ] && why="(no reason recorded)"
    ALLOW_SHAS+=("$sha"); ALLOW_WHY+=("$why")
  done < "$ALLOWFILE"
fi
allow_idx() { local s="$1" i; for i in "${!ALLOW_SHAS[@]}"; do [ "${ALLOW_SHAS[$i]}" = "$s" ] && { printf '%s' "$i"; return 0; }; done; return 1; }

# ---------- scan ----------
hits=0; skipped_fixture=0; excused=0
declare -a USED_ALLOW=()

while IFS= read -r obj; do
  # a blob referenced ONLY from fixture paths is skipped; if it also lives at a real
  # path, it is scanned (someone copy-pasting a fixture into real code must still fail)
  if ! grep -q "^$obj	REAL$" "$BLOBS" && grep -q "^$obj	FIXTURE$" "$BLOBS"; then
    skipped_fixture=$((skipped_fixture+1)); continue
  fi
  git cat-file -p "$obj" 2>/dev/null | grep -qE -f "$PATS" 2>/dev/null || continue

  if i=$(allow_idx "$obj"); then
    excused=$((excused+1)); USED_ALLOW+=("$obj")
    printf '  ~ %s — reviewed & rotated:%s\n' "${obj:0:12}" "${ALLOW_WHY[$i]}"
    continue
  fi
  paths=$(awk -v s="$obj" '$1==s { print substr($0, length($1)+2) }' "$OBJS" | sort -u | head -3 | tr '\n' ' ')
  echo "::error::secret pattern in historical blob $obj  (paths: ${paths:-unknown})"
  git cat-file -p "$obj" 2>/dev/null | grep -nE -f "$PATS" | head -3 | cut -c1-160 | sed 's/^/      /'
  hits=$((hits+1))
done < <(git cat-file --batch-check='%(objectname) %(objecttype) %(objectsize)' < <(awk '{print $1}' "$OBJS") \
          | awk -v m="$MAXSIZE" '$2=="blob" && $3<m {print $1}')

# ---------- stale allowances ----------
# Same rule as everywhere else in this toolkit: an exemption that no longer matches
# anything is an open hole with an out-of-date excuse attached to it.
stale=0
for i in "${!ALLOW_SHAS[@]}"; do
  found=0
  for u in ${USED_ALLOW[@]+"${USED_ALLOW[@]}"}; do [ "$u" = "${ALLOW_SHAS[$i]}" ] && { found=1; break; }; done
  [ "$found" -eq 0 ] && { echo "  ✗ stale allowance: ${ALLOW_SHAS[$i]} no longer matches — remove it from $(basename "$ALLOWFILE")"; stale=$((stale+1)); }
done

echo
echo "scan-history: $n_pat BLOCK patterns · $hits un-allowed hit(s) · $excused reviewed · $skipped_fixture scanner fixture(s) skipped · $stale stale allowance(s)"

[ "$MODE" = "--list" ] && exit 0

if [ "$hits" -gt 0 ] || [ "$stale" -gt 0 ]; then
  [ "$hits" -gt 0 ] && cat <<'MSG'

🔴 Rotate the credential at the provider FIRST. Cleaning history does not un-leak it —
   the value is already out and stays valid until rotated. Once rotated, record the blob
   in .secret-scan-history-allow.txt with the rotation date so this stays green and the
   next person can see WHY rather than re-investigating it.
MSG
  exit 1
fi
exit 0
