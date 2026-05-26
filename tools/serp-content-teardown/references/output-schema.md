# Output Schema

Every artifact lands under `--out-dir`. Field types and meanings below are taken from the actual pipeline output. JSON files are arrays of objects unless noted.

---

## `url_pool.json` — ranked competitor blog/info URLs (from `parse_serp.py`)

| Field | Type | Meaning |
|---|---|---|
| `domain` | str | Registrable domain (www-stripped). |
| `path` | str | Normalized URL path (trailing slash stripped, lowercased). |
| `url` | str | Original full URL (first seen). |
| `category` | str | `"blog"` (blog/journal/guides/etc. path) or `"info_page"` (Shopify `/pages/` with an informational slug). |
| `appearances` | int | How many SERP rows (across all keyword/region files) this URL appeared in. |
| `matched_keywords` | str[] | Sorted keywords whose SERP this URL ranked in. |
| `info_topic_hits` | str[] | Subset of `matched_keywords` that are priority info topics (drives ranking). |
| `us_min_pos` | int \| null | Best (lowest) US position seen. |
| `all_min_pos` | int \| null | Best position across all regions. |
| `avg_pos` | float \| null | Mean position across all appearances. |
| `n_keywords` | int | Count of distinct matched keywords (breadth). |
| `max_traffic` | float | Max `Search Traffic` value seen for this URL. |
| `types` | str[] | Sorted SERP `Type` values seen (e.g. Organic). |

Rank order: info-topic hits desc, then `us_min_pos` asc, then `all_min_pos` asc, then `appearances` desc, then `n_keywords` desc.

---

## `fetch_manifest.json` — fetch log (from `fetch_competitors.py`)

| Field | Type | Meaning |
|---|---|---|
| `slug` | str | Filesystem-safe slug; HTML saved at `html/<slug>.html`. |
| `domain` | str | Registrable domain. |
| `url` | str | Fetched URL. |
| `category` | str | Carried from `url_pool.json`. |
| `matched_keywords` | str[] | Carried from pool. |
| `info_topic_hits` | str[] | Carried from pool. |
| `us_min_pos` / `all_min_pos` / `avg_pos` | int \| null / float | Carried from pool. |
| `http_code` | str | HTTP status from `curl` (or `ERR:…`). |
| `bytes` | int | Saved file size. |
| `ok` | bool | `true` if not blocked. Blocked = non-2xx, `< 1500` bytes, or anti-bot marker in first 6 KB. Downstream steps process only `ok` rows. |

`html/<slug>.html` — raw fetched HTML, one file per selected article.

---

## `results.json` — per-article structure metrics (from `analyze_structure.py`)

| Field | Type | Meaning |
|---|---|---|
| `domain`, `url`, `category` | str | Identity (carried from manifest). |
| `keyword` | str | Primary keyword for this article (first info-topic hit, else first matched keyword). |
| `all_matched_keywords` | str[] | All keywords this URL ranked in. |
| `us_min_pos`, `all_min_pos`, `avg_pos` | int\|null / float | Ranking positions (carried). |
| `word_count` | int | Word-char tokens in the picked content container. |
| `h1`, `h2`, `h3` | int | Heading counts. `h1` is whole-document; `h2`/`h3` are within the content container. |
| `imgs`, `ul`, `ol`, `table` | int | Element counts within the container. |
| `schema_types` | str[] | Sorted set of all JSON-LD `@type` values found on the page (before junk-stripping). |
| `schema_blocks` | int | Count of `<script type="application/ld+json">` blocks. |
| `has_faq_section` | bool | `FAQPage` schema present, or an H2/H3 matching "frequently asked"/"faq". |
| `author` | str \| null | Author name (JSON-LD → meta → byline class). |
| `has_author` | bool | `author` is non-null. |
| `date_published`, `date_modified` | str \| null | `YYYY-MM-DD` (JSON-LD → article:* meta → `<time>`). |
| `brand_per_1k` | float | Brand-name mentions per 1000 words. Variants come from `brand-names.json`; if a domain is absent, a token is auto-derived from the domain. |
| `brand_mentions` | int | Raw brand-name match count. |
| `authority_outlinks` | int | External links to authority domains (Wikipedia, NIH/NCBI, WHO, ASTM, GIA, FTC/FDA, Mayo, `.gov`/`.edu`, …). |
| `authority_domains` | str[] | Those authority domains. |
| `external_outlinks` | int | All distinct external registrable domains linked (excludes infra: Shopify/Klaviyo/Google/CDNs). |
| `external_domains` | str[] | First 12 external domains. |
| `social_outlinks` | int | Distinct social domains linked. |
| `h2_texts`, `h3_texts` | str[] | Heading texts (≤90 chars each) — the outline. |
| `opening` | str | First ~2 non-heading paragraphs (≤700 chars). |
| `closing` | str | Last non-heading blocks (≤700 chars). |

Sorted by `us_min_pos` asc, then `all_min_pos` asc.

`prose_dump.txt` — for each article: a header line (domain / keyword / us# / words / H2 / H3 / schema), the URL, the opening paragraphs, the H2 outline, and the closing blocks. Plain text, for eyeballing tone.

---

## `classified.json` — `results.json` + archetype (from `classify_archetypes.py`)

All `results.json` fields, plus:

| Field | Type | Meaning |
|---|---|---|
| `archetype` | str | One of the 8 (see archetypes.md): `DEFINITION_QA`, `TUTORIAL_HOWTO`, `LISTICLE_TIPS`, `COMPARISON_VS`, `PILLAR_GUIDE`, `MYTH_DEBUNK`, `PRODUCT_MICROGUIDE`, `NEWS_EDITORIAL`. |
| `archetype_reason` | str | Human-readable reason the precedence ladder assigned it. |
| `opening_pattern` | str | `DIRECT_INTRO`, `QUESTION_TEASE`, `DEFINITION_LEAD`, `MYTH_BUST`, `TLDR_FIRST`, `STAT_LEAD`, `RELATABLE_HOOK`, `MERCH/PROMO`. |
| `closing_pattern` | str | `SUMMARY_WRAP`, `BRAND_PRODUCT_TIE`, `PRODUCT_GRID/PRICES`, `INVESTMENT/VERDICT`, `EMPOWERMENT`, `AUTHOR_BIO`, `RELATED_LINKS`, `READER_COMMENTS`. |
| `schema_sig` | str | Compact schema signature, e.g. `Article+Person+Organization+WebPage` or `(none)`. |

The console additionally prints the per-archetype distribution (n, word band, H2 band, FAQ%, brand/1k band, common schema) and overall cross-sample stats — these are not in the JSON; capture from stdout or recompute.

---

## `keywords.json` — keyword universe (from `keyword_analysis.py`)

| Field | Type | Meaning |
|---|---|---|
| `kw` | str | Keyword (lowercased, deduped to highest-volume row). |
| `vol` | int | Monthly search `Volume`. |
| `kd` | float \| null | `Keyword Difficulty` (0-100), null if absent/NaN. |
| `intent` | str | Semrush `Intent` string (e.g. `Informational`, `Commercial`, `Informational, Transactional`). |
| `feats` | str | Raw `SERP Features` string (parsed downstream for `ai overview` / `people also ask` / `video` / `featured snippet` / `image`). |
| `cluster` | str | First-matching cluster from `topic-clusters.yaml`, else `OTHER`. |

Distributions (intent / volume bands / KD bands / per-cluster / core keywords / quick-wins) are printed to console only.

---

## `backlinks.json` — per organic SERP row (from `backlink_analysis.py`)

| Field | Type | Meaning |
|---|---|---|
| `kw` | str | Keyword (from filename). |
| `cluster` | str | Cluster assigned to that keyword. |
| `pos` | int | Organic position. |
| `as` | float \| null | Semrush **Page AS** — page-level Authority Score (0-100). NOT domain DR. |
| `ref` | float \| null | `Ref.Domains` for the ranking URL. |
| `bl` | float \| null | `Backlinks` for the ranking URL. |
| `domain` | str | Registrable domain. |
| `url` | str | Ranking URL. |

Deduped to one row per `(keyword, domain)`. Authority bands by position and weak-link winners are printed to console.

---

## `onpage.json` — per-article on-page SEO (from `onpage_analysis.py`)

| Field | Type | Meaning |
|---|---|---|
| `domain` | str | Registrable domain. |
| `kw` | str | Article keyword (de-suffixed, spaces). |
| `us` | int \| null | Best US position. |
| `archetype` | str | Carried from `classified.json`. |
| `title` | str | `<title>` text. |
| `title_len` | int | Title length (SEO sweet spot 50-60). |
| `meta_len` | int | Meta description length. |
| `has_meta` | bool | Meta description (or og:description) present. |
| `canonical` | bool | `<link rel=canonical>` present. |
| `h1n` | int | H1 count (1 is ideal; 0 or >1 are flagged in aggregate). |
| `h1` | str | First H1 text. |
| `kw_in_title`, `kw_in_h1`, `kw_in_meta` | bool | Keyword tokens present (allows one missing token). |
| `title_is_question` | bool | Title starts with what/why/how/is/are/does/can/do or contains `?`. |
| `internal_links` | int | Body links to same registrable domain (+ root-relative `/…`). |
| `external_links` | int | Body links to other domains. |

Aggregates (% meta/canonical/single-H1, % kw-in-title/h1/meta, title-length band, link medians, strongest-ranker title patterns) are printed to console.

---

## GEO (`geo_analysis.py`) — console only

No JSON artifact. Prints: (1) AI-Overview opportunity sizing per cluster (info# / AIO# / AIO% / AIO volume), (2) AI-cited domains across US SERPs (cites / #queries / domain / which queries), (3) schema readiness of each fetched page (schema-type count / whether its domain is AI-cited / schema types) + GEO-relevant node coverage across all fetched pages. Reads `keywords.json` + `classified.json` + the `Type=AI Overview` rows of the serp_urls xlsx. Capture from stdout for the report.
