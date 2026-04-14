# Backlink KOL Extraction Methodology

## Data Sources (Priority Order)

1. **Refdomains** — Most effective. Shows which domains link to competitors.
2. **Backlinks** — Shows specific URLs, anchors. Can extract social handles.
3. **Competitors** — Traffic overlap sites. Indirect KOL discovery.

## Category Detection Keywords

| Category | Domain Keywords |
|----------|----------------|
| KOL/Review | review, blog, best, guide, test, unbox, everyday, daily, life, personal, vlog, howto, tip |
| Media/Press | news, press, magazine, journal, digest, wire, report, times, post, gazette, herald, media |
| Forum/Community | forum, talk, community, board, club, society, group, nation, hide, addicts, discussion |
| Affiliate/Deal | deals, coupon, discount, compare, versus, vs, pick, choice, finder, shop, affiliate, partner |

## Cross-Validation Scoring

- Links to 5+ competitors → Core industry site (must engage)
- Links to 3-4 competitors → Important channel
- Links to 2 competitors → Worth monitoring

## Priority Score Formula

```
priority = (source_count × 10) + (log10(traffic + 1) × 3) + category_bonus

category_bonus:
  KOL/Review: 20
  Media/Press: 15
  Affiliate/Deal: 10
  Forum/Community: 5
```

## Social Media Extraction Patterns

From backlink URLs:
- `linktr.ee/{username}` → All social links on Linktree page
- `youtube.com/@{channel}` → YouTube channel
- `instagram.com/{user}` → Instagram profile (skip: p, reel, stories, explore)
- `tiktok.com/@{user}` → TikTok profile

## Filter Rules

Skip:
- Generic platforms (Google, Facebook, YouTube, Reddit, Wikipedia, Amazon, etc.)
- Spam backlinks (blogspot bulk sites, .info/.xyz/.tk domains)
- Competitor's own domains
- .gov / .edu domains
