import os
import pandas as pd
import json
import datetime
import argparse
import re
import base64
# 导入AI分析函数
from ai_analysis import analyze_rating_distribution, analyze_country_distribution, analyze_sentiment_trends, analyze_word_cloud, analyze_time_trends, call_ai_model

def extract_topics_from_lda(topic_file):
    """从LDA主题文件中提取主题数据"""
    try:
        topic_df = pd.read_csv(topic_file)
        topics = {}
        for idx, row in topic_df.iterrows():
            topics[f'Topic_{idx+1}'] = {
                'keywords': row['Keywords'].split(','),
                'sentiment': row['Sentiment'],
                'percentage': row['Percentage']
            }
        return topics
    except Exception as e:
        print(f"读取主题文件出错: {e}")
        return {}

def extract_complaint_categories(topic_data, review_data):
    """从主题数据和评论数据中提取投诉类别"""
    categories = []
    try:
        # 基于主题数据生成投诉类别
        for topic_id, topic_info in topic_data.items():
            sentiment = topic_info['sentiment']
            if sentiment < 0:  # 负面情感的主题作为投诉类别
                category = {
                    'category': ' '.join(topic_info['keywords'][:3]),  # 使用前3个关键词作为类别名
                    'keywords': topic_info['keywords'],
                    'percentage': round(topic_info['percentage'] * 100, 1),
                    'sentiment': sentiment,
                    'color': 'red' if sentiment < -0.5 else 'orange'
                }
                categories.append(category)
        
        # 如果没有主题数据，从评论数据中提取
        if not categories and 'sentiment' in review_data.columns:
            negative_reviews = review_data[review_data['sentiment'] < 0]
            if not negative_reviews.empty:
                categories.append({
                    'category': '一般性投诉',
                    'keywords': ['问题', '投诉', '建议'],
                    'percentage': round(len(negative_reviews) / len(review_data) * 100, 1),
                    'sentiment': negative_reviews['sentiment'].mean(),
                    'color': 'orange'
                })
    except Exception as e:
        print(f"提取投诉类别时出错: {e}")
    
    return sorted(categories, key=lambda x: abs(x['sentiment']), reverse=True)

def generate_complaint_summary(complaint_categories):
    """生成投诉要点总结"""
    summaries = []
    for category in complaint_categories:
        summary = {
            'category': category['category'],
            'percentage': category['percentage'],
            'summary': f"主要涉及{', '.join(category['keywords'][:5])}等方面的问题",
            'color': category['color']
        }
        summaries.append(summary)
    return summaries

def generate_improvement_suggestions(complaint_categories):
    """基于投诉类别生成改进建议"""
    suggestions = []
    for category in complaint_categories:
        keywords = category['keywords'][:3]
        suggestion = f"针对{category['category']}问题（占比{category['percentage']}%），建议关注{', '.join(keywords)}等方面，制定相应的改进措施。"
        suggestions.append(suggestion)
    return suggestions

def generate_summary_data(review_data):
    """生成数据摘要"""
    total_reviews = len(review_data)
    negative_reviews = len(review_data[review_data['sentiment'] < 0]) if 'sentiment' in review_data.columns else 0
    negative_percentage = round(negative_reviews / total_reviews * 100, 1) if total_reviews > 0 else 0
    average_rating = round(review_data['rating_col'].mean(), 1) if 'rating_col' in review_data.columns else 0.0
    
    return {
        'total_reviews': total_reviews,
        'negative_percentage': negative_percentage,
        'total_issues': negative_reviews,
        'average_rating': average_rating
    }

def generate_html_report(run_dir, brand_name):
    """生成HTML报告"""
    try:
        # 定位分析结果目录
        analysis_dir = os.path.join(run_dir, "analysis_results")
        if not os.path.exists(analysis_dir):
            print(f"Analysis directory not found: {analysis_dir}")
            return None
            
        # 各分析子目录
        rating_dir = os.path.join(analysis_dir, "rating_analysis")
        sentiment_dir = os.path.join(analysis_dir, "sentiment_analysis")
        topic_dir = os.path.join(analysis_dir, "topic_analysis")
        country_dir = os.path.join(analysis_dir, "country_analysis")
        time_dir = os.path.join(analysis_dir, "time_analysis")
        word_dir = os.path.join(analysis_dir, "word_analysis")
        
        # 加载评论数据
        sentiment_data_file = os.path.join(sentiment_dir, f"{brand_name}_with_sentiment.csv")
        if not os.path.exists(sentiment_data_file):
            print(f"Sentiment data file not found: {sentiment_data_file}")
            return None
            
        review_data = pd.read_csv(sentiment_data_file)
        
        # 提取主题数据
        topic_sentiment_file = os.path.join(topic_dir, f"{brand_name}_topic_sentiment_data.csv")
        topic_data = {}
        if os.path.exists(topic_sentiment_file):
            topic_data = extract_topics_from_lda(topic_sentiment_file)
        
        # 生成投诉类别数据
        complaint_categories = extract_complaint_categories(topic_data, review_data)
        
        # 提取关键词频率
        keyword_data = extract_keyword_frequency(word_dir, review_data)
        
        # 生成数据摘要
        summary_data = generate_summary_data(review_data)
        
        # 生成投诉要点总结
        complaint_summaries = generate_complaint_summary(complaint_categories)
        
        # 生成改进建议
        improvement_suggestions = generate_improvement_suggestions(complaint_categories)
        
        # 生成顶部问题文本
        top_issues = [cat['category'] for cat in complaint_categories[:3]]
        if len(top_issues) >= 3:
            top_issues_text = f"{top_issues[0]}、{top_issues[1]}和{top_issues[2]}"
        elif len(top_issues) == 2:
            top_issues_text = f"{top_issues[0]}和{top_issues[1]}"
        elif len(top_issues) == 1:
            top_issues_text = top_issues[0]
        else:
            top_issues_text = "未发现明显问题"
        
        # 使用AI模型生成各维度分析结论
        print("暂时跳过AI分析结论生成...")
        ai_analyses = {
            'rating_analysis': None,
            'country_analysis': None,
            'sentiment_analysis': None, 
            'word_analysis': None,
            'time_analysis': None,
            'topic_analysis': None
        }
        
        """
        print("正在使用AI模型生成分析结论...")
        ai_analyses = {
            'rating_analysis': analyze_rating_distribution(review_data, brand_name),
            'country_analysis': analyze_country_distribution(review_data, brand_name),
            'sentiment_analysis': analyze_sentiment_trends(review_data, brand_name),
            'word_analysis': analyze_word_cloud(review_data, brand_name),
            'time_analysis': analyze_time_trends(review_data, brand_name),
            'topic_analysis': None  # 初始化主题分析结果
        }
        """
        
        # 将AI分析结论转换为HTML格式
        for key in ai_analyses:
            if ai_analyses[key]:
                ai_analyses[key] = markdown_to_html(ai_analyses[key])
        
        # 尝试从topic_analysis文件夹中读取AI分析结论
        topic_analysis_file = os.path.join(topic_dir, f"{brand_name}_topic_analysis.txt")
        if os.path.exists(topic_analysis_file):
            try:
                with open(topic_analysis_file, 'r', encoding='utf-8') as f:
                    ai_analyses['topic_analysis'] = markdown_to_html(f.read())
                print(f"已加载主题分析结论: {topic_analysis_file}")
            except Exception as e:
                print(f"读取主题分析文件出错: {e}")
        
        # 生成综合分析报告
        print("暂时跳过综合分析报告生成...")
        comprehensive_analysis = "AI分析功能已暂时关闭。"
        """
        comprehensive_analysis = generate_comprehensive_analysis(review_data, brand_name)
        """
        if comprehensive_analysis:
            comprehensive_analysis = markdown_to_html(comprehensive_analysis)
        
        # 编码图片为base64
        images = {}
        image_files = {
            'rating_pie': os.path.join(rating_dir, f"{brand_name}_rating_pie.png"),
            'word_cloud': os.path.join(word_dir, f"{brand_name}_word_cloud.png"),
            'country_distribution': os.path.join(country_dir, f"{brand_name}_country_distribution.png"),
            'time_sentiment': os.path.join(time_dir, f"{brand_name}_time_sentiment.png"),
            'word_sentiment': os.path.join(word_dir, f"{brand_name}_word_sentiment.png"),
            'topic_sentiment': os.path.join(topic_dir, f"{brand_name}_topic_sentiment.png"),
            'rating_topic': os.path.join(rating_dir, f"{brand_name}_rating_topic.png"),
            'country_topic': os.path.join(country_dir, f"{brand_name}_country_topic.png")
        }
        
        for key, path in image_files.items():
            if os.path.exists(path):
                images[key] = encode_image_to_base64(path)
        
        # 生成投诉要点HTML
        complaint_summary_html = ""
        for summary in complaint_summaries:
            color_class = {
                'red': 'bg-red-50 border-red-500',
                'orange': 'bg-orange-50 border-orange-500',
                'yellow': 'bg-yellow-50 border-yellow-500',
                'blue': 'bg-blue-50 border-blue-500',
                'green': 'bg-green-50 border-green-500'
            }.get(summary['color'], 'bg-gray-50 border-gray-500')
            
            complaint_summary_html += f"""
            <div class="p-3 {color_class} rounded border-l-4">
                <p class="font-medium">{summary['category']} ({summary['percentage']}%)</p>
                <p class="text-sm">{summary['summary']}</p>
            </div>
            """
        
        # 生成改进建议HTML
        improvement_suggestions_html = ""
        for suggestion in improvement_suggestions:
            improvement_suggestions_html += f"<li>{suggestion}</li>\n"
        
        # 生成词云HTML
        word_cloud_img = ""
        if 'word_cloud' in images and images['word_cloud']:
            word_cloud_img = f'<img src="data:image/png;base64,{images["word_cloud"]}" alt="词云图" class="word-cloud-img">'
            if ai_analyses['word_analysis']:
                word_cloud_img += f'<div class="analysis-conclusion"><h4>AI分析结论</h4><p>{ai_analyses["word_analysis"]}</p></div>'
        
        # 生成评分分布HTML
        rating_pie_img = ""
        if 'rating_pie' in images and images['rating_pie']:
            rating_pie_img = f'<img src="data:image/png;base64,{images["rating_pie"]}" alt="评分分布" class="chart-img">'
            if ai_analyses['rating_analysis']:
                rating_pie_img += f'<div class="analysis-conclusion"><h4>AI分析结论</h4><p>{ai_analyses["rating_analysis"]}</p></div>'
        
        # 生成国家分布HTML
        country_distribution_img = ""
        if 'country_distribution' in images and images['country_distribution']:
            country_distribution_img = f'<img src="data:image/png;base64,{images["country_distribution"]}" alt="国家分布" class="chart-img">'
            if ai_analyses['country_analysis']:
                country_distribution_img += f'<div class="analysis-conclusion"><h4>AI分析结论</h4><p>{ai_analyses["country_analysis"]}</p></div>'
        
        # 生成情感分析HTML
        sentiment_analysis_img = ""
        if 'time_sentiment' in images and images['time_sentiment']:
            sentiment_analysis_img = f'<img src="data:image/png;base64,{images["time_sentiment"]}" alt="情感分析" class="chart-img">'
            if ai_analyses['sentiment_analysis']:
                sentiment_analysis_img += f'<div class="analysis-conclusion"><h4>AI分析结论</h4><p>{ai_analyses["sentiment_analysis"]}</p></div>'
        
        # 生成词语情感关联HTML
        word_sentiment_img = ""
        if 'word_sentiment' in images and images['word_sentiment']:
            word_sentiment_img = f'<img src="data:image/png;base64,{images["word_sentiment"]}" alt="词语情感关联" class="chart-img">'
            # 尝试读取词语情感关联的专门分析结论
            word_sentiment_analysis_file = os.path.join(word_dir, f"{brand_name}_word_sentiment_analysis.txt")
            if os.path.exists(word_sentiment_analysis_file):
                try:
                    with open(word_sentiment_analysis_file, 'r', encoding='utf-8') as f:
                        word_sentiment_analysis = markdown_to_html(f.read())
                        word_sentiment_img += f'<div class="analysis-conclusion"><h4>AI分析结论</h4><p>{word_sentiment_analysis}</p></div>'
                        print(f"已加载词语情感关联分析结论: {word_sentiment_analysis_file}")
                except Exception as e:
                    print(f"读取词语情感关联分析文件出错: {e}")
                    # 如果读取失败，回退到使用词云分析结论
                    if ai_analyses['word_analysis']:
                        word_sentiment_img += f'<div class="analysis-conclusion"><h4>AI分析结论</h4><p>{ai_analyses["word_analysis"]}</p></div>'
            # 如果没有专门的词语情感关联分析文件，回退到使用词云分析结论
            elif ai_analyses['word_analysis']:
                word_sentiment_img += f'<div class="analysis-conclusion"><h4>AI分析结论</h4><p>{ai_analyses["word_analysis"]}</p></div>'
        
        # 生成主题分析HTML
        topic_analysis_img = ""
        if 'topic_sentiment' in images and images['topic_sentiment']:
            topic_analysis_img = f'<img src="data:image/png;base64,{images["topic_sentiment"]}" alt="主题情感分析" class="chart-img">'
            if ai_analyses['topic_analysis']:
                topic_analysis_img += f'<div class="analysis-conclusion"><h4>AI分析结论</h4><p>{ai_analyses["topic_analysis"]}</p></div>'
        
        # 添加国家矩形树状图链接
        country_treemap_link = ""
        country_treemap_path = os.path.join(country_dir, f"{brand_name}_country_treemap.html")
        if os.path.exists(country_treemap_path):
            relative_path = os.path.relpath(country_treemap_path, run_dir)
            country_treemap_link = f'<p class="mt-4"><a href="{relative_path}" target="_blank" class="text-blue-600 hover:underline">查看交互式国家分布矩形树状图</a></p>'
        
        # 准备数据用于JavaScript
        complaint_data_json = json.dumps(complaint_categories)
        keyword_data_json = json.dumps(keyword_data)
        
        # 添加综合分析结论
        comprehensive_analysis_html = ""
        if comprehensive_analysis:
            comprehensive_analysis_html = f"""
            <div class="bg-blue-50 p-4 rounded-lg mb-6">
                <h3 class="text-xl font-bold mb-2">AI综合分析</h3>
                <div class="text-gray-800">{comprehensive_analysis.replace('\n', '<br>')}</div>
            </div>
            """
        
        # 更新CSS样式，添加分析结论的样式
        additional_css = """
        .analysis-conclusion {
            margin-top: 15px;
            padding: 10px;
            background-color: #f0f7ff;
            border-radius: 5px;
            border-left: 4px solid #3b82f6;
        }
        .analysis-conclusion h4 {
            margin-top: 0;
            font-weight: bold;
            color: #1e40af;
        }
        .chart-container {
            margin-bottom: 30px;
        }
        """
        
        # 获取当前时间
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 使用字符串替换而不是format方法来填充HTML模板
        # 首先将两个HTML模板片段拼接起来
        html_content = html_template.replace('</body>\n</html>', '') + html_fragment
        
        # 替换基本变量
        html_content = html_content.replace('{brand_name}', brand_name)
        html_content = html_content.replace('{current_time}', current_time)
        html_content = html_content.replace('{total_reviews}', str(summary_data['total_reviews']))
        html_content = html_content.replace('{negative_percentage}', str(summary_data['negative_percentage']))
        html_content = html_content.replace('{total_issues}', str(summary_data['total_issues']))
        html_content = html_content.replace('{average_rating}', str(summary_data['average_rating']))
        html_content = html_content.replace('{rating_pie_img}', rating_pie_img)
        html_content = html_content.replace('{country_distribution_img}', country_distribution_img)
        html_content = html_content.replace('{sentiment_analysis_img}', sentiment_analysis_img)
        html_content = html_content.replace('{word_sentiment_img}', word_sentiment_img)
        html_content = html_content.replace('{topic_analysis_img}', topic_analysis_img)
        html_content = html_content.replace('{word_cloud_img}', word_cloud_img)
        html_content = html_content.replace('{top_issues_text}', top_issues_text)
        html_content = html_content.replace('{complaint_summary_html}', complaint_summary_html)
        html_content = html_content.replace('{improvement_suggestions}', improvement_suggestions_html)
        html_content = html_content.replace('{country_treemap_link}', country_treemap_link)
        html_content = html_content.replace('{comprehensive_analysis_html}', comprehensive_analysis_html)
        html_content = html_content.replace('{additional_css}', additional_css)
        # 替换JavaScript变量
        html_content = html_content.replace('{complaint_data_json}', complaint_data_json)
        html_content = html_content.replace('{keyword_data_json}', keyword_data_json)
        
        # 准备SWOT分析所需的变量
        if 'sentiment_category' in review_data.columns:
            sentiment_counts = review_data['sentiment_category'].value_counts()
            positive_pct = sentiment_counts.get('Positive', 0) / summary_data['total_reviews'] * 100 if summary_data['total_reviews'] > 0 else 0
        else:
            positive_pct = 100 - summary_data['negative_percentage']
            
        # 准备国家分布数据
        top_countries_text = "全球各地区"
        if 'country' in review_data.columns:
            country_counts = review_data['country'].value_counts()
            top_countries = country_counts.head(3)
            if not top_countries.empty:
                top_countries_text = ', '.join([f"{country}" for country in top_countries.index])
        
        # 替换SWOT分析变量
        html_content = html_content.replace('{positive_pct:.1f}', f"{positive_pct:.1f}")
        html_content = html_content.replace('{top_countries_text}', top_countries_text)
        
        # 保存HTML报告
        report_path = os.path.join(run_dir, f"{brand_name}_report.html")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"报告已生成: {report_path}")
        return report_path
    except Exception as e:
        print(f"生成HTML报告时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_keyword_frequency(word_dir, review_data):
    """从评论数据中提取关键词频率"""
    keyword_data = {}
    try:
        if 'review' in review_data.columns:
            # 简单处理：将所有评论合并，分词并计数
            all_text = ' '.join(review_data['review'].dropna().astype(str))
            words = all_text.lower().split()
            # 过滤掉常见的停用词
            stop_words = ['the', 'and', 'is', 'in', 'to', 'a', 'of', 'for', 'with', 'on', 'at', 'from', 'by', 'about', 'as']
            filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
            
            # 计算词频
            from collections import Counter
            word_counts = Counter(filtered_words)
            
            # 取前20个高频词
            top_words = word_counts.most_common(20)
            
            for word, count in top_words:
                keyword_data[word] = count
    except Exception as e:
        print(f"提取关键词频率时出错: {e}")
    
    return keyword_data

def encode_image_to_base64(image_path):
    """将图片编码为base64格式"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
    except Exception as e:
        print(f"编码图片出错: {e}")
        return ""

def generate_comprehensive_analysis(review_data, brand_name):
    """生成综合分析报告"""
    try:
        # 计算基本统计数据
        total_reviews = len(review_data)
        avg_rating = review_data['rating_col'].mean() if 'rating_col' in review_data.columns else 0.0
        
        # 情感分析
        if 'sentiment_category' in review_data.columns:
            sentiment_counts = review_data['sentiment_category'].value_counts()
            positive_pct = sentiment_counts.get('Positive', 0) / total_reviews * 100
            neutral_pct = sentiment_counts.get('Neutral', 0) / total_reviews * 100
            negative_pct = sentiment_counts.get('Negative', 0) / total_reviews * 100
        else:
            positive_pct = neutral_pct = negative_pct = 0
        
        # 生成综合分析文本
        analysis = f"""{brand_name}的Trustpilot评论综合分析:

总体情况:共收集到{total_reviews}条评论，平均评分为{avg_rating:.1f}/5。

情感分布:正面评价占{positive_pct:.1f}%，中性评价占{neutral_pct:.1f}%，负面评价占{negative_pct:.1f}%。

"""
        
        # 添加评分分布分析
        if 'rating' in review_data.columns:
            rating_analysis = analyze_rating_distribution(review_data, brand_name)
            if rating_analysis:
                analysis += f"评分分布:{rating_analysis.split('.')[0]}。\n\n"
            
        # 添加国家分布分析
        if 'country' in review_data.columns:
            country_counts = review_data['country'].value_counts()
            top_countries = country_counts.head(3)
            top_countries_text = ', '.join([f"{country}({count}条)" for country, count in top_countries.items()])
            
            analysis += f"地域分布:评论主要来自{top_countries_text}等地区。\n\n"
        
        # 添加时间趋势分析
        if 'date' in review_data.columns:
            try:
                review_data['date'] = pd.to_datetime(review_data['date'])
                recent_month = review_data[review_data['date'] > (review_data['date'].max() - pd.Timedelta(days=30))]
                recent_count = len(recent_month)
                recent_sentiment = recent_month['sentiment'].mean() if 'sentiment' in recent_month.columns else 0
                
                if recent_count > 0:
                    trend_text = "改善" if recent_sentiment > 0 else "恶化" if recent_sentiment < 0 else "保持稳定"
                    analysis += f"近期趋势:最近30天内有{recent_count}条评论，整体评价趋势{trend_text}。\n\n"
            except Exception as e:
                print(f"分析时间趋势出错: {e}")
        
        # 添加建议
        if negative_pct > 20:
            analysis += "改进建议:负面评价比例较高，建议重点关注用户投诉的主要问题，制定针对性的改进措施。"
        elif negative_pct > 10:
            analysis += "改进建议:存在一定比例的负面评价，建议关注这些问题并持续改进产品和服务质量。"
        else:
            analysis += "改进建议:虽然负面评价比例较低，但仍建议关注个别投诉问题，保持良好的用户体验。"
        
        return analysis
    except Exception as e:
        print(f"生成综合分析报告出错: {e}")
        return "无法生成综合分析报告，请检查数据完整性。"

def main():
    parser = argparse.ArgumentParser(description='生成Trustpilot评论分析报告')
    parser.add_argument('--run_dir', type=str, required=True, help='运行目录路径')
    parser.add_argument('--brand_name', type=str, required=True, help='品牌名称')
    parser.add_argument('--generate_all', action='store_true', help='是否生成所有文件夹的报告')
    
    args = parser.parse_args()
    
    if args.generate_all:
        generate_all_folder_reports(args.run_dir)
    else:
        generate_html_report(args.run_dir, args.brand_name)

if __name__ == "__main__":
    main()

# HTML报告模板
html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{brand_name} - Trustpilot评论分析报告</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        .chart-img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
        .word-cloud-img {{ max-width: 100%; height: auto; border-radius: 8px; }}
        .complaint-card {{ transition: transform 0.3s; }}
        .complaint-card:hover {{ transform: translateY(-5px); }}
        .swot-card {{ border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }}
        .swot-strength {{ background-color: #d1fae5; border-left: 4px solid #10b981; }}
        .swot-weakness {{ background-color: #fee2e2; border-left: 4px solid #ef4444; }}
        .swot-opportunity {{ background-color: #e0f2fe; border-left: 4px solid #3b82f6; }}
        .swot-threat {{ background-color: #fef3c7; border-left: 4px solid #f59e0b; }}
        
        /* 响应式设计增强 */
        @media (max-width: 768px) {{
            .container {{ padding: 10px; }}
            h1 {{ font-size: 1.5rem; }}
            h2 {{ font-size: 1.25rem; }}
            .chart-container {{ overflow-x: auto; }}
            .analysis-conclusion {{ padding: 8px; }}
            .swot-card {{ padding: 0.75rem; }}
            .text-3xl {{ font-size: 1.5rem; }}
        }}
        
        /* 表格响应式 */
        table {{ width: 100%; overflow-x: auto; display: block; }}
        
        /* 图表容器响应式 */
        .chart-container {{ margin-bottom: 20px; overflow-x: auto; }}
        
        /* 导航菜单响应式 */
        .nav-menu {{ 
            display: flex; 
            flex-wrap: wrap; 
            justify-content: center; 
            gap: 15px; 
            margin: 0 auto 20px auto;
            padding: 12px;
            background-color: #f9fafb;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            max-width: 800px;
        }}
        .nav-item {{ 
            padding: 10px 16px; 
            background-color: white; 
            border-radius: 6px;
            color: #4b5563;
            font-weight: 500;
            transition: all 0.2s ease;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            text-decoration: none;
        }}
        .nav-item:hover {{
            background-color: #e5e7eb;
            transform: translateY(-2px);
            box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
            color: #1f2937;
        }}
        
        @media (max-width: 640px) {{
            .nav-menu {{ 
                flex-direction: row;
                flex-wrap: wrap;
                justify-content: center;
                padding: 8px;
            }}
            .nav-item {{ 
                width: calc(50% - 10px);
                text-align: center;
                margin-bottom: 8px;
                padding: 8px 10px;
            }}
            .p-6 {{ padding: 1rem; }}
            .gap-4 {{ gap: 0.5rem; }}
            .gap-8 {{ gap: 1rem; }}
        }}
        {additional_css}
    </style>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-8 max-w-6xl">
        <header class="mb-8 text-center">
            <h1 class="text-3xl font-bold text-gray-800 mb-2">{brand_name} - Trustpilot评论分析报告</h1>
            <p class="text-gray-600">生成时间: {current_time}</p>
        </header>
        
        {comprehensive_analysis_html}
        
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-2xl font-bold mb-4 text-gray-800">数据概览</h2>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="bg-blue-50 p-4 rounded-lg text-center">
                    <p class="text-sm text-gray-600">总评论数</p>
                    <p class="text-3xl font-bold text-blue-600">{total_reviews}</p>
                </div>
                <div class="bg-green-50 p-4 rounded-lg text-center">
                    <p class="text-sm text-gray-600">平均评分</p>
                    <p class="text-3xl font-bold text-green-600">{average_rating}/5</p>
                </div>
                <div class="bg-red-50 p-4 rounded-lg text-center">
                    <p class="text-sm text-gray-600">负面评价比例</p>
                    <p class="text-3xl font-bold text-red-600">{negative_percentage}%</p>
                </div>
                <div class="bg-orange-50 p-4 rounded-lg text-center">
                    <p class="text-sm text-gray-600">问题总数</p>
                    <p class="text-3xl font-bold text-orange-600">{total_issues}</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# 另一个HTML片段
html_fragment = """</div>
        </div>
        
        <!-- 添加导航菜单，方便在移动设备上快速跳转到各部分 -->
        <div class="nav-menu mb-6">
            <a href="#rating" class="nav-item">评分分布</a>
            <a href="#country" class="nav-item">国家分布</a>
            <a href="#sentiment" class="nav-item">情感分析</a>
            <a href="#word" class="nav-item">词语分析</a>
            <a href="#topic" class="nav-item">主题分析</a>
            <a href="#swot" class="nav-item">SWOT分析</a>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div id="rating" class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-bold mb-4 text-gray-800">评分分布</h2>
                <div class="chart-container">
                    {rating_pie_img}
                </div>
            </div>
            <div id="country" class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-bold mb-4 text-gray-800">国家分布</h2>
                <div class="chart-container">
                    {country_distribution_img}
                    {country_treemap_link}
                </div>
            </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div id="sentiment" class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-bold mb-4 text-gray-800">情感分析</h2>
                <div class="chart-container">
                    {sentiment_analysis_img}
                </div>
            </div>
            <div id="word" class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-bold mb-4 text-gray-800">词语情感关联</h2>
                <div class="chart-container">
                    {word_sentiment_img}
                </div>
            </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
            <div id="topic" class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-bold mb-4 text-gray-800">主题分析</h2>
                <div class="chart-container">
                    {topic_analysis_img}
                </div>
            </div>
            <div class="bg-white rounded-lg shadow-md p-6">
                <h2 class="text-xl font-bold mb-4 text-gray-800">词云分析</h2>
                <div class="chart-container">
                    {word_cloud_img}
                </div>
            </div>
        </div>
        
        <div id="swot" class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-2xl font-bold mb-4 text-gray-800">SWOT分析</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="swot-card swot-strength">
                    <h3 class="font-bold text-lg mb-2">优势 (Strengths)</h3>
                    <p>基于评论数据分析，{brand_name}的主要优势在于：</p>
                    <ul class="list-disc pl-5 text-gray-700 space-y-1 mt-2">
                        <li>正面评价占比{positive_pct:.1f}%，用户满意度较高</li>
                        <li>平均评分达到{average_rating}/5分</li>
                        <li>在{top_countries_text}等地区有良好口碑</li>
                    </ul>
                </div>
                <div class="swot-card swot-weakness">
                    <h3 class="font-bold text-lg mb-2">劣势 (Weaknesses)</h3>
                    <p>需要改进的方面主要集中在：</p>
                    <ul class="list-disc pl-5 text-gray-700 space-y-1 mt-2">
                        <li>负面评价占比{negative_percentage}%</li>
                        <li>主要问题集中在: {top_issues_text}</li>
                        <li>共有{total_issues}个问题需要解决</li>
                    </ul>
                </div>
                <div class="swot-card swot-opportunity">
                    <h3 class="font-bold text-lg mb-2">机会 (Opportunities)</h3>
                    <p>潜在的发展机会：</p>
                    <ul class="list-disc pl-5 text-gray-700 space-y-1 mt-2">
                        <li>通过解决用户反馈的问题提升服务质量</li>
                        <li>改善产品体验，提高用户满意度</li>
                        <li>扩大在高评分地区的市场份额</li>
                    </ul>
                </div>
                <div class="swot-card swot-threat">
                    <h3 class="font-bold text-lg mb-2">威胁 (Threats)</h3>
                    <p>需要警惕的风险：</p>
                    <ul class="list-disc pl-5 text-gray-700 space-y-1 mt-2">
                        <li>负面评价可能影响品牌形象</li>
                        <li>竞争对手可能提供更好的服务体验</li>
                        <li>用户期望持续提高，需不断改进</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <footer class="text-center text-gray-500 text-sm mt-12 mb-6">
            <p>© {current_time[:10]} Trustpilot评论分析系统 - 由AI辅助生成</p>
        </footer>
    </div>
    
    <script>
        // 可以在这里添加交互功能的JavaScript代码
        const complaintData = {complaint_data_json};
        const keywordData = {keyword_data_json};
        console.log('数据加载完成');
    </script>
</body>
</html>
"""

def markdown_to_html(text):
    """将Markdown文本转换为HTML"""
    try:
        # 使用正则表达式处理基本的Markdown格式
        # 处理粗体 **text**
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        # 处理斜体 *text*
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        # 处理标题 # text
        text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        text = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
        text = re.sub(r'^##### (.*?)$', r'<h5>\1</h5>', text, flags=re.MULTILINE)
        
        # 处理有序列表 1. item
        text = re.sub(r'^(\d+)\. (.*?)$', r'<li>\2</li>', text, flags=re.MULTILINE)
        
        # 处理无序列表 - item
        text = re.sub(r'^- (.*?)$', r'<li>\1</li>', text, flags=re.MULTILINE)
        text = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\g<0></ul>', text, flags=re.DOTALL)
        
        # 处理段落 - 改进版本，更好地处理多行段落
        paragraphs = re.split(r'\n{2,}', text)
        for i, p in enumerate(paragraphs):
            if not p.startswith('<') and not p.strip() == '':
                paragraphs[i] = f'<p>{p}</p>'
        text = '\n'.join(paragraphs)
        
        # 处理换行
        text = text.replace('\n', '<br>')
        
        # 修复可能的HTML标签嵌套问题
        text = text.replace('<br><ul>', '<ul>')
        text = text.replace('</ul><br>', '</ul>')
        text = text.replace('<br><li>', '<li>')
        text = text.replace('</li><br>', '</li>')
        text = text.replace('<br><p>', '<p>')
        text = text.replace('</p><br>', '</p>')
        text = text.replace('<br><h', '<h')
        text = text.replace('</h1><br>', '</h1>')
        text = text.replace('</h2><br>', '</h2>')
        text = text.replace('</h3><br>', '</h3>')
        text = text.replace('</h4><br>', '</h4>')
        text = text.replace('</h5><br>', '</h5>')
        
        return text
    except Exception as e:
        print(f"Error converting markdown to HTML: {e}")
        return text

def generate_report(filtered_df, brand_name, safe_brand_name, run_dir, analysis_dir, 
                   rating_dir, country_dir, word_dir, time_dir, sentiment_dir, topic_dir):
    """
    生成分析报告
    
    Args:
        filtered_df: 过滤后的数据
        brand_name: 品牌名称（原始）
        safe_brand_name: 安全的品牌名称（用于文件名）
        run_dir: 运行目录
        analysis_dir: 分析结果目录
        rating_dir: 评分分析目录
        country_dir: 国家分析目录
        word_dir: 词语分析目录
        time_dir: 时间分析目录
        sentiment_dir: 情感分析目录
        topic_dir: 主题分析目录
    
    Returns:
        str: 生成的报告文件路径
    """
    # 图片路径字典
    images = {
        'rating_pie': os.path.join(rating_dir, f"{safe_brand_name}_rating_pie.png"),
        'word_cloud': os.path.join(word_dir, f"{safe_brand_name}_word_cloud.png"),
        'country_distribution': os.path.join(country_dir, f"{safe_brand_name}_country_distribution.png"),
        'time_sentiment': os.path.join(time_dir, f"{safe_brand_name}_time_sentiment.png"),
        'word_sentiment': os.path.join(word_dir, f"{safe_brand_name}_word_sentiment.png"),
        'topic_sentiment': os.path.join(topic_dir, f"{safe_brand_name}_topic_sentiment.png"),
        'rating_topic': os.path.join(rating_dir, f"{safe_brand_name}_rating_topic.png"),
        'country_topic': os.path.join(country_dir, f"{safe_brand_name}_country_topic.png")
    }
    
    # 生成分析结果数据
    analysis_data = filtered_df.copy()
    
    # 生成HTML报告
    report_path = os.path.join(run_dir, f"{safe_brand_name}_report.html")
    
    # 使用旧函数生成HTML内容
    html_content = generate_html_report_content(brand_name, analysis_data, images, 
                                              run_dir, country_dir)
    
    # 写入HTML文件
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_path

def generate_html_report_content(brand_name, review_data, images, run_dir, country_dir):
    """
    生成HTML报告内容
    
    Args:
        brand_name: 品牌名称
        review_data: 评论数据
        images: 图片路径字典
        run_dir: 运行目录
        country_dir: 国家分析目录
    
    Returns:
        str: 生成的HTML内容
    """
    try:
        # 生成投诉类别数据
        complaint_categories = []  # 简化处理
        
        # 生成数据摘要
        summary_data = {
            'total_reviews': len(review_data),
            'avg_rating': review_data['rating'].mean() if 'rating' in review_data.columns else 0,
            'positive_percentage': 0,
            'negative_percentage': 0,
            'neutral_percentage': 0
        }
        
        if 'sentiment_category' in review_data.columns:
            sentiment_counts = review_data['sentiment_category'].value_counts()
            total = len(review_data)
            summary_data['positive_percentage'] = round(sentiment_counts.get('Positive', 0) / total * 100, 1)
            summary_data['negative_percentage'] = round(sentiment_counts.get('Negative', 0) / total * 100, 1)
            summary_data['neutral_percentage'] = round(sentiment_counts.get('Neutral', 0) / total * 100, 1)
        
        # 综合分析报告
        comprehensive_analysis = "AI分析功能已暂时关闭。"
        
        # 嵌入图片如果存在
        embedded_images = {}
        for key, path in images.items():
            if os.path.exists(path):
                try:
                    with open(path, "rb") as image_file:
                        encoded = base64.b64encode(image_file.read()).decode('utf-8')
                        embedded_images[key] = encoded
                except Exception as e:
                    print(f"图片嵌入失败 {key}: {e}")
        
        # 国家分布地图如果存在
        country_treemap_html = ""
        country_treemap_path = os.path.join(country_dir, f"{brand_name}_country_treemap.html")
        if os.path.exists(country_treemap_path):
            try:
                with open(country_treemap_path, 'r', encoding='utf-8') as f:
                    country_treemap_html = f.read()
                    # 只提取必要的图表部分
                    start_idx = country_treemap_html.find('<div id="chart')
                    end_idx = country_treemap_html.find('</script>', start_idx)
                    if start_idx > 0 and end_idx > 0:
                        country_treemap_html = country_treemap_html[start_idx:end_idx + 9]
            except Exception as e:
                print(f"读取国家树图HTML失败: {e}")
        
        # 日期数据
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 构建HTML内容
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{brand_name} - Trustpilot评论分析报告</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        .chart-img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
        .word-cloud-img {{ max-width: 100%; height: auto; border-radius: 8px; }}
        .complaint-card {{ transition: transform 0.3s; }}
        .complaint-card:hover {{ transform: translateY(-5px); }}
    </style>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-8 max-w-6xl">
        <header class="mb-8 text-center">
            <h1 class="text-3xl font-bold text-gray-800 mb-2">{brand_name} - Trustpilot评论分析报告</h1>
            <p class="text-gray-600">生成时间: {current_time}</p>
        </header>
        
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-2xl font-bold mb-4 text-gray-800">分析摘要</h2>
            <div class="prose max-w-none">
                <p>{comprehensive_analysis}</p>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-2xl font-bold mb-4 text-gray-800">数据概览</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-blue-50 p-4 rounded-lg text-center">
                    <p class="text-sm text-gray-600">总评论数</p>
                    <p class="text-3xl font-bold text-blue-600">{summary_data['total_reviews']}</p>
                </div>
                <div class="bg-green-50 p-4 rounded-lg text-center">
                    <p class="text-sm text-gray-600">正面评价比例</p>
                    <p class="text-3xl font-bold text-green-600">{summary_data['positive_percentage']}%</p>
                </div>
                <div class="bg-red-50 p-4 rounded-lg text-center">
                    <p class="text-sm text-gray-600">负面评价比例</p>
                    <p class="text-3xl font-bold text-red-600">{summary_data['negative_percentage']}%</p>
                </div>
                </div>
            </div>
"""
        
        # 添加评分分布部分
        if 'rating_pie' in embedded_images:
            html_content += f"""
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-2xl font-bold mb-4 text-gray-800">评分分布</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <img src="data:image/png;base64,{embedded_images['rating_pie']}" class="chart-img" alt="评分分布">
        </div>
                <div class="prose max-w-none">
                    <p>AI分析功能已暂时关闭。</p>
        </div>
                </div>
            </div>
"""
                
        # 添加国家分布部分
        if 'country_distribution' in embedded_images:
            html_content += f"""
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-2xl font-bold mb-4 text-gray-800">地域分布</h2>
            <div class="grid grid-cols-1 gap-6">
                <div>
                    <img src="data:image/png;base64,{embedded_images['country_distribution']}" class="chart-img" alt="国家分布">
                </div>
                <div class="prose max-w-none">
                    <p>AI分析功能已暂时关闭。</p>
            </div>
                </div>
            </div>
"""
                
        # 添加词云部分
        if 'word_cloud' in embedded_images:
            html_content += f"""
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-2xl font-bold mb-4 text-gray-800">关键词词云</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <img src="data:image/png;base64,{embedded_images['word_cloud']}" class="word-cloud-img" alt="词云">
                </div>
                <div class="prose max-w-none">
                    <p>AI分析功能已暂时关闭。</p>
            </div>
                </div>
            </div>
"""
                
        # 添加时间趋势部分
        if 'time_sentiment' in embedded_images:
            html_content += f"""
        <div class="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 class="text-2xl font-bold mb-4 text-gray-800">时间趋势分析</h2>
            <div class="grid grid-cols-1 gap-6">
                <div>
                    <img src="data:image/png;base64,{embedded_images['time_sentiment']}" class="chart-img" alt="时间趋势">
                </div>
                <div class="prose max-w-none">
                    <p>AI分析功能已暂时关闭。</p>
                </div>
                </div>
                </div>
"""
        
        # 结束HTML
        html_content += """
    </div>
</body>
</html>
"""

        return html_content
    except Exception as e:
        print(f"生成HTML报告内容时出错: {e}")
        return f"""<!DOCTYPE html>
<html>
<head><title>报告生成错误</title></head>
<body>
<h1>报告生成过程中发生错误</h1>
<p>错误信息: {str(e)}</p>
</body>
</html>"""