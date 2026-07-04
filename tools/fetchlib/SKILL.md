# fetchlib — 合规抓取 waterfall（分层取页 + 自适应控速 + 后端自升级）

一个小而完整的**取页 waterfall**,给本仓库抓取类 skill 复用。核心思想(来自 2026 双源调研):**默认用最便宜的方案,只有当前层被真正拦截时才升级一层**(Markov 式状态机)。控速用 `api-pacer` + **AIMD**(慢加速/遇封猛砍)+ **熔断器**;全程合规优先。

> 基于两轮调研(多 Agent + Gemini Deep Research)的结论落地。`curl_cffi` 是免费 TLS 伪装主力;`cloudscraper`/`FlareSolverr`/`undetected-chromedriver` 已死/衰,不在其列。

## 分层 waterfall（便宜 → 贵,遇 block 才升级）

| Tier | 后端 | 能干什么 | 成本 | 本批状态 |
|---|---|---|---|---|
| L1 | **curl_cffi** | 真浏览器 TLS/JA3 伪装,过 TLS/header 层;**不跑 JS** | 免费 | ✅ 已实现(未装 curl_cffi 时优雅回退 urllib) |
| L2 | **jina**（r.jina.ai） | 渲染 JS → 干净 markdown | 免费* | ✅ 已实现(*商用条款自查) |
| L3 | **nodriver** | 反检测浏览器,过 Cloudflare JS 质询 | 免费(算力) | 🔌 批二 `register_backend('nodriver', fn)` |
| L4 | **managed** | 付费 unblocker(Bright Data 等),打 DataDome/Akamai | 付费 | 🔌 opt-in `Fetcher(managed=fn)` |

## 控制层

- **api-pacer**（同目录工具）：按响应头自适应 + full-jitter 退避。
- **AIMD**：每域请求速率"加增乘减"——成功慢慢提速,一遇封**猛砍一半**,自动逼近站点能容忍的上限。
- **CircuitBreaker**：某域连续被封 N 次 → **熔断冷却**(closed→open→half_open→closed),别再捶正在封你的站。
- **打点**：每次抓取写 JSONL(`url/tier/status/blocked/bytes/ms`),用来判断"免费层什么时候失效、该不该上付费"。

## 快速用法

```python
from fetchlib import Fetcher          # 需同时能 import api_pacer（同在 tools/）

f = Fetcher(tiers=("curl_cffi", "jina"), respect_robots=True,
            jina_key=None, log_path="fetch_log.jsonl")
r = f.fetch("https://example.com/product/123")
if r["tier"]:                          # None = 各层都被拦
    parse(r["text"])                   # curl_cffi 返回 HTML；jina 返回 markdown
```

插入批二后端(nodriver / 付费 unblocker):

```python
import fetchlib
fetchlib.register_backend("nodriver", my_nodriver_fetch)   # fn(url, **kw) -> (status, body, headers)
f = Fetcher(tiers=("curl_cffi", "jina", "nodriver"),
            managed=my_brightdata_fetch)                    # 追加付费 L4，opt-in
```

自测(无网络,验证 AIMD/熔断/block 检测/升级逻辑):`PYTHONPATH=../api-pacer python3 fetchlib.py`。

## 被哪些 skill 使用（adoption）

| Skill | 怎么接 |
|---|---|
| `serp-content-teardown` | `fetch_competitors.py` 把裸 `curl` 换成 `Fetcher(tiers=("curl_cffi",))`,产物 manifest/flags 不变 |
| `media-press-discovery` | Muckrack 是 JS 质询(curl_cffi 已证 403)→ 批二加 `nodriver` 后端 |
| `tools/trustpilot` | 评论多为 SSR,先试 `curl_cffi`;能收就砍多线程 Selenium |
| `outbound-prospecting` | 打 SERP/搜索前挂 `Fetcher` + api-pacer |
| `reddit-voc` | 只读研究:优先官方 API(PRAW),HTML 兜底走 fetchlib |

> 现有 skill **可选接入**——它们已能独立跑;本工具是"想更稳/更省"时的 drop-in,不改其核心逻辑。

## 依赖

- **必需**：`tools/api-pacer`(同目录,`api_pacer.py`)。
- **可选**：`curl_cffi`（`pip install curl_cffi`;不装则 L1 回退到无伪装的 urllib,功能降级但可跑)。
- 纯 stdlib 之外无强依赖;L2 用 stdlib `urllib` 调 r.jina.ai。

## 诚实边界 & 合规红线

- **只做合规研究抓取**:默认 honor robots.txt;**不破解访问壁垒(no access-barrier defeat)、不换 IP、不伪造指纹、不解 CAPTCHA**。这些留给上层/付费方案,且需自行评估合法性。
- **不服务** ToS 违规自动化(刷票/水帖/养号/规避封禁)。
- **PII 是调用方的责任**:抓 VOC 前后自行做 PII 脱敏(GDPR/CIPA),遵守最小化。
- **代理**:若接付费代理,**只用 KYC/知情同意审计过的**供应商(2026 已有灰产代理网络被查封);优先公开+登出+无 PII 的目标。
- **本土法律**:注意中国《反不正当竞争法》(2025-10-15)第 13 条对"非法数据抓取/规避技术管理措施"的规定。
- 免费层会失效、反爬会更新——**打点日志 + 熔断**就是让你及时发现并降级,而不是硬刚。

---
> Created by Alex / 黄子阳 — https://ckcm.us
> Open Source: https://github.com/noique/cross-border-ecommerce-skills
> Licensed under CC BY-NC 4.0
