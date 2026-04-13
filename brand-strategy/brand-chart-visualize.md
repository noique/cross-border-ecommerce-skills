# 品牌报告数据可视化 SKILL

你是一位数据可视化专家。用户已完成品牌战略系列报告（01-08），你需要读取报告中的关键数据，调用 AntV API 生成专业图表，并将图表嵌入对应报告。

## 执行模式：batch（独立执行，读取已有报告生成图表）

## API 接口

```
POST https://antv-studio.alipay.com/api/gpt-vis
Content-Type: application/json

请求体必须包含 "source": "chart-visualization-skills"
返回：{"success":true,"resultObj":"https://图片URL"}
```

## 输入要求

用户提供报告所在目录路径（如 `~/Downloads/Pickleball-Apparel调研/`），本 SKILL 自动：
1. 读取目录下所有 .md 报告
2. 从报告中提取可视化数据
3. 调用 AntV API 生成图表
4. 将图表图片下载到 `{目录}/charts/` 子文件夹
5. 在报告对应位置插入 `![标题](charts/文件名.png)` 引用

## 图表生成清单

### 基础图表（从单份报告提取数据）

| 序号 | 图表 | 类型 | 数据来源 | 插入报告 |
|------|------|------|---------|---------|
| 1 | 可行性八维度雷达图 | `radar` | 00 或 08 中的八维度评分表 | 00-可行性结论 |
| 2 | VOC 机会分数条形图 | `bar` | 01 中的 VOC 散点矩阵表 | 01-市场扫描 |
| 3 | 赛道 GTM 飞轮对比雷达图 | `radar` | 02 中 Top 3 赛道的四维度得分 | 02-赛道假设 |
| 4 | 5D 评分对比雷达图 | `radar` | 03 中各赛道的 D1-D5 得分 | 03-深度验证 |
| 5 | 单位经济瀑布图 | `waterfall` | 04 中的单位经济模型 | 04-品牌战略 |
| 6 | 渠道预算分配饼图 | `pie` | 05 中的渠道预算占比 | 05-IMC 框架 |

### 高级图表（跨报告提取或需要计算）

| 序号 | 图表 | 类型 | 数据来源 | 插入报告 |
|------|------|------|---------|---------|
| 7 | 竞品价格带柱状图 | `column` | 01 中竞品价格 + 04 中自身定价 | 01-市场扫描 |
| 8 | SEO 关键词机会散点矩阵 | `scatter` | 06 中的关键词 KD 和搜索量 | 06-SEO 调研 |
| 9 | 12 月流量增长预测折线图 | `line` | 05 中的 SEO 流量里程碑 | 05-IMC 框架 |
| 10 | 品类扩展路径桑基图 | `sankey` | 04 中的 Phase 1→2→3 扩展路径 | 04-品牌战略 |

## 执行流程

### 第一步：读取报告并提取数据

依次读取目录下的报告文件，从表格中提取数据点：

**提取规则：**
- 评分表 → 提取维度名称 + 分数
- 价格数据 → 提取品牌名 + 价格 + 分组（价格带）
- VOC 矩阵 → 提取功能卖点 + 机会分数
- GTM 飞轮 → 提取赛道名 + 四维度得分
- 单位经济 → 提取各项成本明细
- 关键词 → 提取关键词 + KD + 搜索量

### 第二步：构造 API 请求并生成图表

对每个图表执行：

```bash
# 1. 构造请求
DATA='{"type":"[图表类型]","source":"chart-visualization-skills","title":"[标题]","data":[数据数组],"theme":"academy","width":700,"height":500}'

# 2. 调用 API
RESULT=$(curl -s -X POST https://antv-studio.alipay.com/api/gpt-vis \
  -H "Content-Type: application/json" \
  -d "$DATA")

# 3. 提取图片 URL
URL=$(echo $RESULT | python3 -c "import sys,json; print(json.load(sys.stdin)['resultObj'])")

# 4. 下载图片
curl -s "$URL" -o "{目录}/charts/{编号}-{类型}-{名称}.png"
```

### 第三步：插入图表到报告

在每份报告的对应位置插入 Markdown 图片引用：
```markdown
![图表标题](charts/01-radar-feasibility.png)
```

**插入位置规则：**
- 评分表 → 紧跟表格后
- 对比数据 → 紧跟对比表后
- 财务数据 → 紧跟财务模型后
- 不要替换原有表格，图表是**补充**不是替代

### 第四步：验证

- 检查所有图片文件是否存在且大小 > 10KB
- 检查报告中的图片引用路径是否正确
- 如某个 API 调用失败，在报告中标注"图表生成失败，请查看数据表格"

## 各图表类型 data 格式速查

| 类型 | data 格式 | 关键参数 |
|------|---------|---------|
| `radar` | `[{name, value, group}]` | group 区分不同系列 |
| `bar` | `[{category, value, group?}]` | 横向条形图 |
| `column` | `[{category, value, group?}]` | 纵向柱状图 |
| `pie` | `[{category, value}]` | 可加 innerRadius 做环形 |
| `waterfall` | `[{category, value?, isTotal?}]` | 最后一项 isTotal:true |
| `scatter` | `[{x, y, group?}]` | group 区分分类 |
| `line` | `[{time, value, group?}]` | time 为 X 轴 |
| `sankey` | `[{source, target, value}]` | 流向图 |
| `funnel` | `[{category, value}]` | 漏斗图 |

## 通用参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| theme | "academy" | 推荐使用 academy 主题（学术风格，适合报告） |
| width | 700 | 图表宽度（px） |
| height | 500 | 图表高度（px） |
| title | "" | 图表标题 |
| axisXTitle | "" | X 轴标题（柱状/条形/散点图适用） |
| axisYTitle | "" | Y 轴标题 |

## 输出

完成后输出图表生成报告：

```
=== 图表生成报告 ===
✅ 01-radar-feasibility.png (XXX KB) → 插入 00-可行性结论.md
✅ 02-column-price-bands.png (XXX KB) → 插入 01-市场扫描.md
✅ 03-bar-voc-opportunity.png (XXX KB) → 插入 01-市场扫描.md
...
❌ XX-xxx.png — API 调用失败（原因）

总计：X/10 图表生成成功
```

## 注意事项

- API 返回的是图片 URL，需要 curl 下载为本地 PNG 文件
- 图表文件统一存放在 `{报告目录}/charts/` 子文件夹
- Markdown 中使用相对路径引用：`charts/文件名.png`
- 如果报告中已有同名图表引用，跳过不重复生成
- theme 统一用 "academy"，保持报告风格一致
- 图表是数据的**可视化补充**，不替代原有表格数据

---

---

> Created by Alex / 黄子阳 — https://ckcm.us
> Open Source: https://github.com/noique/cross-border-ecommerce-skills
> Licensed under CC BY-NC 4.0
