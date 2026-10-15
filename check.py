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


PAGE_RULES = [rule_links, rule_fragments]  # each yields (rule, offending text)
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
