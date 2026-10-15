#!/usr/bin/env python3
"""The site check: reads the built site from disk, prints one line per violation
("page: rule: offending text") and exits non-zero if there is any.

Run from the repository root, no arguments. Standard library only, Python 3.11.
Rules are the lists below; add a rule by adding a function to RULES.
"""
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag, urlparse

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


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []  # (attr, value)
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if v is None:
                continue
            if k in LINK_ATTRS:
                self.refs.append((k, v))
            elif k in ("id", "name") and (k == "id" or tag == "a"):
                self.ids.add(v)


def pages():
    names = [LANDING] if (ROOT / LANDING).is_file() else []
    for d in PAGE_DIRS:
        names += sorted(str(p) for p in (ROOT / d).glob("*.html"))
        names += sorted(str(p) for p in (ROOT / d).glob("*/index.html"))
    return names


def parse(name, cache={}):
    if name not in cache:
        p = Page()
        p.feed((ROOT / name).read_text())
        cache[name] = p
    return cache[name]


def internal(page, value):
    """Return (site path, fragment) for an internal reference, else None."""
    if value.startswith(("mailto:", "tel:", "data:", "javascript:")):
        return None
    u = urlparse(value)
    if u.scheme or u.netloc:
        if u.netloc not in SITE_HOSTS or u.scheme not in ("http", "https"):
            return None
        path = u.path or "/"
    elif not u.path:
        return page, unquote(u.fragment)
    else:
        path = u.path
    if path.startswith("/"):
        target = Path(path.lstrip("/"))
    else:
        target = Path(page).parent / path
    parts = []
    for part in target.parts:
        if part == "..":
            if parts:
                parts.pop()
        elif part != ".":
            parts.append(part)
    rel = "/".join(parts)
    if rel == "" or (ROOT / rel).is_dir():
        rel = (rel + "/index.html").lstrip("/")
    return rel, unquote(u.fragment)


def resolved_refs(page):
    for attr, value in parse(page).refs:
        r = internal(page, value)
        if r:
            yield value, r[0], r[1]


def rule_links(page):
    for value, target, _ in resolved_refs(page):
        if not (ROOT / target).is_file():
            yield "internal link resolves", value


def rule_fragments(page):
    for value, target, frag in resolved_refs(page):
        if frag and target.endswith(".html") and (ROOT / target).is_file():
            if frag not in parse(target).ids:
                yield "fragment resolves to an id", value


def manifest_paths():
    return json.loads((ROOT / MANIFEST).read_text())["paths"]


def rule_manifest():
    paths = manifest_paths()
    listed = set(paths)
    for p in sorted(listed):
        parts = p.split("/")
        if any(x in MANIFEST_FORBIDDEN_PARTS or x.startswith(".") for x in parts):
            yield MANIFEST, "manifest lists nothing under src/, __pycache__/ or a dot-directory", p
        elif not (ROOT / p).is_file():
            yield MANIFEST, "manifest lists only files that exist", p
    needed = {}
    for page in pages():
        needed.setdefault(page, page)
        for value, target, _ in resolved_refs(page):
            if (ROOT / target).is_file():
                needed.setdefault(target, page)
    for target, page in sorted(needed.items()):
        if target not in listed:
            yield MANIFEST, "manifest lists every page and referenced asset", target + " (from " + page + ")"


PAGE_RULES = [rule_links, rule_fragments]


def main():
    problems = []
    for page in pages():
        for rule in PAGE_RULES:
            for name, text in rule(page):
                problems.append(f"{page}: {name}: {text}")
    for page, name, text in rule_manifest():
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
