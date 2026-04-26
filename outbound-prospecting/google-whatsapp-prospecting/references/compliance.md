# Compliance & Risk Reference

The original article's only legal-adjacent advice was "don't spam product brochures or you'll get reported". That's a UX tip, not compliance. This file covers actual legal exposure.

Three layers of risk, in order of severity:

1. **Platform** — WhatsApp will ban your number for ToS violations regardless of legal status
2. **Country law** — anti-spam regulations in the buyer's jurisdiction (GDPR, CASL, CCPA, etc.)
3. **Industry-specific** — additional rules for healthcare / finance / regulated goods

If layer 1 fires, your campaign stops. If layer 2 fires, you can be fined. If layer 3 fires, you can be criminally liable in some markets.

---

## Layer 1 — WhatsApp ToS

WhatsApp's *Terms of Service* and *Acceptable Use Policy* prohibit:

- "Bulk or automated messaging" from a personal WhatsApp account
- "Use that conflicts with our Acceptable Use Policy" (broad — includes unsolicited promotional messaging)
- Use of unauthorised third-party clients (any "WhatsApp marketing tool" not built on Business API)

**What gets a number banned:**
- 3+ recipients block you within 24h → automatic warning
- 5+ block + 2+ report → 24h ban
- Repeat offence → permanent ban + device-fingerprint ban (new SIMs from same device get re-banned)

**The compliant path for any campaign >50 messages/day:**

| Approach | Cost | Setup time | Use when |
|---|---|---|---|
| Personal WA, manual | Free | 0 | <30 messages/day, 1:1 conversations only |
| WhatsApp Business app (free) | Free | 1 day | <50 messages/day, single user, broadcast list ≤256 |
| WhatsApp Business API via BSP (Twilio, 360dialog, Gupshup, MessageBird) | $0.005–0.05 / message | 1–2 weeks | >50/day, automation, multi-user |
| Direct Meta Cloud API | Free messages, $billing on conversations | 2–4 weeks | >5000/month, in-house dev resource |

For Business API, every "marketing template" must be **pre-approved by Meta**. They reject templates that look like cold outreach without prior consent. The realistic compliant flow:

1. Find lead via Google
2. Send a *transactional-looking* opt-in request via email or web form
3. Once user replies / clicks consent → send WhatsApp via Business API

This is more friction than the article suggests but is the path that doesn't get your business banned.

---

## Layer 2 — Country regulation

### EU + UK — GDPR / UK GDPR / PECR

**Lawful basis options for B2B cold WhatsApp:**

- **Legitimate interest** (Art. 6(1)(f)) — defensible if all of:
  - Recipient is a *business contact* (corporate role, not consumer)
  - First message clearly identifies sender, company, source ("found you on europages.com")
  - First message contains opt-out instruction ("Reply STOP and I won't message again")
  - You keep a Legitimate Interest Assessment (LIA) document on file
  - You honour opt-outs across all channels

- **Consent** (Art. 6(1)(a)) — required for any consumer or marketing-heavy message. Cold WhatsApp cannot establish this.

**Country-specific overlays:**

- 🇩🇪 Germany — UWG §7 Abs. 2 Nr. 2: even B2B cold electronic messaging requires *prior express consent* per the Federal Court (BGH I ZR 169/04). Practical advice: do not run cold WhatsApp into German businesses. Use email with double opt-in or partner channel.
- 🇫🇷 France — CNIL guidance permits B2B legitimate interest but requires opt-out in every message.
- 🇮🇹 Italy — Garante has enforced against cold WhatsApp B2C; B2B less tested.

Fines: up to €20M or 4% global revenue, whichever higher.

### Canada — CASL

Canadian Anti-Spam Legislation covers any "commercial electronic message" including WhatsApp. Need:

- **Express consent** (recipient said yes), OR
- **Implied consent**:
  - Existing business relationship (purchase / inquiry within last 24 months)
  - "Conspicuous publication" of contact info — *and* the contact is relevant to the role advertised. Pulling a procurement manager's WhatsApp from their LinkedIn where they listed it specifically for business inquiries → defensible. Pulling the CEO's number from a leaked PDF → not defensible.

Implied consent **expires** 6 months after last interaction.

Fines: up to CA$10M per violation.

### USA — TCPA + CCPA

- **TCPA**: regulates "telephone solicitations" including text messages. WhatsApp messages are arguably text under TCPA, but enforcement has focused on SMS. Cold WhatsApp B2B is a grey area — most enforcement comes from class actions, not regulators.
- **CCPA / CPRA** (California residents): if recipient is identifiable as Californian, they can request deletion + opt-out. Provide opt-out in message 1.

### Brazil — LGPD

Substantively similar to GDPR. Legitimate interest available for B2B but with stricter "data subject expectation" test. Brazil also enforces a national do-not-call registry (Não Me Perturbe) that some courts have extended to WhatsApp.

### Australia — Spam Act 2003

- Express, inferred, or deemed consent required
- Inferred consent is closest to "their contact is published for business inquiries"
- Functional unsubscribe required in every message
- ACMA actively fines (AU$2.2M+ recent cases)

### India / SE Asia / MENA / Africa

Generally permissive for B2B. India's IT Act + DPDPA 2023 introduce GDPR-like rules but enforcement is light. Personal opt-out should still be honoured.

### Russia

Personal data law (152-FZ) requires consent. Practically, less enforcement risk than EU. Bigger risk: sanctions due-diligence — confirm recipient isn't on OFAC / EU consolidated lists before transacting.

---

## Layer 3 — Industry overlays

| Industry | Restriction |
|---|---|
| Healthcare / pharma | EU + US: cold marketing of prescription products to non-HCPs is illegal. WhatsApp doesn't exempt. |
| Financial services / crypto | MiFID II + most national regulators forbid unsolicited investment promotion. |
| Tobacco / vape / alcohol | Country-specific marketing restrictions; WhatsApp counts as direct marketing. |
| Gambling | Most EU countries prohibit cold marketing; UAE, KSA prohibit entirely. |
| Children's products | COPPA (US), GDPR-K (EU) — never collect data on under-16s. |
| Defence / dual-use | Export control overrides everything; verify recipient against denied parties lists. |

---

## A practical compliance checklist (run before every campaign)

```
[ ] Target country flag from country-targeting.md is 🟢 OR 🟡-with-mitigation OR 🔴-and-I'm-switching-channel
[ ] Legitimate Interest Assessment written and saved (EU/UK/CA/AU)
[ ] First message includes: my name, my company, where I found their contact, opt-out instruction
[ ] Sending via WhatsApp Business app (≤50/day) OR Business API (any volume)
[ ] No claims about regulated products without licence (financial / health / etc.)
[ ] Recipient list run against OFAC/EU/UK sanctions lists (if any chance of restricted-party hits)
[ ] Time-zone send window respected
[ ] Opt-out tracking in place — STOP / "remove me" / 不要再发了 etc.
[ ] DPO / legal counsel consulted for any campaign >1000 EU/UK contacts
```

If any unchecked item is a hard requirement for the target market, **stop the campaign** and either fix it or switch channel.

---

## Recommended channel switch when WhatsApp is too risky

| Original target | Switch to | Why |
|---|---|---|
| Cold DE business contacts | Email with explicit opt-in form | UWG §7 |
| Cold CA contacts >6mo old | Email with CASL-compliant header | Implied consent expired |
| Cold consumer markets | Paid Meta ads with WhatsApp click-to-chat (consent at click time) | Consent flow |
| Regulated industry | LinkedIn InMail (less aggressive) + content marketing | Lower marketing-touch threshold |
| Sanctions-restricted recipient | Stop. Do not transact. | OFAC violations are criminal |
