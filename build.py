#!/usr/bin/env python3
"""Build docs/ and ecosystem/ from the fragments in src/.

    python3 build.py

Each src/docs/<slug>.html is a body fragment. This script wraps it in the docs layout
(header, sidebar, table of contents, pager, footer) and writes docs/<slug>.html.
src/ecosystem.html becomes ecosystem/index.html. index.html at the root is hand-written
and self-contained, and this script never touches it.

No dependencies beyond the standard library. No scripts are emitted into any page.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

# (section title, [(slug, nav title, one-line summary)])
NAV = [
    ("Start here", [
        ("index", "Overview", "What a TOON node is, the two roles, and which path to take."),
        ("concepts", "Concepts", "The words the rest of the docs use, each defined once."),
    ]),
    ("Operators", [
        ("run-a-node", "Run a node", "One image, one TOML file, one command."),
        ("put-your-app-behind-it", "Put your app behind it", "What a route terminates to, and what your app sees."),
        ("get-paid", "Get paid", "The settlement block, the chains, the tokens, and who pays gas."),
        ("peering", "Peer with another node", "Carry someone else's packets one hop further for a fee."),
        ("operator-surface", "The operator surface", "Reads, signed writes, the dashboard, and operating it."),
    ]),
    ("Callers", [
        ("pay-a-node", "Pay a node", "From nothing to a paid request, with the CLI and the library."),
        ("channels", "Payment channels", "Opening without gas, who pays what, the watermark, leaving."),
        ("cli", "CLI reference", "Every setting, where it comes from, and the commands."),
        ("errors", "Errors and reject codes", "Who refused, what each code means, and what to do."),
        ("hidden-services", "Hidden services", "Paying a node that lives at a .anyone address."),
    ]),
    ("Agents", [
        ("spaceturtle", "spaceturtle", "An agent that runs a node from your own machine."),
    ]),
    ("Reference", [
        ("devnet", "Devnet reference", "Nodes, routes, prices, contracts and the faucet."),
        ("protocol", "Protocol and specs", "The wire, the greeting, the specs, the ADRs and the vectors."),
    ]),
]

FLAT = [(slug, title, summary, section) for section, pages in NAV for slug, title, summary in pages]

MARK = """<svg class="mark" viewBox="0 0 220 220" width="26" height="26" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
<g><rect x="0" y="0" width="104" height="104" rx="10" class="sq"/>
<path d="M12 12 h80 M12 28 h64 M12 44 h48 v48 M28 92 v-64 h48 M44 76 v-32 M60 92 v-32 M92 28 v64 h-32" class="ln"/>
<rect x="78" y="78" width="14" height="14" class="dot"/></g>
<g transform="translate(116,0)"><rect x="0" y="0" width="104" height="104" rx="10" class="sq"/>
<path d="M92 12 h-80 v80 h80 v-64 h-64 v48 h48 v-32 h-32" class="ln"/></g>
<g transform="translate(0,116)"><rect x="0" y="0" width="104" height="104" rx="10" class="sq"/>
<path d="M12 92 v-80 h80 v80 h-64 v-48 h48 v32 h-32" class="ln"/></g>
<g transform="translate(116,116)"><rect x="0" y="0" width="104" height="104" rx="10" class="sq"/>
<path d="M12 12 v80 M28 92 v-80 h64 M44 28 h48 M28 44 h48 v48 M92 60 h-32 v32" class="ln"/>
<rect x="12" y="78" width="14" height="14" class="dot"/></g>
</svg>"""

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 220 220'%3E%3Crect width='220' "
           "height='220' rx='40' fill='%230b0d12'/%3E%3Cg fill='none' stroke='%23e6e9ef' stroke-width='14'%3E%3Cpath "
           "d='M40 40h140M40 80h100M40 120h60v60M70 180v-100h70M140 110v70'/%3E%3C/g%3E%3Crect x='150' y='150' "
           "width='30' height='30' fill='%237dd3fc'/%3E%3C/svg%3E")


def header(root, active):
    def cls(name):
        return ' class="active"' if name == active else ""
    return f"""<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{root}index.html" aria-label="TOON Protocol, home">{MARK}<span class="name">TOON Protocol</span></a>
    <nav aria-label="Primary">
      <a class="hide-s" href="{root}index.html#how">How it works</a>
      <a href="{root}docs/index.html"{cls('docs')}>Docs</a>
      <a href="{root}ecosystem/index.html"{cls('ecosystem')}>Ecosystem</a>
      <a class="hide-s" href="https://github.com/toon-protocol">GitHub</a>
      <a class="button primary" href="{root}docs/run-a-node.html">Run a node</a>
    </nav>
  </div>
</header>"""


def footer(root):
    return f"""<footer>
  <div class="wrap">
    <span>TOON Protocol · MIT licensed · stored on Arweave via a paid TOON write</span>
    <nav>
      <a href="{root}index.html">Home</a>
      <a href="{root}docs/index.html">Docs</a>
      <a href="{root}ecosystem/index.html">Ecosystem</a>
      <a href="https://github.com/toon-protocol">GitHub</a>
      <a href="https://discord.gg/PxzjbtXg9Q">Discord</a>
      <a href="https://x.com/toonprotocol">X</a>
    </nav>
  </div>
</footer>"""


def head(title, description, root):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description, quote=True)}">
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="{root}assets/site.css">
</head>
<body>
"""


def nav_groups(active, wrapper_class):
    out = []
    for section, pages in NAV:
        links = "\n".join(
            f'      <a href="{slug}.html"{" class=\"active\"" if slug == active else ""}>{html.escape(title)}</a>'
            for slug, title, _ in pages)
        out.append(f'    <div class="group">\n      <h4>{html.escape(section)}</h4>\n{links}\n    </div>')
    return "\n".join(out)


SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).lower()
    return SLUG_RE.sub("-", text).strip("-")


def add_anchors(body):
    """Give every h2 an id and an anchor link; collect (id, text) for the table of contents."""
    toc = []

    def repl(m):
        attrs, inner = m.group(1), m.group(2)
        idm = re.search(r'id="([^"]+)"', attrs)
        hid = idm.group(1) if idm else slugify(inner)
        toc.append((hid, re.sub(r"<[^>]+>", "", inner)))
        attrs = re.sub(r'\s*id="[^"]+"', "", attrs)
        return f'<h2 id="{hid}"{attrs}><a class="anchor" href="#{hid}">{inner}</a></h2>'

    body = re.sub(r"<h2([^>]*)>(.*?)</h2>", repl, body, flags=re.S)
    return body, toc


def build_doc(index, slug, title, summary, section, body):
    body, toc = add_anchors(body)
    prev_page = FLAT[index - 1] if index > 0 else None
    next_page = FLAT[index + 1] if index + 1 < len(FLAT) else None
    pager = '<nav class="pager" aria-label="Previous and next">'
    pager += (f'<a class="prev" href="{prev_page[0]}.html"><small>Previous</small>{html.escape(prev_page[1])}</a>'
              if prev_page else "<span></span>")
    pager += (f'<a class="next" href="{next_page[0]}.html"><small>Next</small>{html.escape(next_page[1])}</a>'
              if next_page else "<span></span>")
    pager += "</nav>"
    toc_html = ""
    if toc:
        toc_html = '<aside class="toc" aria-label="On this page"><h4>On this page</h4>\n' + "\n".join(
            f'  <a href="#{hid}">{html.escape(text)}</a>' for hid, text in toc) + "\n</aside>"
    page_title = f"{title} · TOON Protocol docs" if slug != "index" else "TOON Protocol docs"
    return (head(page_title, summary, "../")
            + header("../", "docs")
            + f"""
<div class="wrap docs">
  <details class="mobilenav">
    <summary>Docs</summary>
{nav_groups(slug, 'mobilenav')}
  </details>
  <aside class="sidebar" aria-label="Docs">
{nav_groups(slug, 'sidebar')}
  </aside>
  <main class="doc">
    <p class="eyebrow">{html.escape(section)}</p>
    <h1>{html.escape(title)}</h1>
    <p class="lede">{html.escape(summary)}</p>
{body}
{pager}
  </main>
  {toc_html}
</div>
"""
            + footer("../")
            + "\n</body>\n</html>\n")


def build_ecosystem(body):
    return (head("Ecosystem · TOON Protocol",
                 "The apps behind TOON nodes, the clients that pay them, and the rails underneath: "
                 "AR.IO, Arweave, Anyone Protocol, x402, Solana, Base, Interledger.", "../")
            + header("../", "ecosystem")
            + "\n<main>\n" + body + "\n</main>\n"
            + footer("../")
            + "\n</body>\n</html>\n")


def main():
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "ecosystem").mkdir(exist_ok=True)
    for i, (slug, title, summary, section) in enumerate(FLAT):
        src = SRC / "docs" / f"{slug}.html"
        out = ROOT / "docs" / f"{slug}.html"
        out.write_text(build_doc(i, slug, title, summary, section, src.read_text()))
        print("wrote", out.relative_to(ROOT))
    eco = (ROOT / "ecosystem" / "index.html")
    eco.write_text(build_ecosystem((SRC / "ecosystem.html").read_text()))
    print("wrote", eco.relative_to(ROOT))
    # A path manifest for Arweave: every file under the site, keyed by path.
    paths = {}
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and not any(part.startswith(".") or part in ("src", "build.py", "README.md") for part in p.relative_to(ROOT).parts):
            paths[str(p.relative_to(ROOT))] = {"id": "<arweave tx id of this file>"}
    manifest = {"manifest": "arweave/paths", "version": "0.2.0", "index": {"path": "index.html"}, "paths": paths}
    (ROOT / "manifest.template.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("wrote manifest.template.json with", len(paths), "paths")


if __name__ == "__main__":
    main()
