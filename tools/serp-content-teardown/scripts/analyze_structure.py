#!/usr/bin/env python3
"""Deterministic per-article structure metrics for a fetched competitor cohort.

Reads fetch_manifest.json + the HTML in <out-dir>/html/, computes word count,
heading counts, image/list/table counts, JSON-LD @type set, author, dates,
brand-name density, and outbound authority links per article. Writes
results.json + a human-readable prose_dump.txt (opening / H2 outline / closing).

No LLM, no network. Niche-agnostic: brand display names come from --brand-names
(falls back to a token derived from the domain).

Usage:
    python3 analyze_structure.py --out-dir DIR [--brand-names FILE]

Arguments:
    --out-dir       Dir with fetch_manifest.json + html/; writes results.json + prose_dump.txt
    --brand-names   Optional domain->[name variants] JSON (see templates/brand-names.json).
                    Missing domains fall back to a token derived from the domain.
"""
import argparse
import json
import os
import re
import sys
from urllib.parse import urlsplit

# html5lib (NOT html.parser): html.parser silently nests article bodies into
# unclosed void tags (<link>/<input>) on many Shopify themes, zeroing word counts.
from bs4 import BeautifulSoup, Comment

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import load_brand_names, brand_variants, regdom  # noqa: E402

JUNK_TAGS = ["script", "style", "noscript", "svg", "form", "iframe", "button", "nav",
             "header", "footer", "aside", "template", "link", "meta", "path", "select", "input"]
JUNK_TOKENS = {"nav", "navbar", "navigation", "menu", "header", "site-header", "footer",
    "site-footer", "breadcrumb", "breadcrumbs", "cookie", "cookies", "consent", "newsletter",
    "popup", "modal", "drawer", "cart", "minicart", "search", "searchbar", "sidebar", "aside",
    "related", "related-posts", "recommended", "recommendations", "recommendation", "upsell",
    "cross-sell", "you-may-also-like", "announcement", "announcement-bar", "social", "share",
    "sharing", "share-buttons", "predictive-search", "mega-menu", "subnav", "utility-bar",
    "skip-link", "pagination", "comments", "comment-form", "toolbar", "product-grid",
    "product-card", "collection-grid", "also-bought", "footer-menu"}

SOCIAL = {"instagram.com", "facebook.com", "twitter.com", "x.com", "tiktok.com", "youtube.com",
    "youtu.be", "pinterest.com", "linkedin.com", "spotify.com", "snapchat.com", "threads.net",
    "reddit.com", "whatsapp.com", "t.me"}
INFRA = {"shopify.com", "cdn.shopify.com", "myshopify.com", "klaviyo.com", "google.com",
    "googleapis.com", "gstatic.com", "cloudflare.com", "gtag", "doubleclick.net", "facebook.net",
    "fonts.googleapis.com", "schema.org", "w3.org", "apple.com", "shopifycdn.com"}
AUTHORITY = {"en.wikipedia.org", "wikipedia.org", "ncbi.nlm.nih.gov", "pubmed.ncbi.nlm.nih.gov",
    "nih.gov", "who.int", "astm.org", "iso.org", "gia.edu", "ftc.gov", "fda.gov", "mayoclinic.org",
    "healthline.com", "medicalnewstoday.com", "sciencedirect.com", "nature.com", "jstor.org",
    "aad.org", "webmd.com", "britannica.com"}

CONTENT_RE = re.compile(r"(article[-_]?(template|content|body|__content|__body|__rte)"
    r"|(post|entry|blog)[-_]?(content|body|article)|\brte\b|main[-_]?content"
    r"|page[-_]?content|content[-_]?wrapper|article-template)", re.I)


def classes_of(el):
    if el is None or getattr(el, "attrs", None) is None:
        return set()
    c = el.get("class") or []
    if isinstance(c, str):
        c = c.split()
    toks = set()
    for x in c:
        toks.add(str(x).lower())
    if el.get("id"):
        toks.add(str(el.get("id")).lower())
    return toks


def strip_junk(soup):
    for t in soup(JUNK_TAGS):
        t.decompose()
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    for el in list(soup.find_all(True)):
        # guard: skip nodes already removed (decomposed) or detached (attrs None)
        # so we don't crash walking a node whose parent was just decomposed.
        if getattr(el, "decomposed", False) or getattr(el, "attrs", None) is None:
            continue
        if classes_of(el) & JUNK_TOKENS:
            el.decompose()
    return soup


def prose_len(el):
    n = 0
    for p in el.find_all(["p", "li"]):
        n += len(p.get_text(" ", strip=True))
    return n


def pick_container(soup):
    """Choose the main content container by max <p>/<li> text length."""
    cands = []
    cands += soup.find_all("article")
    cands += soup.find_all(attrs={"itemprop": "articleBody"})
    for el in soup.find_all(["div", "section", "main"]):
        if CONTENT_RE.search(" ".join(classes_of(el))):
            cands.append(el)
    cands += soup.find_all("main")
    best, best_score = None, -1
    for el in cands:
        s = prose_len(el)
        if s > best_score:
            best, best_score = el, s
    if best is None or best_score < 200:  # fall back to body for thin/odd pages
        best = soup.body or soup
    return best


def word_count(el):
    txt = el.get_text(" ", strip=True)
    return len([w for w in re.split(r"\s+", txt) if re.search(r"\w", w)]), txt


def collect_schema_types(soup):
    """JSON-LD @type set, handling @graph + arrays + nested objects."""
    types = set()
    blocks = 0

    def walk(o):
        if isinstance(o, dict):
            t = o.get("@type")
            if isinstance(t, str):
                types.add(t)
            elif isinstance(t, list):
                for x in t:
                    if isinstance(x, str):
                        types.add(x)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    for s in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = (s.string or s.get_text() or "").strip()
        if not raw:
            continue
        blocks += 1
        try:
            walk(json.loads(raw))
        except Exception:
            # salvage multiple concatenated objects
            for m in re.finditer(r"\{.*?\}", raw, re.S):
                try:
                    walk(json.loads(m.group(0)))
                except Exception:
                    pass
    return sorted(types), blocks


def find_author(soup):
    for s in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = (s.string or s.get_text() or "").strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue
        stack = [data]
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                a = o.get("author")
                if isinstance(a, dict) and a.get("name"):
                    return a["name"].strip()[:60]
                if isinstance(a, list):
                    for x in a:
                        if isinstance(x, dict) and x.get("name"):
                            return x["name"].strip()[:60]
                if isinstance(a, str) and a.strip():
                    return a.strip()[:60]
                stack += list(o.values())
            elif isinstance(o, list):
                stack += o
    m = soup.find("meta", attrs={"name": "author"})
    if m and m.get("content"):
        return m["content"].strip()[:60]
    for el in soup.find_all(attrs={"class": re.compile(r"(author|byline)", re.I)}):
        t = el.get_text(" ", strip=True)
        t = re.sub(r"(?i)^(by|written by|author:?)\s*", "", t).strip()
        if 2 < len(t) < 50 and not re.search(r"https?://", t):
            return t
    return None


def find_dates(soup):
    pub = mod = None
    for s in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = (s.string or s.get_text() or "").strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue
        stack = [data]
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                if not pub and o.get("datePublished"):
                    pub = str(o["datePublished"])[:10]
                if not mod and o.get("dateModified"):
                    mod = str(o["dateModified"])[:10]
                stack += list(o.values())
            elif isinstance(o, list):
                stack += o
    if not pub:
        m = soup.find("meta", attrs={"property": "article:published_time"})
        if m and m.get("content"):
            pub = m["content"][:10]
    if not mod:
        m = soup.find("meta", attrs={"property": "article:modified_time"})
        if m and m.get("content"):
            mod = m["content"][:10]
    if not pub:
        t = soup.find("time")
        if t and t.get("datetime"):
            pub = t["datetime"][:10]
    return pub, mod


def brand_density(text, variants, words):
    n = 0
    low = text.lower()
    for v in variants:
        n += len(re.findall(r"\b" + re.escape(v.lower()) + r"\b", low))
    return round(n / words * 1000, 1) if words else 0.0, n


def outbound(el, domain):
    selfreg = regdom(domain)
    ext, auth, soc = set(), set(), set()
    for a in el.find_all("a", href=True):
        href = a["href"]
        if not href.startswith("http"):
            continue
        d = regdom(urlsplit(href).netloc)
        if not d or d == selfreg:
            continue
        if d in INFRA or "schema.org" in d:
            continue
        if d in SOCIAL:
            soc.add(d)
            continue
        if d in AUTHORITY or d.endswith(".gov") or d.endswith(".edu"):
            auth.add(d)
        ext.add(d)
    return len(auth), sorted(auth), len(ext), sorted(ext), len(soc)


def clean_para(t):
    return re.sub(r"\s+", " ", t).strip()


def head_tail_prose(container):
    paras = []
    for p in container.find_all(["p", "li", "h2", "h3"]):
        if p.name in ("h2", "h3"):
            txt = "## " + clean_para(p.get_text(" ", strip=True))
        else:
            txt = clean_para(p.get_text(" ", strip=True))
        if len(txt) > 2:
            paras.append(txt)
    head = [p for p in paras if not p.startswith("## ")][:3]
    tail = paras[-6:]
    return head, tail


def main():
    ap = argparse.ArgumentParser(
        description="Per-article structure metrics -> results.json + prose_dump.txt")
    ap.add_argument("--out-dir", required=True,
                    help="Dir with fetch_manifest.json + html/")
    ap.add_argument("--brand-names", metavar="FILE",
                    help="domain->[variants] JSON (see templates/brand-names.json)")
    args = ap.parse_args()

    base = args.out_dir
    man = json.load(open(os.path.join(base, "fetch_manifest.json"), encoding="utf-8"))
    brand_map = load_brand_names(args.brand_names)

    results, prose_out = [], []
    for m in man:
        if not m["ok"]:
            continue
        path = os.path.join(base, "html", f"{m['slug']}.html")
        if not os.path.exists(path):
            continue
        html = open(path, "r", errors="ignore").read()
        soup = BeautifulSoup(html, "html5lib")  # html5lib: see module header note
        types, schema_blocks = collect_schema_types(soup)
        author = find_author(soup)
        pub, mod = find_dates(soup)
        h1_all = len(soup.find_all("h1"))
        soup = strip_junk(soup)
        container = pick_container(soup)
        words, text = word_count(container)
        h2 = container.find_all("h2")
        h3 = container.find_all("h3")
        h2_txt = [clean_para(x.get_text(" ", strip=True))[:90] for x in h2 if x.get_text(strip=True)]
        h3_txt = [clean_para(x.get_text(" ", strip=True))[:90] for x in h3 if x.get_text(strip=True)]
        imgs = len(container.find_all("img"))
        uls = len(container.find_all("ul"))
        ols = len(container.find_all("ol"))
        tables = len(container.find_all("table"))
        variants = brand_variants(m["domain"], brand_map)
        bd, bn = brand_density(text, variants, words)
        auth_n, auth_d, ext_n, ext_d, soc_n = outbound(container, m["domain"])
        has_faq = ("FAQPage" in types) or any(
            re.search(r"frequently asked|^faq\b", h, re.I) for h in h2_txt + h3_txt)
        rec = {
            "domain": m["domain"], "url": m["url"], "category": m["category"],
            "keyword": (m["info_topic_hits"] or m["matched_keywords"] or ["-"])[0],
            "all_matched_keywords": m["matched_keywords"],
            "us_min_pos": m["us_min_pos"], "all_min_pos": m["all_min_pos"], "avg_pos": m["avg_pos"],
            "word_count": words,
            "h1": h1_all, "h2": len(h2_txt), "h3": len(h3_txt),
            "imgs": imgs, "ul": uls, "ol": ols, "table": tables,
            "schema_types": types, "schema_blocks": schema_blocks,
            "has_faq_section": has_faq,
            "author": author, "has_author": bool(author),
            "date_published": pub, "date_modified": mod,
            "brand_variants": variants,
            "brand_per_1k": bd, "brand_mentions": bn,
            "authority_outlinks": auth_n, "authority_domains": auth_d,
            "external_outlinks": ext_n, "external_domains": ext_d[:12], "social_outlinks": soc_n,
            "h2_texts": h2_txt, "h3_texts": h3_txt,
        }
        head, tail = head_tail_prose(container)
        rec["opening"] = " ".join(head[:2])[:700]
        rec["closing"] = " ".join(t for t in tail if not t.startswith("## "))[-700:]
        results.append(rec)
        prose_out.append("=" * 100)
        prose_out.append(f"{m['domain']}  | kw={rec['keyword']} us#{m['us_min_pos']}  | "
                         f"words={words} H2={len(h2_txt)} H3={len(h3_txt)} | schema={','.join(types) or '-'}")
        prose_out.append(f"URL {m['url']}")
        prose_out.append("--- OPENING (first paras) ---")
        for h in head:
            prose_out.append("  " + h[:500])
        prose_out.append("--- H2 OUTLINE ---")
        for h in h2_txt:
            prose_out.append("  ## " + h)
        prose_out.append("--- CLOSING (last blocks) ---")
        for t in tail:
            prose_out.append("  " + t[:400])
        prose_out.append("")

    results.sort(key=lambda x: (x["us_min_pos"] if x["us_min_pos"] is not None else 999,
                                x["all_min_pos"] or 999))
    json.dump(results, open(os.path.join(base, "results.json"), "w", encoding="utf-8"), indent=2)
    open(os.path.join(base, "prose_dump.txt"), "w", encoding="utf-8").write("\n".join(prose_out))

    print(f"analyzed={len(results)} articles -> results.json + prose_dump.txt\n")
    if not results:
        print("(no OK articles in fetch_manifest.json — nothing to summarize)")
        return
    hdr = (f"{'domain':<24}{'kw':<14}{'us#':>4}{'words':>6}{'H2':>3}{'H3':>3}{'img':>4}"
           f"{'ul':>3}{'ol':>3}{'tbl':>4}{'auth':>5}{'br/1k':>6}{'faq':>4}  schema")
    print(hdr)
    print("-" * len(hdr))
    for r in results:
        sch = ",".join(t for t in r["schema_types"] if t in
            ("Article", "BlogPosting", "NewsArticle", "FAQPage", "Person", "Organization",
             "BreadcrumbList", "WebPage", "HowTo", "ItemList", "Product", "VideoObject"))
        print(f"{r['domain'][:23]:<24}{r['keyword'][:13]:<14}"
              f"{str(r['us_min_pos'] or '-'):>4}{r['word_count']:>6}{r['h2']:>3}{r['h3']:>3}{r['imgs']:>4}"
              f"{r['ul']:>3}{r['ol']:>3}{r['table']:>4}{r['authority_outlinks']:>5}{r['brand_per_1k']:>6}"
              f"{('Y' if r['has_faq_section'] else '-'):>4}  {sch[:46]}")


if __name__ == "__main__":
    main()
