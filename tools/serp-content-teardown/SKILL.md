---
name: serp-content-teardown
description: Reverse-engineer what content shape wins a Google / AI-search niche from LOCAL Semrush xlsx exports + competitor HTML — fully deterministic, no LLM, no paid API. Parses Semrush serp_urls + broad-match files, fetches the top-ranking competitor articles (curl, browser UA), and computes per-article structure metrics (words, H1/H2/H3, lists, tables, JSON-LD @type set, author byline, dates, brand-mentions/1k, authority outlinks), then classifies each into 8 article archetypes and aggregates the winning bands. Also sizes keyword distribution + core keywords, backlink/authority thresholds (Semrush Page Authority Score / Ref.Domains / Backlinks), AI-Overview (GEO) saturation + cited domains + schema readiness, and on-page SEO. Output: JSON artifacts + a per-topic content-strategy report (which archetype, word/H2/schema/FAQ/opening-closing to use, which keywords to target, what authority is needed, what GEO posture to take). Use when the user wants to "tear down a SERP", "reverse-engineer competitor content", "find what article shape ranks", do a "competitor blog structure analysis", a "SEO/GEO/keyword/backlink teardown from Semrush", or asks 竞品文章结构分析 / 反推信息博客该用什么结构 / SERP 内容拆解 / 这个词该写多长配什么 schema / 竞品都用什么文章模板 / 关键词+反链+GEO 一起拆.
---

# SERP Content Teardown

Deterministic (no-LLM) pipeline that reverse-engineers what content wins a Google / AI-search niche, from **local Semrush xlsx exports + fetched competitor HTML**. It answers, per target topic: which article archetype to write, how long, how many H2s, what schema + FAQ, what opening/closing pattern, which keywords to target, what backlink authority is realistically needed, and what GEO (AI-Overview) posture to take.

Everything runs offline against files you already have, except one network step: fetching competitor article HTML via `curl` with a browser UA. **No paid APIs, no live AI-citation probing** (see [references/honest-scope.md](references/honest-scope.md)).

## Quick Start

```bash
cd tools/serp-content-teardown

# One-shot: runs all 8 steps in order, writes every artifact to --out-dir.
python3 scripts/run_all.py \
  --semrush-dir ~/Downloads/semrush/_project_<niche>/_keywords \
  --out-dir ./teardown_out \
  --topics templates/topic-clusters.yaml \
  --brand-names templates/brand-names.json \
  --top 30
```

`run_all.py` is just the per-step scripts chained. Run them individually when iterating (e.g. re-fetch without re-parsing, or re-classify after tweaking the topic map):

```bash
# 1. Parse Semrush serp_urls xlsx -> ranked blog/info-article URL pool
python3 scripts/parse_serp.py --semrush-dir ~/Downloads/semrush/_project_<niche>/_keywords \
  --out-dir ./teardown_out --topics templates/topic-clusters.yaml --limit 40

# 2. Fetch top competitor articles (curl, browser UA). --select to override the auto-pick.
python3 scripts/fetch_competitors.py --out-dir ./teardown_out --top 30

# 3. Per-article structure metrics -> results.json + prose_dump.txt
python3 scripts/analyze_structure.py --out-dir ./teardown_out --brand-names templates/brand-names.json

# 4. Classify into 8 archetypes + opening/closing patterns + aggregate bands
python3 scripts/classify_archetypes.py --out-dir ./teardown_out

# 5. Keyword distribution + core keywords + SERP-feature triggers (broad-match xlsx)
python3 scripts/keyword_analysis.py --semrush-dir ~/Downloads/semrush/_project_<niche>/_keywords \
  --out-dir ./teardown_out --topics templates/topic-clusters.yaml

# 6. Backlink / authority thresholds + weak-link winners (serp_urls Organic rows)
python3 scripts/backlink_analysis.py --semrush-dir ~/Downloads/semrush/_project_<niche>/_keywords \
  --out-dir ./teardown_out --topics templates/topic-clusters.yaml

# 7. GEO: AI-Overview saturation + cited domains + schema readiness of cited vs non-cited
python3 scripts/geo_analysis.py --semrush-dir ~/Downloads/semrush/_project_<niche>/_keywords \
  --out-dir ./teardown_out

# 8. On-page SEO: title/meta/H1/canonical/internal-link density + SERP features
python3 scripts/onpage_analysis.py --out-dir ./teardown_out
```

Steps 3, 4, 7, 8 reuse the HTML fetched in step 2 — no re-fetching. Steps 1, 5, 6, 7 read the Semrush xlsx directly.

## Inputs

| Input | Required | What it is | Where |
|---|---|---|---|
| `*serp_urls*.xlsx` | yes | Semrush "SERP URLs" export per keyword/region. Columns used: `URL`, `Position`, `Type` (Organic / AI Overview / …), `Search Traffic`, `Page AS`, `Ref.Domains`, `Backlinks`. Drives the URL pool (step 1), authority thresholds (step 6), AI-cited domains (step 7). | `--semrush-dir` |
| `*broad-match*.xlsx` | for steps 5/7 | Semrush "Broad Match" keyword export (US). Columns used: `Keyword`, `Volume`, `Keyword Difficulty`, `Intent`, `SERP Features`. Drives keyword distribution + GEO sizing. | `--semrush-dir` |
| `templates/topic-clusters.yaml` | yes | Ordered cluster → regex map (first match wins as the keyword's primary cluster). Also seeds the blog/info-article path heuristics. Adapt to your niche. | `--topics` |
| `templates/brand-names.json` | optional | `domain → [name variants]` for brand-mention density. If a domain is missing, the brand token is auto-derived from the domain (e.g. `oceanwavejewelry.com` → `oceanwave`); use specific forms only, never generic words. | `--brand-names` |
| fetched HTML | produced | `fetch_competitors.py` writes `html/<slug>.html` + `fetch_manifest.json`; steps 3/4/7/8 re-parse these. | `--out-dir/html/` |

The Semrush directory layout mirrors `tools/backlink-kol-extractor` — point `--semrush-dir` at the folder holding the `*serp_urls*` and `*broad-match*` xlsx files (typically `~/Downloads/semrush/_project_<niche>/_keywords`).

## Output schema

All artifacts land under `--out-dir`. Full field tables in [references/output-schema.md](references/output-schema.md).

| Artifact | Produced by | Contents |
|---|---|---|
| `url_pool.json` | parse_serp | Ranked blog/info-article URLs: `domain, path, url, category` (blog / info_page), `appearances`, `matched_keywords`, `us_min_pos`, `all_min_pos`, `avg_pos`, `n_keywords`, `max_traffic`. |
| `html/`, `fetch_manifest.json` | fetch_competitors | Raw HTML per article + fetch log (`http_code`, `bytes`, `ok`, anti-bot block flag). |
| `results.json` | analyze_structure | Per-article structure metrics (word_count, h1/h2/h3, imgs, ul/ol/table, schema_types, schema_blocks, has_faq_section, author, dates, brand_per_1k, authority_outlinks, h2_texts, opening, closing). |
| `prose_dump.txt` | analyze_structure | Human-readable opening + H2 outline + closing per article (for eyeballing tone). |
| `classified.json` | classify_archetypes | `results.json` + `archetype`, `archetype_reason`, `opening_pattern`, `closing_pattern`, `schema_sig`. |
| `keywords.json` | keyword_analysis | Deduped keyword universe: `kw, vol, kd, intent, feats, cluster`. Console prints intent/volume/KD/cluster distributions + core + quick-win lists. |
| `backlinks.json` | backlink_analysis | Per organic SERP row: `kw, cluster, pos, as (Page AS), ref (Ref.Domains), bl (Backlinks), domain, url`. Console prints authority bands + weak-link winners. |
| `onpage.json` | onpage_analysis | Per-article on-page: title/meta/H1, canonical, kw-in-title/h1/meta, title_is_question, internal/external link counts. |

The **content-strategy report** (per-topic recommendations) is assembled from these artifacts — see `templates/` and `examples/` (owned by the report templates) for the report shape; the methodology for reading them is in [references/methodology.md](references/methodology.md).

## When to use

- You have Semrush exports for a niche and want to know **what to actually write** — archetype, length, structure, schema — not just a keyword list.
- New informational-SEO content cluster: reverse-engineer the incumbents before drafting.
- You want a defensible authority read: "is the long tail beatable with content alone, or do I need links first?"
- You want to size the GEO / AI-Overview opportunity per topic from data you already pay Semrush for.

## When NOT to use

- **KOL / influencer / media prospect discovery** → use `tools/backlink-kol-extractor` (different anchor: refdomains, not article structure).
- **Implementing the schema** the teardown recommends → use `structured-data-buildout` (this skill measures schema; it does not write it).
- **You have no Semrush data** → out of scope. This pipeline is built around Semrush xlsx column shapes; it does not crawl a SERP live or call a keyword API.
- **You want a domain-authority (DR) verdict** → Semrush exports carry *page-level* Authority Score, not domain DR. See honest-scope.
- **Cloudflare-heavy targets** → the fetcher is `curl`-only; pages behind a JS challenge get flagged `blocked` and skipped (no headless browser, no paid scraper). Expect to lose a few of the top URLs.

## Honest scope

This finds the **structure / SEO / GEO "code-side" of what wins — roughly the 20-30%** you can copy mechanically. The other **70-80% is content quality, domain age, and backlinks**, none of which this measures or fixes. Two specific limits worth stating up front to the user:

- Backlink data is Semrush **Page Authority Score (page-level), not domain DR**. You can confidently say "page-level links aren't the bottleneck for the long tail" (the data shows top-3 pages routinely ranking at Page AS 0-20); you **cannot** quantify the domain-authority floor from this.
- AI-Overview citation capture in Semrush exports is **sparse**. "Schema depth didn't gate citation in-sample" is what the data supports — *not* "schema is useless." Flag any GEO estimate with ⚠️.

Full caveats + the red line on paid APIs / live AI probing: [references/honest-scope.md](references/honest-scope.md).

## References

- [references/methodology.md](references/methodology.md) — the full 8-step pipeline (input → deterministic algorithm → output) + how to read the cross-sample findings.
- [references/archetypes.md](references/archetypes.md) — the 8-archetype spec: trigger rule, word/H2 bands, FAQ, schema set, opening/closing pattern, "when it wins".
- [references/honest-scope.md](references/honest-scope.md) — what this does and does NOT tell you; the paid-API / AI-probe red line; parser gotchas.
- [references/output-schema.md](references/output-schema.md) — JSON field schemas for every artifact.
