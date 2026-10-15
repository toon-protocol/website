#!/usr/bin/env python3
"""Build docs/, apps/ and agents/ from the fragments in src/.

    python3 build.py

Each src/docs/<slug>.html is a body fragment. This script wraps it in the docs layout
(header, sidebar, table of contents, pager, footer) and writes docs/<slug>.html.
src/apps.html and src/agents.html become apps/index.html and agents/index.html. index.html at the root is hand-written;
the only thing this script does to it is copy assets/site.css between its <style> markers,
so the one file stands alone while the stylesheet stays the single source.

It also writes docs/search-index.js, one record per page section, which assets/search.js
loads when a reader first uses the docs search box. The docs pages also carry
assets/docs.js (phone menu, theme picker, "On this page" highlight, copy buttons); without
either script the search box and theme picker stay hidden and the pages read the same.

No dependencies beyond the standard library.
"""
import html
import json
import re
import subprocess
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
        ("get-paid", "Take payment from anyone", "A node anyone on Base or Solana can open a channel to and pay, with no gas."),
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

FULL_MARK = """<svg class="mark" viewBox="0 0 1024 1024" width="28" height="28" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"><g class="c"><rect x="112" y="484" width="56" height="56"/><rect x="168" y="499" width="120" height="26"/><rect x="736" y="499" width="120" height="26"/><rect x="856" y="484" width="56" height="56"/></g><rect class="a" x="288" y="252" width="212" height="536"/><rect class="hole" x="324" y="292" width="64" height="64"/><rect class="b" x="524" y="252" width="212" height="536"/></svg>"""

# The two-bar mark for 24 to 48px (assets/icon/toon-icon-small.svg), inline so the page's tokens theme it:
# an Ink header bar with a Paper square on Paper, a Paper bar with a Night square on Night.
SMALL_MARK = """<svg class="mark" viewBox="0 0 48 48" width="36" height="36" aria-hidden="true" shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg"><rect class="a" x="10" y="8" width="12" height="32"/><rect class="hole" x="12" y="10" width="4" height="4"/><rect class="b" x="26" y="8" width="12" height="32"/></svg>"""

# The interim lockup: TOON in Plex Sans Condensed Bold, Protocol in Plex Mono in Wire, after the mark.
BRAND_NAME = '<span class="name">TOON<small>Protocol</small></span>'


def favicons(root):
    """The 16px pixel mark as files, the light one for a light browser and the dark one for a dark browser."""
    return "".join(f'<link rel="icon" type="image/svg+xml" href="{root}assets/icon/{name}.svg" media="(prefers-color-scheme: {scheme})">\n'
                   for name, scheme in (("toon-icon-16", "light"), ("toon-icon-16-dark", "dark")))


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


# The status chip in every header: what is live and what is next. The wording is the maintainer's; check.py
# insists the chip says "Live" and "Next". OPERATORS is the number of independent connector operators, shown
# only once it is above zero so the site never implies a network size that doesn't exist.
STATUS_LIVE = "Live: mainnet USDC on Base and Solana, devnet to test"
STATUS_NEXT = "Next: independent operators"
OPERATORS = 0


def status_chip():
    count = f' <b class="count">{OPERATORS:,} independent operators</b>' if OPERATORS > 0 else ""
    return f'<p class="status-chip"><span>{STATUS_LIVE}</span> <span>{STATUS_NEXT}</span>{count}</p>'


def header(root, active):
    """The header of every page. On the landing page (root == "") the brand and the button
    point at anchors in the page itself."""
    def cls(name):
        return ' class="active"' if name == active else ""
    home = root == ""
    return f"""<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{'#top' if home else root + 'index.html'}" aria-label="TOON Protocol, home">{SMALL_MARK}{BRAND_NAME}</a>
    {status_chip()}
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
    <a class="brand" href="{root}index.html" aria-label="TOON Protocol, home">{SMALL_MARK}</a>
    <nav aria-label="Footer">
      <a href="{root}docs/index.html">docs</a>
      <a href="{root}apps/index.html">apps</a>
      <a href="{root}agents/index.html">agents</a>
      <a href="{root}docs/proof.html">proof</a>
      <a href="{GITHUB}">source</a>
    </nav>
    <span class="fact">MIT licensed · No protocol fee · stored on Arweave via a paid TOON write</span>
    <span class="out">{social()}</span>
  </div>
</footer>"""


# Docs pages set the reader's chosen theme before the stylesheet paints; without a choice,
# or without storage, the page follows the system as every other page does.
THEME_SCRIPT = ("<script>try{var t=localStorage.getItem(\"toon-theme\");"
                "if(t===\"dark\"||t===\"light\")document.documentElement.dataset.theme=t}catch(e){}</script>")


def head(title, description, root, docs=False):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description, quote=True)}">
{favicons(root)}{THEME_SCRIPT + chr(10) if docs else ""}<link rel="stylesheet" href="{root}assets/site.css">
</head>
<body{' class="docs-body"' if docs else ""}>
"""


CHEVRON = '<svg class="chev" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>'


def nav_groups(active):
    """The sidebar: one collapsible group per section, every group open."""
    out = []
    current = ' aria-current="page"'
    for section, pages in NAV:
        links = "\n".join(
            f'      <a href="{slug}.html"{current if slug == active else ""}>{html.escape(title)}</a>'
            for slug, title, _ in pages)
        out.append(f'    <details class="group" open>\n      <summary>{html.escape(section)}{CHEVRON}</summary>\n{links}\n    </details>')
    return "\n".join(out)


SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).lower()
    return SLUG_RE.sub("-", text).strip("-")


def add_anchors(body):
    """Give every h2 and h3 an id and an anchor link; collect (level, id, text) for the
    table of contents."""
    toc = []

    def repl(m):
        level, attrs, inner = m.group(1), m.group(2), m.group(3)
        idm = re.search(r'id="([^"]+)"', attrs)
        hid = idm.group(1) if idm else slugify(inner)
        toc.append((int(level), hid, re.sub(r"<[^>]+>", "", inner)))
        attrs = re.sub(r'\s*id="[^"]+"', "", attrs)
        return f'<h{level} id="{hid}"{attrs}><a class="anchor" href="#{hid}">{inner}</a></h{level}>'

    body = re.sub(r"<h([23])([^>]*)>(.*?)</h\1>", repl, body, flags=re.S)
    return body, toc


GLASS = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5"/></svg>'

# The button in the docs header that opens the search.
SEARCH_BUTTON = ('<button type="button" class="docsearch-open" aria-haspopup="dialog" aria-label="Search the docs" hidden>'
                 + GLASS + '<span>Search</span><kbd aria-hidden="true">/</kbd></button>')

# The search itself, one per page, opened over it by assets/search.js.
SEARCH_DIALOG = f"""<dialog class="docsearch" aria-label="Search the docs" data-index="search-index.js">
  <div class="panel">
    <form method="dialog" role="search">
      {GLASS}
      <input type="search" placeholder="Search the docs" aria-label="Search the docs" autocomplete="off" spellcheck="false">
      <button type="button" class="close" aria-label="Close search">esc</button>
    </form>
    <div class="results" aria-live="polite"></div>
    <p class="hint"><span><kbd>↑</kbd><kbd>↓</kbd> move</span><span><kbd>↵</kbd> open</span><span><kbd>esc</kbd> close</span></p>
  </div>
</dialog>"""

BLOCK_RE = re.compile(r"</?(?:p|li|ul|ol|dt|dd|dl|pre|div|table|tr|td|th|h3|h4|blockquote|figure|figcaption|br)\b[^>]*>")


def plain(fragment):
    """The text of an HTML fragment, one line, for the search index."""
    text = re.sub(r"<[^>]+>", "", BLOCK_RE.sub(" ", fragment))
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def search_records(slug, title, anchored):
    """One record per section of an anchored page body: the text before the first h2, then
    each h2 with the text up to the next."""
    parts = re.split(r'<h2 id="([^"]+)"[^>]*>(.*?)</h2>', anchored, flags=re.S)
    records = [{"u": f"{slug}.html", "p": title, "s": "", "t": plain(parts[0])}]
    for i in range(1, len(parts), 3):
        hid, heading, text = parts[i], parts[i + 1], parts[i + 2]
        records.append({"u": f"{slug}.html#{hid}", "p": title, "s": plain(heading), "t": plain(text)})
    return records


MENU = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path class="open" d="M4 6h16M4 12h16M4 18h16"/>'
        '<path class="shut" d="M6 6l12 12M18 6 6 18"/></svg>')
THEME_ICONS = {
    "dark": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5Z"/></svg>',
    "light": ('<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/>'
              '<path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'),
    "auto": ('<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4" width="18" height="12" rx="2"/>'
             '<path d="M8 20h8M12 16v4"/></svg>'),
}
CHECK = '<svg class="check" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 5 5 9-10"/></svg>'


def theme_picker():
    """The theme picker: a button and a menu of three, opened by assets/docs.js."""
    options = "".join(
        f'<li role="option" data-value="{value}" aria-selected="{"true" if value == "auto" else "false"}" tabindex="-1">'
        f'{THEME_ICONS[value]}<span>{name}</span>{CHECK}</li>'
        for value, name in (("dark", "Dark"), ("light", "Light"), ("auto", "Auto")))
    return (f'<div class="theme" hidden><button type="button" class="theme-btn" aria-haspopup="listbox" aria-expanded="false" '
            f'aria-controls="theme-menu" aria-label="Theme: Auto"><span class="icon">{THEME_ICONS["auto"]}</span>'
            f'<span class="label">Auto</span>{CHEVRON}</button>'
            f'<ul class="theme-menu" id="theme-menu" role="listbox" aria-label="Theme" hidden>{options}</ul></div>')
SOURCE = "https://github.com/toon-protocol/website/blob/main/src/docs"


def docs_header(with_menu):
    """The docs header, as on herdr.dev/docs: brand and sections on the left, the search in
    the middle, the socials and the theme on the right. assets/docs.js unhides the menu
    button and the theme picker; without it the sidebar sits above the page on a phone."""
    menu = ('  <button type="button" class="menu" aria-label="Menu" aria-controls="docs-nav" aria-expanded="false" hidden>'
            + MENU + '</button>\n') if with_menu else ""
    return f"""<header class="docs-header">
{menu}  <div class="left">
    <a class="brand" href="../index.html" aria-label="TOON Protocol, home">{SMALL_MARK}{BRAND_NAME}</a>
    {status_chip()}
    <nav aria-label="Primary">
      <a href="index.html" class="active">Docs</a>
      <a href="../apps/index.html">Apps</a>
      <a href="../agents/index.html">Agents</a>
    </nav>
  </div>
  <div class="mid">{SEARCH_BUTTON}</div>
  <div class="right">
      {social()}
    {theme_picker()}
    <a class="button primary" href="first-agent-node.html">Run a node</a>
  </div>
</header>"""


def pager_html(index):
    prev_page = FLAT[index - 1] if index > 0 else None
    next_page = FLAT[index + 1] if index + 1 < len(FLAT) else None
    arrow = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{d}"/></svg>'
    out = '<nav class="pager" aria-label="Previous and next">'
    out += (f'<a class="prev" rel="prev" href="{prev_page[0]}.html">{arrow.format(d="M15 18l-6-6 6-6")}'
            f'<span><small>Previous</small>{html.escape(prev_page[1])}</span></a>' if prev_page else "<span></span>")
    out += (f'<a class="next" rel="next" href="{next_page[0]}.html"><span><small>Next</small>{html.escape(next_page[1])}</span>'
            f'{arrow.format(d="M9 18l6-6-6-6")}</a>' if next_page else "<span></span>")
    return out + "</nav>"


def doc_foot(slug, index):
    return f"""  <div class="doc-foot">
    <p class="doc-meta"><a href="{SOURCE}/{slug}.html">Edit page</a><span>MIT licensed · stored on Arweave via a paid TOON write · <a href="proof.html">proof</a></span></p>
    {pager_html(index)}
  </div>"""


def toc_links(toc):
    return "\n".join(f'    <a href="#{hid}" class="h{level}">{html.escape(text)}</a>' for level, hid, text in toc)


# The docs home is a splash, as herdr.dev/docs is: a hero, then the page, with no sidebar.
HERO_TITLE = "Every request arrives paid."
HERO_TAGLINE = "TOON is a reverse proxy for your machine: a request reaches your app only after it is paid."


def build_splash(index, slug, title, summary, body):
    body, _ = add_anchors(body)
    return (head("TOON Protocol docs", summary, "../", docs=True)
            + docs_header(with_menu=False)
            + f"""
<main class="splash" id="_top">
  <div class="hero">
    <div class="copy">
      <h1>{HERO_TITLE}</h1>
      <p class="tagline">{HERO_TAGLINE}</p>
      <div class="actions">
        <a class="pill primary" href="install.html">Install toon</a>
        <a class="pill secondary" href="first-agent-node.html">Your first agent node</a>
      </div>
    </div>
    <div class="art">{FULL_MARK.replace('width="28" height="28"', 'width="320" height="320"')}</div>
  </div>
  <div class="doc">
{body}
  </div>
{doc_foot(slug, index)}
</main>
"""
            + SEARCH_DIALOG + '\n<script src="../assets/search.js" defer></script>\n<script src="../assets/docs.js" defer></script>\n</body>\n</html>\n')


def build_doc(index, slug, title, summary, section, body):
    if slug == "index":
        return build_splash(index, slug, title, summary, body)
    body, toc = add_anchors(body)
    toc_html = mtoc_html = ""
    if toc:
        links = toc_links([(2, "_top", "Overview")] + toc)
        toc_html = f'  <aside class="toc" aria-label="On this page">\n    <h2>On this page</h2>\n{links}\n  </aside>'
        mtoc_html = (f'    <details class="mtoc"><summary>On this page <span>Overview</span>{CHEVRON}</summary>\n'
                     f'    <nav aria-label="On this page">\n{links}\n    </nav></details>')
    return (head(f"{title} · TOON Protocol docs", summary, "../", docs=True)
            + docs_header(with_menu=True)
            + f"""
<nav class="sidebar" id="docs-nav" aria-label="Docs">
{nav_groups(slug)}
</nav>
<div class="main-pane">
  <main class="content" aria-labelledby="_top">
{mtoc_html}
    <div class="titlebar"><p class="section">{html.escape(section)}</p><h1 id="_top">{html.escape(title)}</h1></div>
    <div class="doc">
    <p class="lede">{html.escape(summary)}</p>
{body}
    </div>
{doc_foot(slug, index)}
  </main>
{toc_html}
</div>
"""
            + SEARCH_DIALOG + '\n<script src="../assets/search.js" defer></script>\n<script src="../assets/docs.js" defer></script>\n</body>\n</html>\n')


PAGES = {
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
    records = []
    for i, (slug, title, summary, section) in enumerate(FLAT):
        src = SRC / "docs" / f"{slug}.html"
        out = ROOT / "docs" / f"{slug}.html"
        body = src.read_text()
        out.write_text(build_doc(i, slug, title, summary, section, body))
        records += search_records(slug, title, add_anchors(body)[0])
        print("wrote", out.relative_to(ROOT))
    index = ROOT / "docs" / "search-index.js"
    index.write_text("/* Built by build.py from src/docs: one record per page section. */\n"
                     "window.TOON_DOCS_INDEX = " + json.dumps(records, separators=(",", ":")) + ";\n")
    print("wrote", index.relative_to(ROOT), "with", len(records), "sections")
    for slug in PAGES:
        (ROOT / slug).mkdir(exist_ok=True)
        out = ROOT / slug / "index.html"
        out.write_text(build_page(slug, (SRC / f"{slug}.html").read_text()))
        print("wrote", out.relative_to(ROOT))
    # A path manifest for Arweave: every file git tracks under the site, keyed by path, so an
    # untracked draft in the working tree never reaches it and a local build matches CI's.
    tracked = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    paths = {}
    for p in sorted(ROOT / name for name in tracked.split("\0") if name):
        if p.is_file() and not any(part.startswith(".") or part in ("src", "__pycache__", "build.py", "check.py", "README.md", "CLAUDE.md") for part in p.relative_to(ROOT).parts):
            paths[str(p.relative_to(ROOT))] = {"id": "<arweave tx id of this file>"}
    manifest = {"manifest": "arweave/paths", "version": "0.2.0", "index": {"path": "index.html"}, "paths": paths}
    (ROOT / "manifest.template.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("wrote manifest.template.json with", len(paths), "paths")


if __name__ == "__main__":
    main()
