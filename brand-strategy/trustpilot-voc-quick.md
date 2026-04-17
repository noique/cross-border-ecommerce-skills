# Trustpilot VOC 快速扫描 SKILL

用户想要快速获取某品牌在 Trustpilot 上的用户评价概况时调用此技能。使用 WebFetch 抓取表层数据（总评分、评论数、星级分布、近期评论摘要），5 分钟内出结果。

**适用场景：**
- 品牌战略扫描第零步（brand-market-scan 的 VOC 快速采集）
- 竞品横向对比（多品牌并行调用，每个品牌 1-2 分钟）
- 不需要深度主题分析的快速尽调

**如果需要全量评论+情感分析+主题建模+AI 归纳，请使用 `/trustpilot-voc-deep`。**

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

## 输出示例（Aoocci 真实案例）

```
## Aoocci — Trustpilot VOC 快速扫描

抓取日期：2026-04-11
总评分：4.5/5（基于 269 条评论）

星级分布：
- 5★: 216 (80%)
- 4★: 21 (8%)
- 3★: 4 (1%)
- 2★: 2 (1%)
- 1★: 26 (10%)

观察：两极分化——80% 五星但 10% 一星，中间缺失。
需深挖 26 条一星评论的共性原因。
```

## 注意事项

- Trustpilot 有反爬，WebFetch 可能被限流 → 降级为手动告知用户贴页面内容
- 评论数 >100 时抓取前 20 条即可判断大致趋势
- 星级占比精度到整数（Trustpilot 只显示整数 %）
- 如本 SKILL 无法访问 Trustpilot，尝试 Trustpilot 的 Google 缓存页面

---

> Created by Alex / 黄子阳 — https://ckcm.us
> Open Source: https://github.com/noique/cross-border-ecommerce-skills
> Licensed under CC BY-NC 4.0
