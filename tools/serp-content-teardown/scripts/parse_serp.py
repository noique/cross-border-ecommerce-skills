#!/usr/bin/env python3
"""Parse SEMrush *serp_urls*.xlsx files -> ranked competitor blog/info URL pool.

Read-only. No DB, no network, no LLM. Deterministic.

Reads every ``*serp_urls*.xlsx`` in --semrush-dir (all regions, for breadth),
keeps rows whose URL path looks like a blog / informational article, ranks them
(topic-cluster hits first, then best US position, then breadth), and writes
``url_pool.json`` to --out-dir.

Usage:
    python3 parse_serp.py --semrush-dir DIR --out-dir DIR --topics topic-clusters.yaml [--limit N]

Arguments:
    --semrush-dir   Directory of SEMrush xlsx exports (looks for *serp_urls*.xlsx)
    --out-dir       Where to write url_pool.json (created if missing)
    --topics        topic-clusters.yaml (see templates/) — drives info-topic priority
    --limit         Cap rows printed in the console table (default: 40; file is full)
"""
import argparse
import glob
import json
import os
import re
import sys
import warnings
from collections import defaultdict
from urllib.parse import urlsplit

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import load_clusters, cluster_of  # noqa: E402

warnings.filterwarnings("ignore")

# ── blog / info-article path classification ─────────────────────────────────
BLOG_TOKENS = ("/blog", "/blogs/", "/journal", "/guides", "/guide/", "/learn",
               "/stories", "/story/", "/article", "/articles", "/edit",
               "/education", "/magazine", "/news/", "/tips", "/resources",
               "/the-edit", "/discover", "/inspiration", "/advice", "/post/")

# obvious non-article buckets (niche-agnostic e-commerce / utility paths)
EXCLUDE_PATH_RE = re.compile(
    r"^/?$|/products?/|/collections?/|/cart|/checkout|/account|/search|"
    r"/policies|/policy|/pages/(about|contact|shipping|returns?|refund|"
    r"faq|wholesale|stockist|store-locator|size-chart|size-guide|"
    r"track|warranty|terms|privacy|press|careers?|affiliate|reviews?$|"
    r"gift-?card|our-story|sustainability)", re.I)

# marketplaces / UGC / SEO noise that are never peer brand blogs
NON_PEER_DOMAINS = {
    "amazon.com", "ebay.com", "etsy.com", "walmart.com", "aliexpress.com",
    "reddit.com", "quora.com", "youtube.com", "pinterest.com", "tiktok.com",
    "instagram.com", "facebook.com", "wikipedia.org", "google.com",
    "temu.com", "alibaba.com", "wikihow.com",
}


def parse_fname(fn):
    """e.g. waterproof-jewelry_serp_urls_us_2026-... -> ('waterproof-jewelry', 'us')."""
    base = os.path.basename(fn)
    m = re.match(r"(.+?)_serp_urls_([a-z]{2})_", base)
    if not m:
        return None, None
    kw = m.group(1).replace("_", "-")
    return kw, m.group(2)


def classify_path(url, info_slug_re):
    """Return (registrable_domain, category|None).

    category is 'blog' for clear blog paths, 'info_page' for Shopify-style
    /pages/ slugs that match a configured topic cluster, else None.
    info_slug_re is built from the topic-cluster patterns (niche-driven).
    """
    try:
        sp = urlsplit(url)
    except Exception:
        return None, None
    dom = sp.netloc.lower().lstrip("www.")
    path = (sp.path or "/").lower()
    if dom in NON_PEER_DOMAINS:
        return dom, None
    if any(t in path for t in BLOG_TOKENS):
        return dom, "blog"
    if "/pages/" in path and info_slug_re.search(path):
        return dom, "info_page"
    return dom, None


def norm_key(url):
    sp = urlsplit(url)
    dom = sp.netloc.lower()
    if dom.startswith("www."):
        dom = dom[4:]
    path = (sp.path or "/").rstrip("/").lower()
    return dom, path


def build_info_slug_re(clusters):
    """Union of all cluster regex sources -> single regex for /pages/ info detection.

    Lets a Shopify /pages/<slug> qualify as informational when the slug mentions
    any configured topic, instead of a hardcoded niche word list.
    """
    parts = [pat.pattern for _, pat in clusters]
    return re.compile("(" + "|".join(parts) + ")", re.I)


def main():
    ap = argparse.ArgumentParser(
        description="SEMrush serp_urls xlsx -> ranked competitor blog/info URL pool")
    ap.add_argument("--semrush-dir", required=True,
                    help="Directory of SEMrush xlsx exports (*serp_urls*.xlsx)")
    ap.add_argument("--out-dir", required=True, help="Output dir for url_pool.json")
    ap.add_argument("--topics", required=True,
                    help="topic-clusters.yaml (drives info-topic priority)")
    ap.add_argument("--limit", type=int, default=40,
                    help="Rows printed in console table (default: 40)")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    clusters = load_clusters(args.topics)
    info_slug_re = build_info_slug_re(clusters)
    cluster_names = [n for n, _ in clusters]

    files = sorted(glob.glob(os.path.join(
        os.path.expanduser(args.semrush_dir), "*serp_urls*.xlsx")))

    rec = {}
    total_rows = kept_rows = 0
    for f in files:
        kw, region = parse_fname(f)
        if kw is None:
            continue
        try:
            df = pd.read_excel(f)
        except Exception as e:
            print("READ FAIL", os.path.basename(f), e)
            continue
        if "URL" not in df.columns:
            continue
        for _, row in df.iterrows():
            url = row.get("URL")
            if not isinstance(url, str) or not url.startswith("http"):
                continue
            total_rows += 1
            dom, cat = classify_path(url, info_slug_re)
            if cat is None:
                continue
            path = urlsplit(url).path
            if EXCLUDE_PATH_RE.search(path):
                continue
            kept_rows += 1
            k = norm_key(url)
            pos = row.get("Position")
            try:
                pos = int(pos)
            except Exception:
                pos = None
            typ = str(row.get("Type") or "")
            traf = row.get("Search Traffic")
            try:
                traf = float(traf)
            except Exception:
                traf = None
            if k not in rec:
                rec[k] = {
                    "domain": k[0], "path": k[1], "url": url, "category": cat,
                    "appearances": 0, "kw": defaultdict(list), "positions": [],
                    "us_positions": [], "types": set(), "max_traffic": 0.0,
                }
            r = rec[k]
            r["appearances"] += 1
            r["kw"][kw].append((region, pos, typ))
            if pos is not None:
                r["positions"].append(pos)
                if region == "us":
                    r["us_positions"].append(pos)
            r["types"].add(typ)
            if traf and traf > r["max_traffic"]:
                r["max_traffic"] = traf

    # ── info-topic priority: a matched keyword whose cluster is not OTHER ──
    def summarize(r):
        matched = set(r["kw"].keys())
        info_hits = sorted(
            kw for kw in matched if cluster_of(kw, clusters) != "OTHER")
        us_min = min(r["us_positions"]) if r["us_positions"] else None
        all_min = min(r["positions"]) if r["positions"] else None
        avg = round(sum(r["positions"]) / len(r["positions"]), 1) if r["positions"] else None
        return {
            "domain": r["domain"], "path": r["path"], "url": r["url"],
            "category": r["category"], "appearances": r["appearances"],
            "matched_keywords": sorted(matched),
            "info_topic_hits": info_hits,
            "us_min_pos": us_min, "all_min_pos": all_min, "avg_pos": avg,
            "n_keywords": len(matched), "max_traffic": r["max_traffic"],
            "types": sorted(r["types"]),
        }

    rows = [summarize(r) for r in rec.values()]

    # rank: info-topic hits first, then good US position, then breadth
    def rank_key(x):
        has_info = 1 if x["info_topic_hits"] else 0
        us = x["us_min_pos"] if x["us_min_pos"] is not None else 999
        allm = x["all_min_pos"] if x["all_min_pos"] is not None else 999
        return (-has_info, us, allm, -x["appearances"], -x["n_keywords"])

    rows.sort(key=rank_key)

    out_path = os.path.join(args.out_dir, "url_pool.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, indent=2)

    print(f"clusters={len(cluster_names)} {cluster_names}")
    print(f"files={len(files)}  total_url_rows={total_rows}  kept_blog/info_rows={kept_rows}")
    print(f"unique blog/info URLs={len(rows)} -> {out_path}")
    n = max(0, args.limit)
    print(f"\n=== TOP {n} candidate competitor blog/info URLs ===")
    print(f"{'#':>2} {'cat':<9} {'usPos':>5} {'allPos':>6} {'app':>3} {'info?':<5} domain | path")
    for i, x in enumerate(rows[:n], 1):
        info = ",".join(x["info_topic_hits"])[:5] or "-"
        print(f"{i:>2} {x['category']:<9} {str(x['us_min_pos'] or '-'):>5} {str(x['all_min_pos'] or '-'):>6} "
              f"{x['appearances']:>3} {info:<5} {x['domain']} | {x['path'][:60]}")


if __name__ == "__main__":
    main()
