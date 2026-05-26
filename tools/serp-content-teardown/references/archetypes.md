# The 8 Article Archetypes

`classify_archetypes.py` assigns each fetched article **exactly one** archetype via a fixed precedence ladder — the first rule that matches wins. Order matters: a "best waterproof brands" press roundup is `NEWS_EDITORIAL` (caught first by schema), not `LISTICLE_TIPS`, even though it is a list.

Word/H2/FAQ/brand bands below are the per-archetype aggregates from the reference run (jewelry niche, 25 articles). Treat them as the *shape* to expect; your own run's distribution table (printed by `classify_archetypes.py`) is the number you should actually write to.

## Precedence ladder (top = checked first)

| # | Archetype | Trigger rule (from `classify_archetypes.py`) |
|---|---|---|
| 1 | **NEWS_EDITORIAL** | `NewsArticle` in schema types, OR the domain is a known press/editorial domain. |
| 2 | **LISTICLE_TIPS** *(marketplace outlier)* | Domain is a marketplace/aggregator, OR H2 blob contains "top products" ≥ 2×. Tagged as outlier (product listing, not editorial). |
| 3 | **COMPARISON_VS** | Slug contains `vs` as a token (`-vs-`, `vs-`, `-vs`), `compared-to`, or `-or-solid` — explicit X-vs-Y intent at the slug level. |
| 4 | **MYTH_DEBUNK** | Opening matches a myth-bust regex (`myth(s)`, `forget the`, `the truth`, `misconception`, `debunk`, `don't believe`, …). |
| 5 | **LISTICLE_TIPS** | ≥ 3 numbered H2s, OR H2 blob has `\d+ (types\|ways\|reasons\|brands)`, OR slug starts `best-`/`top-`, OR slug has `essentials`/`ways-to`, OR URL path has `/styling/`. |
| 6 | **PRODUCT_MICROGUIDE** | `category == info_page` AND `word_count < 520` AND not a definitional opener AND (merch/promo language present OR zero H2s). Thin product-embedded landing page. |
| 7 | **TUTORIAL_HOWTO** | Slug starts `how-to`/`how-do`, OR is a known cleaning slug, OR has `clean`/`care` in slug **without** `guide`. |
| 8 | **PILLAR_GUIDE** *(≡ REFERENCE_BIBLE)* | Slug has `types-of`/`complete`/`everything`/`ultimate`, OR **H2 ≥ 12**, OR (`-101` slug AND (H2 ≥ 8 OR words ≥ 1500)), OR (`guide` slug AND **H3 ≥ 10**). Comprehensive guide / types-taxonomy / mega question-cluster. |
| 9 | **DEFINITION_QA** *(fallback)* | Anything else — definitional / pros-cons / "is X good" explainer. |

> The `vs` token check uses a word-boundary pattern, so `services`/`reviews` do **not** falsely trigger COMPARISON_VS. The PILLAR_GUIDE `-101` and `guide` sub-rules are why a "Waterproof Jewelry 101" with 8+ H2s lands as a pillar, while a short "101" with few H2s falls through to DEFINITION_QA.

## Per-archetype spec

### 1. DEFINITION_QA — definitional / pros-cons / "is X good" explainer
- **Trigger:** fallback (no higher rule matched). Often a `what-is-`/`is-`/`does-`/`why-` slug or a definitional opener.
- **Word band:** 416–1814 (med ~1139). **H2 band:** 0–10 (med 6). **FAQ:** ~27%.
- **Schema:** most commonly `Organization` only, sometimes `Article+Person+Organization+WebPage`. Brand/1k: low (med 0).
- **Opening:** `DIRECT_INTRO` or `DEFINITION_LEAD` ("X is a …"). **Closing:** `SUMMARY_WRAP`, sometimes `INVESTMENT/VERDICT` or `AUTHOR_BIO`.
- **When it wins:** the bread-and-butter informational query ("is stainless steel jewelry good", "what is gold-plated jewelry"). The single most common archetype in the cohort (11/25). Beatable with a clear, complete answer + a FAQ.

### 2. TUTORIAL_HOWTO — how-to / care steps
- **Trigger:** `how-to`/`how-do` slug, or clean/care slug without `guide`.
- **Word band:** ~800 (single sample 832). **H2 band:** ~6. **FAQ:** present in-sample.
- **Schema:** `Article+FAQPage+Person+Organization+…`. **HowTo schema notably absent in-sample (0/25 cohort)** — a cheap differentiator.
- **Opening:** `DIRECT_INTRO`. **Closing:** `SUMMARY_WRAP`.
- **When it wins:** procedural intent ("how to clean … ", "how to store … "). Add real `HowTo` + `FAQPage` schema — the cohort doesn't.

### 3. LISTICLE_TIPS — enumerated list / best-of / styling tips
- **Trigger:** ≥3 numbered H2s, "N types/ways/reasons/brands", `best-`/`top-` slug, `essentials`, `ways-to`, or `/styling/`. (Marketplace listings caught earlier as the outlier branch.)
- **Word band:** 974–4367 (med ~1494). **H2 band:** 2–16 (med ~10). **FAQ:** ~25%.
- **Schema:** richest in-cohort — commonly `Article+FAQPage+Person+Organization+…`. Brand/1k: 1.0–5.0 (med 1).
- **Opening:** `DIRECT_INTRO` or `RELATABLE_HOOK`. **Closing:** `BRAND_PRODUCT_TIE`, `PRODUCT_GRID/PRICES`, or `INVESTMENT/VERDICT`.
- **When it wins:** "best X" / "N ways to" / styling intent. The longest-running articles in the cohort were listicles. Pairs naturally with product ties.

### 4. COMPARISON_VS — explicit X vs Y comparison
- **Trigger:** `vs` token / `compared-to` / `-or-solid` in slug.
- **Word band:** long (single sample 2633). **H2 band:** ~6. **FAQ:** present in-sample (100% of the 1 sample).
- **Schema:** `Article+Person+Organization+BreadcrumbList+…`.
- **Opening:** `QUESTION_TEASE`. **Closing:** `SUMMARY_WRAP`.
- **When it wins:** decision-stage "A vs B" queries (gold-filled vs plated, plated vs solid). Tends to run long and benefits from a comparison table + FAQ.

### 5. PILLAR_GUIDE — comprehensive guide / types-taxonomy / mega question-cluster (≡ REFERENCE_BIBLE)
- **Trigger:** `types-of`/`complete`/`everything`/`ultimate` slug, **H2 ≥ 12**, `-101` + depth, or `guide` + **H3 ≥ 10**.
- **Word band:** 1407–2565 (med ~1538). **H2 band:** 6–14 (med ~11). **FAQ:** ~25%.
- **Schema:** mixed — strongest pages carry deep graphs (`Article+BreadcrumbList+ImageObject+…`), but in-cohort the most-common sig was `(none)` (a real gap to exploit). Brand/1k: 0.0–7.8 (med 2).
- **Opening:** `DIRECT_INTRO`, `QUESTION_TEASE`, or `STAT_LEAD`. **Closing:** `READER_COMMENTS`, `RELATED_LINKS`, or `BRAND_PRODUCT_TIE`.
- **When it wins:** head-term "types of X" / "complete guide" intent where breadth + internal-linking hub value matters. The archetype to use for a cluster's pillar page.

### 6. MYTH_DEBUNK — myth-bust opener
- **Trigger:** myth/misconception/debunk language in the opening.
- **Word band:** short (single sample 294). **H2 band:** ~4. **FAQ:** none in-sample.
- **Schema:** `(none)` in-sample. Brand/1k: ~3.4.
- **Opening:** `MYTH_BUST`. **Closing:** `PRODUCT_GRID/PRICES`.
- **When it wins:** counter-intuitive corrections ("tarnish-free jewelry — forget what you've heard"). Short, punchy, often used as a product on-ramp. Rare (1/25) but distinctive.

### 7. PRODUCT_MICROGUIDE — thin product-embedded landing page
- **Trigger:** `info_page` + `< 520` words + not definitional + (merch language OR zero H2s).
- **Word band:** 403–512 (med ~457). **H2 band:** 0–7 (med ~3). **FAQ:** none.
- **Schema:** `(none)` in-sample.
- **Opening:** `MERCH/PROMO` or `DIRECT_INTRO`. **Closing:** `SUMMARY_WRAP`.
- **When it wins:** thin Shopify `/pages/` that rank #1 on brand/category strength, not content depth — they appear because the *domain* is strong, not because the page is good. **Do not copy these as a content template** (they're a ranking artifact of authority); they're useful as a signal that the topic can rank with very little, given some authority.

### 8. NEWS_EDITORIAL — press / editorial best-of roundup
- **Trigger:** `NewsArticle` schema or a known press domain.
- **Word band:** ~894 (single sample). **H2 band:** ~6. **FAQ:** none in-sample.
- **Schema:** `Article+Person+Organization+Product+…` (publisher-grade).
- **Opening:** `DIRECT_INTRO`. **Closing:** `SUMMARY_WRAP`.
- **When it wins:** major-publisher "best X to shop" articles that rank on domain authority (e.g. a top-5 result from a national outlet). Like PRODUCT_MICROGUIDE, this is an **authority artifact** — a brand site can't replicate the domain, only the structure. Treat as "what the press did," not a copyable target.

## How to use this in the report

For each target topic:
1. Look up the dominant archetype in the cluster (from `classify_archetypes.py`'s per-article table).
2. Take the **word band + H2 band + FAQ% + schema sig** from *your* run's distribution table (not the reference numbers above).
3. Recommend an **opening + closing pattern** from the rows above.
4. Skip PRODUCT_MICROGUIDE and NEWS_EDITORIAL as *templates* — flag them as "ranks on authority, not structure" so the user doesn't try to copy a thin page and expect it to rank.
