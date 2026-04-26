---
name: google-whatsapp-prospecting
description: Find B2B buyers' WhatsApp contacts at scale by Google-dorking product + region + WhatsApp signals, then validate, enrich, and run a compliant cold outreach sequence. Use when a foreign-trade / cross-border / DTC seller wants to build a targeted outbound list of importers, distributors, wholesalers, or end-buyers reachable on WhatsApp — without relying on paid B2B databases (Alibaba, IndiaMART, Kompass). Trigger phrases include "find WhatsApp leads", "Google reverse-lookup WhatsApp", "外贸 WhatsApp 开发客户", "Google 反查 WhatsApp", "外贸找客户公式", "海外采购商 WhatsApp", "拓客 WhatsApp 群发".
---

# Google → WhatsApp Prospecting

## What this skill produces

A repeatable pipeline that turns one input — `(product, target country, buyer type)` — into a **validated, compliance-checked, ready-to-message list** of overseas buyers on WhatsApp:

1. A **search plan** of 6–12 Google dork queries tuned to the country's mobile prefixes and locally-popular B2B platforms
2. A **lead sheet** (CSV) with extracted WhatsApp numbers, source URL, company, role/buyer-type, country, language
3. An **outreach plan** — first message in the buyer's language, follow-up cadence, time-zone send window, and a specific compliance flag for that region

The final test: hand the lead sheet to a junior salesperson; they should be able to send the first message without rewriting anything, and not get the WhatsApp number banned in the first week.

## When to use this skill

- A 1688/Shopify/Amazon seller wants to add an outbound channel beyond paid ads and Alibaba
- An agency is building a country-specific outbound campaign for a manufacturer client
- A founder wants to validate a new export market with 50–200 cold WhatsApp conversations before committing to inventory
- An existing list has gone cold and needs to be refreshed with new buyers

Do NOT use for:
- B2C consumer prospecting (DM scraping from IG/TikTok bios) — that's a different skill (`backlink-kol-extractor` for KOLs, not relevant here)
- Markets with hard WhatsApp-ban rules (China mainland, parts of MENA where it's blocked) — switch to WeChat / LINE / Telegram pipeline instead
- Regulated industries where cold WhatsApp is illegal regardless of message content (healthcare in EU, financial advisory in most markets)

## Required inputs

Confirm all three before starting. Refuse to proceed if any are missing — the skill produces garbage with vague inputs.

| Input | Format | Example |
|-------|--------|---------|
| Product | Specific noun, not category | "12V LED strip light, IP65, 5050 SMD" — NOT "lighting" |
| Target country | One country at a time, with regional sub-area if huge | "India, focus Mumbai/Delhi" — NOT "Asia" |
| Buyer type | Importer / distributor / wholesaler / installer / end-user | "distributor with own retail brand" — NOT "buyer" |

Optional but recommended: target volume (low-volume retailer vs container-load importer), price band, and any 3 competitor brand names (used as exclusion filters).

## The four-stage pipeline

Each stage has its own reference. Always read the reference before executing.

### Stage 1 — Search
Build a query plan from `references/search-formulas.md`. The original 3-formula playbook (direct / site: / intitle:"contact us") is the floor, not the ceiling. A real campaign uses 6–12 queries combining:
- Mobile-prefix-targeted phone patterns (not just `+91` — use `"+91 9*"` for Indian mobile)
- Platform-specific `site:` operators per region (`site:tradeindia.com` for India, `site:europages.com` for EU)
- File-type dorks (`filetype:pdf "WhatsApp" "supplier"`)
- Exclusion of competitor noise (`-alibaba.com -aliexpress.com -indiamart.com` when looking past Alibaba)
- Wildcards for flexible phone formats (`"WhatsApp:" * "+49"`)

Also pick the right execution mode:
- **Manual** (≤30 queries, one-off): use Google directly with VPN per country
- **Semi-auto** (30–300): SerpAPI / ScraperAPI one-shot script in `templates/serpapi-batch.py`
- **High-volume** (300+): rotate IPs, throttle to 1 req/3s, expect ~5% CAPTCHA loss

### Stage 2 — Extract & validate

Run results through a number-extraction regex (provided in `templates/extract-numbers.py`) and dedupe. Then validate:

- **Format check**: number matches E.164 for the claimed country code
- **WhatsApp existence check**: open `https://wa.me/<number>` — if it shows "Phone number shared via url is invalid" the number isn't on WhatsApp
- **Business vs personal**: WhatsApp Business accounts show a "Business" badge — flag in lead sheet (these are higher-intent)

Discard ~30–60% of raw extractions. This is normal; the article's "存进通讯录直接开聊" understates the noise.

### Stage 3 — Enrich

For every surviving number, capture from the source page:
- Company name + website
- Role / job title (if from LinkedIn) or buyer type (if from B2B platform)
- Country + city (used for time-zone send window)
- Primary business language (drives outreach script choice)

If the source is a personal LinkedIn profile, cross-check on the company website that the person actually still works there — LinkedIn profiles get stale.

### Stage 4 — Outreach

Use `templates/outreach-playbook.md`. Hard rules:
- **First message ≤ 2 sentences, in the buyer's primary language, no product brochure, no link**
- Reference where you found them ("Saw your contact on tradeindia.com under LED distributors") — establishes you're not a random bot
- Ask one specific question that requires a one-line answer
- Follow up at 48h / 5d / 14d, then archive
- Send only during the buyer's local 09:00–17:00 — `references/country-targeting.md` has the time-zone column

## Compliance checklist (mandatory)

Before sending the first message, run through `references/compliance.md` for the target country. Hard stops:

- **EU + UK**: GDPR Art. 6 lawful basis required. Cold WhatsApp B2B is *generally* defensible under "legitimate interest" if you (a) clearly identify yourself, (b) offer an opt-out in message 1, (c) don't message consumers. Get this wrong and fines start at €20M / 4% revenue.
- **Canada**: CASL applies. WhatsApp counts as "commercial electronic message". Need express or implied consent. Implied consent expires 6 months after last business interaction.
- **Germany specifically**: UWG §7 — even B2B cold messaging is restricted. Consider abandoning the country or routing via in-country reseller instead.
- **WhatsApp Terms of Service**: bulk messaging from a personal number gets the number banned in 24–72h once recipients hit "Block" 3+ times. Use **WhatsApp Business API** (via Meta or a BSP) for any campaign >50 messages/day.
- **California (CCPA/CPRA)**: similar to GDPR for any contact identifiable as Californian. Use IP/state inference at extraction time and route them to email instead.

If the compliance answer is "this country is too risky", tell the user explicitly and suggest the alternative channel (email outreach with double opt-in, partner reseller, paid ad funnel).

## Workflow (end-to-end)

1. Confirm the three required inputs. Refuse to start if vague.
2. Open `references/country-targeting.md`, find the country block. Note: mobile prefix, regional B2B platforms, primary language(s), time-zone, and compliance flag.
3. Open `references/search-formulas.md`. Build 6–12 queries adapted to the country block from step 2. Write them to a query plan in `templates/lead-tracker.csv`'s "queries" sheet.
4. Execute (manual / SerpAPI / scraper, depending on volume).
5. Extract numbers with regex, dedupe, validate against wa.me, classify as Business/Personal.
6. Enrich each row with company / role / language / city.
7. Open `templates/outreach-playbook.md`, pick the first-message template that matches the buyer type and write the personalized message per row.
8. Verify the compliance checklist for the country. If a hard stop fires, route those rows to email instead.
9. Schedule sends inside the buyer's 09:00–17:00 local window. Cap to 50/day per WhatsApp number.
10. Log replies in the tracker. Re-engage non-replies at 48h / 5d / 14d.

## Common failure modes

- **Searching "+91" alone** returns landline-heavy results from Indian directory sites. Use `"+91 9*"` or `"+91 8*"`. (Same logic per country in `references/country-targeting.md`.)
- **Extracting numbers without the country code prefix** — they all collide on dedupe. Always store in E.164 (`+919876543210`).
- **Translating the first message via Google Translate** — comes across as a bot in markets that read English fine (NL/DK/SE) and as broken in markets that don't (BR/MX/JP). Use a native template, not a translation.
- **Same WhatsApp number for 200+ daily sends** — guaranteed ban. Either rotate numbers or move to BSP/API.
- **Skipping the validation step** — sales team wastes hours on numbers that aren't on WhatsApp at all.
- **Ignoring the time-zone column** — messaging Brazil at 3am Brasilia time is the fastest way to get blocked.

## See also

- `references/search-formulas.md` — the full dork library (15+ patterns), grouped by intent
- `references/country-targeting.md` — 30+ countries with mobile prefixes, regional B2B platforms, time-zone, language, compliance flag
- `references/compliance.md` — region-specific legal checklist + WhatsApp ToS risk matrix
- `templates/outreach-playbook.md` — first-message + 3-touch follow-up scripts per buyer type, in EN / ES / PT / DE / FR / AR
- `templates/lead-tracker.csv` — CRM sheet structure
- `templates/serpapi-batch.py` — SerpAPI script for 30–300 query batches
- `templates/extract-numbers.py` — regex + wa.me validator for raw HTML/text dumps
