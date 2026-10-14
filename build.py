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
        ("agent-node", "The agent node", "Agent node, TOON app, connector, app, relay, peering, address and channel: one meaning each."),
        ("concepts", "Connector concepts", "After this page the connector pages read without a glossary."),
        ("compared", "Where TOON sits", "Pay-per-request protocols, purchase-authorization protocols, and the route only TOON has."),
        ("faq", "FAQ", "The questions operators and callers ask, with short answers and where to read on."),
    ]),
    ("Run an agent node", [
        ("install", "Install", "toon in ~/.local/bin, checked against the release's checksum, and the agent skills beside it."),
        ("first-agent-node", "Your first agent node", "A hidden agent node on the devnet, funded and running, with an event on your own relay read back."),
        ("networks-and-reachability", "Networks and reachability", "Which network init settles on and joins, and the connector reached hidden or on clearnet."),
        ("money", "Money", "Where each address is funded, what each command moves, the spending limit, and channels by hand."),
        ("agent-keys", "Agent keys", "A scoped, limited key an agent works the node with: its orders, its file, and the apps it may add."),
        ("peering", "Peering", "A peering toward another operator, a route over it, a probe of the path's cost, and one paid packet."),
        ("adding-an-app", "Adding an app", "Your HTTP service behind the connector at its own price, confined, with its variables and secrets."),
        ("creating-a-toon-app", "Creating a TOON app", "A second connector with its own keys and onion endpoint, peered with the first, and how to destroy it."),
        ("relay", "The relay", "Writes to your relay and to others', its settings and prices, and a live feed sold or bought."),
        ("operations", "Operations", "up, down, status and logs, packet counts and history, every --json exit code, and where things live."),
        ("backup-and-restore", "Backup and restore", "One sealed file that brings the wallet and the onion endpoints back on another machine."),
    ]),
    ("The connector, by hand", [
        ("run-a-node", "Run a node", "A node running on your machine and answering GET /ilp, in one command or by hand."),
        ("put-your-app-behind-it", "Put your app behind it", "Your own app behind a priced route, told who paid in three headers."),
        ("get-paid", "Get paid", "A node anyone on Base or Solana can open a channel to and pay, with no gas."),
        ("peering-by-hand", "Peer with another node", "Your node carrying another node's packets for a fee, set up from one URL."),
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
        ("exit-codes", "Exit codes", "Every exit code and error code toon can return, and the rules behind each command's output."),
        ("proof", "Proof", "The landing page is not on a web server: every revision, its Arweave transaction and the receipts of the write that bought it."),
    ]),
]

FLAT = [(slug, title, summary, section) for section, pages in NAV for slug, title, summary in pages]

MARK = """<svg class="mark" viewBox="0 0 1024 1024" width="28" height="28" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"><g class="c"><rect x="112" y="484" width="56" height="56"/><rect x="168" y="499" width="120" height="26"/><rect x="736" y="499" width="120" height="26"/><rect x="856" y="484" width="56" height="56"/></g><rect class="a" x="288" y="252" width="212" height="536"/><rect class="hole" x="324" y="292" width="64" height="64"/><rect class="b" x="524" y="252" width="212" height="536"/></svg>"""

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Crect width='16' height='16' "
           "fill='%23f3efe6'/%3E%3Crect x='2' y='7' width='3' height='2' fill='%236b6f76'/%3E%3Crect x='11' y='7' width='3' "
           "height='2' fill='%236b6f76'/%3E%3Crect x='5' y='4' width='3' height='8' fill='%232b2f36'/%3E%3Crect x='9' y='4' "
           "width='3' height='8' fill='%23c9a24a'/%3E%3C/svg%3E")


# toon_cli's GitHub stars, shown beside the GitHub icon once they pass the threshold.
# Update by hand before a publish: gh api repos/toon-protocol/toon_cli --jq .stargazers_count
GITHUB_STARS = 0
STAR_THRESHOLD = 100
GITHUB = "https://github.com/toon-protocol/toon_cli"
SOCIAL = [
    ("GitHub", GITHUB, "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"),
    ("X", "https://x.com/toonprotocol", "M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"),
    ("Discord", "https://discord.gg/PxzjbtXg9Q", "M20.317 4.37a19.79 19.79 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.865-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.74 19.74 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.058a.082.082 0 0 0 .031.056 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.3 12.3 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.84 19.84 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"),
]


def social():
    out = ['<span class="social">']
    for name, url, d in SOCIAL:
        count = ""
        if name == "GitHub" and GITHUB_STARS >= STAR_THRESHOLD:
            count = f"<b>{GITHUB_STARS:,}</b>"
        out.append(f'<a href="{url}" aria-label="TOON on {name}" title="{name}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="{d}"/></svg>{count}</a>')
    out.append('</span>')
    return "\n      ".join(out)


def header(root, active):
    """The header of every page. On the landing page (root == "") the brand and the button
    point at anchors in the page itself."""
    def cls(name):
        return ' class="active"' if name == active else ""
    home = root == ""
    return f"""<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{'#top' if home else root + 'index.html'}" aria-label="TOON Protocol, home">{MARK}<span class="name">TOON<small>Protocol</small></span></a>
    <nav aria-label="Primary">
      <a href="{root}docs/index.html"{cls('docs')}>Docs</a>
      <a href="{root}apps/index.html"{cls('apps')}>Apps</a>
      <a href="{root}agents/index.html"{cls('agents')}>Agents</a>
      {social()}
      <a class="button primary" href="{'#run' if home else root + 'docs/first-agent-node.html'}">Run a node</a>
    </nav>
  </div>
</header>"""


def footer(root):
    return f"""<footer class="site-foot">
  <div class="wrap">
    <a class="brand" href="{root}index.html" aria-label="TOON Protocol, home">{MARK}</a>
    <nav aria-label="Footer">
      <a href="{root}docs/index.html">docs</a>
      <a href="{root}apps/index.html">apps</a>
      <a href="{root}agents/index.html">agents</a>
      <a href="{root}ecosystem/index.html">ecosystem</a>
      <a href="{root}docs/proof.html">proof</a>
      <a href="{GITHUB}">source</a>
    </nav>
    <span class="fact">MIT licensed · stored on Arweave via a paid TOON write</span>
    <span class="out">{social()}</span>
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
            + '\n<div class="page">\n' + header("../", "docs")
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
            + "\n</div>\n</body>\n</html>\n")


PAGES = {
    "ecosystem": ("Ecosystem · TOON Protocol",
                  "The apps behind TOON nodes, the clients that pay them, and the rails underneath: "
                  "AR.IO, Arweave, Anyone Protocol, x402, Solana, Base, Interledger."),
    "apps": ("Apps · TOON Protocol",
             "Open-source services that run behind a TOON node and are paid per request. "
             "None contains payment code."),
    "agents": ("Agents · TOON Protocol",
               "Agents that run a TOON node, pay one, or both: spaceturtle and hermes-toon."),
}


def build_page(slug, body):
    title, description = PAGES[slug]
    return (head(title, description, "../")
            + '\n<div class="page">\n' + header("../", slug)
            + "\n<main>\n" + body + "\n</main>\n"
            + footer("../")
            + "\n</div>\n</body>\n</html>\n")


def sync_landing_chrome():
    """Write the header and footer into index.html between their markers, so the landing
    page carries the same chrome as every generated page."""
    page = ROOT / "index.html"
    html_text = page.read_text()
    for marker, body in (("header", header("", "home")), ("footer", footer(""))):
        start_tag, end_tag = f"<!-- {marker} -->", f"<!-- /{marker} -->"
        start = html_text.index(start_tag) + len(start_tag)
        end = html_text.index(end_tag, start)
        html_text = html_text[:start] + "\n" + body + "\n" + html_text[end:]
    page.write_text(html_text)
    print("synced the header and footer into index.html")


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
    sync_landing_chrome()
    inline_stylesheet()
    (ROOT / "docs").mkdir(exist_ok=True)
    for i, (slug, title, summary, section) in enumerate(FLAT):
        src = SRC / "docs" / f"{slug}.html"
        out = ROOT / "docs" / f"{slug}.html"
        out.write_text(build_doc(i, slug, title, summary, section, src.read_text()))
        print("wrote", out.relative_to(ROOT))
    for slug in PAGES:
        (ROOT / slug).mkdir(exist_ok=True)
        out = ROOT / slug / "index.html"
        out.write_text(build_page(slug, (SRC / f"{slug}.html").read_text()))
        print("wrote", out.relative_to(ROOT))
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
