---
name: trustpilot-voc-quick
description: Pull a 5-minute surface read of a brand's Trustpilot page with WebFetch — overall rating, total review count, 5★-to-1★ distribution, Verified/Claimed status, a summary table of the 10-20 most recent reviews with their core themes, positive/negative high-frequency words, and a trend call — plus an automatic side-by-side comparison table with green/yellow/red reputation-risk flags when several brands are passed at once. Every figure must come from the fetch that ran: Trustpilot throttles hard, so the skill treats "couldn't fetch" as a main path — three ordered fallbacks (direct WebFetch → Google cache → ask the user to paste), and if all three fail it emits an explicit ❌未获取 block instead of a rating, a distribution or a trend call, with brands that failed kept in the comparison table as ❌ rows rather than filled in. Nothing may be inferred from brand impression, category intuition or the layout example in the skill itself. Use when the user just wants a fast read on how a brand's word-of-mouth looks right now, or wants to benchmark a handful of competitors in parallel, without setting up a scraper or waiting on a full-corpus run. Triggers on "Trustpilot 快速扫描", "看看这个品牌口碑怎么样", "查一下 Trustpilot 评分", "几个竞品口碑对比", "Trustpilot 星级分布", "这个牌子差评多不多", "quick Trustpilot check", "what's this brand's Trustpilot rating", "compare competitors on Trustpilot". Supplies the VOC section of /brand-market-scan 第零步; escalate to /trustpilot-voc-deep when the brand has >500 reviews, its rating sits in the 2.0-3.5 danger band, or LDA topic modeling / AI theme synthesis is needed; complements /amazon-market-research (Amazon platform VOC vs. this skill's independent-site VOC).
---

# Trustpilot VOC 快速扫描 SKILL

用户想要快速获取某品牌在 Trustpilot 上的用户评价概况时调用此技能。使用 WebFetch 抓取表层数据（总评分、评论数、星级分布、近期评论摘要），5 分钟内出结果。

**适用场景：**
- 品牌战略扫描第零步（brand-market-scan 的 VOC 快速采集）
- 竞品横向对比（多品牌并行调用，每个品牌 1-2 分钟）
- 不需要深度主题分析的快速尽调

**如果需要全量评论+情感分析+主题建模+AI 归纳，请使用 `/trustpilot-voc-deep`。**

## 🔴 数据获取规则（先于以下所有步骤）

> 本 SKILL 的每一个数字都来自一次 WebFetch。**Trustpilot 反爬很强，抓不到是常态而非例外**——所以"抓不到时怎么办"是本 SKILL 的主路径，不是边角料。

- 🔴 **下方输出模板里的每个数字（总评分 / 评论数 / 星级分布 / 高频词 / 趋势）都必须来自本次实际抓取的页面。** 严禁凭品牌印象、类目常识或本文件中的示例格式推断任何一项。
- 🔴 **抓不到 ≠ 可以估一个。** 三条降级路径（见「注意事项」）全部失败时，输出：
  ```
  ## [品牌名] — ❌ 未获取
  已尝试：WebFetch 直取 / Google 缓存 / 请用户粘贴页面内容
  失败原因：[限流 / 页面不存在 / 用户未提供]
  本次不产出评分、星级分布与趋势判断。
  ```
  **这就是本次任务的正确完成形态，不算失败。**
- **部分获取照实标：** 拿到总评分但星级分布被折叠 → 分布表填 ❌未获取 + 原因，不要按总评分反推一个分布。
- 🔴 **多品牌对比时，缺数据的品牌保留在表里但整行标 ❌未获取**，不得为了让对比表好看而补齐——一张有洞的对比表，好过一张填满的假表。
- 🔴 **本 SKILL 的输出会被 `/brand-market-scan` 第零步直接插入 VOC 章节**（见下方第四步）。那份报告明令「严禁用记忆或推断补齐 ASIN、价格、评分、上架日期或评论原文」——**本 SKILL 是它的上游，标准只能同等严格，不能更松。**

## 执行模式：batch（可并行对多个品牌执行）

## 输入要求

**必须提供：**
- 品牌 Trustpilot 页面 URL（如 `https://www.trustpilot.com/review/aoocci.com`）
- 或品牌域名（自动拼接 URL）

**可选提供：**
- 多个品牌（逗号分隔）→ 自动并行对比
- 输出路径（默认为当前工作目录下 `trustpilot-voc/`）

## 执行步骤

### 第一步：WebFetch 抓取

使用 WebFetch 访问 Trustpilot 页面，提取：
- 品牌名 + Trustpilot 总评分（X.X/5）
- 评论总数
- 星级分布（5★/4★/3★/2★/1★ 各自占比 %）
- 最近 10-20 条评论的摘要（评分 + 短文 + 日期）
- Trustpilot 认证状态（Verified Business / Claimed）

### 第二步：结构化输出

生成 markdown 表格，包含：

```markdown
## [品牌名] — Trustpilot VOC 快速扫描

**抓取日期：** YYYY-MM-DD
**Trustpilot URL：** https://...
**总评分：** X.X/5（基于 N 条评论）

### 星级分布

| 星级 | 数量 | 占比 |
|------|------|------|
| 5★ | | |
| 4★ | | |
| 3★ | | |
| 2★ | | |
| 1★ | | |

### 最近评论摘要

| 评分 | 日期 | 评论摘要 | 核心主题 |
|------|------|---------|---------|
| | | | 产品质量/物流/客服/... |

### 关键观察

- 正面高频词：[从评论中提取]
- 负面高频词：[从评论中提取]
- 趋势判断：向好 / 持平 / 恶化
```

### 第三步：多品牌对比（如用户提供多个）

如用户输入了多个品牌，额外输出：

| 品牌 | 总评分 | 评论数 | 5★ 占比 | 1★ 占比 | 风险标签 |
|------|--------|--------|--------|---------|---------|
| Brand A | 4.5 | 269 | 80% | 10% | 🟢 健康 |
| Brand B | 3.5 | 247 | 61% | 26% | 🟡 需关注 |
| Brand C | 2.0 | 1213 | — | — | 🔴 口碑危机 |

### 第四步：与 brand-market-scan 集成

如果本次调用是 `brand-market-scan` 第零步的一部分，输出将直接插入第一轮报告的 VOC 章节。

## 深度分析触发条件

当扫描结果显示以下情况时，提醒用户升级到 `/trustpilot-voc-deep`：

- 品牌评论 >500 条 — 值得做全量分析
- 评分在 2.0-3.5 之间 — 值得深挖"为什么用户不满"
- 需要竞品级深度对比 — 单品牌平均 200+ 评论主题分析
- 需要 LDA 主题建模或 AI 归纳

## 与其他 SKILL 的关系

| SKILL | 定位 | 关系 |
|-------|------|------|
| brand-market-scan | 品牌战略扫描第一轮 | 调用本 SKILL 采集表层数据 |
| trustpilot-voc-deep | 全量评论+主题+AI 归纳 | 本 SKILL 的升级版，需本地环境 |
| amazon-market-research | Amazon 评论 VOC | 互补——Trustpilot 是独立站 VOC，Amazon 是平台 VOC |

## 输出形态示例（占位符 — 🔴 数字一律以本次抓取为准）

> ⚠️ 本节演示的是**排版与观察写法**，不是可套用的数据。**严禁把任何示例数字搬进真实报告**——包括"看起来差不多"的情况。

```
## [品牌名] — Trustpilot VOC 快速扫描

抓取日期：[本次抓取日期]
总评分：[X.X]/5（基于 [N] 条评论）

星级分布：
- 5★: [n] ([p]%)
- 4★: [n] ([p]%)
- 3★: [n] ([p]%)
- 2★: [n] ([p]%)
- 1★: [n] ([p]%)

观察：[从实际分布读出的形态，例如"两极分化——五星与一星双高、中间星级缺失"]
下一步：[基于实际数据的建议，例如"深挖一星评论的共性原因"]
```

> 观察句要**从本次真实分布读出来**。上例的"两极分化"只是一种可能形态；分布平缓、单峰、长尾都各有写法，不要默认套用两极分化的叙事。

## 注意事项

- **降级顺序（依次尝试，不可跳过直接下结论）：** ① WebFetch 直取 → ② Trustpilot 的 Google 缓存页 → ③ 请用户手动粘贴页面内容。🔴 **三条全失败 → 按上方「数据获取规则」输出 ❌未获取，不得估算。**
- 评论数 >100 时抓取前 20 条即可判断大致趋势（**前提是这 20 条真的抓到了**）
- 星级占比精度到整数（Trustpilot 只显示整数 %）——**不要为了凑 100% 去调整某一档**，合计 99% 或 101% 照实写并注明"平台四舍五入"
- 近期评论摘要按**实际抓到的条数**写，抓到 7 条就写 7 条并注明「实际 7 条」，不要凑满 10-20 条

---

> Created by Alex / 黄子阳 — https://ckcm.us
> Open Source: https://github.com/noique/cross-border-ecommerce-skills
> Licensed under CC BY-NC 4.0
