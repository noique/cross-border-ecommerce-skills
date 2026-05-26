> Worked example — output of the `serp-content-teardown` skill run on the waterproof / stainless-steel women's jewelry niche (US SERPs, Semrush 2026-04 pull). Illustrative; numbers are Semrush estimates. "Stylr" is the planning-target site in this example.

# Jewelry Niche — Competitor Blog-Structure Analysis (Part 1: content structure)

**Method:** Parsed 92 Semrush `serp_urls` xlsx (all regions, US positions prioritized) → 9,154 SERP rows → 155 unique blog/info-article URLs after filtering out `/products/`, `/collections/`, `/cart`, homepages, generic `/pages/` landings, and marketplaces/UGC. Fetched 27 curated top-ranking URLs (browser UA); **26 returned 200** (one 429-blocked, logged+skipped); dropped one 157-word product-category blurb → **25 analyzed articles**. All metrics computed deterministically (Python + html5lib; no LLM).

> **Parser note:** Python's default `html.parser` silently absorbs article bodies into unclosed void tags (`<link>`/`<input>`) on several Shopify themes, zeroing out word counts. Switched to spec-compliant `html5lib` — that's why these counts are trustworthy.

---

## A. Comparison table — 25 real-ranking jewelry competitor articles

Sorted by archetype, then US position. `pos` = best US SERP position (`#N~` = ranks outside US top-100 but #1–few in AU/UK/CA). `img *` = inflated by Shopify product-card galleries. `lists` = ul/ol/tbl. Schema abbreviations: Art=Article/BlogPosting, FAQ=FAQPage, Per=Person, Org=Organization, Bc=BreadcrumbList, WP=WebPage, Prod=Product, Img=ImageObject.

| # | domain | keyword | pos | words | H2 | H3 | img | lists | schema | author | br/1k | date | archetype |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | helloadorn.com | waterproof/tarnish | #1 | 618 | 9 | 4 | 35 | 1ul | Org | — | 0.0 | — | DEFINITION_QA |
| 2 | artizanjoyeria.com | stainless-steel | #1 | 1814 | 6 | 19 | 53* | 2ul/1ol | Art+Per+Org+WP | Mauren Kaufmann | 0.0 | 2025-08 | DEFINITION_QA |
| 3 | gldn.com | waterproof | #5 | 779 | 6 | 5 | 4 | 6ul | Art+Per+Org+WP | GLDN Team | 1.3 | 2022-08 | DEFINITION_QA |
| 4 | monera-design.com | stainless-steel | #22 | 780 | 2 | 12 | 11 | 8ul | — | —¹ | 3.8 | — | DEFINITION_QA |
| 5 | statementcollective.com | gold-plated | #34 | 1397 | 10 | 3 | 8 | 2ul | Art+Per+Org+Bc+WP | Daniel Lowry | 0.0 | 2023-04 | DEFINITION_QA |
| 6 | magnoliaandtulle.com | tarnish | #45 | 1442 | 9 | 2 | 6 | 3ul/4ol | Art+Org+Img | Kimberly Ellis | 0.0 | 2020-05 | DEFINITION_QA |
| 7 | bluestreakcrystals.com | stainless-steel | #56 | 1154 | 5 | 13 | 2 | 1ul | Art+Per+Org+WP+Img | Amanda Middleton | 3.5 | 2025-01 | DEFINITION_QA |
| 8 | clarajane.co | waterproof | #69 | 416 | 0 | 0 | 0 | 0 | Org | — | 0.0 | — | DEFINITION_QA |
| 9 | jewelersmutual.com | gold-plated | #74 | 1139 | 5 | 0 | 7 | 3ul | Art+Per+Bc+WP+Img | Matt Wodenka | 1.8 | 2024² | DEFINITION_QA |
| 10 | insyncdesign.com.au | stainless-steel | #1~ | 1471 | 4 | 13 | 3 | 1ul | Art+Per+Org+Bc+WP+Img | Iris Saar Isaacs | 0.0 | 2023-12 | DEFINITION_QA |
| 11 | nelsoncoleman.com | gold-plated | #1~ | 993 | 8 | 4 | 6 | 3ul | — | — | 1.0 | — | DEFINITION_QA |
| 12 | simpleanddainty.com | gold-plated (types) | #19 | 2565 | 6 | 1 | 6 | 0 | — | —¹ | 1.2 | 2021-08 | PILLAR_GUIDE |
| 13 | harlembling.com | stainless-steel-earrings | #25 | 1662 | 8 | 13 | 7 | 2ul | Art+FAQ+Per+Org+WP+Prod | Luke Bright | 7.8 | 2026-03 | PILLAR_GUIDE |
| 14 | thevintagepearl.com | gold-plated | #41 | 1407 | 14 | 6 | 9 | 0 | Art+Per+Org+Bc+WP+Img | Sanjana Jain | 0.0 | 2023-04 | PILLAR_GUIDE |
| 15 | sunrisebling.com | tarnish | #56 | 1414 | 14 | 39 | 6 | 15ul/2ol | Art+Per+Org+WP | Zuo Han | 4.2 | 2026-03 | PILLAR_GUIDE |
| 16 | statementcollective.com | stainless-steel (care) | #1~ | 832 | 6 | 4 | 2 | 2ul | Art+FAQ+Per+Org+Bc+WP | Daniel Lowry | 0.0 | 2022-04 | TUTORIAL_HOWTO |
| 17 | statementcollective.com | gold-plated **vs** solid | #91 | 2633 | 6 | 9 | 6 | 3ul | Art+Per+Org+Bc+WP | Vic N | 0.0 | 2023-04 | COMPARISON_VS |
| 18 | mejuri.com | waterproof (styling) | #18 | 974 | 2³ | 6 | 4 | 2ul | Art+FAQ+Per+Org+Img | Mejuri Team | 1.0 | 2026² | LISTICLE_TIPS |
| 19 | preciouspulsejewelry.com | tarnish (brand roundup) | #34 | 4367 | 14 | 16 | 34 | 26ul/2tbl | Art+Per+Org+WP | Mark Barry | 1.1 | — | LISTICLE_TIPS |
| 20 | faire.com | waterproof | #39 | 1579 | 16 | 2 | 100* | 0 | — | — | 1.9 | — | LISTICLE_TIPS⁴ |
| 21 | atoleajewelry.com | tarnish (6 types) | #46 | 1410 | 6 | 7 | 4 | 2ul | Art+Per+Org+Bc+Img | C B | 5.0 | 2024-04 | LISTICLE_TIPS |
| 22 | saltycali.com | tarnish | #9 | 294 | 4 | 0 | 11 | 0 | — | — | 3.4 | — | MYTH_DEBUNK |
| 23 | oceanwavejewelry.com | waterproof/tarnish | #1 | 512 | 7 | 0 | 15 | 0 | — | — | 0.0 | — | PRODUCT_MICROGUIDE |
| 24 | puravidabracelets.com | waterproof | #1 | 403 | 0 | 6 | 0 | 2ul | Org | — | 0.0 | — | PRODUCT_MICROGUIDE |
| 25 | nypost.com | tarnish (best-of) | #4 | 894 | 6 | 1 | 9 | 1ul | Art+Per+Org+Prod+Img | Sophie Cannon | 6.7 | 2025-11 | NEWS_EDITORIAL⁴ |

¹ author field caught site-name/"published date:" boilerplate, not a real byline — counted as no-author. ² malformed RFC date in source; year approximate. ³ Mejuri is partly headless-rendered; body H3 sections under-captured (real structure is richer than 2 H2). ⁴ faire = B2B marketplace listing, nypost = press commerce roundup — **outliers, not brand-blog models** (kept for completeness).

### Per-topic winners (best US position wins the query)

- **waterproof-jewelry:** #1 puravida (PMG 403w) · #1 oceanwave (PMG 512w) · **#5 gldn (DEFINITION_QA 779w/6H2)** ← best real blog · #18 mejuri (LISTICLE) · #69 clarajane (DEFINITION 416w)
- **stainless-steel-jewelry:** **#1 artizanjoyeria (DEFINITION_QA 1814w/6H2+19H3 pros-cons+FAQ)** · #22 monera (DEFINITION 780w) · #56 bluestreak (DEFINITION 1154w) · AU#1 insyncdesign (DEFINITION 1471w) · AU#1 statementcollective (TUTORIAL care 832w)
- **stainless-steel-earrings:** #25 harlembling (PILLAR 1662w, TOC+FAQ)
- **tarnish-free-jewelry:** #1 oceanwave (PMG) · #1 helloadorn (DEFINITION 618w) · **#4 nypost (best-of)** · **#9 saltycali (MYTH 294w)** · #45 magnoliaandtulle (DEFINITION 1442w material-compare)
- **gold-plated-jewelry:** #19 simpleanddainty (PILLAR types 2565w) · **#34 statementcollective (DEFINITION pros-cons 1397w)** · #41 thevintagepearl (PILLAR 14H2 Q-cluster) · #74 jewelersmutual (DEFINITION 1139w) · AU#1 nelsoncoleman (DEFINITION TLDR-first "does X tarnish")

---

## B. Cross-sample conclusions (25 articles)

**1. DEFINITION_QA is the workhorse of jewelry info-SERP — 11/25 (44%).** For "what is X / is X good / pros-&-cons / does X tarnish," the winning shape is a definitional explainer, not a how-to or listicle. It takes #1 for both head terms (artizanjoyeria stainless #1, helloadorn tarnish #1) and dominates the long tail.

**2. Word count varies ~15× (294 → 4,367; median 1,154). No "right" length.**
- DEFINITION_QA winners cluster **600–1,800w** (artizanjoyeria #1 at 1,814; gldn #5 at 779; helloadorn #1 at 618).
- Thin pages still rank: oceanwave/puravida/clarajane (#1/#1/#69) run **400–510w**; saltycali takes #9 on **294w**.
- The 4,367w monster (preciouspulse) is a 12-brand roundup, not an explainer — length came from product blocks, and it only reached #34.

**3. H2 count varies 0 → 16 (median 6).** DEFINITION_QA winners sit at **5–8 H2**. Above ~12 H2 you're in PILLAR/question-cluster territory (sunrisebling 14, thevintagepearl 14). Several #1 pages use semantic-heading-free layouts (clarajane 0 H2, puravida 0 H2) — Google still parses them.

**4. External authority citations ≈ ZERO — 1/25 (one link, nelsoncoleman).** This is the single strongest finding. **Nobody cites ASTM/Mohs/peer-review/.gov.** A pipeline rule like "RAG-Full mode ⇒ ≥5 external citations" is over-fit; the cohort wins citing nothing.

**5. Brand mentions in body are low — median 0/1k (range 0–7.8).** 9/25 never name themselves in body text at all. The high-density ones are commerce-led (harlembling 7.8, nypost 6.7 self-references, atolea 5.0). **Pure-info winners (gldn 1.3, artizanjoyeria 0.0, magnoliaandtulle 0.0, insyncdesign 0.0) keep body brand density ≈0** and carry brand via byline/footer/product cards.

**6. Schema is LIGHT — and 20% rank with none.**
- 16/25 carry `Article`/`BlogPosting`; **5/25 (oceanwave, saltycali, clarajane, simpleanddainty, faire) rank with zero schema.**
- Modal "winning" signature: **`Article + Person + Organization + WebPage`** (+ `BreadcrumbList`/`ImageObject` on the better-built ones).
- **`FAQPage` is rare: explicit FAQ section in 28% (7/25), but only 12% (3/25) actually mark it with FAQPage schema.** FAQ is optional, not table stakes.
- **None of the templated-AI blocks** ("Why Trust This Guide" / "Key Takeaways" / a mandatory "On camera" video H2) appear in any of the 25 — those are an AI-content fingerprint, never a competitor pattern.

**7. E-E-A-T signals present but lightweight.** 16/25 (64%) carry a genuine person byline (`Person` schema). Dates exposed on only 15/25 — and stale dates still win (magnoliaandtulle 2020, simpleanddainty 2021, gldn 2022 all rank). Some bump to 2026. Freshness helps but isn't required.

**8. Opening patterns:** DIRECT_INTRO (14/25) ≫ QUESTION_TEASE (5) > STAT_LEAD / MYTH_BUST / TLDR_FIRST / RELATABLE_HOOK / DEFINITION_LEAD (1 each). Best brand-blog openers are gldn's relatable hook ("We've all been there… can I wear this in the water?") and nelsoncoleman's snippet-bait TLDR ("**Yes**, gold-plated jewelry can tarnish over time…").

**9. Closing patterns:** SUMMARY_WRAP (15/25) ≫ BRAND_PRODUCT_TIE (3) > PRODUCT_GRID/PRICES (2) / INVESTMENT-VERDICT (2) > RELATED_LINKS / READER_COMMENTS / AUTHOR_BIO (1 each). The soft brand-tie close ("With our waterproof jewelry you'll find styles you'll never want to take off") is the standard, never a hard CTA.

---

## C. Structure recommendations for the Wave-1 info cluster

**Strategic frame:** the planning target ("Stylr") is the **pure-informational** SEO arm; a sister brand owns commercial intent. So Stylr should sit at the **low-brand-density, info-first** end the cohort rewards: **body brand density ≈ 0/1k, no hard product CTA, soft internal link only.** Avoid PRODUCT_MICROGUIDE entirely — those thin merch-y `/pages/` (oceanwave/puravida) belong to the commerce side, not the info arm.

### Per-topic mapping

| Wave-1 slug | Archetype | Words | H2 | FAQ? | Opening | Closing | Schema | Cohort model |
|---|---|---|---|---|---|---|---|---|
| **is-waterproof-jewelry-real** | DEFINITION_QA (myth-aware) | 800–1,100 | 5–7 | optional (skip or 3-Q) | QUESTION_TEASE / mild MYTH-bust ("Is it actually waterproof? Sort of — here's the truth") | soft brand-tie + TL;DR table | Art+Per+Org+WP | gldn #5 (779w/6H2) + saltycali #9 myth opener |
| **how-to-clean-stainless-steel** | TUTORIAL_HOWTO | 800–1,200 | 6–9 (steps) | **yes + FAQPage** | TLDR-first answer | step recap + soft tie | Art+**FAQ**+Per+Org+Bc | statementcollective care AU#1 (832w/6H2+FAQ) |
| **does-stainless-steel-tarnish** | DEFINITION_QA | 700–1,000 | 6–8 | optional | **TLDR-FIRST** ("No — true stainless steel resists tarnish, but…") for featured snippet | verdict/summary | Art+Per+Org | nelsoncoleman "does-gold-plated-tarnish" (TLDR-first) |
| **what-is-stainless-steel-jewelry** | DEFINITION_QA (head term → PILLAR upgrade path) | 1,100–1,800 | 5–8 | optional (artizanjoyeria #1 has one) | DEFINITION_LEAD ("Stainless steel jewelry is…") | summary + internal links | Art+Per+Org+WP(+Img) | **artizanjoyeria #1 (1,814w)** / bluestreak (1,154w); upgrade = harlembling PILLAR w/ TOC |
| **can-you-shower-with-stainless-steel** | DEFINITION_QA | 700–1,000 | 5–6 | optional | **TLDR-FIRST** (yes-with-caveats in sentence 1) | care recap | Art+Per+Org | thevintagepearl "Can you shower with…" H2 + nelsoncoleman TLDR |

**Adjacent clusters (later expansion):** `gold-plated-vs-solid-gold` / `gold-filled-vs-plated` → **COMPARISON_VS** (1,100–1,700w, 5–8 H2 incl. a comparison table, verdict close — beat statementcollective's bloated 2,633w #91). `jewelry-that-wont-tarnish` / `types-of-…` → **PILLAR_GUIDE** (1,500–2,200w, 8–15 H2, TOC + FAQ — head terms only; sunrisebling/harlembling models). `is-stainless-steel-hypoallergenic` → **DEFINITION_QA** + the *one* place to add a single authority outlink (AAD/Mayo on nickel allergy) — a cheap E-E-A-T edge since **0 competitors cite anyone**.

### Master shape spec (grounded in the 25-sample bands)

- **DEFINITION_QA** (default, ~half the calendar): 800–1,500w · 5–8 H2 · FAQ optional · `Article+Person+Organization+WebPage` · brand/1k 0 · open QUESTION_TEASE/DEFINITION_LEAD/TLDR · close SUMMARY_WRAP + soft internal link.
- **TUTORIAL_HOWTO** (care/clean queries): 800–1,200w · 6–9 step H2 · **FAQ + FAQPage** · `+BreadcrumbList` · open TLDR-first · close step recap.
- **COMPARISON_VS** (X vs Y): 1,100–1,700w · 5–8 H2 + table · verdict close.
- **PILLAR_GUIDE** (head terms only): 1,500–2,200w · 8–15 H2 + TOC · FAQ yes · fuller schema (`+BreadcrumbList+ImageObject`).
- **MYTH_DEBUNK** (sparingly, "is X real / too good to be true"): 700–1,200w · 4–7 H2 · myth-bust open · empowerment close.

### Anti-fingerprint checklist (0/25 competitors do these — drop them)
- ❌ "Why Trust This Guide" block · ❌ mandatory "Key Takeaways" · ❌ mandatory "On camera / Watch" video H2 · ❌ FAQ on *every* article (use only ~28% of the time, when the query is genuinely multi-question) · ❌ forced ≥5 external citations (cohort cites ~0).
- ✅ Keep: one genuine `Person` byline + `<time>` date + light `Article+Person+Organization` schema · near-zero body brand density · soft summary/internal-link close.

---

**Bottom line:** jewelry info-SERP is won by **lean DEFINITION_QA explainers (600–1,800w, 5–8 H2), light schema, a real byline, ~zero body-brand-mentions, and zero external citations.** Biggest wins: default to DEFINITION_QA, answer-first (TLDR) for "does/can" queries, reserve PILLAR for head terms, and do *not* ship templated trust/takeaways/video blocks that no ranking competitor uses.

Raw artifacts (results.json / classified.json / keywords.json / backlinks.json / onpage.json) are written to the skill's `--out-dir`.
