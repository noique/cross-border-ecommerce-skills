# ai_analysis_topic.py
import os
import pandas as pd
import numpy as np
from ai_analysis import call_ai_model

def analyze_topic_model(topic_dir, brand_name):
    """分析主题模型结果"""
    # 尝试读取主题模型数据文件
    topic_sentiment_file = os.path.join(topic_dir, f"{brand_name}_topic_sentiment_data.csv")
    if not os.path.exists(topic_sentiment_file):
        print(f"Topic sentiment data file not found: {topic_sentiment_file}")
        # 尝试查找其他可能的文件名
        possible_files = [f for f in os.listdir(topic_dir) if f.endswith('.csv') and 'topic' in f.lower()]
        if possible_files:
            topic_sentiment_file = os.path.join(topic_dir, possible_files[0])
            print(f"Using alternative topic file: {topic_sentiment_file}")
        else:
            print(f"没有找到任何主题相关的CSV文件在 {topic_dir} 目录中")
            return None
    
    try:
        # 读取主题数据
        print(f"正在读取主题数据文件: {topic_sentiment_file}")
        topic_df = pd.read_csv(topic_sentiment_file)
        print(f"成功读取主题数据，共 {len(topic_df)} 行")
        
        # 检查列名并尝试映射到标准列名
        columns = topic_df.columns.tolist()
        print(f"Found columns in topic file: {columns}")
        
        # 尝试映射列名
        topic_col = None
        word_col = None
        sentiment_col = None
        
        # 查找Topic列
        for col in columns:
            if col.lower() == 'topic' or 'topic' in col.lower() or 'dominant_topic' in col.lower():
                topic_col = col
                print(f"找到主题列: {topic_col}")
                break
        
        # 查找Word列或类似列
        for col in columns:
            if col.lower() == 'word' or 'term' in col.lower() or 'keyword' in col.lower() or 'token' in col.lower():
                word_col = col
                print(f"找到关键词列: {word_col}")
                break
        
        # 如果没有找到Word列，但有Country列，可能是country_topic文件
        if not word_col and any('country' in col.lower() for col in columns):
            # 使用Country列作为Word列
            for col in columns:
                if 'country' in col.lower():
                    word_col = col
                    break
            print(f"Using '{word_col}' column as keywords")
        
        # 查找情感列
        for col in columns:
            if 'sentiment' in col.lower() or 'polarity' in col.lower() or 'score' in col.lower():
                sentiment_col = col
                print(f"找到情感列: {sentiment_col}")
                break
        
        if not topic_col:
            print("No topic column found in data")
            # 如果没有Topic列，但有其他可用列，创建一个虚拟Topic列
            if word_col:
                topic_df['Topic'] = 0  # 所有行都属于同一个主题
                topic_col = 'Topic'
                print("Created a default Topic column")
            else:
                print("无法找到或创建主题列，无法继续分析")
                return None
        
        if not word_col:
            print("No word/keyword column found in data")
            # 尝试使用其他列作为关键词列
            if len(columns) > 1:
                for col in columns:
                    if col != topic_col and col != sentiment_col:
                        word_col = col
                        print(f"使用 {word_col} 列作为关键词列")
                        break
            
            if not word_col:
                print("无法找到或创建关键词列，无法继续分析")
                return None
        
        # 提取每个主题的关键词和情感倾向
        topics_info = []
        unique_topics = sorted(topic_df[topic_col].unique())
        print(f"发现 {len(unique_topics)} 个不同的主题: {unique_topics}")
        
        for topic_id in unique_topics:
            topic_data = topic_df[topic_df[topic_col] == topic_id]
            print(f"处理主题 {topic_id}, 包含 {len(topic_data)} 行数据")
            
            # 获取关键词
            try:
                keywords = topic_data[word_col].tolist()[:10]  # 取前10个关键词
                print(f"主题 {topic_id} 的关键词: {keywords[:3]}...等")
            except Exception as e:
                print(f"提取主题 {topic_id} 的关键词时出错: {e}")
                keywords = [f"Keyword_{i}" for i in range(5)]  # 创建默认关键词
            
            # 计算情感得分
            avg_sentiment = 0
            try:
                if sentiment_col:
                    avg_sentiment = topic_data[sentiment_col].mean()
                    print(f"主题 {topic_id} 的平均情感得分: {avg_sentiment:.3f}")
            except Exception as e:
                print(f"计算主题 {topic_id} 的情感得分时出错: {e}")
            
            sentiment_category = 'Positive' if avg_sentiment > 0.1 else 'Negative' if avg_sentiment < -0.1 else 'Neutral'
            
            topics_info.append({
                'topic_id': topic_id,
                'keywords': keywords,
                'avg_sentiment': avg_sentiment,
                'sentiment_category': sentiment_category
            })
        
        # 按情感倾向排序
        positive_topics = [t for t in topics_info if t['sentiment_category'] == 'Positive']
        negative_topics = [t for t in topics_info if t['sentiment_category'] == 'Negative']
        neutral_topics = [t for t in topics_info if t['sentiment_category'] == 'Neutral']
        
        print(f"正面情感主题: {len(positive_topics)}个")
        print(f"中性情感主题: {len(neutral_topics)}个")
        print(f"负面情感主题: {len(negative_topics)}个")
        
        # 生成更详细的提示
        prompt = f"""分析以下{brand_name}的主题模型分析结果：

主题模型已经从用户评论中提取了{len(topics_info)}个主要主题，每个主题的关键词和情感倾向如下：

"""
        
        for i, topic in enumerate(topics_info):
            prompt += f"主题{topic['topic_id']}：\n"
            prompt += f"关键词：{', '.join(str(k) for k in topic['keywords'])}\n"
            prompt += f"情感倾向：{topic['sentiment_category']} (情感得分: {topic['avg_sentiment']:.3f})\n\n"
        
        prompt += f"""正面情感主题数量：{len(positive_topics)}个
中性情感主题数量：{len(neutral_topics)}个
负面情感主题数量：{len(negative_topics)}个

请深入分析这些主题，提供以下内容：

1. 品牌核心优势分析
   - 基于正面情感主题，识别品牌的3-5个核心优势
   - 每个优势的具体表现和影响
   - 这些优势如何为品牌创造竞争力
   - 如何进一步强化这些优势

2. 品牌主要问题分析
   - 基于负面情感主题，识别品牌的3-5个主要问题
   - 每个问题的具体表现和影响
   - 这些问题如何影响用户体验和品牌声誉
   - 问题的严重程度和优先级排序

3. 具体可行的改进建议
   - 针对每个主要问题提出具体的改进措施
   - 建议的实施优先级和预期效果
   - 短期可立即实施的改进措施
   - 长期需要战略性调整的改进方向

4. 市场机会和发展方向
   - 基于主题分析的潜在市场机会
   - 品牌可以拓展的新领域或新市场
   - 与竞争对手差异化的关键点

请用简洁专业的语言输出分析结果，确保分析具有可操作性和实用价值，能够直接指导品牌改进和发展策略。"""
        
        # 调用AI模型获取分析结果
        print("开始生成主题模型详细分析结果...")
        print(f"提示词长度: {len(prompt)} 字符")
        analysis_result = call_ai_model(prompt)
        
        if analysis_result:
            print(f"成功获取AI分析结果，长度: {len(analysis_result)} 字符")
            # 保存分析结果
            analysis_file = os.path.join(topic_dir, f"{brand_name}_topic_analysis.txt")
            with open(analysis_file, 'w', encoding='utf-8') as f:
                f.write(analysis_result)
            print(f"保存主题分析结论到{analysis_file}")
            return analysis_result
        else:
            print("主题分析生成失败，AI模型未返回结果")
            return None
    except Exception as e:
        print(f"Error analyzing topic model: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # 可以直接运行此脚本来生成主题分析
    import sys
    if len(sys.argv) > 2:
        run_dir = sys.argv[1]
        brand_name = sys.argv[2]
        topic_dir = os.path.join(run_dir, "analysis_results", "topic_analysis")
        if os.path.exists(topic_dir):
            analyze_topic_model(topic_dir, brand_name)
        else:
            print(f"Topic directory not found: {topic_dir}")
    else:
        print("Usage: python ai_analysis_topic.py <run_dir> <brand_name>")