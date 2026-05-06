# Media Press Discovery — Full Methodology

This document expands SKILL.md's 5-step summary into a step-by-step playbook with rationale, code references, and known failure modes.

## Step 1: Outlet → Muckrack Roster

**What it does**: Given a list of media outlet domains, retrieve the journalist roster for each from Muckrack's public outlet pages.

**Why Muckrack**:
- Free public pages at `muckrack.com/media-outlet/{slug}` list every bylined journalist at a publication.
- Coverage is comprehensive for major US/UK outlets (~95% of the IMC §11 Tier A list是被索引的).
- Structured HTML — anchor links to journalist profiles are a stable surface (verified across 3 pilot outlets 2026-05-06).
- Free at the outlet-page level. Only journalist contact info (email/phone) is paywalled.

**Why NOT scrape outlet sites directly**:
- Major outlets (Hearst, Condé Nast, Dotdash Meredith) sit behind Cloudflare. Selenium dumps frequently hit "请稍候…" challenges.
- Site-internal `/search?q=` endpoints exist but JS-render late and require Selenium with 6+ second waits.
- WebSearch with `site:domain` operator is unreliable — major search backends don't always honor it.

**Slug discovery**: For most outlets the Muckrack slug is the outlet name lowercased and dashed. Exceptions:
- `nbcnews.com` → `nbc-news`
- `nytimes.com` → `the-new-york-times`
- `theguardian.com` → `the-guardian`
- `glamourmagazine.co.uk` → `glamourmagazine-uk`

When unsure, manually visit `muckrack.com` and search the outlet name.

**Code**: `scripts/discover_journalists.py`. Uses `requests` + `BeautifulSoup`. Falls back to Selenium with `--selenium-fallback` if HTTP request returns blocked / sparse content.

**Known failure modes**:
- **Niche outlets not on Muckrack**: e.g., very small Substack newsletters or new-launch publications. Workaround: use the outlet's onsite `/about/` or `/team/` page (Selenium dump if blocked).
- **Rate limiting**: Aggressive scraping (>10 req/min) triggers 429. Script paces with `gaussian_sleep(mean=2.5, sd=0.7)`.
- **Roster freshness**: Muckrack lags actual outlet hires by 2-8 weeks. For cutting-edge new hires, also check the outlet's masthead.

## Step 2: Journalist → Topic Relevance

**What it does**: For each journalist, fetch their `muckrack.com/{slug}/articles` page and score topical relevance from their byline history.

**Scoring inputs**:
- `topic_match_count`: Number of bylined articles whose title contains a topic keyword.
- `most_recent_topic_date`: Most recent in-topic byline.
- These feed into `score_and_export.py`'s composite formula.

**Why title-only matching**: Reading article body for accurate semantic relevance is order-of-magnitude slower (full HTML fetch + parse + LLM scoring). Title gives ~80% of the signal at <5% of the cost. For high-value targets, a follow-up semantic pass can be added.

**Code**: `scripts/find_articles.py`.

**Known failure modes**:
- **Sparse profile**: Some journalists' Muckrack profiles list only 5-10 articles even if they've published 100s. Workaround: cross-reference with their outlet's site search via Selenium.
- **No topic match ≠ irrelevant**: A wellness editor may not have a "period" article in title even if they cover the category. The `cross_link_bonus` from competitor backlink data partially compensates (Step 3).

## Step 3: Cross-Reference with Competitor Backlinks (Optional)

**What it does**: If `tools/backlink-kol-extractor` was run on competitor Semrush data, journalists whose outlet appears in 2+ competitors' refdomains receive a `+20` score bump.

**Why**: An editor who's already covered multiple competitors in articles you can see in the backlink graph is a higher-conviction target than one who matches keywords but hasn't been linked. The backlink graph gives "who's been cited" while Muckrack gives "who's published".

**Code**: `score_and_export.py --backlinks kol_prospects.csv` (output of `extract_kol.py`).

## Step 4: Email Pattern Guessing

**What it does**: Generate 1-3 candidate emails per journalist using outlet-specific email format conventions.

**Why guess vs paid lookup**:
- Hunter.io / RocketReach / Apollo charge $0.10-$0.50 per verified email lookup. At 100s of journalists, that's a real spend.
- Outlet email formats are highly standardized within publishing groups. Once you know one Hearst journalist's email pattern, you know all of them. The pattern table in `guess_emails.py` covers 95% of US/UK lifestyle media.
- For high-value targets ("Tier S" by relevance_score), supplement with a paid verifier — set `HUNTER_API_KEY` env var.

**Default patterns** (covered in `OUTLET_PATTERNS` dict):
| Group | Pattern | Examples |
|---|---|---|
| Hearst | `firstname.lastname@` | cosmopolitan, esquire, goodhousekeeping |
| Condé Nast | `firstname_lastname@` | vogue, glamour, allure, teenvogue |
| Dotdash Meredith | `firstname.lastname@` | people, instyle, byrdie, parents |
| NBCUniversal | `flastname@` | nbcnews |
| Vice / Refinery29 | `firstname.lastname@` | refinery29 |

**Verification options**:
- `--verify` with `dnspython` + `smtplib` → free SMTP MX probe (~60% accurate, can false-positive on accept-all servers).
- `--verify` with `HUNTER_API_KEY` env var → paid Hunter.io API (~95% accurate).

**Known failure modes**:
- **Outlets with non-standard email**: Some smaller indies use `tips@outlet.com` or `editor@outlet.com` only. The pattern engine still produces guesses; user must spot-check.
- **Names with apostrophes / accents**: `normalize_name()` ASCII-folds (e.g., "O'Brien" → "obrien"). Most outlets follow this convention but some preserve apostrophes via `firstnameosbrien@`.

## Step 5: Manual Qualification + Outreach

**This step is intentionally NOT automated.**

The CSV output is a structured starting point. Actual outreach requires:
- Read 2-3 of each high-priority journalist's recent articles to understand their voice and angle preferences.
- Craft a personalized pitch (no template-spray). Industry response rates (推算): generic spray 1-3%, personalized 15-25%, warm intro 30-50%.
- Time pitches against the outlet's editorial calendar (most categories have natural seasonality — e.g. category awareness months, holiday gifting cycles, back-to-school).

This is craft, not pipeline. The user's local PR playbook covers outreach methodology — see your project's `PR_建联方法论_*.md` if it exists.

## End-to-End Quick Run

```bash
# 1. Build outlet list (or use templates/outlets_template.txt as seed)
cp templates/outlets_template.txt outlets.txt
cp templates/keywords_template.txt keywords.txt

# 2. Step 1: Discover journalists
python3 scripts/discover_journalists.py outlets.txt --out journalists.jsonl
# expect: ~10-20 journalists per outlet × N outlets

# 3. Step 2: Topic-filter their articles
python3 scripts/find_articles.py journalists.jsonl --keywords keywords.txt --out articles.jsonl
# expect: ~10-20% of journalists will have ≥1 topic match

# 4. Step 4: Guess emails
python3 scripts/guess_emails.py journalists.jsonl --out emails.csv

# 5. Step 5: Score + export
python3 scripts/score_and_export.py journalists.jsonl articles.jsonl emails.csv \
    --backlinks /path/to/kol_prospects.csv \
    --out pitch_db.csv

# Result: pitch_db.csv sorted by relevance_score desc.
# Top 30-50 rows are usually the actionable Tier A pitch list.
```

For multi-machine fan-out, see `multi_machine.md`.
