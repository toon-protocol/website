<!-- Copied verbatim from toon-protocol/brand: messaging.md at commit 49e5970fee2b15a4e187c316f3ef9bc34514d435 (branch brand/positioning-messaging-voice, ahead of brand's main, which still says pre-launch on devnet). Edit it there, then copy it again. -->

# Brand Messaging: TOON Protocol

*Drafted 2026-10-15. Built on [positioning.md](positioning.md) (category: paid self-hosting), [context.md](context.md) and the competitor reports. This package is the source of truth for the brand. The current website's taglines ("Value, routed." and "Host it from home. Get paid by anyone.") are retired, and the site's copy gets rewritten from this file. Product facts and the terms defined in `toon_cli/CONTEXT.md` are not brand choices; they constrain everything here. Secondary audiences are inferred from context.md and the toon_cli README, because none were recorded: agents operating nodes themselves, and connector operators and protocol peers.*

**Rule that applies to everything below**: TOON settles in USDC on Base and Solana mainnet through the project's node, and devnet is for testing. Proof marked **owed** stays out of public copy until it's real. Any page that says "paid" carries a visible **live: Base and Solana mainnet · devnet for testing** label.

---

## 01 — Core message

> **TOON helps developers and agent builders earn from what already runs on their own machines by making it reachable and charging for every request, with no server, no open port and no company in the middle.**

The anchor is *reachable and paid, in one sentence*. Any copy that drops one half reads as a tunnel or a 402 rail. (See [positioning.md](positioning.md), red flag 4.)

---

## 02 — Value proposition

TOON is an open network that lets an app or agent on your own machine take paid requests from anyone, person or agent. A connector on your machine checks payment the way nginx terminates SSL, so your app receives ordinary HTTP that has already been paid for. You set the price, you don't need a server, a domain, an open port or a payment account, and there's no platform taking a cut or holding your money.

---

## 03 — Tagline options

| # | Tagline | Style | Rationale |
|---|---|---|---|
| 1 | **Your machine. Paid per request.** | Functional | Both halves in five words: *your machine* is the self-hosting, *paid per request* is the business. |
| 2 | **Every request arrives paid.** | Functional | Compresses the reverse-proxy idea into the operator's experience, using the project's own words ("every request that reaches it has been paid for"). |
| 3 | **Your machine is the business.** | Aspirational | States the unclaimed territory exactly. It's the strongest strategic line, but on its own it doesn't say *how*. |
| 4 | **Answer the request. Keep the money.** | Witty / pointed | Says the thesis (message and payment are one action) and "nobody in the middle" without a single technical word. |
| 5 | **Run it at home. Charge for it.** | Functional | The most concrete, but "home" sounds like a hobby and undersells agents and servers in a closet. |

Rejected: anything with "Get paid." as its own sentence (Apify owns "Publish Actors. Get paid.", Nevermined owns "Agents get paid"). Also "The message is the money", which is too close to Interledger's "Making Money Move like Data" and needs explaining.

**Recommended: #1, "Your machine. Paid per request."** It's the only option that holds both halves of the position. It's plain, and true on mainnet today, with the label. Nobody in either competitor report uses "your machine". Use **#2 "Every request arrives paid."** as the product line under it in technical contexts (README, docs hero). Keep **#3** internal, as the strategic test every page should pass.

---

## 04 — Messaging hierarchy

### Level 1 — Brand headline
> **Your machine. Paid per request.**

### Level 2 — Supporting statement
> Run your app or agent where it already lives. TOON gets requests to it with no server, no domain and no open port, and makes sure each one is paid before your code sees it.

### Level 3 — Key messages

**1. Reachable from anywhere, with no open port.**
Your service can sit behind a home router and still answer the internet. You don't need a cloud account, a domain or port forwarding.
*Proof*: **mechanism live, demo owed.** A new TOON app is reachable as a hidden service by default, at an `.anyone` address inside the Anyone overlay, so it needs no open port and no public address. What's missing is a public, reproducible demo: a laptop on residential internet, no port forwarding, an outside agent paying and getting a response. Don't use this message in paid channels until the demo exists.

**2. Your app never touches the money.**
The connector on your machine terminates payment the way nginx terminates SSL. Your app gets plain HTTP that's already paid for, with no SDK, no wallet and no billing code.
*Proof*: **live.** That's how the connector works. The app behind it is any HTTP service.

**3. Nobody you have to sign up with.**
Payment routes hop by hop between peered connectors, and anyone can run one. No merchant account, no facilitator, no platform cut, no payout schedule.
*Proof*: **live** in the protocol. Each packet carries its own claim, so there's no invoice, settle round trip or facilitator call per request. No protocol fee. On devnet, a new agent node peers toward the network's hub, which is a connector like any other. The live mainnet node is the one the project runs. Once there are independent connector operators, add their number, and until then don't imply there are many.

**4. One binary, built to be run by people and agents.**
`toon` is the whole agent node: connector, supervisor and CLI. Every command is non-interactive and returns JSON, so an agent can operate it as easily as you can.
*Proof*: **live.** toon_cli v0.1.0 for Linux x86_64/aarch64. `toon up` installs a `systemd --user` service. `--json` on every command, with stable exit codes.

### Level 4 — Proof point bank

| # | Proof | Status | Use for |
|---|---|---|---|
| 1 | Payment is terminated by a connector in front of the app, which receives plain HTTP | live | Message 2, docs hero |
| 2 | A packet carries its own payment claim, with no invoice or settle round trip | live | Message 3, technical audiences |
| 3 | Routes hop by hop across peered connectors and changes token along the way | live (two paid hops on mainnet; token change on devnet) | Message 3, protocol peers |
| 4 | Settles in USDC on Base mainnet and Solana mainnet, so not tied to one chain. Base Sepolia and Solana devnet for testing | live | Against L402 (Bitcoin only) |
| 4a | Every channel is an x402 batch-settlement channel on x402's audited contract; a stock x402 client can open one | live | Relating TOON to x402: "ILP routes, x402 settles" |
| 4b | A new TOON app is a hidden service by default, at an `.anyone` address, with no open port | live | The mechanism behind message 1 |
| 4c | MIT licensed, no protocol fee | live | Openness and "nobody takes a cut" |
| 5 | One `toon` binary, released for Linux x86_64 and aarch64, checksummed | live (v0.1.0) | Message 4, install pages |
| 6 | Every command non-interactive with `--json`, stable documented exit codes | live | Agent audience |
| 7 | Reads are free, writes are paid | live (project copy) | Explaining pricing to callers |
| 8 | Website served from Arweave (`toon.ar.io`), not a rented host | live | Consistency proof: the brand practises the "no landlord" idea |
| 8a | The site's own Arweave write was bought through the mainnet node, with receipts on the proof page that check against a public chain | live | The strongest proof that "paid" is real. Link the receipt |
| 9 | A paid request answered from behind a home router with no port forwarding | **owed** | Message 1. The most important missing proof |
| 10 | Number of independent connector operators, paid packets per day | **owed** | Replace adjectives with numbers once they're real |

---

## 05 — Audience-specific messaging

### For independent developers and agent builders (primary)
- **What they care most about**: Getting a thing they built earning without becoming an ops team or a business. Keeping control of their code, price and money.
- **How to lead**: Lead with the outcome and what they don't need. *"Your machine. Paid per request. No server, no domain, no open port."* Then the nginx analogy, then the install command.
- **Proof that lands hardest**: The home-router demo (owed), "your app never touches the money", and a real `toon up` terminal session.
- **Avoid**: Protocol theory first, token talk, and anything implying TOON hosts or holds funds. Don't make agents the whole story, because people run models and APIs too.

### For agents operating or calling agent nodes (secondary)
Agents read docs, run the CLI and pay other agent nodes. They're a real audience, not a metaphor.
- **What they care most about**: Deterministic interfaces, machine-readable output, a price known up front, and no human step (signup, captcha, KYC).
- **How to lead**: Plain spec voice. *"`toon` is non-interactive. Every command accepts `--json` and prints one JSON document. Reads are free; writes are paid."* State what the agent node does. No persuasion.
- **Proof that lands hardest**: `--json` everywhere, stable exit codes, skills shipped for operating an agent node.
- **Avoid**: The "Hi agents! 👋" / "Are you an AI agent? Read our agents.md" move. ngrok, Apify and Lightning already do it, and it's a cliché now. Just make the docs good for machines.

### For connector operators and protocol peers (tertiary)
Nostr builders, Interledger people, and anyone who might run a connector or build a TOON app.
- **What they care most about**: Openness, a design that holds up, and not being captured by one company or one currency.
- **How to lead**: Lead with the architecture and the honesty. Connectors, packets with their own claims, hop-by-hop routing across tokens, and a clear live/next list. Credit Interledger openly as the lineage.
- **Proof that lands hardest**: The design, open source, NIP drafts, multi-chain settlement.
- **Avoid**: Tribal framing (Bitcoin-only, anti-Coinbase), or claiming a network size that doesn't exist yet.

---

## 06 — Messaging by channel

| Channel | Headline approach | Tone | Length |
|---|---|---|---|
| Website hero | "Your machine. Paid per request." over the supporting statement, then a real terminal session and a live/next block | Plain, confident, no superlatives | Short |
| README / docs hero | "Every request arrives paid." plus one paragraph on the reverse-proxy model, then install | Engineer to engineer, spec-like | Medium |
| Social bio | "Your machine. Paid per request. Open protocol, settling on Base and Solana." | Dry, factual | Very short |
| Email subject lines | Concrete change, not hype: "Your app can now take paid requests from behind a router" / "The store is priced on mainnet" | Direct, newsy | Short |
| Talks / pitch deck | Open on the three-product problem (tunnel + payment rail + public server) → one network → the route diagram → live/next | Measured, show-don't-tell | Medium |
| Paid ads | Hold until the home-router demo is live. Then "Charge for what runs on your machine." with a link to the demo | Blunt | Very short |
| CLI / spinner | Real state words ("Routing", "Signing", "Settled"), no marketing | Literal | One word |

---

## 07 — Things not to say

**Claims without proof**
- "No open port" in ads or headlines before the public demo exists.
- "Get paid" without the live label, or in a way that implies traffic, earnings or operators beyond what the live node shows.
- "Nobody in the middle" stated without qualification. Say "no company you sign up with; anyone can run a connector."
- Network-size words ("global", "thousands of nodes"), logo walls, or headline stats before the numbers are real.

**Category clichés** (from the competitor reports)
- "internet-native payments", "agentic commerce / economy", "economic infrastructure for AI", "the agents are here", "single line of code", "zero fees", "frictionless", "unstoppable", "the future of payments", "connect anything, anywhere", noun stacks like "Access. Identity. Checkout."

**Competitor-adjacent language**
- Retelling the HTTP 402 story (x402, Cloudflare). TOON settles on x402 channels, so say that plainly ("ILP routes, x402 settles") and don't present x402 as a rival or as TOON's own idea.
- "Get paid." as a sentence (Apify), "agents get paid" (Nevermined), "own your agent" (Olas), "mandate" (AP2), "fractions of a cent" (Mastercard), "unified interface" or "router" alone (OpenRouter). Say *what* routes: payments, hop by hop.
- "Hidden service" in headlines or ads, where it reads as Tor and darknet. It's TOON's defined term for the default reachability mode, so use it in docs and body copy, glossed on first use (see [voice.md](voice.md)). Never "onion" or ".onion".
- "Money moves like data" (Interledger). Say *"every packet carries its own payment."*

**Anything that contradicts the positioning**
- Leading with "cheaper". The claim is sovereignty, not price.
- Implying TOON hosts your code, holds your money, or takes a cut.
- Leading with "no account" alone, which L402 and x402 already say.
- Token or Bitcoin-first framing, or policy-mission framing.
- Separating "reachable" from "paid" anywhere above the fold.
