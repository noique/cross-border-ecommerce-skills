#!/usr/bin/env python3
"""api_pacer.py — polite, adaptive request pacing + full-jitter backoff.

A tiny, dependency-light rate limiter for the repo's scraping / API skills. It paces
requests to the SERVER'S OWN rate-limit budget when the response exposes rate-limit
headers, and falls back to a configured requests-per-second budget otherwise. On
429/503/Retry-After it does AWS-style "full jitter" exponential backoff.

Why not a Gaussian/uniform sleep? Because the optimum is to read the real budget
(the response headers), not to guess a delay from any distribution. Where jitter
genuinely matters (retry storms), the researched winner is FULL JITTER = uniform(0, cap),
not a bell curve. See references.

Legitimate use ONLY: stay under published rate limits, avoid thundering-herd, be a good
API citizen while doing research / data collection. NOT for ToS-violating automation
(vote manipulation, spam, sockpuppets, ban evasion).

Stdlib only. `requests` is optional (only for the polite_get helper).
"""
import time
import random

# Known rate-limit header conventions (keys are lowercased on read). Extend as needed.
HEADER_SETS = {
    # Reddit API: remaining requests + seconds until the window resets
    "reddit":  {"remaining": "x-ratelimit-remaining", "reset": "x-ratelimit-reset", "reset_is_epoch": False},
    # GitHub-style: reset is a UNIX epoch timestamp
    "github":  {"remaining": "x-ratelimit-remaining", "reset": "x-ratelimit-reset", "reset_is_epoch": True},
    # Generic x-ratelimit-* (assume seconds-until-reset)
    "generic": {"remaining": "x-ratelimit-remaining", "reset": "x-ratelimit-reset", "reset_is_epoch": False},
}


class Pacer:
    """Adaptive pacer + full-jitter backoff.

    Typical loop:
        p = Pacer(rps=1.0, headers="reddit")
        for url in urls:
            p.wait()                                   # sleep BEFORE the request
            resp = session.get(url)
            if p.on_response(resp.status_code, resp.headers,
                             resp.headers.get("retry-after")):
                continue                               # got 429/503 → already backed off, retry
            handle(resp)
    """

    def __init__(self, rps=1.0, safety=0.8, headers="generic",
                 reset_is_epoch=None, max_backoff=60.0, min_sleep=0.0):
        self.default_gap = 1.0 / max(rps, 1e-6)        # seconds between requests when no headers
        self.safety = safety                           # use only this fraction of the stated budget
        conf = HEADER_SETS.get(headers, HEADER_SETS["generic"])
        self.h_remaining = conf["remaining"]
        self.h_reset = conf["reset"]
        self.reset_is_epoch = conf["reset_is_epoch"] if reset_is_epoch is None else reset_is_epoch
        self.max_backoff = max_backoff
        self.min_sleep = min_sleep
        self.remaining = None
        self.reset = None
        self.fails = 0

    def update(self, response_headers):
        """Feed a response's headers so the next wait() uses the real budget."""
        h = {str(k).lower(): v for k, v in dict(response_headers or {}).items()}
        r = h.get(self.h_remaining)
        rs = h.get(self.h_reset)
        self.remaining = float(r) if r not in (None, "") else None
        if rs not in (None, ""):
            rs = float(rs)
            self.reset = max(rs - time.time(), 0.0) if self.reset_is_epoch else rs
        else:
            self.reset = None

    def _base_gap(self):
        # No budget info → constant configured gap.
        if self.remaining is None or self.reset is None:
            return self.default_gap
        # Budget exhausted → wait out the window.
        if self.remaining <= 1:
            return max(self.reset, 0.0) + 1.0
        # Spread the remaining budget over the remaining window (with a safety margin).
        return max(self.reset, 0.0) / max(self.remaining * self.safety, 1.0)

    def wait(self):
        """Sleep before the next request. Full jitter over [0, base_gap]."""
        gap = self._base_gap()
        time.sleep(max(self.min_sleep, random.uniform(0.0, gap)))

    def on_response(self, status, headers=None, retry_after=None):
        """Update budget from headers; on 429/503/Retry-After do full-jitter backoff.

        Returns True if the caller should RETRY (a limit was hit), else False.
        """
        if headers is not None:
            self.update(headers)
        hit = status in (429, 503) or bool(retry_after)
        if hit:
            self.fails += 1
            if retry_after not in (None, ""):
                try:
                    cap = float(retry_after)
                except (TypeError, ValueError):
                    cap = min(self.max_backoff, 2 ** self.fails)
            else:
                cap = min(self.max_backoff, 2 ** self.fails)
            time.sleep(random.uniform(0.0, cap))       # full-jitter backoff
            return True
        self.fails = 0
        return False


def polite_get(session, url, pacer, max_retries=5, **kwargs):
    """Drop-in `requests` GET that paces + retries with backoff. Returns the final Response."""
    resp = None
    for _ in range(max_retries):
        pacer.wait()
        resp = session.get(url, **kwargs)
        if pacer.on_response(resp.status_code, resp.headers, resp.headers.get("retry-after")):
            continue
        return resp
    return resp  # exhausted retries; caller inspects resp.status_code


if __name__ == "__main__":
    # Tiny self-test (no network): simulate a shrinking budget.
    p = Pacer(rps=2.0, headers="reddit", safety=0.8)
    for rem in (100, 50, 5, 1):
        p.update({"x-ratelimit-remaining": rem, "x-ratelimit-reset": 60})
        print(f"remaining={rem:>3}  base_gap≈{p._base_gap():.2f}s (mean sleep≈{p._base_gap()/2:.2f}s)")
    print("429 backoff caps (fails 1..5):", [min(60, 2 ** i) for i in range(1, 6)])
