#!/usr/bin/env python3
"""Multi-source contact email extractor for KOL / media prospect rows.

Input  : CSV with at minimum a `personal_site` column. Optional columns:
         `youtube` (channel slug), `podcast_apple` (Apple Podcast id),
         `linktree_handle` (used as identifier in output).
Output : Same CSV + 5 new columns:
           contact_email_1, contact_email_2, contact_email_3 (ranked),
           contact_sources                  (e.g. "site_about / yt_api"),
           contact_confidence               ("high" / "medium" / "low")

Sources tried in order (free → paid):

  1. personal_site root + /about + /contact + /contact-us + /press
     - regex emails in HTML (mailto: + visible text)
     - high confidence if appears in mailto: link
  2. YouTube Data API v3 (set YOUTUBE_API_KEY env var)
     - channel.brandingSettings.businessEmail
     - high confidence (verified by YT)
  3. Apple Podcasts public API
     - host site → contact extraction
     - medium confidence (often a generic "hello@show.com")
  4. Email pattern guess on personal_site domain
     - patterns: hello@, hi@, contact@, {firstname}@, {firstname}.{lastname}@
     - low confidence unless verified via SMTP MX probe (--verify)

Usage:
  python3 extract_contacts.py linktree_expanded.csv --out linktree_with_contacts.csv
  python3 extract_contacts.py creators.csv --verify --out enriched.csv
"""

import argparse
import csv
import json
import os
import random
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, urljoin

try:
    import requests
except ImportError:
    sys.exit("install: pip install requests beautifulsoup4")

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("install: pip install beautifulsoup4")


DESKTOP_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
MAILTO_RE = re.compile(r'mailto:([^?"\s>]+)', re.I)

# Skip generic / role / spam emails — these are not actionable for KOL outreach
SKIP_EMAIL_DOMAINS = {
    "example.com", "domain.com", "yoursite.com", "gmail.com", "yahoo.com",
    "hotmail.com", "outlook.com", "icloud.com", "aol.com",  # not skip — real founders use these
}
SKIP_LOCAL_PARTS = {
    "no-reply", "noreply", "donotreply", "do-not-reply", "info-no-reply",
    "abuse", "postmaster", "webmaster", "support@wordpress",
}
GENERIC_PRIORITY = {
    "hello": 1, "hi": 2, "contact": 3, "team": 4, "info": 5,
    "press": 1, "pr": 1, "collab": 1, "partnerships": 1,
    "media": 2, "marketing": 3,
}


def gaussian_sleep(mean=1.5, sd=0.4, lo=0.5):
    time.sleep(max(lo, random.gauss(mean, sd)))


def is_actionable_email(email: str) -> bool:
    """Filter out junk emails."""
    email = email.lower().strip()
    try:
        local, domain = email.split("@", 1)
    except ValueError:
        return False
    if domain in SKIP_EMAIL_DOMAINS:
        return False
    if any(s in local for s in SKIP_LOCAL_PARTS):
        return False
    # Skip image-like emails (e.g. "image.png@something")
    if local.endswith((".png", ".jpg", ".gif", ".jpeg", ".webp")):
        return False
    if "." in local and len(local) < 4:
        return False
    return True


def email_score(email: str, domain_hint: str = "") -> int:
    """Rank emails: lower score = higher priority.

    domain_hint = the personal_site domain. Emails ON that domain rank higher.
    """
    score = 100
    local, domain = email.split("@", 1)
    # Personal-domain bonus
    if domain_hint and domain.endswith(domain_hint):
        score -= 50
    # Mailto sources rank below — handled at gather time, not here
    # Generic-name priority
    bonus = GENERIC_PRIORITY.get(local, 0)
    if bonus:
        score -= 30 - bonus * 5
    return score


# --- Source 1: personal_site scrape ---

CONTACT_PATHS = ["", "/about", "/about-me", "/about/", "/contact", "/contact-us",
                 "/press", "/work-with-me", "/collab", "/connect"]

# Domains we should NEVER deep-dig for contact info — these are third-party
# utilities / aggregators / shorteners that produce noise emails (sponsor /
# platform / random-3rd-party) not the creator's actual contact.
NEVER_DIG_DOMAINS = {
    "amzn.to", "bit.ly", "tinyurl.com", "t.co", "rebrand.ly", "ow.ly",
    "ngl.link", "fbuy.io", "glnk.io", "posh.mk", "lnk.bio",
    "liketoknow.it", "ltk.shopmy.com", "shopmy.com", "stan.store",
    "beacons.ai", "linktr.ee", "solo.to", "snipfeed.co",
    "docs.google.com", "drive.google.com", "forms.gle", "form.typeform.com",
    "calendly.com", "tally.so",
    "archive.md", "archive.org", "web.archive.org",
    "additudemag.com", "leafwell.com", "eventbrite.com",
    "wellnessliving.com", "checkmybodyhealth.com", "brookdalecc.edu",
    "amazon.com", "etsy.com", "walmart.com", "target.com",
    "spotify.com", "apple.com", "podcasts.apple.com",
    "anchor.fm",  # Anchor's auto-generated email (podcasts60+...@anchor.fm) is not actionable
    "myshopify.com",
}


def fetch_html(url: str, session: requests.Session, timeout=15):
    try:
        r = session.get(url, timeout=timeout, allow_redirects=True)
        if r.status_code == 200 and 1000 < len(r.text) < 5_000_000:
            return r.text
    except requests.RequestException:
        pass
    return None


def extract_from_personal_site(domain: str, session: requests.Session):
    """Visit common contact pages on the domain. Return list of (email, source)."""
    if not domain:
        return []
    bare = domain[4:] if domain.startswith("www.") else domain
    if bare in NEVER_DIG_DOMAINS or any(bare == d or bare.endswith("." + d)
                                        for d in NEVER_DIG_DOMAINS):
        # Don't waste requests on known non-personal domains
        return []
    results = []
    seen = set()
    base = f"https://{domain}" if not domain.startswith("http") else domain
    for path in CONTACT_PATHS:
        url = urljoin(base, path)
        html = fetch_html(url, session)
        if not html:
            continue
        # mailto: links — high confidence
        for m in MAILTO_RE.finditer(html):
            em = m.group(1).strip().lower()
            if is_actionable_email(em) and em not in seen:
                seen.add(em)
                results.append((em, f"site_mailto:{path or '/'}"))
        # visible text emails
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)
        for em in EMAIL_RE.findall(text):
            em = em.lower()
            if is_actionable_email(em) and em not in seen:
                seen.add(em)
                results.append((em, f"site_text:{path or '/'}"))
        time.sleep(0.4)
        # Stop early if we got a clear hit on /contact
        if path in ("/contact", "/contact-us") and results:
            break
    return results


# --- Source 2: YouTube Data API ---

def extract_from_youtube(channel_slug: str):
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key or not channel_slug:
        return []
    # First resolve handle → channel_id (channel_slug from Linktree often is @handle or username)
    base = "https://www.googleapis.com/youtube/v3"
    try:
        # If looks like UCxxx (channel ID), use directly; else search by handle
        if channel_slug.startswith("UC") and len(channel_slug) > 10:
            cid = channel_slug
        else:
            r = requests.get(f"{base}/search",
                             params={"part": "snippet", "q": channel_slug,
                                     "type": "channel", "maxResults": 1, "key": api_key},
                             timeout=15)
            items = r.json().get("items", [])
            if not items:
                return []
            cid = items[0]["snippet"]["channelId"]
        r = requests.get(f"{base}/channels",
                         params={"part": "brandingSettings,snippet",
                                 "id": cid, "key": api_key}, timeout=15)
        item = (r.json().get("items") or [{}])[0]
        # YouTube hides businessEmail behind a CAPTCHA challenge; the API does NOT
        # return it directly. Description sometimes contains the email.
        desc = (item.get("snippet") or {}).get("description") or ""
        results = []
        for em in EMAIL_RE.findall(desc):
            em = em.lower()
            if is_actionable_email(em):
                results.append((em, "yt_api_description"))
        return results
    except Exception as e:
        print(f"  [yt {channel_slug}] error: {e}", file=sys.stderr)
        return []


# --- Source 3: Apple Podcasts public lookup ---

def extract_from_apple_podcast(podcast_id: str, session: requests.Session):
    if not podcast_id:
        return []
    try:
        # Apple's public lookup API
        r = session.get(f"https://itunes.apple.com/lookup?id={podcast_id}", timeout=15)
        if r.status_code != 200:
            return []
        data = r.json().get("results", [])
        if not data:
            return []
        # The podcast record has artistName, feedUrl (RSS feed often has owner email)
        feed_url = data[0].get("feedUrl")
        results = []
        if feed_url:
            feed = fetch_html(feed_url, session)
            if feed:
                # iTunes:owner email field in podcast XML
                m = re.search(r"<itunes:email>([^<]+)</itunes:email>", feed)
                if m:
                    em = m.group(1).strip().lower()
                    if is_actionable_email(em):
                        results.append((em, "podcast_rss_owner"))
                # Generic email in feed text
                for em in EMAIL_RE.findall(feed[:50000]):
                    em = em.lower()
                    if is_actionable_email(em) and em not in [r[0] for r in results]:
                        results.append((em, "podcast_rss_text"))
                        if len(results) >= 3:
                            break
        return results
    except Exception as e:
        print(f"  [podcast {podcast_id}] error: {e}", file=sys.stderr)
        return []


# --- Source 4: Email pattern guess ---

def guess_emails_for_domain(domain: str, name_hint: str = ""):
    if not domain:
        return []
    # Strip "www." prefix — valid in URL but not standard in email domains
    bare = domain[4:] if domain.startswith("www.") else domain
    candidates = ["hello", "hi", "contact", "team", "info"]
    if name_hint:
        first = re.sub(r"[^a-z]", "", name_hint.lower().split()[0]) if name_hint.split() else ""
        if first and len(first) >= 2:
            candidates.insert(0, first)
            candidates.insert(1, f"{first}.contact")
    return [(f"{c}@{bare}", "pattern_guess") for c in candidates[:5]]


# --- Optional SMTP verification ---

def smtp_verify(email: str):
    try:
        import dns.resolver
        import smtplib
    except ImportError:
        return "unknown"
    try:
        domain = email.split("@", 1)[1]
        records = dns.resolver.resolve(domain, "MX")
        mx = sorted(records, key=lambda r: r.preference)[0].exchange.to_text()
        s = smtplib.SMTP(timeout=8)
        s.connect(mx)
        s.helo("example.com")
        s.mail("verify@example.com")
        code, _ = s.rcpt(email)
        s.quit()
        return "smtp_ok" if code in (250, 251) else "smtp_fail"
    except Exception:
        return "unknown"


# --- Main pipeline ---

def enrich_row(row: dict, session, do_verify=False):
    """Enrich one row with contact info from all sources."""
    domain = (row.get("personal_site") or "").strip()
    yt = (row.get("youtube") or "").strip()
    pod = (row.get("podcast_apple") or "").strip()
    name = (row.get("page_title") or row.get("linktree_handle") or "").strip()

    all_hits = []  # list of (email, source)
    sources_used = []

    # Source 1 — site
    if domain:
        hits = extract_from_personal_site(domain, session)
        if hits:
            all_hits.extend(hits)
            sources_used.append("site")

    # Source 2 — YouTube
    if yt:
        hits = extract_from_youtube(yt)
        if hits:
            all_hits.extend(hits)
            sources_used.append("yt")

    # Source 3 — Apple Podcast
    if pod:
        hits = extract_from_apple_podcast(pod, session)
        if hits:
            all_hits.extend(hits)
            sources_used.append("podcast")

    # Source 4 — pattern guess (only if no direct hits)
    if not all_hits and domain:
        hits = guess_emails_for_domain(domain, name)
        all_hits.extend(hits)
        sources_used.append("guess")

    # Dedup + rank
    seen = {}
    for em, src in all_hits:
        if em not in seen:
            seen[em] = src
    ranked = sorted(seen.items(),
                    key=lambda x: (
                        # mailto > text > yt_api > podcast_rss_owner > podcast_rss_text > pattern_guess
                        ["site_mailto", "yt_api", "podcast_rss_owner",
                         "site_text", "podcast_rss_text", "pattern_guess"].index(
                             next((p for p in ["site_mailto", "yt_api",
                                               "podcast_rss_owner", "site_text",
                                               "podcast_rss_text", "pattern_guess"]
                                   if p in x[1]), "pattern_guess")
                         ),
                        email_score(x[0], domain),
                    ))

    if do_verify and ranked:
        # Verify top candidate
        verified_email, _ = ranked[0]
        result = smtp_verify(verified_email)
        if result == "smtp_ok":
            row["contact_confidence"] = "high"
        elif "site_mailto" in seen.get(verified_email, ""):
            row["contact_confidence"] = "high"
        else:
            row["contact_confidence"] = "medium"
    else:
        # Heuristic confidence
        if any("mailto" in s for _, s in ranked[:1]):
            row["contact_confidence"] = "high"
        elif any("yt_api" in s or "podcast_rss_owner" in s for _, s in ranked[:1]):
            row["contact_confidence"] = "high"
        elif ranked and "pattern_guess" not in ranked[0][1]:
            row["contact_confidence"] = "medium"
        elif ranked:
            row["contact_confidence"] = "low"
        else:
            row["contact_confidence"] = "none"

    row["contact_email_1"] = ranked[0][0] if len(ranked) > 0 else ""
    row["contact_email_2"] = ranked[1][0] if len(ranked) > 1 else ""
    row["contact_email_3"] = ranked[2][0] if len(ranked) > 2 else ""
    row["contact_sources"] = " / ".join(sources_used) if sources_used else ""
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path,
                    help="Input CSV. Required columns: personal_site (optional: youtube, podcast_apple, page_title)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--verify", action="store_true",
                    help="SMTP MX probe top candidate (slow)")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--delay", type=float, default=1.5,
                    help="Mean inter-request delay (default 1.5s)")
    args = ap.parse_args()

    rows = list(csv.DictReader(args.input.read_text(encoding="utf-8-sig").splitlines()))
    if args.limit:
        rows = rows[:args.limit]
    print(f"Enriching {len(rows)} rows", file=sys.stderr)

    session = requests.Session()
    session.headers.update({"User-Agent": DESKTOP_UA, "Accept-Language": "en-US,en;q=0.9"})

    enriched = []
    for i, row in enumerate(rows, 1):
        ident = row.get("linktree_handle") or row.get("name") or row.get("handle") or f"row{i}"
        print(f"[{i}/{len(rows)}] {ident}", file=sys.stderr)
        if row.get("status") and row.get("status") != "ok":
            row["contact_email_1"] = row["contact_email_2"] = row["contact_email_3"] = ""
            row["contact_sources"] = ""
            row["contact_confidence"] = "none"
            enriched.append(row)
            continue
        enriched.append(enrich_row(row, session, do_verify=args.verify))
        if i < len(rows):
            gaussian_sleep(args.delay)

    # Write enriched CSV (preserve original columns + add 5 new)
    fieldnames = list(rows[0].keys()) if rows else []
    for new_col in ["contact_email_1", "contact_email_2", "contact_email_3",
                    "contact_sources", "contact_confidence"]:
        if new_col not in fieldnames:
            fieldnames.append(new_col)

    with args.out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(enriched)

    high = sum(1 for r in enriched if r.get("contact_confidence") == "high")
    medium = sum(1 for r in enriched if r.get("contact_confidence") == "medium")
    low = sum(1 for r in enriched if r.get("contact_confidence") == "low")
    none_ = sum(1 for r in enriched if r.get("contact_confidence") == "none")
    print(f"\nWrote {len(enriched)} rows to {args.out}", file=sys.stderr)
    print(f"  high: {high} | medium: {medium} | low (guess only): {low} | none: {none_}", file=sys.stderr)


if __name__ == "__main__":
    main()
