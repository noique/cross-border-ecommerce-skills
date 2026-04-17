# Trustpilot VOC 深度分析 SKILL

用户需要对某品牌进行**全量评论抓取 + 情感分析 + LDA 主题建模 + AI 深度归纳**时调用此技能。调用本地爬虫工具链，图表输出使用 AntV API（统一报告风格）。

**适用场景：**
- 确定了目标竞品后的深度 VOC 挖掘
- 品牌危机诊断（Ottocast 2.0/5 要查清具体抱怨模式）
- 投资尽调 / 收购前调研
- 跨国市场对比（按国家拆分情感差异）

**如果只需要表层数据（5 分钟内），请用 `/trustpilot-voc-quick`。**

## 执行模式：batch（本地运行，耗时 15-40 分钟）

## 前置条件

### 1. 环境依赖

本 SKILL 依赖本地 Python 工具链：

```bash
# 安装依赖
pip install selenium seleniumwire webdriver-manager fake-useragent \
            pandas openpyxl numpy requests tqdm \
            scikit-learn nltk

# Chrome/Chromium 浏览器必须已安装
```

### 2. 环境变量

```bash
# AI 分析需要的 API key（OpenRouter / Claude / OpenAI 兼容）
export OPENROUTER_API_KEY="your-key-here"
# 或
export LLM_API_KEY="your-key-here"
```

### 3. 工具路径

本地脚本位置：`~/.claude/tools/trustpilot/`
- `main.py` — 主入口
- `scraper.py` — Selenium 爬虫（支持代理池）
- `sentiment.py` — 情感分析
- `topic_modeling.py` — LDA 主题建模
- `ai_analysis.py` — AI 深度归纳（需 API key）
- `visualization_antv.py` — **AntV 图表生成**（替代原 matplotlib）
- `config.py` — 代理池配置

### 4. 代理配置（如 Trustpilot 反爬）

编辑 `~/.claude/tools/trustpilot/config.py` 中的 `PROXIES` 变量：

```python
PROXIES = [
    "http://user:pass@proxy1:port",
    "socks5://user:pass@proxy2:port",
]
```

## 输入要求

**必须提供：**
- 品牌 Trustpilot URL
- 最大抓取页数（默认 50 页 ≈ 1000 条评论）

**可选提供：**
- 是否启用 AI 深度归纳（默认：是，需要 API key）
- 是否生成可视化图表（默认：是，调用 AntV API）
- 输出目录（默认 `./trustpilot_output/`）

## 执行步骤

### 第一步：调用本地爬虫

```bash
cd ~/.claude/tools/trustpilot
python3 main.py \
  --url "https://www.trustpilot.com/review/aoocci.com" \
  --max-pages 50 \
  --output-dir "~/Downloads/aoocci-trustpilot-deep/" \
  --ai-analysis yes \
  --visualizer antv   # 使用 AntV 替代 matplotlib
```

> **注意：** 如 `main.py` 不支持 `--visualizer antv` 参数，手动修改 `main.py` 顶部 import：
> 将 `from visualization import ...` 改为 `from visualization_antv import ...`

### 第二步：输出结构

爬虫完成后，输出目录结构：

```
{brand}_trustpilot_data_{timestamp}/
├── {brand}_trustpilot_reviews_all.xlsx    # 全量评论 Excel
├── {brand}_trustpilot_reviews_all.txt     # 全量评论纯文本
├── sentiment_analysis/
│   ├── {brand}_with_sentiment.csv         # 每条评论的情感标签
│   ├── {brand}_sentiment_analysis.png     # AntV 情感分布柱状图
│   ├── {brand}_rating_vs_length.png       # AntV 评分 vs 评论长度
│   └── ...
├── topic_analysis/
│   ├── {brand}_lda_topics.txt             # LDA 主题文本
│   ├── {brand}_lda_topics_data.csv        # 主题权重数据
│   └── {brand}_topic_1.png ...            # AntV 主题可视化
├── country_analysis/
│   ├── {brand}_country_bar.png            # AntV 国家柱状图
│   └── {brand}_country_treemap.png        # AntV 国家 Treemap
├── wordcloud_analysis/
│   ├── {brand}_wordcloud_positive.png     # AntV 正面词云
│   └── {brand}_wordcloud_negative.png     # AntV 负面词云
├── time_analysis/
│   └── {brand}_monthly_trend.png          # AntV 月度评分趋势
└── ai_analysis/
    ├── {brand}_complaint_topics.md        # AI 归纳的抱怨主题
    ├── {brand}_praise_topics.md           # AI 归纳的赞美主题
    └── {brand}_action_recommendations.md  # AI 给出的改进建议
```

### 第三步：结构化报告生成

读取上述输出，整合成一份 markdown 报告：

```markdown
# {品牌} — Trustpilot 深度 VOC 分析

**抓取日期：** YYYY-MM-DD
**评论总数：** N 条
**时间跨度：** YYYY-MM 至 YYYY-MM
**总评分：** X.X/5

## 一、整体情感分布
![](sentiment_analysis/{brand}_sentiment_analysis.png)

- 正面：X% (N 条)
- 中性：X% (N 条)
- 负面：X% (N 条)

## 二、星级分布
![](sentiment_analysis/{brand}_rating_pie.png)

## 三、Top 5 抱怨主题（LDA + AI 归纳）

从 N 条 1-2★ 评论中识别的主要抱怨：

1. **主题 1：[AI 命名]** — 占负面评论 X%
   - 关键词：[LDA 输出]
   - 代表评论：[真实引用]
   - 影响评估：[AI 分析]

2. **主题 2：...**

## 四、Top 5 赞美主题

从 4-5★ 评论中识别的核心优势：

1. **主题 1：[AI 命名]** — 占正面评论 X%
   - ...

## 五、国家分布
![](country_analysis/{brand}_country_bar.png)

- Top 市场：[国家列表]
- 国家间情感差异：[各国平均评分对比]

## 六、时间趋势
![](time_analysis/{brand}_monthly_trend.png)

- 整体趋势：向好/持平/恶化
- 关键拐点：[日期 + 事件推测]

## 七、AI 归纳的改进建议（来自 ai_analysis.py）

[AI 输出的可执行改进清单]

## 八、可信度声明

| 数据类型 | 样本量 | 可信度 |
|---------|--------|--------|
| 总体情感分布 | N 条 | 高 |
| LDA 主题 | 基于 N 条评论 | 中（主题建模受样本影响） |
| AI 归纳 | AI 生成 | 中（需交叉验证） |
```

### 第四步：集成到品牌战略 SKILL

如果本次调用是 `brand-market-scan` 或 `brand-deep-validation` 的一部分，将输出自动嵌入对应章节：

- `brand-market-scan` → 嵌入第零步 VOC 深度数据
- `brand-deep-validation` → 嵌入 D1（驱动力分析）的需求侧验证

## 可视化说明

**为什么用 AntV 替代 matplotlib？**

1. 风格统一：与其他报告图表一致（academy theme）
2. 无需本地中文字体配置
3. 输出的 PNG 可直接嵌入 PDF 报告（样式兼容）
4. API 稳定，不受本地 matplotlib 版本影响

**visualization_antv.py 提供的函数（与原 visualization.py 同名）：**

- `create_rating_pie_chart()` — 星级饼图
- `create_country_bar_chart()` — 国家柱状图
- `create_country_treemap()` — 国家 Treemap
- `generate_word_cloud()` — 评论词云
- `generate_rating_word_clouds()` — 正负面分开词云
- `analyze_combined_trends()` — 时间趋势折线图
- `create_sentiment_distribution()` — 情感分布柱状图
- `create_topic_bar_chart()` — LDA 主题权重条形图

## 运行时预期

| 场景 | 预计耗时 | 数据量 |
|------|---------|--------|
| 小品牌（<200 条） | 5-10 分钟 | 爬取+分析 |
| 中品牌（200-1000 条） | 15-25 分钟 | + LDA 主题建模 |
| 大品牌（>1000 条） | 30-60 分钟 | + AI 归纳（按批次调用） |

## 注意事项

- **Trustpilot 反爬：** 爬虫内置代理池 + 随机 UA + 等待间隔。如仍被限流，降低 `--max-pages` 或增加 proxy
- **AI Key：** 未设置时跳过 AI 归纳，只做情感+LDA+可视化
- **合法性：** Trustpilot 评论属于公开数据，爬取用于品牌研究属于合理使用；请勿用于恶意竞争或转售
- **结果可信度：** LDA 主题建模对语料量敏感，评论 <100 条时主题质量下降明显
- **输出集成：** 生成的 AntV PNG 图片可直接嵌入 markdown 报告，PDF 导出时用 `/report-pdf-export` 保持风格统一

## 与其他 SKILL 的关系

| SKILL | 定位 | 本 SKILL 位置 |
|-------|------|-------------|
| `/trustpilot-voc-quick` | WebFetch 表层数据（5 分钟） | 升级替换 |
| `/brand-market-scan` | 品牌战略扫描第零步 | 可选调用（当需要深度 VOC 时） |
| `/brand-deep-validation` | D1 驱动力分析 | 可选调用（验证用户痛点真实性） |
| `/brand-chart-visualize` | 报告图表可视化 | 复用 AntV API 基础设施 |
| `/amazon-market-research` | Amazon VOC | 互补——本 SKILL 做独立站，那个做 Amazon |

## 本地工具维护

脚本路径：`~/.claude/tools/trustpilot/`

| 文件 | 作用 | 是否需要改 |
|------|------|----------|
| `main.py` | 主入口（需支持 `--visualizer antv` 参数） | 首次使用需改 |
| `scraper.py` | 爬虫核心 | 免改 |
| `sentiment.py` | 情感分析 | 免改 |
| `topic_modeling.py` | LDA 主题建模 | 免改 |
| `ai_analysis.py` | AI 归纳（已改为从环境变量读 API key） | 免改 |
| `visualization_antv.py` | **AntV 图表生成（新增替代 matplotlib）** | 免改 |
| `visualization.py` | 原 matplotlib 版本（保留以备降级） | 免改 |
| `config.py` | 代理池配置 | 按需配置 |

---

> Created by Alex / 黄子阳 — https://ckcm.us
> Open Source: https://github.com/noique/cross-border-ecommerce-skills
> Licensed under CC BY-NC 4.0
