# 礼貌抓取节奏 (rate-limiting) — reddit-voc 数据采集

`reddit-voc` 是**只读的 VOC 调研**(抓公开帖子/评论做洞察)。要稳定跑完一次采集、不被限流/封 IP,正确姿势不是"用随机/高斯延迟伪装成人",而是:**走官方 API + 尊重 rate-limit + 配速 + 退避**。

## 优先级

1. **优先用官方 API(PRAW)**,而非抓 HTML。PRAW 自带官方 ~100 QPM 限速处理,是最稳、最合规的路径。
2. **按响应头的真实预算配速**,而不是猜一个 sleep。用共享工具 [`tools/api-pacer`](../../../tools/api-pacer/SKILL.md)。
3. **429/503 时 full-jitter 指数退避**(uniform,不是高斯)。

## 用法(PRAW + api-pacer)

```python
import praw
from api_pacer import Pacer   # tools/api-pacer/api_pacer.py

reddit = praw.Reddit(client_id=..., client_secret=..., user_agent="voc-research/1.0 by u/you")
pacer = Pacer(rps=1.0, headers="reddit", safety=0.8)   # 额外礼貌层；PRAW 已管官方限额

for post in reddit.subreddit("skincareaddiction").top("year", limit=200):
    analyze_post(post)        # 你的 6 轴帖子拆解 → post-analysis.csv
    pacer.wait()              # 处理后再等，按预算 full-jitter，摊开负载
```

若确实需要抓 old.reddit HTML(API 拿不到的字段),用 `polite_get` 自动配速+退避:

```python
import requests
from api_pacer import Pacer, polite_get
s = requests.Session(); s.headers["User-Agent"] = "voc-research/1.0"
p = Pacer(rps=0.5, headers="generic")           # HTML 抓取更保守
resp = polite_get(s, "https://old.reddit.com/r/xxx/top/.json?t=year", p)
```

## 为什么不用"高斯延迟躲检测"

- Reddit **不会**检验你的延迟像不像钟形;它看的是**速率 vs 官方限额、OAuth/账号/IP 卫生、宏观规律**。
- 只读研究**根本不需要"装人"**——你本来就是合规访客。配速的目的是**不打满限额 + 抗节流**,不是伪装。
- 真需要拟人节奏时(灰色场景),真解也是**泊松到达 + 昼夜 λ(t) + 会话爆发**,不是单个高斯——但那超出本 skill 的只读范围。

## 红线

**只读调研 OK。** 不要把配速/退避用于**刷票、水帖、养小号、规避封禁**——那违反 Reddit ToS,`reddit-voc` 与本仓库均不服务于此。
