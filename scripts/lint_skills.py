#!/usr/bin/env python3
"""lint_skills.py — repo hygiene gate for the skill library.

Checks the failure modes that actually bit this repo (each one is a real, fixed incident):

  1. FRONTMATTER   every skill has YAML frontmatter with a non-empty `name` + `description`,
                   and `name` matches its filename (a mismatched name breaks slash-invocation).
  2. DUPLICATES    no skill filename appears at two paths — 14 amazon skills once existed
                   twice and ALL 14 copies had silently diverged.
  3. DEAD LINKS    every relative .md link resolves — deleting a file must not orphan a link.
  4. RED LINE      no skill teaches IP/number rotation, CAPTCHA solving, or barrier defeat,
                   which would contradict the scraping red line in tools/fetchlib.
  5. DECEPTION     no skill tells the reader to disguise a message or identity (e.g. sending a
                   "transactional-looking" opt-in to harvest consent) — deceptive on its own
                   terms and an FTC Act s5 exposure for a US operator.
  6. FOLKLORE      no skill states an unpublished enforcement threshold as fact ("5+ blocks ->
                   24h ban"); vendors don't publish these, and a fake line invites gaming it.

Support files (references/ templates/ scripts/ assets/ examples/) are NOT skills and are
exempt from the frontmatter check — but they ARE still link- and red-line checked.

Usage:  python3 scripts/lint_skills.py [--quiet]
Exit 0 = clean, 1 = violations found. Stdlib only, no deps (runs on a bare CI image).
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUPPORT_DIRS = ("/references/", "/templates/", "/scripts/", "/assets/", "/examples/")
SKIP_DIRS = {".git", "node_modules", ".github"}

# Phrases that would contradict tools/fetchlib's red line. Matched case-insensitively.
# Negated//quoted mentions ("does NOT rotate IPs") are allowed via ALLOW below.
RED_LINE = (
    r"rotate\s+ips?\b", r"rotating\s+ips?\b", r"rotate\s+numbers?\b",
    r"轮换\s*ip", r"轮换\s*号码", r"更换\s*ip\s*(?:以|来)?\s*(?:规避|绕过)",
    r"solve\s+(?:the\s+)?captchas?\b", r"captcha[- ]solv", r"解\s*captcha", r"破解\s*验证码",
    r"bypass\s+(?:the\s+)?(?:ban|access\s+barrier)", r"defeat\s+access\s+barriers?",
)
ALLOW = (
    r"\bno\b", r"\bnot\b", r"\bnever\b", r"without", r"don'?t", r"do not",
    r"不换", r"不解", r"不破", r"不轮换", r"禁止", r"red line", r"红线",
    r"crosses the", r"would contradict", r"is tos evasion", r"rather than",
    r"deceptive", r"是欺骗", r"不需要", r"根本不需要",
    r"不是", r"而是", r"无需", r"别去", r"不应",       # 中文 "不是 X 而是 Y" negation
)

# Outreach/messaging deception — advising that a message be dressed up as something it
# isn't. Caught late: a references/ file once told users to send a "transactional-looking"
# opt-in request to harvest consent, which the four checks above all sailed past.
DECEPTION = (
    r"[-\s](?:looking|styled|disguised)\s+(?:opt-?in|request|message|email|notice)",
    r"\bdisguis\w*", r"\bmasquerad\w*", r"\bpose\s+as\b", r"\bposing\s+as\b",
    r"make it (?:look|appear|seem) like",
    r"伪装(?:成|为)", r"假装(?:成|是)", r"冒充",
)

# Precise enforcement thresholds vendors do not publish (e.g. "5+ blocks -> 24h ban").
# Growth-blog folklore stated as fact invites users to optimize against a fake line.
FAKE_THRESHOLD = (
    r"[0-9]+\+?\s*(?:blocks?|reports?)\b[^.\n]{0,30}(?:→|->|=+>?|gets?\s+you)[^.\n]{0,20}\b(?:ban|warning|restrict)",
    r"(?:→|->)\s*[0-9]+\s*h(?:our)?s?\s+ban\b",
)

FM_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n", re.S)
LINK_RE = re.compile(r"\]\(([^)\s]+?\.md)(?:#[^)]*)?\)")


def is_support(rel):
    return any(d in "/" + rel for d in SUPPORT_DIRS)


def skill_name_for(rel):
    base = os.path.basename(rel)
    if base == "SKILL.md":
        return os.path.basename(os.path.dirname(rel))
    return base[:-3]


def md_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
            if fn.lower() == "readme.md" or rel.startswith("examples/"):
                continue
            yield rel


def parse_fm(text):
    """Return dict of top-level scalar keys, or None if no frontmatter block."""
    m = FM_RE.match(text)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        if line[:1] in (" ", "\t", "#") or ":" not in line:
            continue                       # nested/comment lines aren't top-level keys
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip()
    return out


def main():
    quiet = "--quiet" in sys.argv
    errors, seen_names, checked = [], {}, 0

    for rel in sorted(md_files()):
        path = os.path.join(ROOT, rel)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        checked += 1
        support = is_support(rel)

        # ---- 1) frontmatter (skills only) ----
        if not support:
            fm = parse_fm(text)
            if fm is None:
                errors.append("%s: missing YAML frontmatter (need name + description)" % rel)
            else:
                expected = skill_name_for(rel)
                name, desc = fm.get("name", ""), fm.get("description", "")
                if not name:
                    errors.append("%s: frontmatter has no `name`" % rel)
                elif name != expected:
                    errors.append("%s: name '%s' != expected '%s'" % (rel, name, expected))
                if not desc:
                    errors.append("%s: frontmatter has no `description`" % rel)
                elif len(desc) < 40:
                    errors.append("%s: description too short (%d chars) to trigger reliably"
                                  % (rel, len(desc)))

            # ---- 2) duplicate skill filenames ----
            key = skill_name_for(rel)
            if key in seen_names:
                errors.append("%s: duplicate skill name '%s' (also at %s) — copies drift apart"
                              % (rel, key, seen_names[key]))
            else:
                seen_names[key] = rel

        # ---- 3) dead relative links ----
        for target in LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "//")):
                continue
            base = os.path.dirname(path)
            if not (os.path.isfile(os.path.join(base, target))
                    or os.path.isfile(os.path.join(ROOT, target))):
                errors.append("%s: dead link -> %s" % (rel, target))

        # ---- 4/5/6) line-level policy checks ----
        for lineno, line in enumerate(text.splitlines(), 1):
            low = line.lower()
            excused = any(re.search(a, low) for a in ALLOW)
            if any(re.search(p, low) for p in RED_LINE) and not excused:
                errors.append("%s:%d: violates the scraping red line -> %s"
                              % (rel, lineno, line.strip()[:90]))
            if any(re.search(p, low) for p in DECEPTION) and not excused:
                errors.append("%s:%d: tells the reader to disguise a message/identity -> %s"
                              % (rel, lineno, line.strip()[:90]))
            if any(re.search(p, low) for p in FAKE_THRESHOLD):
                errors.append("%s:%d: states an unpublished enforcement threshold as fact "
                              "(vendors don't publish these) -> %s"
                              % (rel, lineno, line.strip()[:90]))

    if errors:
        print("FAIL — %d issue(s) across %d files:\n" % (len(errors), checked))
        for e in errors:
            print("  ✗ " + e)
        print("\nSee scripts/lint_skills.py for what each check defends against.")
        return 1

    if not quiet:
        print("OK — %d files pass (frontmatter, no duplicates, no dead links, red line clean)"
              % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
