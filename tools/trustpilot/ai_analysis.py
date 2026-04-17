# ai_analysis.py
import os
import requests
import json
import pandas as pd
import numpy as np
import concurrent.futures
import time
import tqdm

# API key loaded from environment variable — set OPENROUTER_API_KEY before running
API_BASE_URL = os.environ.get("LLM_API_BASE", "https://openrouter.ai/api/v1/chat/completions")
API_KEY = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("LLM_API_KEY", "")

if not API_KEY:
    print("WARNING: No API key found. Set OPENROUTER_API_KEY or LLM_API_KEY environment variable.")
    print("AI analysis will be skipped if called.")

def call_ai_model(prompt):
    """调用OpenRouter API的大模型"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "trustpilot_analysis",  # 可选，用于OpenRouter排名
        "X-Title": "Trustpilot Analysis"  # 可选，用于OpenRouter排名
    }
    
    data = {
        "model": "qwen/qwq-32b",  # 使用指定的模型
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(API_BASE_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error calling AI model: {e}")
        return None
        
def call_ai_model_concurrent(prompts):
    """并发调用AI模型处理多个提示"""
    if not prompts:
        return []
    
    print(f"并发处理{len(prompts)}个AI请求...")
    
    def call_with_retry(prompt, max_retries=3):
        for attempt in range(max_retries):
            try:
                result = call_ai_model(prompt)
                return result
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避策略
                    print(f"请求失败，{wait_time}秒后重试: {e}")
                    time.sleep(wait_time)
                else:
                    print(f"所有重试失败: {e}")
                    return None
    
    results = []
    # 增加并发数量，从5增加到16
    max_workers = min(16, len(prompts))
    print(f"使用{max_workers}个并发线程处理请求...")
    
    # 使用tqdm创建进度条
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_prompt = {executor.submit(call_with_retry, prompt): i for i, prompt in enumerate(prompts)}
        
        # 添加进度条，显示更详细的信息
        for future in tqdm.tqdm(concurrent.futures.as_completed(future_to_prompt), 
                               total=len(prompts), 
                               desc="AI分析进度",
                               bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'):
            idx = future_to_prompt[future]
            try:
                result = future.result()
                results.append((idx, result))
                print(f"完成第{idx+1}/{len(prompts)}个分析任务")
            except Exception as e:
                print(f"处理请求时出错: {e}")
                results.append((idx, None))
    
    # 按原始顺序排序结果
    results.sort(key=lambda x: x[0])
    return [r[1] for r in results]

def analyze_rating_distribution(df, brand_name):
    """分析评分分布"""
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    if rating_col is None:
        return None
        
    rating_counts = df[rating_col].value_counts().sort_index()
    total_reviews = len(df)
    
    # 计算高分和低分的比例
    high_ratings = rating_counts.get(4, 0) + rating_counts.get(5, 0)
    low_ratings = rating_counts.get(1, 0) + rating_counts.get(2, 0)
    high_percentage = high_ratings / total_reviews * 100
    low_percentage = low_ratings / total_reviews * 100
    
    prompt = f"""分析以下{brand_name}的评分分布数据：
    总评论数：{total_reviews}
    1星评分：{rating_counts.get(1, 0)}条 ({rating_counts.get(1, 0)/total_reviews*100:.1f}%)
    2星评分：{rating_counts.get(2, 0)}条 ({rating_counts.get(2, 0)/total_reviews*100:.1f}%)
    3星评分：{rating_counts.get(3, 0)}条 ({rating_counts.get(3, 0)/total_reviews*100:.1f}%)
    4星评分：{rating_counts.get(4, 0)}条 ({rating_counts.get(4, 0)/total_reviews*100:.1f}%)
    5星评分：{rating_counts.get(5, 0)}条 ({rating_counts.get(5, 0)/total_reviews*100:.1f}%)
    高分(4-5星)比例：{high_percentage:.1f}%
    低分(1-2星)比例：{low_percentage:.1f}%
    
    请深入分析这个评分分布的特点，包括：
    1. 评分的整体趋势和分布特点
    2. 高分评价反映的品牌主要优势
    3. 低分评价反映的品牌主要问题
    4. 用户满意度水平及其影响因素
    5. 评分分布对品牌声誉的影响
    6. 针对低分评价，品牌应该重点改进的方向
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面。"""
    
    return call_ai_model(prompt)

def analyze_country_distribution(df, brand_name):
    """分析国家分布"""
    country_col = next((col for col in df.columns if col.lower() == 'country'), None)
    if country_col is None:
        return None
        
    country_counts = df[country_col].value_counts()
    total_reviews = len(df)
    top_countries = country_counts.head(5)
    
    # 计算前5个国家的评论占比
    top5_percentage = sum(top_countries) / total_reviews * 100
    
    # 尝试分析各国家的评分和情感情况
    country_analysis = ""
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    sentiment_col = 'sentiment_category'
    
    if rating_col and country_col:
        # 获取各国家的平均评分
        country_ratings = df.groupby(country_col)[rating_col].mean().sort_values(ascending=False)
        top_rated_countries = country_ratings.head(3)
        bottom_rated_countries = country_ratings.tail(3)
        
        country_analysis += f"\n    评分最高的3个国家：\n"
        for country, rating in top_rated_countries.items():
            country_analysis += f"    {country}: {rating:.2f}星 (评论数: {country_counts.get(country, 0)}条)\n"
            
        country_analysis += f"\n    评分最低的3个国家：\n"
        for country, rating in bottom_rated_countries.items():
            country_analysis += f"    {country}: {rating:.2f}星 (评论数: {country_counts.get(country, 0)}条)\n"
    
    prompt = f"""分析以下{brand_name}的评论国家分布数据：
    总评论数：{total_reviews}
    前5个国家的分布：
    {', '.join([f'{country}: {count}条 ({count/total_reviews*100:.1f}%)' for country, count in top_countries.items()])}
    前5个国家评论占比：{top5_percentage:.1f}%{country_analysis}
    
    请深入分析这个地理分布的特点，包括：
    1. 用户群体的地理集中度和品牌的国际化程度
    2. 主要市场区域的特点和用户满意度
    3. 不同国家/地区用户反馈的差异性
    4. 品牌在哪些国家/地区表现最好，可能的原因是什么
    5. 品牌在哪些国家/地区面临挑战，需要重点改进的方面
    6. 基于地理分布，品牌的市场拓展策略建议
    
    请用简洁的语言总结分析结果，重点突出品牌在不同地区的优势和劣势，并给出针对性的市场策略建议。"""
    
    return call_ai_model(prompt)

def analyze_sentiment_trends(df, brand_name):
    """分析情感趋势"""
    sentiment_col = 'sentiment_category'
    if sentiment_col not in df.columns:
        return None
        
    sentiment_counts = df[sentiment_col].value_counts()
    total_reviews = len(df)
    
    # 计算正面和负面评价的比例
    positive_percentage = sentiment_counts.get('Positive', 0) / total_reviews * 100
    negative_percentage = sentiment_counts.get('Negative', 0) / total_reviews * 100
    neutral_percentage = sentiment_counts.get('Neutral', 0) / total_reviews * 100
    
    # 提取高分和低分评论的样本
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    if review_col:
        positive_samples = df[df[sentiment_col] == 'Positive'][review_col].sample(min(3, sentiment_counts.get('Positive', 0))).tolist()
        negative_samples = df[df[sentiment_col] == 'Negative'][review_col].sample(min(3, sentiment_counts.get('Negative', 0))).tolist()
        
        positive_examples = "\n".join([f"- {sample[:100]}..." for sample in positive_samples])
        negative_examples = "\n".join([f"- {sample[:100]}..." for sample in negative_samples])
    else:
        positive_examples = "无样本数据"
        negative_examples = "无样本数据"
    
    prompt = f"""分析以下{brand_name}的评论情感分布数据：
    总评论数：{total_reviews}
    正面评价：{sentiment_counts.get('Positive', 0)}条 ({positive_percentage:.1f}%)
    中性评价：{sentiment_counts.get('Neutral', 0)}条 ({neutral_percentage:.1f}%)
    负面评价：{sentiment_counts.get('Negative', 0)}条 ({negative_percentage:.1f}%)
    
    正面评价样本：
{positive_examples}
    
    负面评价样本：
{negative_examples}
    
    请深入分析这个情感分布的特点，包括：
    1. 整体情感倾向和用户满意度水平
    2. 正面评价中反映的品牌主要优势和亮点
    3. 负面评价中反映的品牌主要问题和痛点
    4. 用户投诉的主要焦点和表扬的核心方面
    5. 情感极化现象分析（如果存在）
    6. 针对负面情感，品牌应该采取的改进措施
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面。"""
    
    return call_ai_model(prompt)

def analyze_word_cloud(df, brand_name):
    """分析词云数据"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    sentiment_col = 'sentiment_category'
    if review_col is None:
        return None
        
    # 分别提取正面和负面评论中的关键词
    all_text = ' '.join(df[review_col].dropna().astype(str))
    
    # 设置停用词
    from wordcloud import STOPWORDS
    import string
    stopwords = set(STOPWORDS)
    custom_stopwords = {
        # 英文常见停用词
        'the', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'with', 'for', 'on', 'is', 'was', 'be',
        'this', 'have', 'from', 'or', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'there', 'can', 'an', 'your', 'which', 'their', 'said', 'if', 'will', 'my', 'one',
        'would', 'so', 'up', 'out', 'them', 'about', 'who', 'get', 'me', 'been', 'has', 'just',
        'do', 'did', 'doing', 'does', 'then', 'such', 'no', 'yes', 'they', 'also', 'any', 'are',
        
        # 品牌和产品相关词
        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
        
        # 电商常见词
        'shipping', 'delivery', 'arrived', 'package', 'item', 'items', 'customer', 'customers',
        'review', 'reviews', 'rating', 'ratings', 'star', 'stars', 'experience'
    }
    stopwords.update(custom_stopwords)
    
    # 处理文本，移除标点符号和停用词
    text = all_text.lower()
    for p in string.punctuation:
        text = text.replace(p, ' ')
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
    
    # 获取总体词频
    word_freq = pd.Series(filtered_words).value_counts().head(15)
    
    # 如果有情感分类列，分别提取正面和负面评论的关键词
    pos_word_freq = None
    neg_word_freq = None
    if sentiment_col in df.columns:
        pos_reviews = ' '.join(df[df[sentiment_col] == 'Positive'][review_col].dropna().astype(str))
        neg_reviews = ' '.join(df[df[sentiment_col] == 'Negative'][review_col].dropna().astype(str))
        
        # 处理正面评论文本
        pos_text = pos_reviews.lower()
        for p in string.punctuation:
            pos_text = pos_text.replace(p, ' ')
        pos_words = pos_text.split()
        pos_filtered = [word for word in pos_words if word not in stopwords and len(word) > 2]
        pos_word_freq = pd.Series(pos_filtered).value_counts().head(10)
        
        # 处理负面评论文本
        neg_text = neg_reviews.lower()
        for p in string.punctuation:
            neg_text = neg_text.replace(p, ' ')
        neg_words = neg_text.split()
        neg_filtered = [word for word in neg_words if word not in stopwords and len(word) > 2]
        neg_word_freq = pd.Series(neg_filtered).value_counts().head(10)
    
    # 构建提示词
    prompt = f"""分析以下{brand_name}的评论关键词数据：
    
    总体最常见的15个关键词及其出现次数：
    {', '.join([f'{word}: {count}次' for word, count in word_freq.items()])}
    """
    
    # 添加正面评论关键词
    if pos_word_freq is not None and len(pos_word_freq) > 0:
        prompt += f"""
    
    正面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in pos_word_freq.items()])}
    """
    
    # 添加负面评论关键词
    if neg_word_freq is not None and len(neg_word_freq) > 0:
        prompt += f"""
    
    负面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in neg_word_freq.items()])}
    """
    
    prompt += f"""
    
    请深入分析这些关键词的特点，包括：
    1. 用户最关注的产品/服务方面
    2. 正面评价中反映的品牌主要优势和特色
    3. 负面评价中反映的品牌主要问题和痛点
    4. 关键词与具体业务场景的关联（如产品质量、客户服务、物流配送等）
    5. 品牌应该重点改进的方面
    6. 品牌可以继续保持和强化的优势
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面，并给出具体可行的改进建议。"""
    
    return call_ai_model(prompt)

def analyze_time_trends(df, brand_name):
    """分析时间趋势"""
    date_col = next((col for col in df.columns if col.lower() == 'date'), None)
    if date_col is None:
        return None
        
    df['date'] = pd.to_datetime(df[date_col])
    monthly_counts = df.groupby(df['date'].dt.to_period('M')).size()
    
    if len(monthly_counts) <= 1:
        return None
    
    trend = 'increasing' if monthly_counts.iloc[-1] > monthly_counts.iloc[0] else 'decreasing'
    avg_monthly = monthly_counts.mean()
    max_month = monthly_counts.idxmax()
    min_month = monthly_counts.idxmin()
    
    # 分析评分随时间的变化趋势
    rating_trend = ""
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    if rating_col:
        # 计算每月平均评分
        monthly_ratings = df.groupby(df['date'].dt.to_period('M'))[rating_col].mean()
        if len(monthly_ratings) > 1:
            rating_trend = 'improving' if monthly_ratings.iloc[-1] > monthly_ratings.iloc[0] else 'declining'
            rating_trend = f"\n    评分趋势：{rating_trend}"
            rating_trend += f"\n    初始月份平均评分：{monthly_ratings.iloc[0]:.2f}星"
            rating_trend += f"\n    最近月份平均评分：{monthly_ratings.iloc[-1]:.2f}星"
    
    # 分析情感随时间的变化趋势
    sentiment_trend = ""
    sentiment_col = 'sentiment'
    if sentiment_col in df.columns:
        # 计算每月平均情感得分
        monthly_sentiment = df.groupby(df['date'].dt.to_period('M'))[sentiment_col].mean()
        if len(monthly_sentiment) > 1:
            sentiment_trend = 'improving' if monthly_sentiment.iloc[-1] > monthly_sentiment.iloc[0] else 'declining'
            sentiment_trend = f"\n    情感趋势：{sentiment_trend}"
            sentiment_trend += f"\n    初始月份平均情感得分：{monthly_sentiment.iloc[0]:.3f}"
            sentiment_trend += f"\n    最近月份平均情感得分：{monthly_sentiment.iloc[-1]:.3f}"
    
    prompt = f"""分析以下{brand_name}的评论时间趋势数据：
    评论数量趋势：{trend}
    平均每月评论数：{avg_monthly:.1f}
    评论最多的月份：{max_month}（{monthly_counts[max_month]}条）
    评论最少的月份：{min_month}（{monthly_counts[min_month]}条）{rating_trend}{sentiment_trend}
    
    请深入分析这个时间趋势的特点，包括：
    1. 品牌影响力随时间的变化趋势
    2. 用户满意度随时间的变化趋势
    3. 季节性波动及其可能的原因
    4. 高峰期和低谷期的特点及其与品牌活动的关联
    5. 品牌表现是否在改善或恶化，以及可能的原因
    6. 基于时间趋势，品牌应该采取的策略调整
    
    请用简洁的语言总结分析结果，重点突出品牌随时间变化的优势和劣势，并给出针对性的发展趋势建议。"""
    
    return call_ai_model(prompt)

def generate_comprehensive_analysis(df, brand_name):
    """生成综合分析报告"""
    analyses = {
        'rating': analyze_rating_distribution(df, brand_name),
        'country': analyze_country_distribution(df, brand_name),
        'sentiment': analyze_sentiment_trends(df, brand_name),
        'keywords': analyze_word_cloud(df, brand_name),
        'time': analyze_time_trends(df, brand_name)
    }
    
    # 过滤掉None值
    valid_analyses = {k: v for k, v in analyses.items() if v is not None}
    
    prompt = f"""基于以下{brand_name}的各个维度分析结果，生成一个全面深入的综合分析报告：

{json.dumps(valid_analyses, ensure_ascii=False, indent=2)}

请系统性地总结以下几个方面：

1. 品牌整体表现评估
   - 总体用户满意度水平
   - 品牌在市场中的定位和影响力
   - 品牌声誉的总体状况

2. 品牌核心优势（至少3-5点）
   - 具体列出品牌最突出的优势
   - 每个优势的具体表现和影响
   - 这些优势如何为品牌创造竞争力
   - 如何进一步强化这些优势

3. 品牌主要劣势和问题（至少3-5点）
   - 具体列出品牌最突出的问题和劣势
   - 每个问题的具体表现和影响
   - 这些问题如何影响用户体验和品牌声誉
   - 问题的严重程度和优先级排序

4. 具体可行的改进建议（至少5点）
   - 针对每个主要问题提出具体的改进措施
   - 建议的实施优先级和预期效果
   - 短期可立即实施的改进措施
   - 长期需要战略性调整的改进方向

5. 市场机会和发展方向
   - 基于用户反馈的潜在市场机会
   - 品牌可以拓展的新领域或新市场
   - 与竞争对手差异化的关键点

请用简洁专业的语言输出分析结果，确保分析具有可操作性和实用价值，能够直接指导品牌改进和发展策略。"""
    
    return call_ai_model(prompt)

def analyze_sentiment_trends(df, brand_name):
    """分析情感趋势"""
    sentiment_col = 'sentiment_category'
    if sentiment_col not in df.columns:
        return None
        
    sentiment_counts = df[sentiment_col].value_counts()
    total_reviews = len(df)
    
    # 计算正面和负面评价的比例
    positive_percentage = sentiment_counts.get('Positive', 0) / total_reviews * 100
    negative_percentage = sentiment_counts.get('Negative', 0) / total_reviews * 100
    neutral_percentage = sentiment_counts.get('Neutral', 0) / total_reviews * 100
    
    # 提取高分和低分评论的样本
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    if review_col:
        positive_samples = df[df[sentiment_col] == 'Positive'][review_col].sample(min(3, sentiment_counts.get('Positive', 0))).tolist()
        negative_samples = df[df[sentiment_col] == 'Negative'][review_col].sample(min(3, sentiment_counts.get('Negative', 0))).tolist()
        
        positive_examples = "\n".join([f"- {sample[:100]}..." for sample in positive_samples])
        negative_examples = "\n".join([f"- {sample[:100]}..." for sample in negative_samples])
    else:
        positive_examples = "无样本数据"
        negative_examples = "无样本数据"
    
    prompt = f"""分析以下{brand_name}的评论情感分布数据：
    总评论数：{total_reviews}
    正面评价：{sentiment_counts.get('Positive', 0)}条 ({positive_percentage:.1f}%)
    中性评价：{sentiment_counts.get('Neutral', 0)}条 ({neutral_percentage:.1f}%)
    负面评价：{sentiment_counts.get('Negative', 0)}条 ({negative_percentage:.1f}%)
    
    正面评价样本：
{positive_examples}
    
    负面评价样本：
{negative_examples}
    
    请深入分析这个情感分布的特点，包括：
    1. 整体情感倾向和用户满意度水平
    2. 正面评价中反映的品牌主要优势和亮点
    3. 负面评价中反映的品牌主要问题和痛点
    4. 用户投诉的主要焦点和表扬的核心方面
    5. 情感极化现象分析（如果存在）
    6. 针对负面情感，品牌应该采取的改进措施
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面。"""
    
    return call_ai_model(prompt)

def analyze_word_cloud(df, brand_name):
    """分析词云数据"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    sentiment_col = 'sentiment_category'
    if review_col is None:
        return None
        
    # 分别提取正面和负面评论中的关键词
    all_text = ' '.join(df[review_col].dropna().astype(str))
    
    # 设置停用词
    from wordcloud import STOPWORDS
    import string
    stopwords = set(STOPWORDS)
    custom_stopwords = {
        # 英文常见停用词
        'the', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'with', 'for', 'on', 'is', 'was', 'be',
        'this', 'have', 'from', 'or', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'there', 'can', 'an', 'your', 'which', 'their', 'said', 'if', 'will', 'my', 'one',
        'would', 'so', 'up', 'out', 'them', 'about', 'who', 'get', 'me', 'been', 'has', 'just',
        'do', 'did', 'doing', 'does', 'then', 'such', 'no', 'yes', 'they', 'also', 'any', 'are',
        
        # 品牌和产品相关词
        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
        
        # 电商常见词
        'shipping', 'delivery', 'arrived', 'package', 'item', 'items', 'customer', 'customers',
        'review', 'reviews', 'rating', 'ratings', 'star', 'stars', 'experience'
    }
    stopwords.update(custom_stopwords)
    
    # 处理文本，移除标点符号和停用词
    text = all_text.lower()
    for p in string.punctuation:
        text = text.replace(p, ' ')
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
    
    # 获取总体词频
    word_freq = pd.Series(filtered_words).value_counts().head(15)
    
    # 如果有情感分类列，分别提取正面和负面评论的关键词
    pos_word_freq = None
    neg_word_freq = None
    if sentiment_col in df.columns:
        pos_reviews = ' '.join(df[df[sentiment_col] == 'Positive'][review_col].dropna().astype(str))
        neg_reviews = ' '.join(df[df[sentiment_col] == 'Negative'][review_col].dropna().astype(str))
        
        # 处理正面评论文本
        pos_text = pos_reviews.lower()
        for p in string.punctuation:
            pos_text = pos_text.replace(p, ' ')
        pos_words = pos_text.split()
        pos_filtered = [word for word in pos_words if word not in stopwords and len(word) > 2]
        pos_word_freq = pd.Series(pos_filtered).value_counts().head(10)
        
        # 处理负面评论文本
        neg_text = neg_reviews.lower()
        for p in string.punctuation:
            neg_text = neg_text.replace(p, ' ')
        neg_words = neg_text.split()
        neg_filtered = [word for word in neg_words if word not in stopwords and len(word) > 2]
        neg_word_freq = pd.Series(neg_filtered).value_counts().head(10)
    
    # 构建提示词
    prompt = f"""分析以下{brand_name}的评论关键词数据：
    
    总体最常见的15个关键词及其出现次数：
    {', '.join([f'{word}: {count}次' for word, count in word_freq.items()])}
    """
    
    # 添加正面评论关键词
    if pos_word_freq is not None and len(pos_word_freq) > 0:
        prompt += f"""
    
    正面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in pos_word_freq.items()])}
    """
    
    # 添加负面评论关键词
    if neg_word_freq is not None and len(neg_word_freq) > 0:
        prompt += f"""
    
    负面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in neg_word_freq.items()])}
    """
    
    prompt += f"""
    
    请深入分析这些关键词的特点，包括：
    1. 用户最关注的产品/服务方面
    2. 正面评价中反映的品牌主要优势和特色
    3. 负面评价中反映的品牌主要问题和痛点
    4. 关键词与具体业务场景的关联（如产品质量、客户服务、物流配送等）
    5. 品牌应该重点改进的方面
    6. 品牌可以继续保持和强化的优势
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面，并给出具体可行的改进建议。"""
    
    return call_ai_model(prompt)

def analyze_time_trends(df, brand_name):
    """分析时间趋势"""
    date_col = next((col for col in df.columns if col.lower() == 'date'), None)
    if date_col is None:
        return None
        
    df['date'] = pd.to_datetime(df[date_col])
    monthly_counts = df.groupby(df['date'].dt.to_period('M')).size()
    
    if len(monthly_counts) <= 1:
        return None
    
    trend = 'increasing' if monthly_counts.iloc[-1] > monthly_counts.iloc[0] else 'decreasing'
    avg_monthly = monthly_counts.mean()
    max_month = monthly_counts.idxmax()
    min_month = monthly_counts.idxmin()
    
    # 分析评分随时间的变化趋势
    rating_trend = ""
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    if rating_col:
        # 计算每月平均评分
        monthly_ratings = df.groupby(df['date'].dt.to_period('M'))[rating_col].mean()
        if len(monthly_ratings) > 1:
            rating_trend = 'improving' if monthly_ratings.iloc[-1] > monthly_ratings.iloc[0] else 'declining'
            rating_trend = f"\n    评分趋势：{rating_trend}"
            rating_trend += f"\n    初始月份平均评分：{monthly_ratings.iloc[0]:.2f}星"
            rating_trend += f"\n    最近月份平均评分：{monthly_ratings.iloc[-1]:.2f}星"
    
    # 分析情感随时间的变化趋势
    sentiment_trend = ""
    sentiment_col = 'sentiment'
    if sentiment_col in df.columns:
        # 计算每月平均情感得分
        monthly_sentiment = df.groupby(df['date'].dt.to_period('M'))[sentiment_col].mean()
        if len(monthly_sentiment) > 1:
            sentiment_trend = 'improving' if monthly_sentiment.iloc[-1] > monthly_sentiment.iloc[0] else 'declining'
            sentiment_trend = f"\n    情感趋势：{sentiment_trend}"
            sentiment_trend += f"\n    初始月份平均情感得分：{monthly_sentiment.iloc[0]:.3f}"
            sentiment_trend += f"\n    最近月份平均情感得分：{monthly_sentiment.iloc[-1]:.3f}"
    
    prompt = f"""分析以下{brand_name}的评论时间趋势数据：
    评论数量趋势：{trend}
    平均每月评论数：{avg_monthly:.1f}
    评论最多的月份：{max_month}（{monthly_counts[max_month]}条）
    评论最少的月份：{min_month}（{monthly_counts[min_month]}条）{rating_trend}{sentiment_trend}
    
    请深入分析这个时间趋势的特点，包括：
    1. 品牌影响力随时间的变化趋势
    2. 用户满意度随时间的变化趋势
    3. 季节性波动及其可能的原因
    4. 高峰期和低谷期的特点及其与品牌活动的关联
    5. 品牌表现是否在改善或恶化，以及可能的原因
    6. 基于时间趋势，品牌应该采取的策略调整
    
    请用简洁的语言总结分析结果，重点突出品牌随时间变化的优势和劣势，并给出针对性的发展趋势建议。"""
    
    return call_ai_model(prompt)

def generate_comprehensive_analysis(df, brand_name):
    """生成综合分析报告"""
    analyses = {
        'rating': analyze_rating_distribution(df, brand_name),
        'country': analyze_country_distribution(df, brand_name),
        'sentiment': analyze_sentiment_trends(df, brand_name),
        'keywords': analyze_word_cloud(df, brand_name),
        'time': analyze_time_trends(df, brand_name)
    }
    
    # 过滤掉None值
    valid_analyses = {k: v for k, v in analyses.items() if v is not None}
    
    prompt = f"""基于以下{brand_name}的各个维度分析结果，生成一个全面深入的综合分析报告：

{json.dumps(valid_analyses, ensure_ascii=False, indent=2)}

请系统性地总结以下几个方面：

1. 品牌整体表现评估
   - 总体用户满意度水平
   - 品牌在市场中的定位和影响力
   - 品牌声誉的总体状况

2. 品牌核心优势（至少3-5点）
   - 具体列出品牌最突出的优势
   - 每个优势的具体表现和影响
   - 这些优势如何为品牌创造竞争力
   - 如何进一步强化这些优势

3. 品牌主要劣势和问题（至少3-5点）
   - 具体列出品牌最突出的问题和劣势
   - 每个问题的具体表现和影响
   - 这些问题如何影响用户体验和品牌声誉
   - 问题的严重程度和优先级排序

4. 具体可行的改进建议（至少5点）
   - 针对每个主要问题提出具体的改进措施
   - 建议的实施优先级和预期效果
   - 短期可立即实施的改进措施
   - 长期需要战略性调整的改进方向

5. 市场机会和发展方向
   - 基于用户反馈的潜在市场机会
   - 品牌可以拓展的新领域或新市场
   - 与竞争对手差异化的关键点

请用简洁专业的语言输出分析结果，确保分析具有可操作性和实用价值，能够直接指导品牌改进和发展策略。"""
    
    return call_ai_model(prompt)

def analyze_sentiment_trends(df, brand_name):
    """分析情感趋势"""
    sentiment_col = 'sentiment_category'
    if sentiment_col not in df.columns:
        return None
        
    sentiment_counts = df[sentiment_col].value_counts()
    total_reviews = len(df)
    
    # 计算正面和负面评价的比例
    positive_percentage = sentiment_counts.get('Positive', 0) / total_reviews * 100
    negative_percentage = sentiment_counts.get('Negative', 0) / total_reviews * 100
    neutral_percentage = sentiment_counts.get('Neutral', 0) / total_reviews * 100
    
    # 提取高分和低分评论的样本
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    if review_col:
        positive_samples = df[df[sentiment_col] == 'Positive'][review_col].sample(min(3, sentiment_counts.get('Positive', 0))).tolist()
        negative_samples = df[df[sentiment_col] == 'Negative'][review_col].sample(min(3, sentiment_counts.get('Negative', 0))).tolist()
        
        positive_examples = "\n".join([f"- {sample[:100]}..." for sample in positive_samples])
        negative_examples = "\n".join([f"- {sample[:100]}..." for sample in negative_samples])
    else:
        positive_examples = "无样本数据"
        negative_examples = "无样本数据"
    
    prompt = f"""分析以下{brand_name}的评论情感分布数据：
    总评论数：{total_reviews}
    正面评价：{sentiment_counts.get('Positive', 0)}条 ({positive_percentage:.1f}%)
    中性评价：{sentiment_counts.get('Neutral', 0)}条 ({neutral_percentage:.1f}%)
    负面评价：{sentiment_counts.get('Negative', 0)}条 ({negative_percentage:.1f}%)
    
    正面评价样本：
{positive_examples}
    
    负面评价样本：
{negative_examples}
    
    请深入分析这个情感分布的特点，包括：
    1. 整体情感倾向和用户满意度水平
    2. 正面评价中反映的品牌主要优势和亮点
    3. 负面评价中反映的品牌主要问题和痛点
    4. 用户投诉的主要焦点和表扬的核心方面
    5. 情感极化现象分析（如果存在）
    6. 针对负面情感，品牌应该采取的改进措施
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面。"""
    
    return call_ai_model(prompt)

def analyze_word_cloud(df, brand_name):
    """分析词云数据"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    sentiment_col = 'sentiment_category'
    if review_col is None:
        return None
        
    # 分别提取正面和负面评论中的关键词
    all_text = ' '.join(df[review_col].dropna().astype(str))
    
    # 设置停用词
    from wordcloud import STOPWORDS
    import string
    stopwords = set(STOPWORDS)
    custom_stopwords = {
        # 英文常见停用词
        'the', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'with', 'for', 'on', 'is', 'was', 'be',
        'this', 'have', 'from', 'or', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'there', 'can', 'an', 'your', 'which', 'their', 'said', 'if', 'will', 'my', 'one',
        'would', 'so', 'up', 'out', 'them', 'about', 'who', 'get', 'me', 'been', 'has', 'just',
        'do', 'did', 'doing', 'does', 'then', 'such', 'no', 'yes', 'they', 'also', 'any', 'are',
        
        # 品牌和产品相关词
        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
        
        # 电商常见词
        'shipping', 'delivery', 'arrived', 'package', 'item', 'items', 'customer', 'customers',
        'review', 'reviews', 'rating', 'ratings', 'star', 'stars', 'experience'
    }
    stopwords.update(custom_stopwords)
    
    # 处理文本，移除标点符号和停用词
    text = all_text.lower()
    for p in string.punctuation:
        text = text.replace(p, ' ')
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
    
    # 获取总体词频
    word_freq = pd.Series(filtered_words).value_counts().head(15)
    
    # 如果有情感分类列，分别提取正面和负面评论的关键词
    pos_word_freq = None
    neg_word_freq = None
    if sentiment_col in df.columns:
        pos_reviews = ' '.join(df[df[sentiment_col] == 'Positive'][review_col].dropna().astype(str))
        neg_reviews = ' '.join(df[df[sentiment_col] == 'Negative'][review_col].dropna().astype(str))
        
        # 处理正面评论文本
        pos_text = pos_reviews.lower()
        for p in string.punctuation:
            pos_text = pos_text.replace(p, ' ')
        pos_words = pos_text.split()
        pos_filtered = [word for word in pos_words if word not in stopwords and len(word) > 2]
        pos_word_freq = pd.Series(pos_filtered).value_counts().head(10)
        
        # 处理负面评论文本
        neg_text = neg_reviews.lower()
        for p in string.punctuation:
            neg_text = neg_text.replace(p, ' ')
        neg_words = neg_text.split()
        neg_filtered = [word for word in neg_words if word not in stopwords and len(word) > 2]
        neg_word_freq = pd.Series(neg_filtered).value_counts().head(10)
    
    # 构建提示词
    prompt = f"""分析以下{brand_name}的评论关键词数据：
    
    总体最常见的15个关键词及其出现次数：
    {', '.join([f'{word}: {count}次' for word, count in word_freq.items()])}
    """
    
    # 添加正面评论关键词
    if pos_word_freq is not None and len(pos_word_freq) > 0:
        prompt += f"""
    
    正面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in pos_word_freq.items()])}
    """
    
    # 添加负面评论关键词
    if neg_word_freq is not None and len(neg_word_freq) > 0:
        prompt += f"""
    
    负面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in neg_word_freq.items()])}
    """
    
    prompt += f"""
    
    请深入分析这些关键词的特点，包括：
    1. 用户最关注的产品/服务方面
    2. 正面评价中反映的品牌主要优势和特色
    3. 负面评价中反映的品牌主要问题和痛点
    4. 关键词与具体业务场景的关联（如产品质量、客户服务、物流配送等）
    5. 品牌应该重点改进的方面
    6. 品牌可以继续保持和强化的优势
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面，并给出具体可行的改进建议。"""
    
    return call_ai_model(prompt)

def analyze_time_trends(df, brand_name):
    """分析时间趋势"""
    date_col = next((col for col in df.columns if col.lower() == 'date'), None)
    if date_col is None:
        return None
        
    df['date'] = pd.to_datetime(df[date_col])
    monthly_counts = df.groupby(df['date'].dt.to_period('M')).size()
    
    if len(monthly_counts) <= 1:
        return None
    
    trend = 'increasing' if monthly_counts.iloc[-1] > monthly_counts.iloc[0] else 'decreasing'
    avg_monthly = monthly_counts.mean()
    max_month = monthly_counts.idxmax()
    min_month = monthly_counts.idxmin()
    
    # 分析评分随时间的变化趋势
    rating_trend = ""
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    if rating_col:
        # 计算每月平均评分
        monthly_ratings = df.groupby(df['date'].dt.to_period('M'))[rating_col].mean()
        if len(monthly_ratings) > 1:
            rating_trend = 'improving' if monthly_ratings.iloc[-1] > monthly_ratings.iloc[0] else 'declining'
            rating_trend = f"\n    评分趋势：{rating_trend}"
            rating_trend += f"\n    初始月份平均评分：{monthly_ratings.iloc[0]:.2f}星"
            rating_trend += f"\n    最近月份平均评分：{monthly_ratings.iloc[-1]:.2f}星"
    
    # 分析情感随时间的变化趋势
    sentiment_trend = ""
    sentiment_col = 'sentiment'
    if sentiment_col in df.columns:
        # 计算每月平均情感得分
        monthly_sentiment = df.groupby(df['date'].dt.to_period('M'))[sentiment_col].mean()
        if len(monthly_sentiment) > 1:
            sentiment_trend = 'improving' if monthly_sentiment.iloc[-1] > monthly_sentiment.iloc[0] else 'declining'
            sentiment_trend = f"\n    情感趋势：{sentiment_trend}"
            sentiment_trend += f"\n    初始月份平均情感得分：{monthly_sentiment.iloc[0]:.3f}"
            sentiment_trend += f"\n    最近月份平均情感得分：{monthly_sentiment.iloc[-1]:.3f}"
    
    prompt = f"""分析以下{brand_name}的评论时间趋势数据：
    评论数量趋势：{trend}
    平均每月评论数：{avg_monthly:.1f}
    评论最多的月份：{max_month}（{monthly_counts[max_month]}条）
    评论最少的月份：{min_month}（{monthly_counts[min_month]}条）{rating_trend}{sentiment_trend}
    
    请深入分析这个时间趋势的特点，包括：
    1. 品牌影响力随时间的变化趋势
    2. 用户满意度随时间的变化趋势
    3. 季节性波动及其可能的原因
    4. 高峰期和低谷期的特点及其与品牌活动的关联
    5. 品牌表现是否在改善或恶化，以及可能的原因
    6. 基于时间趋势，品牌应该采取的策略调整
    
    请用简洁的语言总结分析结果，重点突出品牌随时间变化的优势和劣势，并给出针对性的发展趋势建议。"""
    
    return call_ai_model(prompt)

def generate_comprehensive_analysis(df, brand_name):
    """生成综合分析报告"""
    analyses = {
        'rating': analyze_rating_distribution(df, brand_name),
        'country': analyze_country_distribution(df, brand_name),
        'sentiment': analyze_sentiment_trends(df, brand_name),
        'keywords': analyze_word_cloud(df, brand_name),
        'time': analyze_time_trends(df, brand_name)
    }
    
    # 过滤掉None值
    valid_analyses = {k: v for k, v in analyses.items() if v is not None}
    
    prompt = f"""基于以下{brand_name}的各个维度分析结果，生成一个全面深入的综合分析报告：

{json.dumps(valid_analyses, ensure_ascii=False, indent=2)}

请系统性地总结以下几个方面：

1. 品牌整体表现评估
   - 总体用户满意度水平
   - 品牌在市场中的定位和影响力
   - 品牌声誉的总体状况

2. 品牌核心优势（至少3-5点）
   - 具体列出品牌最突出的优势
   - 每个优势的具体表现和影响
   - 这些优势如何为品牌创造竞争力
   - 如何进一步强化这些优势

3. 品牌主要劣势和问题（至少3-5点）
   - 具体列出品牌最突出的问题和劣势
   - 每个问题的具体表现和影响
   - 这些问题如何影响用户体验和品牌声誉
   - 问题的严重程度和优先级排序

4. 具体可行的改进建议（至少5点）
   - 针对每个主要问题提出具体的改进措施
   - 建议的实施优先级和预期效果
   - 短期可立即实施的改进措施
   - 长期需要战略性调整的改进方向

5. 市场机会和发展方向
   - 基于用户反馈的潜在市场机会
   - 品牌可以拓展的新领域或新市场
   - 与竞争对手差异化的关键点

请用简洁专业的语言输出分析结果，确保分析具有可操作性和实用价值，能够直接指导品牌改进和发展策略。"""
    
    return call_ai_model(prompt)

def analyze_sentiment_trends(df, brand_name):
    """分析情感趋势"""
    sentiment_col = 'sentiment_category'
    if sentiment_col not in df.columns:
        return None
        
    sentiment_counts = df[sentiment_col].value_counts()
    total_reviews = len(df)
    
    # 计算正面和负面评价的比例
    positive_percentage = sentiment_counts.get('Positive', 0) / total_reviews * 100
    negative_percentage = sentiment_counts.get('Negative', 0) / total_reviews * 100
    neutral_percentage = sentiment_counts.get('Neutral', 0) / total_reviews * 100
    
    # 提取高分和低分评论的样本
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    if review_col:
        positive_samples = df[df[sentiment_col] == 'Positive'][review_col].sample(min(3, sentiment_counts.get('Positive', 0))).tolist()
        negative_samples = df[df[sentiment_col] == 'Negative'][review_col].sample(min(3, sentiment_counts.get('Negative', 0))).tolist()
        
        positive_examples = "\n".join([f"- {sample[:100]}..." for sample in positive_samples])
        negative_examples = "\n".join([f"- {sample[:100]}..." for sample in negative_samples])
    else:
        positive_examples = "无样本数据"
        negative_examples = "无样本数据"
    
    prompt = f"""分析以下{brand_name}的评论情感分布数据：
    总评论数：{total_reviews}
    正面评价：{sentiment_counts.get('Positive', 0)}条 ({positive_percentage:.1f}%)
    中性评价：{sentiment_counts.get('Neutral', 0)}条 ({neutral_percentage:.1f}%)
    负面评价：{sentiment_counts.get('Negative', 0)}条 ({negative_percentage:.1f}%)
    
    正面评价样本：
{positive_examples}
    
    负面评价样本：
{negative_examples}
    
    请深入分析这个情感分布的特点，包括：
    1. 整体情感倾向和用户满意度水平
    2. 正面评价中反映的品牌主要优势和亮点
    3. 负面评价中反映的品牌主要问题和痛点
    4. 用户投诉的主要焦点和表扬的核心方面
    5. 情感极化现象分析（如果存在）
    6. 针对负面情感，品牌应该采取的改进措施
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面。"""
    
    return call_ai_model(prompt)

def analyze_word_cloud(df, brand_name):
    """分析词云数据"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    sentiment_col = 'sentiment_category'
    if review_col is None:
        return None
        
    # 分别提取正面和负面评论中的关键词
    all_text = ' '.join(df[review_col].dropna().astype(str))
    
    # 设置停用词
    from wordcloud import STOPWORDS
    import string
    stopwords = set(STOPWORDS)
    custom_stopwords = {
        # 英文常见停用词
        'the', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'with', 'for', 'on', 'is', 'was', 'be',
        'this', 'have', 'from', 'or', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'there', 'can', 'an', 'your', 'which', 'their', 'said', 'if', 'will', 'my', 'one',
        'would', 'so', 'up', 'out', 'them', 'about', 'who', 'get', 'me', 'been', 'has', 'just',
        'do', 'did', 'doing', 'does', 'then', 'such', 'no', 'yes', 'they', 'also', 'any', 'are',
        
        # 品牌和产品相关词
        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
        
        # 电商常见词
        'shipping', 'delivery', 'arrived', 'package', 'item', 'items', 'customer', 'customers',
        'review', 'reviews', 'rating', 'ratings', 'star', 'stars', 'experience'
    }
    stopwords.update(custom_stopwords)
    
    # 处理文本，移除标点符号和停用词
    text = all_text.lower()
    for p in string.punctuation:
        text = text.replace(p, ' ')
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
    
    # 获取总体词频
    word_freq = pd.Series(filtered_words).value_counts().head(15)
    
    # 如果有情感分类列，分别提取正面和负面评论的关键词
    pos_word_freq = None
    neg_word_freq = None
    if sentiment_col in df.columns:
        pos_reviews = ' '.join(df[df[sentiment_col] == 'Positive'][review_col].dropna().astype(str))
        neg_reviews = ' '.join(df[df[sentiment_col] == 'Negative'][review_col].dropna().astype(str))
        
        # 处理正面评论文本
        pos_text = pos_reviews.lower()
        for p in string.punctuation:
            pos_text = pos_text.replace(p, ' ')
        pos_words = pos_text.split()
        pos_filtered = [word for word in pos_words if word not in stopwords and len(word) > 2]
        pos_word_freq = pd.Series(pos_filtered).value_counts().head(10)
        
        # 处理负面评论文本
        neg_text = neg_reviews.lower()
        for p in string.punctuation:
            neg_text = neg_text.replace(p, ' ')
        neg_words = neg_text.split()
        neg_filtered = [word for word in neg_words if word not in stopwords and len(word) > 2]
        neg_word_freq = pd.Series(neg_filtered).value_counts().head(10)
    
    # 构建提示词
    prompt = f"""分析以下{brand_name}的评论关键词数据：
    
    总体最常见的15个关键词及其出现次数：
    {', '.join([f'{word}: {count}次' for word, count in word_freq.items()])}
    """
    
    # 添加正面评论关键词
    if pos_word_freq is not None and len(pos_word_freq) > 0:
        prompt += f"""
    
    正面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in pos_word_freq.items()])}
    """
    
    # 添加负面评论关键词
    if neg_word_freq is not None and len(neg_word_freq) > 0:
        prompt += f"""
    
    负面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in neg_word_freq.items()])}
    """
    
    prompt += f"""
    
    请深入分析这些关键词的特点，包括：
    1. 用户最关注的产品/服务方面
    2. 正面评价中反映的品牌主要优势和特色
    3. 负面评价中反映的品牌主要问题和痛点
    4. 关键词与具体业务场景的关联（如产品质量、客户服务、物流配送等）
    5. 品牌应该重点改进的方面
    6. 品牌可以继续保持和强化的优势
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面，并给出具体可行的改进建议。"""
    
    return call_ai_model(prompt)

def analyze_time_trends(df, brand_name):
    """分析时间趋势"""
    date_col = next((col for col in df.columns if col.lower() == 'date'), None)
    if date_col is None:
        return None
        
    df['date'] = pd.to_datetime(df[date_col])
    monthly_counts = df.groupby(df['date'].dt.to_period('M')).size()
    
    if len(monthly_counts) <= 1:
        return None
    
    trend = 'increasing' if monthly_counts.iloc[-1] > monthly_counts.iloc[0] else 'decreasing'
    avg_monthly = monthly_counts.mean()
    max_month = monthly_counts.idxmax()
    min_month = monthly_counts.idxmin()
    
    # 分析评分随时间的变化趋势
    rating_trend = ""
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    if rating_col:
        # 计算每月平均评分
        monthly_ratings = df.groupby(df['date'].dt.to_period('M'))[rating_col].mean()
        if len(monthly_ratings) > 1:
            rating_trend = 'improving' if monthly_ratings.iloc[-1] > monthly_ratings.iloc[0] else 'declining'
            rating_trend = f"\n    评分趋势：{rating_trend}"
            rating_trend += f"\n    初始月份平均评分：{monthly_ratings.iloc[0]:.2f}星"
            rating_trend += f"\n    最近月份平均评分：{monthly_ratings.iloc[-1]:.2f}星"
    
    # 分析情感随时间的变化趋势
    sentiment_trend = ""
    sentiment_col = 'sentiment'
    if sentiment_col in df.columns:
        # 计算每月平均情感得分
        monthly_sentiment = df.groupby(df['date'].dt.to_period('M'))[sentiment_col].mean()
        if len(monthly_sentiment) > 1:
            sentiment_trend = 'improving' if monthly_sentiment.iloc[-1] > monthly_sentiment.iloc[0] else 'declining'
            sentiment_trend = f"\n    情感趋势：{sentiment_trend}"
            sentiment_trend += f"\n    初始月份平均情感得分：{monthly_sentiment.iloc[0]:.3f}"
            sentiment_trend += f"\n    最近月份平均情感得分：{monthly_sentiment.iloc[-1]:.3f}"
    
    prompt = f"""分析以下{brand_name}的评论时间趋势数据：
    评论数量趋势：{trend}
    平均每月评论数：{avg_monthly:.1f}
    评论最多的月份：{max_month}（{monthly_counts[max_month]}条）
    评论最少的月份：{min_month}（{monthly_counts[min_month]}条）{rating_trend}{sentiment_trend}
    
    请深入分析这个时间趋势的特点，包括：
    1. 品牌影响力随时间的变化趋势
    2. 用户满意度随时间的变化趋势
    3. 季节性波动及其可能的原因
    4. 高峰期和低谷期的特点及其与品牌活动的关联
    5. 品牌表现是否在改善或恶化，以及可能的原因
    6. 基于时间趋势，品牌应该采取的策略调整
    
    请用简洁的语言总结分析结果，重点突出品牌随时间变化的优势和劣势，并给出针对性的发展趋势建议。"""
    
    return call_ai_model(prompt)

def generate_comprehensive_analysis(df, brand_name):
    """生成综合分析报告"""
    analyses = {
        'rating': analyze_rating_distribution(df, brand_name),
        'country': analyze_country_distribution(df, brand_name),
        'sentiment': analyze_sentiment_trends(df, brand_name),
        'keywords': analyze_word_cloud(df, brand_name),
        'time': analyze_time_trends(df, brand_name)
    }
    
    # 过滤掉None值
    valid_analyses = {k: v for k, v in analyses.items() if v is not None}
    
    prompt = f"""基于以下{brand_name}的各个维度分析结果，生成一个全面深入的综合分析报告：

{json.dumps(valid_analyses, ensure_ascii=False, indent=2)}

请系统性地总结以下几个方面：

1. 品牌整体表现评估
   - 总体用户满意度水平
   - 品牌在市场中的定位和影响力
   - 品牌声誉的总体状况

2. 品牌核心优势（至少3-5点）
   - 具体列出品牌最突出的优势
   - 每个优势的具体表现和影响
   - 这些优势如何为品牌创造竞争力
   - 如何进一步强化这些优势

3. 品牌主要劣势和问题（至少3-5点）
   - 具体列出品牌最突出的问题和劣势
   - 每个问题的具体表现和影响
   - 这些问题如何影响用户体验和品牌声誉
   - 问题的严重程度和优先级排序

4. 具体可行的改进建议（至少5点）
   - 针对每个主要问题提出具体的改进措施
   - 建议的实施优先级和预期效果
   - 短期可立即实施的改进措施
   - 长期需要战略性调整的改进方向

5. 市场机会和发展方向
   - 基于用户反馈的潜在市场机会
   - 品牌可以拓展的新领域或新市场
   - 与竞争对手差异化的关键点

请用简洁专业的语言输出分析结果，确保分析具有可操作性和实用价值，能够直接指导品牌改进和发展策略。"""
    
    return call_ai_model(prompt)

def analyze_sentiment_trends(df, brand_name):
    """分析情感趋势"""
    sentiment_col = 'sentiment_category'
    if sentiment_col not in df.columns:
        return None
        
    sentiment_counts = df[sentiment_col].value_counts()
    total_reviews = len(df)
    
    # 计算正面和负面评价的比例
    positive_percentage = sentiment_counts.get('Positive', 0) / total_reviews * 100
    negative_percentage = sentiment_counts.get('Negative', 0) / total_reviews * 100
    neutral_percentage = sentiment_counts.get('Neutral', 0) / total_reviews * 100
    
    # 提取高分和低分评论的样本
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    if review_col:
        positive_samples = df[df[sentiment_col] == 'Positive'][review_col].sample(min(3, sentiment_counts.get('Positive', 0))).tolist()
        negative_samples = df[df[sentiment_col] == 'Negative'][review_col].sample(min(3, sentiment_counts.get('Negative', 0))).tolist()
        
        positive_examples = "\n".join([f"- {sample[:100]}..." for sample in positive_samples])
        negative_examples = "\n".join([f"- {sample[:100]}..." for sample in negative_samples])
    else:
        positive_examples = "无样本数据"
        negative_examples = "无样本数据"
    
    prompt = f"""分析以下{brand_name}的评论情感分布数据：
    总评论数：{total_reviews}
    正面评价：{sentiment_counts.get('Positive', 0)}条 ({positive_percentage:.1f}%)
    中性评价：{sentiment_counts.get('Neutral', 0)}条 ({neutral_percentage:.1f}%)
    负面评价：{sentiment_counts.get('Negative', 0)}条 ({negative_percentage:.1f}%)
    
    正面评价样本：
{positive_examples}
    
    负面评价样本：
{negative_examples}
    
    请深入分析这个情感分布的特点，包括：
    1. 整体情感倾向和用户满意度水平
    2. 正面评价中反映的品牌主要优势和亮点
    3. 负面评价中反映的品牌主要问题和痛点
    4. 用户投诉的主要焦点和表扬的核心方面
    5. 情感极化现象分析（如果存在）
    6. 针对负面情感，品牌应该采取的改进措施
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面。"""
    
    return call_ai_model(prompt)

def analyze_word_cloud(df, brand_name):
    """分析词云数据"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    sentiment_col = 'sentiment_category'
    if review_col is None:
        return None
        
    # 分别提取正面和负面评论中的关键词
    all_text = ' '.join(df[review_col].dropna().astype(str))
    
    # 设置停用词
    from wordcloud import STOPWORDS
    import string
    stopwords = set(STOPWORDS)
    custom_stopwords = {
        # 英文常见停用词
        'the', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'with', 'for', 'on', 'is', 'was', 'be',
        'this', 'have', 'from', 'or', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'there', 'can', 'an', 'your', 'which', 'their', 'said', 'if', 'will', 'my', 'one',
        'would', 'so', 'up', 'out', 'them', 'about', 'who', 'get', 'me', 'been', 'has', 'just',
        'do', 'did', 'doing', 'does', 'then', 'such', 'no', 'yes', 'they', 'also', 'any', 'are',
        
        # 品牌和产品相关词
        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
        
        # 电商常见词
        'shipping', 'delivery', 'arrived', 'package', 'item', 'items', 'customer', 'customers',
        'review', 'reviews', 'rating', 'ratings', 'star', 'stars', 'experience'
    }
    stopwords.update(custom_stopwords)
    
    # 处理文本，移除标点符号和停用词
    text = all_text.lower()
    for p in string.punctuation:
        text = text.replace(p, ' ')
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
    
    # 获取总体词频
    word_freq = pd.Series(filtered_words).value_counts().head(15)
    
    # 如果有情感分类列，分别提取正面和负面评论的关键词
    pos_word_freq = None
    neg_word_freq = None
    if sentiment_col in df.columns:
        pos_reviews = ' '.join(df[df[sentiment_col] == 'Positive'][review_col].dropna().astype(str))
        neg_reviews = ' '.join(df[df[sentiment_col] == 'Negative'][review_col].dropna().astype(str))
        
        # 处理正面评论文本
        pos_text = pos_reviews.lower()
        for p in string.punctuation:
            pos_text = pos_text.replace(p, ' ')
        pos_words = pos_text.split()
        pos_filtered = [word for word in pos_words if word not in stopwords and len(word) > 2]
        pos_word_freq = pd.Series(pos_filtered).value_counts().head(10)
        
        # 处理负面评论文本
        neg_text = neg_reviews.lower()
        for p in string.punctuation:
            neg_text = neg_text.replace(p, ' ')
        neg_words = neg_text.split()
        neg_filtered = [word for word in neg_words if word not in stopwords and len(word) > 2]
        neg_word_freq = pd.Series(neg_filtered).value_counts().head(10)
    
    # 构建提示词
    prompt = f"""分析以下{brand_name}的评论关键词数据：
    
    总体最常见的15个关键词及其出现次数：
    {', '.join([f'{word}: {count}次' for word, count in word_freq.items()])}
    """
    
    # 添加正面评论关键词
    if pos_word_freq is not None and len(pos_word_freq) > 0:
        prompt += f"""
    
    正面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in pos_word_freq.items()])}
    """
    
    # 添加负面评论关键词
    if neg_word_freq is not None and len(neg_word_freq) > 0:
        prompt += f"""
    
    负面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in neg_word_freq.items()])}
    """
    
    prompt += f"""
    
    请深入分析这些关键词的特点，包括：
    1. 用户最关注的产品/服务方面
    2. 正面评价中反映的品牌主要优势和特色
    3. 负面评价中反映的品牌主要问题和痛点
    4. 关键词与具体业务场景的关联（如产品质量、客户服务、物流配送等）
    5. 品牌应该重点改进的方面
    6. 品牌可以继续保持和强化的优势
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面，并给出具体可行的改进建议。"""
    
    return call_ai_model(prompt)

def analyze_time_trends(df, brand_name):
    """分析时间趋势"""
    date_col = next((col for col in df.columns if col.lower() == 'date'), None)
    if date_col is None:
        return None
        
    df['date'] = pd.to_datetime(df[date_col])
    monthly_counts = df.groupby(df['date'].dt.to_period('M')).size()
    
    if len(monthly_counts) <= 1:
        return None
    
    trend = 'increasing' if monthly_counts.iloc[-1] > monthly_counts.iloc[0] else 'decreasing'
    avg_monthly = monthly_counts.mean()
    max_month = monthly_counts.idxmax()
    min_month = monthly_counts.idxmin()
    
    # 分析评分随时间的变化趋势
    rating_trend = ""
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    if rating_col:
        # 计算每月平均评分
        monthly_ratings = df.groupby(df['date'].dt.to_period('M'))[rating_col].mean()
        if len(monthly_ratings) > 1:
            rating_trend = 'improving' if monthly_ratings.iloc[-1] > monthly_ratings.iloc[0] else 'declining'
            rating_trend = f"\n    评分趋势：{rating_trend}"
            rating_trend += f"\n    初始月份平均评分：{monthly_ratings.iloc[0]:.2f}星"
            rating_trend += f"\n    最近月份平均评分：{monthly_ratings.iloc[-1]:.2f}星"
    
    # 分析情感随时间的变化趋势
    sentiment_trend = ""
    sentiment_col = 'sentiment'
    if sentiment_col in df.columns:
        # 计算每月平均情感得分
        monthly_sentiment = df.groupby(df['date'].dt.to_period('M'))[sentiment_col].mean()
        if len(monthly_sentiment) > 1:
            sentiment_trend = 'improving' if monthly_sentiment.iloc[-1] > monthly_sentiment.iloc[0] else 'declining'
            sentiment_trend = f"\n    情感趋势：{sentiment_trend}"
            sentiment_trend += f"\n    初始月份平均情感得分：{monthly_sentiment.iloc[0]:.3f}"
            sentiment_trend += f"\n    最近月份平均情感得分：{monthly_sentiment.iloc[-1]:.3f}"
    
    prompt = f"""分析以下{brand_name}的评论时间趋势数据：
    评论数量趋势：{trend}
    平均每月评论数：{avg_monthly:.1f}
    评论最多的月份：{max_month}（{monthly_counts[max_month]}条）
    评论最少的月份：{min_month}（{monthly_counts[min_month]}条）{rating_trend}{sentiment_trend}
    
    请深入分析这个时间趋势的特点，包括：
    1. 品牌影响力随时间的变化趋势
    2. 用户满意度随时间的变化趋势
    3. 季节性波动及其可能的原因
    4. 高峰期和低谷期的特点及其与品牌活动的关联
    5. 品牌表现是否在改善或恶化，以及可能的原因
    6. 基于时间趋势，品牌应该采取的策略调整
    
    请用简洁的语言总结分析结果，重点突出品牌随时间变化的优势和劣势，并给出针对性的发展趋势建议。"""
    
    return call_ai_model(prompt)

def generate_comprehensive_analysis(df, brand_name):
    """生成综合分析报告"""
    analyses = {
        'rating': analyze_rating_distribution(df, brand_name),
        'country': analyze_country_distribution(df, brand_name),
        'sentiment': analyze_sentiment_trends(df, brand_name),
        'keywords': analyze_word_cloud(df, brand_name),
        'time': analyze_time_trends(df, brand_name)
    }
    
    # 过滤掉None值
    valid_analyses = {k: v for k, v in analyses.items() if v is not None}
    
    prompt = f"""基于以下{brand_name}的各个维度分析结果，生成一个全面深入的综合分析报告：

{json.dumps(valid_analyses, ensure_ascii=False, indent=2)}

请系统性地总结以下几个方面：

1. 品牌整体表现评估
   - 总体用户满意度水平
   - 品牌在市场中的定位和影响力
   - 品牌声誉的总体状况

2. 品牌核心优势（至少3-5点）
   - 具体列出品牌最突出的优势
   - 每个优势的具体表现和影响
   - 这些优势如何为品牌创造竞争力
   - 如何进一步强化这些优势

3. 品牌主要劣势和问题（至少3-5点）
   - 具体列出品牌最突出的问题和劣势
   - 每个问题的具体表现和影响
   - 这些问题如何影响用户体验和品牌声誉
   - 问题的严重程度和优先级排序

4. 具体可行的改进建议（至少5点）
   - 针对每个主要问题提出具体的改进措施
   - 建议的实施优先级和预期效果
   - 短期可立即实施的改进措施
   - 长期需要战略性调整的改进方向

5. 市场机会和发展方向
   - 基于用户反馈的潜在市场机会
   - 品牌可以拓展的新领域或新市场
   - 与竞争对手差异化的关键点

请用简洁专业的语言输出分析结果，确保分析具有可操作性和实用价值，能够直接指导品牌改进和发展策略。"""
    
    return call_ai_model(prompt)

def analyze_sentiment_trends(df, brand_name):
    """分析情感趋势"""
    sentiment_col = 'sentiment_category'
    if sentiment_col not in df.columns:
        return None
        
    sentiment_counts = df[sentiment_col].value_counts()
    total_reviews = len(df)
    
    # 计算正面和负面评价的比例
    positive_percentage = sentiment_counts.get('Positive', 0) / total_reviews * 100
    negative_percentage = sentiment_counts.get('Negative', 0) / total_reviews * 100
    neutral_percentage = sentiment_counts.get('Neutral', 0) / total_reviews * 100
    
    # 提取高分和低分评论的样本
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    if review_col:
        positive_samples = df[df[sentiment_col] == 'Positive'][review_col].sample(min(3, sentiment_counts.get('Positive', 0))).tolist()
        negative_samples = df[df[sentiment_col] == 'Negative'][review_col].sample(min(3, sentiment_counts.get('Negative', 0))).tolist()
        
        positive_examples = "\n".join([f"- {sample[:100]}..." for sample in positive_samples])
        negative_examples = "\n".join([f"- {sample[:100]}..." for sample in negative_samples])
    else:
        positive_examples = "无样本数据"
        negative_examples = "无样本数据"
    
    prompt = f"""分析以下{brand_name}的评论情感分布数据：
    总评论数：{total_reviews}
    正面评价：{sentiment_counts.get('Positive', 0)}条 ({positive_percentage:.1f}%)
    中性评价：{sentiment_counts.get('Neutral', 0)}条 ({neutral_percentage:.1f}%)
    负面评价：{sentiment_counts.get('Negative', 0)}条 ({negative_percentage:.1f}%)
    
    正面评价样本：
{positive_examples}
    
    负面评价样本：
{negative_examples}
    
    请深入分析这个情感分布的特点，包括：
    1. 整体情感倾向和用户满意度水平
    2. 正面评价中反映的品牌主要优势和亮点
    3. 负面评价中反映的品牌主要问题和痛点
    4. 用户投诉的主要焦点和表扬的核心方面
    5. 情感极化现象分析（如果存在）
    6. 针对负面情感，品牌应该采取的改进措施
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面。"""
    
    return call_ai_model(prompt)

def analyze_word_cloud(df, brand_name):
    """分析词云数据"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    sentiment_col = 'sentiment_category'
    if review_col is None:
        return None
        
    # 分别提取正面和负面评论中的关键词
    all_text = ' '.join(df[review_col].dropna().astype(str))
    
    # 设置停用词
    from wordcloud import STOPWORDS
    import string
    stopwords = set(STOPWORDS)
    custom_stopwords = {
        # 英文常见停用词
        'the', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'with', 'for', 'on', 'is', 'was', 'be',
        'this', 'have', 'from', 'or', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'there', 'can', 'an', 'your', 'which', 'their', 'said', 'if', 'will', 'my', 'one',
        'would', 'so', 'up', 'out', 'them', 'about', 'who', 'get', 'me', 'been', 'has', 'just',
        'do', 'did', 'doing', 'does', 'then', 'such', 'no', 'yes', 'they', 'also', 'any', 'are',
        
        # 品牌和产品相关词
        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
        
        # 电商常见词
        'shipping', 'delivery', 'arrived', 'package', 'item', 'items', 'customer', 'customers',
        'review', 'reviews', 'rating', 'ratings', 'star', 'stars', 'experience'
    }
    stopwords.update(custom_stopwords)
    
    # 处理文本，移除标点符号和停用词
    text = all_text.lower()
    for p in string.punctuation:
        text = text.replace(p, ' ')
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
    
    # 获取总体词频
    word_freq = pd.Series(filtered_words).value_counts().head(15)
    
    # 如果有情感分类列，分别提取正面和负面评论的关键词
    pos_word_freq = None
    neg_word_freq = None
    if sentiment_col in df.columns:
        pos_reviews = ' '.join(df[df[sentiment_col] == 'Positive'][review_col].dropna().astype(str))
        neg_reviews = ' '.join(df[df[sentiment_col] == 'Negative'][review_col].dropna().astype(str))
        
        # 处理正面评论文本
        pos_text = pos_reviews.lower()
        for p in string.punctuation:
            pos_text = pos_text.replace(p, ' ')
        pos_words = pos_text.split()
        pos_filtered = [word for word in pos_words if word not in stopwords and len(word) > 2]
        pos_word_freq = pd.Series(pos_filtered).value_counts().head(10)
        
        # 处理负面评论文本
        neg_text = neg_reviews.lower()
        for p in string.punctuation:
            neg_text = neg_text.replace(p, ' ')
        neg_words = neg_text.split()
        neg_filtered = [word for word in neg_words if word not in stopwords and len(word) > 2]
        neg_word_freq = pd.Series(neg_filtered).value_counts().head(10)
    
    # 构建提示词
    prompt = f"""分析以下{brand_name}的评论关键词数据：
    
    总体最常见的15个关键词及其出现次数：
    {', '.join([f'{word}: {count}次' for word, count in word_freq.items()])}
    """
    
    # 添加正面评论关键词
    if pos_word_freq is not None and len(pos_word_freq) > 0:
        prompt += f"""
    
    正面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in pos_word_freq.items()])}
    """
    
    # 添加负面评论关键词
    if neg_word_freq is not None and len(neg_word_freq) > 0:
        prompt += f"""
    
    负面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in neg_word_freq.items()])}
    """
    
    prompt += f"""
    
    请深入分析这些关键词的特点，包括：
    1. 用户最关注的产品/服务方面
    2. 正面评价中反映的品牌主要优势和特色
    3. 负面评价中反映的品牌主要问题和痛点
    4. 关键词与具体业务场景的关联（如产品质量、客户服务、物流配送等）
    5. 品牌应该重点改进的方面
    6. 品牌可以继续保持和强化的优势
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面，并给出具体可行的改进建议。"""
    
    return call_ai_model(prompt)

def analyze_time_trends(df, brand_name):
    """分析时间趋势"""
    date_col = next((col for col in df.columns if col.lower() == 'date'), None)
    if date_col is None:
        return None
        
    df['date'] = pd.to_datetime(df[date_col])
    monthly_counts = df.groupby(df['date'].dt.to_period('M')).size()
    
    if len(monthly_counts) <= 1:
        return None
    
    trend = 'increasing' if monthly_counts.iloc[-1] > monthly_counts.iloc[0] else 'decreasing'
    avg_monthly = monthly_counts.mean()
    max_month = monthly_counts.idxmax()
    min_month = monthly_counts.idxmin()
    
    # 分析评分随时间的变化趋势
    rating_trend = ""
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    if rating_col:
        # 计算每月平均评分
        monthly_ratings = df.groupby(df['date'].dt.to_period('M'))[rating_col].mean()
        if len(monthly_ratings) > 1:
            rating_trend = 'improving' if monthly_ratings.iloc[-1] > monthly_ratings.iloc[0] else 'declining'
            rating_trend = f"\n    评分趋势：{rating_trend}"
            rating_trend += f"\n    初始月份平均评分：{monthly_ratings.iloc[0]:.2f}星"
            rating_trend += f"\n    最近月份平均评分：{monthly_ratings.iloc[-1]:.2f}星"
    
    # 分析情感随时间的变化趋势
    sentiment_trend = ""
    sentiment_col = 'sentiment'
    if sentiment_col in df.columns:
        # 计算每月平均情感得分
        monthly_sentiment = df.groupby(df['date'].dt.to_period('M'))[sentiment_col].mean()
        if len(monthly_sentiment) > 1:
            sentiment_trend = 'improving' if monthly_sentiment.iloc[-1] > monthly_sentiment.iloc[0] else 'declining'
            sentiment_trend = f"\n    情感趋势：{sentiment_trend}"
            sentiment_trend += f"\n    初始月份平均情感得分：{monthly_sentiment.iloc[0]:.3f}"
            sentiment_trend += f"\n    最近月份平均情感得分：{monthly_sentiment.iloc[-1]:.3f}"
    
    prompt = f"""分析以下{brand_name}的评论时间趋势数据：
    评论数量趋势：{trend}
    平均每月评论数：{avg_monthly:.1f}
    评论最多的月份：{max_month}（{monthly_counts[max_month]}条）
    评论最少的月份：{min_month}（{monthly_counts[min_month]}条）{rating_trend}{sentiment_trend}
    
    请深入分析这个时间趋势的特点，包括：
    1. 品牌影响力随时间的变化趋势
    2. 用户满意度随时间的变化趋势
    3. 季节性波动及其可能的原因
    4. 高峰期和低谷期的特点及其与品牌活动的关联
    5. 品牌表现是否在改善或恶化，以及可能的原因
    6. 基于时间趋势，品牌应该采取的策略调整
    
    请用简洁的语言总结分析结果，重点突出品牌随时间变化的优势和劣势，并给出针对性的发展趋势建议。"""
    
    return call_ai_model(prompt)

def generate_comprehensive_analysis(df, brand_name):
    """生成综合分析报告"""
    analyses = {
        'rating': analyze_rating_distribution(df, brand_name),
        'country': analyze_country_distribution(df, brand_name),
        'sentiment': analyze_sentiment_trends(df, brand_name),
        'keywords': analyze_word_cloud(df, brand_name),
        'time': analyze_time_trends(df, brand_name)
    }
    
    # 过滤掉None值
    valid_analyses = {k: v for k, v in analyses.items() if v is not None}
    
    prompt = f"""基于以下{brand_name}的各个维度分析结果，生成一个全面深入的综合分析报告：

{json.dumps(valid_analyses, ensure_ascii=False, indent=2)}

请系统性地总结以下几个方面：

1. 品牌整体表现评估
   - 总体用户满意度水平
   - 品牌在市场中的定位和影响力
   - 品牌声誉的总体状况

2. 品牌核心优势（至少3-5点）
   - 具体列出品牌最突出的优势
   - 每个优势的具体表现和影响
   - 这些优势如何为品牌创造竞争力
   - 如何进一步强化这些优势

3. 品牌主要劣势和问题（至少3-5点）
   - 具体列出品牌最突出的问题和劣势
   - 每个问题的具体表现和影响
   - 这些问题如何影响用户体验和品牌声誉
   - 问题的严重程度和优先级排序

4. 具体可行的改进建议（至少5点）
   - 针对每个主要问题提出具体的改进措施
   - 建议的实施优先级和预期效果
   - 短期可立即实施的改进措施
   - 长期需要战略性调整的改进方向

5. 市场机会和发展方向
   - 基于用户反馈的潜在市场机会
   - 品牌可以拓展的新领域或新市场
   - 与竞争对手差异化的关键点

请用简洁专业的语言输出分析结果，确保分析具有可操作性和实用价值，能够直接指导品牌改进和发展策略。"""
    
    return call_ai_model(prompt)

def analyze_sentiment_trends(df, brand_name):
    """分析情感趋势"""
    sentiment_col = 'sentiment_category'
    if sentiment_col not in df.columns:
        return None
        
    sentiment_counts = df[sentiment_col].value_counts()
    total_reviews = len(df)
    
    # 计算正面和负面评价的比例
    positive_percentage = sentiment_counts.get('Positive', 0) / total_reviews * 100
    negative_percentage = sentiment_counts.get('Negative', 0) / total_reviews * 100
    neutral_percentage = sentiment_counts.get('Neutral', 0) / total_reviews * 100
    
    # 提取高分和低分评论的样本
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    if review_col:
        positive_samples = df[df[sentiment_col] == 'Positive'][review_col].sample(min(3, sentiment_counts.get('Positive', 0))).tolist()
        negative_samples = df[df[sentiment_col] == 'Negative'][review_col].sample(min(3, sentiment_counts.get('Negative', 0))).tolist()
        
        positive_examples = "\n".join([f"- {sample[:100]}..." for sample in positive_samples])
        negative_examples = "\n".join([f"- {sample[:100]}..." for sample in negative_samples])
    else:
        positive_examples = "无样本数据"
        negative_examples = "无样本数据"
    
    prompt = f"""分析以下{brand_name}的评论情感分布数据：
    总评论数：{total_reviews}
    正面评价：{sentiment_counts.get('Positive', 0)}条 ({positive_percentage:.1f}%)
    中性评价：{sentiment_counts.get('Neutral', 0)}条 ({neutral_percentage:.1f}%)
    负面评价：{sentiment_counts.get('Negative', 0)}条 ({negative_percentage:.1f}%)
    
    正面评价样本：
{positive_examples}
    
    负面评价样本：
{negative_examples}
    
    请深入分析这个情感分布的特点，包括：
    1. 整体情感倾向和用户满意度水平
    2. 正面评价中反映的品牌主要优势和亮点
    3. 负面评价中反映的品牌主要问题和痛点
    4. 用户投诉的主要焦点和表扬的核心方面
    5. 情感极化现象分析（如果存在）
    6. 针对负面情感，品牌应该采取的改进措施
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面。"""
    
    return call_ai_model(prompt)

def analyze_word_cloud(df, brand_name):
    """分析词云数据"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    sentiment_col = 'sentiment_category'
    if review_col is None:
        return None
        
    # 分别提取正面和负面评论中的关键词
    all_text = ' '.join(df[review_col].dropna().astype(str))
    
    # 设置停用词
    from wordcloud import STOPWORDS
    import string
    stopwords = set(STOPWORDS)
    custom_stopwords = {
        # 英文常见停用词
        'the', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'with', 'for', 'on', 'is', 'was', 'be',
        'this', 'have', 'from', 'or', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'there', 'can', 'an', 'your', 'which', 'their', 'said', 'if', 'will', 'my', 'one',
        'would', 'so', 'up', 'out', 'them', 'about', 'who', 'get', 'me', 'been', 'has', 'just',
        'do', 'did', 'doing', 'does', 'then', 'such', 'no', 'yes', 'they', 'also', 'any', 'are',
        
        # 品牌和产品相关词
        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
        
        # 电商常见词
        'shipping', 'delivery', 'arrived', 'package', 'item', 'items', 'customer', 'customers',
        'review', 'reviews', 'rating', 'ratings', 'star', 'stars', 'experience'
    }
    stopwords.update(custom_stopwords)
    
    # 处理文本，移除标点符号和停用词
    text = all_text.lower()
    for p in string.punctuation:
        text = text.replace(p, ' ')
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
    
    # 获取总体词频
    word_freq = pd.Series(filtered_words).value_counts().head(15)
    
    # 如果有情感分类列，分别提取正面和负面评论的关键词
    pos_word_freq = None
    neg_word_freq = None
    if sentiment_col in df.columns:
        pos_reviews = ' '.join(df[df[sentiment_col] == 'Positive'][review_col].dropna().astype(str))
        neg_reviews = ' '.join(df[df[sentiment_col] == 'Negative'][review_col].dropna().astype(str))
        
        # 处理正面评论文本
        pos_text = pos_reviews.lower()
        for p in string.punctuation:
            pos_text = pos_text.replace(p, ' ')
        pos_words = pos_text.split()
        pos_filtered = [word for word in pos_words if word not in stopwords and len(word) > 2]
        pos_word_freq = pd.Series(pos_filtered).value_counts().head(10)
        
        # 处理负面评论文本
        neg_text = neg_reviews.lower()
        for p in string.punctuation:
            neg_text = neg_text.replace(p, ' ')
        neg_words = neg_text.split()
        neg_filtered = [word for word in neg_words if word not in stopwords and len(word) > 2]
        neg_word_freq = pd.Series(neg_filtered).value_counts().head(10)
    
    # 构建提示词
    prompt = f"""分析以下{brand_name}的评论关键词数据：
    
    总体最常见的15个关键词及其出现次数：
    {', '.join([f'{word}: {count}次' for word, count in word_freq.items()])}
    """
    
    # 添加正面评论关键词
    if pos_word_freq is not None and len(pos_word_freq) > 0:
        prompt += f"""
    
    正面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in pos_word_freq.items()])}
    """
    
    # 添加负面评论关键词
    if neg_word_freq is not None and len(neg_word_freq) > 0:
        prompt += f"""
    
    负面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in neg_word_freq.items()])}
    """
    
    prompt += f"""
    
    请深入分析这些关键词的特点，包括：
    1. 用户最关注的产品/服务方面
    2. 正面评价中反映的品牌主要优势和特色
    3. 负面评价中反映的品牌主要问题和痛点
    4. 关键词与具体业务场景的关联（如产品质量、客户服务、物流配送等）
    5. 品牌应该重点改进的方面
    6. 品牌可以继续保持和强化的优势
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面，并给出具体可行的改进建议。"""
    
    return call_ai_model(prompt)

def analyze_time_trends(df, brand_name):
    """分析时间趋势"""
    date_col = next((col for col in df.columns if col.lower() == 'date'), None)
    if date_col is None:
        return None
        
    df['date'] = pd.to_datetime(df[date_col])
    monthly_counts = df.groupby(df['date'].dt.to_period('M')).size()
    
    if len(monthly_counts) <= 1:
        return None
    
    trend = 'increasing' if monthly_counts.iloc[-1] > monthly_counts.iloc[0] else 'decreasing'
    avg_monthly = monthly_counts.mean()
    max_month = monthly_counts.idxmax()
    min_month = monthly_counts.idxmin()
    
    # 分析评分随时间的变化趋势
    rating_trend = ""
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    if rating_col:
        # 计算每月平均评分
        monthly_ratings = df.groupby(df['date'].dt.to_period('M'))[rating_col].mean()
        if len(monthly_ratings) > 1:
            rating_trend = 'improving' if monthly_ratings.iloc[-1] > monthly_ratings.iloc[0] else 'declining'
            rating_trend = f"\n    评分趋势：{rating_trend}"
            rating_trend += f"\n    初始月份平均评分：{monthly_ratings.iloc[0]:.2f}星"
            rating_trend += f"\n    最近月份平均评分：{monthly_ratings.iloc[-1]:.2f}星"
    
    # 分析情感随时间的变化趋势
    sentiment_trend = ""
    sentiment_col = 'sentiment'
    if sentiment_col in df.columns:
        # 计算每月平均情感得分
        monthly_sentiment = df.groupby(df['date'].dt.to_period('M'))[sentiment_col].mean()
        if len(monthly_sentiment) > 1:
            sentiment_trend = 'improving' if monthly_sentiment.iloc[-1] > monthly_sentiment.iloc[0] else 'declining'
            sentiment_trend = f"\n    情感趋势：{sentiment_trend}"
            sentiment_trend += f"\n    初始月份平均情感得分：{monthly_sentiment.iloc[0]:.3f}"
            sentiment_trend += f"\n    最近月份平均情感得分：{monthly_sentiment.iloc[-1]:.3f}"
    
    prompt = f"""分析以下{brand_name}的评论时间趋势数据：
    评论数量趋势：{trend}
    平均每月评论数：{avg_monthly:.1f}
    评论最多的月份：{max_month}（{monthly_counts[max_month]}条）
    评论最少的月份：{min_month}（{monthly_counts[min_month]}条）{rating_trend}{sentiment_trend}
    
    请深入分析这个时间趋势的特点，包括：
    1. 品牌影响力随时间的变化趋势
    2. 用户满意度随时间的变化趋势
    3. 季节性波动及其可能的原因
    4. 高峰期和低谷期的特点及其与品牌活动的关联
    5. 品牌表现是否在改善或恶化，以及可能的原因
    6. 基于时间趋势，品牌应该采取的策略调整
    
    请用简洁的语言总结分析结果，重点突出品牌随时间变化的优势和劣势，并给出针对性的发展趋势建议。"""
    
    return call_ai_model(prompt)

def generate_comprehensive_analysis(df, brand_name):
    """生成综合分析报告"""
    analyses = {
        'rating': analyze_rating_distribution(df, brand_name),
        'country': analyze_country_distribution(df, brand_name),
        'sentiment': analyze_sentiment_trends(df, brand_name),
        'keywords': analyze_word_cloud(df, brand_name),
        'time': analyze_time_trends(df, brand_name)
    }
    
    # 过滤掉None值
    valid_analyses = {k: v for k, v in analyses.items() if v is not None}
    
    prompt = f"""基于以下{brand_name}的各个维度分析结果，生成一个全面深入的综合分析报告：

{json.dumps(valid_analyses, ensure_ascii=False, indent=2)}

请系统性地总结以下几个方面：

1. 品牌整体表现评估
   - 总体用户满意度水平
   - 品牌在市场中的定位和影响力
   - 品牌声誉的总体状况

2. 品牌核心优势（至少3-5点）
   - 具体列出品牌最突出的优势
   - 每个优势的具体表现和影响
   - 这些优势如何为品牌创造竞争力
   - 如何进一步强化这些优势

3. 品牌主要劣势和问题（至少3-5点）
   - 具体列出品牌最突出的问题和劣势
   - 每个问题的具体表现和影响
   - 这些问题如何影响用户体验和品牌声誉
   - 问题的严重程度和优先级排序

4. 具体可行的改进建议（至少5点）
   - 针对每个主要问题提出具体的改进措施
   - 建议的实施优先级和预期效果
   - 短期可立即实施的改进措施
   - 长期需要战略性调整的改进方向

5. 市场机会和发展方向
   - 基于用户反馈的潜在市场机会
   - 品牌可以拓展的新领域或新市场
   - 与竞争对手差异化的关键点

请用简洁专业的语言输出分析结果，确保分析具有可操作性和实用价值，能够直接指导品牌改进和发展策略。"""
    
    return call_ai_model(prompt)

def analyze_sentiment_trends(df, brand_name):
    """分析情感趋势"""
    sentiment_col = 'sentiment_category'
    if sentiment_col not in df.columns:
        return None
        
    sentiment_counts = df[sentiment_col].value_counts()
    total_reviews = len(df)
    
    # 计算正面和负面评价的比例
    positive_percentage = sentiment_counts.get('Positive', 0) / total_reviews * 100
    negative_percentage = sentiment_counts.get('Negative', 0) / total_reviews * 100
    neutral_percentage = sentiment_counts.get('Neutral', 0) / total_reviews * 100
    
    # 提取高分和低分评论的样本
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    if review_col:
        positive_samples = df[df[sentiment_col] == 'Positive'][review_col].sample(min(3, sentiment_counts.get('Positive', 0))).tolist()
        negative_samples = df[df[sentiment_col] == 'Negative'][review_col].sample(min(3, sentiment_counts.get('Negative', 0))).tolist()
        
        positive_examples = "\n".join([f"- {sample[:100]}..." for sample in positive_samples])
        negative_examples = "\n".join([f"- {sample[:100]}..." for sample in negative_samples])
    else:
        positive_examples = "无样本数据"
        negative_examples = "无样本数据"
    
    prompt = f"""分析以下{brand_name}的评论情感分布数据：
    总评论数：{total_reviews}
    正面评价：{sentiment_counts.get('Positive', 0)}条 ({positive_percentage:.1f}%)
    中性评价：{sentiment_counts.get('Neutral', 0)}条 ({neutral_percentage:.1f}%)
    负面评价：{sentiment_counts.get('Negative', 0)}条 ({negative_percentage:.1f}%)
    
    正面评价样本：
{positive_examples}
    
    负面评价样本：
{negative_examples}
    
    请深入分析这个情感分布的特点，包括：
    1. 整体情感倾向和用户满意度水平
    2. 正面评价中反映的品牌主要优势和亮点
    3. 负面评价中反映的品牌主要问题和痛点
    4. 用户投诉的主要焦点和表扬的核心方面
    5. 情感极化现象分析（如果存在）
    6. 针对负面情感，品牌应该采取的改进措施
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面。"""
    
    return call_ai_model(prompt)

def analyze_word_cloud(df, brand_name):
    """分析词云数据"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    sentiment_col = 'sentiment_category'
    if review_col is None:
        return None
        
    # 分别提取正面和负面评论中的关键词
    all_text = ' '.join(df[review_col].dropna().astype(str))
    
    # 设置停用词
    from wordcloud import STOPWORDS
    import string
    stopwords = set(STOPWORDS)
    custom_stopwords = {
        # 英文常见停用词
        'the', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'with', 'for', 'on', 'is', 'was', 'be',
        'this', 'have', 'from', 'or', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'there', 'can', 'an', 'your', 'which', 'their', 'said', 'if', 'will', 'my', 'one',
        'would', 'so', 'up', 'out', 'them', 'about', 'who', 'get', 'me', 'been', 'has', 'just',
        'do', 'did', 'doing', 'does', 'then', 'such', 'no', 'yes', 'they', 'also', 'any', 'are',
        
        # 品牌和产品相关词
        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
        
        # 电商常见词
        'shipping', 'delivery', 'arrived', 'package', 'item', 'items', 'customer', 'customers',
        'review', 'reviews', 'rating', 'ratings', 'star', 'stars', 'experience'
    }
    stopwords.update(custom_stopwords)
    
    # 处理文本，移除标点符号和停用词
    text = all_text.lower()
    for p in string.punctuation:
        text = text.replace(p, ' ')
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
    
    # 获取总体词频
    word_freq = pd.Series(filtered_words).value_counts().head(15)
    
    # 如果有情感分类列，分别提取正面和负面评论的关键词
    pos_word_freq = None
    neg_word_freq = None
    if sentiment_col in df.columns:
        pos_reviews = ' '.join(df[df[sentiment_col] == 'Positive'][review_col].dropna().astype(str))
        neg_reviews = ' '.join(df[df[sentiment_col] == 'Negative'][review_col].dropna().astype(str))
        
        # 处理正面评论文本
        pos_text = pos_reviews.lower()
        for p in string.punctuation:
            pos_text = pos_text.replace(p, ' ')
        pos_words = pos_text.split()
        pos_filtered = [word for word in pos_words if word not in stopwords and len(word) > 2]
        pos_word_freq = pd.Series(pos_filtered).value_counts().head(10)
        
        # 处理负面评论文本
        neg_text = neg_reviews.lower()
        for p in string.punctuation:
            neg_text = neg_text.replace(p, ' ')
        neg_words = neg_text.split()
        neg_filtered = [word for word in neg_words if word not in stopwords and len(word) > 2]
        neg_word_freq = pd.Series(neg_filtered).value_counts().head(10)
    
    # 构建提示词
    prompt = f"""分析以下{brand_name}的评论关键词数据：
    
    总体最常见的15个关键词及其出现次数：
    {', '.join([f'{word}: {count}次' for word, count in word_freq.items()])}
    """
    
    # 添加正面评论关键词
    if pos_word_freq is not None and len(pos_word_freq) > 0:
        prompt += f"""
    
    正面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in pos_word_freq.items()])}
    """
    
    # 添加负面评论关键词
    if neg_word_freq is not None and len(neg_word_freq) > 0:
        prompt += f"""
    
    负面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in neg_word_freq.items()])}
    """
    
    prompt += f"""
    
    请深入分析这些关键词的特点，包括：
    1. 用户最关注的产品/服务方面
    2. 正面评价中反映的品牌主要优势和特色
    3. 负面评价中反映的品牌主要问题和痛点
    4. 关键词与具体业务场景的关联（如产品质量、客户服务、物流配送等）
    5. 品牌应该重点改进的方面
    6. 品牌可以继续保持和强化的优势
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面，并给出具体可行的改进建议。"""
    
    return call_ai_model(prompt)

def analyze_time_trends(df, brand_name):
    """分析时间趋势"""
    date_col = next((col for col in df.columns if col.lower() == 'date'), None)
    if date_col is None:
        return None
        
    df['date'] = pd.to_datetime(df[date_col])
    monthly_counts = df.groupby(df['date'].dt.to_period('M')).size()
    
    if len(monthly_counts) <= 1:
        return None
    
    trend = 'increasing' if monthly_counts.iloc[-1] > monthly_counts.iloc[0] else 'decreasing'
    avg_monthly = monthly_counts.mean()
    max_month = monthly_counts.idxmax()
    min_month = monthly_counts.idxmin()
    
    # 分析评分随时间的变化趋势
    rating_trend = ""
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    if rating_col:
        # 计算每月平均评分
        monthly_ratings = df.groupby(df['date'].dt.to_period('M'))[rating_col].mean()
        if len(monthly_ratings) > 1:
            rating_trend = 'improving' if monthly_ratings.iloc[-1] > monthly_ratings.iloc[0] else 'declining'
            rating_trend = f"\n    评分趋势：{rating_trend}"
            rating_trend += f"\n    初始月份平均评分：{monthly_ratings.iloc[0]:.2f}星"
            rating_trend += f"\n    最近月份平均评分：{monthly_ratings.iloc[-1]:.2f}星"
    
    # 分析情感随时间的变化趋势
    sentiment_trend = ""
    sentiment_col = 'sentiment'
    if sentiment_col in df.columns:
        # 计算每月平均情感得分
        monthly_sentiment = df.groupby(df['date'].dt.to_period('M'))[sentiment_col].mean()
        if len(monthly_sentiment) > 1:
            sentiment_trend = 'improving' if monthly_sentiment.iloc[-1] > monthly_sentiment.iloc[0] else 'declining'
            sentiment_trend = f"\n    情感趋势：{sentiment_trend}"
            sentiment_trend += f"\n    初始月份平均情感得分：{monthly_sentiment.iloc[0]:.3f}"
            sentiment_trend += f"\n    最近月份平均情感得分：{monthly_sentiment.iloc[-1]:.3f}"
    
    prompt = f"""分析以下{brand_name}的评论时间趋势数据：
    评论数量趋势：{trend}
    平均每月评论数：{avg_monthly:.1f}
    评论最多的月份：{max_month}（{monthly_counts[max_month]}条）
    评论最少的月份：{min_month}（{monthly_counts[min_month]}条）{rating_trend}{sentiment_trend}
    
    请深入分析这个时间趋势的特点，包括：
    1. 品牌影响力随时间的变化趋势
    2. 用户满意度随时间的变化趋势
    3. 季节性波动及其可能的原因
    4. 高峰期和低谷期的特点及其与品牌活动的关联
    5. 品牌表现是否在改善或恶化，以及可能的原因
    6. 基于时间趋势，品牌应该采取的策略调整
    
    请用简洁的语言总结分析结果，重点突出品牌随时间变化的优势和劣势，并给出针对性的发展趋势建议。"""
    
    return call_ai_model(prompt)

def generate_comprehensive_analysis(df, brand_name):
    """生成综合分析报告"""
    analyses = {
        'rating': analyze_rating_distribution(df, brand_name),
        'country': analyze_country_distribution(df, brand_name),
        'sentiment': analyze_sentiment_trends(df, brand_name),
        'keywords': analyze_word_cloud(df, brand_name),
        'time': analyze_time_trends(df, brand_name)
    }
    
    # 过滤掉None值
    valid_analyses = {k: v for k, v in analyses.items() if v is not None}
    
    prompt = f"""基于以下{brand_name}的各个维度分析结果，生成一个全面深入的综合分析报告：

{json.dumps(valid_analyses, ensure_ascii=False, indent=2)}

请系统性地总结以下几个方面：

1. 品牌整体表现评估
   - 总体用户满意度水平
   - 品牌在市场中的定位和影响力
   - 品牌声誉的总体状况

2. 品牌核心优势（至少3-5点）
   - 具体列出品牌最突出的优势
   - 每个优势的具体表现和影响
   - 这些优势如何为品牌创造竞争力
   - 如何进一步强化这些优势

3. 品牌主要劣势和问题（至少3-5点）
   - 具体列出品牌最突出的问题和劣势
   - 每个问题的具体表现和影响
   - 这些问题如何影响用户体验和品牌声誉
   - 问题的严重程度和优先级排序

4. 具体可行的改进建议（至少5点）
   - 针对每个主要问题提出具体的改进措施
   - 建议的实施优先级和预期效果
   - 短期可立即实施的改进措施
   - 长期需要战略性调整的改进方向

5. 市场机会和发展方向
   - 基于用户反馈的潜在市场机会
   - 品牌可以拓展的新领域或新市场
   - 与竞争对手差异化的关键点

请用简洁专业的语言输出分析结果，确保分析具有可操作性和实用价值，能够直接指导品牌改进和发展策略。"""
    
    return call_ai_model(prompt)

def analyze_sentiment_trends(df, brand_name):
    """分析情感趋势"""
    sentiment_col = 'sentiment_category'
    if sentiment_col not in df.columns:
        return None
        
    sentiment_counts = df[sentiment_col].value_counts()
    total_reviews = len(df)
    
    # 计算正面和负面评价的比例
    positive_percentage = sentiment_counts.get('Positive', 0) / total_reviews * 100
    negative_percentage = sentiment_counts.get('Negative', 0) / total_reviews * 100
    neutral_percentage = sentiment_counts.get('Neutral', 0) / total_reviews * 100
    
    # 提取高分和低分评论的样本
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    if review_col:
        positive_samples = df[df[sentiment_col] == 'Positive'][review_col].sample(min(3, sentiment_counts.get('Positive', 0))).tolist()
        negative_samples = df[df[sentiment_col] == 'Negative'][review_col].sample(min(3, sentiment_counts.get('Negative', 0))).tolist()
        
        positive_examples = "\n".join([f"- {sample[:100]}..." for sample in positive_samples])
        negative_examples = "\n".join([f"- {sample[:100]}..." for sample in negative_samples])
    else:
        positive_examples = "无样本数据"
        negative_examples = "无样本数据"
    
    prompt = f"""分析以下{brand_name}的评论情感分布数据：
    总评论数：{total_reviews}
    正面评价：{sentiment_counts.get('Positive', 0)}条 ({positive_percentage:.1f}%)
    中性评价：{sentiment_counts.get('Neutral', 0)}条 ({neutral_percentage:.1f}%)
    负面评价：{sentiment_counts.get('Negative', 0)}条 ({negative_percentage:.1f}%)
    
    正面评价样本：
{positive_examples}
    
    负面评价样本：
{negative_examples}
    
    请深入分析这个情感分布的特点，包括：
    1. 整体情感倾向和用户满意度水平
    2. 正面评价中反映的品牌主要优势和亮点
    3. 负面评价中反映的品牌主要问题和痛点
    4. 用户投诉的主要焦点和表扬的核心方面
    5. 情感极化现象分析（如果存在）
    6. 针对负面情感，品牌应该采取的改进措施
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面。"""
    
    return call_ai_model(prompt)

def analyze_word_cloud(df, brand_name):
    """分析词云数据"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    sentiment_col = 'sentiment_category'
    if review_col is None:
        return None
        
    # 分别提取正面和负面评论中的关键词
    all_text = ' '.join(df[review_col].dropna().astype(str))
    
    # 设置停用词
    from wordcloud import STOPWORDS
    import string
    stopwords = set(STOPWORDS)
    custom_stopwords = {
        # 英文常见停用词
        'the', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'with', 'for', 'on', 'is', 'was', 'be',
        'this', 'have', 'from', 'or', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'there', 'can', 'an', 'your', 'which', 'their', 'said', 'if', 'will', 'my', 'one',
        'would', 'so', 'up', 'out', 'them', 'about', 'who', 'get', 'me', 'been', 'has', 'just',
        'do', 'did', 'doing', 'does', 'then', 'such', 'no', 'yes', 'they', 'also', 'any', 'are',
        
        # 品牌和产品相关词
        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
        
        # 电商常见词
        'shipping', 'delivery', 'arrived', 'package', 'item', 'items', 'customer', 'customers',
        'review', 'reviews', 'rating', 'ratings', 'star', 'stars', 'experience'
    }
    stopwords.update(custom_stopwords)
    
    # 处理文本，移除标点符号和停用词
    text = all_text.lower()
    for p in string.punctuation:
        text = text.replace(p, ' ')
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
    
    # 获取总体词频
    word_freq = pd.Series(filtered_words).value_counts().head(15)
    
    # 如果有情感分类列，分别提取正面和负面评论的关键词
    pos_word_freq = None
    neg_word_freq = None
    if sentiment_col in df.columns:
        pos_reviews = ' '.join(df[df[sentiment_col] == 'Positive'][review_col].dropna().astype(str))
        neg_reviews = ' '.join(df[df[sentiment_col] == 'Negative'][review_col].dropna().astype(str))
        
        # 处理正面评论文本
        pos_text = pos_reviews.lower()
        for p in string.punctuation:
            pos_text = pos_text.replace(p, ' ')
        pos_words = pos_text.split()
        pos_filtered = [word for word in pos_words if word not in stopwords and len(word) > 2]
        pos_word_freq = pd.Series(pos_filtered).value_counts().head(10)
        
        # 处理负面评论文本
        neg_text = neg_reviews.lower()
        for p in string.punctuation:
            neg_text = neg_text.replace(p, ' ')
        neg_words = neg_text.split()
        neg_filtered = [word for word in neg_words if word not in stopwords and len(word) > 2]
        neg_word_freq = pd.Series(neg_filtered).value_counts().head(10)
    
    # 构建提示词
    prompt = f"""分析以下{brand_name}的评论关键词数据：
    
    总体最常见的15个关键词及其出现次数：
    {', '.join([f'{word}: {count}次' for word, count in word_freq.items()])}
    """
    
    # 添加正面评论关键词
    if pos_word_freq is not None and len(pos_word_freq) > 0:
        prompt += f"""
    
    正面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in pos_word_freq.items()])}
    """
    
    # 添加负面评论关键词
    if neg_word_freq is not None and len(neg_word_freq) > 0:
        prompt += f"""
    
    负面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in neg_word_freq.items()])}
    """
    
    prompt += f"""
    
    请深入分析这些关键词的特点，包括：
    1. 用户最关注的产品/服务方面
    2. 正面评价中反映的品牌主要优势和特色
    3. 负面评价中反映的品牌主要问题和痛点
    4. 关键词与具体业务场景的关联（如产品质量、客户服务、物流配送等）
    5. 品牌应该重点改进的方面
    6. 品牌可以继续保持和强化的优势
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面，并给出具体可行的改进建议。"""
    
    return call_ai_model(prompt)

def analyze_time_trends(df, brand_name):
    """分析时间趋势"""
    date_col = next((col for col in df.columns if col.lower() == 'date'), None)
    if date_col is None:
        return None
        
    df['date'] = pd.to_datetime(df[date_col])
    monthly_counts = df.groupby(df['date'].dt.to_period('M')).size()
    
    if len(monthly_counts) <= 1:
        return None
    
    trend = 'increasing' if monthly_counts.iloc[-1] > monthly_counts.iloc[0] else 'decreasing'
    avg_monthly = monthly_counts.mean()
    max_month = monthly_counts.idxmax()
    min_month = monthly_counts.idxmin()
    
    # 分析评分随时间的变化趋势
    rating_trend = ""
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    if rating_col:
        # 计算每月平均评分
        monthly_ratings = df.groupby(df['date'].dt.to_period('M'))[rating_col].mean()
        if len(monthly_ratings) > 1:
            rating_trend = 'improving' if monthly_ratings.iloc[-1] > monthly_ratings.iloc[0] else 'declining'
            rating_trend = f"\n    评分趋势：{rating_trend}"
            rating_trend += f"\n    初始月份平均评分：{monthly_ratings.iloc[0]:.2f}星"
            rating_trend += f"\n    最近月份平均评分：{monthly_ratings.iloc[-1]:.2f}星"
    
    # 分析情感随时间的变化趋势
    sentiment_trend = ""
    sentiment_col = 'sentiment'
    if sentiment_col in df.columns:
        # 计算每月平均情感得分
        monthly_sentiment = df.groupby(df['date'].dt.to_period('M'))[sentiment_col].mean()
        if len(monthly_sentiment) > 1:
            sentiment_trend = 'improving' if monthly_sentiment.iloc[-1] > monthly_sentiment.iloc[0] else 'declining'
            sentiment_trend = f"\n    情感趋势：{sentiment_trend}"
            sentiment_trend += f"\n    初始月份平均情感得分：{monthly_sentiment.iloc[0]:.3f}"
            sentiment_trend += f"\n    最近月份平均情感得分：{monthly_sentiment.iloc[-1]:.3f}"
    
    prompt = f"""分析以下{brand_name}的评论时间趋势数据：
    评论数量趋势：{trend}
    平均每月评论数：{avg_monthly:.1f}
    评论最多的月份：{max_month}（{monthly_counts[max_month]}条）
    评论最少的月份：{min_month}（{monthly_counts[min_month]}条）{rating_trend}{sentiment_trend}
    
    请深入分析这个时间趋势的特点，包括：
    1. 品牌影响力随时间的变化趋势
    2. 用户满意度随时间的变化趋势
    3. 季节性波动及其可能的原因
    4. 高峰期和低谷期的特点及其与品牌活动的关联
    5. 品牌表现是否在改善或恶化，以及可能的原因
    6. 基于时间趋势，品牌应该采取的策略调整
    
    请用简洁的语言总结分析结果，重点突出品牌随时间变化的优势和劣势，并给出针对性的发展趋势建议。"""
    
    return call_ai_model(prompt)

def generate_comprehensive_analysis(df, brand_name):
    """生成综合分析报告"""
    analyses = {
        'rating': analyze_rating_distribution(df, brand_name),
        'country': analyze_country_distribution(df, brand_name),
        'sentiment': analyze_sentiment_trends(df, brand_name),
        'keywords': analyze_word_cloud(df, brand_name),
        'time': analyze_time_trends(df, brand_name)
    }
    
    # 过滤掉None值
    valid_analyses = {k: v for k, v in analyses.items() if v is not None}
    
    prompt = f"""基于以下{brand_name}的各个维度分析结果，生成一个全面深入的综合分析报告：

{json.dumps(valid_analyses, ensure_ascii=False, indent=2)}

请系统性地总结以下几个方面：

1. 品牌整体表现评估
   - 总体用户满意度水平
   - 品牌在市场中的定位和影响力
   - 品牌声誉的总体状况

2. 品牌核心优势（至少3-5点）
   - 具体列出品牌最突出的优势
   - 每个优势的具体表现和影响
   - 这些优势如何为品牌创造竞争力
   - 如何进一步强化这些优势

3. 品牌主要劣势和问题（至少3-5点）
   - 具体列出品牌最突出的问题和劣势
   - 每个问题的具体表现和影响
   - 这些问题如何影响用户体验和品牌声誉
   - 问题的严重程度和优先级排序

4. 具体可行的改进建议（至少5点）
   - 针对每个主要问题提出具体的改进措施
   - 建议的实施优先级和预期效果
   - 短期可立即实施的改进措施
   - 长期需要战略性调整的改进方向

5. 市场机会和发展方向
   - 基于用户反馈的潜在市场机会
   - 品牌可以拓展的新领域或新市场
   - 与竞争对手差异化的关键点

请用简洁专业的语言输出分析结果，确保分析具有可操作性和实用价值，能够直接指导品牌改进和发展策略。"""
    
    return call_ai_model(prompt)

def analyze_sentiment_trends(df, brand_name):
    """分析情感趋势"""
    sentiment_col = 'sentiment_category'
    if sentiment_col not in df.columns:
        return None
        
    sentiment_counts = df[sentiment_col].value_counts()
    total_reviews = len(df)
    
    # 计算正面和负面评价的比例
    positive_percentage = sentiment_counts.get('Positive', 0) / total_reviews * 100
    negative_percentage = sentiment_counts.get('Negative', 0) / total_reviews * 100
    neutral_percentage = sentiment_counts.get('Neutral', 0) / total_reviews * 100
    
    # 提取高分和低分评论的样本
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    if review_col:
        positive_samples = df[df[sentiment_col] == 'Positive'][review_col].sample(min(3, sentiment_counts.get('Positive', 0))).tolist()
        negative_samples = df[df[sentiment_col] == 'Negative'][review_col].sample(min(3, sentiment_counts.get('Negative', 0))).tolist()
        
        positive_examples = "\n".join([f"- {sample[:100]}..." for sample in positive_samples])
        negative_examples = "\n".join([f"- {sample[:100]}..." for sample in negative_samples])
    else:
        positive_examples = "无样本数据"
        negative_examples = "无样本数据"
    
    prompt = f"""分析以下{brand_name}的评论情感分布数据：
    总评论数：{total_reviews}
    正面评价：{sentiment_counts.get('Positive', 0)}条 ({positive_percentage:.1f}%)
    中性评价：{sentiment_counts.get('Neutral', 0)}条 ({neutral_percentage:.1f}%)
    负面评价：{sentiment_counts.get('Negative', 0)}条 ({negative_percentage:.1f}%)
    
    正面评价样本：
{positive_examples}
    
    负面评价样本：
{negative_examples}
    
    请深入分析这个情感分布的特点，包括：
    1. 整体情感倾向和用户满意度水平
    2. 正面评价中反映的品牌主要优势和亮点
    3. 负面评价中反映的品牌主要问题和痛点
    4. 用户投诉的主要焦点和表扬的核心方面
    5. 情感极化现象分析（如果存在）
    6. 针对负面情感，品牌应该采取的改进措施
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面。"""
    
    return call_ai_model(prompt)

def analyze_word_cloud(df, brand_name):
    """分析词云数据"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    sentiment_col = 'sentiment_category'
    if review_col is None:
        return None
        
    # 分别提取正面和负面评论中的关键词
    all_text = ' '.join(df[review_col].dropna().astype(str))
    
    # 设置停用词
    from wordcloud import STOPWORDS
    import string
    stopwords = set(STOPWORDS)
    custom_stopwords = {
        # 英文常见停用词
        'the', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'with', 'for', 'on', 'is', 'was', 'be',
        'this', 'have', 'from', 'or', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'there', 'can', 'an', 'your', 'which', 'their', 'said', 'if', 'will', 'my', 'one',
        'would', 'so', 'up', 'out', 'them', 'about', 'who', 'get', 'me', 'been', 'has', 'just',
        'do', 'did', 'doing', 'does', 'then', 'such', 'no', 'yes', 'they', 'also', 'any', 'are',
        
        # 品牌和产品相关词
        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
        
        # 电商常见词
        'shipping', 'delivery', 'arrived', 'package', 'item', 'items', 'customer', 'customers',
        'review', 'reviews', 'rating', 'ratings', 'star', 'stars', 'experience'
    }
    stopwords.update(custom_stopwords)
    
    # 处理文本，移除标点符号和停用词
    text = all_text.lower()
    for p in string.punctuation:
        text = text.replace(p, ' ')
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
    
    # 获取总体词频
    word_freq = pd.Series(filtered_words).value_counts().head(15)
    
    # 如果有情感分类列，分别提取正面和负面评论的关键词
    pos_word_freq = None
    neg_word_freq = None
    if sentiment_col in df.columns:
        pos_reviews = ' '.join(df[df[sentiment_col] == 'Positive'][review_col].dropna().astype(str))
        neg_reviews = ' '.join(df[df[sentiment_col] == 'Negative'][review_col].dropna().astype(str))
        
        # 处理正面评论文本
        pos_text = pos_reviews.lower()
        for p in string.punctuation:
            pos_text = pos_text.replace(p, ' ')
        pos_words = pos_text.split()
        pos_filtered = [word for word in pos_words if word not in stopwords and len(word) > 2]
        pos_word_freq = pd.Series(pos_filtered).value_counts().head(10)
        
        # 处理负面评论文本
        neg_text = neg_reviews.lower()
        for p in string.punctuation:
            neg_text = neg_text.replace(p, ' ')
        neg_words = neg_text.split()
        neg_filtered = [word for word in neg_words if word not in stopwords and len(word) > 2]
        neg_word_freq = pd.Series(neg_filtered).value_counts().head(10)
    
    # 构建提示词
    prompt = f"""分析以下{brand_name}的评论关键词数据：
    
    总体最常见的15个关键词及其出现次数：
    {', '.join([f'{word}: {count}次' for word, count in word_freq.items()])}
    """
    
    # 添加正面评论关键词
    if pos_word_freq is not None and len(pos_word_freq) > 0:
        prompt += f"""
    
    正面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in pos_word_freq.items()])}
    """
    
    # 添加负面评论关键词
    if neg_word_freq is not None and len(neg_word_freq) > 0:
        prompt += f"""
    
    负面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in neg_word_freq.items()])}
    """
    
    prompt += f"""
    
    请深入分析这些关键词的特点，包括：
    1. 用户最关注的产品/服务方面
    2. 正面评价中反映的品牌主要优势和特色
    3. 负面评价中反映的品牌主要问题和痛点
    4. 关键词与具体业务场景的关联（如产品质量、客户服务、物流配送等）
    5. 品牌应该重点改进的方面
    6. 品牌可以继续保持和强化的优势
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面，并给出具体可行的改进建议。"""
    
    return call_ai_model(prompt)

def analyze_time_trends(df, brand_name):
    """分析时间趋势"""
    date_col = next((col for col in df.columns if col.lower() == 'date'), None)
    if date_col is None:
        return None
        
    df['date'] = pd.to_datetime(df[date_col])
    monthly_counts = df.groupby(df['date'].dt.to_period('M')).size()
    
    if len(monthly_counts) <= 1:
        return None
    
    trend = 'increasing' if monthly_counts.iloc[-1] > monthly_counts.iloc[0] else 'decreasing'
    avg_monthly = monthly_counts.mean()
    max_month = monthly_counts.idxmax()
    min_month = monthly_counts.idxmin()
    
    # 分析评分随时间的变化趋势
    rating_trend = ""
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    if rating_col:
        # 计算每月平均评分
        monthly_ratings = df.groupby(df['date'].dt.to_period('M'))[rating_col].mean()
        if len(monthly_ratings) > 1:
            rating_trend = 'improving' if monthly_ratings.iloc[-1] > monthly_ratings.iloc[0] else 'declining'
            rating_trend = f"\n    评分趋势：{rating_trend}"
            rating_trend += f"\n    初始月份平均评分：{monthly_ratings.iloc[0]:.2f}星"
            rating_trend += f"\n    最近月份平均评分：{monthly_ratings.iloc[-1]:.2f}星"
    
    # 分析情感随时间的变化趋势
    sentiment_trend = ""
    sentiment_col = 'sentiment'
    if sentiment_col in df.columns:
        # 计算每月平均情感得分
        monthly_sentiment = df.groupby(df['date'].dt.to_period('M'))[sentiment_col].mean()
        if len(monthly_sentiment) > 1:
            sentiment_trend = 'improving' if monthly_sentiment.iloc[-1] > monthly_sentiment.iloc[0] else 'declining'
            sentiment_trend = f"\n    情感趋势：{sentiment_trend}"
            sentiment_trend += f"\n    初始月份平均情感得分：{monthly_sentiment.iloc[0]:.3f}"
            sentiment_trend += f"\n    最近月份平均情感得分：{monthly_sentiment.iloc[-1]:.3f}"
    
    prompt = f"""分析以下{brand_name}的评论时间趋势数据：
    评论数量趋势：{trend}
    平均每月评论数：{avg_monthly:.1f}
    评论最多的月份：{max_month}（{monthly_counts[max_month]}条）
    评论最少的月份：{min_month}（{monthly_counts[min_month]}条）{rating_trend}{sentiment_trend}
    
    请深入分析这个时间趋势的特点，包括：
    1. 品牌影响力随时间的变化趋势
    2. 用户满意度随时间的变化趋势
    3. 季节性波动及其可能的原因
    4. 高峰期和低谷期的特点及其与品牌活动的关联
    5. 品牌表现是否在改善或恶化，以及可能的原因
    6. 基于时间趋势，品牌应该采取的策略调整
    
    请用简洁的语言总结分析结果，重点突出品牌随时间变化的优势和劣势，并给出针对性的发展趋势建议。"""
    
    return call_ai_model(prompt)

def generate_comprehensive_analysis(df, brand_name):
    """生成综合分析报告"""
    analyses = {
        'rating': analyze_rating_distribution(df, brand_name),
        'country': analyze_country_distribution(df, brand_name),
        'sentiment': analyze_sentiment_trends(df, brand_name),
        'keywords': analyze_word_cloud(df, brand_name),
        'time': analyze_time_trends(df, brand_name)
    }
    
    # 过滤掉None值
    valid_analyses = {k: v for k, v in analyses.items() if v is not None}
    
    prompt = f"""基于以下{brand_name}的各个维度分析结果，生成一个全面深入的综合分析报告：

{json.dumps(valid_analyses, ensure_ascii=False, indent=2)}

请系统性地总结以下几个方面：

1. 品牌整体表现评估
   - 总体用户满意度水平
   - 品牌在市场中的定位和影响力
   - 品牌声誉的总体状况

2. 品牌核心优势（至少3-5点）
   - 具体列出品牌最突出的优势
   - 每个优势的具体表现和影响
   - 这些优势如何为品牌创造竞争力
   - 如何进一步强化这些优势

3. 品牌主要劣势和问题（至少3-5点）
   - 具体列出品牌最突出的问题和劣势
   - 每个问题的具体表现和影响
   - 这些问题如何影响用户体验和品牌声誉
   - 问题的严重程度和优先级排序

4. 具体可行的改进建议（至少5点）
   - 针对每个主要问题提出具体的改进措施
   - 建议的实施优先级和预期效果
   - 短期可立即实施的改进措施
   - 长期需要战略性调整的改进方向

5. 市场机会和发展方向
   - 基于用户反馈的潜在市场机会
   - 品牌可以拓展的新领域或新市场
   - 与竞争对手差异化的关键点

请用简洁专业的语言输出分析结果，确保分析具有可操作性和实用价值，能够直接指导品牌改进和发展策略。"""
    
    return call_ai_model(prompt)

def analyze_sentiment_trends(df, brand_name):
    """分析情感趋势"""
    sentiment_col = 'sentiment_category'
    if sentiment_col not in df.columns:
        return None
        
    sentiment_counts = df[sentiment_col].value_counts()
    total_reviews = len(df)
    
    # 计算正面和负面评价的比例
    positive_percentage = sentiment_counts.get('Positive', 0) / total_reviews * 100
    negative_percentage = sentiment_counts.get('Negative', 0) / total_reviews * 100
    neutral_percentage = sentiment_counts.get('Neutral', 0) / total_reviews * 100
    
    # 提取高分和低分评论的样本
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    if review_col:
        positive_samples = df[df[sentiment_col] == 'Positive'][review_col].sample(min(3, sentiment_counts.get('Positive', 0))).tolist()
        negative_samples = df[df[sentiment_col] == 'Negative'][review_col].sample(min(3, sentiment_counts.get('Negative', 0))).tolist()
        
        positive_examples = "\n".join([f"- {sample[:100]}..." for sample in positive_samples])
        negative_examples = "\n".join([f"- {sample[:100]}..." for sample in negative_samples])
    else:
        positive_examples = "无样本数据"
        negative_examples = "无样本数据"
    
    prompt = f"""分析以下{brand_name}的评论情感分布数据：
    总评论数：{total_reviews}
    正面评价：{sentiment_counts.get('Positive', 0)}条 ({positive_percentage:.1f}%)
    中性评价：{sentiment_counts.get('Neutral', 0)}条 ({neutral_percentage:.1f}%)
    负面评价：{sentiment_counts.get('Negative', 0)}条 ({negative_percentage:.1f}%)
    
    正面评价样本：
{positive_examples}
    
    负面评价样本：
{negative_examples}
    
    请深入分析这个情感分布的特点，包括：
    1. 整体情感倾向和用户满意度水平
    2. 正面评价中反映的品牌主要优势和亮点
    3. 负面评价中反映的品牌主要问题和痛点
    4. 用户投诉的主要焦点和表扬的核心方面
    5. 情感极化现象分析（如果存在）
    6. 针对负面情感，品牌应该采取的改进措施
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面。"""
    
    return call_ai_model(prompt)

def analyze_word_cloud(df, brand_name):
    """分析词云数据"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    sentiment_col = 'sentiment_category'
    if review_col is None:
        return None
        
    # 分别提取正面和负面评论中的关键词
    all_text = ' '.join(df[review_col].dropna().astype(str))
    
    # 设置停用词
    from wordcloud import STOPWORDS
    import string
    stopwords = set(STOPWORDS)
    custom_stopwords = {
        # 英文常见停用词
        'the', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'with', 'for', 'on', 'is', 'was', 'be',
        'this', 'have', 'from', 'or', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'there', 'can', 'an', 'your', 'which', 'their', 'said', 'if', 'will', 'my', 'one',
        'would', 'so', 'up', 'out', 'them', 'about', 'who', 'get', 'me', 'been', 'has', 'just',
        'do', 'did', 'doing', 'does', 'then', 'such', 'no', 'yes', 'they', 'also', 'any', 'are',
        
        # 品牌和产品相关词
        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
        
        # 电商常见词
        'shipping', 'delivery', 'arrived', 'package', 'item', 'items', 'customer', 'customers',
        'review', 'reviews', 'rating', 'ratings', 'star', 'stars', 'experience'
    }
    stopwords.update(custom_stopwords)
    
    # 处理文本，移除标点符号和停用词
    text = all_text.lower()
    for p in string.punctuation:
        text = text.replace(p, ' ')
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
    
    # 获取总体词频
    word_freq = pd.Series(filtered_words).value_counts().head(15)
    
    # 如果有情感分类列，分别提取正面和负面评论的关键词
    pos_word_freq = None
    neg_word_freq = None
    if sentiment_col in df.columns:
        pos_reviews = ' '.join(df[df[sentiment_col] == 'Positive'][review_col].dropna().astype(str))
        neg_reviews = ' '.join(df[df[sentiment_col] == 'Negative'][review_col].dropna().astype(str))
        
        # 处理正面评论文本
        pos_text = pos_reviews.lower()
        for p in string.punctuation:
            pos_text = pos_text.replace(p, ' ')
        pos_words = pos_text.split()
        pos_filtered = [word for word in pos_words if word not in stopwords and len(word) > 2]
        pos_word_freq = pd.Series(pos_filtered).value_counts().head(10)
        
        # 处理负面评论文本
        neg_text = neg_reviews.lower()
        for p in string.punctuation:
            neg_text = neg_text.replace(p, ' ')
        neg_words = neg_text.split()
        neg_filtered = [word for word in neg_words if word not in stopwords and len(word) > 2]
        neg_word_freq = pd.Series(neg_filtered).value_counts().head(10)
    
    # 构建提示词
    prompt = f"""分析以下{brand_name}的评论关键词数据：
    
    总体最常见的15个关键词及其出现次数：
    {', '.join([f'{word}: {count}次' for word, count in word_freq.items()])}
    """
    
    # 添加正面评论关键词
    if pos_word_freq is not None and len(pos_word_freq) > 0:
        prompt += f"""
    
    正面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in pos_word_freq.items()])}
    """
    
    # 添加负面评论关键词
    if neg_word_freq is not None and len(neg_word_freq) > 0:
        prompt += f"""
    
    负面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in neg_word_freq.items()])}
    """
    
    prompt += f"""
    
    请深入分析这些关键词的特点，包括：
    1. 用户最关注的产品/服务方面
    2. 正面评价中反映的品牌主要优势和特色
    3. 负面评价中反映的品牌主要问题和痛点
    4. 关键词与具体业务场景的关联（如产品质量、客户服务、物流配送等）
    5. 品牌应该重点改进的方面
    6. 品牌可以继续保持和强化的优势
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面，并给出具体可行的改进建议。"""
    
    return call_ai_model(prompt)

def analyze_time_trends(df, brand_name):
    """分析时间趋势"""
    date_col = next((col for col in df.columns if col.lower() == 'date'), None)
    if date_col is None:
        return None
        
    df['date'] = pd.to_datetime(df[date_col])
    monthly_counts = df.groupby(df['date'].dt.to_period('M')).size()
    
    if len(monthly_counts) <= 1:
        return None
    
    trend = 'increasing' if monthly_counts.iloc[-1] > monthly_counts.iloc[0] else 'decreasing'
    avg_monthly = monthly_counts.mean()
    max_month = monthly_counts.idxmax()
    min_month = monthly_counts.idxmin()
    
    # 分析评分随时间的变化趋势
    rating_trend = ""
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    if rating_col:
        # 计算每月平均评分
        monthly_ratings = df.groupby(df['date'].dt.to_period('M'))[rating_col].mean()
        if len(monthly_ratings) > 1:
            rating_trend = 'improving' if monthly_ratings.iloc[-1] > monthly_ratings.iloc[0] else 'declining'
            rating_trend = f"\n    评分趋势：{rating_trend}"
            rating_trend += f"\n    初始月份平均评分：{monthly_ratings.iloc[0]:.2f}星"
            rating_trend += f"\n    最近月份平均评分：{monthly_ratings.iloc[-1]:.2f}星"
    
    # 分析情感随时间的变化趋势
    sentiment_trend = ""
    sentiment_col = 'sentiment'
    if sentiment_col in df.columns:
        # 计算每月平均情感得分
        monthly_sentiment = df.groupby(df['date'].dt.to_period('M'))[sentiment_col].mean()
        if len(monthly_sentiment) > 1:
            sentiment_trend = 'improving' if monthly_sentiment.iloc[-1] > monthly_sentiment.iloc[0] else 'declining'
            sentiment_trend = f"\n    情感趋势：{sentiment_trend}"
            sentiment_trend += f"\n    初始月份平均情感得分：{monthly_sentiment.iloc[0]:.3f}"
            sentiment_trend += f"\n    最近月份平均情感得分：{monthly_sentiment.iloc[-1]:.3f}"
    
    prompt = f"""分析以下{brand_name}的评论时间趋势数据：
    评论数量趋势：{trend}
    平均每月评论数：{avg_monthly:.1f}
    评论最多的月份：{max_month}（{monthly_counts[max_month]}条）
    评论最少的月份：{min_month}（{monthly_counts[min_month]}条）{rating_trend}{sentiment_trend}
    
    请深入分析这个时间趋势的特点，包括：
    1. 品牌影响力随时间的变化趋势
    2. 用户满意度随时间的变化趋势
    3. 季节性波动及其可能的原因
    4. 高峰期和低谷期的特点及其与品牌活动的关联
    5. 品牌表现是否在改善或恶化，以及可能的原因
    6. 基于时间趋势，品牌应该采取的策略调整
    
    请用简洁的语言总结分析结果，重点突出品牌随时间变化的优势和劣势，并给出针对性的发展趋势建议。"""
    
    return call_ai_model(prompt)

def generate_comprehensive_analysis(df, brand_name):
    """生成综合分析报告"""
    analyses = {
        'rating': analyze_rating_distribution(df, brand_name),
        'country': analyze_country_distribution(df, brand_name),
        'sentiment': analyze_sentiment_trends(df, brand_name),
        'keywords': analyze_word_cloud(df, brand_name),
        'time': analyze_time_trends(df, brand_name)
    }
    
    # 过滤掉None值
    valid_analyses = {k: v for k, v in analyses.items() if v is not None}
    
    prompt = f"""基于以下{brand_name}的各个维度分析结果，生成一个全面深入的综合分析报告：

{json.dumps(valid_analyses, ensure_ascii=False, indent=2)}

请系统性地总结以下几个方面：

1. 品牌整体表现评估
   - 总体用户满意度水平
   - 品牌在市场中的定位和影响力
   - 品牌声誉的总体状况

2. 品牌核心优势（至少3-5点）
   - 具体列出品牌最突出的优势
   - 每个优势的具体表现和影响
   - 这些优势如何为品牌创造竞争力
   - 如何进一步强化这些优势

3. 品牌主要劣势和问题（至少3-5点）
   - 具体列出品牌最突出的问题和劣势
   - 每个问题的具体表现和影响
   - 这些问题如何影响用户体验和品牌声誉
   - 问题的严重程度和优先级排序

4. 具体可行的改进建议（至少5点）
   - 针对每个主要问题提出具体的改进措施
   - 建议的实施优先级和预期效果
   - 短期可立即实施的改进措施
   - 长期需要战略性调整的改进方向

5. 市场机会和发展方向
   - 基于用户反馈的潜在市场机会
   - 品牌可以拓展的新领域或新市场
   - 与竞争对手差异化的关键点

请用简洁专业的语言输出分析结果，确保分析具有可操作性和实用价值，能够直接指导品牌改进和发展策略。"""
    
    return call_ai_model(prompt)

def analyze_sentiment_trends(df, brand_name):
    """分析情感趋势"""
    sentiment_col = 'sentiment_category'
    if sentiment_col not in df.columns:
        return None
        
    sentiment_counts = df[sentiment_col].value_counts()
    total_reviews = len(df)
    
    # 计算正面和负面评价的比例
    positive_percentage = sentiment_counts.get('Positive', 0) / total_reviews * 100
    negative_percentage = sentiment_counts.get('Negative', 0) / total_reviews * 100
    neutral_percentage = sentiment_counts.get('Neutral', 0) / total_reviews * 100
    
    # 提取高分和低分评论的样本
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    if review_col:
        positive_samples = df[df[sentiment_col] == 'Positive'][review_col].sample(min(3, sentiment_counts.get('Positive', 0))).tolist()
        negative_samples = df[df[sentiment_col] == 'Negative'][review_col].sample(min(3, sentiment_counts.get('Negative', 0))).tolist()
        
        positive_examples = "\n".join([f"- {sample[:100]}..." for sample in positive_samples])
        negative_examples = "\n".join([f"- {sample[:100]}..." for sample in negative_samples])
    else:
        positive_examples = "无样本数据"
        negative_examples = "无样本数据"
    
    prompt = f"""分析以下{brand_name}的评论情感分布数据：
    总评论数：{total_reviews}
    正面评价：{sentiment_counts.get('Positive', 0)}条 ({positive_percentage:.1f}%)
    中性评价：{sentiment_counts.get('Neutral', 0)}条 ({neutral_percentage:.1f}%)
    负面评价：{sentiment_counts.get('Negative', 0)}条 ({negative_percentage:.1f}%)
    
    正面评价样本：
{positive_examples}
    
    负面评价样本：
{negative_examples}
    
    请深入分析这个情感分布的特点，包括：
    1. 整体情感倾向和用户满意度水平
    2. 正面评价中反映的品牌主要优势和亮点
    3. 负面评价中反映的品牌主要问题和痛点
    4. 用户投诉的主要焦点和表扬的核心方面
    5. 情感极化现象分析（如果存在）
    6. 针对负面情感，品牌应该采取的改进措施
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面。"""
    
    return call_ai_model(prompt)

def analyze_word_cloud(df, brand_name):
    """分析词云数据"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    sentiment_col = 'sentiment_category'
    if review_col is None:
        return None
        
    # 分别提取正面和负面评论中的关键词
    all_text = ' '.join(df[review_col].dropna().astype(str))
    
    # 设置停用词
    from wordcloud import STOPWORDS
    import string
    stopwords = set(STOPWORDS)
    custom_stopwords = {
        # 英文常见停用词
        'the', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'with', 'for', 'on', 'is', 'was', 'be',
        'this', 'have', 'from', 'or', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'there', 'can', 'an', 'your', 'which', 'their', 'said', 'if', 'will', 'my', 'one',
        'would', 'so', 'up', 'out', 'them', 'about', 'who', 'get', 'me', 'been', 'has', 'just',
        'do', 'did', 'doing', 'does', 'then', 'such', 'no', 'yes', 'they', 'also', 'any', 'are',
        
        # 品牌和产品相关词
        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
        
        # 电商常见词
        'shipping', 'delivery', 'arrived', 'package', 'item', 'items', 'customer', 'customers',
        'review', 'reviews', 'rating', 'ratings', 'star', 'stars', 'experience'
    }
    stopwords.update(custom_stopwords)
    
    # 处理文本，移除标点符号和停用词
    text = all_text.lower()
    for p in string.punctuation:
        text = text.replace(p, ' ')
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
    
    # 获取总体词频
    word_freq = pd.Series(filtered_words).value_counts().head(15)
    
    # 如果有情感分类列，分别提取正面和负面评论的关键词
    pos_word_freq = None
    neg_word_freq = None
    if sentiment_col in df.columns:
        pos_reviews = ' '.join(df[df[sentiment_col] == 'Positive'][review_col].dropna().astype(str))
        neg_reviews = ' '.join(df[df[sentiment_col] == 'Negative'][review_col].dropna().astype(str))
        
        # 处理正面评论文本
        pos_text = pos_reviews.lower()
        for p in string.punctuation:
            pos_text = pos_text.replace(p, ' ')
        pos_words = pos_text.split()
        pos_filtered = [word for word in pos_words if word not in stopwords and len(word) > 2]
        pos_word_freq = pd.Series(pos_filtered).value_counts().head(10)
        
        # 处理负面评论文本
        neg_text = neg_reviews.lower()
        for p in string.punctuation:
            neg_text = neg_text.replace(p, ' ')
        neg_words = neg_text.split()
        neg_filtered = [word for word in neg_words if word not in stopwords and len(word) > 2]
        neg_word_freq = pd.Series(neg_filtered).value_counts().head(10)
    
    # 构建提示词
    prompt = f"""分析以下{brand_name}的评论关键词数据：
    
    总体最常见的15个关键词及其出现次数：
    {', '.join([f'{word}: {count}次' for word, count in word_freq.items()])}
    """
    
    # 添加正面评论关键词
    if pos_word_freq is not None and len(pos_word_freq) > 0:
        prompt += f"""
    
    正面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in pos_word_freq.items()])}
    """
    
    # 添加负面评论关键词
    if neg_word_freq is not None and len(neg_word_freq) > 0:
        prompt += f"""
    
    负面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in neg_word_freq.items()])}
    """
    
    prompt += f"""
    
    请深入分析这些关键词的特点，包括：
    1. 用户最关注的产品/服务方面
    2. 正面评价中反映的品牌主要优势和特色
    3. 负面评价中反映的品牌主要问题和痛点
    4. 关键词与具体业务场景的关联（如产品质量、客户服务、物流配送等）
    5. 品牌应该重点改进的方面
    6. 品牌可以继续保持和强化的优势
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面，并给出具体可行的改进建议。"""
    
    return call_ai_model(prompt)

def analyze_time_trends(df, brand_name):
    """分析时间趋势"""
    date_col = next((col for col in df.columns if col.lower() == 'date'), None)
    if date_col is None:
        return None
        
    df['date'] = pd.to_datetime(df[date_col])
    monthly_counts = df.groupby(df['date'].dt.to_period('M')).size()
    
    if len(monthly_counts) <= 1:
        return None
    
    trend = 'increasing' if monthly_counts.iloc[-1] > monthly_counts.iloc[0] else 'decreasing'
    avg_monthly = monthly_counts.mean()
    max_month = monthly_counts.idxmax()
    min_month = monthly_counts.idxmin()
    
    # 分析评分随时间的变化趋势
    rating_trend = ""
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    if rating_col:
        # 计算每月平均评分
        monthly_ratings = df.groupby(df['date'].dt.to_period('M'))[rating_col].mean()
        if len(monthly_ratings) > 1:
            rating_trend = 'improving' if monthly_ratings.iloc[-1] > monthly_ratings.iloc[0] else 'declining'
            rating_trend = f"\n    评分趋势：{rating_trend}"
            rating_trend += f"\n    初始月份平均评分：{monthly_ratings.iloc[0]:.2f}星"
            rating_trend += f"\n    最近月份平均评分：{monthly_ratings.iloc[-1]:.2f}星"
    
    # 分析情感随时间的变化趋势
    sentiment_trend = ""
    sentiment_col = 'sentiment'
    if sentiment_col in df.columns:
        # 计算每月平均情感得分
        monthly_sentiment = df.groupby(df['date'].dt.to_period('M'))[sentiment_col].mean()
        if len(monthly_sentiment) > 1:
            sentiment_trend = 'improving' if monthly_sentiment.iloc[-1] > monthly_sentiment.iloc[0] else 'declining'
            sentiment_trend = f"\n    情感趋势：{sentiment_trend}"
            sentiment_trend += f"\n    初始月份平均情感得分：{monthly_sentiment.iloc[0]:.3f}"
            sentiment_trend += f"\n    最近月份平均情感得分：{monthly_sentiment.iloc[-1]:.3f}"
    
    prompt = f"""分析以下{brand_name}的评论时间趋势数据：
    评论数量趋势：{trend}
    平均每月评论数：{avg_monthly:.1f}
    评论最多的月份：{max_month}（{monthly_counts[max_month]}条）
    评论最少的月份：{min_month}（{monthly_counts[min_month]}条）{rating_trend}{sentiment_trend}
    
    请深入分析这个时间趋势的特点，包括：
    1. 品牌影响力随时间的变化趋势
    2. 用户满意度随时间的变化趋势
    3. 季节性波动及其可能的原因
    4. 高峰期和低谷期的特点及其与品牌活动的关联
    5. 品牌表现是否在改善或恶化，以及可能的原因
    6. 基于时间趋势，品牌应该采取的策略调整
    
    请用简洁的语言总结分析结果，重点突出品牌随时间变化的优势和劣势，并给出针对性的发展趋势建议。"""
    
    return call_ai_model(prompt)

def generate_comprehensive_analysis(df, brand_name):
    """生成综合分析报告"""
    analyses = {
        'rating': analyze_rating_distribution(df, brand_name),
        'country': analyze_country_distribution(df, brand_name),
        'sentiment': analyze_sentiment_trends(df, brand_name),
        'keywords': analyze_word_cloud(df, brand_name),
        'time': analyze_time_trends(df, brand_name)
    }
    
    # 过滤掉None值
    valid_analyses = {k: v for k, v in analyses.items() if v is not None}
    
    prompt = f"""基于以下{brand_name}的各个维度分析结果，生成一个全面深入的综合分析报告：

{json.dumps(valid_analyses, ensure_ascii=False, indent=2)}

请系统性地总结以下几个方面：

1. 品牌整体表现评估
   - 总体用户满意度水平
   - 品牌在市场中的定位和影响力
   - 品牌声誉的总体状况

2. 品牌核心优势（至少3-5点）
   - 具体列出品牌最突出的优势
   - 每个优势的具体表现和影响
   - 这些优势如何为品牌创造竞争力
   - 如何进一步强化这些优势

3. 品牌主要劣势和问题（至少3-5点）
   - 具体列出品牌最突出的问题和劣势
   - 每个问题的具体表现和影响
   - 这些问题如何影响用户体验和品牌声誉
   - 问题的严重程度和优先级排序

4. 具体可行的改进建议（至少5点）
   - 针对每个主要问题提出具体的改进措施
   - 建议的实施优先级和预期效果
   - 短期可立即实施的改进措施
   - 长期需要战略性调整的改进方向

5. 市场机会和发展方向
   - 基于用户反馈的潜在市场机会
   - 品牌可以拓展的新领域或新市场
   - 与竞争对手差异化的关键点

请用简洁专业的语言输出分析结果，确保分析具有可操作性和实用价值，能够直接指导品牌改进和发展策略。"""
    
    return call_ai_model(prompt)

def analyze_sentiment_trends(df, brand_name):
    """分析情感趋势"""
    sentiment_col = 'sentiment_category'
    if sentiment_col not in df.columns:
        return None
        
    sentiment_counts = df[sentiment_col].value_counts()
    total_reviews = len(df)
    
    # 计算正面和负面评价的比例
    positive_percentage = sentiment_counts.get('Positive', 0) / total_reviews * 100
    negative_percentage = sentiment_counts.get('Negative', 0) / total_reviews * 100
    neutral_percentage = sentiment_counts.get('Neutral', 0) / total_reviews * 100
    
    # 提取高分和低分评论的样本
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    if review_col:
        positive_samples = df[df[sentiment_col] == 'Positive'][review_col].sample(min(3, sentiment_counts.get('Positive', 0))).tolist()
        negative_samples = df[df[sentiment_col] == 'Negative'][review_col].sample(min(3, sentiment_counts.get('Negative', 0))).tolist()
        
        positive_examples = "\n".join([f"- {sample[:100]}..." for sample in positive_samples])
        negative_examples = "\n".join([f"- {sample[:100]}..." for sample in negative_samples])
    else:
        positive_examples = "无样本数据"
        negative_examples = "无样本数据"
    
    prompt = f"""分析以下{brand_name}的评论情感分布数据：
    总评论数：{total_reviews}
    正面评价：{sentiment_counts.get('Positive', 0)}条 ({positive_percentage:.1f}%)
    中性评价：{sentiment_counts.get('Neutral', 0)}条 ({neutral_percentage:.1f}%)
    负面评价：{sentiment_counts.get('Negative', 0)}条 ({negative_percentage:.1f}%)
    
    正面评价样本：
{positive_examples}
    
    负面评价样本：
{negative_examples}
    
    请深入分析这个情感分布的特点，包括：
    1. 整体情感倾向和用户满意度水平
    2. 正面评价中反映的品牌主要优势和亮点
    3. 负面评价中反映的品牌主要问题和痛点
    4. 用户投诉的主要焦点和表扬的核心方面
    5. 情感极化现象分析（如果存在）
    6. 针对负面情感，品牌应该采取的改进措施
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面。"""
    
    return call_ai_model(prompt)

def analyze_word_cloud(df, brand_name):
    """分析词云数据"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    sentiment_col = 'sentiment_category'
    if review_col is None:
        return None
        
    # 分别提取正面和负面评论中的关键词
    all_text = ' '.join(df[review_col].dropna().astype(str))
    
    # 设置停用词
    from wordcloud import STOPWORDS
    import string
    stopwords = set(STOPWORDS)
    custom_stopwords = {
        # 英文常见停用词
        'the', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'with', 'for', 'on', 'is', 'was', 'be',
        'this', 'have', 'from', 'or', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'there', 'can', 'an', 'your', 'which', 'their', 'said', 'if', 'will', 'my', 'one',
        'would', 'so', 'up', 'out', 'them', 'about', 'who', 'get', 'me', 'been', 'has', 'just',
        'do', 'did', 'doing', 'does', 'then', 'such', 'no', 'yes', 'they', 'also', 'any', 'are',
        
        # 品牌和产品相关词
        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
        
        # 电商常见词
        'shipping', 'delivery', 'arrived', 'package', 'item', 'items', 'customer', 'customers',
        'review', 'reviews', 'rating', 'ratings', 'star', 'stars', 'experience'
    }
    stopwords.update(custom_stopwords)
    
    # 处理文本，移除标点符号和停用词
    text = all_text.lower()
    for p in string.punctuation:
        text = text.replace(p, ' ')
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
    
    # 获取总体词频
    word_freq = pd.Series(filtered_words).value_counts().head(15)
    
    # 如果有情感分类列，分别提取正面和负面评论的关键词
    pos_word_freq = None
    neg_word_freq = None
    if sentiment_col in df.columns:
        pos_reviews = ' '.join(df[df[sentiment_col] == 'Positive'][review_col].dropna().astype(str))
        neg_reviews = ' '.join(df[df[sentiment_col] == 'Negative'][review_col].dropna().astype(str))
        
        # 处理正面评论文本
        pos_text = pos_reviews.lower()
        for p in string.punctuation:
            pos_text = pos_text.replace(p, ' ')
        pos_words = pos_text.split()
        pos_filtered = [word for word in pos_words if word not in stopwords and len(word) > 2]
        pos_word_freq = pd.Series(pos_filtered).value_counts().head(10)
        
        # 处理负面评论文本
        neg_text = neg_reviews.lower()
        for p in string.punctuation:
            neg_text = neg_text.replace(p, ' ')
        neg_words = neg_text.split()
        neg_filtered = [word for word in neg_words if word not in stopwords and len(word) > 2]
        neg_word_freq = pd.Series(neg_filtered).value_counts().head(10)
    
    # 构建提示词
    prompt = f"""分析以下{brand_name}的评论关键词数据：
    
    总体最常见的15个关键词及其出现次数：
    {', '.join([f'{word}: {count}次' for word, count in word_freq.items()])}
    """
    
    # 添加正面评论关键词
    if pos_word_freq is not None and len(pos_word_freq) > 0:
        prompt += f"""
    
    正面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in pos_word_freq.items()])}
    """
    
    # 添加负面评论关键词
    if neg_word_freq is not None and len(neg_word_freq) > 0:
        prompt += f"""
    
    负面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in neg_word_freq.items()])}
    """
    
    prompt += f"""
    
    请深入分析这些关键词的特点，包括：
    1. 用户最关注的产品/服务方面
    2. 正面评价中反映的品牌主要优势和特色
    3. 负面评价中反映的品牌主要问题和痛点
    4. 关键词与具体业务场景的关联（如产品质量、客户服务、物流配送等）
    5. 品牌应该重点改进的方面
    6. 品牌可以继续保持和强化的优势
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面，并给出具体可行的改进建议。"""
    
    return call_ai_model(prompt)

def analyze_time_trends(df, brand_name):
    """分析时间趋势"""
    date_col = next((col for col in df.columns if col.lower() == 'date'), None)
    if date_col is None:
        return None
        
    df['date'] = pd.to_datetime(df[date_col])
    monthly_counts = df.groupby(df['date'].dt.to_period('M')).size()
    
    if len(monthly_counts) <= 1:
        return None
    
    trend = 'increasing' if monthly_counts.iloc[-1] > monthly_counts.iloc[0] else 'decreasing'
    avg_monthly = monthly_counts.mean()
    max_month = monthly_counts.idxmax()
    min_month = monthly_counts.idxmin()
    
    # 分析评分随时间的变化趋势
    rating_trend = ""
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    if rating_col:
        # 计算每月平均评分
        monthly_ratings = df.groupby(df['date'].dt.to_period('M'))[rating_col].mean()
        if len(monthly_ratings) > 1:
            rating_trend = 'improving' if monthly_ratings.iloc[-1] > monthly_ratings.iloc[0] else 'declining'
            rating_trend = f"\n    评分趋势：{rating_trend}"
            rating_trend += f"\n    初始月份平均评分：{monthly_ratings.iloc[0]:.2f}星"
            rating_trend += f"\n    最近月份平均评分：{monthly_ratings.iloc[-1]:.2f}星"
    
    # 分析情感随时间的变化趋势
    sentiment_trend = ""
    sentiment_col = 'sentiment'
    if sentiment_col in df.columns:
        # 计算每月平均情感得分
        monthly_sentiment = df.groupby(df['date'].dt.to_period('M'))[sentiment_col].mean()
        if len(monthly_sentiment) > 1:
            sentiment_trend = 'improving' if monthly_sentiment.iloc[-1] > monthly_sentiment.iloc[0] else 'declining'
            sentiment_trend = f"\n    情感趋势：{sentiment_trend}"
            sentiment_trend += f"\n    初始月份平均情感得分：{monthly_sentiment.iloc[0]:.3f}"
            sentiment_trend += f"\n    最近月份平均情感得分：{monthly_sentiment.iloc[-1]:.3f}"
    
    prompt = f"""分析以下{brand_name}的评论时间趋势数据：
    评论数量趋势：{trend}
    平均每月评论数：{avg_monthly:.1f}
    评论最多的月份：{max_month}（{monthly_counts[max_month]}条）
    评论最少的月份：{min_month}（{monthly_counts[min_month]}条）{rating_trend}{sentiment_trend}
    
    请深入分析这个时间趋势的特点，包括：
    1. 品牌影响力随时间的变化趋势
    2. 用户满意度随时间的变化趋势
    3. 季节性波动及其可能的原因
    4. 高峰期和低谷期的特点及其与品牌活动的关联
    5. 品牌表现是否在改善或恶化，以及可能的原因
    6. 基于时间趋势，品牌应该采取的策略调整
    
    请用简洁的语言总结分析结果，重点突出品牌随时间变化的优势和劣势，并给出针对性的发展趋势建议。"""
    
    return call_ai_model(prompt)

def generate_comprehensive_analysis(df, brand_name):
    """生成综合分析报告"""
    analyses = {
        'rating': analyze_rating_distribution(df, brand_name),
        'country': analyze_country_distribution(df, brand_name),
        'sentiment': analyze_sentiment_trends(df, brand_name),
        'keywords': analyze_word_cloud(df, brand_name),
        'time': analyze_time_trends(df, brand_name)
    }
    
    # 过滤掉None值
    valid_analyses = {k: v for k, v in analyses.items() if v is not None}
    
    prompt = f"""基于以下{brand_name}的各个维度分析结果，生成一个全面深入的综合分析报告：

{json.dumps(valid_analyses, ensure_ascii=False, indent=2)}

请系统性地总结以下几个方面：

1. 品牌整体表现评估
   - 总体用户满意度水平
   - 品牌在市场中的定位和影响力
   - 品牌声誉的总体状况

2. 品牌核心优势（至少3-5点）
   - 具体列出品牌最突出的优势
   - 每个优势的具体表现和影响
   - 这些优势如何为品牌创造竞争力
   - 如何进一步强化这些优势

3. 品牌主要劣势和问题（至少3-5点）
   - 具体列出品牌最突出的问题和劣势
   - 每个问题的具体表现和影响
   - 这些问题如何影响用户体验和品牌声誉
   - 问题的严重程度和优先级排序

4. 具体可行的改进建议（至少5点）
   - 针对每个主要问题提出具体的改进措施
   - 建议的实施优先级和预期效果
   - 短期可立即实施的改进措施
   - 长期需要战略性调整的改进方向

5. 市场机会和发展方向
   - 基于用户反馈的潜在市场机会
   - 品牌可以拓展的新领域或新市场
   - 与竞争对手差异化的关键点

请用简洁专业的语言输出分析结果，确保分析具有可操作性和实用价值，能够直接指导品牌改进和发展策略。"""
    
    return call_ai_model(prompt)

def analyze_sentiment_trends(df, brand_name):
    """分析情感趋势"""
    sentiment_col = 'sentiment_category'
    if sentiment_col not in df.columns:
        return None
        
    sentiment_counts = df[sentiment_col].value_counts()
    total_reviews = len(df)
    
    # 计算正面和负面评价的比例
    positive_percentage = sentiment_counts.get('Positive', 0) / total_reviews * 100
    negative_percentage = sentiment_counts.get('Negative', 0) / total_reviews * 100
    neutral_percentage = sentiment_counts.get('Neutral', 0) / total_reviews * 100
    
    # 提取高分和低分评论的样本
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    if review_col:
        positive_samples = df[df[sentiment_col] == 'Positive'][review_col].sample(min(3, sentiment_counts.get('Positive', 0))).tolist()
        negative_samples = df[df[sentiment_col] == 'Negative'][review_col].sample(min(3, sentiment_counts.get('Negative', 0))).tolist()
        
        positive_examples = "\n".join([f"- {sample[:100]}..." for sample in positive_samples])
        negative_examples = "\n".join([f"- {sample[:100]}..." for sample in negative_samples])
    else:
        positive_examples = "无样本数据"
        negative_examples = "无样本数据"
    
    prompt = f"""分析以下{brand_name}的评论情感分布数据：
    总评论数：{total_reviews}
    正面评价：{sentiment_counts.get('Positive', 0)}条 ({positive_percentage:.1f}%)
    中性评价：{sentiment_counts.get('Neutral', 0)}条 ({neutral_percentage:.1f}%)
    负面评价：{sentiment_counts.get('Negative', 0)}条 ({negative_percentage:.1f}%)
    
    正面评价样本：
{positive_examples}
    
    负面评价样本：
{negative_examples}
    
    请深入分析这个情感分布的特点，包括：
    1. 整体情感倾向和用户满意度水平
    2. 正面评价中反映的品牌主要优势和亮点
    3. 负面评价中反映的品牌主要问题和痛点
    4. 用户投诉的主要焦点和表扬的核心方面
    5. 情感极化现象分析（如果存在）
    6. 针对负面情感，品牌应该采取的改进措施
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面。"""
    
    return call_ai_model(prompt)

def analyze_word_cloud(df, brand_name):
    """分析词云数据"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    sentiment_col = 'sentiment_category'
    if review_col is None:
        return None
        
    # 分别提取正面和负面评论中的关键词
    all_text = ' '.join(df[review_col].dropna().astype(str))
    
    # 设置停用词
    from wordcloud import STOPWORDS
    import string
    stopwords = set(STOPWORDS)
    custom_stopwords = {
        # 英文常见停用词
        'the', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'with', 'for', 'on', 'is', 'was', 'be',
        'this', 'have', 'from', 'or', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'there', 'can', 'an', 'your', 'which', 'their', 'said', 'if', 'will', 'my', 'one',
        'would', 'so', 'up', 'out', 'them', 'about', 'who', 'get', 'me', 'been', 'has', 'just',
        'do', 'did', 'doing', 'does', 'then', 'such', 'no', 'yes', 'they', 'also', 'any', 'are',
        
        # 品牌和产品相关词
        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
        
        # 电商常见词
        'shipping', 'delivery', 'arrived', 'package', 'item', 'items', 'customer', 'customers',
        'review', 'reviews', 'rating', 'ratings', 'star', 'stars', 'experience'
    }
    stopwords.update(custom_stopwords)
    
    # 处理文本，移除标点符号和停用词
    text = all_text.lower()
    for p in string.punctuation:
        text = text.replace(p, ' ')
    words = text.split()
    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
    
    # 获取总体词频
    word_freq = pd.Series(filtered_words).value_counts().head(15)
    
    # 如果有情感分类列，分别提取正面和负面评论的关键词
    pos_word_freq = None
    neg_word_freq = None
    if sentiment_col in df.columns:
        pos_reviews = ' '.join(df[df[sentiment_col] == 'Positive'][review_col].dropna().astype(str))
        neg_reviews = ' '.join(df[df[sentiment_col] == 'Negative'][review_col].dropna().astype(str))
        
        # 处理正面评论文本
        pos_text = pos_reviews.lower()
        for p in string.punctuation:
            pos_text = pos_text.replace(p, ' ')
        pos_words = pos_text.split()
        pos_filtered = [word for word in pos_words if word not in stopwords and len(word) > 2]
        pos_word_freq = pd.Series(pos_filtered).value_counts().head(10)
        
        # 处理负面评论文本
        neg_text = neg_reviews.lower()
        for p in string.punctuation:
            neg_text = neg_text.replace(p, ' ')
        neg_words = neg_text.split()
        neg_filtered = [word for word in neg_words if word not in stopwords and len(word) > 2]
        neg_word_freq = pd.Series(neg_filtered).value_counts().head(10)
    
    # 构建提示词
    prompt = f"""分析以下{brand_name}的评论关键词数据：
    
    总体最常见的15个关键词及其出现次数：
    {', '.join([f'{word}: {count}次' for word, count in word_freq.items()])}
    """
    
    # 添加正面评论关键词
    if pos_word_freq is not None and len(pos_word_freq) > 0:
        prompt += f"""
    
    正面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in pos_word_freq.items()])}
    """
    
    # 添加负面评论关键词
    if neg_word_freq is not None and len(neg_word_freq) > 0:
        prompt += f"""
    
    负面评价中最常见的10个关键词：
    {', '.join([f'{word}: {count}次' for word, count in neg_word_freq.items()])}
    """
    
    prompt += f"""
    
    请深入分析这些关键词的特点，包括：
    1. 用户最关注的产品/服务方面
    2. 正面评价中反映的品牌主要优势和特色
    3. 负面评价中反映的品牌主要问题和痛点
    4. 关键词与具体业务场景的关联（如产品质量、客户服务、物流配送等）
    5. 品牌应该重点改进的方面
    6. 品牌可以继续保持和强化的优势
    
    请用简洁的语言总结分析结果，重点突出品牌优势和需要改进的方面，并给出具体可行的改进建议。"""
    
    return call_ai_model(prompt)

def analyze_time_trends(df, brand_name):
    """分析时间趋势"""
    date_col = next((col for col in df.columns if col.lower() == 'date'), None)
    if date_col is None:
        return None
        
    df['date'] = pd.to_datetime(df[date_col])
    monthly_counts = df.groupby(df['date'].dt.to_period('M')).size()
    
    if len(monthly_counts) <= 1:
        return None
    
    trend = 'increasing' if monthly_counts.iloc[-1] > monthly_counts.iloc[0] else 'decreasing'
    avg_monthly = monthly_counts.mean()
    max_month = monthly_counts.idxmax()
    min_month = monthly_counts.idxmin()
    
    # 分析评分随时间的变化趋势
    rating_trend = ""
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    if rating_col:
        # 计算每月平均评分
        monthly_ratings = df.groupby(df['date'].dt.to_period('M'))[rating_col].mean()
        if len(monthly_ratings) > 1:
            rating_trend = 'improving' if monthly_ratings.iloc[-1] > monthly_ratings.iloc[0] else 'declining'
            rating_trend = f"\n    评分趋势：{rating_trend}"
            rating_trend += f"\n    初始月份平均评分：{monthly_ratings.iloc[0]:.2f}星"
            rating_trend += f"\n    最近月份平均评分：{monthly_ratings.iloc[-1]:.2f}星"
    
    # 分析情感随时间的变化趋势
    sentiment_trend = ""
    sentiment_col = 'sentiment'
    if sentiment_col in df.columns:
        # 计算每月平均情感得分
        monthly_sentiment = df.groupby(df['date'].dt.to_period('M'))[sentiment_col].mean()
        if len(monthly_sentiment) > 1:
            sentiment_trend = 'improving' if monthly_sentiment.iloc[-1] > monthly_sentiment.iloc[0] else 'declining'
            sentiment_trend = f"\n    情感趋势：{sentiment_trend}"
            sentiment_trend += f"\n    初始月份平均情感得分：{monthly_sentiment.iloc[0]:.3f}"
            sentiment_trend += f"\n    最近月份平均情感得分：{monthly_sentiment.iloc[-1]:.3f}"
    
    prompt = f"""分析以下{brand_name}的评论时间趋势数据：
    评论数量趋势：{trend}
    平均每月评论数：{avg_monthly:.1f}
    评论最多的月份：{max_month}（{monthly_counts[max_month]}条）
    评论最少的月份：{min_month}（{monthly_counts[min_month]}条）{rating_trend}{sentiment_trend}
    
    请深入分析这个时间趋势的特点，包括：
    1. 品牌影响力随时间的变化趋势
    2. 用户满意度随时间的变化趋势
    3. 季节性波动及其可能的原因
    4. 高峰期和低谷期的特点及其与品牌活动的关联
    5. 品牌表现是否在改善或恶化，以及可能的原因
    6. 基于时间趋势，品牌应该采取的策略调整
    
    请用简洁的语言总结分析结果，重点突出品牌随时间变化的优势和劣势，并给出针对性的发展趋势建议。"""
    
    return call_ai_model(prompt)

def generate_comprehensive_analysis(df, brand_name):
    """生成综合分析报告"""
    analyses = {
        'rating': analyze_rating_distribution(df, brand_name),
        'country': analyze_country_distribution(df, brand_name),
        'sentiment': analyze_sentiment_trends(df, brand_name),
        'keywords': analyze_word_cloud(df, brand_name),
        'time': analyze_time_trends(df, brand_name)
    }
    
    # 过滤掉None值
    valid_analyses = {k: v for k, v in analyses.items() if v is not None}