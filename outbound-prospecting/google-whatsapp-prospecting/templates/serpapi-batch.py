#!/usr/bin/env python3
"""
Batch-run a query plan against SerpAPI (or any Google SERP provider with same shape).

Usage:
    SERPAPI_KEY=xxx python3 serpapi-batch.py queries.txt out.csv

queries.txt: one Google query per line. Lines starting with # are ignored.
out.csv:     append-mode CSV with one row per organic result.

Free SerpAPI tier = 100 searches/month. ScraperAPI / SearchAPI / Zenserp use the
same shape; swap the URL + auth header.

This handles the things the article omits:
- Rate limit (1 query / 1.5s) so you don't burn quota on duplicates
- Throws on auth fail rather than silently writing 0 rows
- Skips queries that already ran (resumable)
"""

import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

SERPAPI = "https://serpapi.com/search.json"
KEY = os.environ.get("SERPAPI_KEY")
RATE_DELAY_S = 1.5

if not KEY:
    sys.exit("Set SERPAPI_KEY env var (get one free at serpapi.com).")

if len(sys.argv) != 3:
    sys.exit("Usage: serpapi-batch.py <queries.txt> <out.csv>")

queries_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])

queries = [
    line.strip()
    for line in queries_path.read_text().splitlines()
    if line.strip() and not line.startswith("#")
]

# Resume: skip queries already in out.csv
already = set()
if out_path.exists():
    with out_path.open() as f:
        already = {row["query"] for row in csv.DictReader(f)}

write_header = not out_path.exists()
with out_path.open("a", newline="") as f:
    writer = csv.DictWriter(
        f, fieldnames=["query", "rank", "title", "url", "snippet"]
    )
    if write_header:
        writer.writeheader()

    for q in queries:
        if q in already:
            print(f"[skip-resumed] {q}")
            continue
        params = urllib.parse.urlencode(
            {
                "q": q,
                "engine": "google",
                "num": 30,
                "hl": "en",
                "api_key": KEY,
            }
        )
        url = f"{SERPAPI}?{params}"
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                data = json.loads(r.read())
        except Exception as e:
            print(f"[error] {q}: {e}", file=sys.stderr)
            time.sleep(RATE_DELAY_S * 4)
            continue

        if data.get("error"):
            sys.exit(f"SerpAPI error: {data['error']}")

        results = data.get("organic_results", [])
        for i, r in enumerate(results, 1):
            writer.writerow(
                {
                    "query": q,
                    "rank": i,
                    "title": r.get("title", ""),
                    "url": r.get("link", ""),
                    "snippet": r.get("snippet", ""),
                }
            )
        f.flush()
        print(f"[ok] {q} → {len(results)} results")
        time.sleep(RATE_DELAY_S)

print(f"\nDone. Output: {out_path}")
print("Next step: run extract-numbers.py on the URLs to pull WhatsApp numbers.")
