# Cross-Border E-Commerce AI Skills

**AI-powered skill templates for cross-border e-commerce operations.**

Compatible with Claude Code (`~/.claude/commands/`) and Google Antigravity (`SKILL.md`).

[中文说明](#中文说明) | [English](#english)

---

## English

### What is this?

A collection of AI agent skills (prompt templates) that automate key workflows in cross-border e-commerce — from product selection to market research, IP risk assessment, keyword strategy, and listing copywriting.

Each skill is a standalone `.md` file. Drop it into your AI IDE's skill directory and invoke it.

### Brand Strategy Skills (6 skills) — NEW

**4-Round Brand Analysis Pipeline + IMC + Knowledge Base**
| Skill | What it does |
|-------|-------------|
| [brand-market-scan](brand-strategy/brand-market-scan.md) | Round 1: Market panoramic scan — 4-layer user insight, VOC matrix, competitive landscape |
| [brand-track-hypothesis](brand-strategy/brand-track-hypothesis.md) | Round 2: Track hypothesis generation — 3-5 market tracks, DTNICE classification, GTM flywheel |
| [brand-deep-validation](brand-strategy/brand-deep-validation.md) | Round 3: Deep hypothesis validation — 5D framework, benchmark case studies, Zone 4 positioning |
| [brand-strategy-plan](brand-strategy/brand-strategy-plan.md) | Round 4: Brand strategy & execution — 7-element positioning, 4 pillars, pricing, narrative, roadmap |
| [brand-imc-framework](brand-strategy/brand-imc-framework.md) | IMC integrated marketing framework — Audience/User dual-path, 6-stage funnel, channel mix, calendar |
| [brand-knowledge-base](brand-strategy/brand-knowledge-base.md) | Obsidian knowledge base generator — batch-creates 30-50 interlinked .md files |

### Amazon Skills (14 skills)

**Phase 1: Product Selection**
| Skill | What it does |
|-------|-------------|
| [amazon-product-selection](amazon/product-selection/amazon-product-selection.md) | Scores and ranks Top 30 potential products from any data source |
| [amazon-product-shortlist](amazon/product-selection/amazon-product-shortlist.md) | Feasibility screening: compliance, GTM flywheel check, Go-List |

**Phase 2: Research & Risk**
| Skill | What it does |
|-------|-------------|
| [amazon-market-research](amazon/market-research/amazon-market-research.md) | Full market research: VOC matrix, competitor teardown, SWOT |
| [amazon-ip-risk-assessment](amazon/ip-risk/amazon-ip-risk-assessment.md) | Patent + trademark risk, design comparison, risk rating |
| [amazon-supplier-decision](amazon/supplier/amazon-supplier-decision.md) | 1688/Alibaba supplier evaluation, cost breakdown, red flag detection |

**Phase 3: Listing Creation**
| Skill | What it does |
|-------|-------------|
| [amazon-keyword-research](amazon/listing-optimization/amazon-keyword-research.md) | Keyword library: 3-tier CPC, COSMO/Rufus/A10 SEO guide |
| [amazon-listing-copywriter](amazon/listing-optimization/amazon-listing-copywriter.md) | Title, bullet points, A+ description, Search Terms |
| [amazon-main-image-prompt](amazon/image-design/amazon-main-image-prompt.md) | Main + secondary image design briefs and AI prompts |
| [amazon-aplus-image-prompt](amazon/image-design/amazon-aplus-image-prompt.md) | A+ Content module layout, Brand Story, image prompts |

**Phase 4: Compliance & Launch**
| Skill | What it does |
|-------|-------------|
| [amazon-compliance-review](amazon/compliance-launch/amazon-compliance-review.md) | 3-dimension parallel audit: platform rules, legal/IP, AI search |
| [amazon-pre-launch-review](amazon/compliance-launch/amazon-pre-launch-review.md) | Final pre-launch checklist across all previous SKILL outputs |

**Phase 5: Advertising & Operations**
| Skill | What it does |
|-------|-------------|
| [amazon-ad-architecture](amazon/advertising/amazon-ad-architecture.md) | PPC campaign structure: SP/SB/SD/SBV, budget allocation, bid strategy |
| [amazon-weekly-ad-review](amazon/advertising/amazon-weekly-ad-review.md) | Weekly ad performance review, Search Term analysis, action list |
| [amazon-ad-diagnosis](amazon/advertising/amazon-ad-diagnosis.md) | **Existing product** ad diagnosis: competitive scan → keyword rebuild → copy fix → ad optimization |

### Recommended Workflow

**Brand Strategy → Amazon Execution (full pipeline):**
```
Brand / Product Info
    |
    v  Brand Strategy (4-round pipeline):
1.  /brand-market-scan             -> Market scan + VOC + competitive landscape
2.  /brand-track-hypothesis        -> 3-5 track hypotheses + top 2 selection
3.  /brand-deep-validation         -> 5D validation + benchmark cases + Zone 4
4.  /brand-strategy-plan           -> Brand positioning + 4 pillars + roadmap
5.  /brand-imc-framework           -> Marketing framework + channel mix + calendar
6.  /brand-knowledge-base          -> Obsidian knowledge base (30-50 files)
     |
     v  Then execute with Amazon Skills:
```

**Amazon Execution (product-level):**
```
Data Source (Jimu / Helium10 / JungleScout)
    |
    v
1.  /amazon-product-selection      -> Top 30 candidates
     |
2.  /amazon-product-shortlist      -> Go-List + action plan
     |
     v  For each product:
3.  /amazon-market-research        -> Market research report
4.  /amazon-ip-risk-assessment     -> IP risk report
5.  /amazon-supplier-decision      -> Supplier decision doc
6.  /amazon-keyword-research       -> Keyword library
7.  /amazon-listing-copywriter     -> Listing copy
8.  /amazon-main-image-prompt      -> Product image briefs
9.  /amazon-aplus-image-prompt     -> A+ content design
10. /amazon-compliance-review      -> 3-dimension compliance audit
11. /amazon-pre-launch-review      -> Final pre-launch checklist
     |
     v  After launch:
12. /amazon-ad-architecture        -> PPC campaign setup
13. /amazon-weekly-ad-review       -> Weekly optimization (recurring)

     For existing products needing optimization:
14. /amazon-ad-diagnosis           -> Full diagnosis + optimization (4-stage pipeline)
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

| Model Tier | Expected Quality | Examples (as of April 2026) |
|-----------|-----------------|---------|
| Recommended | Full execution, data verification works | Claude Opus 4.6 / Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro |
| Usable | Structure OK, may skip verification steps | DeepSeek V4 / V3.2, Llama 4, Qwen 3.5 (72B+), GLM-5.1 |
| Not recommended | Sections missing, compliance checks fail | Qwen 3.5 9B and below, any model under 30B parameters |

Key requirements: long context (8K+ input), strong instruction following, Chinese-English bilingual capability, tool use / web browsing (for research steps).

### Examples

See [examples/](examples/) for test reports (coming soon).

---

## 中文说明

### 这是什么？

一套跨境电商 AI 技能模板（Prompt 模板），覆盖选品→市场调研→IP风险排查→关键词→文案的全流程自动化。

每个技能是独立的 `.md` 文件，放入你的 AI IDE 技能目录即可使用。

### 品牌出海战略技能（6 个技能）— 新增

**四轮品牌分析 + IMC 整合营销 + 知识库生成**
| 技能 | 功能 |
|------|------|
| [brand-market-scan](brand-strategy/brand-market-scan.md) | 第一轮：市场全景扫描 — 四层用户洞察、VOC矩阵、竞争格局 |
| [brand-track-hypothesis](brand-strategy/brand-track-hypothesis.md) | 第二轮：赛道假设生成 — 3-5个赛道假设、DTNICE分类、GTM飞轮 |
| [brand-deep-validation](brand-strategy/brand-deep-validation.md) | 第三轮：假设深度验证 — 5D评估框架、对标案例拆解、第4区间定位 |
| [brand-strategy-plan](brand-strategy/brand-strategy-plan.md) | 第四轮：品牌战略与执行 — 定位七要素、四大支柱、定价、叙事、路线图 |
| [brand-imc-framework](brand-strategy/brand-imc-framework.md) | IMC整合营销框架 — Audience/User双路径、6阶段漏斗、渠道预算、执行日历 |
| [brand-knowledge-base](brand-strategy/brand-knowledge-base.md) | Obsidian知识库生成 — 批量创建30-50个互联.md文件 |

### Amazon 技能矩阵（14 个技能）

**阶段一：选品**
| 技能 | 功能 |
|------|------|
| [amazon-product-selection](amazon/product-selection/amazon-product-selection.md) | 从榜单筛选 Top 30 潜力产品 |
| [amazon-product-shortlist](amazon/product-selection/amazon-product-shortlist.md) | 可行性筛选：合规红绿灯、GTM飞轮、落地行动计划 |

**阶段二：调研与风险**
| 技能 | 功能 |
|------|------|
| [amazon-market-research](amazon/market-research/amazon-market-research.md) | 市场调研：VOC矩阵、竞品拆解、SWOT |
| [amazon-ip-risk-assessment](amazon/ip-risk/amazon-ip-risk-assessment.md) | IP风险：专利+商标检索、外观对比、风险评级 |
| [amazon-supplier-decision](amazon/supplier/amazon-supplier-decision.md) | 供应商决策：1688比价、成本拆解、红旗检测 |

**阶段三：Listing 创建**
| 技能 | 功能 |
|------|------|
| [amazon-keyword-research](amazon/listing-optimization/amazon-keyword-research.md) | 关键词词库：3层CPC、COSMO/Rufus/A10 SEO |
| [amazon-listing-copywriter](amazon/listing-optimization/amazon-listing-copywriter.md) | 标题、卖点、A+描述、Search Terms |
| [amazon-main-image-prompt](amazon/image-design/amazon-main-image-prompt.md) | 主副图设计方案 + AI图片生成提示词 |
| [amazon-aplus-image-prompt](amazon/image-design/amazon-aplus-image-prompt.md) | A+ Content 模块排布 + Brand Story + 图片提示词 |

**阶段四：合规与上架**
| 技能 | 功能 |
|------|------|
| [amazon-compliance-review](amazon/compliance-launch/amazon-compliance-review.md) | 三维度并行审查：平台规则/法律IP/AI搜索 |
| [amazon-pre-launch-review](amazon/compliance-launch/amazon-pre-launch-review.md) | 上架前总复查：所有前置 SKILL 输出一次性检查 |

**阶段五：广告与运营**
| 技能 | 功能 |
|------|------|
| [amazon-ad-architecture](amazon/advertising/amazon-ad-architecture.md) | PPC广告架构：SP/SB/SD/SBV Campaign 设计 |
| [amazon-weekly-ad-review](amazon/advertising/amazon-weekly-ad-review.md) | 每周广告复查：ACoS/TACoS分析、出价调整、行动清单 |
| [amazon-ad-diagnosis](amazon/advertising/amazon-ad-diagnosis.md) | **已有产品**广告诊断：竞争环境→词库重建→文案埋词→广告优化（4阶段串联） |

### 推荐流程

```
品牌/产品信息
    |
    v  品牌战略（四轮串联）：
1.  /brand-market-scan             -> 市场扫描 + VOC + 竞争格局
2.  /brand-track-hypothesis        -> 3-5个赛道假设 + 选出Top 2
3.  /brand-deep-validation         -> 5D验证 + 对标案例 + 第4区间
4.  /brand-strategy-plan           -> 品牌定位 + 四大支柱 + 路线图
5.  /brand-imc-framework           -> 营销框架 + 渠道预算 + 执行日历
6.  /brand-knowledge-base          -> Obsidian知识库（30-50个文件）
     |
     v  然后用 Amazon 技能执行落地：

数据源（极目数据 / Helium10 / JungleScout）
    |
    v
1.  /amazon-product-selection      -> Top 30 候选品
     |
2.  /amazon-product-shortlist      -> Go-List + 行动计划
     |
     v  对每款产品执行：
3.  /amazon-market-research        -> 调研报告
4.  /amazon-ip-risk-assessment     -> IP风险排查
5.  /amazon-supplier-decision      -> 供应商决策
6.  /amazon-keyword-research       -> 关键词词库
7.  /amazon-listing-copywriter     -> Listing文案
8.  /amazon-main-image-prompt      -> 主副图设计
9.  /amazon-aplus-image-prompt     -> A+内容设计
10. /amazon-compliance-review      -> 三维度合规审查
11. /amazon-pre-launch-review      -> 上架前总复查
     |
     v  上架后：
12. /amazon-ad-architecture        -> 广告架构搭建
13. /amazon-weekly-ad-review       -> 每周广告优化（持续循环）

     已上架产品需要优化时：
14. /amazon-ad-diagnosis           -> 全链路诊断+优化（4阶段串联）
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

| 模型层级 | 预期效果 | 代表模型（截至 2026 年 4 月） |
|---------|---------|---------|
| 推荐 | 完整执行，数据验证步骤生效 | Claude Opus 4.6 / Sonnet 4.6、GPT-5.4、Gemini 3.1 Pro |
| 可用 | 结构完整，可能跳过验证步骤 | DeepSeek V4 / V3.2、Llama 4、Qwen 3.5 (72B+)、GLM-5.1 |
| 不建议 | 章节缺失，合规检查失效 | Qwen 3.5 9B 及以下、30B 以下参数模型 |

关键能力要求：长上下文（8K+ 输入）、强指令遵循、中英双语、联网/工具调用（调研步骤需要）。

### 示例

查看 [examples/](examples/) — 测试报告即将上传。

---

## License

Licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).

You are free to use, share, and adapt these skills for any purpose, including commercial use, as long as you give credit.

## Author

Created by **Alex / 黄子阳** — [ckcm.us](https://ckcm.us)
