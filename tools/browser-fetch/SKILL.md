# browser-fetch — 共享可选浏览器渲染后端（fetchlib L3）

把"**真浏览器渲染 + 可选代理**"能力(和 `tools/trustpilot` 里那套 Selenium 一个路子)提成一个**可复用的共享后端**,直接当 `fetchlib` 的 **L3** 挂上——多个 skill 不再各写一套浏览器。**引擎可插拔,默认 Selenium。**

## 诚实定位（据 2026-06 实测,数据中心 IP、无代理)

| 目标 | curl_cffi | Jina | **本工具(Selenium)** | nodriver |
|---|---|---|---|---|
| Trustpilot | ❌403 | ✅ | ✅ **真内容 1008k** | ⚠️ 薄 6k |
| Cloudflare 质询 / Muckrack / G2 | ❌403 | ❌ | ❌ 卡质询页 | ❌ 卡质询页 |

- **定位 = "JS 渲染 + 中等防护(Trustpilot 级)"**:它能拿下 curl_cffi 渲染不了的站。
- **不是反爬银弹**:从数据中心 IP,连真浏览器(Selenium/nodriver)也过不了 Cloudflare Managed Challenge / DataDome 堡垒。**那些要住宅 IP(+ 或 Camoufox/Scrapling 的 Turnstile solver)或付费 unblocker**——不是换个更炫的浏览器库能解决的。
- ⇒ **默认用已验证的 Selenium**;`nodriver` / `camoufox` / `scrapling` 作 opt-in 引擎,**先在住宅 IP 上本地比测再信**。

## 用法

**当 fetchlib 的 L3 后端(推荐):**
```python
import fetchlib, browser_fetch
fetchlib.register_backend("browser", browser_fetch.as_fetchlib_backend(engine="selenium", proxy=None))
f = fetchlib.Fetcher(tiers=("curl_cffi", "jina", "browser"))   # curl_cffi/Jina 拿不下才升级到浏览器
```

**独立用:**
```python
from browser_fetch import browser_fetch
status, html, headers = browser_fetch("https://example.com/spa", engine="selenium",
                                       proxy="http://host:port", headless=True, wait=6)
# 检测到质询页会归一化成 status=403，让 fetchlib 正确判 blocked
```

**插入别的引擎(等有住宅 IP 再测):**
```python
import browser_fetch
browser_fetch.register_engine("nodriver", my_nodriver_fn)   # fn(url, proxy=, headless=, ...) -> (status, body, headers)
```

自测(无浏览器/网络,验证 block 检测 + 引擎注册 + fetchlib 适配):`python3 browser_fetch.py`。

## 引擎现状

| 引擎 | 状态 | 说明 |
|---|---|---|
| `selenium` | ✅ 内置 | 已验证拿下 Trustpilot;authed/住宅代理需配 `selenium-wire`(如 trustpilot 那样) |
| `nodriver` / `camoufox` / `scrapling` | 🔌 `register_engine` 可插 | 更隐蔽,但**要住宅 IP 才有意义**;实测数据中心 IP 下同样过不了堡垒,先本地比测 |

## 被哪些 skill 使用（adoption,均 opt-in）

| Skill | 怎么接 |
|---|---|
| 任意需要 **JS 渲染**的抓取 | 挂成 fetchlib 的 `browser` L3,curl_cffi/Jina 失败才升级 |
| `media-press-discovery` | Muckrack 是 Cloudflare 堡垒 → **即使本工具也需住宅 IP**;有住宅代理时 `proxy=` 再接 |
| `tools/trustpilot` | **保持现有 Selenium 不动**;本工具是给"想复用浏览器能力的其它 skill",不替换它 |

> **不碰 trustpilot**:平行新模块,接受一点重复;以后想 DRY 再让 trustpilot 反过来用它,那是另说。

## 依赖

- **可选**:`selenium`(`pip install selenium`,4.6+ 自带 Selenium Manager 下驱动)+ 本机 Chrome。不装则只有引擎注册/适配逻辑可跑(懒加载)。
- 与 `fetchlib` 搭配用(它负责 waterfall / 限速 / 熔断 / 合规)。

## 诚实边界 & 合规红线（美国运营)

- **只做合规研究抓取**:渲染 JS + 可选代理;**不解 CAPTCHA、不破解访问壁垒、不用僵尸网络代理、不碰 PII**——这些是调用方的法律判断(CFAA / hiQ v. LinkedIn / Meta v. Bright Data / CCPA-CPRA)。若你插入一个**自动解 Turnstile**的引擎,那已越入"破壁",风险自负。
- **不服务** ToS 违规自动化。代理只用 **KYC/知情同意审计过**的供应商。
- **重**:每次起浏览器,只当 fetchlib waterfall 里 curl_cffi/Jina 失败后的 L3 升级用,别当默认。

---
> Created by Alex / 黄子阳 — https://ckcm.us
> Open Source: https://github.com/noique/cross-border-ecommerce-skills
> Licensed under CC BY-NC 4.0
