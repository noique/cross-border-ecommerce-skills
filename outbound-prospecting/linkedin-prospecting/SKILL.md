---
name: linkedin-prospecting
description: Find overseas B2B decision-makers via Google/Bing reverse-search of LinkedIn profiles, enrich with email/phone via legitimate SaaS tools, then run a 4-touch outreach sequence (connection request → accepted-DM → follow-up → channel-switch) with reply-rate-tested templates. Use when a foreign-trade / cross-border / DTC seller wants to build a targeted list of buyers, procurement managers, distributors, or CEOs on LinkedIn — without paying LinkedIn Sales Navigator and without burning Connection requests on dead profiles. Sister skill to `google-whatsapp-prospecting`. Trigger phrases include "find LinkedIn buyers", "LinkedIn 反查", "Google 反查 LinkedIn CEO", "外贸 LinkedIn 开发", "LinkedIn 私信模板", "领英开发客户", "LinkedIn DM templates", "find decision makers LinkedIn".
---

# LinkedIn Prospecting

## What this skill produces

A repeatable pipeline that turns one input — `(product, target country, decision-maker role)` — into a **validated, contactable, message-ready list** of LinkedIn decision-makers, complete with the email/phone the article-floor "google → linkedin" trick can't actually deliver:

1. A **search plan** of 8–15 Google + Bing + Wayback dorks adapted to the country's primary LinkedIn profile language and to the role's local title
2. A **profile list** with LinkedIn URL, name, title, company, location, mutual-connection count, post-activity tier
3. An **enrichment file** with email + phone (where legally extractable) via Apollo/Snov/Hunter/Lusha/Wiza
4. A **4-touch outreach sequence** — Connection Request → Accepted DM → Follow-up → Channel-switch — with templates in EN / ES / PT / FR / DE / AR / JA, plus a reply-handling matrix
5. A **compliance pass** — LinkedIn ToS limits + GDPR / CASL / CCPA flags per country

The end state: a junior salesperson can pick up the list and start sending without rewriting messages, and the LinkedIn account doesn't get rate-limited or restricted in week one.

## When to use this skill

- Foreign-trade seller wants to skip LinkedIn Sales Navigator ($99/mo) and still find the same people
- Founder needs 50–200 cold conversations with overseas decision-makers to validate a market
- Agency is building an outbound list of procurement/buying contacts for a manufacturer client
- A previous WhatsApp campaign (`google-whatsapp-prospecting`) is exhausted — switch to LinkedIn channel for the same buyer set

Do NOT use for:
- B2C influencer outreach — see `tools/backlink-kol-extractor` and `brand-strategy/influencer-marketing`
- Recruiting / hiring — different ToS rules apply, different role keywords
- Markets with low LinkedIn penetration — Russia (LI is blocked), China mainland (LI shut down 2021), Iran. Switch to local platforms.

## Required inputs

Refuse to start with vague inputs.

| Input | Format | Example |
|---|---|---|
| Product | Specific noun phrase | "12V LED strip light, IP65, 5050 SMD" — NOT "lighting" |
| Target country | One country at a time | "Brazil, focus São Paulo + RJ" — NOT "LatAm" |
| Decision-maker role | One specific title (or "tier" — exec/buyer/sourcing) | "Procurement Manager at companies with 50–500 employees" — NOT "anyone who buys" |

Optional: target company-size band, industry vertical, language requirement (EN-only vs OK with PT/ES native).

## The four-stage pipeline

Each stage has a dedicated reference. Read it before executing the stage.

### Stage 1 — Search

Build a query plan from `references/search-formulas.md`. The article's single formula
```
site:linkedin.com/in/ "<product>" "<country>" "<role>"
```
is the floor — it now misses 30–60% of profiles because of LinkedIn's 2024 Auth Wall and Google's resulting deindexing. Real campaigns add:

- **Bing + Yandex** mirrors (often have less LI deindexing than Google in 2025–26)
- **Localized role keywords** from `references/role-keywords.md` — "Comprador" for Brazil, "Acheteur" for France, "Einkaufsleiter" for Germany — most countries' LI profiles use the local title
- **Wayback Machine** fallback for profiles Google has dropped: `https://web.archive.org/web/*/linkedin.com/in/*<role-keyword>*`
- **Company-page → people** chain: find target companies first via `site:linkedin.com/company/`, then dork their employees
- **Post-activity targeting** via `linkedin.com/posts/` to find people who posted about the product recently
- **Exclusion** of consultants/freelancers/recruiters who pollute results: `-"open to work" -"consultant" -"recruiter" -"hiring"`

### Stage 2 — Enrich (find email + phone)

Article A vaguely promises "tools to extract emails" — `references/enrichment-tools.md` names them with cost, accuracy, and legal context. The realistic stack:

- **Free tier**: Hunter.io (50/mo), Snov.io (50/mo), Apollo.io (60/mo) — start here for under-50 lists
- **Paid bulk**: Apollo ($49/mo, 12k credits), Lusha ($29 starter, mobile-first), Wiza ($30, LinkedIn-export specialist)
- **Manual fallback**: pattern-guess email from company domain (`firstname.lastname@company.com`) → verify with NeverBounce / ZeroBounce

Tools cost money. The article elides this — set client expectations.

### Stage 3 — Outreach (4 touches)

Use `templates/outreach-playbook.md`. The article gives 7 DM templates, all of one archetype (pain → solution → low-friction CTA). The playbook adds:

- **5 more archetypes** the article missed: mutual-connection intro, replied-to-post warm, recent-news/award reference, reverse-pitch ("we want distributors"), voice-note opener (highest 2026 reply rate)
- **Connection Request template** — completely separate from DM, hard 300-char limit, different psychology
- **Per-language native templates** — not Google Translate
- **Reply-handling matrix** — what to send when they ask price / send catalog / not interested / ghost

Touch cadence:
1. **T0**: Connection Request (≤300 chars)
2. **T1** (24–48h after acceptance): Opening DM using one of 12 archetypes
3. **T2** (5d after T1, no reply): Follow-up
4. **T3** (10d after T2, no reply): Channel switch — pivot to email or WhatsApp using enrichment from Stage 2

Stop after T3. Do not chase further on LinkedIn — your account gets flagged.

### Stage 4 — Compliance + LinkedIn account hygiene

Read `references/linkedin-limits.md` before any campaign >25 connection requests/day. Hard limits in 2026:

- **Connection requests**: ~80–100/week (down from 200/week pre-2024). Exceed → "You're approaching the weekly limit" warning, then 1-week freeze.
- **DM volume**: ~100/day for 1st-degree connections, 0/day for 2nd+ unless you pay InMail credits
- **Automation tools** (Phantombuster, Linked Helper, Dux-Soup, Octopus, Expandi): all violate LinkedIn ToS § 8.2. Account ban is the standard outcome — even "throttled" tools eventually get caught.
- **Country regulation**: same GDPR / CASL / CCPA / UWG §7 as `google-whatsapp-prospecting` — LinkedIn DM is "commercial electronic message" under most regimes

Recommended account hygiene:
- One personal LinkedIn per active outbound campaign
- Warm the account for 2 weeks (post 1×/week, comment 3×/week, accept inbound) before high-volume outbound
- Never send the same message text >5 times — LI similarity-detects across accounts

## Workflow (end-to-end)

1. Confirm the three required inputs. Refuse to proceed if vague.
2. Open `references/role-keywords.md`, get the localized role list for the target country.
3. Open `references/search-formulas.md`, build 8–15 queries combining: localized role + product + country + Google/Bing/Wayback + exclusions.
4. Execute searches manually or via SerpAPI batch (reuse `templates/serpapi-batch.py` from `google-whatsapp-prospecting/templates/`). Dedupe LinkedIn URLs.
5. For each LI URL, capture: name, current title, company, city, mutual connections (if visible without login), post-activity tier (last 30d).
6. Run the URL list through Apollo / Snov / Hunter — see `references/enrichment-tools.md` for picking the right tool by region. Get email + (where available) mobile.
7. Score each lead (`templates/lead-tracker.csv`'s priority column): mutual connections (×3), post-activity (×2), title match (×2), company size match (×2).
8. Write Connection Requests for top 80 leads/week using `templates/outreach-playbook.md`.
9. After acceptance (T1): pick the right DM archetype based on what you saw on their profile. Personalize the merge fields. Send only inside their local 09:00–17:00.
10. Track in CSV. Run T2 follow-up at 5d. Run T3 channel-switch at 10d (use email from Stage 2, or WhatsApp number if surfaced).
11. After T3, archive. Do not chase further on LinkedIn.

## Common failure modes

- **Using English role titles in non-English markets**: searching `"Purchasing Manager" "Brazil"` returns ~25% of the BR procurement population that lists their title in English. Always include the local term (Portuguese: "Gerente de Compras" / "Comprador").
- **Hunting CEOs of large enterprises**: in companies with 1000+ employees, the CEO never signs purchase orders. Filter to small/mid companies (10–500 employees) when targeting CEO/Owner; for enterprise, target Procurement/Sourcing director.
- **Connection request opens with "Hi, hope you're doing well"**: 300 chars are precious. Cut all pleasantries, lead with the specific reason in 1 sentence.
- **Sending 7 identical templates from the article**: LinkedIn's similarity detection flags pattern-blast accounts. Use the templates as scaffolds, rewrite the verb and the example each send.
- **"Free gift / send link" hook in T1**: triggers LI's auto-spam classifier. Defer the link to T2 after they reply.
- **Skipping enrichment**: 30% of leads will ghost on LI but reply on email. Without an email column you can't do the T3 channel-switch.
- **Running 200+ connection requests/day via Phantombuster**: account gets restricted in 7–14 days. Worth it only if you're OK losing the account.
- **Sending DM at 3am buyer-local time**: same time-zone issue as WhatsApp prospecting; cross-reference `google-whatsapp-prospecting/references/country-targeting.md` for send windows.

## Source-article gap analysis (2026-04-26)

Source articles built from:
- "开发信没邮箱？一键复制这个Google公式，精准反查LinkedIn海外买家CEO！" (慧进AI工具说)
- "建议马上收藏！外贸老鸟都在悄悄用的7个LinkedIn高回复私信模板" (慧进AI工具说)

| Article topic | Article said | This skill adds |
|---|---|---|
| Google reverse-search | 1 formula | 8+ formula variants + Bing/Yandex + Wayback + company-page chain + post-targeting |
| Role keywords | 10 English titles | 50+ titles localized into 8 languages with regional variants |
| CEO targeting | "Find the CEO" | Company-size band gating: CEO only for ≤500 employees; >500 = Procurement/Sourcing Director |
| Tool mention | "Use specialized tools" | Named comparison of 6 enrichment tools with cost, accuracy, legal context |
| LinkedIn ToS | Not mentioned | Full quota / automation risk / account hygiene reference |
| DM templates | 7 same-archetype | 12 templates across 5 archetypes; plus separate Connection Request templates |
| Localization | English only | Native templates for ES / PT / FR / DE / AR / JA |
| Follow-up | None | T2 + T3 sequence with channel-switch logic |
| Reply handling | None | 7-row response matrix |
| Voice notes | Not mentioned | Voice-note opener template (2026 highest reply-rate format) |

## See also

- `references/search-formulas.md` — Google + Bing + Wayback + company-chain dorks for LI
- `references/role-keywords.md` — 50+ decision-maker titles in 8 languages, by company-size band
- `references/enrichment-tools.md` — Apollo/Snov/Hunter/Lusha/Wiza comparison + free fallback patterns
- `references/linkedin-limits.md` — quota table + ToS § 8.2 (automation ban) + account warm-up protocol
- `templates/outreach-playbook.md` — Connection Request + 12 DM templates + T2/T3 sequence + reply matrix
- `templates/lead-tracker.csv` — CRM with priority scoring
- Sister skill: `../google-whatsapp-prospecting/` — same 4-stage shape but channel = WhatsApp; share the SerpAPI script
