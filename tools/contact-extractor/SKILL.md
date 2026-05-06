---
name: contact-extractor
description: Multi-source contact email extraction for KOL / media prospect rows. Given a CSV with personal_site / youtube / podcast_apple columns (e.g. output of linktree-expander or media-press-discovery), enrich each row with up to 3 ranked candidate emails + source label + confidence tier (high/medium/low/none). Triggers on "find contact email", "extract email from creator profile", "deep dig contact info", "enrich KOL contacts".
---

# Contact Extractor

Multi-source email extraction with confidence tiering.

## Quick Start

```bash
python3 scripts/extract_contacts.py linktree_expanded.csv --out linktree_with_contacts.csv
python3 scripts/extract_contacts.py creators.csv --verify --out enriched.csv  # SMTP MX probe
```

## Sources tried (in order)

1. **personal_site root + /about + /contact + /press + /work-with-me**
   - mailto: links → high confidence
   - Visible text emails → medium
2. **YouTube Data API v3** (set `YOUTUBE_API_KEY` env var)
   - Channel description email → high
3. **Apple Podcasts public API** (no key needed)
   - RSS feed iTunes:owner email → high
4. **Email pattern guess** (only if 1-3 produce no hits)
   - `hello@`, `hi@`, `contact@`, `{firstname}@` on personal_site domain
   - Low confidence unless `--verify` runs SMTP MX probe

## Required input columns

- `personal_site` — domain (e.g. `nurtuher.com`)

## Optional input columns

- `youtube` — channel slug or ID (for YouTube source)
- `podcast_apple` — Apple Podcast ID (for podcast RSS)
- `page_title` / `linktree_handle` — used as name hint for pattern guessing

## Output

Same CSV + 5 new columns:
- `contact_email_1`, `contact_email_2`, `contact_email_3` — ranked
- `contact_sources` — e.g. `"site / podcast"` (which sources hit)
- `contact_confidence` — `high` / `medium` / `low` / `none`

## Confidence rubric

| Tier | Source pattern | Action |
|---|---|---|
| **high** | mailto: link OR YouTube API description OR podcast RSS owner | safe to outreach directly |
| **medium** | Visible text email on creator's site | spot-check before outreach |
| **low** | Pattern-guessed email only (no verification) | run `--verify` OR Hunter.io before outreach |
| **none** | No personal_site / no hits | needs IG bio extraction or manual lookup |

## NEVER_DIG_DOMAINS

The script skips visiting known third-party domains that produce noise emails (link shorteners, affiliate platforms, scheduling tools, etc.). See list in source.

## Pilot run (2026-05-06, 45 Linktree-derived KOLs)

After fixing personal_site identification (handle-match scoring) + NEVER_DIG filtering:
- 5 high (real mailto / podcast owner / brand support)
- 4 medium (text emails on creator sites)
- 11 low (pattern guess on validated personal_site)
- 25 none (no findable personal_site — recommend IG bio extraction next)

## Limitations

- Requires `personal_site` in input — for KOLs without one (~50-70% of Linktree pool), this skill produces "none". Use IG bio extraction (Apify or manual) for those.
- Pattern guess at low confidence has ~60% land rate (推算 industry baseline) — recommend SMTP probe or Hunter.io verification before mass send.
- YouTube channel `businessEmail` is hidden behind CAPTCHA — only emails embedded in description are captured.
