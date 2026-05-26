#!/usr/bin/env python3
"""Shared config + helpers for the SERP content-teardown toolkit.

Pure-Python, deterministic, no network, no LLM. Imported by every step script.
Keeps topic-cluster loading, brand-name loading, and domain helpers in one place
so the 8 step scripts stay DRY while remaining individually runnable.
"""
import json
import os
import re
from urllib.parse import urlsplit

import yaml


# ── topic clusters ──────────────────────────────────────────────────────────

def load_clusters(path):
    """Load topic clusters from a YAML file.

    Format:
        clusters:
          - {name: STR, pattern: REGEX}   # evaluated in order, first match wins

    Returns a list of (name, compiled_regex) tuples in declared order.
    Raises ValueError on a malformed file so misconfiguration fails loudly.
    """
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict) or "clusters" not in data:
        raise ValueError(f"{path}: expected a top-level 'clusters:' list")
    out = []
    for i, item in enumerate(data["clusters"] or []):
        if not isinstance(item, dict) or "name" not in item or "pattern" not in item:
            raise ValueError(f"{path}: clusters[{i}] needs both 'name' and 'pattern'")
        out.append((str(item["name"]), re.compile(item["pattern"], re.I)))
    if not out:
        raise ValueError(f"{path}: 'clusters' list is empty")
    return out


def cluster_of(text, clusters):
    """Return the name of the first cluster whose regex matches, else 'OTHER'."""
    low = (text or "").lower()
    for name, pat in clusters:
        if pat.search(low):
            return name
    return "OTHER"


# ── brand names ─────────────────────────────────────────────────────────────

def derive_brand_token(domain):
    """Fallback brand variant when a domain isn't in brand-names.json.

    Strips a leading 'www.', drops the TLD(s), and removes a few generic
    e-commerce suffix words so 'oceanwavejewelry.com' -> 'oceanwave'. The token
    is intentionally conservative (one concatenated form) to avoid inflating
    brand-density counts with generic words.
    """
    d = (domain or "").lower()
    if d.startswith("www."):
        d = d[4:]
    label = d.split(".")[0]  # registrable name without TLD
    # peel common generic suffixes so the token is brand-specific
    for suf in ("jewelry", "jewellery", "official", "shop", "store",
                "store", "co", "online", "boutique"):
        if label.endswith(suf) and len(label) > len(suf) + 2:
            label = label[: -len(suf)]
    return [label] if label else []


def load_brand_names(path):
    """Load domain -> [name variants] from JSON. Drops the __comment__ key.

    Returns {} if path is None/missing so callers can fall back to
    derive_brand_token() per domain.
    """
    if not path or not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return {k: v for k, v in data.items()
            if not k.startswith("__") and isinstance(v, list)}


def brand_variants(domain, brand_map):
    """Resolve display-name variants for a domain (config first, else derived)."""
    v = brand_map.get(domain)
    if v:
        return v
    return derive_brand_token(domain)


# ── domain helpers ──────────────────────────────────────────────────────────

def regdom(url_or_netloc):
    """Best-effort registrable domain from a URL or netloc.

    Handles common multi-part ccTLDs (.com.au, .co.uk, etc.). Strips 'www.'.
    """
    s = url_or_netloc or ""
    netloc = urlsplit(s).netloc if "//" in s or s.startswith("http") else s
    netloc = netloc.lower().split(":")[0]
    if netloc.startswith("www."):
        netloc = netloc[4:]
    parts = netloc.split(".")
    if (len(parts) >= 3 and parts[-2] in ("com", "co", "org", "net", "gov")
            and parts[-1] in ("au", "uk", "nz", "za")):
        return ".".join(parts[-3:])
    return ".".join(parts[-2:]) if len(parts) >= 2 else netloc
