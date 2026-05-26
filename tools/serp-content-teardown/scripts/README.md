# SERP Content Teardown — scripts

A deterministic, reusable toolkit that reverse-engineers what it takes to rank in
a niche's informational SERPs. It turns SEMrush exports into a ranked competitor
blog/info URL pool, fetches the top articles (curl only), and produces
per-article structure metrics, an 8-archetype classification, keyword /
authority-threshold / GEO (AI-Overview) / on-page analyses — all as JSON you can
feed into a content brief.

Everything is deterministic. **No LLM. No paid APIs.** Fetching is `curl` with a
browser User-Agent and nothing else (see [Red lines](#red-lines)).

Works for **any brand / niche** — the niche-specific bits (topic clusters, brand
display names) are externalized to two small config files.

---

## Install

```bash
cd tools/serp-content-teardown/scripts
python3 -m pip install -r requirements.txt
```

Dependencies: `pandas`, `openpyxl` (read SEMrush `.xlsx`), `beautifulsoup4` +
`html5lib` (parse HTML), `PyYAML` (read the topic-cluster config). `curl` must be
on `PATH` (it ships with macOS and most Linux distros).

---

## Inputs

1. **SEMrush exports** in one directory (`--semrush-dir`). The toolkit reads:
   - `*serp_urls*.xlsx` — per-keyword SERP rows (used by parse / backlink / geo).
     Filenames must look like `KEYWORD_serp_urls_REGION_DATE.xlsx`
     (e.g. `waterproof-jewelry_serp_urls_us_2026-05-01.xlsx`).
   - `*broad-match*us*.xlsx` — keyword universe (used by keyword analysis).
2. **A topic-cluster config** (`--topics`, YAML) — see [Config](#config).
3. **Optional brand-names config** (`--brand-names`, JSON) — see [Config](#config).

---

## Quick start (run everything)

```bash
python3 run_all.py \
  --semrush-dir ~/Downloads/semrush/my_project/_keywords \
  --out-dir     /tmp/teardown_mybrand \
  --topics      ../templates/topic-clusters.yaml \
  --brand-names ../templates/brand-names.json \
  --top 30
```

`run_all.py` runs the 8 steps in dependency order and stops on the first failure.
Copy the two template configs, edit them for your niche, and point `--topics` /
`--brand-names` at your copies.

---

## Per-step usage

Run individually for debugging or partial reruns. All artifacts land in
`--out-dir`; later steps read earlier steps' JSON, so keep `--out-dir` consistent.

```bash
# 1. SEMrush serp_urls -> ranked blog/info URL pool
python3 parse_serp.py --semrush-dir DIR --out-dir DIR --topics topic-clusters.yaml [--limit 40]

# 2. Fetch top-N articles (curl + browser UA; anti-bot pages skipped+logged)
python3 fetch_competitors.py --out-dir DIR [--top 30] [--select FILE]

# 3. Per-article structure metrics -> results.json + prose_dump.txt
python3 analyze_structure.py --out-dir DIR [--brand-names brand-names.json]

# 4. 8-archetype classification + aggregate stats -> classified.json
python3 classify_archetypes.py --out-dir DIR

# 5. Keyword distribution + core/quick-win keywords -> keywords.json
python3 keyword_analysis.py --semrush-dir DIR --out-dir DIR --topics topic-clusters.yaml

# 6. Authority/backlink thresholds + weak-link winners -> backlinks.json
python3 backlink_analysis.py --semrush-dir DIR --out-dir DIR --topics topic-clusters.yaml

# 7. GEO / AI-Overview saturation + cited domains + schema readiness (console)
python3 geo_analysis.py --semrush-dir DIR --out-dir DIR

# 8. On-page SEO (title/meta/H1/canonical/internal links) -> onpage.json
python3 onpage_analysis.py --out-dir DIR
```

### Choosing which articles to fetch (step 2)

By default `fetch_competitors.py` auto-selects the top `--top` ranked URLs from
`url_pool.json`, capped at **2 per domain** for diversity. To curate manually,
pass `--select FILE` with one path-fragment per line (overrides `--top`):

```text
# one fragment per line; '#' comments allowed
/blogs/journal/waterproof-jewelry-101          # substring match on domain+path
clarajane.co|/pages/waterproof-jewelry         # 'domain|fragment' pins the domain
```

---

## Config

### `topic-clusters.yaml` (`--topics`)

Buckets keywords / URLs into named topic clusters. A top-level `clusters:` list
of `{name, pattern}`, **evaluated in order — first match wins**. `pattern` is a
Python regex matched case-insensitively (substring) against the lowercased
keyword or slug. Anything matching nothing is bucketed as `OTHER`.

```yaml
clusters:
  - name: COMPARISON
    pattern: \b(vs|versus|difference|compared)\b
  - name: WATER_SHOWER
    pattern: \b(waterproof|water.?resistant|shower|swim|sweat)\b
  # ... most specific / highest-intent first; broad catch-alls last
```

`templates/topic-clusters.yaml` ships as an **example for the jewelry niche** —
replace it wholesale for yours. Cluster names flow into the output JSON, so keep
them stable across reruns.

### `brand-names.json` (`--brand-names`, optional)

Maps a registrable domain to its brand display-name variants, used only for
brand-density scoring in `analyze_structure.py`. Use **specific** forms
(spaced + concatenated), never generic words like "jewelry" that would inflate
the count.

```json
{
  "oceanwavejewelry.com": ["ocean wave", "oceanwave"],
  "mejuri.com": ["mejuri"]
}
```

If a fetched domain is **not** listed (or the flag is omitted), the brand token
is auto-derived from the domain (`oceanwavejewelry.com` → `oceanwave`).
`templates/brand-names.json` ships as a small jewelry-niche example.

---

## Outputs

All written under `--out-dir`:

| File                 | Produced by            | Contents |
|----------------------|------------------------|----------|
| `url_pool.json`      | parse_serp             | Ranked competitor blog/info URLs + matched keywords / positions |
| `html/`              | fetch_competitors      | Raw fetched HTML, one file per article (slugged) |
| `fetch_manifest.json`| fetch_competitors      | Per-URL fetch result: http code, bytes, ok/blocked |
| `results.json`       | analyze_structure      | Per-article structure metrics (words, headings, schema, author, dates, brand density, outlinks) |
| `prose_dump.txt`     | analyze_structure      | Human-readable opening / H2 outline / closing for each article |
| `classified.json`    | classify_archetypes    | `results.json` + archetype, opening/closing pattern, schema signature |
| `keywords.json`      | keyword_analysis       | Deduped keyword universe with volume / KD / intent / cluster / SERP-feature flags |
| `backlinks.json`     | backlink_analysis      | Organic ranking rows with Page AS / Ref.Domains / Backlinks per cluster |
| `onpage.json`        | onpage_analysis        | Per-page title/meta/H1/canonical/internal-link facts |

Steps 4-8 also print summary tables to the console (distributions, bands,
thresholds, cited domains) — that's where the read-at-a-glance analysis lives.

---

## Red lines

- **Fetching is `curl` only** (browser UA, follow redirects, `--compressed`, ~25s
  timeout). **No paid scraping / SERP / extraction APIs** (Ahrefs, Apify, Tavily,
  Jina, OpenRouter, ScrapingBee, etc.). Pages that return non-2xx, are tiny
  (<1500 bytes), or carry an anti-bot fingerprint ("just a moment",
  "cf-browser-verification", "attention required", "captcha", …) are **skipped
  and logged**, never retried through a paid service.
- **No LLM anywhere.** Every classification and metric is rule-based and
  deterministic — same inputs, same outputs.
- **No live AI-engine probing.** GEO analysis reads SEMrush's AI-Overview rows
  and local HTML schema only; it does not call Perplexity / Gemini / ChatGPT.

## Implementation notes

- **HTML parsing uses `BeautifulSoup(html, "html5lib")`, not `html.parser`.**
  `html.parser` silently nests article bodies inside unclosed void tags
  (`<link>` / `<input>`) on many Shopify themes, which zeroes out word counts.
  `html5lib` parses the way a browser does and avoids this. Don't swap it.
- Content extraction strips `script/style/nav/header/footer/aside` + junk-class
  elements, then picks the main container by maximum `<p>`/`<li>` text length
  (falling back to `<body>` for thin pages), so metrics reflect article prose
  rather than chrome.
