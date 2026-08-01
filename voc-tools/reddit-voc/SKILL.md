---
name: reddit-voc
description: Mine Reddit for pre-purchase Voice-of-Customer (VOC) insights for a DTC brand or Amazon product. Use when the user wants to understand what overseas users actually say about a category before buying — pain points, value-system landmines, jargon, alternatives. Triggers on "Reddit VOC", "Reddit 用户洞察", "海外用户怎么说我们品类", "购买前 VOC", "find subreddits for [category]", "what do Redditors think of [product]", "听用户声音", "Reddit 调研", "海外用户痛点". Pairs with /trustpilot-voc-deep (post-purchase) and /amazon-market-research (post-purchase).
---

# Reddit VOC — 购买前用户洞察 SKILL

从 Reddit 挖**购买前**用户真实声音(VOC: Voice of Customer)— 痛点、价值观红线、行业黑话、替代方案。

**为什么是 Reddit?** Amazon Review 与 Trustpilot 都是**购买后**视角(已经买了的人怎么说);Reddit 是**购买前**视角(还没买的人在讨论什么、纠结什么、骂什么)。两者覆盖不同的决策环节,缺一不可。

## 适用场景

- **品类调研** — 入局一个新品类前,先听用户在 Reddit 怎么说,避免拍脑袋
- **品牌战略** — 写品牌定位 / IMC 之前,确认核心痛点和价值观底线
- **Listing 优化** — 用户原话直接转化为亚马逊 Listing / DTC 落地页文案
- **广告创意** — Reddit 高赞吐槽 → TikTok / Facebook 广告 hook
- **竞品弱点反向放大** — 用户骂竞品的具体问题 → 我们差异化定位

## 不适用

- **快速验证选品是否好卖** — Reddit 不反映销售数据,用 Jungle Scout / 卖家精灵
- **购买后投诉/服务问题** — 用 `/trustpilot-voc-deep` 或 `/amazon-market-research`
- **B2B / 工业品** — Reddit 主要覆盖 C 端;B2B 用 LinkedIn

## 执行模式

**纯人工 + AI 引导**(无爬虫,Reddit 反爬严格且 API 限频)。一次完整调研约 **2-4 小时**,产出一份结构化 VOC 报告。

如果未来需要规模化抓取,可结合 [PRAW API](https://praw.readthedocs.io/) + 关键词筛选,但当前 SKILL 不依赖。

## 五步流程

```
Step 1: 找社区(4 维度)
  ↓
Step 2: 筛高价值帖子(Top + 6 类标签)
  ↓
Step 3: 帖子拆解(类型 / 情绪 / 原话 / 替代方案 / 价值观)
  ↓
Step 4: 洞察 → 业务动作(Listing / 广告 / 客服 / 定位)
  ↓
Step 5: 二维矩阵定位(功能重要性 × 满意度)— 可选,系统化时用
```

每一步都有独立的 reference 文件支撑,见下文。

---

## Step 1 — 找社区(4 个维度)

详见 [`references/community-dimensions.md`](references/community-dimensions.md)。

围绕你的品类,在 Reddit 上必须找到这 4 类社区:

| 维度 | 含义 | 例子(以智能猫砂盆为例) |
|---|---|---|
| **D1. 品类品牌社区** | 直接讨论这个产品本身或竞品的社区 | r/LitterRobot, r/CatLitterTraining |
| **D2. 人群数据社区** | 跳出产品,讨论这群用户的生活方式 | r/SoloLiving, r/CrazyCatLadies, r/Apartments |
| **D3. 问题社区** | 用户养宠/使用过程中遇到的具体问题 | r/CatHealth, r/AskVet, r/CatAdvice |
| **D4. 价值观社区** | 用户的价值观底线,营销时必须规避或对齐 | r/ZeroWaste(环保)、r/AntiConsumption(反过度消费)、r/BuyItForLife(耐用) |

**找社区的 2 个方法:**

- **A. AI 搜(推荐)**:用 Claude / Perplexity,因其底层数据有 Reddit API 协议,数据准
- **B. Google 公式**:`关键词 + site:reddit.com` 或 `关键词 + reddit`(不要省 site:)
- **C. 进入一个核心社区后**,看右侧栏 "Related Communities" / "Similar Subreddits",可以滚雪球

搜索公式见 [`references/community-dimensions.md`](references/community-dimensions.md) 末尾。

**产出**:[`templates/community-map.csv`](templates/community-map.csv) — 8-15 个社区清单 + 订阅数 + 维度归属。

---

## Step 2 — 筛高价值帖子(Top + 6 类标签)

进入每个目标社区后,**不要从 Hot/New 开始读**,而是:

1. **按 Top → All Time / Past Year 排序**,看历史高赞帖
2. **看到 51-100 名也别跳过** — 高赞太聚焦,中间排名常有完整故事和具体场景
3. **按 Reddit 内置标签筛选**(社区左上角 Flair 过滤),6 类高价值标签:

| 标签 / Post Flair | 中文叫法 | VOC 价值 |
|---|---|---|
| `Recommendation` / `[REC]` | 求推荐 | 用户已到购买决策口,要的是临门一脚的标准 |
| `Rant` / `Vent` / `Hate` | 吐槽点 | 竞品具体翻车点 = 我们差异化机会 |
| `Question` / `Help` | 求助帖 | 用户已买但没用好,客服话术 + IPQ 直接素材 |
| `Comparison` / `vs` | 竞品对比 | 用户视角下的电梯弱点 |
| `Discussion` / `Daily` | 日常品 / 闲聊 | 痛点埋在生活细节里,需要挖掘 |
| `Review` / `Experience` | 评测体验 | 完整故事,长内容,带数据 |

详见 [`references/post-taxonomy.md`](references/post-taxonomy.md)。

**产出**:[`templates/post-analysis.csv`](templates/post-analysis.csv) — 每个社区 5-10 个高价值帖子。

---

## Step 3 — 帖子拆解(6 维分析)

每个高价值帖子,按 6 维拆解:

| 维度 | 拆什么 | 怎么用 |
|---|---|---|
| **1. 来源社区** | 哪个 subreddit + 哪个维度(D1-D4) | 判断这个洞察的代表性 |
| **2. 原话(Quote)** | 用户的原话,逐字抄 | 直接喂给 Listing / 广告(用户语言 ≥ 你的语言) |
| **3. 类型** | 功能价值 / 信任产品 / 价值观 | 决定营销 hook 的层级 |
| **4. 情绪强度** | 0-10 分,看用词激烈度 + 点赞数 + 评论支持度 | 强度高的优先做内容 |
| **5. 替代方案** | 用户当前怎么解决?(用什么品牌 / 什么 DIY 方法) | 这是真正的竞品(可能不是同品类) |
| **6. 价值观底线** | 涉及环保 / 反过度消费 / 政治正确等敏感点 | 营销时务必规避,否则踩雷 |

**Reddit 黑话识别**:用户原话里会有大量缩写(BIFL / YMMV / NSFW / TIL 等),不认识会误读情绪和价值观。详见 [`references/reddit-slang.md`](references/reddit-slang.md)。

---

## Step 4 — 洞察 → 业务动作(映射表)

6 类帖子各自对应**不同的业务输出**,不能混着用。详见 [`references/voc-to-output.md`](references/voc-to-output.md)。

| 帖子类型 | 优先输出 | 二级输出 |
|---|---|---|
| 求推荐(REC) | Listing 卖点 / 落地页主标题 | SEO 关键词 |
| 吐槽(Rant) | 竞品弱点 → 我们差异化定位 | 广告 hook(对立式) |
| 求助(Question) | 客服话术库 / IPQ(售前问答) | A+ Content 解决方案区 |
| 对比(Comparison) | 我们 vs 竞品对比矩阵 | 红人种草分镜脚本 |
| 日常(Daily) | 长线内容策略(博客/YouTube 选题) | 品牌人设故事 |
| 高赞 Top | 平台定位 / 品类心智 | 全年内容日历主线 |

**3 个真实 case**(全部基于 PDF 实录清洗整理):

1. **Listening case** — 用户在 Reddit 抱怨某竞品猫砂盆"要拆七块洗",我们的差异化文案直接写"单步即明白,还没出账"
2. **广告 hook case** — Reddit 高赞原话"额头刷盆,每天可以自动清洁",直接做成 TikTok 视频 hook
3. **终结型文案 case** — 跑步耳机用户 Reddit 原话"跑步时不会掉",优于团队憋出来的"100 句广告创意"

---

## Step 5 — 二维矩阵定位(可选,高阶)

详见 [`references/positioning-matrix.md`](references/positioning-matrix.md)。

把 N 个帖子结构化标注后,可以画一张矩阵:

```
                  满意度(纵轴)
                       ↑
        高重要性         |         高重要性
        + 高满意度       |         + 低满意度
        (维持区)         |         ★ 机会区 ★
        ─────────────────┼─────────────────
        低重要性         |         低重要性
        + 高满意度       |         + 低满意度
        (溢出区)         |         (放弃区)
                       │                    → 重要性(横轴)
```

**右下角"高重要性 + 低满意度"= 用户想要但市场没满足** = 我们的定位机会区。

矩阵法适合做**品类深度诊断**(每品类做一次,周期 2-4 周),不是每个 VOC 调研都需要。

---

## 输入要求

**必填:**
- 目标品类 / 关键词(英文,因 Reddit 主要为英语社区)
- 调研目的(品类调研 / Listing 优化 / 广告创意 / 品牌定位 — 决定深度)

**选填:**
- 已知竞品名(用于精准定位品牌社区)
- 目标市场(US / UK / AU — 影响社区选择和价值观判断)
- 配套的 Trustpilot / Amazon Review 数据(做购买前 vs 购买后对比)

## 输出结构

调研完成后,产出:

```
{category}_reddit_voc_{date}/
├── community-map.csv         # 8-15 个目标社区清单
├── post-analysis.csv          # 30-80 个高价值帖子拆解
├── insight-action-map.csv     # 洞察 → 业务动作映射
├── slang-dictionary.md        # 本次调研中遇到的黑话(累积更新)
├── positioning-matrix.png     # (可选)二维矩阵图
└── report.md                  # 综合洞察报告
```

报告标准章节:
1. 品类心智 — 用户怎么定义这个品类
2. 核心痛点 Top 5(带原话引用)
3. 竞品翻车点 Top 5(具体场景)
4. 价值观红线 Top 3(营销规避项)
5. 用户语言库 — 直接可用的 Listing / 广告原话
6. 替代方案地图 — 用户当前在用什么(可能不是同品类)
7. (可选)二维矩阵定位结论

#### 🔴 配额短交规则(Top 5 / Top 3 是目标,不是及格线)

> Reddit 限流/封禁常见,样本不足是常态。**配额撑不住时如实少交,不要用编造的"原话"把章节填满。**

- 🔴 **严禁编造、改写或"合成"任何 Reddit 原话、用户名、帖子链接或点赞数。** 每一条引用必须能追溯到一个真实帖子/评论(附 permalink 或 subreddit + 日期)。这条与本 SKILL 的「永远抄用户原话」是一体两面——**抄的前提是有东西可抄**。
- **痛点只统计到 3 条就写 3 条**,标注「实际 3/5,原因:相关讨论样本不足 / 目标 subreddit 抓取失败」。**如实短交 = 本步骤完成,不算失败。**
- **区分"必出的章节"和"必出的结论":** 章节一律输出(哪怕只有一句「本次样本不足,不下结论」+ 缺口说明);结论只在有原话支撑时才写。
- **抓取整体失败时**(403 / 限流 / subreddit 不可访问):整份报告标 ❌未获取 + 已尝试的 subreddit 与检索式,**不产出洞察**。一份写明缺口的报告,优于一份读起来很顺但没有真实语料的报告。
- 「多维度交叉(≥2 个社区)」是可信度门槛,不是凑数指标——只在 1 个社区出现的洞察照实标注「单社区,未交叉验证」,不要为了达标去别的社区"找"一条相似的。

## 关键原则

1. **用户语言 > 你的语言** — 永远抄用户原话,别自己改写
2. **价值观比功能痛点更重要** — 营销可以不说卖点,但绝不能踩价值观
3. **Top 不只看第 1-10 名** — 51-100 名常有最完整的故事
4. **多维度交叉** — 一个洞察出现在 ≥2 个不同维度社区,可信度才够
5. **录音 / 转写不能直接用** — Reddit 原文是文字,本身就是结构化语料,别二次加工

## 与其他 SKILL 的关系

| SKILL | 定位 | 与本 SKILL 关系 |
|---|---|---|
| `/trustpilot-voc-deep` | 购买后 VOC(独立站评论) | 互补 — 本 SKILL 做购买前 |
| `/trustpilot-voc-quick` | Trustpilot 表层数据 | 互补 |
| `/amazon-market-research` | Amazon Review VOC | 互补 — 本 SKILL 做购买前 |
| `/brand-market-scan` | 品牌战略第零步 | 本 SKILL 可作为 D1 驱动力验证输入 |
| `/brand-deep-validation` | 品牌战略深度验证 | 本 SKILL 提供需求侧原始证据 |
| `/amazon-listing-copywriter` | 亚马逊 Listing 撰写 | 本 SKILL 输出"用户语言库"是其核心输入 |
| `/amazon-keyword-research` | 关键词研究 | 本 SKILL 的"求推荐"标签直接产出长尾词 |
| `/tiktok-growth` | TikTok 增长 | 本 SKILL 的"广告 hook"直接产出短视频脚本素材 |

## References

- [`references/community-dimensions.md`](references/community-dimensions.md) — Reddit 找社区的 4 维度方法 + 搜索公式
- [`references/reddit-slang.md`](references/reddit-slang.md) — Reddit 黑话词典(BIFL / YMMV / AITA 等)
- [`references/post-taxonomy.md`](references/post-taxonomy.md) — 6 类帖子分类详解
- [`references/voc-to-output.md`](references/voc-to-output.md) — 洞察 → 业务动作映射 + 3 个真实 case
- [`references/positioning-matrix.md`](references/positioning-matrix.md) — 二维矩阵法(发言人2 实录方法论)

## Templates

- [`templates/community-map.csv`](templates/community-map.csv) — 社区清单
- [`templates/post-analysis.csv`](templates/post-analysis.csv) — 帖子拆解
- [`templates/insight-action-map.csv`](templates/insight-action-map.csv) — 洞察→动作映射

---

> Created by Alex / 黄子阳 — https://ckcm.us
> Open Source: https://github.com/noique/cross-border-ecommerce-skills
> Licensed under CC BY-NC 4.0
> 方法论来源:基于一份内部 VOC 实战分享(2026-05)清洗整理
