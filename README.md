# Cross-Border E-Commerce AI Skills

**54 AI-powered skill templates for cross-border e-commerce — from brand strategy to Amazon operations to DTC growth to finance & capital ops to affiliate-program building to EU channel entry to overseas-buyer prospecting + earned-media press discovery + Reddit pre-purchase VOC.**

Compatible with Claude Code (`~/.claude/commands/`), Google Antigravity (`SKILL.md`), and any AI IDE with skill/prompt support.

[中文说明](#中文说明) | [English](#english)

---

## English

### What is this?

A collection of **54 AI agent skills** (structured prompt templates) that automate the entire cross-border e-commerce workflow — brand strategy, market research, product selection, listing optimization, advertising, DTC site operations, **finance & capital management**, **affiliate-program building**, **EU channel & market entry**, social media, influencer marketing, **overseas-buyer outbound prospecting**, **earned-media press discovery**, and **Reddit pre-purchase VOC**.

Two formats:
- **Single-file skills** (45) — one `.md` file each, drop into your AI IDE's skill directory.
- **Multi-file skill packages** (5, under `brand-strategy/`, `outbound-prospecting/`, and `voc-tools/`) — `SKILL.md` + `references/` + `templates/` (incl. Python scripts and CSV trackers). Point your AI IDE at the package directory.

Plus **7 standalone tools** under `tools/` (Python utilities used by skills, also runnable independently): `backlink-kol-extractor`, `trustpilot`, `linktree-expander`, `contact-extractor`, `api-pacer`, `fetchlib`, `browser-fetch`.

### Skill Map (54 skills across 13 chains)

```
                        ┌─────────────────────────────────────┐
                        │     Brand Strategy Chain (10)        │
                        │                                     │
  Market Scan ──► Track Hypothesis ──► Deep Validation ──► Strategy Plan
       │                                                       │
       │         Annual Plan ◄── Budget Ops                    │
       │                                                       ▼
       │                                    IMC Framework ──► Knowledge Base
       │                                         │
       │              A/B Compare    Chart Visualize   GTM Launch
       │                                         │
       ▼                                         ▼
  ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
  │ Amazon Chain (14) │   │ DTC Site (5)     │   │ Social & KOL (5) │
  │                  │   │                  │   │                  │
  │ Selection        │   │ SEO Diagnostic   │   │ TikTok Growth    │
  │ Shortlist        │   │ SEO Playbook     │   │ YouTube Ops      │
  │ Market Research  │   │ SEM Ads          │   │ Content Calendar │
  │ IP Risk          │   │ Conversion UX    │   │ Influencer Mktg  │
  │ Supplier         │   └──────────────────┘   │ User Lifecycle   │
  │ Keywords         │                          └──────────────────┘
  │ Listing Copy     │   ┌──────────────────┐   ┌──────────────────┐
  │ Main Image       │   │ Offline (1)      │   │ VOC Tools (3)    │
  │ A+ Content       │   │                  │   │                  │
  │ Compliance       │   │ US Retail        │   │ Reddit VOC (NEW) │
  │ Pre-Launch       │   └──────────────────┘   │ Trustpilot Quick │
  │ Ad Architecture  │                          │ Trustpilot Deep  │
  │ Weekly Ad Review │                          └──────────────────┘
  │ Ad Diagnosis     │
  └──────────────────┘

  ┌──────────────────────────────────────────────────────────────┐
  │ Finance & Capital (8) — NEW                                    │
  │ Unit-Economics · FX/Payout · Tax-Nexus · Cashflow             │
  │ Pricing · Reconciliation · Entity-Structure · Capital-Stack   │
  └──────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────┐
  │ Affiliate & Partnership (2) — NEW                              │
  │ Readiness-Audit (affiliate's-POV mirror of CRO) ·             │
  │ Program-Ops (AI: DB → score → outreach → activate → report)   │
  └──────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────┐
  │ Channel & Market Entry (2) — NEW                               │
  │ EU-Channel-Entry (SSPV · RCS · growth flywheel) ·            │
  │ Price-System & Channel-Conflict Guard                         │
  └──────────────────────────────────────────────────────────────┘
```

---

### Brand Strategy Chain (10 skills)

**4-Round Analysis Pipeline + Planning + Execution + Tools**

| Skill | What it does |
|-------|-------------|
| [brand-market-scan](brand-strategy/brand-market-scan.md) | Round 1: Market panoramic scan — 4-layer user insight, VOC matrix, competitive landscape, Semrush auto-scan |
| [brand-track-hypothesis](brand-strategy/brand-track-hypothesis.md) | Round 2: Track hypothesis generation — 3-5 market tracks, DTNICE classification, GTM flywheel |
| [brand-deep-validation](brand-strategy/brand-deep-validation.md) | Round 3: Deep hypothesis validation — 5D framework, SEO traffic model, benchmark cases, Zone 4 |
| [brand-strategy-plan](brand-strategy/brand-strategy-plan.md) | Round 4: Brand strategy & execution — 7-element positioning, 4 pillars, pricing, narrative, roadmap |
| [brand-imc-framework](brand-strategy/brand-imc-framework.md) | IMC integrated marketing — Audience/User dual-path, 6-stage funnel, channel mix, execution calendar |
| [brand-annual-plan](brand-strategy/brand-annual-plan.md) | Annual planning — BSC scorecard, 52-week calendar, quarterly OKRs, resource allocation |
| [brand-budget-ops](brand-strategy/brand-budget-ops.md) | Budget planning & control — 10-category budget model, monthly tracking, ROI by channel |
| [brand-knowledge-base](brand-strategy/brand-knowledge-base.md) | Obsidian knowledge base — batch-creates 30-50 interlinked .md files from all rounds |
| [brand-ab-compare](brand-strategy/brand-ab-compare.md) | 8-dimension A/B quality comparison between two brand strategy report sets |
| [brand-chart-visualize](brand-strategy/brand-chart-visualize.md) | Auto-generate charts (radar, bar, waterfall, scatter, etc.) via AntV API for all reports |

### Amazon Operations Chain (14 skills)

| Phase | Skill | What it does |
|-------|-------|-------------|
| Selection | [amazon-product-selection](amazon/amazon-product-selection.md) | Score and rank Top 30 potential products |
| Selection | [amazon-product-shortlist](amazon/amazon-product-shortlist.md) | Feasibility screening, GTM flywheel check, Go-List |
| Research | [amazon-market-research](amazon/amazon-market-research.md) | Full market research: VOC matrix, competitor teardown, SWOT |
| Research | [amazon-ip-risk-assessment](amazon/amazon-ip-risk-assessment.md) | Patent + trademark risk, design comparison, risk rating |
| Research | [amazon-supplier-decision](amazon/amazon-supplier-decision.md) | Supplier evaluation, cost breakdown, red flag detection |
| Listing | [amazon-keyword-research](amazon/amazon-keyword-research.md) | Keyword library: 3-tier CPC, COSMO/Rufus/A10 SEO |
| Listing | [amazon-listing-copywriter](amazon/amazon-listing-copywriter.md) | Title, bullet points, A+ description, Search Terms |
| Listing | [amazon-main-image-prompt](amazon/amazon-main-image-prompt.md) | Main + secondary image design briefs and AI prompts |
| Listing | [amazon-aplus-image-prompt](amazon/amazon-aplus-image-prompt.md) | A+ Content module layout, Brand Story, image prompts |
| Launch | [amazon-compliance-review](amazon/amazon-compliance-review.md) | 3-dimension audit: platform rules, legal/IP, AI search |
| Launch | [amazon-pre-launch-review](amazon/amazon-pre-launch-review.md) | Final pre-launch checklist across all SKILL outputs |
| Ads | [amazon-ad-architecture](amazon/amazon-ad-architecture.md) | PPC campaign structure: SP/SB/SD/SBV, budget, bid strategy |
| Ads | [amazon-weekly-ad-review](amazon/amazon-weekly-ad-review.md) | Weekly ad review: ACoS/TACoS, Search Terms, action list |
| Ads | [amazon-ad-diagnosis](amazon/amazon-ad-diagnosis.md) | Existing product diagnosis: 4-stage optimization pipeline |

### DTC Site & Traffic (5 skills)

| Skill | What it does |
|-------|-------------|
| [dsite-seo-diagnostic](brand-strategy/dsite-seo-diagnostic.md) | **NEW** — Entry-orchestrator skill for live-site SEO traffic-drop diagnostics. 7-dimension diagnosis (traffic curve / keyword loss / single-point risk / i18n pollution / backlink quality / content ROI / KPI audit) → algorithm-event alignment → restart roadmap. Chains `xlsx` / `dsite-seo-playbook` / `trustpilot-voc-deep` / `competitors-analysis` / `backlink-kol-extractor` / `report-pdf-export`. Output: deliverable PDF (A4 landscape, hides internal SKILL refs). |
| [dsite-seo-playbook](brand-strategy/dsite-seo-playbook.md) | Full SEO playbook: technical audit, keyword strategy, content plan, Core Web Vitals |
| [dsite-sem-ads](brand-strategy/dsite-sem-ads.md) | SEM & paid ads: 10-platform comparison, AIPL funnel, budget allocation |
| [dsite-conversion-ux](brand-strategy/dsite-conversion-ux.md) — **UPGRADED v3.7** | Live-site **CRO audit / 转化率检测**, rebuilt for **multi-agent concurrency on Claude Code**. **Step 0** fans out 5 parallel recon subagents (PDP / discovery / trust / checkout / competitor) via the `Workflow` tool with `StructuredOutput` schemas → reconPool → parallel **6-module framework** (trust / discovery / product-info / checkout / AOV-LTV / urgency) — retail-analogy CRO × Shopify benchmarks × ICE A/B × AICPL LPO × 35-day welcome flow. v3.7 adds a **technical-health & tracking-integrity check** (console errors / pixel firing / CWV / 404 / mobile-sticky — broken tracking silently invalidates all measurement → highest-priority finding), a mandatory **copy-rewrite table** (current → A/B) + **objection-handling table**, a **quick-win vs high-impact dual-bucket** with wall-clock effort, and A/B **stop-rule discipline**. Honesty preserved — data-credibility statement kept, lift figures stay ⚠️ hypotheses (no fabricated funnel numbers). Uses **browser-class MCP** (Claude in Chrome / Preview) for what static fetch can't see; chains `/dsite-seo-playbook` / `/dsite-sem-ads` / `/report-pdf-export`. |
| [serp-content-teardown](brand-strategy/serp-content-teardown/SKILL.md) — **NEW v3.6** | Multi-file skill: deterministic (no-LLM) SERP/content reverse-engineering from local Semrush xlsx + competitor HTML. Parses serp_urls + broad-match, curl-fetches top competitor articles (html5lib void-tag-safe), computes per-article structure → **8 article archetypes** + opening/closing patterns, then keyword distribution + core keywords, backlink/authority thresholds (Page AS / Ref.Domains / Backlinks) + weak-link winners, AI-Overview (GEO) saturation + schema readiness, on-page SEO. Output: per-topic content blueprint (which archetype / word / H2 / schema / FAQ / keyword / authority / GEO posture). Pairs with `backlink-kol-extractor` (links) + `structured-data-buildout` (schema). |

### Finance & Capital (8 skills) — NEW v3.8

Operator-facing finance/CFO chain for China→US/EU DTC + Amazon sellers — the actuals / profitability / tax / cash / financing side that the planning-oriented `brand-budget-ops` doesn't cover. Every skill is grounded in real tools + 2026 regulations, carries an explicit **YMYL disclaimer** (planning aid, NOT professional tax/legal/accounting advice — verify with a licensed CPA), and tags every rate/threshold/date as point-in-time. Built and cross-validated from a dual-source research pass (multi-agent web research + an independent deep-research report).

| Skill | What it does |
|-------|-------------|
| [finance-landed-cost-unit-economics](finance/finance-landed-cost-unit-economics.md) | **Anchor** — fully-loaded landed cost → **CM1/CM2/CM3** waterfall → break-even ROAS/ACoS → per-SKU keep/kill/reprice + tariff/return sensitivity. Folds in Amazon 2026 fee changes (inbound placement ↑, Low-Inventory-Level Fee, fuel/inflation surcharge). |
| [finance-fx-payout-optimizer](finance/finance-fx-payout-optimizer.md) | Collection · 结汇 · FX hedging. The "two numbers" (gross revenue vs RMB cash-landed) + FX-drag %, provider benchmark (PingPong/WorldFirst/Airwallex/Payoneer/Wise vs ACCS), natural-hedge plan, and a SAFE / 单证一致 compliance checklist (incl. the 2026-01-01 ≥¥5,000 AML monitoring). |
| [finance-tax-nexus-vat-diagnostic](finance/finance-tax-nexus-vat-diagnostic.md) | Per-jurisdiction registration-obligation map + filing calendar + EPR streams. Covers EU OSS/IOSS, the **€3 fixed customs duty** (Reg (EU) 2026/382 — kept distinct from the not-yet-law ~€2 handling fee), UK £135, US economic nexus, and China 9610/9710/9810 + 出口退税. |
| [finance-cashflow-runway-forecaster](finance/finance-cashflow-runway-forecaster.md) | CCC (DIO/DSO/DPO) + a **13-week** rolling direct-method forecast that models the Amazon DD+7/DDBR reserve correctly + a reorder-point capital trade-off → flags the week cash goes negative. |
| [finance-pricing-margin-guard](finance/finance-pricing-margin-guard.md) | Dynamic price floor/ceiling, break-even ROAS = 1/CM%, FX-sensitivity-per-1%, marketplace price-parity + anti-gouging guardrails — fixes the static-floor trap when 2026 fees rise. |
| [finance-reconciliation-bookkeeping](finance/finance-reconciliation-bookkeeping.md) | Multi-channel gross-to-net reconciliation (Amazon settlement / Shopify-Stripe-PayPal payouts → bank) via the clearing-account-to-zero method, an ecommerce chart of accounts, COGS/inventory valuation. Tools: A2X / Link My Books / Synder / Finlens → QuickBooks / Xero. |
| [finance-entity-structure-advisor](finance/finance-entity-structure-advisor.md) | Entity tier (single HK Ltd → ODI → HK/SG holding → US LLC) with a "you don't need this yet" guardrail, the LRD transfer-pricing model, HK TP-doc exemption, and the 4-gate China profit repatriation. **YMYL-heavy.** |
| [finance-capital-stack-advisor](finance/finance-capital-stack-advisor.md) | Normalizes any RBF/MCA flat-fee quote to a true **effective APR** at real repayment speed (Monte-Carlo), a provider-fit matrix (Wayflyer/Clearco/8fig/Amazon Lending), UCC-1-lien / exclusivity contract traps, and chargeback/VAMP defense. |

### Social Media & Content (3 skills)

| Skill | What it does |
|-------|-------------|
| [tiktok-growth](brand-strategy/tiktok-growth.md) | TikTok full-funnel growth: content strategy, TikTok Shop, livestream, paid ads |
| [youtube-channel-ops](brand-strategy/youtube-channel-ops.md) | YouTube channel operations: content strategy, SEO, monetization |
| [social-content-calendar](brand-strategy/social-content-calendar.md) | Social media content calendar: multi-platform scheduling, content pillars |

### VOC & Review Analysis (3 skills) — NEW v3.5 adds pre-purchase VOC

VOC tools split by decision stage. Reddit / Quora capture **pre-purchase** intent (still-deciding users), while Trustpilot / Amazon Review capture **post-purchase** experience (already-bought users). Use them together for full decision-funnel coverage.

| Skill | What it does |
|-------|-------------|
| [reddit-voc](voc-tools/reddit-voc/SKILL.md) — **NEW v3.5** | Multi-file package for **pre-purchase** Reddit VOC mining. 5-step playbook (find subs across 4 dimensions → filter Top + 6 post-flair → 6-axis post teardown → insight-to-action mapping → optional 2D positioning matrix). References: 4-dimension community framework / Reddit slang dictionary (BIFL / YMMV / AITA / DAE / etc.) / 6-class post taxonomy with business-action mapping / 3 real listing+ad rewrite cases / functional-importance × satisfaction matrix. CSV templates for community map, post analysis, insight-action map. Pairs with `/trustpilot-voc-deep` for post-purchase view. |
| [trustpilot-voc-quick](brand-strategy/trustpilot-voc-quick.md) | 5-min WebFetch scan: overall rating, star distribution, recent review summaries. Ideal for brand scanning Step 0 or competitor comparison |
| [trustpilot-voc-deep](brand-strategy/trustpilot-voc-deep.md) | Full pipeline (15-40 min): Selenium scraper with proxy rotation + sentiment analysis + LDA topic modeling + AI-powered deep insights. Uses `tools/trustpilot/` Python toolkit with **AntV visualization** for report-style consistency |

### KOL & User Operations (2 skills)

| Skill | What it does |
|-------|-------------|
| [influencer-marketing](brand-strategy/influencer-marketing.md) | KOL/influencer marketing: 5-tier pyramid, ROI tracking, contract templates |
| [user-lifecycle-ops](brand-strategy/user-lifecycle-ops.md) | User lifecycle management: 5-stage funnel, retention curves, churn analysis |

### GTM & Offline (2 skills)

| Skill | What it does |
|-------|-------------|
| [brand-gtm-launch](brand-strategy/brand-gtm-launch.md) | New product GTM launch: 7-step framework, timeline, channel coordination |
| [offline-retail-us](brand-strategy/offline-retail-us.md) | US offline retail: 8-tier channel analysis, readiness assessment, cost model |

### Affiliate & Partnership (2 skills) — NEW v3.13

Building an affiliate/partnership program from the **affiliate's economics** — audit first (is your product even worth promoting?), then run the AI-automated recruit → score → outreach → activate loop. Complements `influencer-marketing` (content/relationship lens) without overlap: this is the performance/ROI lens.

| Skill | What it does |
|-------|-------------|
| [affiliate-readiness-audit](brand-strategy/affiliate-readiness-audit.md) — **NEW v3.13** | Audits a product/Listing from the **affiliate's wallet POV** — the mirror of `dsite-conversion-ux` (CRO): CRO audits "why users won't buy," this audits "why affiliates won't promote you." Affiliate ROI ledger + EPC + 3-layer arbitrage, 6-dim recruitability scorecard with score bands, admission buckets, 6 silent-rejection red flags, traffic-catch self-check + 30-day fix roadmap. Multi-agent fan-out over the 6 scoring dimensions + competitor-offer benchmark |
| [affiliate-program-ops](brand-strategy/affiliate-program-ops.md) — **NEW v3.13** | AI-automated affiliate operations pipeline: database → find candidates across the **6 affiliate ecosystems** → 100-pt AI scoring with priority bands → standardized contact collection (10 sources) → AI personalized outreach (5-element email, not mass blast) → Partner Resource Hub activation → 4-layer KPI + AI weekly report → 30-day minimum loop. Fan-out per ecosystem type via `Workflow`; reuses `outbound-prospecting` infra + `backlink-kol-extractor` |

### Channel & Market Entry (2 skills) — NEW v3.13

| Skill | What it does |
|-------|-------------|
| [eu-channel-market-entry](brand-strategy/eu-channel-market-entry.md) — **NEW v3.13** | Channel/distributor-driven Europe market entry for **US-entity brands**: US-vs-EU market logic (growth vs mature-replacement), competitive-positioning quadrant, **SSPV** user-value model (JTBD-based), **RCS** regional-combat model (Region × Channel × Service) across the 5 EU regions, channel development + enablement, price protection, overseas-org 3 stages, the 8-step Europe growth flywheel. Org/tax decisions hand off to `finance-*`. 5-region parallel analysis via `Workflow` |
| [price-system-conflict-guard](brand-strategy/price-system-conflict-guard.md) — **NEW v3.13** | Multi-channel price-system & channel-conflict guard for brands running DTC + Amazon + distribution simultaneously: cross-channel real-price diagnosis (auto-flags conflicts), the 3-layer mechanism (unified price × promo-sync × regional protection), DTC-vs-channel boundary, T-60 promo SOP. Carries a US antitrust (MAP vs RPM / Sherman Act) compliance boundary. Pluggable impl of the flywheel's price-protection step |

### Outbound Prospecting (3 skills) — v3.4 adds press discovery

End-to-end pipelines for finding overseas B2B decision-makers, KOLs, and journalists, then converting them into ready-to-message lead sheets. Each skill is a multi-file package with `SKILL.md` + scripts + references + templates.

| Skill | What it does |
|-------|-------------|
| [google-whatsapp-prospecting](outbound-prospecting/google-whatsapp-prospecting/SKILL.md) | Google-dork → WhatsApp lead pipeline. 15+ search formulas (mobile-prefix narrowed), 30+ countries with B2B-platform / time-zone / compliance flags, full GDPR-CASL-CCPA-UWG compliance reference, multi-language outreach playbook (EN/ES/PT/FR/AR), SerpAPI batch script + `wa.me` validator. |
| [linkedin-prospecting](outbound-prospecting/linkedin-prospecting/SKILL.md) | Google/Bing/Yandex/Wayback reverse-search of LinkedIn → enrichment via Apollo/Snov/Hunter/Lusha/Wiza → 4-touch outreach (CR → DM → follow-up → channel-switch). 50+ localized role keywords across 8 languages, LinkedIn ToS + quota reference, 12 DM templates across 5 archetypes (incl. voice-note opener), reply-handling matrix. |
| [media-press-discovery](outbound-prospecting/media-press-discovery/SKILL.md) — **NEW v3.4** | Muckrack-anchored journalist DB pipeline. 5 scripts (`discover_journalists` / `find_articles` / `guess_emails` / `score_and_export` / `merge_partitions`) + shared `_fetcher.py` with 4 backends (requests / remote-chrome / apify / html-dir for Cloudflare-protected pages). Multi-machine partition-merge workflow. Outputs ranked `pitch_db.csv` with journalist contacts + last topical coverage. |

Sister skills — same 4-stage shape (Search → Enrich → Outreach → Compliance), different channels. Designed to run in parallel for the same lead set.

### Tools (standalone utilities)

Standalone Python utilities under `tools/`. Each is a multi-file package with own `SKILL.md` + `scripts/` + `references/` + `templates/`. Used by skills above conditionally; also runnable independently. The three **fetch tools** — `api-pacer`, `fetchlib`, `browser-fetch` — compose into one compliant scraping pipeline (**pace → waterfall → browser L3**); the rest are data/enrichment utilities.

| Tool | What it does | Used by |
|------|-------------|---------|
| [backlink-kol-extractor](tools/backlink-kol-extractor/SKILL.md) | Extract KOL / media / affiliate prospects from Semrush competitor backlink xlsx data — 3-step methodology (domain pattern → cross-competitor validation → social handle extraction) | `influencer-marketing` (Step 2.5), `dsite-seo-playbook` (Step 4.6) — both conditionally activated when Semrush data is provided |
| [trustpilot](tools/trustpilot/) — **rebuilt v3.4** | Selenium-based Trustpilot review scraper with chained-proxy rotation, AI sentiment + topic analysis, multi-language. v3.4 rebuild: modern data-* attribute selectors (replaces 110-line sibling-XPath fallback chain), desktop-UA pin (Trustpilot serves snippet-only DOM to mobile UA), `--cutoff_date` arg, `--skip_ai` mode, redacted hardcoded proxy creds (env-var loading) | `trustpilot-voc-quick`, `trustpilot-voc-deep` |
| [linktree-expander](tools/linktree-expander/SKILL.md) — **NEW v3.4** | Batch-enrich Linktree handles into per-creator profiles via `__NEXT_DATA__` JSON parsing. Extracts IG / TikTok / YouTube / Substack / Twitter / podcast handles + bio + outbound link categorization + handle-match-scored personal_site (with `NON_PERSONAL_HOSTS` blocklist for shorteners / aggregators / docs / scheduling) | KOL discovery pipelines downstream of `backlink-kol-extractor` |
| [contact-extractor](tools/contact-extractor/SKILL.md) — **NEW v3.4** | Multi-source contact email extraction with confidence tiering. Sources: personal_site `/about` `/contact` `/press` paths (mailto/text) + YouTube Data API v3 description + Apple Podcasts RSS owner + email pattern guess (with `--verify` SMTP MX probe / Hunter.io). Outputs ranked `contact_email_1..3` + `confidence` (high / medium / low / none) | KOL outreach prep, post `linktree-expander` or `media-press-discovery` |
| [api-pacer](tools/api-pacer/SKILL.md) — **NEW v3.9** | Polite, adaptive request pacer + AWS-style full-jitter backoff for the scraping / API skills. Paces to the server's OWN rate-limit headers (`x-ratelimit-remaining` / `reset`) when present, else a configured RPS budget; full-jitter (uniform) backoff on 429/503/Retry-After. Reads the REAL budget instead of guessing a delay from a distribution — a Gaussian/uniform "human-like" sleep is not what evades rate limits. Stdlib-only (`requests` optional). Rate-limit-respecting research use only, NOT ToS-violating evasion. | `reddit-voc` (wired), + `serp-content-teardown` / `media-press-discovery` / `trustpilot` / `outbound-prospecting` (opt-in) |
| [fetchlib](tools/fetchlib/SKILL.md) — **NEW v3.10** | Compliant fetch **waterfall** for the scraping skills (built from the 2026 dual-source scraping-stack research). Escalates one tier only on a real block (Markov-style): **L1 `curl_cffi`** (TLS/JA3 impersonation, free) → **L2 Jina Reader** (`r.jina.ai` JS→markdown, free\*) → L3 `nodriver` (batch-2 plug-in) → L4 managed unblocker (paid, opt-in). Control layer = `api-pacer` (header-adaptive pace + full-jitter backoff) + **AIMD** (creep-up / cut-hard-on-block) + **circuit breaker** + per-fetch JSONL instrumentation. Honors robots.txt; **does NOT defeat access barriers / rotate IPs / forge fingerprints / handle PII** — compliant research use only. Stdlib-runnable; `curl_cffi` optional (graceful urllib fallback). Depends on `api-pacer`. | `serp-content-teardown` / `media-press-discovery` / `trustpilot` / `outbound-prospecting` / `reddit-voc` (opt-in) |
| [browser-fetch](tools/browser-fetch/SKILL.md) — **NEW v3.12** | Optional shared **browser-render** backend for `fetchlib`'s **L3** — promotes the "real browser + optional proxy" capability (the kind in `tools/trustpilot`) into one reusable module so skills stop re-implementing a browser. Pluggable engine, **default Selenium** (`register_engine()` for nodriver / camoufox / scrapling). Returns `(status, body, headers)`; normalizes a detected challenge page to `403` so `fetchlib` flags it. **Honest scope (benchmarked from a datacenter IP)**: it clears **Trustpilot-class** sites that `curl_cffi` can't render, but does NOT beat Cloudflare Managed Challenge / DataDome (Muckrack, G2) — even a real browser stalls on the challenge from a datacenter IP; those need a **residential IP** (+ maybe a Turnstile solver) or a paid unblocker, not a fancier library. Renders JS + can use a proxy but does NOT solve CAPTCHAs / defeat barriers / handle PII (caller's call). `selenium` is a lazy import. `tools/trustpilot` is left untouched. | any JS-render need via `fetchlib` `browser` tier (all opt-in) |

See [tools/README.md](tools/README.md) for standalone usage.

---

### Key Features

- **54 Skills, 13 Chains** — Complete coverage from brand strategy to daily operations to finance & capital to affiliate-program building to EU channel entry to overseas-buyer outbound to earned-media press discovery to pre-purchase Reddit VOC
- **Affiliate & Channel Systems (2026 decks)** — a 2-skill affiliate chain built from the affiliate's own economics (`affiliate-readiness-audit` mirrors CRO — "why affiliates won't promote you"; `affiliate-program-ops` runs the AI recruit→score→outreach→activate loop), plus a US-entity Europe channel-entry strategy (SSPV / RCS / growth flywheel) and a multi-channel price-conflict guard. Framework skeletons only, each crediting its source deck in a methodology index
- **Finance & YMYL Discipline** — the 8-skill finance chain carries explicit "planning aid, not professional tax/legal/accounting advice — verify with a CPA" disclaimers, point-in-time-stamped 2026 regulations, and ⚠️-flagged estimates (no fabricated numbers)
- **Data Verification Layer** — Every skill includes mandatory verification; estimates are explicitly flagged with ⚠️
- **Chart Visualization** — 21 skills auto-generate charts (radar, bar, waterfall, scatter, funnel, etc.) via AntV API
- **Semrush Integration** — Brand strategy skills auto-scan local Semrush xlsx/PDF data as high-confidence source
- **VOC Matrix** — Mention frequency × satisfaction matrix to identify unmet needs
- **GTM Flywheel** — Market → Product → Marketing → Operations four-wheel evaluation
- **AI Search Ready** — Optimized for Amazon Rufus, COSMO knowledge graph, and GEO
- **Multi-Agent Concurrency (Claude Code-native)** — skills like `dsite-conversion-ux` orchestrate parallel recon + analysis subagents via the `Workflow` tool with `StructuredOutput` schemas, run as background tasks, and use browser-class MCP (Claude in Chrome / Preview) for live-site inspection — fan out the work, keep the conclusions
- **Compliant Scraping Stack (2026-benchmarked)** — a free-first, US-compliant fetch pipeline the skills share: `api-pacer` (header-adaptive pacing + full-jitter backoff) → `fetchlib` (Markov waterfall `curl_cffi` → Jina Reader → browser → paid, with an AIMD rate limiter, circuit breaker, and a Thompson-sampling backend selector) → `browser-fetch` (pluggable browser-render L3, Selenium default). Grounded in real benchmarks (`cloudscraper` / `FlareSolverr` are dead; hard Cloudflare / DataDome sites need a residential IP or a paid unblocker, not a fancier library) and it honors robots + rate limits — no access-barrier defeat, IP rotation, CAPTCHA-solving, or PII handling (caller's call under CFAA / hiQ / CCPA-CPRA)
- **Multi-Platform** — Works on Claude Code, Google Antigravity, OpenClaw, and any AI IDE

### Installation

**Claude Code (recommended):**
```bash
git clone https://github.com/noique/cross-border-ecommerce-skills.git

# Single-file skills → ~/.claude/commands/
cp cross-border-ecommerce-skills/brand-strategy/*.md ~/.claude/commands/
cp cross-border-ecommerce-skills/amazon/*.md ~/.claude/commands/
cp cross-border-ecommerce-skills/finance/*.md ~/.claude/commands/

# Multi-file skill packages → ~/.claude/skills/ (one directory per skill)
cp -r cross-border-ecommerce-skills/outbound-prospecting/google-whatsapp-prospecting ~/.claude/skills/
cp -r cross-border-ecommerce-skills/outbound-prospecting/linkedin-prospecting ~/.claude/skills/
cp -r cross-border-ecommerce-skills/outbound-prospecting/media-press-discovery ~/.claude/skills/
cp -r cross-border-ecommerce-skills/voc-tools/reddit-voc ~/.claude/skills/
cp -r cross-border-ecommerce-skills/brand-strategy/serp-content-teardown ~/.claude/skills/
cp -r cross-border-ecommerce-skills/tools/backlink-kol-extractor ~/.claude/skills/
```

**Google Antigravity / OpenClaw / Any AI IDE:**
Copy `.md` files (single-file skills) or whole directories (multi-file packages) into your skill directory.

### Model Requirements

| Tier | Quality | Models (as of April 2026) |
|------|---------|--------------------------|
| Recommended | Full execution, verification works | Claude Opus 4.6 / Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro |
| Usable | Structure OK, may skip verification | DeepSeek V4 / V3.2, Llama 4, Qwen 3.5 (72B+), GLM-5.1 |
| Not recommended | Sections missing, checks fail | Models under 30B parameters |

Key requirements: long context (8K+ input), strong instruction following, Chinese-English bilingual, tool use / web browsing.

---

## 中文说明

### 这是什么？

一套 **54 个跨境电商 AI 技能模板**，覆盖品牌战略→选品→调研→文案→广告→独立站→**财务资金**→**联盟营销**→**欧洲渠道进入**→社媒→红人→线下渠道→海外开发→媒体公关→**购买前 Reddit VOC** 全流程自动化。

两种格式：
- **单文件技能（45 个）** — 一个 `.md` 文件，放入 AI IDE 技能目录即可使用
- **多文件技能包（5 个，分布在 `brand-strategy/`、`outbound-prospecting/` 和 `voc-tools/`）** — `SKILL.md` + `references/` + `templates/`（含 Python 脚本和 CSV 跟踪表），将整个目录指向 AI IDE

外加 **7 个独立工具** 在 `tools/`（Python 工具，被 skill 调用也可独立使用）：`backlink-kol-extractor` / `trustpilot` / `linktree-expander` / `contact-extractor` / `api-pacer` / `fetchlib` / `browser-fetch`。

### 技能矩阵（54 个技能，13 条链路）

| 链路 | 数量 | 技能 |
|------|------|------|
| **品牌战略链** | 10 | 市场扫描 → 赛道假设 → 深度验证 → 品牌战略 → IMC框架 → 年度规划 → 预算管控 → 知识库 → A/B对比 → 图表可视化 |
| **Amazon 运营链** | 14 | 选品 → 筛选 → 调研 → IP排查 → 供应商 → 关键词 → 文案 → 主图 → A+ → 合规 → 复查 → 广告架构 → 周报 → 诊断 |
| **独立站流量** | 5 | SEO 全链路诊断（NEW v3.3）→ SEO全链路规划 → SEM广告 → **转化率优化 CRO（UPGRADED v3.7，多 Agent 并发实站检测：第零步 5 子代理并发侦察 + 6 模块 + 技术追踪健康层 + 文案改写/异议表 + 速赢双桶，Claude Code Workflow 编排）** → SERP 内容拆解（NEW v3.6，竞品文章结构 + 关键词 + 反链 + GEO 一起拆） |
| **财务与资金（NEW v3.8）** | 8 | 落地成本与单位经济(CM1/CM2/CM3) → 收款·结汇·FX 对冲 → 税务合规(Nexus/VAT/IOSS/EPR，含 EU €3 关税与 ~€2 处理费之分) → 13 周现金流预测 → 定价·毛利护栏 → 多渠道对账记账 → 跨境架构与利润回流 → 融资真实成本与风控 |
| **社媒与内容** | 3 | TikTok增长 → YouTube运营 → 内容日历 |
| **VOC 评论分析** | 3 | **Reddit VOC（NEW v3.5，购买前用户洞察 / 4 维度找社区 / 6 类帖子分类 / 黑话词典 / 矩阵定位）** → Trustpilot 快速扫描 → Trustpilot 深度分析（爬虫+情感+LDA+AI 归纳） |
| **红人与用户** | 2 | 红人营销 → 用户生命周期 |
| **GTM 执行** | 1 | 新品上市规划 |
| **线下渠道** | 1 | 美国线下零售 |
| **联盟与合作伙伴（NEW v3.13）** | 2 | **联盟可推性审计**（联盟客视角，`dsite-conversion-ux` CRO 的镜像——审"联盟客为什么不推你"：ROI 账本 + EPC + 三层套利 + 六维评分 + 沉默拒绝红灯）→ **联盟运营流水线（AI）**（数据库→6 类生态找候选→100 分评分→10 来源采集→AI 个性化建联→素材库激活→4 层 KPI→30 天闭环，多 Agent 并发） |
| **渠道与市场进入（NEW v3.13）** | 2 | **欧洲渠道进入战略**（美国主体进欧盟：美/欧市场逻辑 · 定位象限 · SSPV 用户价值 · RCS 区域作战 · 渠道赋能 · 组织三阶段 · 增长飞轮，5 区并发）→ **价格体系与渠道冲突护栏**（DTC+Amazon+分销：跨渠道真实价诊断 · 统一价×促销同步×区域保护三层 · T-60 促销 SOP · 含 MAP/反垄断边界） |
| **海外开发与媒体公关（NEW v3.2 + v3.4）** | 3 | Google→WhatsApp 反查开发 → Google→LinkedIn 反查开发 → **媒体公关发现（NEW v3.4，Muckrack-anchored journalist DB pipeline，5 脚本 + Cloudflare-aware 4 后端 fetcher + 多机分片）** |

### 核心特色

- **54 技能 × 13 链路 + 7 独立工具** — 从战略到执行到财务资金到联盟营销到欧洲渠道进入到海外开发到媒体公关到购买前 Reddit VOC 全覆盖
- **联盟与渠道体系（源自 2026 行业分享）** — 从联盟客的经济账反推的 2 技能联盟链（`affiliate-readiness-audit` 是 CRO 的镜像——审"联盟客为什么不推你"；`affiliate-program-ops` 跑 AI 招募→评分→建联→激活闭环），外加美国主体的欧洲渠道进入战略（SSPV / RCS / 增长飞轮）与多渠道价格冲突护栏。只抽方法论骨架，每个技能在"参考方法论索引"注明来源分享
- **财务链 YMYL 纪律** — 8 个财务技能均带"规划辅助、非专业税务/法律/会计意见、需找 CPA 核实"免责，2026 法规打时间戳，估算标 ⚠️（不编造数字）
- **数据验证层** — 每个技能内置强制验证，推测数据标 ⚠️
- **图表可视化** — 21 个技能自动生成图表（雷达/柱状/瀑布/散点/漏斗等），调用 AntV API
- **Semrush 集成** — 品牌战略技能自动扫描本地 Semrush 数据
- **VOC 用户洞察** — 提及量×满意度二维分析
- **GTM 飞轮** — 市场→产品→营销→运营四维评估
- **AI 搜索适配** — Amazon Rufus / COSMO / GEO 优化
- **多 Agent 并发（Claude Code 原生）** — `dsite-conversion-ux` 等技能用 `Workflow` 工具编排并发侦察+分析子代理（`StructuredOutput` schema），后台任务运行 + 浏览器类 MCP（Claude in Chrome / Preview）做实站检测——把活儿 fan out，只留结论
- **合规抓取栈（2026 实测）** — 各 skill 共享的免费优先、美国合规取页流水线：`api-pacer`（按响应头自适应 + full-jitter 退避）→ `fetchlib`（Markov waterfall：`curl_cffi` → Jina Reader → 浏览器 → 付费；带 AIMD 限速 + 熔断 + Thompson 选后端）→ `browser-fetch`（可插拔浏览器渲染 L3，默认 Selenium）。真实基准落地（`cloudscraper`/`FlareSolverr` 已死；Cloudflare/DataDome 堡垒需住宅 IP 或付费，非换库能解），默认守 robots + 限速——不破壁、不换 IP、不解 CAPTCHA、不碰 PII（CFAA / hiQ / CCPA-CPRA 下由调用方判断）
- **多平台兼容** — Claude Code / Antigravity / OpenClaw / 任何 AI IDE

### 安装方式

```bash
# Claude Code 一键安装
git clone https://github.com/noique/cross-border-ecommerce-skills.git

# 单文件技能 → ~/.claude/commands/
cp cross-border-ecommerce-skills/brand-strategy/*.md ~/.claude/commands/
cp cross-border-ecommerce-skills/amazon/*.md ~/.claude/commands/
cp cross-border-ecommerce-skills/finance/*.md ~/.claude/commands/

# 多文件技能包 → ~/.claude/skills/（每个技能一个目录）
cp -r cross-border-ecommerce-skills/outbound-prospecting/google-whatsapp-prospecting ~/.claude/skills/
cp -r cross-border-ecommerce-skills/outbound-prospecting/linkedin-prospecting ~/.claude/skills/
cp -r cross-border-ecommerce-skills/outbound-prospecting/media-press-discovery ~/.claude/skills/
cp -r cross-border-ecommerce-skills/voc-tools/reddit-voc ~/.claude/skills/
cp -r cross-border-ecommerce-skills/brand-strategy/serp-content-teardown ~/.claude/skills/
cp -r cross-border-ecommerce-skills/tools/backlink-kol-extractor ~/.claude/skills/
```

### 模型要求

| 层级 | 效果 | 代表模型（2026 年 4 月） |
|------|------|------------------------|
| 推荐 | 完整执行，验证步骤生效 | Claude Opus 4.6 / Sonnet 4.6、GPT-5.4、Gemini 3.1 Pro |
| 可用 | 结构完整，可能跳过验证 | DeepSeek V4 / V3.2、Llama 4、Qwen 3.5 (72B+)、GLM-5.1 |
| 不建议 | 章节缺失，检查失效 | 30B 以下参数模型 |

---

## Changelog

### v3.13 (2026-07-04)
- **New chain — Affiliate & Partnership (2 skills)**, built from three 2026 industry decks (each skill credits its source in a `参考方法论索引` table, per repo convention — framework skeletons only, no slide copy):
  - **`affiliate-readiness-audit`** — the **mirror of `dsite-conversion-ux` (CRO)**: audits a product/Listing from the affiliate's wallet POV ("why affiliates won't promote you"). Affiliate ROI ledger + EPC + 3-layer arbitrage, 6-dim recruitability scorecard with score bands, admission buckets, 6 silent-rejection red flags, traffic-catch self-check + 30-day fix roadmap. Source: **Toony** (affiliate-POV audit) × **珂仔 / 跨境品牌说** (scoring model).
  - **`affiliate-program-ops`** — AI-automated affiliate operations pipeline: database → find candidates across 6 affiliate ecosystems → 100-pt AI scoring → standardized contact collection (10 sources) → AI personalized outreach (5-element email) → Partner Resource Hub activation → 4-layer KPI + weekly report → 30-day minimum loop. Multi-agent fan-out per ecosystem; reuses `outbound-prospecting`. Source: **珂仔 / 跨境品牌说** (AI affiliate workflow) × **Toony** (6 ecosystems + economics). Complements `influencer-marketing` (content/relationship lens) without overlap.
- **New chain — Channel & Market Entry (2 skills)**:
  - **`eu-channel-market-entry`** — channel/distributor-driven Europe entry for **US-entity brands**: US-vs-EU market logic, positioning quadrant, **SSPV** user-value model, **RCS** regional-combat model across the 5 EU regions, channel enablement, overseas-org 3 stages, the 8-step growth flywheel. Org/tax hand off to `finance-*`. Source: **Amethyst 同易** (Europe channel growth strategy), reframed China-seller → US-entity.
  - **`price-system-conflict-guard`** — multi-channel price-system & channel-conflict guard (DTC + Amazon + distribution): cross-channel real-price diagnosis, 3-layer mechanism (unified price × promo-sync × regional protection), DTC-vs-channel boundary, T-60 promo SOP, US antitrust (MAP vs RPM) boundary. Source: **Amethyst 同易** (price-system & channel-conflict management).
- All four are Claude Code multi-agent-ready (`Workflow` fan-out + `StructuredOutput` schemas), US-jurisdiction framing, brand-neutral examples.
- Total: **54 skills across 13 chains**; standalone tools: 7 (unchanged).

### v3.12 (2026-06-29)
- **New `tools/browser-fetch/`** — an optional shared **browser-render** backend for `fetchlib`'s **L3**, promoting the "real browser + optional proxy" capability (the kind in `tools/trustpilot`) into one reusable module (pluggable engine, **default Selenium**; `register_engine()` for nodriver / camoufox / scrapling). Drop-in: `fetchlib.register_backend("browser", browser_fetch.as_fetchlib_backend(engine="selenium"))`.
  - **Benchmark-driven, honest scope**: real testing (Selenium + nodriver, from a datacenter IP) showed a browser clears **Trustpilot-class** sites `curl_cffi` can't render (Selenium got real content), but **no free tool — Selenium, nodriver, curl_cffi, Jina — beat Cloudflare Managed Challenge / DataDome (Muckrack, G2, cf-challenge) from a datacenter IP**. The bottleneck there is **IP reputation + Turnstile, not the browser library** → those need a residential IP (+ maybe Camoufox/Scrapling's Turnstile solver) or a paid unblocker. So Selenium is the proven default; other engines are opt-in "validate on a residential IP first."
  - Normalizes a detected challenge page (incl. the Chinese Cloudflare interstitial "请稍候") to `403` so `fetchlib` flags it; `selenium` is a lazy import; self-test is browser-free. Also hardened `fetchlib`'s block-detector with the Chinese + a few more challenge markers.
  - **Compliance (US)**: renders JS + optional proxy, but does NOT solve CAPTCHAs, defeat access barriers, use botnet proxies, or handle PII (caller's call under CFAA / hiQ / CCPA-CPRA). `tools/trustpilot`'s working Selenium is left untouched.
- Total: 50 skills across 11 chains; **standalone tools: 7** (was 6).

### v3.11 (2026-06-29)
- **`fetchlib` batch 2 + `serp-content-teardown` migration** — after a real benchmark of the free tiers against representative targets (Shopify `products.json`, Trustpilot, a Cloudflare JS-challenge, Muckrack, G2, from a datacenter IP):
  - **`serp-content-teardown/fetch_competitors.py` now uses `curl_cffi`** (real-browser TLS/JA3, free, local) with a **graceful fallback to plain `curl`** if it isn't installed — non-breaking, same `fetch_manifest.json` / outputs. The skill's "free + local, no paid APIs" red line is preserved (curl_cffi is a free local libcurl, not an API); no headless browser is added (it stays a deterministic offline analyzer).
  - **`fetchlib` gains a `ThompsonSelector`** (per-domain Beta-Bernoulli bandit, `Fetcher(learn=True, selector_path=…)`) that learns which tier actually succeeds per site and tries the best first — because the benchmark showed the "best backend" is **site- and IP-dependent, not fixed** (e.g. `curl_cffi` matched plain `curl` and 403'd on Trustpilot/Cloudflare/Muckrack/G2 from a datacenter IP, while free **Jina Reader** cleared Trustpilot; the hard JS-challenge sites need `nodriver` + a residential IP or a paid unblocker). Self-test covers the selector.
  - **Honest scope**: `nodriver` (L3) stays a documented `register_backend` plug-in — deferred until tested locally on a residential IP (it won't clear those sites from a datacenter IP either). `tools/trustpilot`'s working Selenium is left untouched per its owner.
- No new skills/tools; counts unchanged (50 skills / 11 chains / 6 tools).

### v3.10 (2026-06-29)
- **New `tools/fetchlib/`** — a compliant fetch **waterfall** for the scraping skills, built from the 2026 dual-source scraping-stack research (multi-agent web research + a Gemini Deep Research report). Escalates one tier only on a real block (Markov-style state machine): **L1 `curl_cffi`** (TLS/JA3 impersonation, free, no JS) → **L2 Jina Reader** (`r.jina.ai` JS→clean-markdown, free\*) → L3 `nodriver` (batch-2 `register_backend` plug-in) → L4 managed unblocker (paid, opt-in).
  - **Control layer**: `api-pacer` (header-adaptive pacing + full-jitter backoff) + **AIMD** (additive-increase / multiplicative-decrease per-domain rate — creep up, cut hard on block) + **circuit breaker** (cool down a target that keeps blocking) + per-fetch JSONL instrumentation.
  - **Grounded conclusions**: `curl_cffi` is the free TLS-impersonation workhorse; `cloudscraper` / `FlareSolverr` / `undetected-chromedriver` / `puppeteer-stealth` are dead/declining vs 2026 WAFs and are NOT used; "human-like" delay distributions (Gaussian etc.) are cargo-cult for read-only research — header-driven pacing + full-jitter backoff is what matters.
  - **Compliance-first / red line**: honors robots.txt; does NOT defeat access barriers, rotate IPs, forge fingerprints, solve CAPTCHAs, or handle PII (caller's duty); use only KYC/consent-audited proxies if any; legitimate rate-limit-respecting RESEARCH use only, NOT ToS-violating automation. Governing law is **US** (CFAA + state) with the hiQ / Meta-v-Bright-Data public-data safe harbor (public + logged-off + no-barrier-defeat + no-PII); GDPR / CCPA-CPRA apply only when collecting EU / California residents' personal data.
  - Stdlib-runnable (`curl_cffi` optional with graceful urllib fallback); **depends on `api-pacer`**. Adoption is opt-in for `serp-content-teardown` / `media-press-discovery` / `trustpilot` / `outbound-prospecting` / `reddit-voc` (their working scrapers unchanged). Batch 2 will add the `nodriver` backend + a Thompson-sampling backend selector.
- Total: 50 skills across 11 chains; **standalone tools: 6** (was 5).

### v3.9 (2026-06-29)
- **New `tools/api-pacer/`** — a shared, dependency-light **request pacer** (adaptive rate-limiting + AWS-style full-jitter backoff) for the scraping / API skills. Paces to the server's own `x-ratelimit-*` headers when present (else a configured RPS budget); full-jitter (uniform) backoff on 429/503/Retry-After; stdlib-only, `requests` optional.
  - **Why it exists** — reads the REAL rate-limit budget instead of guessing a delay from a distribution. A Gaussian/uniform "human-like" sleep is *not* what avoids rate limits/blocks (platforms don't fit-test your delay distribution); the winners are (a) obeying the response-header budget and (b) full-jitter backoff for retries.
  - **Adoption** — `reddit-voc` gets an integration note (`voc-tools/reddit-voc/references/rate-limiting.md`: PRAW + pacer, read-only research framing); `serp-content-teardown` / `media-press-discovery` / `trustpilot` / `outbound-prospecting` are documented as **opt-in** drop-ins (their working scrapers are left unchanged).
  - **Scope / red line** — legitimate rate-limit-respecting research use only; NOT for ToS-violating automation (vote manipulation, spam, sockpuppets, ban evasion). It does not defeat anti-bot, rotate IPs, or forge fingerprints.
- Total: 50 skills across 11 chains; **standalone tools: 5** (was 4).

### v3.8 (2026-06-29)
- **New `finance/` chain — 8 skills (Finance & Capital)** for China→US/EU DTC + Amazon sellers: `finance-landed-cost-unit-economics` (CM1/CM2/CM3 + break-even ROAS), `finance-fx-payout-optimizer` (收款/结汇/FX hedging + SAFE checklist), `finance-tax-nexus-vat-diagnostic` (registration-obligation map + EU €3 duty / IOSS / US nexus / EPR), `finance-cashflow-runway-forecaster` (13-week rolling forecast), `finance-pricing-margin-guard`, `finance-reconciliation-bookkeeping` (clearing-account-to-zero), `finance-entity-structure-advisor` (HK/SG/US LLC + repatriation, YMYL), `finance-capital-stack-advisor` (RBF/MCA true-APR + contract traps).
  - **Dual-source, cross-validated** — built from a multi-agent web-research pass + an independent deep-research report, then merged. Example correction surfaced by the merge: the EU low-value-parcel change is a **fixed €3 customs duty** (Council Reg (EU) 2026/382, applies 2026-07-01, interim to 2028) — DISTINCT from the not-yet-law ~€2 per-consignment handling fee (UCC reform, only provisionally agreed 2026-03-26).
  - **YMYL-first** — every finance skill carries an explicit "operator planning aid, NOT professional tax/legal/accounting/financial advice — verify with a licensed CPA before filing/binding decisions" disclaimer; all rates/thresholds/dates tagged point-in-time; estimates flagged ⚠️ hypotheses; no fabricated seller numbers.
  - **Complements `brand-budget-ops`** (forward budgeting) with the actuals / profitability / tax / cash / financing side; cross-links into Amazon ops + DTC chains.
- Total: **50 skills** across **11 chains** (was 42 / 10). Single-file skills: 45 (was 37).

### v3.7 (2026-06-29)
- **`brand-strategy/dsite-conversion-ux` upgraded** — the CRO skill is rebuilt as a **multi-agent, Claude Code-native live-site audit** (was a single-pass content audit):
  - **Multi-agent concurrency execution architecture** — a new section documents running the skill on Claude Code's `Workflow` tool / subagents: **Step 0** fans out 5 parallel recon agents (PDP / discovery / trust / checkout / competitor) with `StructuredOutput` schemas → `reconPool` → parallel **6-module analysis**; background tasks; browser-class MCP (Claude in Chrome / Preview) for what static `WebFetch` can't see (console / pixel firing / sticky / mobile). Concurrency speeds it up and removes blind spots without changing data truth.
  - **New Step 0 — live-site reconnaissance** — turns the skill from "wait for user-supplied data" into "actually go look first," pinning page-level facts with verbatim evidence before diagnosis.
  - **New §1.6 technical-health & tracking-integrity check** — console errors / GA4-Pixel firing / Core Web Vitals / 404 / mobile-sticky. Broken tracking silently invalidates all downstream A/B + funnel data, so it ranks as a foundation-layer, highest-priority finding (a layer most content-only CRO audits miss).
  - **New mandatory deliverables** — a **copy-rewrite table** (current → A/B), an **objection-handling table** (doubt → current handling → gap → fix), and a **quick-win vs high-impact dual-bucket** triage with wall-clock effort estimates.
  - **A/B stop-rule discipline** — every test now carries sample-size + ≥7-14 days + 95% significance + a stop rule.
  - **Honesty preserved** — keeps the data-credibility statement; lift figures stay ⚠️ hypotheses (no fabricated funnel numbers); adds explicit WebFetch tool-boundary disclosure.
- Skill count unchanged at **42** (upgrade to an existing skill, not a new one).

### v3.6 (2026-05-26)
- **New `brand-strategy/serp-content-teardown/`** multi-file skill (DTC Site & Traffic chain) — deterministic (no-LLM) SERP/content reverse-engineering from local Semrush xlsx + competitor HTML. 8 scripts (`parse_serp` → `fetch_competitors` → `analyze_structure` → `classify_archetypes` → `keyword_analysis` → `backlink_analysis` → `geo_analysis` → `onpage_analysis`) + `run_all` orchestrator + shared `_config` (YAML topic-clusters / JSON brand-names).
  - **Structure teardown**: parses Semrush `serp_urls` → ranked blog/info-article URL pool, fetches the top competitor articles (`curl` + browser UA, `html5lib` to survive Shopify void-tag body-nesting), computes per-article metrics (words, H1/H2/H3, lists, tables, JSON-LD `@type` set, author byline, dates, brand-mentions/1k, authority outlinks), classifies each into **8 article archetypes** (DEFINITION_QA / TUTORIAL_HOWTO / LISTICLE_TIPS / COMPARISON_VS / PILLAR_GUIDE / MYTH_DEBUNK / PRODUCT_MICROGUIDE / NEWS_EDITORIAL) + opening/closing patterns + cross-sample winning bands.
  - **SEO/GEO/keyword/backlink layers**: keyword distribution + core keywords + difficulty-cliff (from `broad-match`); backlink/authority thresholds (Page AS / Ref.Domains / Backlinks) + "weak-link winners"; AI-Overview (GEO) saturation per topic + AI-cited domains + schema readiness of cited vs non-cited; on-page SEO (title/meta/H1/canonical/internal-links/SERP-features).
  - **Output**: JSON artifacts + a per-topic content-strategy report (which archetype / word / H2 / schema / FAQ / opening-closing to use, which keywords to target, what authority is realistically needed, what GEO posture to take). Worked example under `examples/`: waterproof / stainless-steel jewelry niche (25 competitor articles).
  - **Honest scope**: covers the ~20-30% code-side of what wins; content quality + domain age + backlinks are the other ~70-80%. Backlink data is page-level Authority Score, not domain DR. AI-Overview citation capture is sparse. Red line: `curl`-only fetch, no paid APIs, no live AI-citation probing. Pairs with `backlink-kol-extractor` (links) and `structured-data-buildout` (implements the schema this skill measures).
- Total: **42 skills** across 10 chains. Multi-file packages: 5 (was 4).

### v3.5 (2026-05-19)
- **New `voc-tools/reddit-voc/`** multi-file skill — pre-purchase VOC mining from Reddit (complements post-purchase `trustpilot-voc-*`). Methodology:
  - **4-dimension community discovery** — category/brand subs (D1) + lifestyle/demographic subs (D2) + problem/help subs (D3) + values/ideology subs (D4). Single-dimension findings are not credible; cross-dimension validation required.
  - **6-class post taxonomy** with business-action mapping — Recommendation / Rant / Question / Comparison / Daily / Top-All-Time. Each class maps to a primary output (Listing copy / differentiation positioning / FAQ + IPQ / vs-matrix / content calendar / brand positioning) and a secondary output.
  - **Reddit slang dictionary** — BIFL / YMMV / AITA / DAE / TIL / PSA / etc., grouped by VOC signal type (values / emotion intensity / moral-judgement / product-evaluation / community-platform / category-specific). Reading slang wrong = misreading user emotion and values.
  - **3 listing+ad rewrite cases** — "7 pieces to clean" listing rewrite, "earbuds don't fall out" TikTok hook, "never scoop never clean" brand tagline. All sourced from real Reddit high-upvote threads, demonstrating *user-language > marketer-language*.
  - **2D positioning matrix** (functional importance × satisfaction) — find the bottom-right "wants but unmet" quadrant. Includes simplified 30-min version and full 2-3-day data-driven version. Compatible with `tools/trustpilot/` `topic_modeling.py` + `sentiment.py` for auto-labeling at scale.
  - 3 CSV templates: `community-map.csv` (8-15 subs across dimensions) / `post-analysis.csv` (30-80 post teardowns) / `insight-action-map.csv` (insight → action with P0/P1/P2 priority + owner + status).
  - Pairs with: `/trustpilot-voc-deep` (post-purchase), `/amazon-market-research` (post-purchase), `/brand-market-scan` (pre-strategy VOC input), `/amazon-listing-copywriter` (user-language input), `/tiktok-growth` (ad-hook input).
- Total: **41 skills** across 10 chains. Multi-file packages: 4 (was 3).

### v3.4 (2026-05-06)
- **New `outbound-prospecting/media-press-discovery/`** multi-file skill — Muckrack-anchored journalist DB pipeline. 5 scripts (`discover_journalists` / `find_articles` / `guess_emails` / `score_and_export` / `merge_partitions`) + shared `_fetcher.py` with 4 backends (`requests` / `remote-chrome` / `apify` / `html-dir`) for Cloudflare-protected pages. Multi-machine partition-merge workflow.
- **New `tools/linktree-expander/`** — batch-enrich Linktree handles via `__NEXT_DATA__` JSON parsing. Handle-match scoring for `personal_site` + `NON_PERSONAL_HOSTS` blocklist (30+ shorteners / aggregators / docs / scheduling tools). Verified 44/45 ok on a 45-handle pilot.
- **New `tools/contact-extractor/`** — multi-source email extraction with confidence tiering. Sources: `personal_site` `/about` `/contact` `/press` (mailto / text) + YouTube Data API v3 description + Apple Podcasts RSS owner + email pattern guess. Optional `--verify` SMTP MX probe / Hunter.io. Outputs ranked `contact_email_1..3` + `confidence` (high / medium / low / none).
- **`tools/trustpilot/` rebuilt**: modern data-* attribute selectors (replaces 110-line sibling-XPath fallback chain that broke on Trustpilot's 2026 DOM update), desktop-UA pin (Trustpilot serves snippet-only DOM to mobile UAs — major silent failure mode), `?sort=recency` URL flag (relevance widget served snippet-only DOM for some brands), `--cutoff_date YYYY-MM-DD` arg (efficient time-bounded scrapes), `--skip_ai` mode bypasses broken `generate_report()` signature, redacted hardcoded SOCKS5 proxy creds in `config.py` (now env-var loaded).
- Total: **40 skills** across 10 chains. Tools count: 4 (was 1).

### v3.3 (2026-04-27)
- **New entry-orchestrator skill** `dsite-seo-diagnostic` (single-file, under `brand-strategy/`) — for live-site SEO traffic-drop diagnostics + restart roadmap.
  - **7-dimension diagnostic framework**: traffic curve (algorithm-downgrade signature) / keyword loss structure / single-point-failure risk / multilingual-Markets URL pollution / backlink quality (DS distribution + anchor text pathology) / content ROI (HCU-hit detection) / KPI body audit (process-volume vs outcome).
  - **Algorithm-event alignment**: traffic curve auto-aligned with public Google Core / HCU / Spam Update timeline (rolling 24-month window).
  - **Restart roadmap**: 4-phase plan (stop-the-bleeding → cleanse → content rebuild → off-site signals) anchored on the `dsite-seo-playbook` 6-step framework.
  - **Multi-skill orchestration**: chains `xlsx` → `dsite-seo-playbook` → `trustpilot-voc-deep` / `competitors-analysis` / `backlink-kol-extractor` → `report-pdf-export`. Hides internal SKILL refs in deliverable.
  - **Standard PDF deliverable** (A4 landscape, deep-blue header, zebra rows, page-numbered) via `report-pdf-export`.
  - **Use cases**: traffic anomaly investigation, pre-vendor-replacement independent diagnostics, annual SEO health check, post-Core-Update impact assessment, post-migration audit, multilingual / Shopify Markets pollution audit.
- Total: **39 skills** across 10 chains.

### v3.2 (2026-04-26)
- **New Outbound Prospecting chain (2 multi-file skill packages)** under `outbound-prospecting/`:
  - `google-whatsapp-prospecting` — Google-dork → WhatsApp lead pipeline. 4-stage workflow (Search → Validate → Enrich → Outreach). 15+ search formula variants, 30+ countries with mobile-prefix narrowing + B2B platforms + time-zone send windows + compliance flags. Full GDPR / CASL / CCPA / UWG §7 / WhatsApp ToS compliance reference. Multi-language outreach playbook (EN/ES/PT/FR/AR). SerpAPI batch script + `wa.me` validator + lead-tracker CSV.
  - `linkedin-prospecting` — Google + Bing + Yandex + Wayback reverse-search of LinkedIn. Post-2024 Auth Wall workarounds. 50+ decision-maker role keywords localized into 8 languages with company-size-band gating (CEO targeting only valid for ≤500 employees). Enrichment-tool comparison (Apollo / Snov / Hunter / Lusha / Wiza) with cost + accuracy + legal context. LinkedIn ToS § 8.2 + 2026 quota table + account warm-up protocol. 4-touch outreach (Connection Request → DM → Follow-up → Channel-switch) with 12 DM templates across 5 archetypes (incl. voice-note opener), reply-handling matrix, native templates in PT/ES/FR/DE/AR/JA.
- **New format**: multi-file skill packages (SKILL.md + references/ + templates/ with Python helpers + CSV trackers), in addition to existing single-file `.md` skills.
- Total: **38 skills** across 10 chains.

### v3.1 (2026-04-14)
- **New VOC chain (2 skills)**: `/trustpilot-voc-quick` (5-min surface scan) and `/trustpilot-voc-deep` (full pipeline with sentiment analysis, LDA topic modeling, and AI-powered insights)
- **New tools directory**: `tools/trustpilot/` with Python toolkit for deep review analysis
- Total: **36 skills** across 9 chains

### v3.0 (2026-04-13)
- **12 new skills**: annual-plan, budget-ops, gtm-launch, seo-playbook, sem-ads, conversion-ux, tiktok-growth, youtube-ops, influencer-marketing, user-lifecycle-ops, social-content-calendar, offline-retail-us
- **Chart visualization**: 21 skills now auto-generate charts via AntV API (radar, bar, column, pie, waterfall, scatter, line, funnel, sankey)
- **Unified footers**: All 36 skills now include GitHub open source link
- Total: **34 skills** across 8 chains

### v2.1 (2026-04-12)
- Added `/brand-ab-compare` SKILL
- Semrush local data auto-scan in Step 0
- Data gap reporting, minimum depth constraints
- SEO traffic model validation in Round 3
- Auto knowledge base trigger in IMC

### v2.0 (2026-04-11)
- Real-time data collection layer added to 3 brand strategy SKILLs

### v1.0 (2026-04-07)
- Initial release: 6 brand strategy + 14 Amazon skills (20 total)

---

## License

Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).

Free to use, share, and adapt with credit.

## Author

Created by **Alex / 黄子阳** — [ckcm.us](https://ckcm.us)

### Contact / 联系方式

有定制化调研需求、品牌咨询、或技能使用问题，扫码加微信：

<img src="wechat-qr.png" alt="WeChat QR Code" width="200">
