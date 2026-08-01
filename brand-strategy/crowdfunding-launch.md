---
name: crowdfunding-launch
description: "Plan and run a reward-based crowdfunding launch (Kickstarter / Indiegogo) as a brand's first overseas beachhead — treating the campaign as four jobs at once, not one: raising production capital, validating real demand with real money, building launch-day awareness and press, and opening a distribution path into DTC and retail. Opens with a mandatory delivery-and-claims gate, because a reward campaign is a legally enforceable promise in the US: the FTC has brought cases against creators who took backer money and did not ship (Erik Chevalier / The Doom That Came to Atlantic City — the FTC's first Kickstarter action, $122k raised on a $35k goal, settled with a $111,793.71 judgment; Douglas Monahan / iBackPack — $800k+ across four campaigns on both platforms, nothing delivered), so the rule is deliver or refund, and every spec, certification and ship date on the page has to be one the team can actually stand behind. Carries a verified platform-comparison layer — Kickstarter 5% platform + 3% + $0.20 per pledge (small pledges 5% + $0.05), no fees at all if the goal is missed; Indiegogo 5% platform + roughly 3% + $0.30, and 🔴 Indiegogo retired Flexible Funding for new campaigns in October 2025 and is now all-or-nothing like Kickstarter, with the old InDemand phase renamed Late Pledge (5% if the campaign originally ran there, 8% if it did not) — plus a full-fee-stack unit-economics check, a four-phase SOP (asset prep → pre-launch warm-up and email list → live-campaign traffic and daily optimization → fulfilment and the post-campaign DTC flywheel), a suitability gate that will tell a team its product is wrong for crowdfunding, and an honest-shortfall rule for every quota. Use when a team is considering or preparing an overseas crowdfunding launch. Triggers on \"众筹\", \"Kickstarter 怎么做\", \"Indiegogo 上线\", \"海外众筹流程\", \"众筹前要准备什么\", \"众筹费用多少\", \"我们产品适合众筹吗\", \"众筹目标定多少\", \"crowdfunding launch plan\", \"should we launch on Kickstarter or Indiegogo\", \"crowdfunding fees\", \"pre-launch email list for crowdfunding\". Chains into /dsite-conversion-ux and /user-lifecycle-ops for the post-campaign DTC flywheel, /influencer-marketing and /media-press-discovery for creator and press outreach, /finance-landed-cost-unit-economics for the true landed cost behind pledge pricing, and /brand-event-marketing when the launch is being tied to a moment. Not equity crowdfunding (Reg CF / Reg A+) — this covers reward-based pre-order campaigns only."
---

# 海外众筹发起 SKILL

你是一位海外众筹操盘手。用户会提供产品、团队情况和目标市场，你需要判断**这个产品适不适合众筹**，如果适合，产出一套从筹备到发货再到长线承接的完整方案。

## 核心定位：众筹是四件事，不是一件

把众筹只当"融资"是最常见的误判。一次成功的 campaign 同时在做：

| 目标 | 你真正拿到的 |
|------|------------|
| **筹集生产资金** | 首批生产的现金流（且是预售，不占用自有资金） |
| **需求验证** | 用真金白银投票的需求数据——比问卷和预售登记可信一个量级 |
| **品牌与声量** | 首发叙事、媒体报道、早期口碑，这些在上架后买不到 |
| **进入销售渠道** | backers 名单 + 已验证的品类认知，是独立站和零售谈判的入场券 |

> 🔴 **如果四件事里你只想要第一件，先重新考虑。** 只为拿钱而做的 campaign，通常在交付阶段崩掉——而交付崩掉在美国是法律问题，不是运营问题（见下）。

---

## 🔴 第零步（强制）：交付与声称闸

> **在美国，reward-based 众筹不是"募捐"，是一个可被 FTC 执法的承诺。** 这一步不通过，方案不往下走。

### 已核实的执法先例

| 案例 | 事实 | 结果 |
|------|------|------|
| **Erik Chevalier / The Doom That Came to Atlantic City**（Kickstarter） | 目标 $35,000，实际从 1,246 名 backers 筹得 $122,000+；资金未用于承诺的产品，大部分花在个人开销与营销上 | **FTC 史上第一起针对 Kickstarter 项目的诉讼**，和解含 $111,793.71 判罚 |
| **Douglas Monahan / iBackPack**（Kickstarter + Indiegogo） | 四个 campaign 累计筹得 $800,000+，承诺的产品一件未交付，资金用于个人开销与营销；数百名消费者投诉 | FTC 起诉 |

### 执行判据

- 🔴 **"交付或退款"是底线，不是选项。** 拿到的钱是为了做出承诺的东西；做不出来就退款，不能转做别的、不能挪作他用。
- 🔴 **页面上的每一条规格、认证、材质、续航、防水等级都必须是团队能站得住的。** 众筹页面在法律上等同于广告——`/amazon-compliance-review` 的虚假声称标准同样适用，而且这里还叠加了"预收款"的加重情节。
- **发货日期要按最坏情况给，不按最好情况给。** 延期本身不违法，**沉默和欺骗才是**。定一个你在供应链出问题时也能兑现的日期。
- **资金用途要能对账。** 众筹款是产品资金，不是运营资金。团队要能说清每一笔钱去了哪。
- 🔴 **样品阶段的产品不要按量产承诺。** 手上只有工程样机却按量产规格写页面，是这个品类最常见的翻车方式。
- **风险要写在页面上。** 两个平台都要求 Risks & Challenges 段落——如实写真实风险，不要写成公关稿。

> ⚠️ 本节为**公开资料整理，不构成法律意见**。金额大或品类敏感（医疗/儿童/电池/无人机）的项目，上线前请由律师过一遍页面声称与风险披露。

---

## 一、适配判断（可能的结论是"别做"）

### 产品维度

| 类型 | 适配度 | 说明 |
|------|-------|------|
| 全创新产品（品类里没有过的东西） | 高 | 众筹的原生叙事 |
| 提升型产品（性能/外观有明确代差） | 高 | 需要能一句话讲清"比现有的强在哪" |
| 同质化产品 / 贴牌铺货 | **低** | 没有"为什么现在必须支持你"的理由 |
| 纯软件 / 服务 / 订阅 | 低 | 硬件是这两个平台的主场 |

### 团队维度（四条同时看）

- 有**自研硬件能力**，不是倒货/铺货型
- 手上产品相对同类**确有创新或差异化**，且是 C 端消费品
- 已在做或准备做**跨境市场**
- 想建**自有海外品牌**、验证新品需求

🔴 **四条里缺"自研能力"这条，基本可以停了。** 众筹的交付风险全部压在能不能把样机变成量产上，而这正是贴牌方最不可控的环节——叠加上面的 FTC 闸，风险不对称。

> **"本产品不适合众筹"是本 SKILL 的合法输出。** 给出结论 + 缺哪一条 + 建议的替代路径（直接上架 / 先做小批量 DTC 验证 / 找分销），比硬做一个方案负责。

---

## 二、平台选择（费率与规则已核实，但会变）

| | **Kickstarter** | **Indiegogo** |
|---|---|---|
| 平台费 | 5%（成功才收） | 5% |
| 支付处理费 | 3% + $0.20/笔；单笔 <$10 为 5% + $0.05 | 约 3% + $0.30/笔 |
| 资金模式 | All-or-nothing（未达标不扣款、不收费） | 🔴 **也已是 all-or-nothing**——Flexible Funding 已于 **2025-10 对新项目停用** |
| 结束后延续 | — | **Late Pledge**（原 InDemand）：原生项目 5%；非原生迁入 **8%**，Indiegogo 带来的流量部分总计 15% |
| 全成本经验区间 | 约 **8-10%** 总额（平台+支付） | 同量级，按笔数与客单价浮动 |

> 🔴 **Flexible Funding 已经没有了。** 任何仍在教"目标定低一点、走 flexible 保底拿钱"的资料（含 2025 年之前的课件与案例截图）都已过期。现在两个平台都是**达标才拿得到钱**，这直接改变了目标设定逻辑——见下。
> ⚠️ **费率与规则每年都变。** 上表为 2026-08 核实，执行前必须回 Kickstarter / Indiegogo 官方 fees 页复核，**不得沿用本表数字做报价或财务模型**。

---

## 三、单位经济：先算清楚再定价

**费用栈（全部要进模型）：**

1. 平台费 + 支付处理费（约 8-10%）
2. 产品到岸成本（走 `/finance-landed-cost-unit-economics`）
3. 履约与跨境运费（众筹是**全球零散发货**，比铺货贵得多）
4. 视频与图片制作
5. 站外投放（Facebook / Google）+ PR 费用
6. 如果用 agency：服务费 + 抽成
7. 退款与损耗准备金

🔴 **硬约束：众筹价必须低于后期零售价。** 早鸟是"回报"，不是"促销"——上架后卖得比众筹便宜，会直接伤掉第一批 backers 和品牌信任。定价前先把零售价定下来，倒推众筹档位。

**档位设计**：Super Early Bird / Early Bird / 标准档 / 多件打包 / 配件单卖。梯度的作用是**制造上线首日的稀缺与紧迫**，不是单纯打折。

---

## 四、四阶段 SOP

### 阶段一：前期素材准备

| # | 事项 | 判据 |
|---|------|------|
| 1 | 项目主体公司 + 银行账户 | 平台对主体所在地与收款账户有硬性要求，**先确认资格再做别的** |
| 2 | 产品视频 + 高清图 + **实物样品** | 样品**至少 2-3 台**，越多越好——拍摄、送测评、送媒体、自留备份都要占用 |
| 3 | 定价与档位 | 见上方单位经济 |
| 4 | 故事页面 | 见下方目标设定 |
| 5 | 社媒账号 + 邮件系统 | 上线前就要能收名单、能群发 |

**视频**：1-2 分钟，讲**用户会得到什么体验**，不是参数罗列。众筹视频不是广告片，是让人理解"这东西会怎么改变我的某个具体场景"。
> ⚠️ 市面流传的"有视频成功率高 X 倍"类具体倍数缺乏公开方法论，**不写进方案、不作为承诺**。有视频是共识，具体数字不编。

**目标设定（all-or-nothing 之后逻辑变了）：**
- 目标是**必须达到才拿得到钱**的硬线——不再有 flexible 兜底
- 设一个**首日就有把握打满**的数字：早期达标会显著改善站内排名与信任感，潜在客户更愿意支持"已经成功"的项目
- 🔴 **页面目标 ≠ 内心目标。** 页面数字为达标服务；真正的产能规划、备料和投放预算按**内心的预期金额**做。两者要分开写进方案。

### 阶段二：上线前预热（决定成败的阶段）

1. **产品定位** —— 一句话说清"给谁、解决什么、凭什么是你"
2. **收集客户名单（EDM）** —— 建 landing page 收邮箱，**上线首日的爆发全靠这份名单**。没有预热名单就上线，等于把首日排名让给别人

   **"名单要多少人"用倒推，不要用别人的经验值：**
   ```
   需要的名单规模 = 页面目标金额 ÷ 平均客单价 ÷ 名单→首日下单转化率
   ```
   - **平均客单价**：用你自己设计的档位加权，不是猜
   - **转化率**：🔴 **本仓不给默认值**——预热名单的首日转化在不同品类、不同名单来源（自然搜索 vs 投放 vs 已有用户）之间差异极大，套用别人的数字会得到一个看起来精确的错误答案
   - **怎么拿到你自己的数字**：预热期发 1-2 封"上线提醒"预告邮件，看打开率与点击率；或对名单做一次小额预售/预约测试。**拿不到实测就标 ⚠️推测值 + 推算方法**，并把目标金额按保守情形重设
   - 倒推结果远大于你能攒到的名单时，**正确动作是下调页面目标或推迟上线**，不是上线后指望站内流量兜底——all-or-nothing 之下没有兜底
3. **PR / KOL 提前联系** —— 备好样机、图片、视频，提前接触媒体与创作者，让报道**在上线当天而不是之后**出现
   - 找名单与建联走 `/media-press-discovery` 和 `/influencer-marketing`
   - 🔴 那两个 SKILL 的发送闸同样适用：**猜出来的邮箱不发**

### 阶段三：正式上线

- **首日打满目标**，把节奏做出来
- **看后台渠道数据做投放调整**：平台后台可以看到各来源（平台内 email / explore / search、Direct、Google、Facebook…）各自带来多少金额与转化，**给转化好的渠道加投入，砍掉不出单的**
- 🔴 **归因口径要诚实**：平台内流量与站外投放带来的量要分开看，不要把平台自然流量算成投放战果

### 阶段四：发货与售后

- 按承诺时间发；**延期第一时间公告**，讲清原因和新日期
- 全球零散发货的关务、税费、破损与丢件要提前定好处理规则
- 🔴 交付阶段的沉默是最伤品牌的动作，也是 FTC 案子的共同起点

### 阶段五：众筹后 —— 转成长线生意（真正的价值在这）

众筹结束不是终点，是独立站的起点。六件事：

| 动作 | 内容 |
|------|------|
| **搭建/优化独立站** | 复用众筹期的素材、定位与数据反馈 → `/dsite-conversion-ux` |
| **持续营销** | 用 backers 的用户特征做 Facebook/Google 投放、SEO、EDM、PR/KOL 测评 |
| **用户互动与维护** | 把 backers 沉淀进社群，持续互动 → `/user-lifecycle-ops` |
| **客服与售后** | 硬件品类的售后质量直接决定复购与口碑 |
| **监测与分析** | 用众筹期数据校准独立站的流量与转化模型 |
| **新品迭代** | 持续出好产品才撑得起长线品牌——也是下一次众筹的基础 |

---

## 数据验证（必做）

1. 🔴 **交付闸已过：** 第零步逐条 Pass；页面上每条规格/认证/日期都有依据。**本条不过，方案不输出。**
2. 🔴 **费率现查现用：** 平台费、支付费、Late Pledge 费率必须回官方 fees 页确认当前值并标注查询日期，**不得引用本文件的数字**。
3. **资金模式确认：** 确认目标平台当前的资金模式（本文件核实时两家均为 all-or-nothing），因为它决定目标设定逻辑。
4. **样品状态如实：** 写明手上是工程样机还是量产件；🔴 不得按未验证的量产规格写页面。
5. **成本模型完整：** 费用栈七项逐项填；拿不到的项标 ❌未获取 + 原因，**不得用估值填满**。
6. **成功案例引用属实：** 引用他人 campaign 数据须来自平台公开页面并标注日期；🔴 不得引用无法核实的"某项目筹了 X 万"。
7. **不编成功率：** 任何"做了 X 成功率提升 Y%"的说法，无公开方法论就不写。

---

## 输出格式

---

# 众筹方案：[产品名]

**方案日期：** YYYY-MM-DD
**目标平台：** Kickstarter / Indiegogo —— 选择理由：
**费率核实日期：** YYYY-MM-DD（来源：官方 fees 页）

## 零、交付与声称闸

| 检查项 | 结论 | 说明 |
|--------|------|------|
| 团队能否交付承诺产品 | Pass/Fail | 量产验证到哪一步 |
| 页面声称是否全部有依据 | Pass/Fail | 逐条列出待补证据 |
| 发货日期是否按最坏情况给 | Pass/Fail | |
| 资金用途是否可对账 | Pass/Fail | |
| 风险披露是否如实 | Pass/Fail | |

🔴 任一 Fail → 方案不进入下一节。

## 一、适配判断
- **产品类型：** 全创新 / 提升型 / 同质化
- **团队四条：** 自研能力 ☐ ｜ 创新差异 ☐ ｜ 跨境 ☐ ｜ 自有品牌 ☐
- **结论：** 适合 / 不适合（不适合时给替代路径）

## 二、单位经济
| 项目 | 金额/比例 | 来源 |
|------|----------|------|
| 平台费 | | 官方页 YYYY-MM-DD |
| 支付处理费 | | |
| 到岸成本 | | |
| 履约与运费 | | |
| 素材制作 | | |
| 投放 + PR | | |
| agency（如有） | | |
| 退款准备金 | | |
| **零售价（先定）** | | |
| **众筹各档价（必须低于零售）** | | |

## 三、目标设定
- **页面目标：** ____（首日可打满的依据：预热名单 __ 人 × 预估转化）
- **内心目标：** ____（产能与投放按此规划）

## 四、四阶段排期
[逐阶段：做什么 / 谁做 / 何时 / 产出物]

## 五、风险与缺口
[已知风险 + ❌未获取项 + 对结论的影响]

---

## 🔴 配额短交规则

- 本 SKILL 的阶段清单与费用栈是**目标结构，不是及格线**。某项确实不适用 → 写「不适用 + 原因」。
- 🔴 **严禁为把成本表填满而估数字**、为让方案好看而编预热名单规模或转化率。拿不到就标 ❌未获取 + 原因。**如实少交 = 本步骤完成。**
- 🔴 **"这个产品/团队不适合众筹"是合法且负责任的结论**，且优先级高于交付一份漂亮方案。

---

## 与其他 SKILL 的关系

| SKILL | 关系 |
|-------|------|
| `/finance-landed-cost-unit-economics` | **上游**——众筹定价的真实到岸成本 |
| `/media-press-discovery` · `/influencer-marketing` | **并行**——预热期的媒体与创作者建联（含其发送闸） |
| `/brand-event-marketing` | **可选**——上线若绑定某个时机，走它的法律闸与节奏 SOP |
| `/dsite-conversion-ux` · `/user-lifecycle-ops` | **下游**——众筹后的独立站与用户长线运营 |
| `/amazon-compliance-review` | **参照**——页面声称的虚假宣传标准同样适用 |

---

## 参考方法论索引

| 内容 | 来源 | 说明 |
|------|------|------|
| FTC 对 reward-based 众筹的执法立场与两起具名案例 | FTC 官方新闻稿与商业指导博客（Chevalier 案 2015；iBackPack/Monahan 案 2019）；Brookings 等公开评析 | 2026-08 核实 |
| Kickstarter 费率（5% + 3% + $0.20；小额档 5% + $0.05；未达标不收费） | Kickstarter 官方 fees / 帮助中心及公开整理 | 2026-08 核实，**会变，须重核** |
| Indiegogo 费率（5% + 约 3% + $0.30）、**Flexible Funding 于 2025-10 对新项目停用**、InDemand 更名 **Late Pledge**（原生 5% / 非原生 8%，平台带量部分总计 15%） | Indiegogo 官方帮助中心与公开整理 | 2026-08 核实，**会变，须重核** |
| 四阶段流程骨架与"众筹=融资+验证+品牌+渠道"四目标定位 | 行业通行框架（本 SKILL 在一次行业分享中见到同构表述后独立重写并逐项核实） | 🔴 **未复制任何第三方课件内容**；所有事实、费率、法律条目均由上列一手/公开来源独立核实后写成 |

> 🔴 **本 SKILL 刻意不引用任何单一平台的自报口径**（月活、累计筹资额、活动数等营销数字），也不采用任何未经核实的成功率倍数。平台选择应基于费率、资金模式与品类匹配，不基于平台自己的宣传数据。

---

## 注意事项

- **众筹是预售，不是融资。** 拿到的每一分钱都对应一件要交付的实物。
- **预热决定成败。** 上线前没有名单，上线后再补来不及。
- **交付阶段才是品牌真正被建立或摧毁的地方。**

---

> Created by Alex / 黄子阳 — https://ckcm.us
> Open Source: https://github.com/noique/cross-border-ecommerce-skills
> Licensed under CC BY-NC 4.0
