# main_dev.py - 开发调试模式
import datetime
import os
import shutil
import random
import time
from scraper import scrape_trustpilot_reviews, extract_brand_name
from data_processing import save_to_csv, format_excel_file, organize_analysis_files
from visualization import create_country_bar_chart, create_country_treemap, generate_word_cloud, analyze_combined_trends, create_rating_pie_chart, generate_rating_word_clouds
from sentiment import analyze_sentiment, analyze_review_length_sentiment, analyze_word_sentiment_correlation, analyze_time_series_sentiment
from topic_modeling import analyze_rating_topic_correlation, analyze_country_topic_correlation, analyze_topic_sentiment_correlation

# 模拟AI模型响应的函数
def mock_ai_model(prompt):
    """模拟AI大模型API调用，返回预设的分析结果"""
    print("[DEV模式] 模拟AI模型调用，不消耗API token")
    time.sleep(random.uniform(0.5, 1.5))  # 模拟API调用延迟
    
    # 根据提示内容生成不同的模拟响应
    if "评分分布" in prompt:
        return "【模拟AI分析 - 评分分布】\n\n该品牌的评分呈现两极分化的特点，高分（4-5星）和低分（1-2星）占比较大，中等评分较少。这表明用户对产品或服务的体验要么非常满意，要么非常不满。整体满意度中等偏上，但需要关注负面评价的具体原因，改进用户体验。"
    elif "国家分布" in prompt:
        return "【模拟AI分析 - 国家分布】\n\n该品牌的用户主要集中在几个核心市场，地理集中度较高。这表明品牌在特定区域有较强的市场渗透力，但国际化多元化程度有待提高。建议在核心市场继续深耕的同时，考虑拓展更多的国际市场。"
    elif "情感分布" in prompt:
        return "【模拟AI分析 - 情感分析】\n\n评论的情感整体呈现正面倾向，正面评价明显多于负面评价。用户满意度较高，但仍存在一定比例的负面情感，需要关注。没有明显的情感极化现象，说明用户体验相对稳定。"
    elif "关键词" in prompt:
        return "【模拟AI分析 - 词云分析】\n\n用户评论中频繁提及产品质量、配送速度和客户服务相关词汇。主要讨论集中在产品体验和购物流程上。存在少量与退款、延迟相关的问题关键词，建议关注。品牌特征词出现频率较高，表明品牌认知度良好。"
    elif "时间趋势" in prompt:
        return "【模拟AI分析 - 时间趋势】\n\n评论数量总体呈现上升趋势，表明品牌影响力在增强。存在季节性波动，特别是在假日购物季评论数量明显增加。高峰期通常与促销活动相关，低谷期可能与供应链或季节性因素有关。用户活跃度整体稳定增长。"
    elif "主题模型" in prompt:
        return "【模拟AI分析 - 主题分析】\n\n用户最关注的主题领域是产品质量、价格性价比和配送体验。正面评价最多的主题是产品设计和客户服务。负面评价最多的主题是配送延迟和尺码问题。品牌应该重点关注改进物流配送系统和提供更准确的产品尺寸指南。"
    else:
        return "【模拟AI分析】\n\n根据数据分析，该品牌整体表现良好，用户满意度较高。主要优势在于产品质量和客户服务，需要改进的方面包括物流配送和产品一致性。建议关注用户反馈，持续优化产品和服务体验。"

# 模拟并发AI模型调用的函数
def mock_ai_model_concurrent(prompts):
    """模拟并发调用AI模型处理多个提示"""
    print(f"[DEV模式] 模拟并发处理{len(prompts)}个AI请求...")
    results = []
    for i, prompt in enumerate(prompts):
        print(f"模拟处理第{i+1}/{len(prompts)}个分析任务")
        result = mock_ai_model(prompt)
        results.append(result)
        time.sleep(random.uniform(0.2, 0.5))  # 模拟并发处理的时间差
    return results

# 替换原始的AI分析模块中的函数
import ai_analysis
ai_analysis.call_ai_model = mock_ai_model
ai_analysis.call_ai_model_concurrent = mock_ai_model_concurrent

# 修改爬虫函数，限制只爬取前2页
def scrape_trustpilot_reviews_dev(url, brand_name, save_dir="review_data"):
    """开发模式下的爬虫函数，限制只爬取前2页"""
    print("[DEV模式] 爬虫限制为最多2页")
    
    # 调用原始爬虫函数但限制页数
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import NoSuchElementException, TimeoutException
    from webdriver_manager.chrome import ChromeDriverManager
    import pandas as pd
    import re
    from utils import create_directory, extract_country_code
    
    all_reviews = []
    all_page_files = []
    
    create_directory(save_dir)
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            ).click()
            print("Accepted cookies")
        except:
            print("No cookie consent dialog found")
        
        page_num = 1
        has_next_page = True
        
        # 修改循环条件，限制最多爬取2页
        while has_next_page and page_num <= 2:
            current_url = f"{url}?page={page_num}" if page_num > 1 else url
            if page_num > 1:
                delay = random.uniform(2, 5)  # 开发模式下缩短等待时间
                print(f"Waiting for {delay:.2f} seconds...")
                time.sleep(delay)
                driver.get(current_url)
                print(f"Navigating to page {page_num}: {current_url}")
            else:
                print(f"Scraping page {page_num}")
            
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-service-review-card-paper='true']"))
                )
            except TimeoutException:
                print("Timed out waiting for reviews.")
                break
            
            time.sleep(2)
            review_containers = driver.find_elements(By.CSS_SELECTOR, "article[data-service-review-card-paper='true']")
            
            if not review_containers:
                print("No reviews found. Ending pagination.")
                break
                
            print(f"Found {len(review_containers)} reviews on page {page_num}")
            page_reviews = []
            
            for container in review_containers:
                try:
                    try:
                        username_element = container.find_element(By.CSS_SELECTOR, "span[data-consumer-name-typography='true']")
                        username = username_element.text.strip()
                    except NoSuchElementException:
                        try:
                            username_element = container.find_element(By.CSS_SELECTOR, ".styles_consumerDetails__qg84T span")
                            username = username_element.text.strip()
                        except NoSuchElementException:
                            username = "Unknown"
                    
                    country = "Unknown"
                    try:
                        user_info_area = container.find_element(By.CSS_SELECTOR, ".styles_consumerDetailsWrapper__LSBJS")
                        user_info_text = user_info_area.text
                        country = extract_country_code(user_info_text, username)
                    except Exception as e:
                        print(f"Error extracting country: {e}")
                    
                    try:
                        time_element = container.find_element(By.CSS_SELECTOR, "time[datetime]")
                        review_date = time_element.get_attribute("datetime").split("T")[0]
                    except NoSuchElementException:
                        review_date = "Unknown"
                    
                    try:
                        review_element = container.find_element(By.CSS_SELECTOR, "p[data-service-review-text-typography='true']")
                        review_content = review_element.text.strip()
                    except NoSuchElementException:
                        review_content = ""
                    
                    try:
                        star_img = container.find_element(By.CSS_SELECTOR, ".star-rating_starRating__sdbkn img")
                        alt_text = star_img.get_attribute("alt")
                        rating_match = re.search(r'Rated (\d+) out of 5', alt_text)
                        rating = rating_match.group(1) if rating_match else "Unknown"
                    except NoSuchElementException:
                        try:
                            rating_container = container.find_element(By.CSS_SELECTOR, "div[data-service-review-rating]")
                            rating = rating_container.get_attribute("data-service-review-rating")
                        except NoSuchElementException:
                            rating = "Unknown"
                    
                    review_data = {
                        'username': username,
                        'country': country,
                        'rating': rating,
                        'date': review_date,
                        'review': review_content
                    }
                    
                    page_reviews.append(review_data)
                    all_reviews.append(review_data)
                    
                except Exception as e:
                    print(f"Error extracting review: {e}")
            
            if page_reviews:
                page_df = pd.DataFrame(page_reviews)
                page_file = os.path.join(save_dir, f"{brand_name}_reviews_page_{page_num}.csv")
                page_df.to_csv(page_file, index=False, encoding='utf-8-sig')
                print(f"Saved {len(page_reviews)} reviews to {page_file}")
                all_page_files.append(page_file)
            
            # 检查是否有下一页，但由于我们限制了最多2页，所以如果已经爬了2页就不再检查
            if page_num >= 2:
                has_next_page = False
                print("[DEV模式] 已达到2页限制，停止爬取")
            else:
                next_page_exists = False
                try:
                    next_page_link = driver.find_element(By.CSS_SELECTOR, "link[rel='next']")
                    if next_page_link:
                        next_page_exists = True
                except NoSuchElementException:
                    try:
                        pagination_elements = driver.find_elements(By.CSS_SELECTOR, "button[data-pagination-button-page]")
                        highest_page = max([int(elem.get_attribute("data-pagination-button-page")) for elem in pagination_elements if elem.get_attribute("data-pagination-button-page").isdigit()], default=1)
                        if highest_page >= page_num + 1:
                            next_page_exists = True
                    except:
                        pass
                
                has_next_page = next_page_exists
                if not has_next_page:
                    print("No more pages available")
            
            page_num += 1
            
    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        driver.quit()
    
    # 合并所有评论数据
    if all_reviews:
        reviews_df = pd.DataFrame(all_reviews)
        print(f"\nTotal reviews scraped: {len(reviews_df)}")
        return reviews_df, all_page_files
    else:
        print("No reviews were scraped.")
        return pd.DataFrame(), []

# 主函数
def main():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    url = "https://www.trustpilot.com/review/cupshe.ca"
    brand_name = extract_brand_name(url)
    print(f"[DEV模式] 提取品牌评论: {brand_name}")
    
    # 使用Windows系统的Downloads文件夹作为输出目录
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    run_dir = os.path.join(downloads_dir, f"{brand_name}_trustpilot_data_{timestamp}_dev")
    os.makedirs(run_dir, exist_ok=True)
    print(f"输出目录: {run_dir}")
    
    pages_dir = os.path.join(run_dir, "pages")
    # 使用开发版本的爬虫函数，限制只爬取前2页
    reviews_df, page_files = scrape_trustpilot_reviews_dev(url, brand_name, save_dir=pages_dir)
    
    if not reviews_df.empty:
        combined_file = os.path.join(run_dir, f"{brand_name}_trustpilot_reviews_all.csv")
        saved_file = save_to_csv(reviews_df, filename=combined_file)
        
        if saved_file:
            formatted_file, filtered_df = format_excel_file(saved_file)
            if filtered_df is not None:
                print(f"\n过滤后的评论总数: {len(filtered_df)}")
                
                country_col = next((col for col in filtered_df.columns if col.lower() == 'country'), None)
                review_col = next((col for col in filtered_df.columns if col.lower() == 'review'), None)
                rating_col = next((col for col in filtered_df.columns if col.lower() == 'rating'), None)
                date_col = next((col for col in filtered_df.columns if col.lower() == 'date'), None)
                
                analysis_dir = os.path.join(run_dir, "analysis_results")
                os.makedirs(analysis_dir, exist_ok=True)
                
                rating_dir = os.path.join(analysis_dir, "rating_analysis")
                country_dir = os.path.join(analysis_dir, "country_analysis")
                word_dir = os.path.join(analysis_dir, "word_analysis")
                time_dir = os.path.join(analysis_dir, "time_analysis")
                sentiment_dir = os.path.join(analysis_dir, "sentiment_analysis")
                topic_dir = os.path.join(analysis_dir, "topic_analysis")
                
                for directory in [rating_dir, country_dir, word_dir, time_dir, sentiment_dir, topic_dir]:
                    os.makedirs(directory, exist_ok=True)
                
                # 创建评分饼状图
                create_rating_pie_chart(filtered_df, brand_name, os.path.join(rating_dir, f"{brand_name}_rating_pie.png"))
                
                if 'sentiment' not in filtered_df.columns or 'sentiment_category' not in filtered_df.columns:
                    print("添加情感分析...")
                    sentiments = []
                    categories = []
                    for review in filtered_df[review_col]:
                        polarity, category = analyze_sentiment(review)
                        sentiments.append(polarity)
                        categories.append(category)
                    filtered_df['sentiment'] = sentiments
                    filtered_df['sentiment_category'] = categories
                
                lda_model, dictionary, corpus, topic_df = analyze_topic_sentiment_correlation(
                    filtered_df, brand_name, os.path.join(topic_dir, f"{brand_name}_topic_sentiment.png"), num_topics=5
                )
                
                analyze_rating_topic_correlation(
                    filtered_df, brand_name, os.path.join(rating_dir, f"{brand_name}_rating_topic.png"),
                    lda_model, dictionary, corpus, num_topics=5
                )
                
                analyze_word_sentiment_correlation(filtered_df, brand_name, os.path.join(word_dir, f"{brand_name}_word_sentiment.png"))
                
                analyze_country_topic_correlation(
                    filtered_df, brand_name, os.path.join(country_dir, f"{brand_name}_country_topic.png"),
                    lda_model, dictionary, corpus, num_topics=5
                )
                
                analyze_review_length_sentiment(filtered_df, brand_name, os.path.join(sentiment_dir, f"{brand_name}_length_sentiment.png"))
                
                analyze_time_series_sentiment(filtered_df, brand_name, os.path.join(time_dir, f"{brand_name}_time_sentiment.png"))
                
                if country_col:
                    create_country_bar_chart(filtered_df, brand_name, os.path.join(country_dir, f"{brand_name}_country_distribution.png"))
                    create_country_treemap(filtered_df, brand_name, os.path.join(country_dir, f"{brand_name}_country_treemap.html"))
                
                generate_word_cloud(filtered_df, brand_name, os.path.join(word_dir, f"{brand_name}_word_cloud.png"))
                # 添加按评分分类的词云生成
                generate_rating_word_clouds(filtered_df, brand_name, word_dir)
                
                # 创建时间趋势分析图（评分和评论数量）
                analyze_combined_trends(filtered_df, brand_name, os.path.join(time_dir, f"{brand_name}_time_trends.png"))
                
                sentiment_data_file = os.path.join(sentiment_dir, f"{brand_name}_with_sentiment.csv")
                filtered_df.to_csv(sentiment_data_file, index=False)
                print(f"保存带情感分析的数据到 {sentiment_data_file}")
                
                organize_analysis_files(run_dir)
                
                # 在生成HTML报告前，预先并发处理所有AI分析请求
                print("\n开始并发处理AI分析请求...")
                from ai_analysis import call_ai_model_concurrent, analyze_rating_distribution, analyze_country_distribution, analyze_sentiment_trends, analyze_word_cloud, analyze_time_trends
                
                # 准备所有需要分析的提示
                prompts = []
                # 评分分布分析
                rating_col = next((col for col in filtered_df.columns if col.lower() == 'rating'), None)
                if rating_col:
                    rating_counts = filtered_df[rating_col].value_counts().sort_index()
                    total_reviews = len(filtered_df)
                    prompts.append(f"""分析以下{brand_name}的评分分布数据：
                    总评论数：{total_reviews}
                    1星评分：{rating_counts.get(1, 0)}条 ({rating_counts.get(1, 0)/total_reviews*100:.1f}%)
                    2星评分：{rating_counts.get(2, 0)}条 ({rating_counts.get(2, 0)/total_reviews*100:.1f}%)
                    3星评分：{rating_counts.get(3, 0)}条 ({rating_counts.get(3, 0)/total_reviews*100:.1f}%)
                    4星评分：{rating_counts.get(4, 0)}条 ({rating_counts.get(4, 0)/total_reviews*100:.1f}%)
                    5星评分：{rating_counts.get(5, 0)}条 ({rating_counts.get(5, 0)/total_reviews*100:.1f}%)
                    
                    请分析这个评分分布的特点，包括：
                    1. 评分的整体趋势
                    2. 高分和低分的比例
                    3. 用户满意度水平
                    4. 是否存在明显的评分倾向
                    
                    请用简洁的语言总结分析结果。""")
                
                # 国家分布分析
                country_col = next((col for col in filtered_df.columns if col.lower() == 'country'), None)
                if country_col:
                    country_counts = filtered_df[country_col].value_counts()
                    total_reviews = len(filtered_df)
                    top_countries = country_counts.head(5)
                    prompts.append(f"""分析以下{brand_name}的评论国家分布数据：
                    总评论数：{total_reviews}
                    前5个国家的分布：
                    {', '.join([f'{country}: {count}条 ({count/total_reviews*100:.1f}%)' for country, count in top_countries.items()])}
                    
                    请分析这个地理分布的特点，包括：
                    1. 用户群体的地理集中度
                    2. 主要市场区域
                    3. 市场覆盖的多样性
                    4. 是否存在明显的地域性特征
                    
                    请用简洁的语言总结分析结果。""")
                
                # 情感分析
                sentiment_col = 'sentiment_category'
                if sentiment_col in filtered_df.columns:
                    sentiment_counts = filtered_df[sentiment_col].value_counts()
                    total_reviews = len(filtered_df)
                    prompts.append(f"""分析以下{brand_name}的评论情感分布数据：
                    总评论数：{total_reviews}
                    正面评价：{sentiment_counts.get('Positive', 0)}条 ({sentiment_counts.get('Positive', 0)/total_reviews*100:.1f}%)
                    中性评价：{sentiment_counts.get('Neutral', 0)}条 ({sentiment_counts.get('Neutral', 0)/total_reviews*100:.1f}%)
                    负面评价：{sentiment_counts.get('Negative', 0)}条 ({sentiment_counts.get('Negative', 0)/total_reviews*100:.1f}%)
                    
                    请分析这个情感分布的特点，包括：
                    1. 整体情感倾向                    2. 正面与负面评价的比例
                    3. 用户满意度水平                    4. 是否存在明显的情感极化现象
                    
                    请用简洁的语言总结分析结果。""")
                
                # 词云分析
                review_col = next((col for col in filtered_df.columns if col.lower() == 'review'), None)
                if review_col:
                    all_text = ' '.join(filtered_df[review_col].dropna().astype(str))
                    
                    # 设置停用词 - 增强版
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
                        'as', 'at', 'before', 'after', 'above', 'below', 'between', 'into', 'through', 'during',
                        'few', 'more', 'most', 'other', 'some', 'its', 'his', 'her', 'our', 'their', 'mine', 'yours',
                        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'am', 'is', 'are', 'was', 'were', 'very',
                        
                        # 品牌和产品相关词
                        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
                        'received', 'bought', 'purchase', 'purchased', 'buy', 'use', 'used', 'using',
                        
                        # 电商常见词
                        'shipping', 'delivery', 'arrived', 'package', 'item', 'items', 'customer', 'customers',
                        'review', 'reviews', 'rating', 'ratings', 'star', 'stars', 'experience', 'website', 'online',
                        'shop', 'shopping', 'store', 'ordered', 'ordering', 'shipped', 'shipping', 'delivered'
                    }
                    stopwords.update(custom_stopwords)
                    
                    # 处理文本，移除标点符号和停用词
                    text = all_text.lower()
                    for p in string.punctuation:
                        text = text.replace(p, ' ')
                    words = text.split()
                    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
                    
                    import pandas as pd
                    word_freq = pd.Series(filtered_words).value_counts().head(10)
                    prompts.append(f"""分析以下{brand_name}的评论关键词数据：
                    最常见的10个关键词及其出现次数：
                    {', '.join([f'{word}: {count}次' for word, count in word_freq.items()])}
                    
                    请分析这些关键词的特点，包括：
                    1. 用户最关注的方面                    2. 主要讨论的话题                    3. 是否存在明显的问题关键词                    4. 品牌特征词的出现情况
                    
                    请用简洁的语言总结分析结果。""")
                
                # 时间趋势分析
                date_col = next((col for col in filtered_df.columns if col.lower() == 'date'), None)
                if date_col:
                    filtered_df['date'] = pd.to_datetime(filtered_df[date_col])
                    monthly_counts = filtered_df.groupby(filtered_df['date'].dt.to_period('M')).size()
                    if len(monthly_counts) > 1:
                        trend = 'increasing' if monthly_counts.iloc[-1] > monthly_counts.iloc[0] else 'decreasing'
                        avg_monthly = monthly_counts.mean()
                        max_month = monthly_counts.idxmax()
                        min_month = monthly_counts.idxmin()
                        prompts.append(f"""分析以下{brand_name}的评论时间趋势数据：
                        评论数量趋势：{trend}
                        平均每月评论数：{avg_monthly:.1f}
                        评论最多的月份：{max_month}（{monthly_counts[max_month]}条）
                        评论最少的月份：{min_month}（{monthly_counts[min_month]}条）
                        
                        请分析这个时间趋势的特点，包括：
                        1. 整体发展趋势                    2. 是否存在季节性波动                    3. 高峰期和低谷期的特点                    4. 用户活跃度的变化
                        
                        请用简洁的语言总结分析结果。""")
                # 并发调用AI模型
                if prompts:
                    print(f"开始并发处理{len(prompts)}个AI分析请求...")
                    results = call_ai_model_concurrent(prompts)
                    
                    # 将结果保存到对应的分析文件夹中
                    analysis_types = []
                    analysis_results = {}
                    
                    # 按照prompts的顺序记录分析类型
                    current_index = 0
                    if rating_col:
                        analysis_types.append(('rating_analysis', rating_dir))
                        if current_index < len(results) and results[current_index]:
                            analysis_results['rating_analysis'] = results[current_index]
                        current_index += 1
                    if country_col:
                        analysis_types.append(('country_analysis', country_dir))
                        if current_index < len(results) and results[current_index]:
                            analysis_results['country_analysis'] = results[current_index]
                        current_index += 1
                    if sentiment_col in filtered_df.columns:
                        analysis_types.append(('sentiment_analysis', sentiment_dir))
                        if current_index < len(results) and results[current_index]:
                            analysis_results['sentiment_analysis'] = results[current_index]
                        current_index += 1
                    if review_col:
                        analysis_types.append(('word_analysis', word_dir))
                        if current_index < len(results) and results[current_index]:
                            analysis_results['word_analysis'] = results[current_index]
                        current_index += 1
                    if date_col and len(monthly_counts) > 1:
                        analysis_types.append(('time_analysis', time_dir))
                        if current_index < len(results) and results[current_index]:
                            analysis_results['time_analysis'] = results[current_index]
                        current_index += 1
                    
                    # 添加主题分析结果 - 为主题分析创建专门的提示
                    if os.path.exists(os.path.join(topic_dir, f"{brand_name}_topic_sentiment.png")):
                        # 创建主题分析的专门提示
                        topic_prompt = f"""分析以下{brand_name}的主题模型分析结果：
                        主题模型已经从用户评论中提取了5个主要主题, 并分析了这些主题与情感的关联。
                        
                        请分析这些主题的特点, 包括：
                        1. 用户最关注的主题领域
                        2. 正面评价最多的主题
                        3. 负面评价最多的主题
                        4. 品牌应该重点关注的主题领域
                        
                        请用简洁的语言总结分析结果。"""
                        
                        # 调用AI模型获取主题分析结果
                        print("开始生成主题分析结果...")
                        topic_analysis = mock_ai_model(topic_prompt)
                        if topic_analysis:
                            analysis_file = os.path.join(topic_dir, f"{brand_name}_topic_analysis.txt")
                            with open(analysis_file, 'w', encoding='utf-8') as f:
                                f.write(topic_analysis)
                            print(f"保存topic_analysis专项分析结论到{analysis_file}")
                        else:
                            print("主题分析生成失败")
                    
                    # 保存分析结果到对应的文件
                    for analysis_type, directory in analysis_types:
                        if analysis_type in analysis_results:
                            analysis_file = os.path.join(directory, f"{brand_name}_{analysis_type}.txt")
                            with open(analysis_file, 'w', encoding='utf-8') as f:
                                f.write(analysis_results[analysis_type])
                            print(f"保存{analysis_type}分析结论到{analysis_file}")
                    print("AI分析请求处理完成")
                # 先生成每个分析文件夹的分类报告
                from folder_reports import generate_all_folder_reports
                print("\n开始为每个分析文件夹生成独立HTML报告...")
                folder_reports = generate_all_folder_reports(run_dir, brand_name)
                if folder_reports:
                    print(f"成功生成了{len(folder_reports)}个分析文件夹的小型HTML报告:")
                    for report in folder_reports:
                        print(f"  - {os.path.basename(report)}")
                else:
                    print("没有生成任何文件夹报告，请检查分析文件夹是否包含必要的图片文件")
                    
                # 生成HTML报告
                from generate_report import generate_html_report
                report_file = generate_html_report(run_dir, brand_name)
                if report_file:
                    print(f"\nHTML报告已生成: {report_file}")
                    print("请在网络浏览器中打开报告文件查看完整分析。")
        
        try:
            shutil.rmtree(pages_dir)
            print(f"删除单独页面目录: {pages_dir}")
        except Exception as e:
            print(f"删除页面目录时出错: {e}")
        
        print(f"\n所有数据已保存到: {run_dir}")
    else:
        print("没有爬取到评论。")

if __name__ == "__main__":
    main()

# 修改爬虫函数，限制只爬取前2页
def scrape_trustpilot_reviews_dev(url, brand_name, save_dir="review_data"):
    """开发模式下的爬虫函数，限制只爬取前2页"""
    print("[DEV模式] 爬虫限制为最多2页")
    
    # 调用原始爬虫函数的实现
    from scraper import scrape_trustpilot_reviews as original_scraper
    
    # 保存原始函数的引用
    original_while_condition = None
    
    # 修改爬虫的页面限制逻辑
    def limited_while_condition(has_next_page, page_num):
        return has_next_page and page_num <= 2
    
    # 使用猴子补丁替换爬虫函数中的循环条件
    import types
    def patched_scraper(url, brand_name, save_dir):
        all_reviews = []
        all_page_files = []
        
        # 这里复制原始爬虫的实现，但限制页数为2页
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import NoSuchElementException, TimeoutException
        from webdriver_manager.chrome import ChromeDriverManager
        import pandas as pd
        import time
        import random
        import re
        import os
        from utils import create_directory, extract_country_code
        
        create_directory(save_dir)
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        try:
            driver.get(url)
            try:
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                ).click()
                print("Accepted cookies")
            except:
                print("No cookie consent dialog found")
            
            page_num = 1
            has_next_page = True
            
            # 修改循环条件，限制最多爬取2页
            while has_next_page and page_num <= 2:
                current_url = f"{url}?page={page_num}" if page_num > 1 else url
                if page_num > 1:
                    delay = random.uniform(2, 5)  # 开发模式下缩短等待时间
                    print(f"Waiting for {delay:.2f} seconds...")
                    time.sleep(delay)
                    driver.get(current_url)
                    print(f"Navigating to page {page_num}: {current_url}")
                else:
                    print(f"Scraping page {page_num}")
                
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-service-review-card-paper='true']"))
                    )
                except TimeoutException:
                    print("Timed out waiting for reviews.")
                    break
                
                time.sleep(2)
                review_containers = driver.find_elements(By.CSS_SELECTOR, "article[data-service-review-card-paper='true']")
                
                if not review_containers:
                    print("No reviews found. Ending pagination.")
                    break
                    
                print(f"Found {len(review_containers)} reviews on page {page_num}")
                page_reviews = []
                
                for container in review_containers:
                    try:
                        try:
                            username_element = container.find_element(By.CSS_SELECTOR, "span[data-consumer-name-typography='true']")
                            username = username_element.text.strip()
                        except NoSuchElementException:
                            try:
                                username_element = container.find_element(By.CSS_SELECTOR, ".styles_consumerDetails__qg84T span")
                                username = username_element.text.strip()
                            except NoSuchElementException:
                                username = "Unknown"
                        
                        country = "Unknown"
                        try:
                            user_info_area = container.find_element(By.CSS_SELECTOR, ".styles_consumerDetailsWrapper__LSBJS")
                            user_info_text = user_info_area.text
                            country = extract_country_code(user_info_text, username)
                        except Exception as e:
                            print(f"Error extracting country: {e}")
                        
                        try:
                            time_element = container.find_element(By.CSS_SELECTOR, "time[datetime]")
                            review_date = time_element.get_attribute("datetime").split("T")[0]
                        except NoSuchElementException:
                            review_date = "Unknown"
                        
                        try:
                            review_element = container.find_element(By.CSS_SELECTOR, "p[data-service-review-text-typography='true']")
                            review_content = review_element.text.strip()
                        except NoSuchElementException:
                            review_content = ""
                        
                        try:
                            star_img = container.find_element(By.CSS_SELECTOR, ".star-rating_starRating__sdbkn img")
                            alt_text = star_img.get_attribute("alt")
                            rating_match = re.search(r'Rated (\d+) out of 5', alt_text)
                            rating = rating_match.group(1) if rating_match else "Unknown"
                        except NoSuchElementException:
                            try:
                                rating_container = container.find_element(By.CSS_SELECTOR, "div[data-service-review-rating]")
                                rating = rating_container.get_attribute("data-service-review-rating")
                            except NoSuchElementException:
                                rating = "Unknown"
                        
                        review_data = {
                            'username': username,
                            'country': country,
                            'rating': rating,
                            'date': review_date,
                            'review': review_content
                        }
                        
                        page_reviews.append(review_data)
                        all_reviews.append(review_data)
                        
                    except Exception as e:
                        print(f"Error extracting review: {e}")
                
                if page_reviews:
                    page_df = pd.DataFrame(page_reviews)
                    page_file = os.path.join(save_dir, f"{brand_name}_reviews_page_{page_num}.csv")
                    page_df.to_csv(page_file, index=False, encoding='utf-8-sig')
                    print(f"Saved {len(page_reviews)} reviews to {page_file}")
                    all_page_files.append(page_file)
                
                # 检查是否有下一页，但由于我们限制了最多2页，所以如果已经爬了2页就不再检查
                if page_num >= 2:
                    has_next_page = False
                    print("[DEV模式] 已达到2页限制，停止爬取")
                else:
                    next_page_exists = False
                    try:
                        next_page_link = driver.find_element(By.CSS_SELECTOR, "link[rel='next']")
                        if next_page_link:
                            next_page_exists = True
                    except NoSuchElementException:
                        try:
                            pagination_elements = driver.find_elements(By.CSS_SELECTOR, "button[data-pagination-button-page]")
                            highest_page = max([int(elem.get_attribute("data-pagination-button-page")) for elem in pagination_elements if elem.get_attribute("data-pagination-button-page").isdigit()], default=1)
                            if highest_page >= page_num + 1:
                                next_page_exists = True
                        except:
                            pass
                    
                    has_next_page = next_page_exists
                    if not has_next_page:
                        print("No more pages found.")
            
            page_num += 1
            
    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        driver.quit()
    
    # 合并所有评论数据
    if all_reviews:
        reviews_df = pd.DataFrame(all_reviews)
        print(f"\nTotal reviews scraped: {len(reviews_df)}")
        return reviews_df, all_page_files
    else:
        print("No reviews were scraped.")
        return pd.DataFrame(), []

# 主函数
def main():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    url = "https://www.trustpilot.com/review/cupshe.ca"
    brand_name = extract_brand_name(url)
    print(f"[DEV模式] 提取品牌评论: {brand_name}")
    
    # 使用Windows系统的Downloads文件夹作为输出目录
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    run_dir = os.path.join(downloads_dir, f"{brand_name}_trustpilot_data_{timestamp}_dev")
    os.makedirs(run_dir, exist_ok=True)
    print(f"输出目录: {run_dir}")
    
    pages_dir = os.path.join(run_dir, "pages")
    # 使用开发版本的爬虫函数，限制只爬取前2页
    reviews_df, page_files = scrape_trustpilot_reviews_dev(url, brand_name, save_dir=pages_dir)
    
    if not reviews_df.empty:
        combined_file = os.path.join(run_dir, f"{brand_name}_trustpilot_reviews_all.csv")
        saved_file = save_to_csv(reviews_df, filename=combined_file)
        
        if saved_file:
            formatted_file, filtered_df = format_excel_file(saved_file)
            if filtered_df is not None:
                print(f"\n过滤后的评论总数: {len(filtered_df)}")
                
                country_col = next((col for col in filtered_df.columns if col.lower() == 'country'), None)
                review_col = next((col for col in filtered_df.columns if col.lower() == 'review'), None)
                rating_col = next((col for col in filtered_df.columns if col.lower() == 'rating'), None)
                date_col = next((col for col in filtered_df.columns if col.lower() == 'date'), None)
                
                analysis_dir = os.path.join(run_dir, "analysis_results")
                os.makedirs(analysis_dir, exist_ok=True)
                
                rating_dir = os.path.join(analysis_dir, "rating_analysis")
                country_dir = os.path.join(analysis_dir, "country_analysis")
                word_dir = os.path.join(analysis_dir, "word_analysis")
                time_dir = os.path.join(analysis_dir, "time_analysis")
                sentiment_dir = os.path.join(analysis_dir, "sentiment_analysis")
                topic_dir = os.path.join(analysis_dir, "topic_analysis")
                
                for directory in [rating_dir, country_dir, word_dir, time_dir, sentiment_dir, topic_dir]:
                    os.makedirs(directory, exist_ok=True)
                
                # 创建评分饼状图
                create_rating_pie_chart(filtered_df, brand_name, os.path.join(rating_dir, f"{brand_name}_rating_pie.png"))
                
                if 'sentiment' not in filtered_df.columns or 'sentiment_category' not in filtered_df.columns:
                    print("添加情感分析...")
                    sentiments = []
                    categories = []
                    for review in filtered_df[review_col]:
                        polarity, category = analyze_sentiment(review)
                        sentiments.append(polarity)
                        categories.append(category)
                    filtered_df['sentiment'] = sentiments
                    filtered_df['sentiment_category'] = categories
                
                lda_model, dictionary, corpus, topic_df = analyze_topic_sentiment_correlation(
                    filtered_df, brand_name, os.path.join(topic_dir, f"{brand_name}_topic_sentiment.png"), num_topics=5
                )
                
                analyze_rating_topic_correlation(
                    filtered_df, brand_name, os.path.join(rating_dir, f"{brand_name}_rating_topic.png"),
                    lda_model, dictionary, corpus, num_topics=5
                )
                
                analyze_word_sentiment_correlation(filtered_df, brand_name, os.path.join(word_dir, f"{brand_name}_word_sentiment.png"))
                
                analyze_country_topic_correlation(
                    filtered_df, brand_name, os.path.join(country_dir, f"{brand_name}_country_topic.png"),
                    lda_model, dictionary, corpus, num_topics=5
                )
                
                analyze_review_length_sentiment(filtered_df, brand_name, os.path.join(sentiment_dir, f"{brand_name}_length_sentiment.png"))
                
                analyze_time_series_sentiment(filtered_df, brand_name, os.path.join(time_dir, f"{brand_name}_time_sentiment.png"))
                
                if country_col:
                    create_country_bar_chart(filtered_df, brand_name, os.path.join(country_dir, f"{brand_name}_country_distribution.png"))
                    create_country_treemap(filtered_df, brand_name, os.path.join(country_dir, f"{brand_name}_country_treemap.html"))
                
                generate_word_cloud(filtered_df, brand_name, os.path.join(word_dir, f"{brand_name}_word_cloud.png"))
                # 添加按评分分类的词云生成
                generate_rating_word_clouds(filtered_df, brand_name, word_dir)
                
                # 创建时间趋势分析图（评分和评论数量）
                analyze_combined_trends(filtered_df, brand_name, os.path.join(time_dir, f"{brand_name}_time_trends.png"))
                
                sentiment_data_file = os.path.join(sentiment_dir, f"{brand_name}_with_sentiment.csv")
                filtered_df.to_csv(sentiment_data_file, index=False)
                print(f"保存带情感分析的数据到 {sentiment_data_file}")
                
                organize_analysis_files(run_dir)
                
                # 在生成HTML报告前，预先并发处理所有AI分析请求
                print("\n开始并发处理AI分析请求...")
                from ai_analysis import call_ai_model_concurrent, analyze_rating_distribution, analyze_country_distribution, analyze_sentiment_trends, analyze_word_cloud, analyze_time_trends
                
                # 准备所有需要分析的提示
                prompts = []
                # 评分分布分析
                rating_col = next((col for col in filtered_df.columns if col.lower() == 'rating'), None)
                if rating_col:
                    rating_counts = filtered_df[rating_col].value_counts().sort_index()
                    total_reviews = len(filtered_df)
                    prompts.append(f"""分析以下{brand_name}的评分分布数据：
                    总评论数：{total_reviews}
                    1星评分：{rating_counts.get(1, 0)}条 ({rating_counts.get(1, 0)/total_reviews*100:.1f}%)
                    2星评分：{rating_counts.get(2, 0)}条 ({rating_counts.get(2, 0)/total_reviews*100:.1f}%)
                    3星评分：{rating_counts.get(3, 0)}条 ({rating_counts.get(3, 0)/total_reviews*100:.1f}%)
                    4星评分：{rating_counts.get(4, 0)}条 ({rating_counts.get(4, 0)/total_reviews*100:.1f}%)
                    5星评分：{rating_counts.get(5, 0)}条 ({rating_counts.get(5, 0)/total_reviews*100:.1f}%)
                    
                    请分析这个评分分布的特点，包括：
                    1. 评分的整体趋势
                    2. 高分和低分的比例
                    3. 用户满意度水平
                    4. 是否存在明显的评分倾向
                    
                    请用简洁的语言总结分析结果。""")
                
                # 国家分布分析
                country_col = next((col for col in filtered_df.columns if col.lower() == 'country'), None)
                if country_col:
                    country_counts = filtered_df[country_col].value_counts()
                    total_reviews = len(filtered_df)
                    top_countries = country_counts.head(5)
                    prompts.append(f"""分析以下{brand_name}的评论国家分布数据：
                    总评论数：{total_reviews}
                    前5个国家的分布：
                    {', '.join([f'{country}: {count}条 ({count/total_reviews*100:.1f}%)' for country, count in top_countries.items()])}
                    
                    请分析这个地理分布的特点，包括：
                    1. 用户群体的地理集中度
                    2. 主要市场区域
                    3. 市场覆盖的多样性
                    4. 是否存在明显的地域性特征
                    
                    请用简洁的语言总结分析结果。""")
                
                # 情感分析
                sentiment_col = 'sentiment_category'
                if sentiment_col in filtered_df.columns:
                    sentiment_counts = filtered_df[sentiment_col].value_counts()
                    total_reviews = len(filtered_df)
                    prompts.append(f"""分析以下{brand_name}的评论情感分布数据：
                    总评论数：{total_reviews}
                    正面评价：{sentiment_counts.get('Positive', 0)}条 ({sentiment_counts.get('Positive', 0)/total_reviews*100:.1f}%)
                    中性评价：{sentiment_counts.get('Neutral', 0)}条 ({sentiment_counts.get('Neutral', 0)/total_reviews*100:.1f}%)
                    负面评价：{sentiment_counts.get('Negative', 0)}条 ({sentiment_counts.get('Negative', 0)/total_reviews*100:.1f}%)
                    
                    请分析这个情感分布的特点，包括：
                    1. 整体情感倾向                    2. 正面与负面评价的比例
                    3. 用户满意度水平                    4. 是否存在明显的情感极化现象
                    
                    请用简洁的语言总结分析结果。""")
                
                # 词云分析
                review_col = next((col for col in filtered_df.columns if col.lower() == 'review'), None)
                if review_col:
                    all_text = ' '.join(filtered_df[review_col].dropna().astype(str))
                    
                    # 设置停用词 - 增强版
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
                        'as', 'at', 'before', 'after', 'above', 'below', 'between', 'into', 'through', 'during',
                        'few', 'more', 'most', 'other', 'some', 'its', 'his', 'her', 'our', 'their', 'mine', 'yours',
                        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'am', 'is', 'are', 'was', 'were', 'very',
                        
                        # 品牌和产品相关词
                        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
                        'received', 'bought', 'purchase', 'purchased', 'buy', 'use', 'used', 'using',
                        
                        # 电商常见词
                        'shipping', 'delivery', 'arrived', 'package', 'item', 'items', 'customer', 'customers',
                        'review', 'reviews', 'rating', 'ratings', 'star', 'stars', 'experience', 'website', 'online',
                        'shop', 'shopping', 'store', 'ordered', 'ordering', 'shipped', 'shipping', 'delivered'
                    }
                    stopwords.update(custom_stopwords)
                    
                    # 处理文本，移除标点符号和停用词
                    text = all_text.lower()
                    for p in string.punctuation:
                        text = text.replace(p, ' ')
                    words = text.split()
                    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
                    
                    import pandas as pd
                    word_freq = pd.Series(filtered_words).value_counts().head(10)
                    prompts.append(f"""分析以下{brand_name}的评论关键词数据：
                    最常见的10个关键词及其出现次数：
                    {', '.join([f'{word}: {count}次' for word, count in word_freq.items()])}
                    
                    请分析这些关键词的特点，包括：
                    1. 用户最关注的方面                    2. 主要讨论的话题                    3. 是否存在明显的问题关键词                    4. 品牌特征词的出现情况
                    
                    请用简洁的语言总结分析结果。""")
                
                # 时间趋势分析
                date_col = next((col for col in filtered_df.columns if col.lower() == 'date'), None)
                if date_col:
                    filtered_df['date'] = pd.to_datetime(filtered_df[date_col])
                    monthly_counts = filtered_df.groupby(filtered_df['date'].dt.to_period('M')).size()
                    if len(monthly_counts) > 1:
                        trend = 'increasing' if monthly_counts.iloc[-1] > monthly_counts.iloc[0] else 'decreasing'
                        avg_monthly = monthly_counts.mean()
                        max_month = monthly_counts.idxmax()
                        min_month = monthly_counts.idxmin()
                        prompts.append(f"""分析以下{brand_name}的评论时间趋势数据：
                        评论数量趋势：{trend}
                        平均每月评论数：{avg_monthly:.1f}
                        评论最多的月份：{max_month}（{monthly_counts[max_month]}条）
                        评论最少的月份：{min_month}（{monthly_counts[min_month]}条）
                        
                        请分析这个时间趋势的特点，包括：
                        1. 整体发展趋势                    2. 是否存在季节性波动                    3. 高峰期和低谷期的特点                    4. 用户活跃度的变化
                        
                        请用简洁的语言总结分析结果。""")
                # 并发调用AI模型
                if prompts:
                    print(f"开始并发处理{len(prompts)}个AI分析请求...")
                    results = call_ai_model_concurrent(prompts)
                    
                    # 将结果保存到对应的分析文件夹中
                    analysis_types = []
                    analysis_results = {}
                    
                    # 按照prompts的顺序记录分析类型
                    current_index = 0
                    if rating_col:
                        analysis_types.append(('rating_analysis', rating_dir))
                        if current_index < len(results) and results[current_index]:
                            analysis_results['rating_analysis'] = results[current_index]
                        current_index += 1
                    if country_col:
                        analysis_types.append(('country_analysis', country_dir))
                        if current_index < len(results) and results[current_index]:
                            analysis_results['country_analysis'] = results[current_index]
                        current_index += 1
                    if sentiment_col in filtered_df.columns:
                        analysis_types.append(('sentiment_analysis', sentiment_dir))
                        if current_index < len(results) and results[current_index]:
                            analysis_results['sentiment_analysis'] = results[current_index]
                        current_index += 1
                    if review_col:
                        analysis_types.append(('word_analysis', word_dir))
                        if current_index < len(results) and results[current_index]:
                            analysis_results['word_analysis'] = results[current_index]
                        current_index += 1
                    if date_col and len(monthly_counts) > 1:
                        analysis_types.append(('time_analysis', time_dir))
                        if current_index < len(results) and results[current_index]:
                            analysis_results['time_analysis'] = results[current_index]
                        current_index += 1
                    
                    # 添加主题分析结果 - 为主题分析创建专门的提示
                    if os.path.exists(os.path.join(topic_dir, f"{brand_name}_topic_sentiment.png")):
                        # 创建主题分析的专门提示
                        topic_prompt = f"""分析以下{brand_name}的主题模型分析结果：
                        主题模型已经从用户评论中提取了5个主要主题, 并分析了这些主题与情感的关联。
                        
                        请分析这些主题的特点, 包括：
                        1. 用户最关注的主题领域
                        2. 正面评价最多的主题
                        3. 负面评价最多的主题
                        4. 品牌应该重点关注的主题领域
                        
                        请用简洁的语言总结分析结果。"""
                        
                        # 调用AI模型获取主题分析结果
                        print("开始生成主题分析结果...")
                        topic_analysis = mock_ai_model(topic_prompt)
                        if topic_analysis:
                            analysis_file = os.path.join(topic_dir, f"{brand_name}_topic_analysis.txt")
                            with open(analysis_file, 'w', encoding='utf-8') as f:
                                f.write(topic_analysis)
                            print(f"保存topic_analysis专项分析结论到{analysis_file}")
                        else:
                            print("主题分析生成失败")
                    
                    # 保存分析结果到对应的文件
                    for analysis_type, directory in analysis_types:
                        if analysis_type in analysis_results:
                            analysis_file = os.path.join(directory, f"{brand_name}_{analysis_type}.txt")
                            with open(analysis_file, 'w', encoding='utf-8') as f:
                                f.write(analysis_results[analysis_type])
                            print(f"保存{analysis_type}分析结论到{analysis_file}")
                    print("AI分析请求处理完成")
                # 先生成每个分析文件夹的分类报告
                from folder_reports import generate_all_folder_reports
                print("\n开始为每个分析文件夹生成独立HTML报告...")
                folder_reports = generate_all_folder_reports(run_dir, brand_name)
                if folder_reports:
                    print(f"成功生成了{len(folder_reports)}个分析文件夹的小型HTML报告:")
                    for report in folder_reports:
                        print(f"  - {os.path.basename(report)}")
                else:
                    print("没有生成任何文件夹报告，请检查分析文件夹是否包含必要的图片文件")
                    
                # 生成HTML报告
                from generate_report import generate_html_report
                report_file = generate_html_report(run_dir, brand_name)
                if report_file:
                    print(f"\nHTML报告已生成: {report_file}")
                    print("请在网络浏览器中打开报告文件查看完整分析。")
        
        try:
            shutil.rmtree(pages_dir)
            print(f"删除单独页面目录: {pages_dir}")
        except Exception as e:
            print(f"删除页面目录时出错: {e}")
        
        print(f"\n所有数据已保存到: {run_dir}")
    else:
        print("没有爬取到评论。")

if __name__ == "__main__":
    main()

# 修改爬虫函数，限制只爬取前2页
def scrape_trustpilot_reviews_dev(url, brand_name, save_dir="review_data"):
    """开发模式下的爬虫函数，限制只爬取前2页"""
    print("[DEV模式] 爬虫限制为最多2页")
    
    # 调用原始爬虫函数的实现
    from scraper import scrape_trustpilot_reviews as original_scraper
    
    # 保存原始函数的引用
    original_while_condition = None
    
    # 修改爬虫的页面限制逻辑
    def limited_while_condition(has_next_page, page_num):
        return has_next_page and page_num <= 2
    
    # 使用猴子补丁替换爬虫函数中的循环条件
    import types
    def patched_scraper(url, brand_name, save_dir):
        all_reviews = []
        all_page_files = []
        
        # 这里复制原始爬虫的实现，但限制页数为2页
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import NoSuchElementException, TimeoutException
        from webdriver_manager.chrome import ChromeDriverManager
        import pandas as pd
        import time
        import random
        import re
        import os
        from utils import create_directory, extract_country_code
        
        create_directory(save_dir)
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        try:
            driver.get(url)
            try:
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                ).click()
                print("Accepted cookies")
            except:
                print("No cookie consent dialog found")
            
            page_num = 1
            has_next_page = True
            
            # 修改循环条件，限制最多爬取2页
            while has_next_page and page_num <= 2:
                current_url = f"{url}?page={page_num}" if page_num > 1 else url
                if page_num > 1:
                    delay = random.uniform(2, 5)  # 开发模式下缩短等待时间
                    print(f"Waiting for {delay:.2f} seconds...")
                    time.sleep(delay)
                    driver.get(current_url)
                    print(f"Navigating to page {page_num}: {current_url}")
                else:
                    print(f"Scraping page {page_num}")
                
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "article[data-service-review-card-paper='true']"))
                    )
                except TimeoutException:
                    print("Timed out waiting for reviews.")
                    break
                
                time.sleep(2)
                review_containers = driver.find_elements(By.CSS_SELECTOR, "article[data-service-review-card-paper='true']")
                
                if not review_containers:
                    print("No reviews found. Ending pagination.")
                    break
                    
                print(f"Found {len(review_containers)} reviews on page {page_num}")
                page_reviews = []
                
                for container in review_containers:
                    try:
                        try:
                            username_element = container.find_element(By.CSS_SELECTOR, "span[data-consumer-name-typography='true']")
                            username = username_element.text.strip()
                        except NoSuchElementException:
                            try:
                                username_element = container.find_element(By.CSS_SELECTOR, ".styles_consumerDetails__qg84T span")
                                username = username_element.text.strip()
                            except NoSuchElementException:
                                username = "Unknown"
                        
                        country = "Unknown"
                        try:
                            user_info_area = container.find_element(By.CSS_SELECTOR, ".styles_consumerDetailsWrapper__LSBJS")
                            user_info_text = user_info_area.text
                            country = extract_country_code(user_info_text, username)
                        except Exception as e:
                            print(f"Error extracting country: {e}")
                        
                        try:
                            time_element = container.find_element(By.CSS_SELECTOR, "time[datetime]")
                            review_date = time_element.get_attribute("datetime").split("T")[0]
                        except NoSuchElementException:
                            review_date = "Unknown"
                        
                        try:
                            review_element = container.find_element(By.CSS_SELECTOR, "p[data-service-review-text-typography='true']")
                            review_content = review_element.text.strip()
                        except NoSuchElementException:
                            review_content = ""
                        
                        try:
                            star_img = container.find_element(By.CSS_SELECTOR, ".star-rating_starRating__sdbkn img")
                            alt_text = star_img.get_attribute("alt")
                            rating_match = re.search(r'Rated (\d+) out of 5', alt_text)
                            rating = rating_match.group(1) if rating_match else "Unknown"
                        except NoSuchElementException:
                            try:
                                rating_container = container.find_element(By.CSS_SELECTOR, "div[data-service-review-rating]")
                                rating = rating_container.get_attribute("data-service-review-rating")
                            except NoSuchElementException:
                                rating = "Unknown"
                        
                        review_data = {
                            'username': username,
                            'country': country,
                            'rating': rating,
                            'date': review_date,
                            'review': review_content
                        }
                        
                        page_reviews.append(review_data)
                        all_reviews.append(review_data)
                        
                    except Exception as e:
                        print(f"Error extracting review: {e}")
                
                if page_reviews:
                    page_df = pd.DataFrame(page_reviews)
                    page_file = os.path.join(save_dir, f"{brand_name}_reviews_page_{page_num}.csv")
                    page_df.to_csv(page_file, index=False, encoding='utf-8-sig')
                    print(f"Saved {len(page_reviews)} reviews to {page_file}")
                    all_page_files.append(page_file)
                
                # 检查是否有下一页，但由于我们限制了最多2页，所以如果已经爬了2页就不再检查
                if page_num >= 2:
                    has_next_page = False
                    print("[DEV模式] 已达到2页限制，停止爬取")
                else:
                    next_page_exists = False
                    try:
                        next_page_link = driver.find_element(By.CSS_SELECTOR, "link[rel='next']")
                        if next_page_link:
                            next_page_exists = True
                    except NoSuchElementException:
                        try:
                            pagination_elements = driver.find_elements(By.CSS_SELECTOR, "button[data-pagination-button-page]")
                            highest_page = max([int(elem.get_attribute("data-pagination-button-page")) for elem in pagination_elements if elem.get_attribute("data-pagination-button-page").isdigit()], default=1)
                            if highest_page >= page_num + 1:
                                next_page_exists = True
                        except:
                            pass
                    
                    has_next_page = next_page_exists
                    if not has_next_page:
                        print("No more pages found.")
            
            page_num += 1
            
    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        driver.quit()
    
    # 合并所有评论数据
    if all_reviews:
        reviews_df = pd.DataFrame(all_reviews)
        print(f"\nTotal reviews scraped: {len(reviews_df)}")
        return reviews_df, all_page_files
    else:
        print("No reviews were scraped.")
        return pd.DataFrame(), []

# 主函数
def main():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    url = "https://www.trustpilot.com/review/cupshe.ca"
    brand_name = extract_brand_name(url)
    print(f"[DEV模式] 提取品牌评论: {brand_name}")
    
    # 使用Windows系统的Downloads文件夹作为输出目录
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    run_dir = os.path.join(downloads_dir, f"{brand_name}_trustpilot_data_{timestamp}_dev")
    os.makedirs(run_dir, exist_ok=True)
    print(f"输出目录: {run_dir}")
    
    pages_dir = os.path.join(run_dir, "pages")
    # 使用开发版本的爬虫函数，限制只爬取前2页
    reviews_df, page_files = scrape_trustpilot_reviews_dev(url, brand_name, save_dir=pages_dir)
    
    if not reviews_df.empty:
        combined_file = os.path.join(run_dir, f"{brand_name}_trustpilot_reviews_all.csv")
        saved_file = save_to_csv(reviews_df, filename=combined_file)
        
        if saved_file:
            formatted_file, filtered_df = format_excel_file(saved_file)
            if filtered_df is not None:
                print(f"\n过滤后的评论总数: {len(filtered_df)}")
                
                country_col = next((col for col in filtered_df.columns if col.lower() == 'country'), None)
                review_col = next((col for col in filtered_df.columns if col.lower() == 'review'), None)
                rating_col = next((col for col in filtered_df.columns if col.lower() == 'rating'), None)
                date_col = next((col for col in filtered_df.columns if col.lower() == 'date'), None)
                
                analysis_dir = os.path.join(run_dir, "analysis_results")
                os.makedirs(analysis_dir, exist_ok=True)
                
                rating_dir = os.path.join(analysis_dir, "rating_analysis")
                country_dir = os.path.join(analysis_dir, "country_analysis")
                word_dir = os.path.join(analysis_dir, "word_analysis")
                time_dir = os.path.join(analysis_dir, "time_analysis")
                sentiment_dir = os.path.join(analysis_dir, "sentiment_analysis")
                topic_dir = os.path.join(analysis_dir, "topic_analysis")
                
                for directory in [rating_dir, country_dir, word_dir, time_dir, sentiment_dir, topic_dir]:
                    os.makedirs(directory, exist_ok=True)
                
                # 创建评分饼状图
                create_rating_pie_chart(filtered_df, brand_name, os.path.join(rating_dir, f"{brand_name}_rating_pie.png"))
                
                if 'sentiment' not in filtered_df.columns or 'sentiment_category' not in filtered_df.columns:
                    print("添加情感分析...")
                    sentiments = []
                    categories = []
                    for review in filtered_df[review_col]:
                        polarity, category = analyze_sentiment(review)
                        sentiments.append(polarity)
                        categories.append(category)
                    filtered_df['sentiment'] = sentiments
                    filtered_df['sentiment_category'] = categories
                
                lda_model, dictionary, corpus, topic_df = analyze_topic_sentiment_correlation(
                    filtered_df, brand_name, os.path.join(topic_dir, f"{brand_name}_topic_sentiment.png"), num_topics=5
                )
                
                analyze_rating_topic_correlation(
                    filtered_df, brand_name, os.path.join(rating_dir, f"{brand_name}_rating_topic.png"),
                    lda_model, dictionary, corpus, num_topics=5
                )
                
                analyze_word_sentiment_correlation(filtered_df, brand_name, os.path.join(word_dir, f"{brand_name}_word_sentiment.png"))
                
                analyze_country_topic_correlation(
                    filtered_df, brand_name, os.path.join(country_dir, f"{brand_name}_country_topic.png"),
                    lda_model, dictionary, corpus, num_topics=5
                )
                
                analyze_review_length_sentiment(filtered_df, brand_name, os.path.join(sentiment_dir, f"{brand_name}_length_sentiment.png"))
                
                analyze_time_series_sentiment(filtered_df, brand_name, os.path.join(time_dir, f"{brand_name}_time_sentiment.png"))
                
                if country_col:
                    create_country_bar_chart(filtered_df, brand_name, os.path.join(country_dir, f"{brand_name}_country_distribution.png"))
                    create_country_treemap(filtered_df, brand_name, os.path.join(country_dir, f"{brand_name}_country_treemap.html"))
                
                generate_word_cloud(filtered_df, brand_name, os.path.join(word_dir, f"{brand_name}_word_cloud.png"))
                # 添加按评分分类的词云生成
                generate_rating_word_clouds(filtered_df, brand_name, word_dir)
                
                # 创建时间趋势分析图（评分和评论数量）
                analyze_combined_trends(filtered_df, brand_name, os.path.join(time_dir, f"{brand_name}_time_trends.png"))
                
                sentiment_data_file = os.path.join(sentiment_dir, f"{brand_name}_with_sentiment.csv")
                filtered_df.to_csv(sentiment_data_file, index=False)
                print(f"保存带情感分析的数据到 {sentiment_data_file}")
                
                organize_analysis_files(run_dir)
                
                # 在生成HTML报告前，预先并发处理所有AI分析请求
                print("\n开始并发处理AI分析请求...")
                from ai_analysis import call_ai_model_concurrent, analyze_rating_distribution, analyze_country_distribution, analyze_sentiment_trends, analyze_word_cloud, analyze_time_trends
                
                # 准备所有需要分析的提示
                prompts = []
                # 评分分布分析
                rating_col = next((col for col in filtered_df.columns if col.lower() == 'rating'), None)
                if rating_col:
                    rating_counts = filtered_df[rating_col].value_counts().sort_index()
                    total_reviews = len(filtered_df)
                    prompts.append(f"""分析以下{brand_name}的评分分布数据：
                    总评论数：{total_reviews}
                    1星评分：{rating_counts.get(1, 0)}条 ({rating_counts.get(1, 0)/total_reviews*100:.1f}%)
                    2星评分：{rating_counts.get(2, 0)}条 ({rating_counts.get(2, 0)/total_reviews*100:.1f}%)
                    3星评分：{rating_counts.get(3, 0)}条 ({rating_counts.get(3, 0)/total_reviews*100:.1f}%)
                    4星评分：{rating_counts.get(4, 0)}条 ({rating_counts.get(4, 0)/total_reviews*100:.1f}%)
                    5星评分：{rating_counts.get(5, 0)}条 ({rating_counts.get(5, 0)/total_reviews*100:.1f}%)
                    
                    请分析这个评分分布的特点，包括：
                    1. 评分的整体趋势
                    2. 高分和低分的比例
                    3. 用户满意度水平
                    4. 是否存在明显的评分倾向
                    
                    请用简洁的语言总结分析结果。""")
                
                # 国家分布分析
                country_col = next((col for col in filtered_df.columns if col.lower() == 'country'), None)
                if country_col:
                    country_counts = filtered_df[country_col].value_counts()
                    total_reviews = len(filtered_df)
                    top_countries = country_counts.head(5)
                    prompts.append(f"""分析以下{brand_name}的评论国家分布数据：
                    总评论数：{total_reviews}
                    前5个国家的分布：
                    {', '.join([f'{country}: {count}条 ({count/total_reviews*100:.1f}%)' for country, count in top_countries.items()])}
                    
                    请分析这个地理分布的特点，包括：
                    1. 用户群体的地理集中度
                    2. 主要市场区域
                    3. 市场覆盖的多样性
                    4. 是否存在明显的地域性特征
                    
                    请用简洁的语言总结分析结果。""")
                
                # 情感分析
                sentiment_col = 'sentiment_category'
                if sentiment_col in filtered_df.columns:
                    sentiment_counts = filtered_df[sentiment_col].value_counts()
                    total_reviews = len(filtered_df)
                    prompts.append(f"""分析以下{brand_name}的评论情感分布数据：
                    总评论数：{total_reviews}
                    正面评价：{sentiment_counts.get('Positive', 0)}条 ({sentiment_counts.get('Positive', 0)/total_reviews*100:.1f}%)
                    中性评价：{sentiment_counts.get('Neutral', 0)}条 ({sentiment_counts.get('Neutral', 0)/total_reviews*100:.1f}%)
                    负面评价：{sentiment_counts.get('Negative', 0)}条 ({sentiment_counts.get('Negative', 0)/total_reviews*100:.1f}%)
                    
                    请分析这个情感分布的特点，包括：
                    1. 整体情感倾向                    2. 正面与负面评价的比例
                    3. 用户满意度水平                    4. 是否存在明显的情感极化现象
                    
                    请用简洁的语言总结分析结果。""")
                
                # 词云分析
                review_col = next((col for col in filtered_df.columns if col.lower() == 'review'), None)
                if review_col:
                    all_text = ' '.join(filtered_df[review_col].dropna().astype(str))
                    
                    # 设置停用词 - 增强版
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
                        'as', 'at', 'before', 'after', 'above', 'below', 'between', 'into', 'through', 'during',
                        'few', 'more', 'most', 'other', 'some', 'its', 'his', 'her', 'our', 'their', 'mine', 'yours',
                        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'am', 'is', 'are', 'was', 'were', 'very',
                        
                        # 品牌和产品相关词
                        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
                        'received', 'bought', 'purchase', 'purchased', 'buy', 'use', 'used', 'using',
                        
                        # 电商常见词
                        'shipping', 'delivery', 'arrived', 'package', 'item', 'items', 'customer', 'customers',
                        'review', 'reviews', 'rating', 'ratings', 'star', 'stars', 'experience', 'website', 'online',
                        'shop', 'shopping', 'store', 'ordered', 'ordering', 'shipped', 'shipping', 'delivered'
                    }
                    stopwords.update(custom_stopwords)
                    
                    # 处理文本，移除标点符号和停用词
                    text = all_text.lower()
                    for p in string.punctuation:
                        text = text.replace(p, ' ')
                    words = text.split()
                    filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
                    
                    import pandas as pd
                    word_freq = pd.Series(filtered_words).value_counts().head(10)
                    prompts.append(f"""分析以下{brand_name}的评论关键词数据：
                    最常见的10个关键词及其出现次数：
                    {', '.join([f'{word}: {count}次' for word, count in word_freq.items()])}
                    
                    请分析这些关键词的特点，包括：
                    1. 用户最关注的方面                    2. 主要讨论的话题                    3. 是否存在明显的问题关键词                    4. 品牌特征词的出现情况
                    
                    请用简洁的语言总结分析结果。""")
                
                # 时间趋势分析
                date_col = next((col for col in filtered_df.columns if col.lower() == 'date'), None)
                if date_col:
                    filtered_df['date'] = pd.to_datetime(filtered_df[date_col])
                    monthly_counts = filtered_df.groupby(filtered_df['date