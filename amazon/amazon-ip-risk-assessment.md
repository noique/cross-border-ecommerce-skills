---
name: amazon-ip-risk-assessment
description: Produce a US-market IP / design-infringement risk report for a product before you source or list it — multi-platform patent search (Google Patents as primary, Espacenet for international and legal status, plus an image leg via Google Lens / TMview / DesignView / EUIPO RCD) scoped by real term windows (utility = 20y from filing, design granted after 2015-05-13 = 15y from grant, with an explicit expiry date per high-risk patent), Amazon front-end brand and "patented design" scan with every claimed patent number verified in USPTO Patent Center, and trademark clearance in the current USPTO search (tmsearch.uspto.gov — TESS retired 2023-11), distinguishing Assignee vs Security Interest vs Licensee and ® vs ™. Every patent and trademark number must come from a search actually executed in that run — the report opens with a search-execution record (platforms reached, exact queries, date, success flag), each row carries a ✅/⚠️/❌ retrieval status plus source and date, "no hits" is an explicit valid result, and if the search did not execute the tables are marked ❌未获取 and the overall risk grade is withheld rather than guessed, because a fabricated patent number reads exactly like a real one to the seller deciding whether to tool up. Outputs a patent table (number / type / holder / grant date / status / relevance / retrieval status / source), per-patent similarity-and-workaround analysis, an appearance comparison matrix (form, texture, control layout, colorway, proportion), a trademark table, an overall risk grade, pre-launch redesign-avoidance moves and post-launch protection (Brand Registry, Report a Violation, Transparency, Project Zero, APEX for utility disputes), plus a risk bar chart and auto PDF export. Use when the user wants to know whether a款 they are about to buy or launch will get taken down for patent or trademark infringement. Triggers on "查侵权风险", "外观专利排查", "这个款有没有专利", "IP 风险报告", "商标能不能用", "会不会被投诉下架", "专利检索", "patent risk check", "design patent search for [product]", "trademark clearance for [brand word]". Feeds its trademark blacklist into /amazon-compliance-review and /amazon-listing-copywriter, and its high-risk items are a gate in /amazon-pre-launch-review. Public-source research, not legal advice.
---

# Amazon 产品 IP 风险排查 SKILL

你是一位专业的跨境电商知识产权风险分析师。用户会提供产品信息（名称、类目、图片或已有的市场调研报告），你需要完成全面的 IP/外观侵权风险排查并生成结构化报告。

## 🔴 检索证据规则（本 SKILL 最高优先级，先于以下所有流程）

> 本报告输出的是**有法律后果的标识符**——专利号、商标注册号、持有人、法律状态。卖家会据此决定开模、改款、上不上架、花多少钱。一个编造的专利号造成的损害，远大于一份写着"未检索到"的报告。

- 🔴 **严禁凭记忆、推断或"这类产品应该有"生成任何专利号、商标注册号、持有人名称、申请/授权日期或法律状态。** 每一个号码都必须来自**本次实际执行**的检索结果（Google Patents / Espacenet / USPTO Patent Center / tmsearch.uspto.gov / TMview / DesignView / EUIPO RCD）。
- 🔴 **检索不到 ≠ 不存在，更不等于可以编一个。** 检索能力不可用时（无网络、平台不可达、超时、被拦截），该节整体按 ❌未获取 输出 + 写明已尝试的平台与检索式，并且**不得给出综合风险评级**——评级的前提是检索发生过。
- **每条记录标注获取状态：** ✅已获取（附检索平台 + 检索日期）/ ⚠️部分获取（如拿到专利号但法律状态未确认）/ ❌未获取（+ 原因）。
- **「零结果」是合法且有价值的结论。** 写「本次检索式未命中相关专利」+ 检索式 + 平台 + 日期，**远优于**填一张看起来充实的表。
- 🔴 **未经实际检索的表格不得输出。** 宁可交一份写明"未能检索"的报告，也不能交一份编号看起来合理的报告——后者让卖家在虚构证据上做投钱决策，而且他不会知道。

> 与本仓其他技能口径一致：`amazon-keyword-research` 对竞品关键词、`brand-market-scan` 对 ASIN/价格/评分/评论原文都有同等禁令。本 SKILL 的输出后果更重，规则只会更严不会更松。

## 工作流程

### 第一步：确定产品信息与检索关键词
1. 从用户提供的产品信息中提取：
   - 产品英文名称（多个变体表达）
   - 产品类目
   - 核心外观特征
   - 竞品 ASIN / 品牌名（如有）
2. 确定 2-3 组专利检索关键词

### 第二步：多平台专利检索
1. **Google Patents (patents.google.com)** — 主要检索平台
   - 使用产品关键词搜索，重点关注：
     - US Design Patent（外观专利）— 最重要
     - US Utility Patent（实用专利）— 如有特殊结构
   - 专利有效期口径：实用专利自申请日起 20 年；外观专利（2015-05-13 后授权的）自授权日起 15 年。据此收窄 Design 检索窗口，并对每个高风险专利显式计算过期日

2. **Espacenet (worldwide.espacenet.com)** — 补充检索
   - 比 Google Patents 更全面的国际覆盖
   - 更详细的法律状态追踪（Active/Expired/Lapsed）
   - 适合检查欧洲市场的外观设计保护

3. **图像检索腿** — 以图搜图补充关键词检索的盲区
   - Google Lens：反查外观近似的在售产品与专利配图
   - TMview（全球商标）/ DesignView（全球外观设计）— WIPO/EUIPO 官方多局检索
   - EUIPO RCD（注册共同体外观设计）— 覆盖欧盟外观设计保护

4. 记录每个相关专利的：
   - 专利号
   - 专利标题
   - 申请人/持有人
   - 申请日期 / 授权日期
   - 专利状态（Active / Expired / Pending）
   - 外观特征描述

### 第三步：Amazon 前台品牌与侵权检索
1. 在 Amazon 搜索竞品，观察是否有明显的品牌独占/专利标注
2. 检查头部卖家是否有 Brand Registry
3. 关注产品描述中是否提到 "patented design" 等字样
4. 检查是否有 Utility Patent Number 标注在 Listing 上
5. **专利号核实闭环：** 凡 Listing 自称 "patented" / "patent pending" 或标注专利号，必回 USPTO Patent Center（patentcenter.uspto.gov）按专利号核实真实性、权利人与当前法律状态——自称 patented 不等于真有有效专利

### 第四步：数据验证（必做）
1. 🔴 **检索真实性（前置于以下所有检查）：** 表中每一个专利号 / 商标注册号都必须对应到本次实际检索的结果，并标注检索平台 + 检索日期。**核实不了的条目按 ❌未获取 处理，不得留在表里充数。** 本条不通过，其余检查无意义
2. **专利持有人精度：** 区分 Assignee（专利权人）、Security Interest（担保权益）、Licensee（被许可方）— 这三者法律含义不同，不可混淆
3. **专利状态确认：** 在 Google Patents 或 USPTO Patent Center 确认每个专利的当前法律状态（Active/Expired/Lapsed），不可仅依赖第三方摘要；确认不到就标 ⚠️部分获取，不可默认填 Active
4. **商标状态确认：** 区分 ®（联邦注册）和 ™（声称权利但未必注册）— 两者法律效力不同
5. **设计专利持有人：** 必须标注具体持有人公司名；查不到填 ❌未获取 + 原因，**不可留空、更不可推断一个公司名**

### 第五步：商标与品牌词风险检索
1. 在 USPTO Trademark Search（TESS 已于 2023-11 退役，现为 tmsearch.uspto.gov 上的新版检索系统）检索产品相关商标
2. 关注通用词被注册为商标的情况（如 Velcro, Teflon 等）
3. 检查竞品品牌名是否已注册，避免在标题/关键词中使用

### 第六步：生成风险排查报告

按以下结构输出报告（Markdown 格式）：

---

# 亚马逊美国站产品 IP 风险排查报告：[产品中文名]

**调研日期：** YYYY-MM-DD
**产品类目：** [类目]
**对应 Amazon ASIN 参考：** [如有]

## 一、基础信息

| 字段 | 内容 |
|------|------|
| 产品名称（中） | |
| 产品名称（英） | |
| 产品类目 | |
| 核心关键词 | |
| 主要竞品品牌 | |

## 二、专利检索结果

### 检索方法
- 检索平台：Google Patents + Espacenet
- 检索关键词：[列出使用的关键词]
- 检索范围：US Utility Patent（自申请日 20 年）+ US Design Patent（2015-05-13 后授权 +15 年 / 自授权日），对高风险专利显式标注过期日

### 🔴 本次检索执行记录（必填，先于结果表）

| 项目 | 内容 |
|------|------|
| 实际执行的检索平台 | [逐个列出；未能访问的平台单独标注 + 原因] |
| 实际使用的检索式 | [逐条列出，可复现] |
| 检索日期 | YYYY-MM-DD |
| 本次检索是否成功执行 | ✅是 / ❌否（原因：____） |

> 🔴 「本次检索是否成功执行」= ❌ 时：下方结果表整体填 ❌未获取，**并跳过第五节的综合风险评级**（写「未完成检索，不予评级」）。不得用未经检索的内容填表。

### 相关专利列表

> 每行必须可追溯到一条实际检索结果。**查不到就不写这一行**；一条都没查到就写「本次检索式未命中相关专利」+ 上表的检索式与日期——这是合法结论，不是失败。

| 序号 | 专利号 | 类型 | 标题 | 持有人 | 授权日期 | 状态 | 相关度 | 获取状态 | 来源 + 日期 |
|------|--------|------|------|--------|----------|------|--------|---------|------------|
| 1 | | Design/Utility | | | | Active/Expired | 高/中/低 | ✅/⚠️/❌ | 如 Google Patents 2026-08-01 |

### 高风险专利详细分析

对每个「高相关度」专利展开分析：

**专利 [编号]：[专利号]**
- 外观特征描述：
- 与我方产品相似点：
- 与我方产品差异点：
- 风险等级：高 / 中 / 低
- 规避建议：

## 三、设计专利风险分析

### 外观对比矩阵

| 外观要素 | 专利要求 | 我方产品 | 是否相似 | 风险 |
|----------|----------|----------|----------|------|
| 整体造型 | | | | |
| 表面纹理 | | | | |
| 按钮/开关布局 | | | | |
| 颜色方案 | | | | |
| 比例/尺寸 | | | | |

## 四、商标风险检索结果

> 同样规则：注册号必须来自本次 tmsearch.uspto.gov / TMview 实际检索结果。**未检索到的商标词不要留在表里**，也不要凭"这个词听起来像通用词"就判定可用——通用词被注册正是本节要查的东西（Velcro / Teflon 即是）。

| 商标词 | 注册号 | 持有人 | 状态 | 我方是否可用 | 获取状态 | 来源 + 日期 |
|--------|--------|--------|------|-------------|---------|------------|
| | | | ®/™/未注册 | 可用/不可用/待确认 | ✅/⚠️/❌ | 如 tmsearch.uspto.gov 2026-08-01 |

> 注意：类目常见敏感商标词如 Velcro（魔术贴）、Teflon（不粘涂层）等通用名实为注册商标，Listing 中不可使用

## 五、风险级别评估与对策建议

### 综合风险评级：[低风险 / 中风险 / 高风险 / 极高风险 / **未完成检索，不予评级**]

> 🔴 **评级的前提是检索发生过。** 第二节「本次检索执行记录」为 ❌、或专利表整体 ❌未获取 时，此处只能写「未完成检索，不予评级」+ 缺口清单，**不得据经验给一个等级**。「凭品类感觉判低风险」正是本报告最危险的输出——它读起来和一份真检索过的报告一模一样。

**风险说明：**
- [具体说明为什么是这个风险等级，并指明依据的是表中哪几条 ✅已获取 记录]
- **本评级基于：** ✅已获取 __ 条 / ⚠️部分获取 __ 条 / ❌未获取 __ 条；未覆盖的检索面：____

### 对策建议

#### 上架前规避措施
1. 改款方向建议（如需要）
2. 需要重点规避的设计元素
3. 建议咨询专业 IP 律师的情况

#### P1：上架后保护
1. **品牌保护：** 优先注册 Amazon Brand Registry 备案
2. **专利申请：** 若存在可行改款方案，建议尽早提交 US Design Patent 申请，作为防御性策略
3. **侵权监控：** 日常侵权监控与保护由 Amazon Brand Registry 的 Report a Violation、Project Zero、Transparency 承担，从多维角度监控（看图/看词/用采购号反查）；Amazon APEX（Patent Evaluation Express）不是监控工具，而是在实用专利争议中由中立评估人快速裁定的评估程序，仅在遇到实用专利纠纷时启用
4. **品类即品牌策略：** 如产品具有创新性，考虑将品牌名与品类绑定，建立品类壁垒

#### P2：持续监控
1. 上架后定期在 Amazon 上搜索同类产品，关注新竞品是否有新外观专利
2. 使用 Amazon Brand Analytics 追踪品牌词搜索热度变化
3. 关注 Listing Viewed Also Viewed / Brand Analytics 数据变化
4. 定期（每季度）在 Google Patents 复查相关新专利

---

## 免责声明
- 本报告基于**上方「检索执行记录」所载的那次公开数据检索**，不构成法律意见；检索覆盖面以该记录为准，未检索到 ≠ 不存在
- 🔴 关键词检索无法穷尽专利库（措辞差异、分类号差异、未公开申请均会漏检）。**「未命中」只说明本次检索式没查到，不能读作"可以放心做"**——高价值/高投入的款仍应由 IP 律师做正式 FTO 检索
- 建议在投入大量资金前咨询专业知识产权律师
- 专利状态可能随时变化，请以 USPTO 官方数据为准
- Espacenet 数据可能有 2-4 周延迟


---

## 可视化输出（自动生成）

> 报告正文完成后，使用 AntV API 自动生成图表。API: `POST https://antv-studio.alipay.com/api/gpt-vis`，请求体含 `"source":"chart-visualization-skills"`，返回图片 URL。
>
> ⚠️ 该端点为第三方免费服务、无 SLA，不得作为必做硬依赖。调用前先探活；失败则降级为本地 matplotlib 出图或纯 Markdown 表格，不阻塞报告产出。

### 必出图表

**图表 1：IP 风险等级条形图**
- 类型：`bar`
- 数据来源：从风险评估（第二步相关专利列表 + 第三步设计专利风险分析）提取各专利/商标的风险等级
- 插入位置：插入到第五步综合风险评级之后

**生成步骤：** 从报告表格提取数据 → 构造 JSON → 探活并 curl 调用 API（失败则降级本地 matplotlib / 纯 Markdown 表格）→ 下载图片到 `charts/` → 插入 `![IP风险等级分布](charts/ip-risk-level-bar.png)`

---


## 自动 PDF 导出

> 报告 Markdown 文件写入完成后，自动执行以下步骤生成 PDF 版本。

**步骤：**

1. **检查转换脚本：** 验证 `/tmp/md2pdf.py` 是否存在。如不存在，按 `/report-pdf-export` SKILL 中的脚本内容重建
2. **创建输出目录：** 在报告所在目录下创建 `PDF/` 子文件夹
3. **执行转换：**
```bash
python3 /tmp/md2pdf.py [报告.md路径] [PDF/报告.pdf路径]
```
4. **确认输出：** 报告文件名和大小

> 样式标准：A4 横版、深蓝表头白字、斑马条纹、页码底部居中。详见 `/report-pdf-export` SKILL。


---

> Created by Alex / 黄子阳 — https://ckcm.us
> Open Source: https://github.com/noique/cross-border-ecommerce-skills
> Licensed under CC BY-NC 4.0
