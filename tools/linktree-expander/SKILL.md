---
name: linktree-expander
description: Expand a list of Linktree handles (e.g. example_creator, brand_x) into a full table of each user's social handles + outbound links + bio + visible email. Use when you have a list of Linktree slugs from KOL discovery (output of backlink-kol-extractor or similar) and need to enrich them into actionable per-creator profiles. Triggers on "expand linktree", "linktree to social handles", "enrich linktree creators", "find IG/TikTok behind linktree".
---

# Linktree Expander

Given a list of Linktree slugs, produce a per-creator profile with all formal social handles (IG / TikTok / YouTube / Substack / etc.), outbound link categorization, bio text, and visible contact email.

## Why useful

Linktree is the dominant link-in-bio service. KOL discovery pipelines (e.g. `tools/backlink-kol-extractor`) often surface Linktree handles as the only contact point for a creator. Each `linktr.ee/{handle}` is a portfolio listing all their socials + featured links. Expanding 45 Linktree handles takes ~2 min and yields ~5-15 social handles per creator.

## Quick Start

```bash
# Input: text file (one handle per line) OR CSV (need --col)
python3 scripts/expand_linktree.py handles.txt --out linktree_expanded.csv

# From a CSV (e.g. kol_prospects_social.csv produced by backlink-kol-extractor)
python3 scripts/expand_linktree.py kol_prospects_social.csv --col username --out lt.csv

# Slow it down (default 1.5s between requests)
python3 scripts/expand_linktree.py handles.txt --delay 3.0 --out lt.csv
```

## Output Schema

`linktree_expanded.csv`:

| Column | Description |
|---|---|
| `linktree_handle` | Slug |
| `page_title` | Display name on Linktree page |
| `bio` | Description text (often contains email or pitch) |
| `ig`, `tiktok`, `youtube`, `twitter`, `facebook` | Social handles (no full URL, just the slug) |
| `substack`, `podcast_apple`, `podcast_spotify`, `pinterest`, `twitch` | Same |
| `personal_site` | First non-social outbound domain (heuristic for own site) |
| `email_visible` | Email regex-matched in bio |
| `outbound_count` | Total outbound link cards |
| `top_categories` | Top 3 outbound link categories (e.g. "social_post(8) / shop(3) / blog(2)") |
| `primary_brand_partner` | Most-frequent shop/affiliate host in outbound (signal of brand collab) |
| `scraped_at` | ISO timestamp |
| `status` | "ok" / "fetch_failed" / "parse_failed" |

## How it works

Linktree pages serve a Next.js app. The user-clickable links are NOT in `<a href="">` tags — they're embedded in the `__NEXT_DATA__` JSON blob. The script parses that JSON for stable extraction (vs DOM scraping which uses React-rendered class hashes that break on every Linktree deploy).

Key paths in `__NEXT_DATA__`:
- `props.pageProps.account` → username, pageTitle, description (bio), socialLinks
- `props.pageProps.links` → outbound link cards (title + url + type)

## When NOT to use

- Other link-in-bio services (`bio.link`, `beacons.ai`, `solo.to`, etc.) — those have different page structures. Adapt this skill to a sister `tools/linkbio-expander/` if needed.
- Detailed engagement data (followers, ER) — Linktree doesn't expose these. After running this skill, feed the IG/TikTok/YouTube handles into a sister skill (or Apify actor) for engagement enrichment.

## Cloudflare / anti-bot

Linktree currently does NOT use Cloudflare (verified 2026-05-06). Plain `requests` works. If this changes, switch to the `_fetcher.py` pattern from `outbound-prospecting/media-press-discovery/scripts/_fetcher.py` (supports `--via remote-chrome` / `--via apify`).

## Performance

- Single-thread, sequential. ~1.5s/page default delay → ~2 min for 45 handles.
- Linktree's rate limit is forgiving but not infinite — sustained >5 req/sec triggers temporary 429.
- For 1000+ handles, consider partitioning (split handles file across machines, run in parallel).

## Known failure modes (实测 2026-05-06)

| Mode | Frequency | Handling |
|---|---|---|
| Handle deleted (404) | ~5% | row marked `status=fetch_failed` (e.g. `knixwear` failed in pilot) |
| `__NEXT_DATA__` not in HTML (page variant) | <1% | row marked `status=parse_failed`, manual fallback |
| Account locked / private | rare | same as 404 |
| Outbound URLs hidden behind Linktree's redirect (`linktr.ee/r/...`) | rare | follow with `requests.head()` to resolve final URL |

## Pilot run results (2026-05-06)

Run on a 45-handle seed list (extracted from
`kol_prospects_social.csv` via `tools/backlink-kol-extractor` for a
single domain category):

```
Wrote 45 rows (44 ok) to linktree_expanded.csv
Field hit rates:
  ig: 26/45 (58%)
  tiktok: 18/45 (40%)
  youtube: 8/45 (18%)
  twitter: 3/45
  facebook: 11/45
  substack: 0/45  (none of these creators primarily on Substack)
  podcast_apple: 5/45 / podcast_spotify: 5/45
  personal_site: 44/45 (98%)
  bio_has_content (>20 chars): 23/45
  email_visible_in_bio: 0/45  (Linktree bios in 2026 are emoji-heavy, emails rare)
```

## Related skills

- [`tools/backlink-kol-extractor`](https://github.com/noique/cross-border-ecommerce-skills/tree/main/tools/backlink-kol-extractor) — produces the input handles list
- [`outbound-prospecting/media-press-discovery`](https://github.com/noique/cross-border-ecommerce-skills/tree/main/outbound-prospecting/media-press-discovery) — for media journalists (different anchor: Muckrack, not Linktree)
- (Future) `tools/linkbio-expander/` — same concept for `bio.link`, `beacons.ai`, etc.
- (Future) `tools/social-platform-enricher/` — IG/TikTok/YouTube engagement data via Apify
