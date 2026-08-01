---
name: media-press-discovery
description: Build a journalist-level press outreach database from a list of media outlet domains. Use when the user wants to do PR / earned media outreach for a DTC brand and needs to find specific journalists at target outlets, with their beats, recent topical coverage, and pattern-guessed candidate emails that are treated as hypotheses rather than contacts: the pipeline runs `--verify` as part of the main flow, `email_verified` acts as a hard send gate (`verified` / `smtp_ok` sendable, `unverified` / `smtp_fail` to a manual-research queue), and no journalist name, byline, article URL or date may be reconstructed from memory to fill a row — an unfetchable outlet stays an explicit not-retrieved row. Triggers on "media pitch list", "find journalists at outlet", "PR outreach database", "press contacts for [outlets]", "build editor list", "who should I pitch at [outlet]", "journalist contacts for media outreach".
---

# Media Press Discovery

Build a per-journalist press outreach database from media outlet domains, anchored on Muckrack's public outlet pages, with a fetcher that handles Cloudflare reality.

## 🔴 Guessed emails are not contacts (read before you send anything)

`guess_emails.py` does exactly what its name says: it **pattern-guesses** (`firstname.lastname@outlet.com` and friends) from a name and a domain. A guess is a hypothesis, not a contact.

- 🔴 **Never send to a row whose `email_verified` is `unverified`.** Verify first (NeverBounce / ZeroBounce / an MX+SMTP probe), or find the address on the journalist's own byline page, outlet masthead or public profile.
- **Why this is not pedantry** — these are named, real journalists. A wrong guess lands one of three ways, and all three are bad:
  1. **Bounce** → repeated hard bounces damage your sending domain's reputation, which quietly degrades every future campaign
  2. **A different real person** at that outlet reads a pitch meant for someone else — worse than not sending
  3. **Spam trap** → some outlet domains run them; a hit can blocklist your domain
- **The verified column is a gate, not a note.** Export/segment on it: `verified` and `smtp_ok` are sendable, `unverified` goes to a manual-research queue.
- 🔴 **Never invent or "reconstruct" a journalist name, byline, article URL or publish date** to fill out the DB. Every row must trace to a page actually fetched in this run. Muckrack lags 2-8 weeks and journalists move — an unfetchable outlet is an `❌ not retrieved` row, not a row to be filled in from memory.
- **Compliance:** cold press outreach must still identify you honestly and offer a way to stop hearing from you (CAN-SPAM; GDPR legitimate-interest if the journalist is in the EU/UK). Repo-wide rule: do not disguise a pitch as something it isn't.

## Cloudflare Reality (read this first)

Muckrack sits behind Cloudflare. As of 2026-05, the following programmatic approaches **fail**:
- `requests` / `curl_cffi` → 403 (Cloudflare 5-sec JS challenge)
- Headless Selenium → blocked by `navigator.webdriver` detection
- `undetected-chromedriver` → version-skew / Apple Silicon binary issues + Cloudflare detection updates
- Connecting Selenium to a freshly-launched Chrome with empty profile → no `cf_clearance` cookie, fails challenge

What **works**:
1. **`--via html-dir`** (recommended for single-time use): user opens each outlet page in their normal browser (which has a valid `cf_clearance`), saves HTML, runs the parser against the directory. Works on any platform, $0, manual save step ~10s per outlet.
2. **`--via remote-chrome`** (for repeat use): user launches their normal Chrome with `--remote-debugging-port=9222`, browses muckrack.com once to obtain `cf_clearance`, then runs script which drives the same Chrome session. Faster than html-dir for repeat runs.
3. **`--via apify`** (paid, ~$0.001/page): Apify's Web Scraper actor handles Cloudflare in their infra. Set `APIFY_TOKEN` env var. Best for scale (100+ outlets).

The pipeline supports all three; choose based on scale.

## Quick Start (recommended html-dir flow)

```bash
# 1. Open each outlet page in your normal browser, save HTML to a dir
#    Naming convention: muckrack.com_media-outlet_<slug>.html
#    For ~25 Tier A outlets, this is 5-10 minutes of save-as.
mkdir -p press_html
# (manually save pages: muckrack.com/media-outlet/teenvogue → press_html/muckrack.com_media-outlet_teenvogue.html, etc.)

# 2. Run pipeline
cp templates/outlets_template.txt outlets.txt
cp templates/keywords_template.txt keywords.txt

python3 scripts/discover_journalists.py outlets.txt --via html-dir --html-dir press_html --out journalists.jsonl
# now ALSO save each journalist's /articles page (one HTML per journalist)
# (or use remote-chrome / apify for this step — see references/multi_machine.md)
python3 scripts/find_articles.py journalists.jsonl --keywords keywords.txt --via html-dir --html-dir press_html --out articles.jsonl
# --verify is NOT optional if you intend to send. Without it every row lands as `unverified`.
# Free path: SMTP MX probe (~60% accurate per the script's own docstring).
# Better: set HUNTER_API_KEY and the script uses Hunter instead of the raw probe.
python3 scripts/guess_emails.py journalists.jsonl --out emails.csv --verify
python3 scripts/score_and_export.py journalists.jsonl articles.jsonl emails.csv \
    --backlinks /path/to/kol_prospects.csv \
    --out pitch_db.csv
```

> 🔴 Before any outreach, split `pitch_db.csv` on `email_verified`: `verified` / `smtp_ok` are sendable; **`unverified` goes to a manual-research queue, not to the mailer.** The SMTP probe is ~60% accurate, so `smtp_fail` is "unproven", not "proven wrong" — send those to manual research too, don't delete the journalist.

## Quick Start (remote-chrome flow, faster repeat use)

```bash
# 1. Quit Chrome, then relaunch with debug port:
#    macOS:
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222 &

# 2. Manually browse to muckrack.com once and verify pages load (this seeds cf_clearance cookie)

# 3. Run pipeline — scripts will drive YOUR Chrome session
python3 scripts/discover_journalists.py outlets.txt --via remote-chrome --port 9222 --out journalists.jsonl
python3 scripts/find_articles.py journalists.jsonl --keywords keywords.txt --via remote-chrome --port 9222 --out articles.jsonl
python3 scripts/guess_emails.py journalists.jsonl --out emails.csv --verify
python3 scripts/score_and_export.py journalists.jsonl articles.jsonl emails.csv --out pitch_db.csv
```

Multi-machine fan-out: `references/multi_machine.md`.

## Inputs

| Required | Description | Example |
|---|---|---|
| `outlets.txt` | One outlet per line. Format: `muckrack_slug,outlet_domain` | `teenvogue,teenvogue.com` |
| `keywords.txt` | Topic keywords for relevance filter (one per line) | `[your category keyword 1]`<br>`[your category keyword 2]` |

Optional:
- `kol_prospects.csv` from sister skill `tools/backlink-kol-extractor` (boosts journalists at outlets that competitors got linked from).

## Output Schema

`pitch_db.csv` (sorted by `relevance_score` desc):

| Column | Type | Description |
|---|---|---|
| `outlet` | str | Muckrack slug |
| `outlet_domain` | str | Outlet root domain |
| `journalist` | str | Full name |
| `muckrack_url` | str | Profile URL |
| `topic_match_count` | int | # of bylined articles whose title matched topic keywords |
| `last_topic_article_url` | str | URL of most recent in-topic article |
| `last_topic_article_date` | str (ISO) | Publish date of that article |
| `relevance_score` | int | 0-100 — see `references/methodology.md` |
| `email_1`, `email_2`, `email_3` | str | **Pattern-guessed candidates — hypotheses, not contacts.** Never send without verifying |
| `email_verified` | str | `verified` / `smtp_ok` = sendable · `smtp_fail` / `unverified` = manual-research queue. 🔴 This column is a **send gate**, not a note |

## When to use

- New brand pre-launch (4-week+ runway), need to seed earned media.
- Have a Tier A outlet list (e.g., from `tools/backlink-kol-extractor` cross-validation).
- Want a structured outreach DB (journalist-level, not just outlet-level).

## When NOT to use

- Influencer/KOL discovery → use `tools/backlink-kol-extractor` (different anchor: backlinks not bylines).
- Pitch personalization at scale → out of scope (no LLM personalizer here; do it by hand or use a sister skill).
- Real-time editor changes / outlet hires → Muckrack lags 2-8 weeks; don't expect cutting-edge.

## References

- `references/methodology.md` — full 5-step playbook
- `references/multi_machine.md` — partition + merge workflow
- `references/tool_choices.md` — why this stack, what we tried, what failed
