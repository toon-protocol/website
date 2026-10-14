#!/usr/bin/env python3
"""Build docs/ and ecosystem/ from the fragments in src/.

    python3 build.py

Each src/docs/<slug>.html is a body fragment. This script wraps it in the docs layout
(header, sidebar, table of contents, pager, footer) and writes docs/<slug>.html.
src/ecosystem.html becomes ecosystem/index.html. index.html at the root is hand-written;
the only thing this script does to it is copy assets/site.css between its <style> markers,
so the one file stands alone while the stylesheet stays the single source.

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
        ("index", "Overview", "What you get, what to run, and what holds. Then pick a path."),
        ("concepts", "Concepts", "After this page the rest of the docs read without a glossary."),
    ]),
    ("Operators", [
        ("run-a-node", "Run a node", "A node running on your machine and answering GET /ilp, in one command or by hand."),
        ("put-your-app-behind-it", "Put your app behind it", "Your own app behind a priced route, told who paid in three headers."),
        ("get-paid", "Get paid", "A node anyone on Base or Solana can open a channel to and pay, with no gas."),
        ("peering", "Peer with another node", "Your node carrying another node's packets for a fee, set up from one URL."),
        ("operator-surface", "The operator surface", "A token that reads what you were paid, and a key that moves it."),
        ("hidden-services", "Hidden services", "Your node at a .anyone address with no domain and no open port, and a client that reaches it."),
    ]),
    ("Callers", [
        ("pay-a-node", "Pay a node", "A wallet, one channel and one paid request on the devnet, in six commands."),
        ("channels", "Payment channels", "A channel you open without gas, pay from with signatures, and leave with your deposit."),
        ("cli", "CLI reference", "Every toon-client setting and command, and where each value comes from."),
        ("errors", "Errors and reject codes", "What each refusal means, and the one thing to do about it."),
    ]),
    ("Agents", [
        ("spaceturtle", "spaceturtle", "An agent running a node from your machine, with the money kept away from it."),
    ]),
    ("Reference", [
        ("devnet", "Devnet reference", "Every devnet address, route and price, and the faucet that funds you."),
        ("protocol", "Protocol and specs", "The packet, the greeting and the self-description, and where the specs live."),
    ]),
]

FLAT = [(slug, title, summary, section) for section, pages in NAV for slug, title, summary in pages]

MARK = """<svg class="mark" viewBox="0 0 1024 1024" width="28" height="28" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"><g class="c"><rect x="112" y="484" width="56" height="56"/><rect x="168" y="499" width="120" height="26"/><rect x="736" y="499" width="120" height="26"/><rect x="856" y="484" width="56" height="56"/></g><rect class="a" x="288" y="252" width="212" height="536"/><rect class="hole" x="324" y="292" width="64" height="64"/><rect class="b" x="524" y="252" width="212" height="536"/></svg>"""

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect width='16' height='16' "
           "fill='%23f3efe6'/%3E%3Crect x='2' y='7' width='3' height='2' fill='%236b6f76'/%3E%3Crect x='11' y='7' width='3' "
           "height='2' fill='%236b6f76'/%3E%3Crect x='5' y='4' width='3' height='8' fill='%232b2f36'/%3E%3Crect x='9' y='4' "
           "width='3' height='8' fill='%23c9a24a'/%3E%3C/svg%3E")


def header(root, active):
    def cls(name):
        return ' class="active"' if name == active else ""
    return f"""<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{root}index.html" aria-label="TOON Protocol, home">{MARK}<span class="name">TOON<small>Protocol</small></span></a>
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
    <span>TOON Protocol · MIT licensed · stored on Arweave via a paid TOON write · no scripts</span>
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


def inline_stylesheet():
    """Copy assets/site.css into index.html between its <style data-src> markers, so the
    landing page stands alone as one file while the stylesheet stays the single source."""
    page = ROOT / "index.html"
    html_text = page.read_text()
    css = (ROOT / "assets" / "site.css").read_text().replace('url("fonts/', 'url("assets/fonts/')
    start_tag = '<style data-src="assets/site.css">'
    start = html_text.index(start_tag) + len(start_tag)
    end = html_text.index("</style>", start)
    page.write_text(html_text[:start] + "\n" + css + html_text[end:])
    print("inlined assets/site.css into index.html")


def main():
    inline_stylesheet()
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
