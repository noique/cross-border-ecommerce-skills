#!/usr/bin/env python3
"""Expand Linktree handles into full social/outbound profiles.

Input : handles.txt (one handle per line, e.g. `example_creator`, `brand.x`)
        OR a CSV with column `username` (Linktree handle slug).

Output: linktree_expanded.csv

Each row:
  linktree_handle, page_title, bio, ig, tiktok, youtube, twitter, facebook,
  substack, podcast_apple, podcast_spotify, personal_site, email_visible,
  outbound_count, top_categories, primary_brand_partner, scraped_at, status

Linktree pages serve a Next.js app — we parse `__NEXT_DATA__` JSON for stable
extraction (vs scraping DOM which is React-rendered + class-hash-volatile).

No Cloudflare, simple `requests` works. Default pacing 1.5s between requests.

Usage:
  python3 expand_linktree.py handles.txt --out linktree_expanded.csv
  python3 expand_linktree.py kol_prospects_social.csv --col username --out lt.csv
  python3 expand_linktree.py handles.txt --delay 2.5 --out lt.csv
"""

import argparse
import csv
import datetime
import json
import random
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    sys.exit("install: pip install requests")


DESKTOP_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

NEXT_DATA_RE = re.compile(
    r'__NEXT_DATA__"[^>]*type="application/json"[^>]*>(.*?)</script>',
    re.DOTALL,
)
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

# Match social handles from URLs.  Order matters; first-match wins.
SOCIAL_PATTERNS = [
    ("ig",            re.compile(r"^https?://(?:www\.)?instagram\.com/([^/?#]+)")),
    ("tiktok",        re.compile(r"^https?://(?:www\.)?tiktok\.com/@?([^/?#]+)")),
    ("youtube",       re.compile(r"^https?://(?:www\.)?youtube\.com/(?:c/|channel/|@|user/)([^/?#]+)")),
    ("twitter",       re.compile(r"^https?://(?:www\.)?(?:twitter|x)\.com/([^/?#]+)")),
    ("facebook",      re.compile(r"^https?://(?:www\.)?facebook\.com/(?:pg/|pages/)?([^/?#]+)")),
    ("substack",      re.compile(r"^https?://([a-z0-9_\-]+)\.substack\.com")),
    ("podcast_apple", re.compile(r"^https?://podcasts\.apple\.com/[^/]+/podcast/[^/]+/(?:id)?(\d+)")),
    ("podcast_spotify", re.compile(r"^https?://open\.spotify\.com/show/([a-zA-Z0-9]+)")),
    ("pinterest",     re.compile(r"^https?://(?:www\.)?pinterest\.com/([^/?#]+)")),
    ("twitch",        re.compile(r"^https?://(?:www\.)?twitch\.tv/([^/?#]+)")),
]

# Skip — these are linktree-internal / generic platform links (not the user's social)
SKIP_HOSTS = {
    "linktr.ee", "assets.production.linktr.ee",
    "fonts.googleapis.com", "fonts.gstatic.com",
    "www.googletagmanager.com", "google.com",
    "form.typeform.com",  # often used by users for surveys, not their primary social
}

# Domains that should NEVER be classified as `personal_site`. These are
# third-party utilities / shorteners / aggregators / docs / scheduling tools that
# happen to appear as outbound links but are not the creator's own site.
NON_PERSONAL_HOSTS = {
    # link shorteners
    "amzn.to", "bit.ly", "tinyurl.com", "t.co", "rebrand.ly", "ow.ly",
    "ngl.link", "fbuy.io", "glnk.io", "posh.mk", "lnk.bio",
    # affiliate / shoppable / link-in-bio platforms
    "liketoknow.it", "ltk.shopmy.com", "shopmy.com", "stan.store",
    "beacons.ai", "linktr.ee", "solo.to", "snipfeed.co", "withkoji.com",
    # docs / forms / scheduling / archive utilities
    "docs.google.com", "drive.google.com", "forms.gle", "form.typeform.com",
    "calendly.com", "tally.so", "savee.it",
    "archive.md", "archive.org", "web.archive.org",
    # major retailers / generic platforms (not creator's own)
    "amazon.com", "etsy.com", "walmart.com", "target.com",
    "spotify.com", "apple.com", "podcasts.apple.com",
    "youtube.com", "instagram.com", "tiktok.com", "twitter.com", "x.com",
    "facebook.com", "pinterest.com", "twitch.tv", "linkedin.com",
    "patreon.com", "kofi.com", "ko-fi.com", "buymeacoffee.com",
    "github.com", "medium.com", "substack.com",
    # generic shopify subdomains (creator brands ARE shopify, but if domain is
    # raw {something}.myshopify.com we don't want it as the canonical site)
    "myshopify.com",
}


def categorize(url: str, title: str) -> str:
    host = urlparse(url).netloc.lower().lstrip("www.")
    title_lower = (title or "").lower()
    if any(s in host for s in ("instagram", "tiktok", "youtube", "twitter", "x.com",
                               "facebook", "pinterest", "twitch")):
        return "social_post"
    if "substack.com" in host or ".substack.com" in url:
        return "newsletter"
    if "apple.com/podcast" in url or "spotify.com/show" in url or "anchor.fm" in host:
        return "podcast"
    if any(s in host for s in ("amazon.", "shop", "etsy.com", "shopify")):
        return "shop"
    if any(s in title_lower for s in ("shop", "buy", "cart", "store")):
        return "shop"
    if any(s in title_lower for s in ("subscribe", "newsletter", "join")):
        return "newsletter"
    if any(s in title_lower for s in ("blog", "post", "article", "read")):
        return "blog"
    if any(s in title_lower for s in ("episode", "podcast", "listen")):
        return "podcast"
    if any(s in title_lower for s in ("course", "class", "workshop", "free")):
        return "lead_magnet"
    return "other"


def parse_linktree(html: str, handle: str = ""):
    m = NEXT_DATA_RE.search(html)
    if not m:
        return None
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return None
    page = data.get("props", {}).get("pageProps", {})
    if not page:
        return None
    acct = page.get("account") or {}
    links = page.get("links") or acct.get("links") or []

    out = {
        "page_title": acct.get("pageTitle") or "",
        "bio":        (acct.get("description") or "").strip(),
        "social_count": len(acct.get("socialLinks") or []),
        "_handle":    handle,
    }

    for s in acct.get("socialLinks") or []:
        url = s.get("url") or ""
        for key, pat in SOCIAL_PATTERNS:
            mm = pat.match(url)
            if mm:
                out[key] = mm.group(1)
                break

    outbound = []
    cat_count = {}
    candidate_sites = []   # list of (host, title) for personal_site scoring
    for L in links:
        url = (L.get("url") or "").strip()
        title = (L.get("title") or L.get("label") or "").strip()
        if not url or url.startswith("javascript:"):
            continue
        host = urlparse(url).netloc.lower()
        if host in SKIP_HOSTS:
            continue
        for key, pat in SOCIAL_PATTERNS:
            mm = pat.match(url)
            if mm and key not in out:
                out[key] = mm.group(1)
                break
        cat = categorize(url, title)
        cat_count[cat] = cat_count.get(cat, 0) + 1
        outbound.append((cat, host))
        # Gather personal_site candidates — only blog/other/shop, not blocked
        if cat in ("blog", "other", "shop"):
            bare_host = host[4:] if host.startswith("www.") else host
            blocked = (
                bare_host in NON_PERSONAL_HOSTS
                or any(bare_host == d or bare_host.endswith("." + d) for d in NON_PERSONAL_HOSTS)
            )
            if not blocked:
                candidate_sites.append((host, title))

    # Pick personal_site by scoring against the linktree handle.
    # Only return if there's a confident match (handle in domain), else leave empty.
    handle_norm = re.sub(r"[^a-z0-9]", "", (out.get("_handle") or "").lower())
    out.pop("_handle", None)
    best_score = 0
    for host, title in candidate_sites:
        bare = host[4:] if host.startswith("www.") else host
        first_label = bare.split(".")[0].lower()
        host_norm = re.sub(r"[^a-z0-9]", "", first_label)
        score = 0
        if handle_norm and host_norm:
            if handle_norm == host_norm:
                score += 100
            elif handle_norm in host_norm or host_norm in handle_norm:
                score += 80
            elif len(handle_norm) >= 5 and handle_norm[:5] in host_norm:
                score += 40
        if bare.count(".") == 1 and bare.endswith((".com", ".co", ".net", ".org", ".me")):
            score += 10
        if score > best_score:
            best_score = score
            out["_best_site"] = host
    if best_score >= 40:
        out["personal_site"] = out.pop("_best_site", None)
    else:
        out.pop("_best_site", None)

    out["outbound_count"] = len(outbound)
    top_cats = sorted(cat_count.items(), key=lambda x: -x[1])[:3]
    out["top_categories"] = " / ".join(f"{c}({n})" for c, n in top_cats)

    brand_hosts = [h for c, h in outbound if c == "shop"]
    if brand_hosts:
        brand_count = {}
        for h in brand_hosts:
            brand_count[h] = brand_count.get(h, 0) + 1
        out["primary_brand_partner"] = max(brand_count.items(), key=lambda x: x[1])[0]

    em = EMAIL_RE.search(out["bio"])
    if em:
        out["email_visible"] = em.group(0)

    return out


def fetch(handle: str, session: requests.Session, retries: int = 2):
    url = f"https://linktr.ee/{handle}"
    for attempt in range(retries + 1):
        try:
            r = session.get(url, timeout=20)
            if r.status_code == 200 and len(r.text) > 5000:
                return r.text
            if r.status_code == 404:
                return None
        except requests.RequestException as e:
            if attempt == retries:
                print(f"  [{handle}] error after {retries} retries: {e}", file=sys.stderr)
                return None
            time.sleep(2 + attempt * 2)
    return None


def load_handles(path: Path, col):
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".csv":
        if not col:
            sys.exit("--col REQUIRED when input is CSV (column with linktree handle)")
        rdr = csv.DictReader(text.splitlines())
        out = []
        for row in rdr:
            v = (row.get(col) or "").strip()
            if v.startswith("http"):
                m = re.match(r"https?://linktr\.ee/([^/?#]+)", v)
                if m:
                    v = m.group(1)
            plat = row.get("platform")
            if plat and plat != "linktree":
                continue
            if v and not v.startswith("#"):
                out.append(v)
        return out
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("http"):
            m = re.match(r"https?://linktr\.ee/([^/?#]+)", line)
            if m: line = m.group(1)
        out.append(line)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path,
                    help="Path to handles.txt or CSV (need --col username)")
    ap.add_argument("--col", default=None,
                    help="If input is CSV: column containing handle / linktree URL")
    ap.add_argument("--out", type=Path, default=Path("linktree_expanded.csv"))
    ap.add_argument("--delay", type=float, default=1.5,
                    help="Mean delay between requests (gaussian, sd=0.4). Default 1.5s.")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    handles = load_handles(args.input, args.col)
    if args.limit:
        handles = handles[:args.limit]
    if not handles:
        sys.exit("No handles loaded.")
    print(f"Loaded {len(handles)} Linktree handles", file=sys.stderr)

    session = requests.Session()
    session.headers.update({"User-Agent": DESKTOP_UA, "Accept-Language": "en-US,en;q=0.9"})

    cols = ["linktree_handle","page_title","bio","ig","tiktok","youtube","twitter",
            "facebook","substack","podcast_apple","podcast_spotify","pinterest",
            "twitch","personal_site","email_visible","outbound_count","top_categories",
            "primary_brand_partner","social_count","scraped_at","status"]

    rows = []
    for i, handle in enumerate(handles, 1):
        print(f"[{i}/{len(handles)}] {handle}", file=sys.stderr)
        html = fetch(handle, session)
        if not html:
            rows.append({"linktree_handle": handle, "status": "fetch_failed",
                         "scraped_at": datetime.datetime.now().isoformat(timespec="seconds")})
            continue
        parsed = parse_linktree(html, handle=handle)
        if not parsed:
            rows.append({"linktree_handle": handle, "status": "parse_failed",
                         "scraped_at": datetime.datetime.now().isoformat(timespec="seconds")})
            continue
        rows.append({
            "linktree_handle": handle,
            "scraped_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "status": "ok",
            **parsed,
        })
        if i < len(handles):
            time.sleep(max(0.5, random.gauss(args.delay, 0.4)))

    with args.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    ok = sum(1 for r in rows if r.get("status") == "ok")
    print(f"\nWrote {len(rows)} rows ({ok} ok) to {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
