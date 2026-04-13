# 报告 PDF 导出 SKILL

当用户需要将 Markdown 报告导出为 PDF 时调用此技能。统一样式、横版 A4、中文字体、深蓝配色，确保跨会话样式一致。

## 执行模式：batch（对指定目录下所有 .md 文件批量转换）

## 输入要求

用户提供以下信息之一：
- **单个文件**：`/path/to/report.md`
- **整个目录**：`/path/to/reports/`（自动转换目录下所有 .md 文件）
- **默认**：如用户只说"导出 PDF"，询问文件路径

## 依赖检查

首先检查依赖是否已安装：

```bash
python3 -c "import weasyprint, markdown; print('OK')" 2>/dev/null || echo "NEED_INSTALL"
```

如需安装：
```bash
pip3 install --break-system-packages weasyprint markdown
```

## PDF 样式规范

> **以下 CSS 是固定样式标准，不可随意修改。所有报告统一使用此样式。**

### 页面设置
- 页面尺寸：**A4 横版**（`size: A4 landscape`）
- 页边距：`1.5cm 1.8cm`
- 页码：底部居中，格式 `X / Y`，8px，灰色

### 字体
- 主字体：`"PingFang SC", "Heiti SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif`
- 代码字体：`"SF Mono", "Menlo", monospace`
- 正文：10pt，行高 1.6
- 表格：8-8.5pt

### 配色方案
| 元素 | 颜色 | 色号 |
|------|------|------|
| h1 标题 | 居中，底部蓝色线 | `#2563eb` |
| h2 标题 | 蓝色文字，浅蓝底线 | `#1e40af` / `#bfdbfe` |
| h3 标题 | 深蓝文字 | `#1e3a5f` |
| 表头 | 白色文字 + 深蓝背景 | `#ffffff` on `#1e40af` |
| 表格斑马纹 | 偶数行浅灰 | `#f8fafc` |
| 引用块 | 蓝色左竖线 + 淡蓝背景 | `#2563eb` + `#f0f7ff` |
| 代码 | 玫红文字 + 浅灰背景 | `#be123c` + `#f1f5f9` |
| 链接 | 蓝色 | `#2563eb` |

### 图片
- `max-width: 65%`，居中显示，自动高度
- 上下 margin 12px

## 执行步骤

### 第一步：创建转换脚本

在 `/tmp/md2pdf.py` 创建（或验证已存在）：

```python
#!/usr/bin/env python3
"""Markdown to PDF converter with unified report styling."""
import sys, os, markdown
from weasyprint import HTML

CSS = """
@page { size: A4 landscape; margin: 1.5cm 1.8cm;
  @bottom-center { content: counter(page) " / " counter(pages); font-size: 8px; color: #999; } }
body { font-family: "PingFang SC", "Heiti SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  font-size: 10pt; line-height: 1.6; color: #1a1a1a; max-width: 100%; }
h1 { font-size: 20pt; font-weight: 600; color: #111; border-bottom: 2.5px solid #2563eb;
  padding-bottom: 8px; margin-top: 28px; margin-bottom: 16px; page-break-after: avoid; }
h2 { font-size: 15pt; font-weight: 600; color: #1e40af; border-bottom: 1.5px solid #bfdbfe;
  padding-bottom: 5px; margin-top: 24px; margin-bottom: 12px; page-break-after: avoid; }
h3 { font-size: 12.5pt; font-weight: 600; color: #1e3a5f; margin-top: 18px; margin-bottom: 8px;
  page-break-after: avoid; }
h4 { font-size: 11.5pt; font-weight: 600; color: #374151; margin-top: 14px; margin-bottom: 6px;
  page-break-after: avoid; }
p { margin: 6px 0; text-align: justify; }
strong { color: #111; }
blockquote { border-left: 3px solid #2563eb; background: #f0f7ff; padding: 8px 14px;
  margin: 10px 0; font-size: 10.5pt; color: #334155; }
blockquote p { margin: 4px 0; }
table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 8.5pt;
  line-height: 1.4; page-break-inside: auto; word-break: break-word; table-layout: auto; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
th { background: #1e40af; color: white; padding: 4px 5px; text-align: left;
  font-weight: 500; font-size: 8pt; }
td { padding: 3px 5px; border-bottom: 1px solid #e2e8f0; vertical-align: top; font-size: 8pt; }
tr:nth-child(even) td { background: #f8fafc; }
code { background: #f1f5f9; padding: 1px 4px; border-radius: 3px; font-size: 9.5pt;
  font-family: "SF Mono", "Menlo", monospace; color: #be123c; }
pre { background: #1e293b; color: #e2e8f0; padding: 12px 16px; border-radius: 6px;
  font-size: 9pt; line-height: 1.5; overflow-x: auto; margin: 10px 0; }
pre code { background: none; color: #e2e8f0; padding: 0; }
ul, ol { padding-left: 22px; margin: 6px 0; }
li { margin: 3px 0; }
hr { border: none; border-top: 1.5px solid #cbd5e1; margin: 20px 0; }
a { color: #2563eb; text-decoration: none; }
img { max-width: 65%; height: auto; display: block; margin: 12px auto; }
body > h1:first-child { font-size: 22pt; text-align: center; border-bottom: 3px solid #2563eb;
  padding-bottom: 12px; margin-bottom: 20px; }
"""

def convert_md_to_pdf(md_path, pdf_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    html_body = markdown.markdown(md_content,
        extensions=['tables', 'fenced_code', 'nl2br'], output_format='html5')
    html_doc = f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><style>{CSS}</style></head><body>{html_body}</body></html>'
    base_dir = os.path.dirname(os.path.abspath(md_path))
    base_url = 'file://' + base_dir + '/'
    HTML(string=html_doc, base_url=base_url).write_pdf(pdf_path)
    size_kb = os.path.getsize(pdf_path) / 1024
    print(f"  OK: {os.path.basename(pdf_path)} ({size_kb:.0f} KB)")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 md2pdf.py <input.md> <output.pdf>")
        sys.exit(1)
    convert_md_to_pdf(sys.argv[1], sys.argv[2])
```

### 第二步：执行转换

**单个文件：**
```bash
python3 /tmp/md2pdf.py input.md output.pdf
```

**整个目录：**
```python
import os, sys
sys.path.insert(0, '/tmp')
from md2pdf import convert_md_to_pdf

input_dir = '/path/to/reports'
output_dir = os.path.join(input_dir, 'PDF')
os.makedirs(output_dir, exist_ok=True)

for f in sorted(os.listdir(input_dir)):
    if f.endswith('.md'):
        convert_md_to_pdf(
            os.path.join(input_dir, f),
            os.path.join(output_dir, f.replace('.md', '.pdf'))
        )
```

### 第三步：验证

转换完成后：
1. 报告文件列表和大小
2. 如有图表引用（`charts/` 目录），确认图片已渲染（PDF 大小应明显大于纯文本版本）
3. 如有乱码字符，用 `grep -c '�' *.md` 检查源文件

## 已知问题与解决

| 问题 | 原因 | 解决 |
|------|------|------|
| 图片不显示 | weasyprint 用 string 模式时相对路径无效 | 脚本已用 `base_url=file://` 解决 |
| 表格溢出 | 列太多或内容太长 | 横版 A4 已大幅缓解；如仍溢出可加 `table { font-size: 7.5pt; }` |
| 中文乱码 `维���度` | 写入时 UTF-8 编码损坏 | 检查源文件 `grep -c '�' *.md`，逐一修复 |
| `/tmp/md2pdf.py` 不存在 | 跨会话 /tmp 被清空 | 本 SKILL 每次执行都会自动重建脚本 |
| weasyprint 未安装 | 新环境 | `pip3 install --break-system-packages weasyprint markdown` |

## 注意事项

- 所有报告统一使用此样式，不要自行修改 CSS
- PDF 输出到源目录下的 `PDF/` 子文件夹
- 如需竖版 A4，将 CSS 中 `size: A4 landscape` 改为 `size: A4`（不推荐，表格容易溢出）
- 脚本支持图片渲染（`charts/` 目录下的 PNG），确保图片文件存在

---

> Created by Alex / 黄子阳 — https://ckcm.us
> Open Source: https://github.com/noique/cross-border-ecommerce-skills
> Licensed under CC BY-NC 4.0
