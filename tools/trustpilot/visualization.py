# visualization.py
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS
import pandas as pd
import numpy as np
import seaborn as sns
import string
import os
from collections import Counter
from data_processing import filter_valid_countries
import matplotlib.font_manager as fm

# 检查和设置中文字体
def check_chinese_fonts():
    """检查系统中可用的中文字体并设置matplotlib字体"""
    chinese_fonts = [f.name for f in fm.fontManager.ttflist if any(keyword in f.name.lower() for keyword in 
                    ['chinese', 'cjk', 'ming', 'song', 'hei', 'kai', 'gothic', 'simhei', 'simsun', 'msyh', 'yahei', 'fangsong', 'nsimsun'])]
    
    # 检查SimHei字体是否可用
    simhei_available = 'SimHei' in [f.name for f in fm.fontManager.ttflist]
    
    # 设置合适的中文字体
    if simhei_available:
        plt.rcParams['font.sans-serif'] = ['SimHei'] + plt.rcParams['font.sans-serif']
    elif chinese_fonts:
        plt.rcParams['font.sans-serif'] = [chinese_fonts[0]] + plt.rcParams['font.sans-serif']
    
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
    
    return {
        'available_chinese_fonts': chinese_fonts,
        'simhei_available': simhei_available,
        'current_sans_serif': plt.rcParams['font.sans-serif'],
        'current_font_family': plt.rcParams['font.family']
    }

# 初始化时检查并设置字体
font_info = check_chinese_fonts()

# 测试饼图生成函数
def test_rating_pie_chart(save_path='test_rating_pie.png'):
    """测试评分饼图生成功能"""
    # 创建测试数据
    rating_counts = pd.Series([10, 5, 15, 30, 40], index=[1, 2, 3, 4, 5])
    total_reviews = sum(rating_counts)
    
    # 计算百分比
    rating_percentages = (rating_counts / total_reviews * 100).round(1)
    
    # 设置颜色映射
    colors = ['#FF4136', '#FF851B', '#FFDC00', '#2ECC40', '#0074D9']
    
    plt.figure(figsize=(12, 8))
    patches, texts, autotexts = plt.pie(
        rating_counts.values, 
        labels=rating_counts.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        explode=[0.05] * len(rating_counts),
        shadow=True
    )
    
    # 设置标签文本大小和颜色，并指定字体
    for text in texts:
        text.set_fontsize(12)
        text.set_fontproperties(plt.rcParams['font.sans-serif'][0])
    for autotext in autotexts:
        autotext.set_fontsize(12)
        autotext.set_color('white')
        autotext.set_fontproperties(plt.rcParams['font.sans-serif'][0])
    
    plt.axis('equal')  # 确保饼图是圆形的
    plt.title('测试评分分布', fontsize=16, fontproperties=plt.rcParams['font.sans-serif'][0])
    
    # 添加图例，显示具体数量和百分比
    legend_labels = [f'{rating}星: {count}条 ({percentage:.1f}%)' 
                    for rating, count, percentage in zip(rating_counts.index, rating_counts.values, rating_percentages)]
    legend = plt.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    
    # 设置图例中的字体
    for text in legend.get_texts():
        text.set_fontproperties(plt.rcParams['font.sans-serif'][0])
    
    # 保存饼图
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Saved rating distribution pie chart to {os.path.abspath(save_path)}")
    plt.close()

def create_rating_pie_chart(df, brand_name, save_path):
    """创建评分分布饼图"""
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    if rating_col is None or df.empty:
        print("No rating data available for pie chart")
        return
    
    # 确保评分列为数值型
    df[rating_col] = pd.to_numeric(df[rating_col], errors='coerce')
    
    # 计算各评分的数量
    rating_counts = df[rating_col].value_counts().sort_index()
    total_reviews = len(df)
    
    # 确保包含所有评分（1-5星）
    for rating in range(1, 6):
        if rating not in rating_counts.index:
            rating_counts[rating] = 0
    rating_counts = rating_counts.sort_index()
    
    # 计算百分比
    rating_percentages = (rating_counts / total_reviews * 100).round(1)
    
    # 设置颜色映射
    colors = ['#FF4136', '#FF851B', '#FFDC00', '#2ECC40', '#0074D9']
    
    plt.figure(figsize=(12, 8))
    patches, texts, autotexts = plt.pie(
        rating_counts.values, 
        labels=rating_counts.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        explode=[0.05] * len(rating_counts),
        shadow=True
    )
    
    # 设置标签文本大小和颜色，并指定字体
    for text in texts:
        text.set_fontsize(12)
        text.set_fontproperties(plt.rcParams['font.sans-serif'][0])
    for autotext in autotexts:
        autotext.set_fontsize(12)
        autotext.set_color('white')
        autotext.set_fontproperties(plt.rcParams['font.sans-serif'][0])
    
    plt.axis('equal')  # 确保饼图是圆形的
    plt.title(f'{brand_name} 评分分布', fontsize=16, fontproperties=plt.rcParams['font.sans-serif'][0])
    
    # 添加图例，显示具体数量和百分比
    legend_labels = [f'{rating}星: {count}条 ({percentage:.1f}%)' 
                    for rating, count, percentage in zip(rating_counts.index, rating_counts.values, rating_percentages)]
    legend = plt.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    
    # 设置图例中的字体
    for text in legend.get_texts():
        text.set_fontproperties(plt.rcParams['font.sans-serif'][0])
    
    try:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved rating distribution pie chart to {save_path}")
    except Exception as e:
        print(f"Error saving pie chart: {e}")
    plt.close()
    
    # 保存评分数据到CSV文件
    rating_data = pd.DataFrame({
        'Rating': rating_counts.index,
        'Count': rating_counts.values,
        'Percentage': rating_percentages.values
    })
    rating_data_file = save_path.replace('.png', '_data.csv')
    rating_data.to_csv(rating_data_file, index=False)
    print(f"Saved rating distribution data to {rating_data_file}")
    
    # 创建评分分布柱状图
    plt.figure(figsize=(12, 6))
    bars = plt.bar(rating_counts.index, rating_counts.values, 
                  color=['#FF4136', '#FF851B', '#FFDC00', '#2ECC40', '#0074D9'])
    
    # 添加数据标签
    for bar in bars:
        height = bar.get_height()
        rating_value = int(bar.get_x() + bar.get_width()/2)
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}\n({rating_percentages[rating_value]:.1f}%)',
                ha='center', va='bottom', fontproperties=plt.rcParams['font.sans-serif'][0])
    
    plt.title(f'{brand_name} 评分分布', fontsize=16, fontproperties=plt.rcParams['font.sans-serif'][0])
    plt.xlabel('评分', fontsize=12, fontproperties=plt.rcParams['font.sans-serif'][0])
    plt.ylabel('评论数量', fontsize=12, fontproperties=plt.rcParams['font.sans-serif'][0])
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 保存柱状图
    bar_chart_path = save_path.replace('.png', '_bar.png')
    plt.savefig(bar_chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved rating distribution bar chart to {bar_chart_path}")

def analyze_combined_trends(df, brand_name, save_path):
    """分析评分和评论数量的时间趋势"""
    date_col = next((col for col in df.columns if col.lower() == 'date'), None)
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    
    if date_col is None or rating_col is None or df.empty:
        print("Missing required columns for combined trends analysis")
        return
    
    # 确保日期列是日期类型
    df['date'] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=['date'])
    if df.empty:
        print("No valid date data available")
        return
    
    # 确保评分列是数值类型
    df[rating_col] = pd.to_numeric(df[rating_col], errors='coerce')
    
    # 按月份分组
    df['month'] = df['date'].dt.to_period('M')
    monthly_data = df.groupby('month').agg({
        rating_col: 'mean',
        'date': 'count'
    })
    monthly_data.columns = ['avg_rating', 'review_count']
    
    # 创建双Y轴图表
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    # 绘制评论数量柱状图
    ax1.bar(range(len(monthly_data)), monthly_data['review_count'], alpha=0.3, color='gray', label='评论数量')
    ax1.set_ylabel('评论数量', fontsize=12)
    ax1.set_xlabel('时间', fontsize=12)
    
    # 创建第二个Y轴
    ax2 = ax1.twinx()
    
    # 绘制平均评分折线图
    line = ax2.plot(range(len(monthly_data)), monthly_data['avg_rating'], 'o-', color='blue', linewidth=2, label='平均评分')
    ax2.set_ylabel('评分', fontsize=12)
    ax2.set_ylim(0, 5.5)
    
    # 设置X轴标签为月份
    plt.xticks(range(len(monthly_data)), [str(period) for period in monthly_data.index], rotation=45)
    
    # 添加图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.title(f'{brand_name} - 评分和评论数量趋势分析', fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    try:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved combined trends analysis to {save_path}")
    except Exception as e:
        print(f"Error saving combined trends analysis: {e}")
    plt.close()
    
    # 保存趋势数据
    trends_file = save_path.replace('.png', '_data.csv')
    monthly_data.to_csv(trends_file)
    print(f"Saved combined trends data to {trends_file}")
    
    # 创建时间为横坐标的折线图
    plt.figure(figsize=(14, 8))
    
    # 转换月份为日期格式以便更好地显示
    month_dates = [pd.Period(p).to_timestamp() for p in monthly_data.index]
    
    # 创建双Y轴图表
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    # 绘制评论数量折线图
    color1 = 'tab:blue'
    ax1.set_xlabel('时间', fontsize=12)
    ax1.set_ylabel('评论数量', fontsize=12, color=color1)
    ax1.plot(month_dates, monthly_data['review_count'], 'o-', color=color1, linewidth=2, label='评论数量')
    ax1.tick_params(axis='y', labelcolor=color1)
    
    # 创建第二个Y轴
    ax2 = ax1.twinx()
    color2 = 'tab:red'
    ax2.set_ylabel('平均评分', fontsize=12, color=color2)
    ax2.plot(month_dates, monthly_data['avg_rating'], 's-', color=color2, linewidth=2, label='平均评分')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, 5.5)
    
    # 设置X轴格式
    import matplotlib.dates as mdates
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    plt.xticks(rotation=45)
    
    # 添加图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.title(f'{brand_name} - 时间趋势分析（评分和评论数量）', fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.7)
    fig.tight_layout()
    
    # 保存时间趋势折线图
    time_trend_path = save_path.replace('.png', '_timeline.png')
    plt.savefig(time_trend_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved time trend line chart to {time_trend_path}")


def create_country_bar_chart(df, brand_name, save_path):
    """创建国家分布条形图"""
    country_col = next((col for col in df.columns if col.lower() == 'country'), None)
    if country_col is None or df.empty:
        print("No country data available for bar chart")
        return
    
    valid_countries_df = filter_valid_countries(df, country_col)
    if valid_countries_df.empty:
        print("No valid country data available")
        return
    
    country_counts = valid_countries_df[country_col].value_counts()
    top_countries = country_counts.head(15) if len(country_counts) > 15 else country_counts
    
    plt.figure(figsize=(14, 8))
    bars = plt.bar(top_countries.index, top_countries.values, color='skyblue')
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1, f'{int(height)}', ha='center', va='bottom')
    
    plt.title(f'Distribution of {brand_name} Reviews by Country (Top {len(top_countries)})', fontsize=16)
    plt.xlabel('Country', fontsize=12)
    plt.ylabel('Number of Reviews', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    try:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved country distribution bar chart to {save_path}")
    except Exception as e:
        print(f"Error saving bar chart: {e}")
    plt.close()
    
    filtered_country_file = save_path.replace('.png', '_filtered.csv')
    country_counts.to_csv(filtered_country_file)
    print(f"Saved filtered country distribution to {filtered_country_file}")

def create_country_treemap(df, brand_name, save_path):
    """创建国家分布矩形树形图，点击国家可显示该国家的评论词云"""
    import os
    import json
    import base64
    from io import BytesIO
    
    country_col = next((col for col in df.columns if col.lower() == 'country'), None)
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    
    if country_col is None or rating_col is None or review_col is None or df.empty:
        print("Missing required columns for treemap")
        return
    
    valid_countries_df = filter_valid_countries(df, country_col)
    if valid_countries_df.empty:
        print("No valid country data available")
        return
    
    valid_countries_df[rating_col] = pd.to_numeric(valid_countries_df[rating_col], errors='coerce')
    country_stats = valid_countries_df.groupby(country_col).agg({
        rating_col: ['mean', 'count']
    }).reset_index()
    country_stats.columns = ['Country', 'Avg_Rating', 'Count']
    country_stats['Avg_Rating'] = country_stats['Avg_Rating'].round(1)
    
    # 创建词云图并保存为base64编码的图片
    country_wordclouds = {}
    wordcloud_dir = os.path.dirname(save_path)
    os.makedirs(wordcloud_dir, exist_ok=True)
    
    stopwords = set(STOPWORDS)
    custom_stopwords = {
        'the', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'with', 'for', 'on', 'is', 'was', 'be',
        'this', 'have', 'from', 'or', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'there', 'can', 'an', 'your', 'which', 'their', 'said', 'if', 'will', 'my', 'one',
        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
        'received', 'bought', 'purchase', 'purchased', 'buy', 'use', 'used', 'using'
    }
    stopwords.update(custom_stopwords)
    
    for country in country_stats['Country']:
        country_df = valid_countries_df[valid_countries_df[country_col] == country]
        all_reviews = ' '.join(country_df[review_col].dropna().astype(str))
        
        if not all_reviews:
            continue
            
        wordcloud = WordCloud(
            width=800, 
            height=400,
            background_color='white',
            stopwords=stopwords,
            max_words=100,
            max_font_size=100,
            random_state=42,
            collocations=False,
            font_path='simhei.ttf'  # 添加中文字体支持
        ).generate(all_reviews)
        
        # 将词云图转换为base64编码
        img = BytesIO()
        wordcloud.to_image().save(img, format='PNG')
        img.seek(0)
        img_b64 = base64.b64encode(img.getvalue()).decode('utf-8')
        country_wordclouds[country] = img_b64
    
    # 创建HTML内容 - 完全重写，使用更简单的方法
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{brand_name} 国家分布分析</title>
    <script src="https://cdn.plot.ly/plotly-2.20.0.min.js"></script>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5; 
        }}
        h1 {{ 
            text-align: center; 
            color: #333; 
            margin-bottom: 20px; 
        }}
        .container {{ 
            display: flex; 
            flex-direction: column; 
            max-width: 1200px; 
            margin: 0 auto; 
            background-color: white; 
            border-radius: 8px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
            padding: 20px;
        }}
        .content {{ 
            display: flex; 
            flex-wrap: wrap; 
        }}
        #treemap {{ 
            width: 100%; 
            height: 500px; 
            margin-bottom: 20px;
        }}
        #wordcloud-container {{ 
            width: 100%; 
            min-height: 400px; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            border: 1px solid #eee;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
        }}
        .instructions {{ 
            padding: 15px; 
            background-color: #f0f7ff; 
            border-radius: 8px; 
            margin-bottom: 20px; 
            border-left: 4px solid #3b82f6;
        }}
        .wordcloud-title {{ 
            font-size: 18px; 
            font-weight: bold; 
            margin-bottom: 15px; 
            color: #333; 
        }}
        .wordcloud-img {{ 
            max-width: 100%; 
            height: auto; 
            border-radius: 8px; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.1); 
        }}
        
        /* 响应式设计增强 */
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
            h1 {{
                font-size: 1.5rem;
                margin-bottom: 15px;
            }}
            .container {{
                padding: 15px;
            }}
            #treemap {{
                height: 400px;
            }}
            .instructions {{
                padding: 10px;
                margin-bottom: 15px;
                font-size: 0.9rem;
            }}
            .wordcloud-title {{
                font-size: 16px;
            }}
        }}
        
        @media (max-width: 480px) {{
            body {{
                padding: 5px;
            }}
            h1 {{
                font-size: 1.2rem;
            }}
            .container {{
                padding: 10px;
            }}
            #treemap {{
                height: 300px;
            }}
            .instructions {{
                padding: 8px;
                font-size: 0.85rem;
            }}
            #wordcloud-container {{
                min-height: 300px;
                padding: 10px;
            }}
            .wordcloud-title {{
                font-size: 14px;
                margin-bottom: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{brand_name} 国家分布分析</h1>
        
        <div class="instructions">
            <p>点击下方矩形树图中的国家区块，可查看该国家评论的词云图。颜色越绿表示平均评分越高，颜色越红表示平均评分越低。</p>
        </div>
        
        <div id="treemap"></div>
        
        <div id="wordcloud-container">
            <div class="wordcloud-title">点击上方国家区块查看对应词云</div>
        </div>
    </div>

    <script>
        // 国家数据
        const countryData = {json.dumps([{"country": row["Country"], "count": int(row["Count"]), "avg_rating": float(row["Avg_Rating"])} for _, row in country_stats.iterrows()])};
        
        // 词云数据
        const wordclouds = {json.dumps(country_wordclouds)};
        
        // 创建Treemap
        const data = [{{
            type: "treemap",
            labels: countryData.map(item => item.country),
            parents: Array(countryData.length).fill(""),
            values: countryData.map(item => item.count),
            text: countryData.map(item => `平均评分: ${{item.avg_rating.toFixed(1)}}/5<br>评论数: ${{item.count}}`),
            hovertemplate: '<b>%{{label}}</b><br>评论数: %{{value}}<br>%{{text}}<extra></extra>',
            textinfo: "label+text",
            marker: {{
                colors: countryData.map(item => {{
                    // 根据评分设置颜色，1分最红，5分最绿
                    const rating = item.avg_rating;
                    if (rating <= 2) return '#ff5f5f';
                    else if (rating <= 3) return '#ffcc5f';
                    else if (rating <= 4) return '#b3e0a0';
                    else return '#5fd35f';
                }}),
                line: {{
                    width: 1,
                    color: 'white'
                }}
            }}
        }}];
        
        const layout = {{
            margin: {{l: 0, r: 0, b: 0, t: 0}},
            autosize: true
        }};
        
        Plotly.newPlot('treemap', data, layout);
        
        // 点击事件处理
        document.getElementById('treemap').on('plotly_click', function(data) {{
            const country = data.points[0].label;
            const wordcloudData = wordclouds[country];
            
            if (wordcloudData) {{
                document.getElementById('wordcloud-container').innerHTML = `
                    <div class="wordcloud-title">${{country}} 评论词云</div>
                    <img src="data:image/png;base64,${{wordcloudData}}" alt="${{country}} 词云" class="wordcloud-img">
                `;
            }} else {{
                document.getElementById('wordcloud-container').innerHTML = `
                    <div class="wordcloud-title">${{country}} 没有足够的评论生成词云</div>
                `;
            }}
        }});
    </script>
</body>
</html>
"""
    
    # 保存HTML文件
    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Saved country treemap to {save_path}")
    except Exception as e:
        print(f"Error saving treemap: {e}")
    
    # 保存国家统计数据
    stats_file = save_path.replace('.html', '_stats.csv')
    country_stats.to_csv(stats_file, index=False)
    print(f"Saved country statistics to {stats_file}")
    
    return True

# 此函数已在文件前部分定义，这里注释掉重复定义
# def create_rating_pie_chart(df, brand_name, save_path):
#     """创建评分分布饼图"""
#     # 此函数已在文件前部分实现，这里避免重复定义

def analyze_combined_trends(df, brand_name, save_path):
    """分析评分、情感和评论数量的时间趋势"""
    date_col = next((col for col in df.columns if col.lower() == 'date'), None)
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    sentiment_col = 'sentiment' if 'sentiment' in df.columns else None
    
    if date_col is None or rating_col is None or df.empty:
        print("Missing required columns for combined trends analysis")
        return
    
    # 确保日期列是日期类型
    df['date'] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=['date'])
    if df.empty:
        print("No valid date data available")
        return
    
    # 确保评分列是数值类型
    df[rating_col] = pd.to_numeric(df[rating_col], errors='coerce')
    
    # 按月份分组
    df['month'] = df['date'].dt.to_period('M')
    monthly_data = df.groupby('month').agg({
        rating_col: 'mean',
        'date': 'count'
    })
    monthly_data.columns = ['avg_rating', 'review_count']
    
    # 如果有情感数据，也计算平均情感
    if sentiment_col:
        sentiment_data = df.groupby('month')[sentiment_col].mean()
        monthly_data['avg_sentiment'] = sentiment_data
    
    # 创建多轴图表
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    # 绘制评论数量柱状图
    ax1.bar(range(len(monthly_data)), monthly_data['review_count'], alpha=0.3, color='gray', label='Review Count')
    ax1.set_ylabel('Review Count', fontsize=12)
    ax1.set_xlabel('')
    
    # 创建第二个Y轴
    ax2 = ax1.twinx()
    
    # 绘制平均评分折线图
    line1 = ax2.plot(range(len(monthly_data)), monthly_data['avg_rating'], 'o-', color='blue', linewidth=2, label='Avg Rating')
    
    # 如果有情感数据，绘制平均情感折线图
    if 'avg_sentiment' in monthly_data.columns:
        line2 = ax2.plot(range(len(monthly_data)), monthly_data['avg_sentiment'], 's-', color='green', linewidth=2, label='Avg Sentiment')
        lines = line1 + line2
    else:
        lines = line1
    
    ax2.set_ylabel('Rating / Sentiment', fontsize=12)
    ax2.set_ylim(-1, 5.5)
    
    # 设置X轴标签为月份
    plt.xticks(range(len(monthly_data)), [str(period) for period in monthly_data.index], rotation=45)
    
    # 添加图例
    labels = [l.get_label() for l in lines]
    ax2.legend(lines, labels, loc='upper left')
    
    # 添加评论数量图例
    handles, labels = ax1.get_legend_handles_labels()
    ax2.legend(handles + lines, labels + [l.get_label() for l in lines], loc='upper left')
    
    plt.title(f'{brand_name} - Combined Trends Analysis', fontsize=16)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    try:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved combined trends analysis to {save_path}")
    except Exception as e:
        print(f"Error saving combined trends analysis: {e}")
    plt.close()
    
    # 保存趋势数据
    trends_file = save_path.replace('.jpg', '_data.csv').replace('.png', '_data.csv')
    monthly_data.to_csv(trends_file)
    print(f"Saved combined trends data to {trends_file}")

def generate_word_cloud(df, brand_name, save_path):
    """生成评论词云图"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    if review_col is None or df.empty:
        print("No review data available for word cloud")
        return
    
    # 合并所有评论文本
    all_text = ' '.join(df[review_col].dropna().astype(str))
    
    # 设置停用词 - 增强版
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
    
    # 创建词云对象
    wordcloud = WordCloud(
        width=1200,
        height=800,
        background_color='white',
        stopwords=stopwords,
        max_words=200,
        max_font_size=150,
        random_state=42,
        collocations=False,
        font_path='simhei.ttf'  # 添加中文字体支持
    ).generate(all_text)
    
    # 创建图形
    plt.figure(figsize=(15, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'{brand_name} Review Word Cloud', fontsize=16, pad=20)
    
    try:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved word cloud to {save_path}")
    except Exception as e:
        print(f"Error saving word cloud: {e}")
    plt.close()
    
    # 保存词频数据
    words = all_text.lower().split()
    word_freq = pd.Series(words).value_counts().head(100)
    freq_file = save_path.replace('.png', '_frequencies.csv')
    word_freq.to_csv(freq_file)
    print(f"Saved word frequencies to {freq_file}")

def generate_rating_word_clouds(df, brand_name, save_dir):
    """按评分分类生成词云图"""
    review_col = next((col for col in df.columns if col.lower() == 'review'), None)
    rating_col = next((col for col in df.columns if col.lower() == 'rating'), None)
    
    if review_col is None or rating_col is None or df.empty:
        print("Missing required columns for rating word clouds")
        return
        
    # 确保品牌名安全可用作文件名
    safe_brand_name = brand_name.split('?')[0]  # 移除问号及其后面的内容
    safe_brand_name = ''.join(c for c in safe_brand_name if c.isalnum() or c in '_-.')  # 只保留字母、数字和特定字符
        
    # 确保评分列为数值型
    df[rating_col] = pd.to_numeric(df[rating_col], errors='coerce')
    
    # 创建评分分布表格
    rating_counts = df[rating_col].value_counts().sort_index()
    rating_percentages = (rating_counts / rating_counts.sum() * 100).round(1)
    
    # 保存评分分布数据
    rating_stats = pd.DataFrame({
        'Count': rating_counts,
        'Percentage': rating_percentages
    })
    stats_file = os.path.join(save_dir, f"{safe_brand_name}_rating_stats.csv")
    rating_stats.to_csv(stats_file)
    print(f"Saved rating statistics to {stats_file}")
    
    # 创建评分分布柱状图
    plt.figure(figsize=(12, 6))
    bars = plt.bar(rating_counts.index, rating_counts.values, color=['#FF4136', '#FF851B', '#FFDC00', '#2ECC40', '#0074D9'][:len(rating_counts)])
    
    # 添加数据标签
    for i, bar in enumerate(bars):
        height = bar.get_height()
        # 使用索引位置而不是x坐标值来访问rating_percentages
        rating_value = rating_counts.index[i]
        percentage = rating_percentages.get(rating_value, 0)
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}\n({percentage:.1f}%)',
                ha='center', va='bottom', fontsize=10)
    
    plt.title(f'{brand_name} 评分分布', fontsize=16)
    plt.xlabel('评分', fontsize=12)
    plt.ylabel('评论数量', fontsize=12)
    plt.xticks(rating_counts.index)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    bar_chart_path = os.path.join(save_dir, f"{safe_brand_name}_rating_bar.png")
    plt.savefig(bar_chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved rating bar chart to {bar_chart_path}")
    
    # 确保评分列是数值类型
    df[rating_col] = pd.to_numeric(df[rating_col], errors='coerce')
    
    # 设置停用词
    stopwords = set(STOPWORDS)
    custom_stopwords = {
        'the', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'with', 'for', 'on', 'is', 'was', 'be',
        'this', 'have', 'from', 'or', 'had', 'by', 'but', 'not', 'what', 'all', 'were', 'when',
        'we', 'there', 'can', 'an', 'your', 'which', 'their', 'said', 'if', 'will', 'my', 'one',
        brand_name.lower(), 'product', 'products', 'company', 'service', 'order', 'ordered',
        'received', 'bought', 'purchase', 'purchased', 'buy', 'use', 'used', 'using'
    }
    stopwords.update(custom_stopwords)
    
    # 按评分分组
    for rating in sorted(df[rating_col].unique()):
        if pd.isna(rating):
            continue
            
        rating_df = df[df[rating_col] == rating]
        if len(rating_df) < 5:  # 如果评论数量太少，跳过
            print(f"Skipping rating {rating} word cloud due to insufficient data")
            continue
            
        # 合并该评分的所有评论
        rating_text = ' '.join(rating_df[review_col].dropna().astype(str))
        if not rating_text.strip():
            continue
            
        # 创建词云
        wordcloud = WordCloud(
            width=1000,
            height=600,
            background_color='white',
            stopwords=stopwords,
            max_words=150,
            max_font_size=120,
            random_state=42,
            collocations=False,
            font_path='simhei.ttf'  # 添加中文字体支持
        ).generate(rating_text)
        
        # 设置颜色映射
        colors = {
            1: 'Reds',
            2: 'Oranges',
            3: 'YlOrBr',
            4: 'GnBu',
            5: 'Greens'
        }
        color_map = colors.get(int(rating), 'viridis')
        
        # 创建图形
        plt.figure(figsize=(12, 8))
        plt.imshow(wordcloud.recolor(colormap=color_map), interpolation='bilinear')
        plt.axis('off')
        plt.title(f'{brand_name} - {int(rating)} Star Reviews Word Cloud', fontsize=16, pad=20)
        
        # 保存词云图
        save_path = os.path.join(save_dir, f"{safe_brand_name}_rating_{int(rating)}_word_cloud.png")
        try:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Saved {int(rating)}-star word cloud to {save_path}")
        except Exception as e:
            print(f"Error saving {int(rating)}-star word cloud: {e}")
        plt.close()
        
        # 保存词频数据
        words = rating_text.lower().split()
        word_freq = pd.Series(words).value_counts().head(100)
        freq_file = save_path.replace('.png', '_frequencies.csv')
        word_freq.to_csv(freq_file)
        print(f"Saved {int(rating)}-star word frequencies to {freq_file}")