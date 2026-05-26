#!/usr/bin/env python3
"""On-page SEO: title/meta/H1 keyword alignment, canonical, internal-link density,
SERP features won.

Re-parses the already-fetched HTML in <out-dir>/html/ (using the fetch_manifest +
classified.json for keyword/archetype context) and reports meta-description /
canonical / single-H1 coverage, keyword-in-title/H1/meta alignment, title length
vs the 50-60 char sweet spot, internal/external link density, and the title
patterns of the strongest rankers. Writes onpage.json.

Local only. No API, no LLM.

Usage:
    python3 onpage_analysis.py --out-dir DIR

Arguments:
    --out-dir   Dir with fetch_manifest.json + classified.json + html/; writes onpage.json
"""
import argparse
import json
import os
import re
import sys
from urllib.parse import urlsplit

# html5lib (NOT html.parser) — same Shopify void-tag nesting reason as analyze_structure.
from bs4 import BeautifulSoup, Comment

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # noqa: F401 (parity)

JUNK = ["script", "style", "noscript", "svg", "form", "nav", "header", "footer", "aside", "template"]
JT = {"nav", "menu", "header", "footer", "breadcrumb", "cookie", "newsletter", "popup", "modal", "drawer",
      "cart", "search", "sidebar", "related", "recommended", "announcement", "social", "share", "pagination",
      "product-grid", "product-card", "mega-menu", "site-header", "site-footer"}

CONTENT_RE = re.compile(r"(article|post|entry|blog|main[-_]?content|page[-_]?content|\brte\b)", re.I)


def cls(e):
    if e is None or getattr(e, "attrs", None) is None:
        return set()
    c = e.get("class") or []
    if isinstance(c, str):
        c = c.split()
    t = {str(x).lower() for x in c}
    if e.get("id"):
        t.add(str(e.get("id")).lower())
    return t


def regdom(u):
    d = urlsplit(u).netloc.lower()
    return d[4:] if d.startswith("www.") else d


def strip(soup):
    for t in soup(JUNK):
        t.decompose()
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    for e in list(soup.find_all(True)):
        if getattr(e, "decomposed", False) or getattr(e, "attrs", None) is None:
            continue
        if cls(e) & JT:
            e.decompose()
    return soup


def pick(soup):
    best, bs = None, -1
    cands = soup.find_all("article") + soup.find_all(attrs={"itemprop": "articleBody"})
    cands += [e for e in soup.find_all(["div", "section", "main"]) if CONTENT_RE.search(" ".join(cls(e)))]
    cands += soup.find_all("main")
    for e in cands:
        s = sum(len(p.get_text(" ", strip=True)) for p in e.find_all(["p", "li"]))
        if s > bs:
            bs, best = s, e
    return best if (best is not None and bs >= 200) else (soup.body or soup)


def toks(s):
    return set(re.findall(r"[a-z0-9]+", (s or "").lower()))


def main():
    ap = argparse.ArgumentParser(description="On-page SEO analysis of fetched cohort")
    ap.add_argument("--out-dir", required=True,
                    help="Dir with fetch_manifest.json + classified.json + html/")
    args = ap.parse_args()

    base = args.out_dir
    MAN = [m for m in json.load(open(os.path.join(base, "fetch_manifest.json"), encoding="utf-8")) if m["ok"]]
    CLS = {r["url"]: r for r in json.load(open(os.path.join(base, "classified.json"), encoding="utf-8"))}

    rows = []
    for m in MAN:
        html_path = os.path.join(base, "html", f"{m['slug']}.html")
        if not os.path.exists(html_path):
            continue
        raw = open(html_path, errors="ignore").read()
        soup = BeautifulSoup(raw, "html5lib")
        title = (soup.title.get_text(strip=True) if soup.title else "") or ""
        md = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        meta = (md.get("content").strip() if md and md.get("content") else "")
        can = soup.find("link", attrs={"rel": "canonical"})
        canonical = bool(can and can.get("href"))
        h1 = [h.get_text(" ", strip=True) for h in soup.find_all("h1") if h.get_text(strip=True)]
        h1t = h1[0] if h1 else ""
        cls_rec = CLS.get(m["url"], {})
        # generic keyword cleaning: dashes -> spaces (no niche-specific token stripping)
        kw = (cls_rec.get("keyword", "") or "").replace("-", " ")
        ktok = toks(kw)
        kw_in_title = len(ktok & toks(title)) >= max(1, len(ktok) - 1) and len(ktok) > 0
        kw_in_h1 = len(ktok & toks(h1t)) >= max(1, len(ktok) - 1) and len(ktok) > 0
        kw_in_meta = len(ktok & toks(meta)) >= max(1, len(ktok) - 1) and len(ktok) > 0
        is_q = "?" in title or bool(re.match(r"(what|why|how|is|are|does|can|do)\b", title.lower()))
        # internal vs external links in body
        body = pick(strip(BeautifulSoup(raw, "html5lib")))
        sd = regdom(m["url"])
        intn = extn = 0
        for a in body.find_all("a", href=True):
            h = a["href"]
            if h.startswith("http"):
                if regdom(h) == sd:
                    intn += 1
                else:
                    extn += 1
            elif h.startswith("/"):
                intn += 1
        rows.append({
            "domain": m["domain"], "kw": kw, "us": m["us_min_pos"],
            "archetype": cls_rec.get("archetype", ""),
            "title": title, "title_len": len(title), "meta_len": len(meta), "has_meta": bool(meta),
            "canonical": canonical, "h1n": len(h1), "h1": h1t,
            "kw_in_title": kw_in_title, "kw_in_h1": kw_in_h1, "kw_in_meta": kw_in_meta,
            "title_is_question": is_q, "internal_links": intn, "external_links": extn})

    out_path = os.path.join(base, "onpage.json")
    json.dump(rows, open(out_path, "w", encoding="utf-8"), indent=2)

    n = len(rows)
    print(f"=== ON-PAGE SEO ({n} pages) ===")
    if n == 0:
        print("(no OK pages to analyze) -> " + out_path)
        return
    print(f"has meta description : {sum(r['has_meta'] for r in rows)}/{n}   median len {sorted(r['meta_len'] for r in rows)[n//2]}")
    print(f"has canonical        : {sum(r['canonical'] for r in rows)}/{n}")
    print(f"exactly one H1       : {sum(1 for r in rows if r['h1n']==1)}/{n}  "
          f"(0 H1: {sum(1 for r in rows if r['h1n']==0)}, multi: {sum(1 for r in rows if r['h1n']>1)})")
    print(f"keyword in <title>   : {sum(r['kw_in_title'] for r in rows)}/{n}")
    print(f"keyword in H1        : {sum(r['kw_in_h1'] for r in rows)}/{n}")
    print(f"keyword in meta desc : {sum(r['kw_in_meta'] for r in rows)}/{n}")
    print(f"title is question    : {sum(r['title_is_question'] for r in rows)}/{n}")
    tl = sorted(r['title_len'] for r in rows)
    print(f"title length         : {tl[0]}-{tl[-1]} (med {tl[n//2]})  [SEO sweet spot 50-60]")
    il = sorted(r['internal_links'] for r in rows)
    print(f"body internal links  : {il[0]}-{il[-1]} (med {il[n//2]})")
    print(f"body external links  : {sorted(r['external_links'] for r in rows)[n//2]} median")

    print("\n=== TITLE PATTERNS of strongest rankers (us top ~25) ===")
    for r in sorted([x for x in rows if x['us']], key=lambda x: x['us'])[:14]:
        flags = "".join(f for f, on in [("Q", r['title_is_question']), ("kwT", r['kw_in_title'])] if on)
        print(f"  us#{r['us']:<3} [{r['archetype'][:12]:<12}] {flags:<5} {r['title'][:72]}")
    no_us = [x for x in rows if not x['us']]
    if no_us:
        print("\n  (no-US-rank / other-region samples)")
        for r in no_us[:6]:
            print(f"  us#--  [{r['archetype'][:12]:<12}]       {r['title'][:72]}")

    print(f"\nsaved onpage.json ({n} pages) -> {out_path}")


if __name__ == "__main__":
    main()
