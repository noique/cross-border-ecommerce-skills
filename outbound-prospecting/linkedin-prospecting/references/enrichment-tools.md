# Enrichment Tools — From LinkedIn URL to Email/Phone

The article said "use specialized tools to extract emails" and stopped there. This file names the tools, compares cost / accuracy / region / legal exposure, and gives a free-tier fallback.

---

## What "enrichment" means

Input: a LinkedIn profile URL
Output: that person's business email + (sometimes) mobile phone

The tool either:
- Looks the URL up in a contact database it has scraped/built (Apollo, Lusha, Hunter)
- Or pattern-guesses from the company domain and verifies (firstname.lastname@domain → SMTP ping)

No tool is 100%. Expect 50–75% email-find rate, 15–30% mobile-find rate, varying by region and company size.

---

## Tool comparison (2026)

| Tool | Free tier | Paid entry | Best for | Email accuracy | Phone | Region strength | Legal posture |
|---|---|---|---|---|---|---|---|
| **Apollo.io** | 60 credits/mo | $49/mo (12k credits) | Largest combined DB; LinkedIn Chrome ext | High (~75%) | Yes (US-strong) | US > EU > APAC | Compliant — opt-out honoured |
| **Hunter.io** | 50 searches/mo | $49/mo (500 searches) | Domain-pattern email finder | High for `firstname.lastname@` patterns | No | Global | Compliant |
| **Snov.io** | 50/mo | $39/mo (1000 credits) | Bulk LinkedIn Chrome ext | Medium (~65%) | Limited | EU/UK strong | Compliant |
| **Lusha** | 50 contacts/mo | $29 starter | Mobile phone numbers (US-best) | Medium-high | Yes — its specialty | US > UK > EU | Faces GDPR scrutiny — opt-out compliance debated |
| **Wiza** | 20 free | $30/mo (300 credits) | LinkedIn search → CSV export pipeline | High | Yes | US/EN-speaking | Compliant |
| **GetProspect** | 100/mo | $49/mo (1000 leads) | LinkedIn → email pipeline | Medium (~60%) | No | EU/global | Compliant |
| **Skrapp** | 150/mo | $49/mo (1000) | Domain pattern + LinkedIn | Medium | No | Global | Compliant |
| **NeverBounce / ZeroBounce** | 100 verifications | Pay-per-use ($0.008/verify) | Verify a guessed email actually exists | n/a — verifier | n/a | Global | Compliant |

---

## Recommended stack by use case

### "I'm just testing — under 50 leads"
1. Hunter.io free (50 searches): get email patterns for top 5 companies
2. Apollo free (60 credits): pull contact data for top 60 LinkedIn URLs
3. NeverBounce (free 100 verifications): verify the guessed emails

Cost: $0. Time: 1–2 hours. Yield: ~30–40 verified emails.

### "Real campaign — 200–500 leads/month, US/EU"
- **Primary**: Apollo $49/mo
- **Secondary** (for mobile): Lusha $29/mo
- Total: $78/mo. Yield: ~300 emails + ~80 mobile numbers monthly.

### "Real campaign — APAC focus (India / SEA)"
- Apollo's APAC database is weaker. Use:
- **Primary**: Lusha $29 (better APAC coverage than Apollo for mobile)
- **Plus**: pattern-guess via Hunter ($49) — most APAC SMEs use predictable email patterns
- Plus manual: 2024-26 APAC business directories (IndiaMART, Tradevietnam) often list emails directly

### "EU compliance-strict (Germany / France)"
- Use Hunter (domain-pattern only, no DB lookup) — least exposure to GDPR Art. 14 challenges
- Get verbal/written permission before adding to a sequence
- Avoid Lusha for EU due to GDPR enforcement risk (CNIL/DPC have flagged similar tools)

---

## The free fallback: pattern-guess + verify

If you don't want to pay anything, this works for ~50% of leads:

### Step 1 — Find the domain
The person's LinkedIn says they work at "Acme Lighting Pvt Ltd". Google `"Acme Lighting" site:.in` to find the website. Or use Hunter's domain finder.

### Step 2 — Get the email pattern
For 5 known employees of that company (ex-colleagues posted on LinkedIn, "Contact" page, AngelList), see what their emails look like. Common patterns:

- `firstname.lastname@domain.com` — most common globally
- `firstinitial.lastname@domain.com` — common in tech
- `firstname@domain.com` — startups, small businesses
- `firstname_lastname@domain.com` — Indian companies often
- `lastname.firstname@domain.com` — German/Japanese companies sometimes
- `flastname@domain.com` — US legacy

### Step 3 — Generate candidates
For "Rajesh Kumar at acmelighting.in":
```
rajesh.kumar@acmelighting.in
rajesh@acmelighting.in
r.kumar@acmelighting.in
rkumar@acmelighting.in
rajesh_kumar@acmelighting.in
kumar.rajesh@acmelighting.in
```

### Step 4 — Verify with NeverBounce / ZeroBounce
Free 100 checks/mo. Tells you which addresses bounce (don't exist) vs accept-all. Use the surviving address(es).

⚠️ Don't send to "accept-all" servers without warming the email — they can mark you as spam permanently.

---

## What about WhatsApp / phone?

`google-whatsapp-prospecting` (sister skill) covers WhatsApp number discovery via Google dorking. Run it in parallel for the same lead set:

1. From LinkedIn enrichment: get email + maybe mobile
2. From Google dorking: get WhatsApp from company website / B2B platforms
3. Merge into one lead row → 3 channels available for T3 channel-switch

Some tools combine: Apollo lists mobile when available, Lusha is mobile-specialist.

---

## Browser-extension automation — the high-risk path

Tools like **Phantombuster, Linked Helper, Dux-Soup, Octopus CRM, Expandi, Lemlist's LinkedIn module** offer "scrape LinkedIn search results → enrich → DM" in one click.

### Why it's tempting
1 person can run 200–500 LinkedIn touches/day "automatically".

### Why it's risky
- **All violate LinkedIn ToS § 8.2** (User Agreement, "Dos and Don'ts" — no automation, no scraping)
- Account ban rate: ~30–60% within 6 months of regular use
- Banned accounts can't be re-created with the same identity (LI tracks device fingerprint + ID verification)
- Some markets (DE under UWG, EU under GDPR) make the *automated mass DMing* itself illegal regardless of LI ToS

### When it's defensible (rare)
- You're an agency burning client accounts (not your own) and you're explicit about the risk
- You're outreach to your existing customer base only (fine)
- You operate in a market with no enforcement and accept the LI risk

### Default recommendation
Don't use them. Use enrichment tools (which are LinkedIn-data lookups, not automation) for the data layer. Send DMs manually. 100/day manual is plenty if your targeting is good.

---

## Compliance fast-reference for enriched data

| Region | Legal requirement |
|---|---|
| EU/UK | Email is personal data → GDPR Art. 14 says you must inform the data subject of the source within 30 days. Practical: include "I found your contact via LinkedIn" in T1 — that doubles as notice. |
| Canada | CASL needs implied consent. "Contact info conspicuously published in business context" (LinkedIn) supports implied consent for **role-relevant** outreach only. |
| USA | TCPA mainly for SMS — email less restricted but CAN-SPAM requires unsubscribe link in commercial email. |
| Brazil | LGPD — same notice requirement as GDPR. |
| Other | See `google-whatsapp-prospecting/references/compliance.md` country flags. |

---

## What never to do with enriched data

- Sell or share the list with third parties (instant GDPR violation, triggers fines)
- Upload to a "warm-up" service that mass-mails on your behalf
- Use the email for marketing automation without the unsubscribe link
- Re-run enrichment on the same person every month — the data doesn't change that fast and it triples your tool costs
- Cross-reference with paid PII databases (people-finder sites) to enrich personal info beyond business contact — that's where GDPR fines escalate
