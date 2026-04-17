# sentiment.py
from textblob import TextBlob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import string
from collections import Counter
from wordcloud import WordCloud, STOPWORDS

def analyze_sentiment(text):
    """情感分析"""
    try:
        analysis = TextBlob(str(text))
        polarity = analysis.sentiment.polarity
        if polarity < -0.1:
            sentiment_category = 'Negative'
        elif polarity > 0.1:
            sentiment_category = 'Positive'
        else:
            sentiment_category = 'Neutral'
        return polarity, sentiment_category
    except:
        return 0, 'Neutral'

def analyze_review_length_sentiment(df, brand_name, save_path):
    """分析评论长度与情感关系"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    if review_col is None or df.empty:
        print("No review data available")
        return
    
    valid_df = df.dropna(subset=[review_col])
    if valid_df.empty:
        print("No valid reviews")
        return
    
    valid_df['review_length'] = valid_df[review_col].astype(str).apply(len)
    if 'sentiment' not in valid_df.columns or 'sentiment_category' not in valid_df.columns:
        print("Adding sentiment analysis...")
        sentiments = []
        categories = []
        for review in valid_df[review_col]:
            polarity, category = analyze_sentiment(review)
            sentiments.append(polarity)
            categories.append(category)
        valid_df['sentiment'] = sentiments
        valid_df['sentiment_category'] = categories
    
    plt.figure(figsize=(14, 8))
    sns.boxplot(x='sentiment_category', y='review_length', data=valid_df, palette='Set3')
    sns.stripplot(x='sentiment_category', y='review_length', data=valid_df, 
                 size=4, color='.3', linewidth=0, alpha=0.3)
    
    plt.title(f'Review Length by Sentiment Category for {brand_name}', fontsize=16)
    plt.xlabel('Sentiment Category', fontsize=14)
    plt.ylabel('Review Length (characters)', fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    try:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved review length-sentiment boxplot to {save_path}")
    except Exception as e:
        print(f"Error saving boxplot: {e}")
    plt.close()
    
    plt.figure(figsize=(14, 8))
    plt.scatter(valid_df['review_length'], valid_df['sentiment'], 
                alpha=0.5, c=valid_df['sentiment'], cmap='RdYlGn', s=50)
    z = np.polyfit(valid_df['review_length'], valid_df['sentiment'], 1)
    p = np.poly1d(z)
    plt.plot(valid_df['review_length'], p(valid_df['review_length']), 
             "r--", linewidth=2, label=f"Trend line: y={z[0]:.6f}x+{z[1]:.2f}")
    correlation = valid_df['review_length'].corr(valid_df['sentiment'])
    
    plt.title(f'Sentiment vs Review Length for {brand_name} (Correlation: {correlation:.3f})', fontsize=16)
    plt.xlabel('Review Length (characters)', fontsize=14)
    plt.ylabel('Sentiment Polarity (-1 to 1)', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.colorbar(label='Sentiment Polarity')
    plt.legend()
    plt.tight_layout()
    
    scatter_path = save_path.replace('.png', '_scatter.png')
    try:
        plt.savefig(scatter_path, dpi=300, bbox_inches='tight')
        print(f"Saved review length-sentiment scatter plot to {scatter_path}")
    except Exception as e:
        print(f"Error saving scatter plot: {e}")
    plt.close()
    
    length_bins = [0, 100, 200, 300, 500, 1000, np.inf]
    length_labels = ['0-100', '101-200', '201-300', '301-500', '501-1000', '1000+']
    valid_df['length_category'] = pd.cut(valid_df['review_length'], bins=length_bins, labels=length_labels)
    
    length_sentiment = valid_df.groupby('length_category').agg({
        'sentiment': ['mean', 'median', 'count'],
        'review_length': ['mean', 'median']
    }).reset_index()
    
    data_file = save_path.replace('.png', '_data.csv')
    length_sentiment.to_csv(data_file, index=False)
    print(f"Saved review length-sentiment analysis data to {data_file}")
    
    plt.figure(figsize=(14, 8))
    mean_sentiments = length_sentiment['sentiment']['mean'].values
    colors = ['red' if s < -0.1 else 'green' if s > 0.1 else 'gray' for s in mean_sentiments]
    
    bars = plt.bar(length_labels, mean_sentiments, color=colors)
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01 if height >= 0 else height - 0.03,
                 f'{height:.3f}', ha='center', va='bottom' if height >= 0 else 'top', fontsize=12)
    
    plt.title(f'Average Sentiment by Review Length for {brand_name}', fontsize=16)
    plt.xlabel('Review Length Category', fontsize=14)
    plt.ylabel('Average Sentiment Polarity (-1 to 1)', fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.tight_layout()
    
    bar_chart_path = save_path.replace('.png', '_bar.png')
    try:
        plt.savefig(bar_chart_path, dpi=300, bbox_inches='tight')
        print(f"Saved review length-sentiment bar chart to {bar_chart_path}")
    except Exception as e:
        print(f"Error saving bar chart: {e}")
    plt.close()
    
    return valid_df

def analyze_word_sentiment_correlation(df, brand_name, save_path, top_n=30):
    """分析高频词情感倾向"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    if review_col is None or df.empty:
        print("No review data available")
        return
    
    if 'sentiment' not in df.columns or 'sentiment_category' not in df.columns:
        print("Adding sentiment analysis...")
        sentiments = []
        categories = []
        for review in df[review_col]:
            polarity, category = analyze_sentiment(review)
            sentiments.append(polarity)
            categories.append(category)
        df['sentiment'] = sentiments
        df['sentiment_category'] = categories
    
    all_words = []
    stopwords = set(STOPWORDS)
    custom_stopwords = {
        'the', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'with', 'for', 'on', 'is', 'was', 'be',
        'this', 'have', 'from', 'or', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'there', 'can', 'an', 'your', 'which', 'their', 'said', 'if', 'will', 'my', 'one',
        'would', 'so', 'up', 'out', 'them', 'about', 'who', 'get', 'me', 'been', 'has', 'just',
        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
        'received', 'bought', 'purchase', 'purchased', 'buy', 'use', 'used', 'using'
    }
    stopwords.update(custom_stopwords)
    
    for review in df[review_col]:
        text = str(review).lower()
        for p in string.punctuation:
            text = text.replace(p, ' ')
        words = text.split()
        filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
        all_words.extend(filtered_words)
    
    word_counts = Counter(all_words)
    top_words = [word for word, _ in word_counts.most_common(top_n)]
    
    word_sentiment_data = []
    for word in top_words:
        for sentiment in ['Positive', 'Neutral', 'Negative']:
            sentiment_df = df[df['sentiment_category'] == sentiment]
            contains_word = sentiment_df[review_col].str.contains(r'\b' + word + r'\b', case=False, regex=True)
            count = contains_word.sum()
            avg_sentiment = sentiment_df.loc[contains_word, 'sentiment'].mean() if count > 0 else 0
            word_sentiment_data.append({
                'Word': word,
                'Sentiment_Category': sentiment,
                'Count': count,
                'Average_Sentiment': avg_sentiment
            })
    
    word_sentiment_df = pd.DataFrame(word_sentiment_data)
    
    plt.figure(figsize=(16, 12))
    pivot_df = word_sentiment_df.pivot(index='Word', columns='Sentiment_Category', values='Count')
    pivot_df['Total'] = pivot_df.sum(axis=1)
    pivot_df = pivot_df.sort_values('Total', ascending=False).drop('Total', axis=1)
    
    sns.heatmap(pivot_df, annot=True, cmap='YlGnBu', fmt='g', linewidths=.5)
    plt.title(f'Word Frequency by Sentiment Category for {brand_name}', fontsize=16)
    plt.xlabel('Sentiment Category', fontsize=12)
    plt.ylabel('Word', fontsize=12)
    plt.tight_layout()
    
    try:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved word-sentiment correlation heatmap to {save_path}")
    except Exception as e:
        print(f"Error saving heatmap: {e}")
    plt.close()
    
    data_file = save_path.replace('.png', '_data.csv')
    word_sentiment_df.to_csv(data_file, index=False)
    print(f"Saved word-sentiment correlation data to {data_file}")

def analyze_time_series_sentiment(df, brand_name, save_path):
    """分析情感随时间变化"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    date_col = next((col for col in df.columns if col.lower() == 'date'), None)
    if review_col is None or date_col is None or df.empty:
        print("Missing required columns")
        return
    
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    valid_df = df.dropna(subset=[date_col, review_col])
    if valid_df.empty:
        print("No valid data")
        return
    
    if 'sentiment' not in valid_df.columns or 'sentiment_category' not in valid_df.columns:
        print("Adding sentiment analysis...")
        sentiments = []
        categories = []
        for review in valid_df[review_col]:
            polarity, category = analyze_sentiment(review)
            sentiments.append(polarity)
            categories.append(category)
        valid_df['sentiment'] = sentiments
        valid_df['sentiment_category'] = categories
    
    valid_df['month'] = valid_df[date_col].dt.to_period('M')
    monthly_sentiment = valid_df.groupby(['month', 'sentiment_category']).size().unstack(fill_value=0)
    for category in ['Positive', 'Neutral', 'Negative']:
        if category not in monthly_sentiment.columns:
            monthly_sentiment[category] = 0
    
    monthly_avg_sentiment = valid_df.groupby('month')['sentiment'].mean()
    monthly_sentiment.index = monthly_sentiment.index.to_timestamp()
    monthly_avg_sentiment.index = monthly_avg_sentiment.index.to_timestamp()
    
    fig, ax1 = plt.subplots(figsize=(16, 8))
    ax1.plot(monthly_sentiment.index, monthly_sentiment['Positive'], 'g-', marker='o', linewidth=2, label='Positive')
    ax1.plot(monthly_sentiment.index, monthly_sentiment['Neutral'], 'b-', marker='s', linewidth=2, label='Neutral')
    ax1.plot(monthly_sentiment.index, monthly_sentiment['Negative'], 'r-', marker='x', linewidth=2, label='Negative')
    
    ax1.set_title(f'Sentiment Trends Over Time for {brand_name}', fontsize=16)
    ax1.set_xlabel('Date', fontsize=14)
    ax1.set_ylabel('Number of Reviews', fontsize=14)
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend(loc='upper left')
    
    ax2 = ax1.twinx()
    ax2.plot(monthly_avg_sentiment.index, monthly_avg_sentiment.values, 'k--', linewidth=2, label='Avg Sentiment')
    ax2.set_ylabel('Average Sentiment Polarity (-1 to 1)', fontsize=14)
    ax2.legend(loc='upper right')
    
    plt.tight_layout()
    try:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved time series sentiment chart to {save_path}")
    except Exception as e:
        print(f"Error saving chart: {e}")
    plt.close()
    
    data_file = save_path.replace('.png', '_data.csv')
    monthly_sentiment['avg_sentiment'] = monthly_avg_sentiment
    monthly_sentiment['total_reviews'] = monthly_sentiment['Positive'] + monthly_sentiment['Neutral'] + monthly_sentiment['Negative']
    for category in ['Positive', 'Neutral', 'Negative']:
        monthly_sentiment[f'{category.lower()}_percent'] = (monthly_sentiment[category] / monthly_sentiment['total_reviews'] * 100).round(2)
    monthly_sentiment.to_csv(data_file)
    print(f"Saved time series sentiment data to {data_file}")
    
    plt.figure(figsize=(16, 8))
    plt.stackplot(monthly_sentiment.index, 
                 monthly_sentiment['Positive'], 
                 monthly_sentiment['Neutral'], 
                 monthly_sentiment['Negative'],
                 labels=['Positive', 'Neutral', 'Negative'],
                 colors=['green', 'gray', 'red'],
                 alpha=0.7)
    plt.title(f'Sentiment Composition Over Time for {brand_name}', fontsize=16)
    plt.xlabel('Date', fontsize=14)
    plt.ylabel('Number of Reviews', fontsize=14)
    plt.tick_params(axis='x', rotation=45)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper left')
    plt.tight_layout()
    
    area_chart_path = save_path.replace('.png', '_area.png')
    try:
        plt.savefig(area_chart_path, dpi=300, bbox_inches='tight')
        print(f"Saved time series sentiment area chart to {area_chart_path}")
    except Exception as e:
        print(f"Error saving area chart: {e}")
    plt.close()
    
    return valid_df