# Search Formulas — Google + Bing + Wayback for LinkedIn

The source article gave one formula. This file gives 8+ patterns across 3 search engines plus a fallback for profiles LinkedIn has hidden behind its 2024 Auth Wall.

Notation: `<product>` = your product noun phrase; `<country>` = country in English; `<role>` = decision-maker title in **the buyer's local language** (use `role-keywords.md`); `<role_en>` = same in English fallback.

---

## Why the article's single formula misses 30–60% of profiles in 2026

LinkedIn rolled out the Auth Wall in waves through 2024–25. Effects on Google indexing:

1. Profiles set to "limit visibility" no longer get indexed — Google returns the LI sign-in page instead of the profile
2. Profile description text is truncated in indexed snippets
3. New profiles created post-Auth-Wall are sometimes never indexed at all
4. Job-title keywords in the profile body (vs the headline) are no longer reliably searchable

Workarounds (used in formulas below):
- Use **Bing** — slightly less aggressive crawl restrictions on LI
- Use **Yandex** — different crawl agreement, often indexes LI profiles Google has dropped
- Use **Wayback Machine** for archived pre-Auth-Wall versions
- Search via **company pages** (`linkedin.com/company/`) which remain mostly indexed, then enumerate employees

---

## Intent A — Direct profile lookup

### A1. Article's original formula (use as floor)
```
site:linkedin.com/in/ "<product>" "<country>" "<role_en>"
```
Example: `site:linkedin.com/in/ "LED lighting" "Brazil" "Purchasing Manager"`
Note: this is the article's exact formula. Run it first to gauge floor.

### A2. Localized role (the **fix** for A1's miss-rate)
```
site:linkedin.com/in/ "<product>" "<country>" "<role>"
```
Example: `site:linkedin.com/in/ "LED" "São Paulo" "Gerente de Compras"`
Note: For non-English markets this is usually the better starter, not A1. See `role-keywords.md`.

### A3. Both languages (widest recall)
```
site:linkedin.com/in/ "<product>" "<country>" ("<role>" OR "<role_en>")
```

### A4. Bing mirror (no `site:` quirks; Bing tolerates `inurl:` better)
```
inurl:linkedin.com/in "<product>" "<country>" "<role>"
```
Run on bing.com and on yandex.com — different result sets.

---

## Intent B — Company-page → employees

When direct profile search returns sparse results (small market, tight role), pivot via company pages.

### B1. Find target companies
```
site:linkedin.com/company/ "<product>" "<country>"
```
Example: `site:linkedin.com/company/ "LED" "Brazil"`
Yields company LI pages that are mostly still well-indexed.

### B2. Then enumerate employees of each company
On the LI company page, the "People" tab lists current employees with role filters. Use it logged-in. For non-logged enumeration:
```
site:linkedin.com/in/ "Currently works at <Company Name>" "<role>"
```
or
```
site:linkedin.com/in/ "<Company Name>" "<role>"
```

### B3. Hierarchical: parent company → subsidiary buyers
Some buyers list the parent group in their headline ("Procurement Manager at XYZ Group, India"). Search:
```
site:linkedin.com/in/ "<Group Name>" "<country>" "<role>"
```

---

## Intent C — Post-activity targeting (warm leads)

People who recently posted/commented about your product space are 5–10× more responsive to outreach.

### C1. Posts mentioning your product
```
site:linkedin.com/posts/ "<product>" "<country>"
```
Click into posts → check author → if author matches your role, prospect them.

### C2. Posts using a buyer pain phrase
```
site:linkedin.com/posts/ "looking for supplier" "<product>"
site:linkedin.com/posts/ "MOQ challenge" "<product>"
site:linkedin.com/posts/ "switching supplier" "<product>"
```

### C3. Recent activity within N days
LinkedIn Search itself (when logged in) supports "Posts → Date posted: Past week". Use this UI rather than Google for time-bound queries.

---

## Intent D — Industry / certification / event signals

These return profiles with strong commercial intent.

### D1. Trade show attendees
```
site:linkedin.com/in/ "<TradeShow Name>" "<role>" "<country>"
```
Example: `site:linkedin.com/in/ "Canton Fair" "Buyer" "Brazil"`

### D2. Certification holders (often = procurement)
```
site:linkedin.com/in/ "ISO 9001" "<product>" "<country>"
site:linkedin.com/in/ "CSCP" OR "CIPS" "<country>"
```
CSCP/CIPS are procurement certifications — strong filter for serious buyers.

### D3. Distributors (LinkedIn description)
```
site:linkedin.com/in/ "distributor" "<product>" "<country>"
site:linkedin.com/in/ "importer" "<product>" "<country>"
```

---

## Intent E — Wayback / cache fallback

For profiles indexed by Google pre-Auth-Wall but no longer accessible:

### E1. Wayback Machine on a known LI URL
```
https://web.archive.org/web/*/linkedin.com/in/<slug>
```
Use when: you have the URL but the live profile is gated.

### E2. Google cache (often expired in 2026 — try anyway)
```
cache:linkedin.com/in/<slug>
```

### E3. Wayback dork for *finding* archived profiles
```
site:web.archive.org "linkedin.com/in" "<product>" "<role>" "<country>"
```
Yields old archived LI pages with full text — the person may still be at the same company.

---

## Intent F — Exclusion stack (always apply)

Append these to A/B/C/D queries to clean noise.

### F1. Remove freelancers / consultants / job-seekers (these dominate `Buyer` searches)
```
... -"open to work" -"open to opportunities" -"freelance" -"independent consultant"
```

### F2. Remove recruiters
```
... -"recruiter" -"talent acquisition" -"hiring" -"head hunter"
```

### F3. Remove your home country (if you're in China and want non-China buyers)
```
... -"China" -"Hong Kong" -"中国"
```

### F4. Remove training/education content
```
... -"course" -"workshop" -"webinar" -"training"
```

---

## Operator differences across engines

| Operator | Google | Bing | Yandex | DuckDuckGo |
|---|---|---|---|---|
| `site:` | Yes (often partial in 2026) | Yes (better LI coverage) | Yes | Yes |
| `inurl:` | Yes | Yes | Yes | Limited |
| `intitle:` | Yes | Yes | Yes | No |
| `"exact phrase"` | Yes | Yes | Yes | Yes |
| `OR` (caps) | Yes | Yes | Yes | Yes |
| `-` exclusion | Yes | Yes | Yes | Yes |
| `cache:` | Mostly retired | No | Limited | No |
| `*` wildcard | Yes | Yes | Limited | No |

**Recommendation 2026**: Run the same query on Google AND Bing AND Yandex. Take union. Expect ~25% overlap, ~75% engine-unique results.

---

## Real campaign skeleton

For "12V LED strip 5050 → Brazil → Procurement Manager":

1. A2 (PT role): `site:linkedin.com/in/ "LED" "Brazil" "Gerente de Compras"`
2. A2 variant: `site:linkedin.com/in/ "iluminação" "Brazil" "Comprador"`
3. A1 (EN role): `site:linkedin.com/in/ "LED lighting" "Brazil" "Procurement Manager"`
4. A4 (Bing): same as 1 on bing.com
5. B1: `site:linkedin.com/company/ "LED" "Brazil"` — collect company list
6. B2 for top 5 companies: `site:linkedin.com/in/ "<Company>" "Procurement"`
7. C1: `site:linkedin.com/posts/ "LED supplier" "Brazil"` (last 30d, in LI UI)
8. D2: `site:linkedin.com/in/ "CIPS" "Brazil"` — certified procurement
9. F1+F2 suffix on 1, 3, 4: clean out consultants/recruiters

Expected: 40–120 profiles raw → 25–60 after dedupe → 15–35 after enrichment yields a usable email or phone.

If you can only run 5 queries, start with: 1, 2, 5, 6, 7.
