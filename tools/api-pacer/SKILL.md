# api-pacer — 礼貌抓取节奏 / 自适应限速 + full-jitter 退避

一个极简、零第三方依赖的**请求配速器**,给本仓库的抓取 / 打 API 类 skill 复用。它**按服务器自己的 rate-limit 响应头**来配速(拿不到头就退回一个配置的 requests-per-second 预算),碰到 `429 / 503 / Retry-After` 时做 AWS 式 **full-jitter 指数退避**。

## 为什么不是"高斯延迟 / 随机 sleep"

常见误区是"用高斯/随机延迟让爬虫像人以躲检测"。真相:

- 平台**不会拟合检验**你的延迟分布是不是钟形;真正触发限流/封禁的是**总吞吐 vs 官方限额、账号/IP/OAuth 卫生、宏观规律(24/7 不睡、完美等间距)**。
- 因此最优不是"选一个更好的分布",而是**读真实预算**(响应头 `x-ratelimit-remaining / reset`)按预算配速。
- 唯一"抖动真正有用"的地方是**重试风暴**,而业界结论(AWS full jitter)里赢家是 **uniform(0, cap)**,不是高斯。

本工具就是把这两点落地:**自适应配速(读头)+ full-jitter 退避(uniform)**。

## 何时用

任何脚本化、会**反复打同一 API / 反复抓同一站**的 skill:`reddit-voc`、`serp-content-teardown`(抓竞品文章)、`media-press-discovery`(多后端 fetcher)、`tools/trustpilot`(翻页)、`outbound-prospecting`(SerpAPI / 搜索引擎)。
**不适用**:吃本地 Semrush xlsx 的 skill(不抓网);走 agent 侧 WebFetch 的 skill(限速在对方手里)。

## 快速用法

```python
from api_pacer import Pacer, polite_get
import requests

s = requests.Session()
p = Pacer(rps=1.0, headers="reddit", safety=0.8)   # headers: reddit / github / generic
for url in urls:
    resp = polite_get(s, url, p)                   # 自动 wait + 429/503 退避 + 重试
    if resp.status_code == 200:
        handle(resp)
```

手动循环(需要自己控重试时):

```python
p = Pacer(rps=2.0, headers="generic")
for url in urls:
    p.wait()                                        # 请求前 sleep（full jitter，按预算）
    resp = s.get(url)
    if p.on_response(resp.status_code, resp.headers, resp.headers.get("retry-after")):
        continue                                    # 命中限流：已退避，重试
    handle(resp)
```

**PRAW(Reddit 官方 API)**:PRAW 内部已按官方 ~100 QPM 限速,本工具作为**额外礼貌层**——在每次 `.top()/.new()` 迭代处理后 `p.wait()`,把负载摊开、避免打满;真正的额度控制交给 PRAW + 响应头。

## API

- `Pacer(rps=1.0, safety=0.8, headers="generic", reset_is_epoch=None, max_backoff=60.0, min_sleep=0.0)`
- `p.update(headers)` — 喂响应头,更新剩余额度/重置时间。
- `p.wait()` — 请求前 sleep;有预算则把"剩余额度铺满剩余窗口",full jitter。
- `p.on_response(status, headers=None, retry_after=None) -> bool` — 更新预算;命中 `429/503/Retry-After` 则 full-jitter 退避并返回 `True`(该重试)。
- `polite_get(session, url, pacer, max_retries=5, **kw)` — `requests` 版一体化 GET(配速+退避+重试)。
- `headers` 预设:`reddit`(reset=秒)/ `github`(reset=epoch)/ `generic`;其它 API 可传 `reset_is_epoch` 覆盖。

自测(无网络):`python3 api_pacer.py`。

## 被哪些 skill 使用

| Skill | 接入点 |
|------|--------|
| `reddit-voc` | PRAW/请求迭代处 `wait()`;见 `voc-tools/reddit-voc/references/rate-limiting.md` |
| `serp-content-teardown` | `scripts/fetch_competitors.py` 抓竞品文章前 `polite_get` |
| `media-press-discovery` | `_fetcher.py` 各后端前挂 pacer |
| `tools/trustpilot` | Selenium 翻页之间用 `wait()` 的延迟逻辑(非 requests,取其配速) |
| `outbound-prospecting` | 打 SerpAPI / 搜索引擎前配速,防封 |

> 现有 skill 是**可选接入**——它们已能独立跑;本工具是"想更稳/更礼貌"时的 drop-in,不改其核心逻辑。

## 诚实边界 & 合规红线

- **正当用途**:遵守公开限额、避免 thundering-herd、做只读研究 / 数据采集时当个好 API 公民。
- **不适用于**违反平台 ToS 的自动化——**刷票 / 水帖 / 养小号矩阵 / 规避封禁**。让机器人"像人"以躲检测属操纵行为,本工具不服务于此。
- 配速≠反爬:本工具**不打反爬、不换 IP、不伪造指纹**;强反爬站(Cloudflare/LinkedIn/Trustpilot)仍需各自的代理/反爬方案,本工具只负责"节奏"。
- `rps` / `safety` / `max_backoff` 是**保守默认**,按各 API 官方限额自行核实调整(限额会变)。

---
> Created by Alex / 黄子阳 — https://ckcm.us
> Open Source: https://github.com/noique/cross-border-ecommerce-skills
> Licensed under CC BY-NC 4.0
