#!/usr/bin/env python3
"""browser-fetch — an OPTIONAL, shared browser-render backend for the repo's scraping skills.

Promotes the "real browser + optional proxy" capability (the kind proven in tools/trustpilot's
Selenium scraper) into a reusable fetchlib **L3** backend, so skills stop each re-implementing a
browser. Pluggable engine, default Selenium.

HONEST SCOPE (benchmarked 2026-06 from a datacenter IP, no proxy):
  This is the "JS-render + moderate protection" tier. A real browser CLEARS Trustpilot-class sites
  that plain HTTP / curl_cffi can't render — but it does NOT beat Cloudflare Managed Challenge /
  DataDome fortresses (Muckrack, G2, cf-challenge): from a datacenter IP, Selenium AND nodriver
  both stall on the "please wait" challenge page. Cracking those needs a RESIDENTIAL IP
  (+ maybe Camoufox / Scrapling's Turnstile solver) or a paid unblocker — not a fancier browser
  library. So default to the proven Selenium; register nodriver / camoufox / scrapling as opt-in
  engines and validate them on a residential IP before trusting.

Returns (status, body, headers) — drop-in as a fetchlib backend:
    import fetchlib, browser_fetch
    fetchlib.register_backend("browser", browser_fetch.as_fetchlib_backend(engine="selenium"))

Compliance (US operator): the caller (fetchlib) honors robots + rate limits. This renders JS and
can use a proxy, but does NOT solve CAPTCHAs, defeat access barriers, rotate botnet IPs, or handle
PII — those are the caller's legal call (CFAA / hiQ / CCPA-CPRA). Research use only. (If you plug in
an engine that auto-solves Turnstile, that crosses into barrier-defeat — your call, not this tool's.)

`selenium` is a lazy import (only needed when you actually call the selenium engine).
Self-test (no browser/network): `python3 browser_fetch.py`.
"""
import time

DEFAULT_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

# Challenge / interstitial fingerprints (EN + the Chinese Cloudflare "please wait" page that the
# benchmark caught slipping past English-only heuristics).
CHALLENGE = ("just a moment", "checking your browser", "cf-chl", "attention required",
             "access denied", "captcha", "datadome", "verify you are human", "unusual traffic",
             "请稍候", "正在验证", "请完成", "pardon our interruption", "are you a robot",
             "additional verification")


def _looks_blocked(title, html):
    t = (title or "").lower()
    h = (html or "")[:6000].lower()
    if any(m in t or m in h for m in CHALLENGE):
        return True
    return len(html or "") < 2000        # a near-empty render is usually a soft block / interstitial


# ---- engines ------------------------------------------------------------------
def _selenium_fetch(url, proxy=None, headless=True, wait=5, timeout=35, user_agent=DEFAULT_UA):
    from selenium import webdriver                     # lazy: only needed at call time
    from selenium.webdriver.chrome.options import Options
    opts = Options()
    for a in ("--headless=new" if headless else "--start-maximized",
              "--disable-gpu", "--no-sandbox", "--window-size=1920,1080",
              "--disable-blink-features=AutomationControlled", "--lang=en-US"):
        opts.add_argument(a)
    opts.add_argument("--user-agent=" + user_agent)
    if proxy:
        opts.add_argument("--proxy-server=" + proxy)   # NOTE: authed/residential proxies need selenium-wire
    d = webdriver.Chrome(options=opts)
    title, html = "", ""
    try:
        d.set_page_load_timeout(timeout)
        try:
            d.get(url)
        except Exception:
            pass                                       # a load timeout still leaves partial DOM to inspect
        time.sleep(wait)                               # let JS / any challenge settle
        title, html = d.title, d.page_source
    finally:
        d.quit()
    status = 403 if _looks_blocked(title, html) else 200   # normalize so fetchlib flags challenges
    return status, html, {}


_ENGINES = {"selenium": _selenium_fetch}


def register_engine(name, fn):
    """Plug in another engine (nodriver / camoufox / scrapling). VALIDATE ON A RESIDENTIAL IP FIRST.
    fn(url, proxy=None, headless=True, wait=..., timeout=..., user_agent=...) -> (status, body, headers)."""
    _ENGINES[name] = fn


def browser_fetch(url, engine="selenium", proxy=None, headless=True, wait=5, timeout=35,
                  user_agent=DEFAULT_UA, **_):
    """Fetch `url` in a real browser. Returns (status:int|None, body:str, headers:dict)."""
    fn = _ENGINES.get(engine)
    if fn is None:
        raise NotImplementedError(
            "engine '{}' not registered. 'selenium' is built in; register others with "
            "register_engine() and validate on a residential IP first.".format(engine))
    try:
        return fn(url, proxy=proxy, headless=headless, wait=wait, timeout=timeout, user_agent=user_agent)
    except Exception as e:
        return None, "browser_fetch error: " + str(e)[:120], {}


def as_fetchlib_backend(engine="selenium", proxy=None, **opts):
    """Return a fetchlib-compatible backend closure:
        fetchlib.register_backend("browser", as_fetchlib_backend(engine="selenium"))"""
    def _backend(url, **kw):
        return browser_fetch(url, engine=engine, proxy=proxy, **opts)
    return _backend


if __name__ == "__main__":
    # ---- offline self-test (no browser / network) ----
    assert _looks_blocked("请稍候…", "x" * 100) is True          # Chinese CF interstitial
    assert _looks_blocked("Just a moment...", "x" * 100) is True  # EN CF interstitial
    assert _looks_blocked("Real", "<html>" + "y" * 5000 + "</html>") is False
    assert _looks_blocked("", "tiny") is True                    # near-empty = soft block
    register_engine("mock", lambda url, **k: (200, "<html>" + "z" * 5000 + "</html>", {}))
    st, body, _ = as_fetchlib_backend(engine="mock")("https://example.com")
    assert st == 200 and len(body) > 2000, "fetchlib adapter / engine registry failed"
    try:
        browser_fetch("https://x", engine="nope")
        raise SystemExit("should have raised NotImplementedError")
    except NotImplementedError:
        pass
    print("OK: browser-fetch self-tests passed (block-detect + engine registry + fetchlib adapter)")
