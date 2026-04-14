---
name: backlink-kol-extractor
description: Extract KOL, influencer, media, and partnership prospects from Semrush competitor backlink/refdomains/competitors xlsx data. Use when the user wants to find influencers, KOLs, review sites, media contacts, PR targets, affiliate partners, or forum communities from Semrush data exports. Triggers on "find KOL", "extract influencers from backlinks", "find review sites", "find media contacts", "partnership prospects", "who links to competitors", "backlink analysis for outreach", "find blogs that review", "discover influencer partners", "find collaboration opportunities from SEO data".
---

# Backlink KOL Extractor

Extract KOL/influencer/media prospects from Semrush competitor data using a three-step methodology: domain pattern matching, cross-competitor validation, and social media handle extraction.

## Quick Start

Run the extraction script on a directory of Semrush xlsx exports:

```bash
python3 scripts/extract_kol.py <input_dir> [--output results.csv] [--min-sources 2] [--min-traffic 500]
```

**Input**: Directory with Semrush xlsx files organized by domain subdirectories:
```
input_dir/
  competitor1.com/
    competitor1.com-backlinks.xlsx
    competitor1.com-backlinks_refdomains.xlsx
    competitor1.com-organic.Competitors-us-*.xlsx
  competitor2.com/
    ...
```

**Output**: CSV with columns: `domain, category, priority_score, traffic, backlinks, source_count, sources`

## Workflow

### Step 1: Gather Data

Ensure Semrush data is downloaded for 3+ competitors in the target niche. Key files:
- `*-backlinks_refdomains.xlsx` — Primary source (which domains link to competitor)
- `*-backlinks.xlsx` — Secondary (specific URLs, can extract social handles)
- `*-organic.Competitors-*.xlsx` — Tertiary (traffic overlap sites)

### Step 2: Run Extraction

```bash
python3 scripts/extract_kol.py ~/Downloads/semrush/_project_tactibeaver/
```

The script scans all xlsx files recursively, categorizes domains into KOL/Review, Media/Press, Forum/Community, Affiliate/Deal, cross-validates by counting how many competitors each domain links to, scores by priority, extracts social media handles from backlink URLs, and outputs sorted CSV.

### Step 3: Interpret Results

Priority tiers:
- **Score 70+**: Core industry sites — prioritize for outreach
- **Score 50-70**: Important channels — include in outreach list
- **Score 30-50**: Worth monitoring — add to watchlist

### Step 4: Expand via Linktree

For domains with linktree URLs found, visit `linktr.ee/{username}` to discover full social media presence.

## Advanced Usage

Custom thresholds:
```bash
python3 scripts/extract_kol.py ./data --min-sources 3 --min-traffic 1000
```

## Methodology Details

See [references/methodology.md](references/methodology.md) for category detection keywords, scoring formula, social media URL patterns, and filter rules.
