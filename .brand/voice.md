<!-- Copied verbatim from toon-protocol/brand: voice.md at commit a38284d0a97034a8a015d952ba2a6b204805dce5 (branch main). Edit it there, then copy it again. -->

# Brand Voice: TOON Protocol

*Drafted 2026-10-15. Sources: [context.md](context.md) (personality: direct, exact, independent, unhyped, practical), the live homepage at `website/index.html`, and the domain vocabulary in `toon_cli/CONTEXT.md`. This guide is the source of truth for how TOON sounds. The current homepage was an input, not the standard: its lines are kept here only where they pass these rules, and the site gets rewritten to match the guide. `CONTEXT.md` still wins on what things are called.*

---

## 01 — Voice overview

TOON writes the way a good engineer writes the README for something they actually run. It says what the thing does, what it costs, and what happens when you type the command, in that order. Most sentences are short and declarative, and each carries one fact. Nothing is promised that isn't shipped, and what's planned is labeled as planned. The reader is treated as a peer who will check: an operator, human or agent, about to put their own machine on the line. The brand doesn't sell; it shows the terminal and lets the output make the case.

> **Voice essence**: *TOON sounds like an engineer who runs the thing they're describing: direct, exact and unhyped.*

---

## 02 — Tone dimensions

**Formality: Casual ←——●—→ Formal**
- *Where TOON sits*: Slightly casual, never loose. Plain words, contractions in prose, but spec-level precision about names, numbers and behaviour.
- *In practice*: Write like a careful colleague, not a press office or a group chat.
- *Example*: "Your app doesn't need to know it's being paid for."

**Energy: Calm ●———— Energetic**
- *Where TOON sits*: Calm. Confidence comes from specifics, not intensity.
- *In practice*: No exclamation marks, no "finally", no countdowns. Let a number or a command carry the weight.
- *Example*: "The release binary runs on Linux, x86_64 or aarch64. Checksums ship with it."

**Humor: Serious —●——— Witty**
- *Where TOON sits*: Serious, with occasional dry understatement. Any humour comes from saying something exactly, never from jokes, puns or emoji.
- *In practice*: If a line is funny, it's because it's precise. At most one dry line per page.
- *Example*: "A refusal comes back as a value, not an exception."

**Expertise: Accessible ——●—— Authoritative**
- *Where TOON sits*: Authoritative about the mechanism, accessible in the words used to explain it. Expertise shows in what is left out, not in jargon.
- *In practice*: Explain a new idea with one familiar comparison (nginx terminating SSL), then use the exact term. Never explain twice.
- *Example*: "The connector sits in front of your app. It refuses an unpaid request with the price and passes on plain HTTP once the request is paid."

**Warmth: Distant ——●—— Intimate**
- *Where TOON sits*: Second person and respectful, not chummy. "Your machine", "your app", "your price". The warmth is in taking the operator's side.
- *In practice*: Talk *to* the operator about *their* things. Never "we're so excited", never "our community family".
- *Example*: "Your machine, your price. Every request that reaches your app is already paid for."

---

## 03 — Voice qualities

**Direct**
Lead with the outcome or the command, then the reason. One idea per sentence, with no warm-up and no wind-down.
- **Do**: "`toon up` installs a `systemd --user` service, so your agent node keeps running after you close the terminal."
- **Don't**: "To make things easier for you, we've built a handy way to keep your node running in the background!"

**Exact**
Name things by their defined names, give numbers as numbers, and say what a command actually prints. If a term has a definition in CONTEXT.md, use it exactly as defined.
- **Do**: "Every command that pays states its amount and needs `--yes`."
- **Don't**: "Payments are safe and you're always in control."

**Honest about state**
Say what is live and what isn't, in the same breath as the claim. Mainnet is mainnet. Devnet is devnet. Test tokens are test tokens.
- **Do**: "Mainnet on Base and Solana. Devnet for testing; the faucet funds it with test tokens."
- **Don't**: "Start earning today." (on a devnet page, or anywhere it implies paid traffic that isn't there)

**Unhyped**
No superlatives, no "revolution", no future-of-anything. The strongest TOON sentences are the plainest ones.
- **Do**: "No protocol fee."
- **Don't**: "Zero fees, zero friction, unlimited potential."

**Independent**
TOON takes the operator's side: their machine, their price, nobody's permission. That shows in what it refuses to need (account, domain, open port), not in attacks on anyone else.
- **Do**: "No cloud · no domain · no open port."
- **Don't**: "Unlike greedy Big Tech platforms…"

**Practical**
Every page should leave the reader able to *do* something. Show the command, the output and the next step.
- **Do**: "Your agent node is peered. Next, put an app behind it:" followed by the command.
- **Don't**: A paragraph about the vision of an open economy with no command in sight.

---

## 04 — Vocabulary

**Words we use**
- *your machine*, *your app*, *your price*, *your own hardware*
- *paid*, *already paid for*, *every request*, *per request*
- *price*, *charge*, *refuse / refusal* ("refuses an unpaid request with the price")
- *route*, *hop by hop*, *packet*, *channel*, *peer / peering*, *settle*
- *plain HTTP*, *ordinary HTTP*
- *reads are free, writes are paid*
- *live*, *devnet*, *mainnet*, *test tokens*, *next*
- *no cloud, no domain, no open port* (as a set)
- Verbs: *run, add, create, join, pay, price, route, settle, refuse*

**Words we avoid**
- Hype: *revolutionary, game-changing, seamless, frictionless, effortless, unleash, unlock, empower, supercharge, next-gen, world-class, unstoppable*
- Category clichés: *internet-native, agentic commerce / economy, the future of payments, the agents are here, single line of code, zero fees, trustless, web3*
- Vague filler: *solution, platform, ecosystem, leverage, robust, powerful, simply, just* (in instructions)
- Other brands' words: *mandate* (AP2), *onion / .onion* (Tor), *unified interface* (OpenRouter), *own your agent* (Olas), "Get paid." as a sentence on its own (Apify)
- Generic infra words that CONTEXT.md replaces: *gateway, terminator, daemon, deploy, spawn, backend, admin, user*

**Brand-specific language** (from CONTEXT.md, which wins on any conflict)

| Term | Use | Not |
|---|---|---|
| **Operator** | Whoever runs an agent node, human or agent | user, admin, customer, merchant |
| **Agent node** | Everything one operator runs on one machine. Always two words in docs. "Node" alone is allowed in navigation and CTAs ("Run a node") | hub, stack, full node |
| **TOON app** | A connector plus the apps behind it | an app on its own, deployment |
| **Connector** | The paid reverse proxy in front of a TOON app | gateway, proxy, terminator |
| **App** | The payment-oblivious HTTP service behind a connector | backend, service |
| **Hidden service** | The default reachability mode, an address inside the Anyone overlay. Gloss it on first use; see the rule below | onion service, dark node |
| **Clearnet** | Reachable at an ordinary public hostname, only by request | public mode |
| **Spending limit** | The most a wallet pays per command and per day | cap, budget |
| Whoever pays | "anyone", "a client" (in code), "an agent" | customer, buyer, shopper |

**Rule for "hidden service"**: It's the product's own defined term, so use it in docs, CLI output and body copy. On first use on any page, pair it with the plain meaning: *"reachable as a hidden service, with no open port and no public address."* Keep it out of headlines and ads, where a reader sees only the word, which reads as Tor and darknet. Never "onion" or ".onion"; the endpoint is an `.anyone` address.

---

## 05 — Writing style rules

**Sentence length**: Short by default, 8–15 words. One fact per sentence. A longer sentence is fine when it walks through a sequence ("accepts a packet, charges for it, and delivers it"), and it's followed by a short one.

**Punctuation**
- **Periods** do most of the work. Fragments are fine in lists and labels ("No SDK in your app.").
- **Colons** introduce the definition or the consequence ("Settles on Base and Solana: no single chain.").
- **Middle dots** (`·`) separate items in compact labels and footers ("No cloud · no domain · no open port").
- **Em dashes**: avoid. Use a colon, a comma or a new sentence.
- **Exclamation marks**: banned.
- **Ellipses**: banned, except in literal terminal output.
- **Oxford comma**: yes.

**Capitalization**: Sentence case everywhere, including headlines, buttons and nav. "TOON" is always all caps. Commands, flags, paths and units stay exactly as typed, in code formatting: `toon up`, `--json`, `systemd --user`.

**Numbers**: Numerals for every quantity, price, version and count ("2 units", "v0.1.0", "x86_64"). Spell out only *one* when it means "a single" in prose ("One channel reaches every app"). Prices state their unit or token. Never round a number up to sound bigger.

**Contractions**: Yes in marketing, social and email ("doesn't", "you'll"). Optional in docs; follow the page's existing style. Never in error codes or CLI output.

**Active vs passive**: Active, with the actor named: the connector refuses, the supervisor restarts, you set the price. Passive is acceptable only when the actor truly doesn't matter ("the mnemonic is shown once").

**Humor**: Rare and dry. It comes only from exact understatement. No puns on "toon", no cartoons, no memes, no emoji in product copy. Not funny at the operator's expense, and never about money lost.

**Claims**: Every claim is either live, or labeled with when it will be ("next: independent operators"). If you can't show it in a terminal or point to it in the source, cut it.

---

## 06 — Channel adaptations

| Channel | Tone adjustment | Example |
|---|---|---|
| Website homepage | The tightest version. Outcome plus absences, then the command | "Your machine. Paid per request. No cloud · no domain · no open port." |
| Docs / README | Spec voice. Define a term once, then use it. Show input and printed output | "`join` peers your connector toward the project's connector and opens the channel that pays for the hop." |
| Social media | Changelog voice. One shipped fact per post, with a command or number. Dry, no emoji, no hashtags beyond one | "Every `toon` command now takes `--json` and prints exactly one JSON document." |
| Email | Newsy and short. Subject is the change, body is what to run | Subject: "The store is priced on mainnet." Body: "Here's the price and the one command to pay it." |
| Support / Discord | Plain and patient, and precise about state. Ask for `toon status --json` before guessing | "Can you paste `toon status --json`? That shows which connector stopped and how often it restarted." |
| Error messages / CLI | Literal. What happened, the number, what to do next. No apology, no blame | "Refused: this command pays 1,200,000 and today's spending limit has 400,000 left." |
| Spinner / status words | Single real states | "Routing" · "Signing" · "Settled" |
| Addressing agents | Same voice with no persuasion. Interfaces, prices and exit codes | "Reads are free. Writes are paid. Every command accepts `--json`." |

---

## 07 — Before and after

**1. Hero**
> **Before**: "The future of agentic payments is here! Unlock frictionless, internet-native monetization for your AI agents with zero fees."
>
> **After**: "Your machine. Paid per request. Run your app or agent where it already lives. Every request that reaches it has been paid for."

**Why it works**: It drops five clichés for one concrete outcome that the reader can check.

**2. Explaining the connector**
> **Before**: "Our powerful gateway seamlessly handles all payment complexity so you can focus on what matters."
>
> **After**: "The connector sits in front of your app and refuses an unpaid request with the price. Your app only ever sees plain HTTP that's already paid for."

**Why it works**: It names the component correctly and says exactly what it does with a request.

**3. Status honesty**
> **Before**: "Start earning USDC from your home server today."
>
> **After**: "Live on Base and Solana mainnet, in USDC. Devnet runs on test tokens. This site's own write was paid for; the receipts are on the proof page."

**Why it works**: The honest version costs nothing now and protects every later claim.

**4. Error message**
> **Before**: "Oops! Something went wrong with your payment. Please try again later."
>
> **After**: "Refused: the peer's channel has 0 left. Top it up with a deposit, or route through another peer."

**Why it works**: The operator learns what failed, by how much, and what to do. (Replace the remedy with the real command once it's final.)

**5. Talking about competitors**
> **Before**: "Unlike centralized rails controlled by Big Tech, TOON is truly decentralized and unstoppable."
>
> **After**: "TOON settles on x402 channels. What it adds is the route: hop by hop, to an app on your own machine, with no account to open."

**Why it works**: It states TOON's relationship to x402 as a fact, without a sneer and without "decentralized". (Every TOON channel is an x402 batch-settlement channel.)

---

## 08 — Things we never say

- **Hollow hype**: "revolutionary", "game-changing", "world-class", "next-generation", "the future of…", "unstoppable", "massive".
- **Category clichés**: "internet-native payments", "agentic commerce", "economic infrastructure for AI", "the agents aren't coming, they're here", "in a single line of code".
- **Unprovable absolutes**: "zero fees" (there's gas; say "no protocol fee"), "fully decentralized", "trustless", "100% private", "censorship-proof".
- **Network-size bluffing**: "global network", "thousands of nodes", logo walls or traffic stats before they're real and sourced.
- **False urgency**: "limited spots", "don't miss out", "early bird", token-launch countdowns.
- **Over-apology and cheer**: "Oops!", "Uh oh", "We're so sorry for the inconvenience", "Yay", "🚀".
- **Talking down or talking crypto**: "WAGMI", "gm", "number go up", "to the moon", "ser". Also no explainer of what a wallet is aimed at people who already run one.
- **Sneering at competitors**: "Big Tech", "greedy platforms", "legacy dinosaurs". State the difference as a fact.
- **The agent gimmick**: "Hi agents! 👋", "Are you an AI agent? Read our agents.md". Write docs that machines can use, and don't perform it.
- **Payment drama**: "get rich", "passive income", "make money while you sleep". TOON is pricing for a service, not a hustle.
