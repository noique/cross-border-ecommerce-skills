#!/usr/bin/env python3
"""Deterministic 8-archetype classification + aggregate stats. No LLM.

Reads results.json (from analyze_structure.py), tags each article with an
archetype, an opening pattern, a closing pattern, and a schema signature, then
prints per-archetype and overall aggregate bands. Writes classified.json.

The 8 archetypes (precedence order, first match wins):
    NEWS_EDITORIAL, LISTICLE_TIPS, COMPARISON_VS, MYTH_DEBUNK,
    PRODUCT_MICROGUIDE, TUTORIAL_HOWTO, PILLAR_GUIDE, DEFINITION_QA

Niche-agnostic: detectors key off slug shape, schema @type, heading patterns and
opening prose — not hardcoded brand domains.

Usage:
    python3 classify_archetypes.py --out-dir DIR

Arguments:
    --out-dir   Dir with results.json; writes classified.json
"""
import argparse
import json
import os
import re
import statistics as st
from collections import Counter, defaultdict
from urllib.parse import urlsplit


def slug_of(url):
    p = urlsplit(url).path.rstrip("/")
    return p.split("/")[-1].lower()


MYTH = re.compile(r"\b(myth|myths|forget the|the truth|it's not all true|clear the air|misconception|debunk|don'?t believe)", re.I)
DEFQ = re.compile(r"^\s*(what is|what are|what does|what kind|why choose|why is|how is|is\b.*\?|does\b.*\?)", re.I)
STATLEAD = re.compile(r"\b\d{1,3}%|\bUSD\s?\$?\d|\$\d+\.?\d*\s?billion|\baccording to .* report", re.I)
TLDR = re.compile(r"^\s*(yes,|no,|the short answer|tl;?dr|in short)", re.I)
RELATE = re.compile(r"(we'?ve all been there|you'?re halfway|the frustration is real|ever (wondered|had)|picture this)", re.I)
MERCH = re.compile(r"(best sellers|bestsellers|newest drop|new collection|shop by|shop our|on sale|% off|sale -|code\s*:)", re.I)


def numbered_h2(h2):
    return sum(1 for h in h2 if re.match(r"^\s*\d+[\.\)]?\s", h))


def classify(r):
    slug = slug_of(r["url"])
    url = r["url"].lower()
    h2 = r["h2_texts"]
    h2blob = " | ".join(h2).lower()
    opening = r.get("opening", "") or ""
    w = r["word_count"]
    h2n = r["h2"]
    h3n = r["h3"]
    cat = r["category"]
    types = set(r["schema_types"])
    numh2 = numbered_h2(h2)
    def_q = bool(DEFQ.search(opening)) or slug.startswith(("what-", "is-", "does-", "why-"))
    merch = bool(MERCH.search(opening)) or any(MERCH.search(h) for h in h2)

    # ---- precedence ----
    if "NewsArticle" in types:
        return "NEWS_EDITORIAL", "NewsArticle schema / press best-of roundup"
    if h2blob.count("top products") >= 2:
        return "LISTICLE_TIPS", "marketplace product-listing (outlier — not editorial)"
    if re.search(r"(^|-)(vs)(-|$)", slug) or "compared-to" in slug or "-or-solid" in slug:
        return "COMPARISON_VS", "explicit X vs Y comparison (slug-level intent)"
    if MYTH.search(opening):
        return "MYTH_DEBUNK", "myth-bust opener"
    if (numh2 >= 3 or re.search(r"\b\d+\s+(types|ways|reasons|brands)\b", h2blob)
            or slug.startswith(("best-", "top-")) or "essentials" in slug
            or "/styling/" in url or "ways-to" in slug):
        return "LISTICLE_TIPS", "enumerated list / best-of / styling tips"
    if cat == "info_page" and w < 520 and not def_q and (merch or h2n == 0):
        return "PRODUCT_MICROGUIDE", "thin product-embedded landing page"
    if slug.startswith(("how-to", "how-do")) or slug in ("cleaning-jewelry",) or \
       (("clean" in slug or "care" in slug) and "guide" not in slug):
        return "TUTORIAL_HOWTO", "how-to / care steps"
    if ("types-of" in slug or "complete" in slug or "everything" in slug
            or "ultimate" in slug or h2n >= 12
            or ("-101" in slug and (h2n >= 8 or w >= 1500))
            or ("guide" in slug and h3n >= 10)):
        return "PILLAR_GUIDE", "comprehensive guide / types-taxonomy / mega question-cluster"
    return "DEFINITION_QA", "definitional / pros-cons / 'is X good' explainer"


def opening_pattern(r):
    o = r.get("opening", "") or ""
    if MYTH.search(o):
        return "MYTH_BUST"
    if TLDR.search(o):
        return "TLDR_FIRST"
    if MERCH.search(o):
        return "MERCH/PROMO"
    if STATLEAD.search(o):
        return "STAT_LEAD"
    if RELATE.search(o):
        return "RELATABLE_HOOK"
    if "?" in o[:120] or re.search(r"\b(ever wondered|wondering|but what)\b", o, re.I):
        return "QUESTION_TEASE"
    if re.match(r"\s*\w[\w\s-]{0,40} is (a |an |the )", o, re.I):
        return "DEFINITION_LEAD"
    return "DIRECT_INTRO"


def closing_pattern(r):
    c = (r.get("closing", "") or "")
    cl = c.lower()
    if re.search(r"(leave a comment|\d+ comments|hoping for your response)", cl):
        return "READER_COMMENTS"
    if re.search(r"\$\d", c) and not re.search(r"invest", cl):
        return "PRODUCT_GRID/PRICES"
    if re.search(r"(shop (our|the)|browse our|explore (our|the)|visit us|our .*collection|shop .*collection)", cl):
        return "BRAND_PRODUCT_TIE"
    if re.search(r"(read more|related articles|similar|other blogs|see related)", cl):
        return "RELATED_LINKS"
    if re.search(r"(invest in|worth it|wise choice|make an informed|final choice|choosing)", cl):
        return "INVESTMENT/VERDICT"
    if re.search(r"(with confidence|your .* your rules|go for it|rock|own it)", cl):
        return "EMPOWERMENT"
    if re.search(r"(she believes|her dedication|about the author|passionate about)", cl):
        return "AUTHOR_BIO"
    return "SUMMARY_WRAP"


def schema_sig(r):
    t = set(r["schema_types"])
    out = []
    if t & {"Article", "BlogPosting", "NewsArticle"}:
        out.append("Article")
    for k in ["FAQPage", "Person", "Organization", "BreadcrumbList", "WebPage",
              "Product", "ImageObject", "HowTo", "ItemList"]:
        if k in t:
            out.append(k)
    return "+".join(out) if out else "(none)"


def band(nums):
    nums = sorted(n for n in nums if n is not None)
    if not nums:
        return "-"
    return f"{min(nums)}–{max(nums)} (med {int(st.median(nums))})"


def main():
    ap = argparse.ArgumentParser(
        description="8-archetype classification + aggregate stats")
    ap.add_argument("--out-dir", required=True,
                    help="Dir with results.json; writes classified.json")
    args = ap.parse_args()

    base = args.out_dir
    R = json.load(open(os.path.join(base, "results.json"), encoding="utf-8"))

    for r in R:
        r["archetype"], r["archetype_reason"] = classify(r)
        r["opening_pattern"] = opening_pattern(r)
        r["closing_pattern"] = closing_pattern(r)
        r["schema_sig"] = schema_sig(r)

    json.dump(R, open(os.path.join(base, "classified.json"), "w", encoding="utf-8"), indent=2)

    if not R:
        print("(results.json is empty — nothing to classify)")
        return

    print("=== PER-ARTICLE CLASSIFICATION ===")
    print(f"{'domain':<24}{'kw':<11}{'us#':>4}{'w':>6}{'H2':>3}{'arch':<20}{'open':<16}{'close'}")
    for r in sorted(R, key=lambda x: (x["archetype"], x["us_min_pos"] or 999)):
        print(f"{r['domain'][:23]:<24}{r['keyword'][:10]:<11}{str(r['us_min_pos'] or '-'):>4}"
              f"{r['word_count']:>6}{r['h2']:>3} {r['archetype']:<19}{r['opening_pattern']:<16}{r['closing_pattern']}")

    print("\n=== ARCHETYPE DISTRIBUTION ===")
    byA = defaultdict(list)
    for r in R:
        byA[r["archetype"]].append(r)
    print(f"{'archetype':<20}{'n':>3}  {'word band':<22}{'H2 band':<16}{'FAQ%':>5}  brand/1k band   common schema")
    for a, rs in sorted(byA.items(), key=lambda x: -len(x[1])):
        faq = round(100 * sum(1 for r in rs if r["has_faq_section"]) / len(rs))
        bsig = Counter(r["schema_sig"] for r in rs).most_common(1)[0][0]
        print(f"{a:<20}{len(rs):>3}  {band([r['word_count'] for r in rs]):<22}"
              f"{band([r['h2'] for r in rs]):<16}{faq:>4}%  {band([r['brand_per_1k'] for r in rs]):<14} {bsig[:34]}")

    print("\n=== OVERALL ===")
    n = len(R)
    print(f"n={n} articles")
    print(f"word_count   : {band([r['word_count'] for r in R])}")
    print(f"H2 count     : {band([r['h2'] for r in R])}")
    print(f"H3 count     : {band([r['h3'] for r in R])}")
    print(f"FAQ section  : {round(100*sum(1 for r in R if r['has_faq_section'])/n)}% ({sum(1 for r in R if r['has_faq_section'])}/{n})")
    print(f"has author   : {round(100*sum(1 for r in R if r['has_author'])/n)}% ({sum(1 for r in R if r['has_author'])}/{n})")
    print(f"authority outlinks>0 : {sum(1 for r in R if r['authority_outlinks']>0)}/{n}  (total auth links across cohort={sum(r['authority_outlinks'] for r in R)})")
    print(f"brand/1k     : {band([r['brand_per_1k'] for r in R])}")
    print(f"has datePublished : {sum(1 for r in R if r['date_published'])}/{n}")
    print("\nschema signatures (freq):")
    for s, c in Counter(r["schema_sig"] for r in R).most_common():
        print(f"   {c:>2}x  {s}")
    print("\nopening patterns:")
    for s, c in Counter(r["opening_pattern"] for r in R).most_common():
        print(f"   {c:>2}x  {s}")
    print("\nclosing patterns:")
    for s, c in Counter(r["closing_pattern"] for r in R).most_common():
        print(f"   {c:>2}x  {s}")


if __name__ == "__main__":
    main()
