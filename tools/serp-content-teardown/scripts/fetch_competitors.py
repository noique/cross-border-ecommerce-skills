#!/usr/bin/env python3
"""Fetch competitor blog/info HTML with curl + a realistic browser UA.

Reads url_pool.json (from parse_serp.py), selects which URLs to fetch
(auto top-N capped per domain, or an explicit --select file), downloads each
with curl, detects anti-bot blocks and SKIPS+LOGS them, and writes the raw HTML
to <out-dir>/html/ plus a fetch_manifest.json.

RED LINE: fetching uses curl ONLY. No paid APIs (Ahrefs / Apify / Tavily / Jina /
OpenRouter / ScrapingBee / etc.). curl with a browser UA is the only allowed
network access in this toolkit.

Usage:
    python3 fetch_competitors.py --out-dir DIR [--top 30] [--select FILE]

Arguments:
    --out-dir   Dir containing url_pool.json; html/ + fetch_manifest.json written here
    --top       Auto-select this many top-ranked URLs (default: 30), capped 2/domain
    --select    Optional file: one path-fragment per line to fetch instead of auto.
                A fragment may be 'domain.com|/path/frag' to pin a domain, or just
                a substring matched against (domain + path). Lines starting with #
                are comments. Overrides --top.
"""
import argparse
import hashlib  # noqa: F401  (kept for parity / optional future slug hashing)
import json
import os
import re
import subprocess
import sys

# Realistic desktop Chrome UA — many Shopify/CDN edges 403 a bare curl UA.
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

# anti-bot / challenge-page fingerprints (lowercased substring match on head)
CF_MARKERS = ("just a moment", "cf-browser-verification", "cf_chl_opt",
              "attention required", "enable javascript and cookies",
              "checking your browser", "px-captcha", "access denied",
              "request unsuccessful", "incapsula", "captcha")

PER_DOMAIN_CAP = 2  # diversity: at most N articles per domain in auto-select


def slugify(dom, path):
    s = (dom + path).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:80]


def pick(pool, frag):
    """Resolve one --select fragment to a pool record (first match)."""
    dom_filter = None
    if "|" in frag:
        dom_filter, frag = frag.split("|", 1)
    for r in pool:
        if dom_filter and r["domain"] != dom_filter:
            continue
        if frag.lower() in (r["domain"] + r["path"]).lower():
            return r
    return None


def auto_select(pool, top, cap):
    """Take the top-ranked records (pool is pre-sorted), capping per domain."""
    chosen, per_dom = [], {}
    for r in pool:
        d = r["domain"]
        if per_dom.get(d, 0) >= cap:
            continue
        per_dom[d] = per_dom.get(d, 0) + 1
        chosen.append(r)
        if len(chosen) >= top:
            break
    return chosen


def load_select_file(path, pool):
    records, missing = [], []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            frag = line.strip()
            if not frag or frag.startswith("#"):
                continue
            r = pick(pool, frag)
            if r:
                records.append(r)
            else:
                missing.append(frag)
    for frag in missing:
        print("NO MATCH:", frag)
    return records


def fetch_one(url, out_path):
    """curl: browser UA, follow redirects, gzip, ~25s. Returns (http_code, nbytes, body)."""
    cmd = ["curl", "-sSL", "--compressed", "--max-time", "25",
           "-A", UA,
           "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "-H", "Accept-Language: en-US,en;q=0.9",
           "-H", "Referer: https://www.google.com/",
           "-o", out_path, "-w", "%{http_code}", url]
    try:
        code = subprocess.run(cmd, capture_output=True, text=True, timeout=40).stdout.strip()
    except Exception as e:
        code = "ERR:" + str(e)[:40]
    body, nbytes = "", 0
    if os.path.exists(out_path):
        nbytes = os.path.getsize(out_path)
        try:
            body = open(out_path, "r", errors="ignore").read()
        except Exception:
            body = ""
    return code, nbytes, body


def main():
    ap = argparse.ArgumentParser(
        description="Fetch competitor HTML with curl + browser UA (no paid APIs)")
    ap.add_argument("--out-dir", required=True,
                    help="Dir with url_pool.json; writes html/ + fetch_manifest.json")
    ap.add_argument("--top", type=int, default=30,
                    help="Auto-select N top URLs, capped 2/domain (default: 30)")
    ap.add_argument("--select", metavar="FILE",
                    help="File of path-fragments (one per line) to fetch instead of auto")
    args = ap.parse_args()

    pool_path = os.path.join(args.out_dir, "url_pool.json")
    pool = json.load(open(pool_path, encoding="utf-8"))
    html_dir = os.path.join(args.out_dir, "html")
    os.makedirs(html_dir, exist_ok=True)

    if args.select:
        records = load_select_file(args.select, pool)
        print(f"select-file: {len(records)} URLs resolved from {args.select}")
    else:
        records = auto_select(pool, args.top, PER_DOMAIN_CAP)
        print(f"auto-select: top {args.top} (cap {PER_DOMAIN_CAP}/domain) -> {len(records)} URLs")

    manifest, seen = [], set()
    for r in records:
        key = (r["domain"], r["path"])
        if key in seen:
            continue
        seen.add(key)
        slug = slugify(r["domain"], r["path"])
        out = os.path.join(html_dir, slug + ".html")
        url = r["url"]
        code, nbytes, body = fetch_one(url, out)
        low = body[:6000].lower()
        blocked = (not code.startswith("2")) or nbytes < 1500 or any(m in low for m in CF_MARKERS)
        rec = {
            "slug": slug, "domain": r["domain"], "url": url, "category": r["category"],
            "matched_keywords": r["matched_keywords"], "info_topic_hits": r["info_topic_hits"],
            "us_min_pos": r["us_min_pos"], "all_min_pos": r["all_min_pos"], "avg_pos": r["avg_pos"],
            "http_code": code, "bytes": nbytes, "ok": (not blocked),
        }
        manifest.append(rec)
        flag = "OK " if not blocked else "BLOCK"
        print(f"{flag} {code:>4} {nbytes:>8}B  {r['domain']:<26} "
              f"us#{str(r['us_min_pos'] or '-'):<3} {r['path'][:46]}")

    man_path = os.path.join(args.out_dir, "fetch_manifest.json")
    json.dump(manifest, open(man_path, "w", encoding="utf-8"), indent=2)
    ok = sum(1 for m in manifest if m["ok"])
    print(f"\nselected={len(manifest)}  ok={ok}  blocked={len(manifest)-ok} -> {man_path}")


if __name__ == "__main__":
    main()
