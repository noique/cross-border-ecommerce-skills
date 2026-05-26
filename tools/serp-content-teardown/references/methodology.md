# SERP Content Teardown — Methodology

Eight deterministic steps. No LLM, no paid API. Every step is `input → algorithm → output`; the only network call is step 2 (`curl` fetch of competitor HTML).

All `med`/band figures quoted below are from the reference run (jewelry "waterproof / stainless / tarnish-free / gold-plated" cluster, 25 fetched articles, 44 broad-match files, 23 US serp_urls files). They are illustrative — your niche will differ. The point is the *shape* of each output, not the exact numbers.

---

## Step 1 — Parse serp_urls → ranked URL pool

`parse_serp.py --semrush-dir DIR --out-dir DIR --topics templates/topic-clusters.yaml [--limit N]`

**Input:** every `*serp_urls*.xlsx` in `--semrush-dir` (all regions, for breadth). Columns: `URL`, `Position`, `Type`, `Search Traffic`.

**Algorithm (deterministic):**
1. Parse keyword + region from each filename (`<kw>_serp_urls_<cc>_…`).
2. Classify each URL's path:
   - `blog` — path contains a blog/info token (`/blog`, `/blogs/`, `/journal`, `/guides`, `/learn`, `/article(s)`, `/news/`, `/tips`, `/resources`, `/the-edit`, `/discover`, …).
   - `info_page` — Shopify-style `/pages/` **and** the slug matches an informational regex (e.g. `waterproof|tarnish|how-to|what-is|care|clean|guide|types-of|…`), i.e. a genuine info page, not a landing page.
   - else dropped.
3. Drop non-article buckets (`/products/`, `/collections/`, `/cart`, policy/about/contact/size-chart/etc.) via an exclude regex.
4. Drop non-peer domains (Amazon, Etsy, Reddit, Quora, YouTube, Pinterest, Wikipedia, AliExpress, …) — marketplaces and UGC are not structure templates to copy.
5. Dedupe to `(domain, normalized-path)`; accumulate appearances, all positions, US positions, matched keywords, types, max traffic.
6. Rank: info-topic hits first, then best US position, then best overall position, then breadth (appearances, # keywords).

**Output:** `url_pool.json` — ranked list of `{domain, path, url, category, appearances, matched_keywords, info_topic_hits, us_min_pos, all_min_pos, avg_pos, n_keywords, max_traffic, types}`. `--limit` caps the console preview.

**Read it as:** the candidate set of competitor articles worth tearing down, already filtered to real blog/info content and ranked by how well they actually rank.

---

## Step 2 — Fetch competitor HTML

`fetch_competitors.py --out-dir DIR [--top 30] [--select FILE]`

**Input:** `url_pool.json`. Default takes the top N (`--top`); `--select` overrides with an explicit fragment list for topic/archetype diversity capped per domain (fragments are matched as `domain|path-substring` or bare path-substring against the pool).

**Algorithm:** `curl -sSL --compressed --max-time 25` with a desktop Chrome **User-Agent**, `Accept`/`Accept-Language`/`Referer: google.com` headers, follow redirects, gzip. Each response is checked for anti-bot blocks: non-2xx code, `< 1500` bytes, or Cloudflare/Incapsula/PerimeterX markers in the first 6 KB ("just a moment", "checking your browser", "attention required", "access denied", …). Blocked pages are flagged and excluded downstream.

**Output:** `html/<slug>.html` per article + `fetch_manifest.json` (`slug, domain, url, category, matched_keywords, info_topic_hits, us/all_min_pos, avg_pos, http_code, bytes, ok`).

**Red line:** `curl` only. No headless browser, no Apify/Tavily/Jina/ScrapingBee. Cloudflare-gated pages are *expected losses* — the manifest tells you which. Do not reach for a paid scraper without explicit user authorization (see honest-scope).

---

## Step 3 — Per-article structure metrics

`analyze_structure.py --out-dir DIR [--brand-names templates/brand-names.json]`

**Input:** the `ok` rows of `fetch_manifest.json` + their HTML.

**Algorithm (per article, all deterministic):**
1. Parse with **`html5lib`** (not stdlib `html.parser` — see honest-scope for why this matters; the wrong parser zeroes word counts on some Shopify themes).
2. Collect JSON-LD `@type` set + block count *before* stripping (walks every `<script type="application/ld+json">`, recursing dicts/lists; salvages concatenated objects).
3. Extract author (JSON-LD `author.name` → `<meta name=author>` → `.author`/`.byline` class text) and dates (`datePublished`/`dateModified` from JSON-LD → `article:published_time`/`modified_time` meta → first `<time datetime>`). Both *before* stripping.
4. Strip junk: remove `script/style/nav/header/footer/aside/form/iframe/…` tags, HTML comments, and any element whose class/id contains a nav/menu/cookie/newsletter/cart/related/share/announcement token.
5. Pick the content container: best of `<article>`, `[itemprop=articleBody]`, `div/section/main` whose class matches a content regex, `<main>` — scored by total `<p>`+`<li>` text length; fall back to `<body>` if none clears 200 chars.
6. Count within the container: words (word-char tokens), H2/H3 (with their texts), images, `ul`/`ol`/`table`.
7. Brand density: count brand-name variants (from `--brand-names`) per 1000 words → `brand_per_1k`.
8. Outbound links: classify each external link's registrable domain as authority (Wikipedia, NCBI/NIH, WHO, ASTM, GIA, FTC/FDA, Mayo, Healthline, `.gov`/`.edu`, …), social, or infra (Shopify/Klaviyo/Google/CDNs — excluded). Count authority + total external + social.
9. FAQ flag: `FAQPage` in schema OR an H2/H3 matching "frequently asked"/"faq".
10. Opening = first 2 non-heading paragraphs (≤700 chars); closing = last non-heading blocks (≤700 chars).

**Output:** `results.json` (full field list in output-schema.md) + `prose_dump.txt` (opening + H2 outline + closing per article, for eyeballing tone the metrics can't capture).

---

## Step 4 — Classify archetypes + aggregate

`classify_archetypes.py --out-dir DIR`

**Input:** `results.json`.

**Algorithm:** each article is assigned exactly one of 8 archetypes by a **fixed precedence ladder** (first rule that matches wins). The ladder, the per-archetype trigger rules, and the resulting bands are documented in [archetypes.md](archetypes.md). Opening and closing prose are also bucketed into named patterns (e.g. `DIRECT_INTRO`, `QUESTION_TEASE`, `MYTH_BUST`, `TLDR_FIRST`, `STAT_LEAD`; `SUMMARY_WRAP`, `BRAND_PRODUCT_TIE`, `INVESTMENT/VERDICT`, `AUTHOR_BIO`, …) by regex on the opening/closing text. A compact `schema_sig` string (e.g. `Article+Person+Organization+WebPage`) is derived from the schema types.

**Output:** `classified.json` (= `results.json` + `archetype`, `archetype_reason`, `opening_pattern`, `closing_pattern`, `schema_sig`) + a console report with three sections: per-article classification, **archetype distribution** (n, word band, H2 band, FAQ%, brand/1k band, most-common schema sig per archetype), and **overall** cross-sample stats.

**Read the cross-sample findings as:** the empirical "winning recipe" for the niche. From the reference run:

| Overall (25 articles) | Value |
|---|---|
| word_count | 294–4367 (med 1154) |
| H2 count | 0–16 (med 6) |
| H3 count | 0–39 (med 5) |
| FAQ section present | 28% (7/25) |
| has author byline | 72% (18/25) |
| has datePublished | 15/25 |
| authority outlinks > 0 | **1/25** (whole cohort cites 1 authority link total) |
| brand mentions / 1k words | 0.0–7.8 (med 1) |

The single most actionable cross-sample read here is often a *negative* one: in this niche brand-blogs almost never cite external authorities (1/25), so an article that does cite 2-3 real sources is differentiated cheaply. Read the archetype distribution table to pick the shape; read `prose_dump.txt` to match tone.

---

## Step 5 — Keyword distribution + core keywords

`keyword_analysis.py --semrush-dir DIR --out-dir DIR --topics templates/topic-clusters.yaml`

**Input:** every `*broad-match*…us…xlsx`. Columns: `Keyword`, `Volume`, `Keyword Difficulty`, `Intent`, `SERP Features`.

**Algorithm:** dedupe keywords (keep the highest-volume row per keyword); assign each to its first-matching cluster from `topic-clusters.yaml`; flag SERP features (`ai overview`, `people also ask`, `video`, `featured snippet`, `image`). Then tabulate: intent distribution, volume bands, KD (difficulty) bands, per-cluster distribution (count / volume / %informational / median KD / %AIO), core informational keywords per cluster (ranked by volume, with KD + feature tags), and a **quick-win list** (Informational + KD ≤ 20 + volume ≥ 70).

**Output:** `keywords.json` (`kw, vol, kd, intent, feats, cluster`) + the console tables.

**Read it as:** which keywords to target and how hard they are. The quick-win list is the practical starting backlog. Reference run: 37,428 unique keywords / 1.05M monthly volume; informational intent 4% of keywords but a meaningful share of *gettable* volume; KD is mostly low (3,046 keywords at KD < 20) — i.e. difficulty is not the gate, content is.

---

## Step 6 — Backlink / authority thresholds

`backlink_analysis.py --semrush-dir DIR --out-dir DIR --topics templates/topic-clusters.yaml`

**Input:** `*serp_urls*…us…xlsx`, **Organic rows only**. Columns: `Position`, `Page AS`, `Ref.Domains`, `Backlinks`, `URL`.

**Algorithm:** per cluster, dedupe to one row per `(keyword, registrable-domain)`; bucket by position band (top-3 / top-10 / 11-20); report median (min, max) of Page AS, Ref.Domains, Backlinks per band. Then list **weak-link winners** — top-10 organic results with Page AS ≤ 20 (proof that content, not links, carried them) — and the literal #1-3 incumbents per cluster.

**Output:** `backlinks.json` (per organic row: `kw, cluster, pos, as, ref, bl, domain, url`) + the console bands.

**Read it as:** the realistic authority needed to rank. Reference run, top-3 Page AS medians by cluster: waterproof 13, stainless 12, tarnish 5, gold-plated 19 — all low, with many top-10 winners at **Page AS 0**. The honest takeaway: *page-level* links are not the bottleneck for this long tail. **Caveat:** Page AS is page-level, not domain DR — you cannot read a domain-authority floor off this (see honest-scope).

---

## Step 7 — GEO / AI-Overview

`geo_analysis.py --semrush-dir DIR --out-dir DIR`

**Input:** `keywords.json` (from step 5) + `classified.json` (from step 4) + the `*serp_urls*…us…xlsx` rows where `Type == "AI Overview"`.

**Algorithm:**
1. **Opportunity sizing:** among informational keywords, what share trigger an AI Overview, by cluster (count / AIO# / AIO% / AIO volume).
2. **Cited domains:** count which domains appear as `Type=AI Overview` URLs across the US SERPs, and on how many distinct queries.
3. **Schema readiness:** for each fetched competitor page, show its schema-type count, whether its domain shows up among AI-cited domains, and its schema types. Then tabulate GEO-relevant node coverage across all fetched pages (`Article/BlogPosting`, `FAQPage`, `Person`, `Organization`, `BreadcrumbList`, `ImageObject`, `VideoObject`, `HowTo`, `Question/Answer`).

**Output:** console only (sizing + cited-domain table + schema-readiness table). No new JSON artifact.

**Read it as:** where the AI-search opportunity is and whether schema gates it. Reference run: 22% of informational keywords trigger AIO (some clusters 80-93%); GEO-relevant schema coverage across fetched pages was thin (FAQPage 3/25, VideoObject 0/25, HowTo 0/25). **Two honest caveats:**
- AI-Overview citation capture in Semrush is **sparse** — in the reference run only one fetched page's domain coincided with a captured AI-cited URL, so "schema depth didn't gate citation in-sample" is the most you can claim, *not* "schema is useless."
- Live Perplexity / Gemini / ChatGPT citation testing is **NOT run** — it is a paid/external probe and needs explicit user authorization. The script prints this note itself.

---

## Step 8 — On-page SEO

`onpage_analysis.py --out-dir DIR`

**Input:** the `ok` fetched HTML + `classified.json`.

**Algorithm:** per article, extract `<title>` + length, meta description + length, canonical presence, H1 count + text; test whether the article's keyword tokens appear in title / H1 / meta (allowing one missing token); flag question-style titles; count body internal vs external links (re-parsing with the same strip + container-pick logic as step 3). Then aggregate: % with meta / canonical / exactly-one-H1, % keyword-in-title/H1/meta, title-length band vs the 50-60 sweet spot, internal/external link medians, and the title patterns of the strongest US rankers.

**Output:** `onpage.json` (per-article on-page fields) + the console aggregates.

**Read it as:** the on-page hygiene baseline the incumbents meet. Reference run: 25/25 had meta + canonical, 18/25 had exactly one H1 (3 had zero, 4 had multiple — a real and copyable mistake to avoid), 22/25 put the keyword in the title, median title length 59 (in the sweet spot). The strongest titles cluster around `Keyword: benefit + benefit | Brand` and `Keyword 101: …` / `Pros and Cons of …` forms.

---

## Putting it together (the report)

The per-topic content-strategy report is assembled from `classified.json` (archetype + bands), `keywords.json` (target keywords + quick-wins), `backlinks.json` (authority read), the GEO console output, and `onpage.json`. For each target topic it should state:

1. **Archetype + structure** — which of the 8 to write, target word band, H2 count, whether to include a FAQ, the schema set to emit, and an opening + closing pattern (from archetypes.md, parameterized by your cross-sample bands).
2. **Keywords** — the core informational keywords for that cluster + the quick-wins (KD ≤ 20).
3. **Authority** — the realistic Page AS / Ref.Domains band to clear top-10, and whether weak-link winners prove the topic is content-beatable.
4. **GEO posture** — AIO saturation for the cluster and whether to lean into FAQ/HowTo/Video schema for citation surface (flagged ⚠️ as estimate).

See `templates/` and `examples/` for the report shape (those are maintained alongside the scripts). Lead the report with the [honest-scope](honest-scope.md) 20-30% / 70-80% framing so the user reads the recommendations as "the copyable code-side," not a ranking guarantee.
