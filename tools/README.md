# Tools

Standalone Python utilities used by skills in this repo. Each tool can also be used independently of any SKILL. Each tool is a multi-file package with its own `SKILL.md` + `scripts/` + `references/` + `templates/`.

## Inventory (5 tools as of v3.6)

| Tool | Purpose | Skill triggers |
|---|---|---|
| [backlink-kol-extractor](#backlink-kol-extractor) | KOL / media / affiliate prospect discovery from Semrush refdomains xlsx | `influencer-marketing`, `dsite-seo-playbook` |
| [trustpilot](#trustpilot) | Trustpilot review scraper + AI sentiment / topic analysis | `trustpilot-voc-quick`, `trustpilot-voc-deep` |
| [linktree-expander](#linktree-expander) | Batch-enrich Linktree handles → per-creator social profile + outbound link categorization | KOL discovery downstream of `backlink-kol-extractor` |
| [contact-extractor](#contact-extractor) | Multi-source contact email extraction with confidence tiering | KOL / press outreach prep, post `linktree-expander` or `media-press-discovery` |
| [serp-content-teardown](#serp-content-teardown) | Reverse-engineer winning content shape + SEO/GEO/keyword/backlink strategy from Semrush serp_urls + broad-match xlsx + competitor HTML | `dsite-seo-playbook`, `brand-market-scan`; pairs with `backlink-kol-extractor` + `structured-data-buildout` |

---

## backlink-kol-extractor

Extracts KOL / influencer / media / affiliate candidates from Semrush competitor backlink & refdomains xlsx exports.

**Standalone usage** (any niche, not limited to cross-border e-commerce):

```bash
cd tools/backlink-kol-extractor
python3 scripts/extract_kol.py <semrush_data_dir> \
  --output prospects.csv \
  --min-sources 2 \
  --min-traffic 500
```

**Input layout:**
```
semrush_data/
  competitor1.com/
    competitor1.com-backlinks_refdomains.xlsx
    competitor1.com-backlinks.xlsx
    competitor1.com-organic.Competitors-us-*.xlsx
  competitor2.com/
    ...
```

**Output:** CSV sorted by `priority_score` with columns `domain, category, priority_score, traffic, backlinks, source_count, sources`.

**Used by (conditional activation):**
- `brand-strategy/influencer-marketing.md` → Step 2.5 (KOL discovery from competitor backlinks)
- `brand-strategy/dsite-seo-playbook.md` → Step 4.6 (external link gap analysis, anchor text reverse learning)

Both skills skip their Semrush modules gracefully if this tool's data is not provided.

See [backlink-kol-extractor/SKILL.md](backlink-kol-extractor/SKILL.md) and [references/methodology.md](backlink-kol-extractor/references/methodology.md) for details.

---

## trustpilot

Selenium-based Trustpilot review scraper with chained-proxy rotation, AI sentiment analysis, multi-language reviews, and full statistical reporting.

**Standalone usage:**

```bash
cd tools/trustpilot
# Set env vars (see config.py for proxy schema)
export TP_PROXY_1="HOST:PORT:USER:PASS"
export TP_PROXY_2="HOST:PORT:USER:PASS"

python3 main.py \
  --url https://www.trustpilot.com/review/yourbrand.com \
  --use_local_only \
  --skip_ai \
  --cutoff_date 2025-11-06 \
  --skip_merge
```

**Key flags:**
- `--cutoff_date YYYY-MM-DD` — stop after a page whose oldest review is older than cutoff. Trustpilot is sorted newest-first under `?sort=recency`, so this efficiently bounds scrapes to a recent window (e.g. last 6 months for VOC analysis).
- `--use_local_only` — skip proxy chain (use direct connection)
- `--skip_ai` — skip AI sentiment / topic / report generation (raw CSV scrape only). Required if downstream `generate_report()` not in scope.
- `--skip_merge` — skip merging multi-thread output

**v3.4 rebuild (2026-05-06)** addresses Trustpilot's 2026 DOM update + several silent-failure modes:
- Modern selectors using `[data-consumer-name-typography]` / `[data-consumer-country-typography]` / `[data-service-review-rating]` / `[data-service-review-text-typography]` / `[data-service-review-title-typography]` (replaces 110-line sibling-XPath fallback chain).
- Use `textContent` not `.text` (avoids lazy-render visibility quirks).
- URL: append `&sort=recency` (without it, Trustpilot serves "relevance" widget = snippet-only DOM with no rating / country / title metadata for some brands).
- User-Agent pinned to desktop (`fake_useragent` would otherwise return iPhone UAs ~30% of the time, triggering Trustpilot's mobile snippet-only layout).
- New `--cutoff_date` flag (efficiently bound scrapes to N-month windows).
- Skip `generate_report()` when `--skip_ai` is set (signature requires 6 dir args from AI pipeline).
- `config.py` proxy creds redacted — now loaded from env vars `TP_PROXY_1` / `TP_PROXY_2`.

**Used by:**
- `brand-strategy/trustpilot-voc-quick.md` → 5-min surface scan
- `brand-strategy/trustpilot-voc-deep.md` → full pipeline with sentiment / LDA topic / AI insights

---

## linktree-expander

Batch-enrich Linktree handles into per-creator profiles. Each `linktr.ee/{handle}` is a portfolio listing all the creator's socials + featured links.

**Standalone usage:**

```bash
cd tools/linktree-expander
# From a CSV (e.g. kol_prospects_social.csv from backlink-kol-extractor)
python3 scripts/expand_linktree.py kol_prospects_social.csv \
  --col profile_url \
  --out linktree_expanded.csv

# Or plain text (one handle per line)
python3 scripts/expand_linktree.py handles.txt --out linktree_expanded.csv
```

**Why __NEXT_DATA__ parsing**: Linktree pages serve a Next.js app — links data lives in the `__NEXT_DATA__` JSON blob, NOT in `<a href>` tags (those are mostly linktree-internal asset URLs). Direct `requests` works (no Cloudflare on Linktree as of 2026-05-06).

**Output schema** (CSV with 21 cols):
- `linktree_handle`, `page_title`, `bio`
- `ig`, `tiktok`, `youtube`, `twitter`, `facebook` (handles, not URLs)
- `substack`, `podcast_apple`, `podcast_spotify`, `pinterest`, `twitch`
- `personal_site` — handle-match-scored (only set if domain's first label contains the handle slug, score ≥ 40 — empty is better than wrong)
- `email_visible` (rare in 2026 — most creators put email in IG bio not Linktree bio)
- `outbound_count`, `top_categories`, `primary_brand_partner`, `social_count`
- `scraped_at`, `status` (ok / fetch_failed / parse_failed)

**`NON_PERSONAL_HOSTS` blocklist** (30+ domains): link shorteners (amzn.to / bit.ly / ngl.link / fbuy.io / glnk.io / posh.mk / lnk.bio), affiliate platforms (liketoknow.it / shopmy / beacons / stan.store), scheduling tools (calendly / typeform / docs.google.com / forms.gle), archive utilities (archive.md / web.archive.org), major retailers / generic platforms (amazon.com / etsy / spotify / social), Patreon / Ko-fi / GitHub / Medium / Substack base domains.

**Pilot run (2026-05-06)**: 44/45 ok on a single-category seed list of 45 handles. Field hit rates: ig 26/45 (58%), tiktok 18/45, youtube 8/45, podcast 5+5/45, personal_site 18/44 (after handle-match filtering — was 44/44 with v1.0's "first non-social outbound" heuristic, but those were 75% sponsor noise).

See [linktree-expander/SKILL.md](linktree-expander/SKILL.md) for details.

---

## contact-extractor

Multi-source contact email extraction for KOL / media prospect rows. Given a CSV with `personal_site` / `youtube` / `podcast_apple` columns (e.g. output of `linktree-expander` or `media-press-discovery`), enrich each row with up to 3 ranked candidate emails + source label + confidence tier.

**Standalone usage:**

```bash
cd tools/contact-extractor
python3 scripts/extract_contacts.py linktree_expanded.csv --out contacts.csv

# With SMTP / Hunter verification (optional)
python3 scripts/extract_contacts.py linktree_expanded.csv --verify --out contacts.csv
export HUNTER_API_KEY=xxx     # if set, uses Hunter API; else free SMTP MX probe
export YOUTUBE_API_KEY=xxx    # for YT description email scrape
```

**Sources tried (in order)**:
1. **`personal_site` root + `/about` + `/contact` + `/press` + `/work-with-me`** — mailto: links (high confidence) + visible text emails (medium)
2. **YouTube Data API v3** (set `YOUTUBE_API_KEY`) — channel description email
3. **Apple Podcasts public API** (no key needed) — RSS feed `<itunes:email>` owner
4. **Email pattern guess** (only if 1-3 produce no hits) — `hello@`, `hi@`, `contact@`, `{firstname}@` on `personal_site` domain. Low confidence unless `--verify` runs SMTP MX probe.

**Confidence tiering**:
| Tier | Source | Action |
|---|---|---|
| **high** | mailto: link OR YT API description OR podcast RSS owner | Outreach directly |
| **medium** | Visible text email on creator's own site | Spot-check before outreach |
| **low** | Pattern-guessed email | Run `--verify` OR Hunter.io before outreach |
| **none** | No personal_site / no hits | Need IG bio extraction or manual lookup |

**`NEVER_DIG_DOMAINS`** — same blocklist concept as linktree-expander, prevents wasting requests on known third-party utilities that produce noise emails (sponsor / platform / random-3rd-party). 30+ entries.

**Pilot run (2026-05-06, on 45 Linktree-derived prospects from a single category)**: 5 high + 4 medium + 11 low + 25 none. The 25 "none" are IG-only / TikTok-only creators who don't have a discoverable personal_site — recommended next step is IG bio extraction via Apify (`apify/instagram-scraper` actor, ~$0.005/profile).

See [contact-extractor/SKILL.md](contact-extractor/SKILL.md) for details.

---

## serp-content-teardown

Deterministic (no-LLM) pipeline that reverse-engineers what content wins a Google / AI-search niche, from **local Semrush xlsx + fetched competitor HTML**. Answers, per target topic: which article archetype to write, how long, how many H2s, what schema + FAQ, what opening/closing pattern, which keywords to target, what backlink authority is realistically needed, and what GEO (AI-Overview) posture to take.

**Standalone usage:**

```bash
cd tools/serp-content-teardown
pip install -r scripts/requirements.txt

# One-shot: all 8 steps in order
python3 scripts/run_all.py \
  --semrush-dir ~/Downloads/semrush/_project_<niche>/_keywords \
  --out-dir ./teardown_out \
  --topics templates/topic-clusters.yaml \
  --brand-names templates/brand-names.json \
  --top 30
```

**Input layout** — point `--semrush-dir` at a folder of Semrush exports (same shape as `backlink-kol-extractor`):
```
_keywords/
  <kw>_serp_urls_us_*.xlsx        # SERP URLs (URL, Position, Type, Page AS, Ref.Domains, Backlinks, Search Traffic, SERP Features)
  <kw>_broad-match_us_*.xlsx      # Keyword overview (Keyword, Volume, Keyword Difficulty, Intent, SERP Features)
```

**Config:** `templates/topic-clusters.yaml` (ordered cluster → regex, first match wins — replace per niche), `templates/brand-names.json` (domain → brand-name variants for brand-density; optional, auto-derives from domain if absent).

**Outputs** (all under `--out-dir`): `url_pool.json`, `html/`, `fetch_manifest.json`, `results.json`, `prose_dump.txt`, `classified.json`, `keywords.json`, `backlinks.json`, `onpage.json`. Worked example reports in `examples/` (jewelry niche).

**8 article archetypes:** DEFINITION_QA, TUTORIAL_HOWTO, LISTICLE_TIPS, COMPARISON_VS, PILLAR_GUIDE, MYTH_DEBUNK, PRODUCT_MICROGUIDE, NEWS_EDITORIAL.

**Red line / honest scope:** `curl`-only fetch (browser UA) — no paid APIs (Ahrefs / Apify / Tavily / Jina / OpenRouter), no live AI-citation probing (Perplexity / Gemini / ChatGPT). Cloudflare-protected pages are flagged `blocked` and skipped. Backlink data is page-level Authority Score, not domain DR. Covers the ~20-30% structure/SEO/GEO "code-side" of what wins; content + domain age + backlinks are the other ~70-80%.

**Used by / pairs with:**
- `brand-strategy/dsite-seo-playbook.md` → content-plan step (what shape to write per target keyword)
- `brand-strategy/brand-market-scan.md` → competitor content teardown
- `tools/backlink-kol-extractor` (link side) + `structured-data-buildout` (implements the schema this tool only measures)

See [serp-content-teardown/SKILL.md](serp-content-teardown/SKILL.md) and [references/methodology.md](serp-content-teardown/references/methodology.md) for details.

---

## Notes for skill authors using these tools

When a SKILL conditionally depends on tool data (e.g. Semrush exports, Linktree expansion output), follow this pattern:

1. State the dependency at the top of the SKILL body in plain language.
2. Specify the expected file(s) location (default: project repo root or user-specified path).
3. Make the tool execution **optional** — if the data is absent, gracefully skip that section of the SKILL workflow with a single sentence note.

This keeps SKILLs runnable without forcing users to set up every tool.
