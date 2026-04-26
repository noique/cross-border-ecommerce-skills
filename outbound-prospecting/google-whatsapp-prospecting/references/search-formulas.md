# Search Formulas — Full Dork Library

The original article gave 3 formulas. This file gives 15+, grouped by intent. Pick 6–12 per campaign; do not run all of them.

Notation: `<product>` = your product noun phrase; `<cc>` = country code (`+91`); `<mp>` = mobile-prefix-narrowed code (`"+91 9*"`); `<lang>` = English buyer-type word in the local market language.

---

## Intent A — Quick lead floor (use first to gauge market depth)

### A1. Direct extract
```
<product> WhatsApp <cc>
```
Example: `LED strip 5050 WhatsApp +91`
Use: 50–500 results, mixed quality. Run first to estimate corpus size before going deeper.

### A2. Mobile-prefix tightened (this is the **fix** for A1's noise)
```
<product> "WhatsApp" <mp>
```
Example: `LED strip 5050 "WhatsApp" "+91 9"` (Indian mobile starts with 6/7/8/9; landlines don't)
Use: cuts ~40% of landline noise from A1.

### A3. Phrase-form variants (catches different page conventions)
```
<product> ("WhatsApp:" OR "WA:" OR "Whatsapp Number" OR "WhatsApp Business") <cc>
```
Use: Indian / SE Asian sites use "WA:" or "Whatsapp Number" prefix. Add to A2 to widen recall.

---

## Intent B — Decision-maker (LinkedIn / Facebook bios)

### B1. LinkedIn person + role
```
site:linkedin.com/in <product> <buyer-role> WhatsApp <cc>
```
Example: `site:linkedin.com/in LED distributor WhatsApp +1`
Note `linkedin.com/in` (not full domain) restricts to **personal profiles**, skipping company pages.

### B2. LinkedIn company page (importer companies, not people)
```
site:linkedin.com/company <product> importer <country>
```
Use: gives you company → then dork the company website for `intitle:"contact" "WhatsApp"`

### B3. Facebook page
```
site:facebook.com <product> <buyer-role> WhatsApp <cc>
```
Use: BR / MX / MENA / Indonesia — Facebook Business pages publish WhatsApp openly.

### B4. Instagram bio
```
site:instagram.com <product> <buyer-role> "+<cc>"
```
Use: smaller buyers / wholesalers / boutiques in fashion, beauty, F&B verticals. The phone in IG bios is almost always WhatsApp.

### B5. X / Twitter bio
```
site:x.com <product> <buyer-role> WhatsApp
site:twitter.com <product> <buyer-role> WhatsApp
```
Use: niche tech B2B (rare but high-quality when found).

---

## Intent C — High-quality buyer with own website

### C1. Contact page intercept (the article's "intitle:contact us")
```
intitle:"contact us" "WhatsApp" <product>
```
Improvement on the article: add country-language variants of "contact us":
- ES: `intitle:"contacto" "WhatsApp"` (LatAm, ES)
- PT: `intitle:"contato" "WhatsApp"` (BR)
- DE: `intitle:"kontakt" "WhatsApp"` (DE/AT/CH)
- FR: `intitle:"contactez-nous" "WhatsApp"` (FR/BE)
- AR: `intitle:"اتصل بنا" "WhatsApp"` (MENA)

### C2. URL-based contact intercept
```
inurl:contact "WhatsApp" <product> <cc>
inurl:contact-us "WhatsApp" <product>
inurl:about "WhatsApp" <product>
```
Use: catches sites where "Contact Us" is in the URL slug but not the title.

### C3. PDF catalog / price list with WhatsApp
```
filetype:pdf "WhatsApp" <product> "<country>"
filetype:pdf "<product>" "price list" WhatsApp
```
Use: importers and large distributors publish PDF catalogs. The WhatsApp number on a PDF is the buyer/sales contact, often a decision-maker.

### C4. XLS/CSV supplier-buyer lists (rare but golden)
```
filetype:xls "WhatsApp" <product>
filetype:xlsx "buyer" OR "importer" <product>
```
Use: trade associations and chambers of commerce sometimes leak member lists. When you find one, the whole sheet is a campaign.

---

## Intent D — Regional B2B platforms (alternative to Alibaba)

The article missed this entire category. Pick the platforms that match the country (full list in `country-targeting.md`).

### D1. India
```
site:tradeindia.com <product> WhatsApp
site:exportersindia.com <product> WhatsApp
site:indiamart.com <product> "+91 9"     # filter to mobile only
```

### D2. Europe
```
site:europages.com <product> WhatsApp
site:wlw.de <product> WhatsApp           # DACH
site:kompass.com <product> contact
```

### D3. MENA
```
site:tradekey.com <product> WhatsApp
site:dubaiyellowpagesonline.com <product> WhatsApp
```

### D4. SE Asia
```
site:globalsources.com <product> WhatsApp
site:tradevietnam.com <product> WhatsApp
```

### D5. LatAm
```
site:mercadolibre.com.ar <product> WhatsApp     # B2B sellers on retail platform
site:cylex.com.br <product> WhatsApp            # BR business directory
```

---

## Intent E — Cached / archived (catch removed contact pages)

### E1. Google cache
```
cache:<exact-url-found-in-A1>
```
Use: when a contact page that surfaced in A1 has been updated and removed the WhatsApp number — check cache for the older version.

### E2. Wayback Machine (manual)
Wayback URL: `https://web.archive.org/web/*/<domain>/contact*`
Use: same purpose, more reliable. Often turns up 2-year-old WhatsApp numbers that are still active.

---

## Intent F — Exclusion masters (clean up D's noise)

These never run alone — they're suffixes appended to A/B/C/D queries.

### F1. Exclude major distributor noise
```
... -alibaba.com -aliexpress.com -indiamart.com -tradeindia.com -made-in-china.com
```
Use when you specifically want **non-platform** (own-website) buyers.

### F2. Exclude job postings (HR pages dilute Linkedin searches)
```
... -"job description" -"we are hiring" -"apply now"
```

### F3. Exclude consumer review sites
```
... -trustpilot.com -reviews -"customer reviews"
```

### F4. Exclude China-mainland suppliers (when you ARE the supplier and want buyers)
```
... -site:cn -"china manufacturer" -"oem factory"
```

---

## Operator cheat sheet (Google-supported as of 2026)

| Operator | What it does | Example |
|---|---|---|
| `"x"` | Exact phrase | `"WhatsApp Business"` |
| `site:` | Restrict to domain | `site:linkedin.com/in` |
| `inurl:` | Word in URL | `inurl:contact` |
| `intitle:` | Word in `<title>` | `intitle:"price list"` |
| `filetype:` | File extension | `filetype:pdf` |
| `OR` (caps) | Either of two terms | `"WhatsApp" OR "WA"` |
| `-` | Exclude | `-alibaba.com` |
| `*` | Wildcard (one or more words) | `"WhatsApp:" * "+49"` |
| `..` | Numeric range | `2022..2026 catalog` |
| `cache:` | Google's cached copy | `cache:example.com/contact` |

Operators NOT to bother with: `link:` (deprecated), `info:` (removed), `+` for forced inclusion (removed in 2011 — use `""` instead).

## How to combine — real campaign skeleton

For "12V LED strip 5050 → India distributors":

1. A2: `LED strip 5050 "WhatsApp" "+91 9"` — floor
2. A3: `LED strip 5050 ("WhatsApp:" OR "WA:") "+91"` — recall widen
3. B1: `site:linkedin.com/in LED distributor WhatsApp "+91"` — decision-makers
4. C1: `intitle:"contact us" "WhatsApp" LED strip India` — own-website
5. C3: `filetype:pdf "WhatsApp" "LED strip" "India"` — catalog buyers
6. D1: `site:tradeindia.com "LED strip 5050" "+91 9"` — platform-listed
7. F1 suffix on 1, 3, 4: `-alibaba.com -indiamart.com -aliexpress.com`

Expect ~150–400 raw URLs from this set. After dedupe + WA validation: 40–120 actionable leads.
