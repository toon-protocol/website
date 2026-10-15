<!-- Copied verbatim from toon-protocol/brand: identity.md at commit 49e5970fee2b15a4e187c316f3ef9bc34514d435 (branch brand/positioning-messaging-voice, ahead of brand's main, which still says pre-launch on devnet). Edit it there, then copy it again. -->

# Visual Identity Brief: TOON Protocol

*Drafted 2026-10-15 from [positioning.md](positioning.md), [messaging.md](messaging.md), [voice.md](voice.md) and the visual findings in [competitors.md](competitors.md) section 05. Existing inputs: the packet mark (`assets/toon-icon.svg`, `assets/toon-icon-tile.svg`), the spinner mod colours (`mod.json`), and the current website (Archivo 800 + JetBrains Mono on a charcoal theme). As with messaging and voice, this package decides. The mark is kept because it passes the brief on its own merits. The website's type and theme are replaced where they conflict. All contrast figures were measured against WCAG 2.x.*

---

## 01 — Identity strategy statement

TOON is the network where your own machine is the business, so the identity should look like an engineering document about a real thing, not a promise about the future. It is built from three flat colours and hard rectangles, with no gradients, glow, purple or neon. That makes it the opposite of the category's dark-mode spectacle, and it makes every graphic look like a diagram you could check. The one idea it has to carry is the thesis: a packet is the message and the money at once. The mark shows that, and the route diagram explains it at scale. Everything else should stay out of the way of real terminals, real hardware and real numbers.

---

## 02 — Logo direction

### Primary direction: the packet symbol + a constructed wordmark

**The symbol (keep it, as drawn).** Two upright bars sit on a thin line. The charcoal bar, carrying a small cream square, is the message, its header. The gold bar is the value. The grey line and end-blocks are the wire it travels on. It's an exact picture of "a packet that is data and value at once", it's made only of rectangles, and nothing in either competitor report looks like it. Don't redraw the large version.

**The wordmark (drawn; see the files below).**
- `TOON` in capitals, set in **IBM Plex Sans Condensed Bold** (see 04), then hand-adjusted. Tighten tracking to about −1%, square off the terminals of the T and N, and make the two O's identical.
  - **Drawn**: Plex Sans Condensed Bold outlined to paths (no font dependency), tracking −1% (−10 units per pair) on top of the font's T/O kerning, one O outline used twice. Plex's T and N already end square, so their terminals are unchanged.
- **Exploration worth one round**: draw the two O's as squared counters (rounded-rectangle O, radius no more than 15% of the cap height), so the double O echoes the two bars of the symbol. Reject it if it reads as "T00N" or "TDDN" at 24px.
- "Protocol" is not part of the logo. Where it's needed, it's set separately in Plex Mono Regular at 40% of the wordmark's cap height, in Wire grey.
- Lockup: symbol left, wordmark right, with the wordmark's cap height equal to the bar height × 0.42. The gap equals one bar width. A stacked lockup is allowed only for square avatars.

**Character**: Exact, constructed, quietly confident. It should look like a part number on a well-made machine, not a startup logo.

**Style notes**: Geometric and constructed. Every edge is horizontal or vertical: no curves except the optional O's, no diagonals, no outlines, no shadows. It's flat colour only, and the mark never sits inside a circle or a hexagon.

### Size variants (required; the current files break when small)
At 16px the wire is 0.4px tall and the gap between the bars is 0.4px, so the bars merge and the wire disappears.

| Size | Variant |
|---|---|
| ≥ 64px | Full mark as drawn |
| 24–48px | **Two-bar mark**: drop the wire and end-blocks, keep the cream square, and widen the gap between the bars to at least 2px |
| 16px | **Hand-hinted pixel version** on a 16×16 grid: two 5px bars with a 2px gap, a 2×2 cream square, and no wire. Draw it pixel by pixel, not by scaling |

**Files** (in `assets/`; "tile" means the background is included)

| Use | Light | Dark |
|---|---|---|
| Full mark, ≥ 64px | `toon-icon.svg`, `toon-icon-tile.svg` | `toon-icon-dark.svg`, `toon-icon-tile-dark.svg` |
| Two-bar mark, 24–48px (48 grid, even coordinates so 24px lands on whole pixels) | `toon-icon-small.svg`, `toon-icon-small-tile.svg` | `toon-icon-small-dark.svg`, `toon-icon-small-tile-dark.svg` |
| Favicon, 16px (pixel-placed, always on a tile) | `toon-icon-16.svg` | `toon-icon-16-dark.svg` |
| Wordmark (Plex Sans Condensed Bold, outlined) | `toon-wordmark.svg` | `toon-wordmark-dark.svg` |
| Horizontal lockup (two bars, no wire; cap height = bar height × 0.42, gap = one bar width) | `toon-lockup.svg` | `toon-lockup-dark.svg` |
| Exploration, rejected: squared-O wordmark (reads as "T00N" at 24px) | `toon-wordmark-squared-o.svg` | |

### Colour variants (required)
The charcoal bar is 1.23:1 against a dark background (`#1c1f24`), so in dark mode it disappears.

| Background | Header bar | Header square | Value bar | Wire |
|---|---|---|---|---|
| Paper `#f3efe6` (primary) | Ink `#2b2f36` | Paper | Gold `#c9a24a` | Wire `#6b6f76` |
| Night `#1c1f24` | **Paper `#f3efe6`** | **Night** | Gold | Wire (3.27:1, passes for graphics) |
| Single colour (stamp, emboss, terminal) | Ink, or Paper on dark | knocked out | Ink, or Paper | Ink, or Paper |

### What to avoid
- Circuit-board traces, nodes-and-edges "network" glyphs, hexagons, cubes and chain links: the crypto and infra clichés.
- Lightning bolts (L402), clouds (Cloudflare), tunnels or portals (ngrok, Tailscale), coins, `$` signs.
- Any gradient, inner glow or metallic shading on the gold. Nevermined's `#ffd700` glow is exactly what TOON's gold must not look like.
- A mascot or cartoon character. "TOON" invites one, and saying no to it is a positioning choice.

### Three logo references
1. **Deutsche Bank (Anton Stankowski, 1974)**: a slash inside a square. Borrow *one abstract geometric figure that means exactly one thing* and needs no lettering to be recognised.
2. **London Underground roundel and Harry Beck's map**: the mark and the diagram are one system, and the symbol shows up *on* the route. Borrow *the mark as a diagram element*: the packet symbol travels along TOON's route diagrams.
3. **Teenage Engineering**: a wordmark that reads like an instrument label, set small, functional and precisely spaced. Borrow *the engineered, spec-plate restraint* for the wordmark and for every product label.

---

## 03 — Colour palette

### Primary: Settlement gold `#c9a24a`
Gold means value, so it's the colour of the money half of the packet. It's muted and flat, more like brass than bullion, which keeps it practical and unhyped. **Gold is a fill colour, not a text colour on light backgrounds**: on Paper it measures 2.09:1, which fails for text.

### Secondary colours

| Name | Hex | Role | Measured contrast |
|---|---|---|---|
| **Ink** | `#2b2f36` | Primary text and the header bar on light. Dark-mode raised surfaces | 11.71:1 on Paper |
| **Paper** | `#f3efe6` | **Primary background** (light leads, see usage) and text on dark | 14.40:1 on Night |
| **Night** | `#1c1f24` | Dark-mode background and terminal background | Gold on Night 6.89:1 |
| **Wire** | `#6b6f76` | Lines, rules, diagram wires, secondary labels | 4.40:1 on Paper (large text and graphics only) |
| **Gold text** | `#7d5f17` | Gold when it must be text on Paper (prices, links) | 5.20:1 on Paper |

**State colours (UI and terminal only, never in marketing graphics)**

| State | On Night | On Paper |
|---|---|---|
| Running / ok | `#6cc08a` (7.51:1) | `#2f7a4c` (4.56:1) |
| Error | `#e07067` (5.26:1) | `#b23b32` (5.13:1) |
| Paid / settled | Gold `#c9a24a` | Gold text `#7d5f17` |
| Refused (with price) | Ink-dim `#9aa0ab`, *not* error red. A refusal is a value, not a failure | Wire `#6b6f76` |

### Colour personality
Warm, material and calm, like brass fittings on a charcoal machine on a paper spec sheet. It sits away from both of the category's looks: the purple dev-infra look and the near-black-with-neon look.

### Usage rules
- **Light leads.** Marketing surfaces (homepage, social cards, decks) default to Paper. Night is for terminals, docs dark mode and the CLI. This is the opposite of the current website, and it stops TOON's charcoal from reading as Tailscale's.
- **Gold covers 10–20% of any layout, and always as flat fills**: the value bar, a price, the active route, one key number. Never a full gold background behind body text.
- Gold on Ink or Night is fine for text, and Gold on Paper never is (use Gold text `#7d5f17`).
- **Never add**: purple, teal (Nevermined, Virtuals, Payman), neon green, blue links, gradients, a second gold. The dark-mode accent `#d9b65c` on the current site is retired, so there's one gold everywhere.
- The four core colours (Gold, Ink, Paper, Wire) are the whole brand palette. Night and the state colours are functional.

### Palette type
Warm neutral with a single accent: an analogous warm base (paper, brass) against a cool-neutral ink.

---

## 04 — Typography

### Primary typeface: IBM Plex Sans (with Plex Sans Condensed for display)
It's a grotesk drawn by an engineering company for engineering documents, with squared-off details and honest proportions, and it reads like a datasheet rather than a magazine. That's the "spec sheet" quality the competitor report asked for. It's free (SIL OFL) with a full weight range. It avoids the category's two uniforms: Instrument Serif with JetBrains Mono (x402, Akash) and Inter, Geist or Söhne (Olas, Apify, Skyfire, Stripe).

### Secondary typeface: IBM Plex Mono
It's the same family, so the shift from prose to command line is seamless. It replaces JetBrains Mono, which is now almost the category default (ngrok, Akash, Skyfire, x402). Use it for every command, address, price, hash and status word.

### Type personality
Engineered and plain. The system says *this was built by people who write specs*, and the confidence comes from consistency, not display flourishes.

### Usage hierarchy

| Level | Face | Weight | Size (web) | Notes |
|---|---|---|---|---|
| Display / hero | Plex Sans Condensed | Bold 700 | 56–72px, line-height 1.0 | Sentence case, tracking −1% |
| Headline (H2) | Plex Sans Condensed | SemiBold 600 | 32–40px | |
| Subhead (H3) | Plex Sans | SemiBold 600 | 20–24px | |
| Body | Plex Sans | Regular 400 | 17–18px, line-height 1.55 | Max 68 characters per line |
| Code, commands, numbers | Plex Mono | Regular 400 / Medium 500 | 0.92em of body | Prices and amounts always mono |
| Labels, eyebrows, live/next tags | Plex Mono | Medium 500 | 12–13px, uppercase, +6% tracking | The only uppercase text |

### Avoid
- Instrument Serif or any editorial serif, as a TOON display face.
- Neue Machina or anything quasi-mono and geometric that reads like Olas.
- JetBrains Mono, Inter, Geist, Söhne, Space Grotesk (crypto default), and Archivo Black (the current site, too blunt and generic-poster).
- Rounded geometric sans (Poppins, Circular), which reads friendly-consumer.
- Italics for emphasis in marketing. Use weight or Gold.

*If a paid upgrade is ever wanted: Berkeley Mono for the terminal, and only then. Plex is not a placeholder.*

---

## 05 — Imagery and photography style

**Overall aesthetic**: Documentary and matter-of-fact, like a photo in a hardware review. Natural light, a real desk, nothing staged.

**Subject matter**
- **The operator's machine**: a small PC under a desk, a laptop on a shelf with its lid open, a Raspberry Pi beside a home router, its status lights on. The router is the hero object, because it's the thing TOON says you don't have to open.
- **Real terminals**: actual `toon` sessions with actual output (`toon status`, `toon add … --price 2`), screenshotted or rendered in Plex Mono on Night. Never a mock-up with invented output.
- **Hands at a keyboard, optionally**: no faces needed, and no one posing.
- **Route diagrams** (see 06) instead of any abstract "network" imagery.

**Colour treatment**: Natural colour, slightly warm, with lifted blacks so that charcoal reads as charcoal and not pure black. The ideal is a palette that already contains cream walls, wood, and brass or gold tones. No colour grading toward teal or orange.

**What to avoid**: Glowing globes and data-streams, robot hands, humanoid AI, server-room aisles with blue LEDs (TOON is the opposite of the data centre), hooded hackers, matrix rain, 3D coins or tokens, AI-generated "futuristic" scenes, laptop-on-a-beach lifestyle shots, and logo walls.

---

## 06 — Iconography and illustration

**Style**: Constructed from the mark's geometry. A 24×24 grid, strokes in 2px, **square caps and mitred joins**, and only 0° and 90° angles (45° allowed for arrowheads). Filled rectangles stand for "things that hold value" (channel, wallet), and outlines for everything else. No circles except where the object is literally round. A custom set of about 20 icons covers the product: machine, router, connector, app, packet, channel, peer, route, wallet, price, refused, settled, live, next.

*Interim, until the custom set exists*: Lucide icons with `stroke-linecap: square; stroke-linejoin: miter` at 2px. Don't mix in a second icon library.

**Weight**: Regular, 2px at 24px and 1.5px at 16px, matched to Plex Sans Regular.

**Personality**: Functional and utilitarian. The branded expression is in the **route diagram**, not in the icons:
- Agent nodes are drawn as small Ink blocks, wires in Wire grey, and the packet travels as the mark itself (header bar plus Gold value bar).
- When a hop changes token, the value bar's label changes (USDC → …), shown in Plex Mono.
- Hop fees are drawn as a sliver of gold left at each connector. That's the one place the diagram is allowed to be clever.
- Everything is orthogonal routing (Beck-map rules: horizontal, vertical, 45°), flat and unshaded.

---

## 07 — Design principles

**Show the machine.**
Every hero, social card and deck opens on something real: the box, the router, the terminal. If a design could illustrate any cloud company's page, it's wrong for TOON.

**Draw the route, not the network.**
Explain by showing one packet travelling from payer to app, hop by hop, with the price and token on it. Never use a constellation of glowing nodes: one exact path beats a thousand implied ones.

**Flat and exact.**
Flat fills, hard edges and one gold, with no gradients, glow, blur, glassmorphism or drop shadows. If an effect hides an edge, remove it.

**State is part of the design.**
The live/next label, mainnet and devnet tags and real prices are designed elements: Plex Mono, uppercase, in a Wire-grey outlined chip, placed prominently and never in a footnote. The visual system makes honesty look intentional.

---

## 08 — Brand expressions

**Social profiles and posts**
- Avatar: the two-bar mark on a Paper tile, or on Night for dark-first platforms (GitHub org, Discord).
- Banner: one route diagram on Paper, with the tagline "Your machine. Paid per request." in Plex Sans Condensed Bold, Ink.
- Posts follow a changelog format. A Paper card holds one headline in Ink and one real command or terminal output on a Night panel, with a Gold highlight on the number that matters. Use a 1200×675 grid with a 64px margin and the symbol bottom-right at 48px.

**Website and docs**
- Light-first homepage on Paper. The hero is the tagline, the supporting statement, the install command in a Night terminal panel, and a live/next chip. Below that comes the route diagram as the main explainer, then real terminal sessions for each step.
- Docs default to the reader's system theme. Dark mode is Night with Paper text, and the mark switches to its dark variant (Paper header bar).
- Prices, amounts and addresses are always Plex Mono. The only Gold text on the page is prices and the active state.
- Replace the current Archivo and JetBrains Mono setup and the `#d9b65c` accent when the site is rewritten.

**Terminal and CLI (TOON's real "packaging")**
- The CLI and spinner use the state colours above: Gold for paid or settled, green for running, red only for errors, and dim for refused.
- The spinner mod keeps `#c9a24a`. `desktop_word` `#a8842c` is 3.5:1 on white and 3.05:1 on Paper, under the 4.5:1 for text, so change it to Gold text `#7d5f17` for legibility.
- The OG image and README header use the full mark on Paper with the wordmark, and nothing else.

**Presentations and pitch decks**
- Paper slides, with Ink text and one Gold element per slide at most.
- The structure from messaging.md: the three-product problem, then one network, then the route diagram built up hop by hop, then a live terminal, then live/next.
- Number every claim slide with its source, in Plex Mono, in the footer.

**Stickers and stationery (minimal)**
- A die-cut sticker of the full mark, Ink, Gold and Paper on a Paper backing. It's for laptops, which is literally where TOON runs.
- Business cards only if needed: Paper stock, the mark on the front, and on the back the name, a key fingerprint or `.anyone` address in Plex Mono. No job-title flourishes.
