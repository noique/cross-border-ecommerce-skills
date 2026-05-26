#!/usr/bin/env python3
"""Authority / backlink threshold analysis from SEMrush serp_urls Organic rows.

Reads every ``*serp_urls*us*.xlsx`` in --semrush-dir, keeps Organic results,
buckets each ranking URL into the topic clusters from --topics, and reports the
Page-Authority-Score / Ref.Domains / Backlinks thresholds needed by position band
(top-3, top-10, 11-20) per cluster, plus "weak-link winners" (top-10 pages with
low authority = beatable with better content) and the #1-3 incumbents. Writes
backlinks.json.

Page AS = SEMrush page-level Authority Score (0-100). Local data only. No API.

Usage:
    python3 backlink_analysis.py --semrush-dir DIR --out-dir DIR --topics topic-clusters.yaml

Arguments:
    --semrush-dir   Directory of SEMrush xlsx exports (*serp_urls*us*.xlsx)
    --out-dir       Where to write backlinks.json
    --topics        topic-clusters.yaml (see templates/)
"""
import argparse
import glob
import json
import math
import os
import re
import statistics as st
import sys
import warnings
from urllib.parse import urlsplit

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import load_clusters, cluster_of  # noqa: E402

warnings.filterwarnings("ignore")


def kw_of(fn):
    m = re.match(r"(.+?)_serp_urls_", os.path.basename(fn))
    return (m.group(1).replace("_", "-") if m else "?")


def regdom(u):
    d = urlsplit(u).netloc.lower()
    return d[4:] if d.startswith("www.") else d


def num(x):
    try:
        v = float(x)
        return None if math.isnan(v) else v
    except Exception:
        return None


def stats(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return "-"
    return f"med {int(st.median(vals))} (min {int(min(vals))}, max {int(max(vals))})"


def main():
    ap = argparse.ArgumentParser(
        description="Authority/backlink thresholds from SEMrush serp_urls Organic rows")
    ap.add_argument("--semrush-dir", required=True,
                    help="Directory of SEMrush xlsx exports (*serp_urls*us*.xlsx)")
    ap.add_argument("--out-dir", required=True, help="Where to write backlinks.json")
    ap.add_argument("--topics", required=True, help="topic-clusters.yaml")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    clusters = load_clusters(args.topics)
    # focus clusters = every configured cluster (catch-all OTHER excluded)
    focus = [n for n, _ in clusters]

    files = sorted(glob.glob(os.path.join(
        os.path.expanduser(args.semrush_dir), "*serp_urls*us*.xlsx")))

    rows = []
    for f in files:
        kw = kw_of(f)
        cl = cluster_of(kw, clusters)
        try:
            df = pd.read_excel(f)
        except Exception:
            continue
        org = df[df["Type"] == "Organic"] if "Type" in df.columns else df
        seen = set()
        for _, r in org.iterrows():
            u = r.get("URL")
            if not isinstance(u, str):
                continue
            try:
                pos = int(r.get("Position"))
            except Exception:
                continue
            key = (kw, regdom(u))
            if key in seen:
                continue
            seen.add(key)
            rows.append({"kw": kw, "cluster": cl, "pos": pos, "as": num(r.get("Page AS")),
                         "ref": num(r.get("Ref.Domains")), "bl": num(r.get("Backlinks")),
                         "domain": regdom(u), "url": u})

    out_path = os.path.join(args.out_dir, "backlinks.json")
    json.dump(rows, open(out_path, "w", encoding="utf-8"), indent=2)

    # clusters that actually have organic rows, in configured order
    present = [c for c in focus if any(r["cluster"] == c for r in rows)]

    print("=== AUTHORITY THRESHOLD to rank — by position band (per topic cluster) ===")
    print("Page AS = SEMrush page-level Authority Score (0-100). Organic results only.\n")
    for cl in present:
        crows = [r for r in rows if r["cluster"] == cl]
        print(f"[{cl}]  ({len(crows)} organic results across its query)")
        for lo, hi, lbl in [(1, 3, "top-3"), (1, 10, "top-10"), (11, 20, "11-20")]:
            band = [r for r in crows if lo <= r["pos"] <= hi]
            if not band:
                continue
            print(f"   {lbl:<7} n={len(band):<3} "
                  f"PageAS {stats([r['as'] for r in band]):<28} "
                  f"RefDom {stats([r['ref'] for r in band]):<28} "
                  f"Backlinks {stats([r['bl'] for r in band])}")
        print()

    print("=== WEAK-LINK WINNERS — top-10 organic with low authority (= beatable / proof content wins) ===")
    weak = [r for r in rows if r["pos"] <= 10 and r["as"] is not None and r["as"] <= 20
            and r["cluster"] in present]
    weak.sort(key=lambda r: (r["pos"], r["as"]))
    print(f"{'pos':>3} {'AS':>3} {'refD':>5} {'BL':>6}  {'kw':<22} domain")
    for r in weak[:25]:
        ref = int(r['ref']) if r['ref'] is not None else '-'
        bl = int(r['bl']) if r['bl'] is not None else '-'
        print(f"{r['pos']:>3} {int(r['as']):>3} {ref:>5} {bl:>6}  {r['kw'][:21]:<22} {r['domain']}")

    print("\n=== HEAD-TERM #1-3 incumbents (what it takes at the very top) ===")
    for cl in present:
        top = [r for r in rows if r["cluster"] == cl and r["pos"] <= 3]
        top.sort(key=lambda r: r["pos"])
        print(f"[{cl}]")
        for r in top[:5]:
            a = int(r['as']) if r['as'] is not None else '?'
            ref = int(r['ref']) if r['ref'] is not None else '?'
            bl = int(r['bl']) if r['bl'] is not None else '?'
            print(f"   #{r['pos']} AS{a:>3} ref{ref:>4} bl{bl:>5}  {r['domain']}  ({r['kw']})")

    print(f"\nsaved backlinks.json ({len(rows)} organic rows) -> {out_path}")


if __name__ == "__main__":
    main()
