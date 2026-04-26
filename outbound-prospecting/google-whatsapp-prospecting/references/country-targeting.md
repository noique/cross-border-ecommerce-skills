# Country Targeting Reference

Per-country: dial code → mobile prefix narrowing → regional B2B platforms → primary languages → time-zone send window → compliance flag.

The article's table had 15 countries with vague product hints ("electronics, clothing"). This expands to 30+ with the data you actually need to run a campaign — product category is **your** decision based on your inventory, not a generic suggestion.

Compliance flag legend:
- 🟢 Cold WhatsApp B2B generally OK with self-ID + opt-out
- 🟡 Defensible but risky — see `compliance.md` for specifics
- 🔴 Hard stop — switch channel (email / partner / paid)

---

## North America

| Country | Code | Mobile narrow | Top regional B2B sites | Lang | Send window (local) | Compliance |
|---|---|---|---|---|---|---|
| 🇺🇸 USA | +1 | Use area-code (e.g. `"+1 212"` NYC, `"+1 415"` SF) | thomasnet.com, ec21.com | EN | 09:00–17:00 | 🟡 CCPA in CA, TCPA federally — opt-out required |
| 🇨🇦 Canada | +1 | `"+1 416"` Toronto, `"+1 604"` Vancouver | scottsinfo.com | EN, FR (QC) | 09:00–17:00 | 🔴 CASL — implied consent only, expires 6mo |
| 🇲🇽 Mexico | +52 | `"+52 1 55"` CDMX, `"+52 1 33"` Guadalajara | cosmos.com.mx | ES | 10:00–18:00 | 🟢 |

## South America

| Country | Code | Mobile narrow | Top regional B2B sites | Lang | Send window | Compliance |
|---|---|---|---|---|---|---|
| 🇧🇷 Brazil | +55 | `"+55 11"` SP, `"+55 21"` RJ; mobiles use `9` after area code: `"+55 11 9"` | mercadolivre.com.br, cylex.com.br | PT | 09:00–18:00 | 🟡 LGPD — close to GDPR |
| 🇦🇷 Argentina | +54 | `"+54 9 11"` BA mobile | mercadolibre.com.ar | ES | 10:00–19:00 | 🟢 |
| 🇨🇱 Chile | +56 | `"+56 9"` mobile | yapo.cl | ES | 10:00–18:00 | 🟢 |
| 🇨🇴 Colombia | +57 | `"+57 3"` mobile | computrabajo.com.co | ES | 09:00–18:00 | 🟢 |
| 🇵🇪 Peru | +51 | `"+51 9"` mobile | mercadolibre.com.pe | ES | 09:00–18:00 | 🟢 |

## Europe (use with caution — see compliance.md before any EU campaign)

| Country | Code | Mobile narrow | Top regional B2B sites | Lang | Send window | Compliance |
|---|---|---|---|---|---|---|
| 🇬🇧 UK | +44 | `"+44 7"` mobile | applegate.co.uk, kompass.co.uk | EN | 09:00–17:00 | 🟡 UK GDPR + PECR — B2B easier than B2C |
| 🇩🇪 Germany | +49 | `"+49 15" / "+49 16" / "+49 17"` mobile | wlw.de, europages.de | DE | 09:00–17:00 | 🔴 UWG §7 restricts even B2B cold msg |
| 🇫🇷 France | +33 | `"+33 6" / "+33 7"` mobile | europages.fr, kompass.com | FR | 09:00–18:00 | 🟡 RGPD strict |
| 🇳🇱 Netherlands | +31 | `"+31 6"` mobile | europages.nl | NL, EN | 09:00–17:00 | 🟡 |
| 🇪🇸 Spain | +34 | `"+34 6" / "+34 7"` mobile | paginasamarillas.es | ES | 09:00–18:00 | 🟡 |
| 🇮🇹 Italy | +39 | `"+39 3"` mobile (always starts 3) | europages.it | IT | 09:00–18:00 | 🟡 |
| 🇵🇱 Poland | +48 | `"+48 5" / "+48 6" / "+48 7" / "+48 8"` mobile | panoramafirm.pl | PL | 08:00–17:00 | 🟡 |
| 🇷🇺 Russia | +7 | `"+7 9"` mobile | tiu.ru, pulscen.ru | RU | 10:00–19:00 | 🟢 (sanctions due-diligence required) |
| 🇹🇷 Turkey | +90 | `"+90 5"` mobile | sanayi.gov.tr | TR | 09:00–18:00 | 🟡 KVKK |

## MENA

| Country | Code | Mobile narrow | Top regional B2B sites | Lang | Send window | Compliance |
|---|---|---|---|---|---|---|
| 🇦🇪 UAE | +971 | `"+971 5"` mobile | dubizzle.com, dubaiyellowpagesonline.com | EN, AR | 09:00–18:00 (Sun–Thu) | 🟢 high WhatsApp adoption |
| 🇸🇦 Saudi Arabia | +966 | `"+966 5"` mobile | sa.opensooq.com | AR | 09:00–18:00 (Sun–Thu) | 🟢 |
| 🇪🇬 Egypt | +20 | `"+20 1"` mobile | tradekey.com, egyptyellowpages.com | AR | 10:00–18:00 (Sun–Thu) | 🟢 |
| 🇮🇱 Israel | +972 | `"+972 5"` mobile | yad2.co.il | HE, EN | 09:00–17:00 (Sun–Thu) | 🟡 |

## Africa

| Country | Code | Mobile narrow | Top regional B2B sites | Lang | Send window | Compliance |
|---|---|---|---|---|---|---|
| 🇿🇦 South Africa | +27 | `"+27 6" / "+27 7" / "+27 8"` mobile | tradekey.com, brabys.com | EN | 09:00–17:00 | 🟡 POPIA |
| 🇳🇬 Nigeria | +234 | `"+234 7" / "+234 8" / "+234 9"` mobile | vconnect.com | EN | 09:00–18:00 | 🟢 |
| 🇰🇪 Kenya | +254 | `"+254 7"` mobile | yellowpageskenya.com | EN | 09:00–18:00 | 🟢 |

## South / SE Asia (highest WhatsApp B2B intent globally)

| Country | Code | Mobile narrow | Top regional B2B sites | Lang | Send window | Compliance |
|---|---|---|---|---|---|---|
| 🇮🇳 India | +91 | `"+91 6" / "+91 7" / "+91 8" / "+91 9"` mobile (skip 1–5: landlines) | indiamart.com, tradeindia.com, exportersindia.com | EN, HI | 10:00–19:00 | 🟢 WhatsApp is *the* B2B channel |
| 🇵🇰 Pakistan | +92 | `"+92 3"` mobile | tcs.com.pk | EN, UR | 10:00–18:00 | 🟢 |
| 🇧🇩 Bangladesh | +880 | `"+880 1"` mobile | bdtradeinfo.com | EN, BN | 10:00–18:00 | 🟢 |
| 🇮🇩 Indonesia | +62 | `"+62 8"` mobile | indotrading.com | ID | 09:00–17:00 | 🟢 |
| 🇲🇾 Malaysia | +60 | `"+60 1"` mobile | yellowpages.my | EN, MS | 09:00–18:00 | 🟢 |
| 🇵🇭 Philippines | +63 | `"+63 9"` mobile | pinoybusiness.org | EN | 09:00–18:00 | 🟢 |
| 🇹🇭 Thailand | +66 | `"+66 6" / "+66 8" / "+66 9"` mobile | thailandyp.com | TH, EN | 09:00–18:00 | 🟢 (LINE more common than WA) |
| 🇻🇳 Vietnam | +84 | `"+84 3" / "+84 7" / "+84 8" / "+84 9"` mobile | vietnamtradefair.com | VI | 09:00–17:00 | 🟢 (Zalo also dominant) |

## East Asia (low WhatsApp adoption — channel switch usually better)

| Country | Code | Mobile narrow | Notes |
|---|---|---|---|
| 🇯🇵 Japan | +81 | LINE >> WhatsApp. Use LINE Open Chat or email. Cold WhatsApp = ~5% reply. |
| 🇰🇷 Korea | +82 | KakaoTalk dominant. Cold WhatsApp = ~3% reply. |
| 🇨🇳 China mainland | +86 | WhatsApp blocked. Use WeChat. Out of scope for this skill. |
| 🇹🇼 Taiwan | +886 | LINE dominant; WhatsApp B2B rare but viable for export-facing companies. |
| 🇭🇰 HK | +852 | WhatsApp common. `"+852 [5-9]"` mobile. 🟢 |

## Oceania

| Country | Code | Mobile narrow | Top regional B2B sites | Lang | Send window | Compliance |
|---|---|---|---|---|---|---|
| 🇦🇺 Australia | +61 | `"+61 4"` mobile | yellowpages.com.au | EN | 09:00–17:00 | 🟡 Spam Act — express/inferred consent |
| 🇳🇿 New Zealand | +64 | `"+64 2"` mobile | yellow.co.nz | EN | 09:00–17:00 | 🟡 |

---

## Notes on the ones the article got slightly wrong

- **Article says "美国和加拿大都是 +1"** — true, but the article suggests searching `"+1"` plain, which returns ~all of NANP including 14+ countries (Caribbean). Always narrow with area code.
- **India "+91"** — article example `LED lights WhatsApp +91` returns mostly landline-only directory pages. Use `"+91 9"` etc.
- **Brazil mobile** — article doesn't note that Brazilian mobiles have a `9` inserted after area code (since 2014), so `"+55 11 9"` not just `"+55 11"`.
- **Germany** — article lists it as a target market without flagging UWG §7 — *do not* run cold WhatsApp campaigns into Germany without legal review. The article's omission is a real liability.
