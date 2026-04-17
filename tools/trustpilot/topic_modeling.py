# topic_modeling.py
# 临时禁用gensim导入
# import gensim
# from gensim import corpora
# from gensim.utils import simple_preprocess
from nltk.corpus import stopwords
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sentiment import analyze_sentiment
from data_processing import filter_valid_countries

def preprocess_text_for_lda(text):
    """预处理文本用于LDA"""
    # 函数被禁用，返回空列表
    print("主题模型功能已临时禁用")
    return []

def analyze_rating_topic_correlation(df, brand_name, save_path, lda_model=None, dictionary=None, corpus=None, num_topics=5):
    """分析评分与主题关联 - 临时禁用"""
    print(f"主题模型功能已临时禁用：评分-主题分析 for {brand_name}")
    return None, None, None

def analyze_country_topic_correlation(df, brand_name, save_path, lda_model=None, dictionary=None, corpus=None, num_topics=5):
    """分析国家与主题关联 - 临时禁用"""
    print(f"主题模型功能已临时禁用：国家-主题分析 for {brand_name}")
    return None, None, None

def analyze_topic_sentiment_correlation(df, brand_name, save_path, lda_model=None, dictionary=None, corpus=None, num_topics=5):
    """分析主题与情感关联 - 临时禁用"""
    print(f"主题模型功能已临时禁用：主题-情感分析 for {brand_name}")
    return None, None, None, None