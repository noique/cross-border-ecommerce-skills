# Cross-Border E-Commerce AI Skills

**AI-powered skill templates for cross-border e-commerce operations.**

Compatible with Claude Code (`~/.claude/commands/`) and Google Antigravity (`SKILL.md`).

[中文说明](#中文说明) | [English](#english)

---

## English

### What is this?

A collection of AI agent skills (prompt templates) that automate key workflows in cross-border e-commerce — from product selection to market research, IP risk assessment, keyword strategy, and listing copywriting.

Each skill is a standalone `.md` file. Drop it into your AI IDE's skill directory and invoke it.

### Amazon Skills (6 skills)

| Skill | What it does |
|-------|-------------|
| [amazon-product-selection](amazon/product-selection/amazon-product-selection.md) | Scores and ranks Top 30 potential products from any data source (Jimu Data, Helium10, JungleScout, etc.) |
| [amazon-product-shortlist](amazon/product-selection/amazon-product-shortlist.md) | Deep feasibility screening: compliance, beginner-friendliness, seasonality, GTM flywheel check, Go-List with action plan |
| [amazon-market-research](amazon/market-research/amazon-market-research.md) | Full market research: 1688 sourcing data, Amazon competitive landscape, VOC matrix, competitor teardown, SWOT |
| [amazon-ip-risk-assessment](amazon/ip-risk/amazon-ip-risk-assessment.md) | Patent search (Google Patents + Espacenet), trademark risk, design comparison matrix, risk rating |
| [amazon-keyword-research](amazon/listing-optimization/amazon-keyword-research.md) | Keyword library: 3-tier CPC strategy, negative keywords, COSMO/Rufus/A10 SEO guide, Search Terms optimization |
| [amazon-listing-copywriter](amazon/listing-optimization/amazon-listing-copywriter.md) | Listing copy: title, bullet points, A+ description, Search Terms, Rufus checklist, 11-point compliance audit |

### Recommended Workflow

```
Data Source (Jimu / Helium10 / JungleScout)
    |
    v
1. /amazon-product-selection      -> Top 30 candidates
    |
    v
2. /amazon-product-shortlist      -> Go-List (5-10 products) + action plan
    |
    v  For each product:
3. /amazon-market-research        -> Deep market research report
4. /amazon-ip-risk-assessment     -> IP risk assessment
5. /amazon-keyword-research       -> Keyword library
6. /amazon-listing-copywriter     -> Listing copy (ready to publish)
```

### Key Features

- **Data Verification Layer** — Every skill includes a mandatory verification step. No fabricated data; unverifiable numbers are explicitly flagged.
- **VOC (Voice of Customer) Matrix** — Mention frequency x satisfaction matrix to identify unmet needs, not just keyword opportunities.
- **GTM Flywheel** — Product selection evaluates Market > Product > Marketing > Operations fit, not just "can it sell."
- **Brand Narrative** — Listing copy anchors into Maslow's hierarchy (safety/social/esteem/self-actualization), not just keyword stuffing.
- **AI Search Ready** — Optimized for Amazon Rufus (300M users), COSMO knowledge graph, and GEO (Generative Engine Optimization).
- **2025-2026 Compliant** — Updated title limits (125 chars for apparel), Search Terms (249 bytes), tiered referral fees, FBA 2026 fee changes.

### Installation

**Claude Code:**
```bash
cp amazon/**/*.md ~/.claude/commands/
```

**Google Antigravity:**
Copy `.md` files to your Antigravity skill directory.

**OpenClaw / 小龙虾:**
Import `.md` files as custom skills. Works with any LLM backend supported by OpenClaw.

**Any AI IDE with skill/prompt support:**
Load the `.md` files as system prompts or skill definitions.

### Minimum Model Requirements

These skills are structured prompts with complex multi-step instructions. LLM capability directly affects output quality:

| Model Tier | Expected Quality | Examples |
|-----------|-----------------|---------|
| Recommended | Full execution, data verification works | Claude Opus/Sonnet, GPT-4o, Gemini Pro |
| Usable | Structure OK, may skip verification steps | DeepSeek V3, Llama 70B+, Qwen 72B+ |
| Not recommended | Sections missing, compliance checks fail | Models under 30B parameters |

Key requirements: long context (8K+ input), strong instruction following, Chinese-English bilingual capability, tool use / web browsing (for research steps).

### Examples

See [examples/](examples/) for test reports (coming soon).

---

## 中文说明

### 这是什么？

一套跨境电商 AI 技能模板（Prompt 模板），覆盖选品→市场调研→IP风险排查→关键词→文案的全流程自动化。

每个技能是独立的 `.md` 文件，放入你的 AI IDE 技能目录即可使用。

### Amazon 技能矩阵（6 个技能）

| 技能 | 功能 |
|------|------|
| [amazon-product-selection](amazon/product-selection/amazon-product-selection.md) | 从榜单数据中筛选 Top 30 潜力产品（支持极目数据/Helium10/JungleScout 等） |
| [amazon-product-shortlist](amazon/product-selection/amazon-product-shortlist.md) | 深度可行性筛选：合规红绿灯、新手友好度、季节性匹配、GTM飞轮快检、落地行动计划 |
| [amazon-market-research](amazon/market-research/amazon-market-research.md) | 完整市场调研：1688数据提取、Amazon竞品扫描、VOC矩阵、竞品品牌拆解、SWOT分析 |
| [amazon-ip-risk-assessment](amazon/ip-risk/amazon-ip-risk-assessment.md) | IP风险排查：Google Patents+Espacenet 专利检索、商标风险、外观对比、风险评级 |
| [amazon-keyword-research](amazon/listing-optimization/amazon-keyword-research.md) | 关键词词库：3层CPC策略、否定词库、COSMO/Rufus/A10融合SEO指南、Search Terms优化 |
| [amazon-listing-copywriter](amazon/listing-optimization/amazon-listing-copywriter.md) | Listing文案：标题、五点卖点、A+描述、Search Terms、Rufus优化清单、11项合规自检 |

### 推荐流程

```
数据源（极目数据 / Helium10 / JungleScout）
    |
    v
1. /amazon-product-selection      -> Top 30 候选品
    |
    v
2. /amazon-product-shortlist      -> Go-List（5-10款）+ 行动计划
    |
    v  对每款产品执行：
3. /amazon-market-research        -> 深度调研报告
4. /amazon-ip-risk-assessment     -> IP风险排查
5. /amazon-keyword-research       -> 关键词词库
6. /amazon-listing-copywriter     -> 上架文案
```

### 核心特色

- **数据验证层** — 每个技能内置强制验证步骤，推测数据必须标注来源，不编造数字
- **VOC 用户洞察矩阵** — 提及量x满意度二维分析，找到真正未被满足的需求
- **GTM 飞轮思维** — 选品评估市场→产品→营销→运营四环可行性，不是只看"能不能卖"
- **品牌叙事驱动** — 文案锚定马斯洛需求层次，不是关键词堆砌
- **AI 搜索适配** — 针对 Amazon Rufus（3亿用户）、COSMO 知识图谱、GEO 优化
- **2025-2026 合规** — 更新了标题字符限制、Search Terms 249字节、服装类分层佣金、FBA 2026费率

### 安装方式

**Claude Code：**
```bash
cp amazon/**/*.md ~/.claude/commands/
```

**Google Antigravity：**
复制 `.md` 文件到 Antigravity 技能目录。

**OpenClaw / 小龙虾：**
导入 `.md` 文件为自定义技能，支持 OpenClaw 接入的任何 LLM 后端。

### 模型要求

这些技能是复杂的多步骤结构化 Prompt，底层 LLM 能力直接决定输出质量：

| 模型层级 | 预期效果 | 代表模型 |
|---------|---------|---------|
| 推荐 | 完整执行，数据验证步骤生效 | Claude Opus/Sonnet、GPT-4o、Gemini Pro |
| 可用 | 结构完整，可能跳过验证步骤 | DeepSeek V3、Llama 70B+、Qwen 72B+ |
| 不建议 | 章节缺失，合规检查失效 | 30B 以下参数模型 |

关键能力要求：长上下文（8K+ 输入）、强指令遵循、中英双语、联网/工具调用（调研步骤需要）。

### 示例

查看 [examples/](examples/) — 测试报告即将上传。

---

## License

Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).

You are free to use, share, and adapt these skills for any purpose, including commercial use, as long as you give credit.

## Author

Created by **Alex / 黄子阳** — [ckcm.us](https://ckcm.us)
