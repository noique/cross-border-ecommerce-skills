> Worked example — output of the `serp-content-teardown` skill run on the waterproof / stainless-steel women's jewelry niche (US SERPs, Semrush 2026-04 pull). Illustrative; numbers are Semrush estimates. "Stylr" is the planning-target site in this example.

# Jewelry Niche — SEO / GEO / Backlink / Keyword Teardown (Part 2)

Same local data as Part 1 (92 `serp_urls` + 44 `broad-match` Semrush xlsx + 26 fetched HTML), extended into four more dimensions. **Pure local data, zero paid API, no live AI probing.** Snapshot = Semrush 2026-04-03 pull (US).
Artifacts: `keywords.json` · `backlinks.json` · `onpage.json` (+ `classified.json`/`results.json` from Part 1).

---

## 1 — Keyword distribution + core keywords

**Keyword universe (deduped): 37,428 keywords / 1,048,160 monthly volume.** But most is product/style long-tail noise. **The usable informational slice = 1,393 kw / 211,780 volume (4%).**

| Dimension | Distribution |
|---|---|
| Intent | Commercial 1,566kw/463k vol · **Informational family ≈1,393kw/211k vol** · Transactional 944kw/128k |
| Volume bands | 1k+: 119kw/384k · 300-999: 317kw/150k · 100-299: 972kw/155k · <50: 34,587kw (long tail) |
| KD bands | **0-9: 1,802kw/209k vol** · 10-19: 1,244kw/229k · 20-29: 664kw/243k · 30+: 199kw |

### The difficulty cliff (most important strategic fact)
Head terms are link-gated and unwinnable for a new site short-term; **the question long-tail is KD 0-15, winnable on content alone**:

| Cluster | Head term (hard) | Question long-tail (winnable, KD≤15) |
|---|---|---|
| WATER_SHOWER | waterproof jewelry **18,100/KD31** | can you shower with stainless steel jewelry 110/**KD0** · is stainless steel jewelry waterproof 140/**KD0** · can gold plated jewelry get wet 170/KD1 |
| STAINLESS | stainless steel jewelry **14,800/KD30** | is stainless steel jewelry good 590/KD7 · 316l stainless steel jewelry 880/KD4 · hypoallergenic stainless steel jewelry 720/KD3 |
| GOLD_PLATED | gold plated jewelry **8,100/KD24** | how long does gold plated jewelry last 880/KD6 · what is gold plated jewelry 720/KD10 · is gold plated jewelry worth anything 590/KD0 |
| TARNISH | — | does stainless steel jewelry tarnish 1,000/KD10 · will stainless steel jewelry tarnish 720/**KD2** · does stainless steel jewelry rust 260/KD2 · tarnish free gold jewelry 1,300/KD2 |
| CARE_CLEAN | — | how to clean stainless steel jewelry 1,300/KD6 · how to clean stainless steel necklace 880/KD2 · gold plated jewelry care 170/KD0 |
| COMPARISON | — | gold filled jewelry vs gold plated 720/KD15 · titanium vs stainless steel earrings 90/KD2 |
| HYPOALLERGENIC | — | does stainless steel jewelry turn green 170/KD2 · does stainless steel jewelry turn skin green 140/**KD0** · nickel free stainless steel jewelry 110/KD4 |

**Takeaway:** the Wave-1 topics sit squarely in the KD 0-15 sweet spot. Eat the question long-tail first to build topical authority, then come back for the head terms.

---

## 2 — Backlink / authority thresholds

Source: `serp_urls` Organic rows — `Page AS` (page-level Authority Score 0-100) / `Ref.Domains` / `Backlinks`.
> **Honest limit:** this is **page-level**, the export carries no **domain-level DR** — so the read is "page-level links aren't the bottleneck," not a quantified domain-authority floor. (n slightly inflated by dual snapshots; medians unaffected.)

| Cluster | top-3 median | top-10 median | Read |
|---|---|---|---|
| WATER_SHOWER | AS13 / RefDom2 / BL2 | **AS18 / RefDom4 / BL4** | single-digit ref.domains gets top-10 |
| STAINLESS | AS12 / RefDom2 / BL2 | **AS12 / RefDom1 / BL2** | almost no page-level links needed |
| TARNISH | AS5 / RefDom2 / BL5 | **AS15 / RefDom2 / BL3** | very low |
| GOLD_PLATED | AS19 / RefDom3 / BL4 | **AS12 / RefDom1 / BL3** | very low |

**Weak-link winners (beatable targets / proof content wins):**
- `tarnish-free-jewelry` **#1 = stelladot.com, page AS 0 / 0 ref.domains / 0 backlinks** (pure domain-authority + relevance)
- `waterproof-jewelry` #1 = oceanwave AS16/14ref/46bl; #3 = baublebar AS13/2ref/2bl
- `gold-plated-jewelry` #1 = pandora AS19/7ref; #2 = astrid&miyu AS19/3ref; #3 = oakandluna AS11/**1ref**

**The only place real links matter = the very top of head terms:** stainless-steel-jewelry #1 = thesteelshop AS64/37ref/1196bl. But that's #1, not top-10.

**Takeaway:** for the informational long tail, **backlinks are not the bottleneck and per-article link-building is low ROI.** Priority = domain-level credibility (a few quality referring domains site-wide) ≫ per-page links.

---

## 3 — GEO / AI Overview

**The core clusters are heavily AI-Overview-saturated** (informational keywords overall 22% trigger AIO, but by cluster):

| Cluster | info kw | AIO% | AIO volume |
|---|---|---|---|
| CARE_CLEAN | 30 | **93%** | 6,270 |
| HYPOALLERGENIC | 13 | **92%** | 1,200 |
| WATER_SHOWER | 40 | **88%** | 21,230 |
| COMPARISON | 17 | **88%** | 1,160 |
| TARNISH | 28 | **82%** | 6,740 |
| GOLD_PLATED | 61 | **80%** | 14,900 |
| STAINLESS | 131 | 48% | 27,910 |

→ nearly every Wave-1 question long-tail triggers **AI Overview + People-also-ask + Video** simultaneously. **No GEO = ceding 80-93% of target traffic to the AI summary.**

### Counterintuitive finding: rich schema ≠ AI citation
The pages that GET cited in AI Overviews (artizanjoyeria, helloadorn, puravida, simpleanddainty) carry **minimal-to-zero schema** (helloadorn = Organization only, puravida = Organization only, simpleanddainty = **0**); the richest-schema pages (thevintagepearl 13 types, harlembling 11) are **not cited**.

Citation tracks with **① an organic ranking + ② a clean, direct answer to the question** — not @graph depth.
> Limit: Semrush's AIO-citation capture is sparse (only ~4 cited pages had schema in-sample), so this is "schema depth didn't gate citation here," not "schema is useless."

**GEO node coverage across the 25 fetched pages:** Article 15 · Person 15 · Organization 18 · **FAQPage only 3 · BreadcrumbList 7 · VideoObject 0 · HowTo 0**.
→ competitors broadly skip HowTo/VideoObject schema — a cheap differentiation (though per the finding above, the real citation lever is answer clarity, not schema).

**Relationship to a schema/@graph buildout (`structured-data-buildout`):** the @graph buildout buys **correct Google parsing + rich-results eligibility + hygiene** — worth doing, but it is **not** the AI-citation lever. The AI-citation lever = organic ranking (low bar, see §2) + answer-first content (the TLDR-first DEFINITION_QA shape) + covering the PAA question cluster. This is what ties all four dimensions together.

---

## 4 — On-page SEO (25 pages re-parsed)

| Signal | Data | Verdict |
|---|---|---|
| meta description | **25/25**, median 152 chars | table stakes, mandatory |
| canonical | **25/25** | table stakes |
| single H1 | 18/25 (3 had 0, 4 had multiple) | hygiene; 72% compliant — enforce single H1 |
| keyword in title | **22/25 (88%)** | near-universal exact/near-match, front-loaded |
| keyword in H1 | 19/25 (76%) | |
| keyword in meta | 21/25 (84%) | |
| question-format title | 7/25 | minority; most are "keyword + specificity hook" |
| title length | median **59** (30-89) | hits the 50-60 sweet spot |
| body internal links | median **10** (0-510*) | topical-cluster signal; *510 = product-link spam outlier |
| body external links | median **1** | confirms near-zero outbound from a different angle |

**Winning title patterns** (keyword front-loaded + specificity): `Waterproof Jewelry 101: What You Can (and Can't) Wear in Water | GLDN` · `The Pros and Cons of Stainless Steel Jewelry` · `12 Brands of Gold Jewelry That Won't Tarnish in 2025`. Brand name goes in the suffix.

---

## 5 — Integrated action sequence (four dimensions + structure)

**Core narrative:** in this niche, **content shape + topical coverage + GEO are the levers; backlinks are barely a gate; head terms are a slow burn earned through domain authority.**

1. **Prioritize topics by KD × AIO × volume** — eat the KD≤15 question long-tail first (§1). Each question keyword = one DEFINITION_QA / TUTORIAL (Part 1 shape spec). **Do not open on the head terms** (`waterproof jewelry` / `stainless steel jewelry`, KD30+, link-gated).

2. **Write every article for AI Overview** (§3): answer-first (sentence 1 directly answers yes/no/number), explicitly cover that keyword's People-also-ask sub-questions as H2/H3, keep extractable concise paragraphs. This matters more than schema for getting cited.

3. **Treat schema as hygiene + rich-results eligibility** (via `structured-data-buildout` / your @graph buildout): Article+Person(with Wikidata)+Organization+BreadcrumbList is the baseline; FAQPage only on genuine FAQ pages; care/how-to articles can add HowTo+VideoObject (0 competitor coverage = cheap edge) — but don't expect schema alone to win AI citations.

4. **Don't buy per-article links** (§2). Spend on content coverage + a few quality site-wide referring domains for domain credibility. Treat the "weak-link winners" (stelladot/oakandluna/baublebar) as near-term beatable benchmarks.

5. **On-page must-haves** (§4): keyword-front-loaded title (50-60 chars) + specificity hook + brand suffix; single H1; every article gets a meta description + canonical; ~8-12 topical internal links; 0-1 external links.

6. **Reuse Part 1's shape spec + anti-fingerprint checklist**: DEFINITION_QA default (600-1800w/5-8 H2), TLDR-first for "does/can" queries, PILLAR only for head terms; drop the templated trust/takeaways/video/forced-FAQ/forced-citation blocks.

**One line:** the info arm should be a "**low-KD question long-tail × answer-first × AI-Overview-optimized**" content machine, not a link-building project; head terms are a later harvest (after domain authority builds), not the opening move.

---

Honest blind spots: KD / volume / Page AS are Semrush 2026-04 estimates; no domain-level DR available; AI-citation sample is sparse (directionally trustworthy, don't over-read the precise numbers); true AI-citation rate would require live Perplexity/Gemini/ChatGPT testing (paid/external — needs explicit authorization). Raw artifacts (keywords.json / backlinks.json / onpage.json / results.json / classified.json) are written to the skill's `--out-dir`.
