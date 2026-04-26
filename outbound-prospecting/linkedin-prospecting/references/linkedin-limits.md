# LinkedIn Limits, ToS, and Account Hygiene

The article doesn't mention any of this. Run a "high reply rate template" campaign past LinkedIn's 2026 limits and your account gets restricted in week one.

---

## Hard quota limits (current as of 2026 Q1)

LinkedIn doesn't publish exact numbers. These are derived from observed account behavior across 2024–26:

| Action | Free account | Premium ($40/mo) | Sales Navigator ($99/mo) | Trigger |
|---|---|---|---|---|
| Connection requests | ~80–100 / week | ~150 / week | ~150–200 / week | Soft warning at 80%, freeze at 100% |
| Pending invitations | 5,000 cap | 5,000 cap | 5,000 cap | Hard cap; old ones must be withdrawn |
| Sent DMs (1st-degree) | ~100 / day | ~150 / day | ~200 / day | Slowdown / shadow-throttle |
| InMail credits | 0 | 5 / month | 50 / month | Pay per credit beyond |
| Profile views | ~80 / day | ~250 / day | unlimited | Soft cap; "Who viewed your profile" stops working |
| Search results visible | ~100 / search | ~700 / search | ~2,500 / search | Commercial Use Limit (CUL) |
| Daily searches | ~300 / day | ~1,000 / day | unlimited | CUL — "You've reached the monthly limit" |

⚠️ Limits **scale with account age and warm-up**. New (<3 months) accounts get hit at 30–50% of these numbers.

---

## What gets your account restricted

In order of severity:

1. **Sending the same message text >5 times in 24h** — LI's similarity detector flags it. First time = warning, repeat = 7-day restriction.
2. **>100 connection requests in a week** — gradual freeze: first you can't send invites for a few days, then for 2 weeks, then permanent restriction
3. **>5% connection-request decline + ignore rate** — if too many people ignore or decline your invites, LI assumes you're spamming and rate-limits you
4. **Multiple "Don't know" responses** — when invitees click "I don't know this person" on your invite, that's a hard signal. Three "Don't know"s in 30d = invite restriction
5. **Use of any browser automation** (Phantombuster / Linked Helper / Dux-Soup / Octopus / Expandi / Waalaxy) — LI fingerprints automation patterns. Detection in 1–6 months. Outcome: permanent ban.
6. **Mass exporting connections** — using "Export your data" repeatedly = scraping signal. 1× per quarter is OK.
7. **Logging in from many IPs simultaneously** (e.g. a VA in another country logged in while you're also active) — triggers security review

---

## Account warm-up protocol (mandatory for new accounts before any outreach)

If your LinkedIn is <90 days old or has <50 connections, do not run outreach. Warm it for 2–4 weeks first:

### Week 1 — Identity establishment
- Complete profile to 100% (photo, banner, headline, about, experience, skills)
- Add 20+ skills, request 3+ endorsements
- Connect with 30 1st-degree people you actually know
- Post 1 thought-leadership post (industry observation, not promo)

### Week 2 — Network build
- Send 15 connection requests (with personal note) to 2nd-degree people in your industry
- Comment thoughtfully on 5+ posts/day
- Like 20–40 posts/day
- React to messages within 4 hours
- Post 2 more posts (case study or industry data)

### Week 3 — Engagement signal
- Send 25 connection requests
- Reply to all messages
- Post 1×/week minimum
- Join 5 industry groups, comment in each

### Week 4 — Begin light outbound
- 30 connection requests/day max
- Use first-name personalization on every invite
- Track acceptance rate; if <30%, slow down further

### Week 5+ — Full outbound
- 60–80 invites/week
- 30–50 DMs/day to 1st-degree
- Continue posting/engaging in parallel

---

## ToS § 8.2 Highlights — what's banned

LinkedIn User Agreement, Dos and Don'ts (paraphrased):

- ❌ Develop, support, or use software / scripts / browsers to scrape Services
- ❌ Use bots, scrapers, or automated methods to access Services
- ❌ Bypass restrictions on use (incl. CUL workarounds)
- ❌ Override Services' security or interoperability features
- ❌ Use the Services for unauthorized commercial communications
- ❌ Reverse-engineer Services or related software
- ❌ Use the Services in ways that violate applicable law

What this means for outreach:
- **Manual DM = OK** (even if commercial)
- **Phantombuster / Dux-Soup / Linked Helper = banned**
- **Apollo / Hunter chrome extensions reading LI page** = grey area; LI has clamped down 2024–26
- **CSV export of your own connections via "Get a copy of your data" = OK** (LI feature)
- **CSV export of OTHER people's connections via scraper = banned**

---

## Specific tools and their account-ban rate (community-observed, 2024–26)

| Tool | Stated as "safe" | Actual ban rate (12mo) | Notes |
|---|---|---|---|
| Phantombuster | Yes | ~50–60% | Most heavily fingerprinted by LI |
| Linked Helper | Yes | ~40–50% | Throttled mode helps, doesn't prevent |
| Dux-Soup | Yes | ~35–45% | Older tool; LI knows its patterns |
| Octopus CRM | Yes | ~30–40% | Newer fingerprint, slightly safer |
| Expandi | Yes | ~25–35% | Cloud-based (different IP per account) |
| Waalaxy | Yes | ~25–40% | Same as Expandi class |
| **Manual sending** | n/a | <2% | Effectively zero risk if you stay under quota |
| **Apollo Chrome ext (read-only)** | Yes | ~10% | Increased 2025 after LI updates |

Math: at $99/mo Sales Navigator + $79/mo Phantombuster + ~50% chance of losing the account in 12 months → if your account is worth >$2k, manual is the better economic choice.

---

## The "shadow restriction" — recognizing it before LI tells you

LinkedIn often **silently throttles** before officially restricting. Signs:

- Connection requests sit in "Pending" for 30+ days even from people who normally accept
- Profile views drop to <5/week (was >30)
- Your search results drop sharply (you used to get 100, now you get 8)
- Notifications about your posts drop to near-zero
- Acceptance rate on your invites drops by half compared to baseline

If you see 2+ of these, **stop outbound for 14 days**. Resume at 50% of previous volume.

---

## Recovery from a restriction

If LI restricts your account:

1. **24–48h restriction** — wait it out; don't send invites
2. **7-day restriction** — wait it out; review your last 30 days for what triggered (usually >100 invites/week or duplicate-message flagging). Adjust before resuming.
3. **Permanent restriction (rare without prior warnings)** — appeal via LI Help. Provide:
   - Government ID (LI Photo Match)
   - Honest explanation
   - Confirmation you'll stop the offending behavior

Recovery rate for permanent restriction: ~25%. Don't count on it.

---

## When to use Premium / Sales Navigator vs free

Free LinkedIn + Apollo enrichment + manual sending is enough for most cross-border outbound campaigns. Pay for Premium/SN when:

- **Premium ($40/mo)**: you regularly hit Commercial Use Limit on searches (you're searching > 300/day). InMail (5/mo) lets you reach decision-makers you can't connection-request.
- **Sales Navigator ($99/mo)**: high-volume targeted outreach, you need to filter by company size / department / years at company / recent job change / etc. The advanced filters cut Stage 1 search effort by ~70%. Worth it for >200 leads/month.
- **Recruiter Lite ($170/mo)**: you're hiring, not selling. Out of scope for this skill.

---

## Multi-account strategies (legal grey area)

Some agencies run 5–10 LinkedIn accounts in parallel to multiply reach. Three approaches:

1. **One real person per account** — legitimate; each person manages their own outreach. Linear scale, fully legal.
2. **VAs operating accounts they "own"** — VA needs to be the named person, account in their name, photo, etc. Legal but risky if VA leaves with the account.
3. **One person operating multiple "personas"** — fake accounts. Violates LI Single Identity policy (Section 1.2 of User Agreement). LI bans these on detection. Don't do this.

---

## TL;DR account hygiene

- Never automate
- Never duplicate message text
- Stay under 80 invites/week, 100 DMs/day
- Warm new accounts 4 weeks before outbound
- Track shadow-restriction signals weekly
- One real person per account
- Manual sending feels slow but is the only sustainable path
