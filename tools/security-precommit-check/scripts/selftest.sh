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
# Usage: scripts/selftest.sh          # exits 0 when every rule is alive, 1 otherwise
#
# Parsing below MIRRORS scan.sh exactly (SEV = first field, DESC = last field, PATTERN =
# everything between). If scan.sh's parser changes, change it here too — a selftest that
# parses differently from the scanner is testing a fiction.

set -uo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RULES="$SCRIPT_DIR/../rules/default.txt"
SAMPLES="$SCRIPT_DIR/../rules/selftest-samples.txt"

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
while IFS= read -r line || [ -n "$line" ]; do
  [ -z "$line" ] && continue
  case "$line" in \#*) continue ;; *"|"*) ;; *) continue ;; esac
  S_DESCS+=("${line%%|*}")
  S_VALS+=("$(expand "${line#*|}")")
done < "$SAMPLES"

sample_for() {           # echo the sample for a description, empty if none
  local want="$1" i
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

echo
if [ "$FAIL" -gt 0 ]; then
  printf 'selftest: %d passed · %d FAILED — a failing rule scans nothing; fix it or the gate is theatre.\n' "$PASS" "$FAIL"
  exit 1
fi
printf 'selftest: ✅ %d checks passed — every rule fires on its positive control.\n' "$PASS"
exit 0
