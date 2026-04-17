# Trustpilot Analysis Toolkit

Python toolkit for scraping and analyzing Trustpilot reviews.

**Used by:** `/trustpilot-voc-deep` SKILL

## Key Files

- `main.py` — Entry point
- `scraper.py` — Selenium-based scraper with proxy rotation
- `sentiment.py` — Review sentiment analysis
- `topic_modeling.py` — LDA topic modeling
- `ai_analysis.py` — AI-powered deep insights (needs `OPENROUTER_API_KEY` env var)
- `visualization_antv.py` — **AntV-based charts** (replaces matplotlib for report-style consistency)
- `visualization.py` — Original matplotlib version (kept for fallback)

## Environment Variables

```bash
export OPENROUTER_API_KEY="your-key"   # for AI analysis
```

## Dependencies

```bash
pip install selenium seleniumwire webdriver-manager fake-useragent \
            pandas openpyxl numpy requests tqdm scikit-learn nltk
```

## Usage

See `/trustpilot-voc-deep` SKILL for full usage guide.

---

> Created by Alex / 黄子阳 — https://ckcm.us
> Open Source: https://github.com/noique/cross-border-ecommerce-skills
> Licensed under CC BY-NC 4.0
