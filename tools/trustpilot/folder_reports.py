# folder_reports.py
import os
import base64
import datetime
import re

def encode_image_to_base64(image_path):
    """将图像文件转换为base64编码"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return ""

def read_analysis_text(analysis_file):
    """读取分析结果文件"""
    try:
        if os.path.exists(analysis_file):
            with open(analysis_file, 'r', encoding='utf-8') as f:
                return f.read()
        return "暂无分析结论"
    except Exception as e:
        print(f"Error reading analysis file {analysis_file}: {e}")
        return "读取分析结论出错"

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

def generate_folder_report(folder_path, brand_name, folder_type):
    """为单个分析文件夹生成小型HTML报告"""
    try:
        if not os.path.exists(folder_path):
            print(f"Folder not found: {folder_path}")
            return None
            
        # 获取文件夹中的所有图片和分析文件
        image_files = []
        analysis_file = None
        
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if file.endswith(".png") or file.endswith(".jpg"):
                image_files.append(file_path)
            elif file.endswith(".txt") and brand_name in file:
                analysis_file = file_path
                
        if not image_files:
            print(f"No images found in {folder_path}")
            return None
            
        # 获取文件夹类型的中文名称
        folder_type_names = {
            "rating_analysis": "评分分析",
            "country_analysis": "国家分布分析",
            "sentiment_analysis": "情感分析",
            "word_analysis": "词云分析",
            "time_analysis": "时间趋势分析",
            "topic_analysis": "主题分析"
        }
        
        folder_title = folder_type_names.get(folder_type, folder_type)
        
        # 读取分析结论
        analysis_text = ""
        if analysis_file:
            analysis_text = read_analysis_text(analysis_file)
            analysis_text = markdown_to_html(analysis_text)
        
        # 编码图片
        image_html = ""
        for img_path in image_files:
            img_name = os.path.basename(img_path)
            img_base64 = encode_image_to_base64(img_path)
            if img_base64:
                image_html += f"""
                <div class="image-container mb-4">
                    <h3 class="text-lg font-semibold mb-2">{img_name}</h3>
                    <img src="data:image/png;base64,{img_base64}" alt="{img_name}" class="max-w-full h-auto rounded shadow">
                </div>
                """
        
        # 生成HTML内容
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{brand_name} {folder_title} 报告</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
            <style>
                /* 响应式设计增强 */
                @media (max-width: 768px) {{
                    .container {{ padding: 12px; }}
                    h1 {{ font-size: 1.5rem; }}
                    h2 {{ font-size: 1.25rem; }}
                    .p-6 {{ padding: 1rem; }}
                    .mb-6 {{ margin-bottom: 1rem; }}
                    .mb-4 {{ margin-bottom: 0.75rem; }}
                }}
                
                @media (max-width: 640px) {{
                    .container {{ padding: 8px; }}
                    h1 {{ font-size: 1.25rem; }}
                    h2 {{ font-size: 1.1rem; }}
                    .p-6 {{ padding: 0.75rem; }}
                }}
                
                /* 图片响应式 */
                .image-container img {{
                    max-width: 100%;
                    height: auto;
                    display: block;
                    margin: 0 auto;
                }}
                
                /* 文本响应式 */
                .text-gray-700 {{
                    word-break: break-word;
                }}
            </style>
        </head>
        <body class="bg-gray-50">
            <div class="container mx-auto px-4 py-8 max-w-4xl">
                <header class="mb-6 text-center">
                    <h1 class="text-2xl font-bold text-gray-800 mb-2">{brand_name} {folder_title} 报告</h1>
                    <p class="text-gray-600">生成时间: {current_time}</p>
                </header>
                
                <div class="bg-white rounded-lg shadow p-6 mb-6">
                    <h2 class="text-xl font-bold mb-4 text-gray-800">分析结论</h2>
                    <div class="text-gray-700 whitespace-pre-line">{analysis_text}</div>
                </div>
                
                <div class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-xl font-bold mb-4 text-gray-800">图表与可视化</h2>
                    {image_html}
                </div>
            </div>
        </body>
        </html>
        """
        
        # 保存HTML报告
        report_file = os.path.join(folder_path, f"{brand_name}_{folder_type}_report.html")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"生成{folder_title}小型HTML报告: {report_file}")
        return report_file
    except Exception as e:
        print(f"Error generating folder report: {e}")
        return None

def generate_all_folder_reports(run_dir, brand_name):
    """为所有分析文件夹生成小型HTML报告"""
    try:
        # 定位分析结果目录
        analysis_dir = os.path.join(run_dir, "analysis_results")
        if not os.path.exists(analysis_dir):
            print(f"Analysis directory not found: {analysis_dir}")
            return []
            
        # 各分析子目录
        folder_types = [
            "rating_analysis",
            "country_analysis",
            "sentiment_analysis",
            "word_analysis",
            "time_analysis",
            "topic_analysis"
        ]
        
        reports = []
        for folder_type in folder_types:
            folder_path = os.path.join(analysis_dir, folder_type)
            if os.path.exists(folder_path):
                report_file = generate_folder_report(folder_path, brand_name, folder_type)
                if report_file:
                    reports.append(report_file)
        
        return reports
    except Exception as e:
        print(f"Error generating all folder reports: {e}")
        return []