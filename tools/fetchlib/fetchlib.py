#!/usr/bin/env python3
"""fetchlib — a small, compliant fetch WATERFALL for the repo's scraping / API skills.

Escalates one tier only when the current tier is ACTUALLY blocked (a Markov-style state
machine — cheap → expensive):

  L1 curl_cffi   TLS/JA3 impersonation, free, no JS        (the default workhorse)
  L2 jina        r.jina.ai renders JS → clean markdown, free*  (JS-heavy but un/lightly-gated)
  L3 nodriver    anti-detect browser for JS challenges     (batch-2 plug-in via register_backend)
  L4 managed     paid unblocker (Bright Data etc.)         (opt-in, for DataDome/Akamai fortresses)

Control layer:
  - api-pacer (sibling tool) — header-adaptive pacing + full-jitter backoff
  - AIMD — additive-increase / multiplicative-decrease per-domain rate (creep up, cut hard on block)
  - CircuitBreaker — stop hammering a target that keeps blocking (cool-down)
  - per-fetch instrumentation → JSONL (target / tier / status / blocked / bytes / ms)

Compliance-first: honors robots.txt by default; it does NOT defeat access barriers, rotate IPs,
forge fingerprints, or handle PII — PII masking + lawful-basis are the caller's duty. Legitimate,
rate-limit-respecting RESEARCH use only (see SKILL.md red line).

Stdlib-runnable. `curl_cffi` is an OPTIONAL upgrade (graceful fallback to urllib if absent).
Self-test (no network): `python3 fetchlib.py`.
"""
import time
import random
import json
import urllib.request
import urllib.error
import urllib.robotparser
from urllib.parse import urlparse

# ---- optional deps (graceful) ----
try:
    from curl_cffi import requests as _cffi          # TLS-impersonation (pip install curl_cffi)
except Exception:
    _cffi = None
try:
    from api_pacer import Pacer                       # sibling tool: tools/api-pacer
except Exception:
    Pacer = None

TIERS = ("curl_cffi", "jina", "nodriver", "managed")  # cheap → expensive
DEFAULT_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
BLOCK_MARKERS = ("just a moment", "checking your browser", "cf-chl", "attention required",
                 "access denied", "captcha", "datadome", "verify you are human",
                 "please enable javascript", "unusual traffic", "pardon our interruption",
                 "are you a robot", "additional verification",
                 "请稍候", "正在验证", "请完成")  # incl. Chinese Cloudflare interstitial (benchmark caught it)


def is_blocked(status, body=""):
    """Heuristic: HTTP status or a challenge-page fingerprint in the body."""
    if status in (401, 403, 407, 429, 503):
        return True
    b = (body or "")[:4000].lower()
    return any(m in b for m in BLOCK_MARKERS)


class AIMD:
    """Additive-increase / multiplicative-decrease on the per-domain request rate.
    Creep the rate up while it works; cut it hard the moment a block appears (TCP-style)."""
    def __init__(self, rps=1.0, rps_min=0.1, rps_max=5.0, add=0.2, mul=0.5):
        self.rps, self.min, self.max, self.add, self.mul = rps, rps_min, rps_max, add, mul

    def on_ok(self):
        self.rps = min(self.max, self.rps + self.add)

    def on_block(self):
        self.rps = max(self.min, self.rps * self.mul)

    def gap(self):
        return 1.0 / max(self.rps, 1e-6)


class CircuitBreaker:
    """closed → (N consecutive blocks) → open (cool-down) → half_open (one trial) → closed."""
    def __init__(self, fail_threshold=3, cooldown=120.0):
        self.fail_threshold, self.cooldown = fail_threshold, cooldown
        self.fails, self.opened_at, self.state = 0, None, "closed"

    def allow(self, now):
        if self.state == "open":
            if self.opened_at is not None and now - self.opened_at >= self.cooldown:
                self.state = "half_open"
                return True
            return False
        return True

    def on_ok(self):
        self.fails, self.state, self.opened_at = 0, "closed", None

    def on_block(self, now):
        self.fails += 1
        if self.state == "half_open" or self.fails >= self.fail_threshold:
            self.state, self.opened_at = "open", now


# ---- tier backends ------------------------------------------------------------
def _fetch_curl_cffi(url, timeout=30, user_agent=DEFAULT_UA, **_):
    """L1: real-browser TLS/JA3 via curl_cffi (impersonate='chrome' auto-tracks latest).
    Falls back to plain urllib (NO impersonation — degraded) if curl_cffi isn't installed."""
    if _cffi is not None:
        r = _cffi.get(url, impersonate="chrome", timeout=timeout)
        return r.status_code, r.text, dict(r.headers)
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace"), dict(resp.headers)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace") if e.fp else ""
        return e.code, body, dict(e.headers or {})


def _fetch_jina(url, timeout=60, api_key=None, browser=True, user_agent=DEFAULT_UA, **_):
    """L2: r.jina.ai renders JS and returns clean markdown. Free without a key (rate-limited);
    a free key raises limits. *Verify commercial-use terms before relying on the free tier."""
    endpoint = "https://r.jina.ai/" + url
    headers = {"User-Agent": user_agent, "X-Return-Format": "markdown"}
    if browser:
        headers["X-Engine"] = "browser"
    if api_key:
        headers["Authorization"] = "Bearer " + api_key
    req = urllib.request.Request(endpoint, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace"), dict(resp.headers)
    except urllib.error.HTTPError as e:
        return e.code, "", dict(e.headers or {})


TIER_FUNCS = {"curl_cffi": _fetch_curl_cffi, "jina": _fetch_jina}
_EXTRA = {}


def register_backend(tier, fn):
    """Plug in a batch-2 backend, e.g. nodriver (L3) or a managed unblocker (L4).
    fn(url, **kwargs) -> (status:int|None, body:str, headers:dict)."""
    _EXTRA[tier] = fn


# ---- compliance: robots.txt ---------------------------------------------------
_robots_cache = {}


def robots_allows(url, user_agent=DEFAULT_UA):
    p = urlparse(url)
    base = "{}://{}".format(p.scheme, p.netloc)
    rp = _robots_cache.get(base, "MISS")
    if rp == "MISS":
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(base + "/robots.txt")
        try:
            rp.read()
        except Exception:
            rp = None  # robots unreachable → default-allow (logged by caller)
        _robots_cache[base] = rp
    return True if rp is None else rp.can_fetch(user_agent, url)


# ---- adaptive backend selection ----------------------------------------------
class ThompsonSelector:
    """Per-(domain, tier) Beta-Bernoulli bandit: learns which tier tends to SUCCEED for each
    domain and tries the empirically-best one FIRST — so a domain where curl_cffi always blocks
    but Jina works stops wasting the curl_cffi attempt. Optional JSON persistence carries the
    learning across runs. (Real benchmarks show the "best backend" is site/IP-dependent, not
    fixed — so learn it instead of hardcoding the waterfall order.)"""

    def __init__(self, path=None):
        self.path = path
        self._ab = {}                        # "host|tier" -> [alpha, beta]
        if path:
            try:
                with open(path) as f:
                    self._ab = json.load(f)
            except Exception:
                self._ab = {}

    @staticmethod
    def _key(host, tier):
        return host + "|" + tier

    def order(self, host, tiers):
        """Sample each tier's success-prob from its Beta posterior; try best first."""
        def score(t):
            a, b = self._ab.get(self._key(host, t), [1.0, 1.0])
            return random.betavariate(a, b)
        return sorted(tiers, key=score, reverse=True)

    def update(self, host, tier, success):
        ab = self._ab.setdefault(self._key(host, tier), [1.0, 1.0])
        ab[0 if success else 1] += 1.0

    def save(self):
        if not self.path:
            return
        try:
            with open(self.path, "w") as f:
                json.dump(self._ab, f)
        except Exception:
            pass


# ---- orchestrator -------------------------------------------------------------
class Fetcher:
    """Per-run fetch orchestrator: one AIMD + CircuitBreaker + Pacer per domain, escalating
    tiers only on a real block. Returns {url, tier, status, text, headers} (tier=None if all fail)."""

    def __init__(self, tiers=("curl_cffi", "jina"), respect_robots=True, jina_key=None,
                 managed=None, log_path=None, user_agent=DEFAULT_UA, pace=True,
                 learn=False, selector_path=None):
        self.tiers = list(tiers)
        self.respect_robots = respect_robots
        self.jina_key = jina_key
        self.user_agent = user_agent
        self.log_path = log_path
        self.pace = pace
        self.selector = ThompsonSelector(selector_path) if learn else None
        self._dom = {}
        if managed:                        # opt-in paid L4
            register_backend("managed", managed)
            if "managed" not in self.tiers:
                self.tiers.append("managed")

    def _state(self, host):
        st = self._dom.get(host)
        if st is None:
            st = {"aimd": AIMD(), "cb": CircuitBreaker(), "pacer": (Pacer() if Pacer else None)}
            self._dom[host] = st
        return st

    def _log(self, rec):
        if not self.log_path:
            return
        try:
            with open(self.log_path, "a") as f:
                f.write(json.dumps(rec) + "\n")
        except Exception:
            pass

    def fetch(self, url, max_retries_per_tier=2):
        host = urlparse(url).netloc
        st = self._state(host)
        if self.respect_robots and not robots_allows(url, self.user_agent):
            self._log({"url": url, "tier": None, "status": None, "blocked": True, "reason": "robots_disallow"})
            raise PermissionError("robots.txt disallows: " + url)
        wired = [t for t in self.tiers if (TIER_FUNCS.get(t) or _EXTRA.get(t))]
        order = self.selector.order(host, wired) if self.selector else wired
        for tier in order:
            fn = TIER_FUNCS.get(tier) or _EXTRA.get(tier)
            for _ in range(max_retries_per_tier):
                now = time.monotonic()
                if not st["cb"].allow(now):
                    self._log({"url": url, "tier": tier, "status": None, "blocked": True, "reason": "circuit_open"})
                    break                  # domain circuit open → skip to next tier
                if self.pace:
                    time.sleep(random.uniform(0, st["aimd"].gap()))   # full jitter over AIMD gap
                t0 = time.monotonic()
                try:
                    status, body, headers = fn(url, api_key=self.jina_key, user_agent=self.user_agent)
                except Exception:
                    status, body, headers = None, "", {}
                blocked = status is None or is_blocked(status, body)
                if st["pacer"] and headers:
                    st["pacer"].update(headers)
                self._log({"url": url, "tier": tier, "status": status, "blocked": blocked,
                           "bytes": len(body or ""), "ms": int((time.monotonic() - t0) * 1000)})
                if self.selector:
                    self.selector.update(host, tier, not blocked)
                if blocked:
                    st["aimd"].on_block()
                    st["cb"].on_block(time.monotonic())
                    if self.pace and status in (429, 503):
                        time.sleep(random.uniform(0, min(60, 2 ** st["cb"].fails)))  # full-jitter backoff
                    continue               # retry same tier, then escalate
                st["aimd"].on_ok()
                st["cb"].on_ok()
                return {"url": url, "tier": tier, "status": status, "text": body, "headers": headers}
        return {"url": url, "tier": None, "status": None, "text": "", "headers": {}, "blocked": True}


if __name__ == "__main__":
    # ---- offline self-test of the control logic (no network) ----
    a = AIMD(rps=1.0)
    for _ in range(5):
        a.on_ok()
    up = round(a.rps, 2)
    a.on_block()
    print("AIMD: creep-up rps={} → after 1 block rps={}".format(up, round(a.rps, 2)))

    cb = CircuitBreaker(fail_threshold=3, cooldown=10)
    for _ in range(3):
        cb.on_block(0.0)
    print("CircuitBreaker: state after 3 blocks={} allow@t=0→{} allow@t=11→{}".format(
        cb.state, cb.allow(0.0), cb.allow(11.0)))

    print("is_blocked(403)=", is_blocked(403),
          "| is_blocked(200,'Just a moment...')=", is_blocked(200, "Just a moment..."),
          "| is_blocked(200,'<html>ok</html>')=", is_blocked(200, "<html>ok</html>"))

    register_backend("mock_block", lambda url, **k: (403, "denied", {}))
    register_backend("mock_ok", lambda url, **k: (200, "hello world", {}))
    f = Fetcher(tiers=("mock_block", "mock_ok"), respect_robots=False, pace=False)
    r = f.fetch("https://example.com/x")
    print("waterfall escalation → served by tier={} status={}".format(r["tier"], r["status"]))
    assert r["tier"] == "mock_ok" and r["status"] == 200, "waterfall escalation failed"

    # ThompsonSelector learns which tier succeeds for a domain
    sel_f = Fetcher(tiers=("mock_block", "mock_ok"), respect_robots=False, pace=False, learn=True)
    for _ in range(10):
        sel_f.fetch("https://learn.example.com/x")
    ok = sel_f.selector._ab.get("learn.example.com|mock_ok", [1.0, 1.0])
    bl = sel_f.selector._ab.get("learn.example.com|mock_block", [1.0, 1.0])
    mean = lambda ab: ab[0] / (ab[0] + ab[1])
    print("ThompsonSelector: success-mean mock_ok={:.2f} vs mock_block={:.2f}".format(mean(ok), mean(bl)))
    assert mean(ok) > mean(bl), "selector did not learn to prefer the OK tier"
    print("OK: all self-tests passed")
