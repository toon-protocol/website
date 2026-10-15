#!/usr/bin/env python3
"""The site check: reads the built site from disk, prints one line per violation
("page: rule: offending text") and exits non-zero if there is any.

Run from the repository root, no arguments. Standard library only, Python 3.11.
The settings are the plain data below; add a rule by adding a function to PAGE_RULES
(called once per page) or SITE_RULES (called once), at the bottom of the file.
"""
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(".")
# The built pages: the landing page and every page under these directories.
PAGE_DIRS = ["docs", "apps", "agents"]
LANDING = "index.html"
# Attributes that reference another file.
LINK_ATTRS = {"href", "src"}
# Manifest paths must not start with or contain any of these parts.
MANIFEST_FORBIDDEN_PARTS = ["src", "__pycache__"]
MANIFEST = "manifest.template.json"
# Hosts that count as this site.
SITE_HOSTS = {"toon.ar.io"}
# A file reference inside CSS, in a <style> block or a linked stylesheet. url(#id) points at an
# SVG element of whichever document uses the rule, not at a file, so it is left out.
CSS_URL = re.compile(r"""url\(\s*['"]?([^'")#][^'")]*)""")


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []  # (attr, value)
        self.ids = set()
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        self.in_style = tag == "style"
        for k, v in attrs:
            if v is None:
                continue
            if k in LINK_ATTRS:
                self.refs.append((k, v))
            elif k in ("id", "name") and (k == "id" or tag == "a"):
                self.ids.add(v)

    def handle_endtag(self, tag):
        self.in_style = False

    def handle_data(self, data):
        if self.in_style:
            self.refs += [("url", v) for v in CSS_URL.findall(data)]


def pages():
    names = [LANDING] if (ROOT / LANDING).is_file() else []
    for d in PAGE_DIRS:
        names += sorted(str(p) for p in (ROOT / d).glob("*.html"))
        names += sorted(str(p) for p in (ROOT / d).glob("*/index.html"))
    return names


def parse(name, cache={}):
    if name not in cache:
        p = Page()
        p.feed((ROOT / name).read_text(encoding="utf-8"))
        cache[name] = p
    return cache[name]


def internal(page, value):
    """Return (site path, fragment) for an internal reference, else None."""
    if value.startswith(("mailto:", "tel:", "data:", "javascript:")):
        return None
    u = urlparse(value)
    if u.scheme or u.netloc:
        if u.hostname not in SITE_HOSTS or u.scheme not in ("http", "https", ""):
            return None
        path = u.path or "/"
    elif not u.path:
        return page, unquote(u.fragment)
    else:
        path = u.path
    path = unquote(path)
    if path.startswith("/"):
        target = Path(path.lstrip("/"))
    else:
        target = Path(page).parent / path
    parts = []
    for part in target.parts:
        if part == "..":
            if not parts:
                return "../" + path, unquote(u.fragment)  # above the site root: never a file
            parts.pop()
        elif part != ".":
            parts.append(part)
    rel = "/".join(parts)
    if rel == "" or (ROOT / rel).is_dir():
        rel = (rel + "/index.html").lstrip("/")
    return rel, unquote(u.fragment)


def stylesheet_refs(name, cache={}):
    """The url(...) references in a stylesheet, as written."""
    if name not in cache:
        cache[name] = CSS_URL.findall((ROOT / name).read_text(encoding="utf-8"))
    return cache[name]


def resolved_refs(page):
    """(reference as written, site path, fragment) for each internal reference on a page,
    and in the stylesheets it links."""
    for _, value in parse(page).refs:
        r = internal(page, value)
        if not r:
            continue
        yield value, r[0], r[1]
        if r[0].endswith(".css") and (ROOT / r[0]).is_file():
            for css_value in stylesheet_refs(r[0]):
                c = internal(r[0], css_value)
                if c and c[0] != r[0]:
                    yield css_value, c[0], c[1]


def rule_links(page):
    for value, target, _ in resolved_refs(page):
        if not (ROOT / target).is_file():
            yield "internal link resolves", value


def rule_fragments(page):
    for value, target, frag in resolved_refs(page):
        if frag and target.endswith(".html") and (ROOT / target).is_file():
            if frag not in parse(target).ids:
                yield "fragment resolves to an id", value


# ---- Copy rules. Each list is copied from the brand package in .brand/ (see .brand/README.md);
# edit a list there first, then copy it here.
# The proof page keeps the revisions it replaced, taglines included, so phrase rules skip it.
HISTORICAL_PAGES = {"docs/proof.html"}
# The marketing pages: the landing page and the apps and agents pages.
MARKETING = [LANDING, "apps/index.html", "agents/index.html"]
# .brand/messaging.md, 04 Messaging hierarchy, Level 1 and Level 2. SUPPORTING is Level 2 in the
# shortened wording issue #15 fixed for the landing page.
TAGLINE = "Your machine. Paid per request."
SUPPORTING = "TOON gets requests to your app and makes sure each one is paid before your code sees it."
# .brand/messaging.md, intro: the retired taglines.
RETIRED_TAGLINES = ["Value, routed.", "Host it from home. Get paid by anyone."]
# .brand/voice.md, 08 Things we never say: hollow hype, category cliches, unprovable absolutes,
# false urgency, the agent gimmick. Matched case-insensitively, at word boundaries.
NEVER_SAY = [
    "revolutionary", "game-changing", "world-class", "next-generation", "the future of", "unstoppable", "massive",
    "internet-native payments", "agentic commerce", "economic infrastructure for AI",
    "the agents aren't coming", "in a single line of code",
    "zero fees", "fully decentralized", "trustless", "100% private", "censorship-proof",
    "limited spots", "don't miss out", "early bird",
    "Hi agents", "Are you an AI agent",
    # .brand/messaging.md, 07 Things not to say, Category clichés (the ones voice.md 08 lacks).
    "agentic economy", "the agents are here", "single line of code", "frictionless", "connect anything, anywhere",
]
# .brand/messaging.md, 07 Things not to say, Competitor-adjacent language: "Get paid." as a sentence.
NEVER_SAY_SENTENCE = ["Get paid."]
# .brand/messaging.md, 07 Things not to say: "No open port" and "Hidden service" in headlines.
HEADLINE_BANNED = ["open port", "hidden service"]
# .brand/messaging.md, 07 Things not to say: never "onion". Marketing pages only: the docs keep
# "onion endpoint", the term toon_cli/CONTEXT.md defines.
MARKETING_BANNED_WORDS = ["onion"]
# .brand/messaging.md, 07 Things not to say: "Get paid" without the live label. The docs page is
# renamed; its slug stays.
SIDEBAR_PAGE_BANNED = ["Get paid"]


class Copy(HTMLParser):
    """What a reader and a link preview see: text outside code, the head's tags, the h1 and the sidebar."""

    def __init__(self):
        super().__init__()
        self.text = []  # visible text nodes outside code, pre, script and style
        self.code = []
        self.meta = {}  # name or property -> content
        self.title = ""
        self.h1 = ""
        self.sidebar = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            k = a.get("name") or a.get("property")
            if k:
                self.meta[k] = a.get("content") or ""
        if tag not in ("meta", "link", "br", "img", "path", "rect", "circle", "input", "hr"):
            self.stack.append((tag, a.get("class") or ""))

    def handle_endtag(self, tag):
        if any(t == tag for t, _ in self.stack):
            while self.stack.pop()[0] != tag:
                pass

    def handle_data(self, data):
        tags = [t for t, _ in self.stack]
        if "script" in tags or "style" in tags:
            return
        if "title" in tags:
            self.title += data
        elif "code" in tags or "pre" in tags:
            self.code.append(data)
        else:
            self.text.append(data)
            if "h1" in tags:
                self.h1 += data
            if any(t == "nav" and "sidebar" in c.split() for t, c in self.stack):
                self.sidebar.append(data)


def copy(name, cache={}):
    if name not in cache:
        c = Copy()
        c.feed((ROOT / name).read_text(encoding="utf-8"))
        cache[name] = c
    return cache[name]


def squash(s):
    return re.sub(r"\s+", " ", s).strip()


def phrase_re(p):
    return re.compile(r"(?<![\w-])" + re.escape(p.rstrip(".")).replace("\\ ", r"\s+").replace("'", "['\u2019]") + r"(?![\w-])", re.I)


def rule_never_say(page):
    if page in HISTORICAL_PAGES:
        return
    c = copy(page)
    seen = [("text", "\n".join(c.text)), ("title", c.title)] + [(k, v) for k, v in c.meta.items()]
    for where, text in seen:
        text = text.replace("\u2019", "'")
        for p in RETIRED_TAGLINES + NEVER_SAY:
            if phrase_re(p).search(text):
                yield "no retired tagline or never-say phrase", f'"{p}" in {where}'
        for p in NEVER_SAY_SENTENCE:
            if re.search(r"(?:^|[.!?]|\n)\s*" + re.escape(p), text):
                yield "no retired tagline or never-say phrase", f'"{p}" as a sentence in {where}'


def rule_landing_copy(page):
    if page != LANDING:
        return
    c = copy(page)
    if squash(c.h1) != TAGLINE:
        yield "landing h1 is the tagline", squash(c.h1)
    if SUPPORTING not in squash(" ".join(c.text)):
        yield "landing page has the supporting statement", SUPPORTING
    heads = {"h1": c.h1, "title": c.title, "og:title": c.meta.get("og:title", ""), "twitter:title": c.meta.get("twitter:title", "")}
    for where, text in heads.items():
        for p in HEADLINE_BANNED:
            if p in text.lower():
                yield "no open port or hidden service in the headline or titles", f'"{p}" in {where}'


def rule_marketing_words(page):
    if page not in MARKETING:
        return
    c = copy(page)
    text = " ".join(c.text + [c.title] + list(c.meta.values())).lower()
    for w in MARKETING_BANNED_WORDS:
        if re.search(r"\b" + w, text):
            yield "no onion on the marketing pages", w
    for t in c.text + list(c.meta.values()) + [c.title]:
        if "!" in t:
            yield "no exclamation mark outside code", squash(t)[:60]


def rule_sidebar(page):
    if not page.startswith("docs/"):
        return
    text = squash(" ".join(copy(page).sidebar))
    for p in SIDEBAR_PAGE_BANNED + RETIRED_TAGLINES + NEVER_SAY:
        if phrase_re(p).search(text):
            yield "docs sidebar has no banned phrase", p


def rule_manifest():
    listed = set(json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))["paths"])
    for p in sorted(listed):
        parts = p.split("/")
        if any(x in MANIFEST_FORBIDDEN_PARTS or x.startswith(".") for x in parts):
            yield MANIFEST, "manifest lists nothing under src/, __pycache__/ or a dot-directory", p
        elif not (ROOT / p).is_file():
            yield MANIFEST, "manifest lists only files that exist", p
    needed = {}
    for page in pages():
        needed.setdefault(page, page)
        for _, target, _ in resolved_refs(page):
            if (ROOT / target).is_file():
                needed.setdefault(target, page)
    for target, page in sorted(needed.items()):
        if target not in listed:
            yield MANIFEST, "manifest lists every page and referenced asset", target + " (from " + page + ")"


PAGE_RULES = [rule_links, rule_fragments, rule_never_say, rule_landing_copy, rule_marketing_words, rule_sidebar]  # each yields (rule, offending text)
SITE_RULES = [rule_manifest]  # each yields (page, rule, offending text)


def main():
    problems = []
    for page in pages():
        for rule in PAGE_RULES:
            for name, text in rule(page):
                problems.append(f"{page}: {name}: {text}")
    for rule in SITE_RULES:
        for page, name, text in rule():
            problems.append(f"{page}: {name}: {text}")
    for line in problems:
        print(line)
    if problems:
        print(f"{len(problems)} violation(s)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    sys.exit(main())
