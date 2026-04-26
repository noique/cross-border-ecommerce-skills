#!/usr/bin/env python3
"""
Pull WhatsApp-shaped phone numbers from a list of URLs and validate against wa.me.

Usage:
    python3 extract-numbers.py serpapi-out.csv leads.csv [--country IN] [--validate]

serpapi-out.csv: produced by serpapi-batch.py
leads.csv:       output, one row per (url, number) pair, deduped on E.164

Steps:
1. Fetch each URL (best-effort; WeChat / LinkedIn / Cloudflare-protected = skipped)
2. Regex-extract candidate phone numbers, normalise to E.164
3. Filter to the target country code if --country given
4. Optional: hit wa.me/<number> and check whether WhatsApp recognises it
   (rate-limited; ~1/2s; expect 5–10% to be CF-blocked)
"""

import argparse
import csv
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# ISO2 → dial code (subset; extend from country-targeting.md as needed)
DIAL = {
    "US": "1", "CA": "1", "MX": "52", "BR": "55", "AR": "54", "CL": "56",
    "CO": "57", "PE": "51", "GB": "44", "DE": "49", "FR": "33", "NL": "31",
    "ES": "34", "IT": "39", "PL": "48", "RU": "7", "TR": "90", "AE": "971",
    "SA": "966", "EG": "20", "IL": "972", "ZA": "27", "NG": "234", "KE": "254",
    "IN": "91", "PK": "92", "BD": "880", "ID": "62", "MY": "60", "PH": "63",
    "TH": "66", "VN": "84", "JP": "81", "KR": "82", "HK": "852", "TW": "886",
    "AU": "61", "NZ": "64",
}

# Common WhatsApp-context tokens — boost candidates that appear near these
WA_TOKENS = re.compile(
    r"whatsapp|wa\.me|wa:|whats app|واتساب|ватсап",
    re.I,
)

# Loose phone candidate: + or 00 + 7–15 digits, with optional spaces/dashes/parens
PHONE_RE = re.compile(
    r"(?:(?<=\D)|^)(\+|00)\s*(\d[\d\s\-\(\)\.]{6,18}\d)(?=\D|$)"
)

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124 Safari/537.36"
)

p = argparse.ArgumentParser()
p.add_argument("input_csv")
p.add_argument("output_csv")
p.add_argument("--country", help="ISO2 (US, IN, BR...) to filter by dial code")
p.add_argument("--validate", action="store_true", help="Hit wa.me to check WhatsApp existence")
args = p.parse_args()

target_dial = DIAL.get(args.country.upper()) if args.country else None
in_path = Path(args.input_csv)
out_path = Path(args.output_csv)


def to_e164(prefix: str, body: str) -> str | None:
    digits = re.sub(r"\D", "", body)
    if not digits:
        return None
    if prefix == "00":
        prefix = "+"
    n = "+" + digits
    # Sanity: E.164 max length 15 digits
    if len(n) - 1 > 15 or len(n) - 1 < 8:
        return None
    return n


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            ct = r.headers.get("Content-Type", "")
            if "text/html" not in ct and "text/plain" not in ct:
                return ""
            data = r.read(2_000_000)
        return data.decode("utf-8", errors="ignore")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return ""


def wa_validate(e164: str) -> str:
    """
    'yes' = wa.me page does not contain the 'invalid' marker
    'no'  = wa.me explicitly says invalid
    'unknown' = couldn't fetch
    """
    num = e164.lstrip("+")
    try:
        req = urllib.request.Request(f"https://wa.me/{num}", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8", errors="ignore")
    except Exception:
        return "unknown"
    if "Phone number shared via url is invalid" in html:
        return "no"
    return "yes"


with in_path.open() as f:
    rows = list(csv.DictReader(f))

seen: set[str] = set()
out_rows = []

for i, row in enumerate(rows, 1):
    url = row.get("url", "")
    if not url:
        continue
    print(f"[{i}/{len(rows)}] {url}", file=sys.stderr)
    html = fetch(url)
    if not html:
        continue

    # Look at full page; if WA tokens absent, lower confidence but still extract
    has_wa = bool(WA_TOKENS.search(html))

    for m in PHONE_RE.finditer(html):
        e164 = to_e164(m.group(1), m.group(2))
        if not e164:
            continue
        if target_dial and not e164.startswith("+" + target_dial):
            continue
        key = e164
        if key in seen:
            continue
        seen.add(key)

        wa_status = ""
        if args.validate:
            wa_status = wa_validate(e164)
            time.sleep(2.0)  # rate limit on wa.me

        out_rows.append(
            {
                "source_url": url,
                "source_query": row.get("query", ""),
                "raw_match": m.group(0).strip(),
                "e164_phone": e164,
                "wa_token_on_page": "yes" if has_wa else "no",
                "wa_validated": wa_status,
            }
        )

with out_path.open("w", newline="") as f:
    w = csv.DictWriter(
        f,
        fieldnames=[
            "source_url",
            "source_query",
            "raw_match",
            "e164_phone",
            "wa_token_on_page",
            "wa_validated",
        ],
    )
    w.writeheader()
    w.writerows(out_rows)

print(f"\nExtracted {len(out_rows)} unique numbers → {out_path}", file=sys.stderr)
print(
    "Next: import into lead-tracker.csv, enrich (company / role / language), "
    "then write outreach per templates/outreach-playbook.md",
    file=sys.stderr,
)
