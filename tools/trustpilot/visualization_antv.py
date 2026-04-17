"""
AntV-based visualization module (replacement for matplotlib/plotly/wordcloud).

Replaces visualization.py functions with AntV API calls to generate
professional charts matching our report style (academy theme).

API: https://antv-studio.alipay.com/api/gpt-vis
"""
import os
import json
import requests
import pandas as pd
from collections import Counter
from data_processing import filter_valid_countries

ANTV_API = "https://antv-studio.alipay.com/api/gpt-vis"


def _call_antv(payload):
    """Call AntV API and download the returned chart image."""
    payload["source"] = "chart-visualization-skills"
    try:
        resp = requests.post(ANTV_API, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("success") and data.get("resultObj"):
            return data["resultObj"]
    except Exception as e:
        print(f"AntV API call failed: {e}")
    return None


def _download_chart(url, save_path):
    """Download chart image from URL to local file."""
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(resp.content)
        print(f"Saved chart to {save_path}")
        return True
    except Exception as e:
        print(f"Failed to download chart: {e}")
        return False


def _generate(payload, save_path):
    """Build chart via AntV API and download."""
    url = _call_antv(payload)
    if url:
        return _download_chart(url, save_path)
    return False


# ============================================================
# Function signatures preserved from original visualization.py
# so main.py can swap with: from visualization_antv import ...
# ============================================================

def create_rating_pie_chart(df, brand_name, save_path):
    """Rating distribution pie chart (1-5 stars)."""
    rating_col = next((col for col in df.columns if col.lower() == "rating"), None)
    if rating_col is None or df.empty:
        print("No rating data available for pie chart")
        return

    df[rating_col] = pd.to_numeric(df[rating_col], errors="coerce")
    rating_counts = df[rating_col].dropna().astype(int).value_counts().sort_index()

    data = [
        {"category": f"{int(rating)}★", "value": int(count)}
        for rating, count in rating_counts.items()
    ]

    payload = {
        "type": "pie",
        "title": f"{brand_name} — Rating Distribution",
        "data": data,
        "theme": "academy",
        "width": 700,
        "height": 500,
    }
    _generate(payload, save_path)


def create_country_bar_chart(df, brand_name, save_path):
    """Review count by country bar chart."""
    df_valid = filter_valid_countries(df)
    if df_valid.empty:
        print("No country data available")
        return

    country_col = next(
        (col for col in df_valid.columns if col.lower() in ("country", "country_code")),
        None,
    )
    if country_col is None:
        return

    top_countries = df_valid[country_col].value_counts().head(15)

    data = [
        {"category": str(country), "value": int(count)}
        for country, count in top_countries.items()
    ]

    payload = {
        "type": "column",
        "title": f"{brand_name} — Reviews by Country (Top 15)",
        "data": data,
        "theme": "academy",
        "width": 800,
        "height": 500,
        "axisXTitle": "Country",
        "axisYTitle": "Review Count",
    }
    _generate(payload, save_path)


def create_country_treemap(df, brand_name, save_path):
    """Country distribution treemap."""
    df_valid = filter_valid_countries(df)
    if df_valid.empty:
        return

    country_col = next(
        (col for col in df_valid.columns if col.lower() in ("country", "country_code")),
        None,
    )
    if country_col is None:
        return

    country_counts = df_valid[country_col].value_counts()

    data = [
        {"name": str(country), "value": int(count)}
        for country, count in country_counts.items()
    ]

    payload = {
        "type": "treemap",
        "title": f"{brand_name} — Country Distribution",
        "data": data,
        "theme": "academy",
        "width": 800,
        "height": 500,
    }
    _generate(payload, save_path)


def generate_word_cloud(df, brand_name, save_path):
    """Word cloud from review text."""
    text_col = next(
        (col for col in df.columns if col.lower() in ("review", "content", "text", "body")),
        None,
    )
    if text_col is None or df.empty:
        return

    # Simple word frequency count
    text = " ".join(df[text_col].dropna().astype(str).str.lower().tolist())

    # Remove common stopwords
    stopwords = {
        "the", "and", "to", "a", "of", "i", "is", "for", "in", "it", "was",
        "this", "my", "have", "with", "on", "they", "are", "but", "you", "me",
        "so", "at", "not", "that", "had", "as", "all", "be", "or", "we",
        "just", "very", "get", "when", "an", "were", "would", "been", "has",
    }

    import re
    words = re.findall(r"\b[a-z]{3,}\b", text)
    word_counts = Counter(w for w in words if w not in stopwords)

    data = [
        {"text": word, "value": int(count)}
        for word, count in word_counts.most_common(100)
    ]

    payload = {
        "type": "word-cloud",
        "title": f"{brand_name} — Top Review Keywords",
        "data": data,
        "theme": "academy",
        "width": 800,
        "height": 500,
    }
    _generate(payload, save_path)


def generate_rating_word_clouds(df, brand_name, save_dir):
    """Separate word clouds for positive (4-5★) and negative (1-2★) reviews."""
    rating_col = next((col for col in df.columns if col.lower() == "rating"), None)
    text_col = next(
        (col for col in df.columns if col.lower() in ("review", "content", "text", "body")),
        None,
    )
    if rating_col is None or text_col is None or df.empty:
        return

    df[rating_col] = pd.to_numeric(df[rating_col], errors="coerce")
    os.makedirs(save_dir, exist_ok=True)

    for label, mask in [
        ("positive_4-5star", df[rating_col].isin([4, 5])),
        ("negative_1-2star", df[rating_col].isin([1, 2])),
    ]:
        subset = df[mask]
        if subset.empty:
            continue
        save_path = os.path.join(save_dir, f"{brand_name}_wordcloud_{label}.png")
        generate_word_cloud(subset, f"{brand_name} ({label})", save_path)


def analyze_combined_trends(df, brand_name, save_path):
    """Rating trend over time (line chart)."""
    date_col = next(
        (col for col in df.columns if col.lower() in ("date", "review_date", "created_at")),
        None,
    )
    rating_col = next((col for col in df.columns if col.lower() == "rating"), None)

    if date_col is None or rating_col is None or df.empty:
        print("Missing date or rating column for trend analysis")
        return

    df[rating_col] = pd.to_numeric(df[rating_col], errors="coerce")
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df_clean = df.dropna(subset=[date_col, rating_col])

    if df_clean.empty:
        return

    # Monthly average rating
    df_clean["month"] = df_clean[date_col].dt.to_period("M").astype(str)
    monthly = df_clean.groupby("month").agg(
        avg_rating=(rating_col, "mean"),
        count=(rating_col, "count"),
    ).reset_index()

    data = [
        {"time": row["month"], "value": round(row["avg_rating"], 2)}
        for _, row in monthly.iterrows()
    ]

    payload = {
        "type": "line",
        "title": f"{brand_name} — Monthly Average Rating Trend",
        "data": data,
        "theme": "academy",
        "width": 800,
        "height": 450,
        "axisXTitle": "Month",
        "axisYTitle": "Avg Rating",
    }
    _generate(payload, save_path)


def create_sentiment_distribution(df, brand_name, save_path):
    """Sentiment distribution bar chart (from sentiment analysis output)."""
    sentiment_col = next(
        (col for col in df.columns if col.lower() in ("sentiment", "sentiment_label")),
        None,
    )
    if sentiment_col is None or df.empty:
        return

    counts = df[sentiment_col].value_counts()
    data = [
        {"category": str(sentiment), "value": int(count)}
        for sentiment, count in counts.items()
    ]

    payload = {
        "type": "column",
        "title": f"{brand_name} — Sentiment Distribution",
        "data": data,
        "theme": "academy",
        "width": 700,
        "height": 450,
        "axisXTitle": "Sentiment",
        "axisYTitle": "Review Count",
    }
    _generate(payload, save_path)


def create_topic_bar_chart(topic_data, brand_name, save_path):
    """LDA topic modeling results bar chart."""
    if not topic_data:
        return

    data = [
        {"category": f"Topic {i+1}", "value": float(item.get("weight", 0))}
        for i, item in enumerate(topic_data)
    ]

    payload = {
        "type": "bar",
        "title": f"{brand_name} — LDA Topic Weights",
        "data": data,
        "theme": "academy",
        "width": 750,
        "height": 450,
        "axisXTitle": "Weight",
    }
    _generate(payload, save_path)


# Alias for backward compatibility with original visualization.py
def check_chinese_fonts():
    """Compatibility stub (AntV handles fonts server-side)."""
    return {"using_antv": True}
