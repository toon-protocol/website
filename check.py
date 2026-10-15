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

# --- The brand's type and palette: .brand/identity.md, "Colour" and "Typography" ------------------
# The stylesheet and the landing page's inlined copy of it, where the rules below look.
STYLESHEET = "assets/site.css"
# The only families the stylesheet may declare ("Typography": Plex Sans, Plex Sans Condensed, Plex Mono).
FONT_FAMILIES = {"IBM Plex Sans", "IBM Plex Sans Condensed", "IBM Plex Mono"}
# Faces and colours that must appear nowhere in the stylesheet, its inlined copy or the manifest
# ("Colour": the dark-mode accent #d9b65c is retired; "Typography": Archivo and JetBrains Mono are replaced).
RETIRED = ["archivo", "jetbrains", "d9b65c"]
# Text-on-background pairings, (name, text variable, background variable), from the contrast table in
# "Colour": Ink on Paper 11.71, Gold text on Paper 5.20, Paper on Night 14.40, Gold on Night 6.89, and the
# state colours for UI states. Every one must reach WCAG 2.x AA for normal text, in the light set and the
# dark set. A colour holding rgba() is blended over the background first.
MIN_CONTRAST = 4.5
PAIRINGS = [
    ("body text", "--ink", "--bg"),
    ("body text on a raised surface", "--ink", "--bg-raised"),
    ("dim text", "--ink-dim", "--bg"),
    ("dim text on a sunken surface", "--ink-dim", "--bg-sunken"),
    ("faint text", "--ink-faint", "--bg"),
    ("faint text on a sunken surface", "--ink-faint", "--bg-sunken"),
    ("link and price text", "--accent", "--bg"),
    ("link and price text on a raised surface", "--accent", "--bg-raised"),
    ("link and price text on a tint", "--accent", "--accent-soft"),
    ("terminal text", "--term-ink", "--term"),
    ("terminal dim text", "--term-dim", "--term"),
    ("terminal gold", "--term-gold", "--term"),
    ("terminal green", "--term-good", "--term"),
    ("chip text", "--good", "--good-soft"),
    ("button text", "--accent-ink", "--gold"),
]


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


def inline_style(page):
    m = re.search(r"<style[^>]*>(.*?)</style>", (ROOT / page).read_text(encoding="utf-8"), re.S)
    return m.group(1) if m else ""


def css_texts():
    """(file, text) for the stylesheet and the landing page's inlined copy."""
    out = []
    if (ROOT / STYLESHEET).is_file():
        out.append((STYLESHEET, (ROOT / STYLESHEET).read_text(encoding="utf-8")))
    if (ROOT / LANDING).is_file():
        out.append((LANDING + " (inlined stylesheet)", inline_style(LANDING)))
    return out


def rule_fonts():
    for name, css in css_texts():
        for f in re.findall(r"@font-face\s*{[^}]*?font-family:\s*['\"]?([^;'\"]+)", css):
            if f.strip() not in FONT_FAMILIES:
                yield name, "stylesheet declares only the three Plex families", f.strip()
        for m in re.finditer(r"--(?:display|mono|body)\s*:\s*([^;]+);", css):
            first = m.group(1).split(",")[0].strip().strip("'\"")
            if first not in FONT_FAMILIES:
                yield name, "type stacks lead with a Plex family", first
    if (ROOT / STYLESHEET).is_file():
        for ref in stylesheet_refs(STYLESHEET):
            if ref.endswith((".woff2", ".woff", ".ttf")):
                u = internal(STYLESHEET, ref)
                if u and not (ROOT / u[0]).is_file():
                    yield STYLESHEET, "every font file the stylesheet references exists", ref


def rule_retired():
    texts = css_texts()
    if (ROOT / MANIFEST).is_file():
        texts.append((MANIFEST, (ROOT / MANIFEST).read_text(encoding="utf-8")))
    for name, text in texts:
        for word in RETIRED:
            if word in text.lower():
                yield name, "Archivo, JetBrains Mono and #d9b65c appear nowhere", word


def parse_colour(v):
    v = v.strip()
    if v.startswith("#"):
        h = v[1:]
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return [int(h[i:i + 2], 16) for i in (0, 2, 4)], 1.0
    m = re.match(r"rgba?\(([^)]*)\)", v)
    if m:
        parts = [x.strip() for x in m.group(1).split(",")]
        return [float(x) for x in parts[:3]], float(parts[3]) if len(parts) > 3 else 1.0
    return None


def luminance(rgb):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def blend(fg, bg):
    """fg (rgb, alpha) laid over an opaque bg rgb."""
    return [f * fg[1] + b * (1 - fg[1]) for f, b in zip(fg[0], bg)]


def contrast(a, b):
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def token_sets(css):
    """The light set (:root), and each dark set laid over it: the picker's (:root[data-theme="dark"]) and
    the system theme's (the docs' block under prefers-color-scheme: dark)."""
    def block(selector_re):
        m = re.search(selector_re + r"\s*{([^}]*)}", css)
        return dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+?)\s*(?:;|$)", m.group(1))) if m else {}
    light = block(r"(?m)^:root")
    sets = {"light": light}
    for theme, selector_re in (("dark", r'(?m)^:root\[data-theme="dark"\]'),
                               ("system dark", r':root:has\(body\.docs-body\):not\(\[data-theme="light"\]\)')):
        sets[theme] = {**light, **block(selector_re)}
    return sets


def rule_contrast():
    if not (ROOT / STYLESHEET).is_file():
        return
    sets = token_sets((ROOT / STYLESHEET).read_text(encoding="utf-8"))
    for theme, tokens in sets.items():
        page_bg = parse_colour(tokens.get("--bg", ""))
        for label, fg, bg in PAIRINGS:
            f, b = parse_colour(tokens.get(fg, "")), parse_colour(tokens.get(bg, ""))
            if not f or not b or not page_bg:
                yield STYLESHEET, f"every listed pairing is declared in the {theme} set", f"{label}: {fg} on {bg}"
                continue
            back = blend(b, page_bg[0])
            ratio = contrast(blend(f, back), back)
            if ratio < MIN_CONTRAST:
                yield STYLESHEET, f"{label} reaches {MIN_CONTRAST}:1 in the {theme} set", f"{fg} on {bg} is {ratio:.2f}:1"


class Resources(HTMLParser):
    """What a page loads (stylesheets, scripts, images, fonts, social images) and how many scripts it has."""
    def __init__(self):
        super().__init__()
        self.loads = []  # (tag, attr, value)
        self.scripts = 0
        self.icons = []  # (href, media) of each <link rel="icon">
        self.in_header = False
        self.header_mark = None  # the classes of the shapes in the header's mark, once it has one
        self.in_mark = False

    def handle_endtag(self, tag):
        if tag == "header":
            self.in_header = False
        elif tag == "svg":
            self.in_mark = False

    def handle_starttag(self, tag, attrs):
        a = {k: v for k, v in attrs if v is not None}
        classes = a.get("class", "").split()
        if tag == "header" and ({"site-header", "docs-header"} & set(classes)):
            self.in_header = True
        elif tag == "svg" and self.in_header and "mark" in classes and self.header_mark is None:
            self.in_mark, self.header_mark = True, set()
        elif tag in ("rect", "g") and self.in_mark:
            self.header_mark |= set(classes)
            if "fill" in a or "fill:" in a.get("style", ""):
                self.header_mark.add("fill=")
        if tag == "link" and a.get("rel") == "icon":
            self.icons.append((a.get("href", ""), a.get("media", "")))
        if tag == "script":
            self.scripts += 1
        if tag == "link" and "href" in a:
            self.loads.append(("link", "href", a["href"]))
        elif tag in ("script", "img", "source", "video", "audio", "iframe", "embed", "image") and "src" in a:
            self.loads.append((tag, "src", a["src"]))
        elif tag == "meta" and a.get("property", a.get("name", "")) in ("og:image", "og:image:secure_url", "twitter:image") and "content" in a:
            self.loads.append(("meta", a.get("property", a.get("name")), a["content"]))


def resources(page, cache={}):
    if page not in cache:
        r = Resources()
        r.feed((ROOT / page).read_text(encoding="utf-8"))
        cache[page] = r
    return cache[page]


def rule_hosts(page):
    rule = "no stylesheet, font, script or image from another host"
    for tag, attr, value in resources(page).loads:
        u = urlparse(value)
        if (u.scheme or u.netloc) and u.hostname not in SITE_HOSTS and not value.startswith(("data:", "mailto:")):
            yield rule, f"<{tag} {attr}> {value}"
    if page == LANDING:
        for ref in CSS_URL.findall(inline_style(page)):
            if urlparse(ref).netloc:
                yield rule, ref


def rule_favicon(page):
    rule = "links the 16px favicon in its light and its dark variant, as files"
    want = {"(prefers-color-scheme: light)": "toon-icon-16.svg", "(prefers-color-scheme: dark)": "toon-icon-16-dark.svg"}
    icons = resources(page).icons
    for href, _ in icons:
        if href.startswith("data:"):
            yield rule, "a data-URI favicon"
    for media, name in want.items():
        if not any(m == media and href.rsplit("/", 1)[-1] == name for href, m in icons):
            yield rule, f"no <link rel=\"icon\" media=\"{media}\"> for {name}"


def rule_header_mark(page):
    rule = "the header mark is the two-bar mark: a header bar, its square and a value bar, with no wire"
    got = resources(page).header_mark
    if got is None:
        yield rule, "no svg.mark in the header"
        return
    for part in ("a", "hole", "b"):
        if part not in got:
            yield rule, f"the header mark has no .{part} shape"
    if "c" in got:
        yield rule, "the header mark draws the wire, which is gone at this size"
    if "fill=" in got:
        yield rule, "the header mark paints its own colours, so the page's theme can't set its light and dark variants"


def rule_scripts(page):
    n = resources(page).scripts
    want = 1 if page == LANDING else (None if page.startswith("docs/") else 0)
    if want is not None and n != want:
        yield "the landing page has exactly one script, the apps and agents pages none", f"{n} <script> element(s)"


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


PAGE_RULES = [rule_links, rule_fragments, rule_hosts, rule_scripts, rule_favicon, rule_header_mark]  # each yields (rule, offending text)
SITE_RULES = [rule_manifest, rule_fonts, rule_retired, rule_contrast]  # each yields (page, rule, offending text)


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
