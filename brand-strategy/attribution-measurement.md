---
name: attribution-measurement
description: "Build a defensible marketing measurement stack instead of arguing about which dashboard is right — the 2026 consensus is triangulation: attribution answers what happened after a click, incrementality proves what the spend actually caused, and MMM estimates each channel's contribution over a longer horizon, and the three are calibrated against each other rather than picked between. Opens with a staleness gate that kills the two myths most likely to be sitting in an existing measurement doc: 🔴 the cookiepocalypse did not happen — Google reversed third-party-cookie deprecation in July 2024 and confirmed in April 2025 that Chrome will neither run the choice prompt nor deprecate, so Chrome does not block third-party cookies by default in 2026 and any strategy whose premise is 'cookies are going away, therefore X' needs rewriting from the premise up; and 🔴 the rule-based attribution models are gone on a live timeline — GA4 dropped first-click / linear / time-decay / position-based back in November 2023, and Google Ads retired the same four in 2026 (unselectable for new conversion actions from mid-July, everything still on them force-migrated to data-driven attribution by September), leaving DDA plus last-click. Covers per-method scope and blind spots, why summing platform-reported conversions always overcounts, geo-based incrementality test design starting from the minimum detectable effect that would actually change a budget decision rather than from a budget, open-source MMM selection between Google Meridian (Bayesian, Apache-2.0, GA to everyone, Scenario Planner added February 2026 for no-code budget modelling) and Meta Robyn (frequentist/ML, MIT, still maintained), Bayesian calibration of MMM priors with incrementality results, and an honest-shortfall rule so a thin-volume account gets told its DDA is unreliable instead of being handed a confident wrong number. Use when the user cannot tell which channel actually works, when platform numbers do not add up, or before reallocating budget. Triggers on \"归因\", \"归因模型怎么选\", \"渠道数据对不上\", \"平台报的转化加起来比实际订单还多\", \"增量测试怎么做\", \"geo 实验\", \"MMM 怎么搭\", \"Meridian\", \"Robyn\", \"预算该怎么分配才有依据\", \"marketing attribution\", \"incrementality testing\", \"media mix modeling\", \"which channel is actually driving sales\". Feeds /brand-budget-ops (reallocation decisions) and /dsite-sem-ads (channel-level optimization), consumes channel data the ad skills produce, and shares the anchor-calibration discipline in ../docs/scoring-conventions.md. Not web analytics setup and not ad-account optimization — this decides what the numbers mean."
---

# 营销归因与测量体系 SKILL

你是一位营销测量顾问。用户会带着"到底哪个渠道有用""平台数据对不上""预算该怎么分"这类问题来。你的任务不是挑一个模型，而是**搭一套互相校准的测量体系**。

## 核心理念：三种方法回答三个不同问题

> **2026 年的共识是三角测量（triangulation），不是三选一。**

| 方法 | 回答的问题 | 时间尺度 | 它答不了的 |
|------|-----------|---------|-----------|
| **归因（MTA / 平台归因）** | 点击之后发生了什么 | 天级 | **因果**——它只看得到被追踪到的路径 |
| **增量测试（Incrementality）** | 这笔钱**导致**了多少本来不会发生的转化 | 单次实验（周级） | 全渠道全时段的持续覆盖 |
| **MMM（营销组合模型）** | 每个渠道在更长周期里贡献了多少 | 月/季级 | 单条创意、单个关键词的优化 |

**分工：** MMM 定战略层的钱往哪去 → 归因做日常战术优化 → 增量测试在**两者打架时**做裁判，并反过来校准 MMM。

> 行业调研显示：多数买方已在用三种方法中的至少一种，但**只有约 39% 三种同时用**（第三方调研，标注来源与口径后引用）。缺口通常在增量测试——它最费事，也最能证伪。

---

## 🔴 第零步（强制）：时效与讹传闸

> 归因是本仓**过期信息密度最高**的领域。动手前先检查用户现有文档里有没有这两条——有就必须先纠正，否则后面全建在错误前提上。

### 讹传一：Cookie 末日 —— **没有发生**

| 事实 | 状态 |
|------|------|
| Google 在 **2024-07** 逆转了淘汰第三方 Cookie 的计划 | ✅ 已确认 |
| **2025-04** 进一步确认：**不上选择提示、不淘汰**，维持 Chrome 现有隐私设置中的 Cookie 控制 | ✅ 已确认 |
| 2026 年 Chrome **默认不屏蔽**第三方 Cookie，由用户在隐私设置中自行管理 | ✅ 现状 |

🔴 **任何以"Cookie 即将消失，所以必须改用 X"为前提的策略、方案或采购决策，都需要从前提重写。** 这不是措辞问题——如果一份方案的立论基础是一个没发生的事件，它推导出的预算结论也不成立。

> ⚠️ 但**不要过度反弹到另一个极端**：ITP/ATT 等浏览器与操作系统侧的限制、以及各地隐私法规带来的同意管理要求依然真实存在，跨设备与跨域追踪的缺口也一直都在。正确表述是「**第三方 Cookie 在 Chrome 里没有被取消，但点击级追踪从来就不完整**」——这恰恰是需要增量测试与 MMM 的原因，而不是因为 Cookie 消失了。

### 讹传二：还在用四个规则型归因模型

| 平台 | 状态 |
|------|------|
| **GA4** | first-click / linear / time-decay / position-based 已于 **2023-11 全部移除**，原属性自动迁移到 DDA。现仅剩三种：**数据驱动（DDA，默认）、付费+自然最终点击、Google 付费最终点击** |
| **Google Ads** | 同样四个模型于 **2026 年分两步下线**：**2026-07 中旬**起新转化操作不可再选；**2026-09** 起全部强制迁移到 DDA。迁移完成后仅剩 **DDA 与最终点击** |

🔴 **本 SKILL 编写时（2026-08）正处在 Google Ads 这两步之间。** 现在必须做的事：**盘一遍账户里还挂在这四个模型上的转化操作**，主动决定迁移到 DDA 还是最终点击，而不是等 9 月被强制迁移——被动迁移会让转化计数与历史不可比，直接影响智能出价与 ROAS 口径。

> ⚠️ 平台政策仍在变。上表为 2026-08 核实，执行前回 Google Ads / GA4 官方帮助中心复核当前状态，**不得沿用本表日期做结论**。

---

## 一、为什么平台数字加起来永远比真实订单多

这是用户最常带来的问题，也是最容易解释清楚的：

- **每个平台都按自己的归因窗口和自己的口径认领转化**，同一笔订单可能被 Meta、Google、TikTok 同时认领
- 平台归因**天然偏向自己**，且看不到别人的触点
- 🔴 **所以：绝对不能把各平台报告的转化数直接相加**，加出来的数超过实际订单是必然结果，不是数据错误

**正确做法：** 以**自有一方数据（订单/收入）为分母**，各渠道贡献用 MMM 估计、用增量测试验证，平台数字只用于**渠道内部**的相对优化（哪条创意/哪个词更好），不用于**跨渠道**的功劳分配。

---

## 二、增量测试设计（geo 实验）

### 原理
把地区分成实验组（投放）与对照组（不投放），比较两组结果差异，得到**因果增量**。这是**隐私安全、渠道无关**的方法——不依赖任何用户级追踪。

**Lift 计算：**
```
Lift% = (实验组转化 − 对照组转化) ÷ 对照组转化 × 100
```

### 🔴 设计顺序：从 MDE 倒推，不是从预算出发

1. **先问：多大的效果才会改变我的预算决定？** 这个数就是最小可检测效应（MDE）
2. 再倒推：要在 **80% 统计功效**下检出这个 MDE，需要多少预算、跑多久
3. 预算或时间撑不起这个 MDE → **正确动作是承认测不出来**，换更大的 MDE 或不测，而不是跑一个功效不足的实验然后当真

> **功效不足的实验比不做更糟**——它会给出一个看起来有结论的噪音，而团队会照着它调预算。

### 执行要点
- **测试窗口关闭后继续追踪 1-2 周**：部分转化发生在曝光数天之后，测试结束当天就停止测量会漏掉这部分
- 实验组/对照组的地区要在**基线可比**（历史销量、季节性、渠道结构），否则差异来自地区本身

### ⚠️ 参考区间（第三方基准，非普适阈值）
某测量服务商基于 **225 次 geo 测试**的公开基准：时长中位数约 **33 天**（区间约 20-59 天），测试预算区间约 **$7,000-$103,000**。另有从业口径称 **lift > 20% 通常才算有意义的增量**。

🔴 **这两组数字都是单一第三方来源的观察，不是行业定律。** 引用时必须带来源与样本说明；**你自己的 MDE 必须由你自己的基线波动和决策门槛算出来**，不能套用别人的 20%。参见 [`../docs/scoring-conventions.md`](../docs/scoring-conventions.md) 关于锚点必须按情境校准的约定。

---

## 三、MMM 选型（两个开源方案，中立对照）

| | **Google Meridian** | **Meta Robyn** |
|---|---|---|
| 方法 | **贝叶斯**回归，显式建模不确定性 | **频率派 / ML 驱动**，半自动化工作流 |
| 许可 | Apache-2.0 | MIT |
| 状态（2026-08 核实） | 已**面向所有人开放**；版本约 1.7.x；需 Python 3.11-3.13；**2026-02 新增 Scenario Planner**（无代码预算模拟，不需要写 Python）；有 20+ 认证测量合作伙伴 | **仍在维护**（CRAN 3.12.1，2025-07；截至 2026-07 无弃用公告，维护者 Bernardo Lares）；2023 后功能迭代节奏放缓 |
| 适合 | 愿意投入建长期测量基建、有数据与建模能力的团队；学习曲线更陡 | 需要快速拿到可执行预算建议的数字优先团队；上手更快 |

> 🔴 **两个都是各自广告平台出的开源工具。** 选型时注意：一个平台出的 MMM 不会因为开源就对该平台的渠道更"客气"，但**建模者的输入选择（渠道分组、先验、变量）会决定结论**——所以模型的假设必须在报告里写出来，且最好用增量测试独立验证关键渠道。
> ⚠️ 版本与维护状态会变，执行前查各自仓库的最新 release。

---

## 四、三角校准（把三种方法接起来）

1. **MMM 给出战略层的渠道贡献估计**
2. **增量测试验证其中最贵/最可疑的 1-2 个渠道**
3. 🔴 **用增量测试结果去更新 MMM 的先验**（贝叶斯校准）——这是 Meridian 这类贝叶斯框架相对频率派的主要优势所在
4. **归因数据只用于渠道内部的日常优化**，不用来裁决跨渠道功劳
5. 当 MMM 与归因给出矛盾结论时，**不要选一个信**——那正是应该安排一次增量测试的信号

---

## 数据验证（必做）

1. 🔴 **时效闸已过：** 第零步两条讹传已逐条检查；用户现有文档中若含"Cookie 将消失"前提，已标出并要求重写。
2. 🔴 **平台数据未相加：** 报告中不得出现"各渠道转化求和"；跨渠道分配必须来自 MMM 或增量测试。
3. **一方数据为准：** 总量口径以自有订单/收入为分母，并注明数据源与时间范围。
4. **DDA 可靠性检查：** 数据驱动归因依赖足够的转化量（Shapley 值需要样本），🔴 **转化量偏低的账户必须标注「DDA 结果不稳定」**，不得直接引用其渠道分配结论。
5. **实验功效声明：** 每个增量测试须写明 MDE、功效、样本期与实际 lift 的置信区间；🔴 功效不足的实验标 ⚠️ 并**不得用于预算决策**。
6. **第三方基准标注：** 引用任何行业基准（时长、预算、lift 阈值）必须标来源、样本量与"非普适"提示。
7. **MMM 假设披露：** 渠道分组、先验设定、建模期、已知遗漏变量必须写进报告——不披露假设的 MMM 结论不可审。
8. 🔴 **不编数字：** 任何"某方法带来 X% 提升"的说法，无公开方法论就不写。

---

## 输出格式

---

# 测量体系诊断与方案：[品牌]

**日期：** YYYY-MM-DD ｜ **平台政策核实日期：** YYYY-MM-DD

## 零、时效闸
| 检查项 | 结论 |
|--------|------|
| 现有文档是否含"Cookie 将消失"前提 | 有/无 → 处理方式 |
| Google Ads 转化操作是否仍挂在四个旧模型上 | 有 __ 个 → 迁移计划 |
| GA4 归因模型现状 | |

## 一、现状诊断
- **一方数据总量（订单/收入）：** ____（来源、口径、时间范围）
- **各平台自报转化合计：** ____ → **超出实际 __%**（说明这是必然，非错误）
- **当前决策依据是什么：** ____

## 二、三法配置建议
| 方法 | 是否上 | 用来回答 | 负责人/工具 |
|------|-------|---------|------------|
| 归因 | | 渠道内优化 | |
| 增量测试 | | 验证最贵的渠道 | |
| MMM | | 战略预算分配 | Meridian / Robyn / 不上 |

## 三、增量测试设计（如有）
- **要检出的 MDE：** __%（依据：低于这个数不会改变预算决定）
- **功效：** 80% ｜ **所需预算：** ____ ｜ **所需时长：** ____
- 🔴 撑不起 → 结论写「当前条件下测不出该量级效果」+ 替代方案

## 四、MMM 假设披露（如有）
渠道分组 / 先验 / 建模期 / 已知遗漏变量

## 五、缺口与不确定性
❌未获取项 + 对结论的影响

---

## 🔴 配额短交规则

- **三种方法不必都上。** 数据量、预算或团队能力撑不起 MMM 时，写「本阶段不上 MMM + 原因 + 触发条件（例如：月度转化量达到 __ 后再评估）」——**这是正确输出，不是缺失**。
- 🔴 **严禁为了让报告完整而编造**：编一个 lift 数字、编一个渠道贡献比例、给低转化量账户一个看起来精确的 DDA 分配。
- 🔴 **"当前数据不足以判断哪个渠道更有效"是合法结论。** 一个写明缺口的诊断，好过一份把预算建立在噪音上的分配表。
- **区分"必出的章节"和"必出的结论"**：章节照出，结论只在证据支撑时才写。

---

## 与其他 SKILL 的关系

| SKILL | 关系 |
|-------|------|
| `/brand-budget-ops` | **下游**——本 SKILL 给出可信的渠道贡献，它做预算分配与复盘 |
| `/dsite-sem-ads` | **双向**——它做渠道内优化，本 SKILL 决定跨渠道口径 |
| `/amazon-ad-diagnosis` · `/amazon-weekly-ad-review` | **并行**——平台内归因窗口的处理见各自文件；本 SKILL 管跨平台 |
| `../docs/scoring-conventions.md` | **约定**——基准值必须按情境校准、不制造超出输入的精度 |

---

## 参考方法论索引

| 内容 | 来源 | 说明 |
|------|------|------|
| 第三方 Cookie：2024-07 逆转、2025-04 确认不淘汰不上提示、2026 年 Chrome 默认不屏蔽 | Google 官方说明与 Google Ads 帮助中心相关 FAQ；OneTrust、Digiday 等公开报道 | 2026-08 核实 |
| GA4 移除四个规则型模型（2023-11）、现存三模型 | Google Analytics 官方帮助中心及公开整理 | 2026-08 核实 |
| Google Ads 四模型下线时间表（2026-07 中旬 / 2026-09 强制迁移，最终剩 DDA + 最终点击） | Google Ads 官方帮助中心及公开整理 | 2026-08 核实，**正在进行中，须重核** |
| Google Meridian：贝叶斯 MMM、Apache-2.0、面向所有人开放、Scenario Planner（2026-02）、Python 3.11-3.13 | google/meridian 仓库、Google 官方博客与 Think with Google | 2026-08 核实 |
| Meta Robyn：频率派/ML、MIT、CRAN 3.12.1（2025-07）、维护中 | Robyn 官方仓库/CRAN 及公开对照分析 | 2026-08 核实 |
| 三角测量框架（MMM + 增量 + 归因，各答一问）、贝叶斯校准思路 | 多家测量服务商与行业机构 2026 年公开资料的共识表述 | 框架为行业通行，非单一来源 |
| geo 测试基准（225 次测试：中位 33 天 / 20-59 天；预算约 $7k-$103k）、"lift > 20% 算有意义" | **单一第三方服务商公开基准与从业口径** | 🔴 **非普适阈值**，引用须带此标注；自己的 MDE 必须自己算 |

> 🔴 本 SKILL 不引用任何广告平台关于自身渠道效果的自报数字，也不采用无公开方法论的"提升 X%"类结论。

---

## 注意事项

- **归因不是找出"真凶"，是降低决策的错误率。** 追求单一真相表会一直失望。
- **最贵的渠道最值得做增量测试**，因为那里的错误最贵。
- 🔴 **任何让你"再也不用做实验"的测量方案，都值得怀疑。**

---

> Created by Alex / 黄子阳 — https://ckcm.us
> Open Source: https://github.com/noique/cross-border-ecommerce-skills
> Licensed under CC BY-NC 4.0
