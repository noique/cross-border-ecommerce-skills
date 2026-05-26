#!/usr/bin/env python3
"""GEO / AI-Overview analysis: who gets AI-cited + schema readiness of the cohort.

Reads keywords.json + classified.json from --out-dir and the SEMrush
``*serp_urls*us*.xlsx`` files in --semrush-dir. Reports how AI-Overview-saturated
the informational keyword universe is (overall + per cluster), which domains get
cited in AI Overviews (SERP rows of Type "AI Overview"), and the @graph / schema
readiness of the fetched competitor pages.

Local data only (SEMrush AI-Overview rows + already-fetched HTML schema).
NO live AI probing (no Perplexity/Gemini/ChatGPT API calls). No LLM.

Usage:
    python3 geo_analysis.py --semrush-dir DIR --out-dir DIR

Arguments:
    --semrush-dir   Directory of SEMrush xlsx exports (*serp_urls*us*.xlsx)
    --out-dir       Dir with keywords.json + classified.json (read-only here)
"""
import argparse
import glob
import json
import os
import re
import warnings
from collections import Counter, defaultdict
from urllib.parse import urlsplit

import pandas as pd

warnings.filterwarnings("ignore")


def regdom(u):
    d = urlsplit(u).netloc.lower()
    return d[4:] if d.startswith("www.") else d


def main():
    ap = argparse.ArgumentParser(
        description="GEO / AI-Overview citation + schema-readiness analysis")
    ap.add_argument("--semrush-dir", required=True,
                    help="Directory of SEMrush xlsx exports (*serp_urls*us*.xlsx)")
    ap.add_argument("--out-dir", required=True,
                    help="Dir with keywords.json + classified.json")
    args = ap.parse_args()

    base = args.out_dir
    KW = json.load(open(os.path.join(base, "keywords.json"), encoding="utf-8"))
    CLS = json.load(open(os.path.join(base, "classified.json"), encoding="utf-8"))
    ncohort = len(CLS)

    def info(r):
        return "Informational" in r["intent"]

    def aio(r):
        return "ai overview" in (r["feats"] or "").lower()

    # ---- 1. AI-Overview saturation of the informational universe ----
    irs = [r for r in KW if info(r)]
    print("=== GEO OPPORTUNITY SIZING (informational keywords) ===")
    if irs:
        n_aio = sum(1 for r in irs if aio(r))
        print(f"informational kw: {len(irs)}  |  trigger AI Overview: {n_aio} "
              f"({round(100*n_aio/len(irs))}%)  vol={sum(r['vol'] for r in irs if aio(r)):,}")
        bc = defaultdict(lambda: [0, 0, 0])
        for r in irs:
            bc[r["cluster"]][0] += 1
            if aio(r):
                bc[r["cluster"]][1] += 1
                bc[r["cluster"]][2] += r["vol"]
        print(f"\n{'cluster':<16}{'info#':>6}{'AIO#':>6}{'AIO%':>6}{'AIO vol':>9}")
        for c, (n, a, v) in sorted(bc.items(), key=lambda x: -x[1][2]):
            if c == "OTHER":
                continue
            print(f"{c:<16}{n:>6}{a:>6}{round(100*a/n) if n else 0:>5}%{v:>9,}")
    else:
        print("(no informational keywords in keywords.json)")

    # ---- 2. who actually gets cited in AI Overviews ----
    files = sorted(glob.glob(os.path.join(
        os.path.expanduser(args.semrush_dir), "*serp_urls*us*.xlsx")))
    cite = Counter()
    cite_kw = defaultdict(set)
    for f in files:
        m = re.match(r"(.+?)_serp_urls_", os.path.basename(f))
        kw = m.group(1).replace("_", "-") if m else "?"
        try:
            df = pd.read_excel(f)
        except Exception:
            continue
        if "Type" not in df.columns:
            continue
        for _, r in df[df["Type"] == "AI Overview"].iterrows():
            u = r.get("URL")
            if not isinstance(u, str):
                continue
            d = regdom(u)
            cite[d] += 1
            cite_kw[d].add(kw)
    print(f"\n=== AI-OVERVIEW CITED DOMAINS (across {len(files)} us SERPs) — top 20 ===")
    print(f"{'cites':>5}  {'#queries':>8}  domain")
    for d, c in cite.most_common(20):
        print(f"{c:>5}  {len(cite_kw[d]):>8}  {d}   [{','.join(sorted(cite_kw[d]))[:50]}]")

    # ---- 3. @graph readiness of fetched competitor pages ----
    print("\n=== @graph / SCHEMA READINESS of fetched competitor pages ===")
    print(f"{'domain':<24}{'arch':<16}{'#schema':>8}  AIO-cited?  schema types")
    for r in sorted(CLS, key=lambda x: -(len(x['schema_types']))):
        is_cited = "YES" if r["domain"] in cite else "—"
        print(f"{r['domain'][:23]:<24}{r.get('archetype', '')[:15]:<16}"
              f"{len(r['schema_types']):>8}  {is_cited:<10}  {','.join(r['schema_types'])[:60]}")

    print(f"\n=== GEO-relevant schema node coverage across {ncohort} fetched pages ===")
    for node in ["Article/BlogPosting", "FAQPage", "Person", "Organization",
                 "BreadcrumbList", "ImageObject", "VideoObject", "HowTo", "Question/Answer"]:
        keys = node.split("/")
        n = sum(1 for r in CLS if set(r["schema_types"]) & set(keys))
        print(f"   {node:<22} {n:>2}/{ncohort}")
    print("\nNOTE: live Perplexity/Gemini/ChatGPT citation testing NOT run "
          "(paid/external probe — needs explicit auth).")


if __name__ == "__main__":
    main()
