# Tools

Standalone utilities used by skills in this repo. Each tool can also be used independently of any SKILL.

## backlink-kol-extractor

Extracts KOL / influencer / media / affiliate candidates from Semrush competitor backlink & refdomains xlsx exports.

**Standalone usage** (any niche, not limited to cross-border e-commerce):

```bash
cd tools/backlink-kol-extractor
python3 scripts/extract_kol.py <semrush_data_dir> \
  --output prospects.csv \
  --min-sources 2 \
  --min-traffic 500
```

**Input layout:**
```
semrush_data/
  competitor1.com/
    competitor1.com-backlinks_refdomains.xlsx
    competitor1.com-backlinks.xlsx
    competitor1.com-organic.Competitors-us-*.xlsx
  competitor2.com/
    ...
```

**Output:** CSV sorted by `priority_score` with columns `domain, category, priority_score, traffic, backlinks, source_count, sources`.

**Used by (conditional activation):**
- `brand-strategy/influencer-marketing.md` → Step 2.5 (KOL discovery from competitor backlinks)
- `brand-strategy/dsite-seo-playbook.md` → Step 4.6 (external link gap analysis, anchor text reverse learning)

Both skills skip their Semrush modules gracefully if this tool's data is not provided.

See [backlink-kol-extractor/SKILL.md](backlink-kol-extractor/SKILL.md) and [references/methodology.md](backlink-kol-extractor/references/methodology.md) for details.
