# Honest Scope

Be upfront with the user about what this teardown does and does NOT tell you. It is a measurement tool, not a ranking guarantee.

## What it finds: the ~20-30% code-side

This pipeline reverse-engineers the **structure / SEO / GEO "code-side" of what wins** — the part you can copy mechanically:

- which **archetype** the incumbents use, and its word / H2 / FAQ / schema bands
- the **keyword** universe, intent split, difficulty, and quick-wins
- the realistic **page-level authority** band to clear top-10, and whether weak-link winners prove the topic is content-beatable
- **on-page hygiene** (title/meta/H1/canonical/internal links) the incumbents meet
- **AI-Overview saturation** per topic and which domains get cited

Realistically that is **20-30% of why a page ranks**.

## What it does NOT find: the ~70-80%

The other **70-80% is content quality, domain age, and backlinks** — none of which this measures or fixes:

- It cannot judge whether the prose is genuinely *helpful* (Google's Helpful Content signal). It counts words and headings; it doesn't read for quality.
- It cannot change your **domain age** or **domain authority**.
- It cannot build **backlinks** (for that, see `tools/backlink-kol-extractor` to find prospects).
- It cannot make Google **crawl a new site**. A perfect archetype on a 3-week-old domain still won't rank.

**The first thing to say to the user** when they ask "so if I copy this structure I'll rank?":

> The teardown gives you the copyable 20-30% — the right shape, length, schema, and keywords. The other 70-80% is content depth, domain age, and backlinks, which no structure analysis can hand you. Match the structure *and* write something genuinely better, then earn links — the teardown just removes the guesswork from the part that's mechanical.

## Specific data limits

### Backlinks are PAGE-level Authority Score, not domain DR
`backlink_analysis.py` reads Semrush **Page AS** (page-level Authority Score, 0-100), `Ref.Domains`, and `Backlinks` for individual ranking URLs.

- You **can** say: "page-level links aren't the bottleneck for this long tail" — the data routinely shows top-3 pages at Page AS 0-20, with multiple top-10 winners at **Page AS 0**.
- You **cannot** say: "you need a domain DR of X to compete." That number is not in these exports. A weak *page* on a strong *domain* still ranks on the domain's authority — and Page AS won't reveal that floor. Do not invent a domain-authority threshold.

### AI-Overview citation capture is SPARSE
`geo_analysis.py` reads the `Type = "AI Overview"` rows Semrush captured. These are **incomplete** — Semrush samples AIO citations, and many triggering queries have no captured cited-URL rows.

- In the reference run, only one fetched competitor page's domain coincided with a captured AI-cited URL. The honest reading is **"schema depth didn't gate citation in-sample."**
- That is **NOT** the same as "schema is useless for GEO." It means the in-sample evidence is too thin to conclude either way. Say so. Flag GEO recommendations as ⚠️ estimates.
- Coverage of GEO-relevant schema nodes across fetched pages (e.g. FAQPage 3/25, VideoObject 0/25, HowTo 0/25 in the reference run) is a real, copyable *gap* — you can recommend adding those nodes for citation surface, framed as a hypothesis ⚠️, not a proven lever.

## RED LINE: no paid APIs, no live AI probing

The fetch step (`fetch_competitors.py`) is **`curl`-only with a browser User-Agent**. This is a hard boundary:

- **No** Ahrefs, Apify, Tavily, Jina, ScrapingBee, OpenRouter, or any other paid scraping/LLM API — not for fetching, not for "filling gaps."
- **No** live AI-citation probing of Perplexity / Gemini / ChatGPT to test whether a page gets cited. `geo_analysis.py` prints a note that this was deliberately not run.
- Cloudflare-gated / JS-challenge pages are **expected losses**. The fetch manifest flags them `blocked`; the pipeline skips them. Do not "work around" a block with a headless browser or a paid scraper.

If — and only if — the user **explicitly authorizes** a paid API or a live AI-citation probe, that becomes a separate, opt-in step outside this pipeline's default behavior. Until then, every number this skill produces comes from local Semrush files + `curl`-fetched HTML, and any figure that extrapolates beyond what the data literally shows must carry a ⚠️.

## Parser gotcha worth knowing

The structure scripts parse HTML with **`html5lib`**, not Python's stdlib `html.parser`. This is deliberate:

> `html.parser` does not treat `<link>` / `<input>` (and other void tags) as self-closing the way a browser does. On some Shopify themes that emit an unclosed `<link>` (or `<input>`) inside the document body, `html.parser` silently nests the entire article body *inside* that void element. Downstream container-picking then sees an empty `<article>`/`<body>` and the **word count comes back 0**. `html5lib` parses void tags the way a real browser does, so the body stays where it belongs.

If you ever swap the parser or see a cluster of suspicious `word_count: 0` rows on otherwise-fine pages, this is the cause. Keep `html5lib`.
