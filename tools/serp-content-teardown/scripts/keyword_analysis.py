#!/usr/bin/env python3
"""Keyword distribution + core-keyword analysis from SEMrush broad-match files.

Reads every ``*broad-match*us*.xlsx`` in --semrush-dir, dedupes keywords (best
volume wins), buckets them into the topic clusters from --topics, and reports
intent / volume / difficulty bands, SERP-feature flags (AI Overview, PAA, Video,
Featured snippet), per-cluster core keywords, and quick-win candidates. Writes
keywords.json (consumed by geo_analysis.py).

Local data only. No API, no LLM.

Usage:
    python3 keyword_analysis.py --semrush-dir DIR --out-dir DIR --topics topic-clusters.yaml

Arguments:
    --semrush-dir   Directory of SEMrush xlsx exports (*broad-match*us*.xlsx)
    --out-dir       Where to write keywords.json
    --topics        topic-clusters.yaml (see templates/)
"""
import argparse
import glob
import json
import math
import os
import sys
import warnings
from collections import defaultdict

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import load_clusters, cluster_of  # noqa: E402

warnings.filterwarnings("ignore")


def feat_flags(s):
    s = (s or "").lower()
    return {
        "aio": "ai overview" in s,
        "paa": "people also ask" in s,
        "video": "video" in s,
        "featured": "featured snippet" in s,
        "image": "image" in s,
    }


def main():
    ap = argparse.ArgumentParser(
        description="Keyword distribution + core keywords from SEMrush broad-match")
    ap.add_argument("--semrush-dir", required=True,
                    help="Directory of SEMrush xlsx exports (*broad-match*us*.xlsx)")
    ap.add_argument("--out-dir", required=True, help="Where to write keywords.json")
    ap.add_argument("--topics", required=True, help="topic-clusters.yaml")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    clusters = load_clusters(args.topics)

    files = sorted(glob.glob(os.path.join(
        os.path.expanduser(args.semrush_dir), "*broad-match*us*.xlsx")))

    rows = {}  # keyword -> best record
    for f in files:
        try:
            df = pd.read_excel(f)
        except Exception:
            continue
        if "Keyword" not in df.columns:
            continue
        for _, r in df.iterrows():
            kw = r.get("Keyword")
            if not isinstance(kw, str):
                continue
            kw = kw.strip().lower()
            try:
                vol = int(r.get("Volume") or 0)
            except Exception:
                vol = 0
            try:
                kd = float(r.get("Keyword Difficulty"))
                if math.isnan(kd):
                    kd = None
            except Exception:
                kd = None
            intent = str(r.get("Intent") or "")
            feats = str(r.get("SERP Features") or "")
            cur = rows.get(kw)
            if cur is None or vol > cur["vol"]:
                rows[kw] = {"kw": kw, "vol": vol, "kd": kd, "intent": intent,
                            "feats": feats, "cluster": cluster_of(kw, clusters)}

    KW = list(rows.values())
    out_path = os.path.join(args.out_dir, "keywords.json")
    json.dump(KW, open(out_path, "w", encoding="utf-8"), indent=2)

    if not KW:
        print(f"no keywords found in {len(files)} broad-match files -> {out_path}")
        return

    def is_info(r):
        return "Informational" in r["intent"]

    tot = len(KW)
    tot_vol = sum(r["vol"] for r in KW)
    info = [r for r in KW if is_info(r)]
    aio = [r for r in KW if feat_flags(r["feats"])["aio"]]
    paa = [r for r in KW if feat_flags(r["feats"])["paa"]]
    vid = [r for r in KW if feat_flags(r["feats"])["video"]]

    print(f"=== KEYWORD UNIVERSE (US, deduped across {len(files)} broad-match files) ===")
    print(f"unique keywords: {tot}  |  total monthly search volume: {tot_vol:,}")
    print(f"Informational intent: {len(info)} ({round(100*len(info)/tot)}%)  vol={sum(r['vol'] for r in info):,}")
    print(f"triggers AI Overview: {len(aio)} ({round(100*len(aio)/tot)}%)  |  "
          f"People-also-ask: {len(paa)} ({round(100*len(paa)/tot)}%)  |  "
          f"Video: {len(vid)} ({round(100*len(vid)/tot)}%)")

    print("\n=== INTENT DISTRIBUTION ===")
    bi = defaultdict(lambda: [0, 0])
    for r in KW:
        key = r["intent"] or "(none)"
        bi[key][0] += 1
        bi[key][1] += r["vol"]
    for k, (c, v) in sorted(bi.items(), key=lambda x: -x[1][1])[:8]:
        print(f"  {c:>4} kw  vol {v:>7,}   {k}")

    print("\n=== VOLUME BANDS ===")
    bands = [(1000, 99999, '1k+'), (300, 999, '300-999'), (100, 299, '100-299'),
             (50, 99, '50-99'), (0, 49, '<50')]
    for lo, hi, lbl in bands:
        g = [r for r in KW if lo <= r["vol"] <= hi]
        print(f"  {lbl:<8} {len(g):>3} kw   vol {sum(r['vol'] for r in g):>7,}")

    print("\n=== KD (difficulty) BANDS ===")
    for lo, hi, lbl in [(0, 9, '0-9 trivial'), (10, 19, '10-19 easy'), (20, 29, '20-29 mod'),
                        (30, 49, '30-49 hard'), (50, 100, '50+ very hard')]:
        g = [r for r in KW if r["kd"] is not None and lo <= r["kd"] <= hi]
        print(f"  {lbl:<14} {len(g):>3} kw   vol {sum(r['vol'] for r in g):>7,}")

    print("\n=== CLUSTER DISTRIBUTION ===")
    bc = defaultdict(lambda: [0, 0, []])
    for r in KW:
        bc[r["cluster"]][0] += 1
        bc[r["cluster"]][1] += r["vol"]
        bc[r["cluster"]][2].append(r)
    print(f"{'cluster':<16}{'#kw':>5}{'volume':>9}{'%info':>7}{'medKD':>7}{'%AIO':>6}")
    for c, (n, v, rs) in sorted(bc.items(), key=lambda x: -x[1][1]):
        pinfo = round(100 * sum(1 for r in rs if is_info(r)) / n)
        kds = sorted(r["kd"] for r in rs if r["kd"] is not None)
        medkd = kds[len(kds) // 2] if kds else None
        paio = round(100 * sum(1 for r in rs if feat_flags(r["feats"])["aio"]) / n)
        print(f"{c:<16}{n:>5}{v:>9,}{pinfo:>6}%{str(medkd):>7}{paio:>5}%")

    print("\n=== CORE KEYWORDS per cluster (Informational, ranked by volume; KD shown) ===")
    for c, (n, v, rs) in sorted(bc.items(), key=lambda x: -x[1][1]):
        if c == "OTHER":  # catch-all bucket is not a real topic cluster
            continue
        irs = sorted([r for r in rs if is_info(r)], key=lambda r: -r["vol"])[:8]
        if not irs:
            continue
        print(f"\n[{c}]")
        for r in irs:
            f = feat_flags(r["feats"])
            tags = "".join(t for t, on in [("AIO", f["aio"]), ("·PAA", f["paa"]),
                                           ("·Vid", f["video"]), ("·FS", f["featured"])] if on)
            print(f"  {r['vol']:>5}  KD{str(int(r['kd']) if r['kd'] is not None else '?'):>3}  {r['kw'][:52]:<52} {tags}")

    print("\n=== QUICK-WIN core keywords (Informational + KD<=20 + vol>=70), top 25 ===")
    qw = sorted([r for r in KW if is_info(r) and r["kd"] is not None and r["kd"] <= 20 and r["vol"] >= 70],
                key=lambda r: -r["vol"])
    for r in qw[:25]:
        f = feat_flags(r["feats"])
        tags = "".join(t for t, on in [("AIO", f["aio"]), ("·PAA", f["paa"]), ("·Vid", f["video"])] if on)
        print(f"  {r['vol']:>5}  KD{int(r['kd']):>3}  {r['cluster']:<14} {r['kw'][:46]:<46} {tags}")

    print(f"\nsaved keywords.json ({tot} keywords) -> {out_path}")


if __name__ == "__main__":
    main()
