# Sam's journal — first TOON node, 2026-10-13
Start: 22:26Z

## 1. Journal

### 22:26Z — Home page (https://toon-protocol.github.io/website/)
- Friend said "paid reverse proxy, run your own node as a hidden service". Home page agrees: "A paid reverse proxy. It terminates payment the way nginx terminates TLS." Good, that's a sentence I understand.
- Hero: "The caller pays with a signed voucher." — **voucher** used in sentence 3 of the site, undefined. Guessable, but I'm guessing.
- Diagram: "POST /ilp + voucher 1,000" — **ILP** / `/ilp` appears as a path with no explanation of what ILP is. The word "Interledger" shows up only in the footer chips and the FAQ.
- "Run a node in three steps ... docker pull ... openssl rand -hex 32 > data/signer.key ... docker compose up -d" — but no compose file shown on the home page; it says "The operator guide covers that". Fine, it's a landing page.
- Hidden services on the home page: the only mentions are "a node can run at an onion address" (Only TOON section) and the anytoon card "reached at a hidden-service address". **onion address** is used but TOON doesn't use Tor; I only learn later it's Anyone/.anyone. The nav has no "Hidden services" link; it's in the docs sidebar only.
- The spaceturtle card says "No cloud, no domain, no open port." — that's the thing my friend meant, but it's an *agent* product; I want to run the node myself.
- "Settles on Base and Solana" + footer chips "Base mainnet / Solana mainnet / Base Sepolia · Solana devnet" — I'm nervous the defaults are mainnet. Noted to check.
- FAQ "Where do I find other nodes and apps?" → "There is no discovery layer by design (ADR 0046)". So to buy a request from "somebody else's node" I need a URL from somewhere. The devnet reference turns out to have them.

### 22:32Z — Docs > Overview (docs/index.html)
- "Pick your path" has four cards. Mine is two of them at once ("I have an app to charge for" + "I want to pay for requests"). The hidden-service card is "I want an agent to run it — spaceturtle runs a node from your own machine as a hidden service". So the site's answer to "run a hidden service" is "let the agent do it". There is no path card for "I want to run a hidden service myself".
- Overview: "Underneath, the node is an Interledger connector: value arrives wrapped in a protocol your app never speaks" — first time ILP is expanded, and only by implication (Interledger ≈ ILP is never stated on the Overview; Concepts says "ILP address").
- "Concepts defines each of those words." — good, a glossary exists. I read it. It is honestly the best page on the site. But it is one click away from where the words are first used.

### 22:35Z — Docs > Run a node
- Clear. Compose file, TOML, `curl http://localhost:3000/ilp`. Two things I'd not have known: named volume for /app/state (bind mount "arrives root-owned and the connector refuses to start"), and `command: ['/app/config/connector.toml']`.
- The compose example includes `quotes:` and `search:` services with `image: your-quotes-app:latest`. I have no app yet. The page doesn't say what to do if you just want the node up first (answer: delete them; the routes would then point at nothing).
- "This minimal config's own self-description has no endpoints and nothing to dial." — I don't know yet what "endpoints" are or whether I need them for a hidden service. (Answer, from Hidden services + off-site runbook: yes, that's exactly the thing.)
- "A TOON node refuses plaintext peers" — does that mean a hidden service, which has no TLS, can't peer? Unanswered on this page. (The runbook later says .anyone endpoints are http:// and that's allowed.)
- No mention of hidden services on the Run a node page at all. Not even a "see also".

### 22:38Z — Docs > Hidden services
- Title: "Paying a node that lives at a .anyone address." It's filed under *Callers*. The operator part is the last paragraph, "Running one": "On the node's side, the connector publishes its .anyone address as its endpoint and reaches onion peers through its own socks_proxy. The connector repository's onion endpoint bring-up is the operator runbook, and spaceturtle does all of it for you."
- That is the whole of the operator content. No config keys, no anon torrc, no port numbers, no "which port of the connector does the hidden service point at", no "how do I know it's published". **I must leave the site** → github.com/toon-protocol/connector/blob/main/docs/operators/onion-endpoint-bringup.md.
- Words used before definition on this page: **anon daemon**, **SOCKS5h port**, **overlay**, **socks_proxy** (a config key, never shown in any TOML on the site), **onion peers**.
- Useful: the "managed daemon" section tells me what `npx toon` will download (anon v0.4.10.2, sha256-checked, cached under $XDG_CACHE_HOME/toon/anon). I like that.

### 22:40Z — Docs > Pay a node, Devnet reference
- Pay a node is a proper walkthrough: `npm install @toon-protocol/client`, `npx toon init`, `faucet`, `channel open --deposit 100000`, `send --body hello`. Node 22+. Keystore at ~/.toon/keystore.json. Good.
- Devnet reference gives me the three "somebody else's" nodes. This answers the FAQ's "no discovery layer" for devnet; the FAQ should link here.
- Concern: Pay a node doesn't say *which chain* the CLI will pick on devnet (Base Sepolia vs Solana devnet) or how to force it. The TypeScript says "picks a chain". I'll find out.

### 22:28Z — Doing: install the client (Pay a node page)
- `npm install @toon-protocol/client` → v5.0.0, fine.
- `npx toon --help` → `npm error could not determine executable to run`. The package's only bin is **`toon-client`** (`"bin": {"toon-client": "./dist/cli/main.js"}`). **Every `npx toon …` command on Pay a node, Hidden services, Devnet reference and CLI reference is wrong for the published package.** Worse, `npx toon` with no such local bin asks the npm registry for a package called `toon` — that's a typosquat waiting to happen. I used `npx toon-client` from here on.
- Expected: the exact command on the site to work.

### 22:29Z — Doing: Run a node (docs/run-a-node.html)
- Followed the page literally: `mkdir -p node/config node/data`, `openssl rand -hex 32 > data/signer.key && chmod 600 data/signer.key`, the compose file verbatim (port changed to 127.0.0.1:33000, their `quotes`/`search` placeholder apps replaced with one `hashicorp/http-echo`), the TOML with one route `g.sam.echo`.
- `docker compose up -d` → connector in `Restarting (1)`. Log: `failed to read signer key_file at /app/data/signer.key: Permission denied (os error 13)`.
- Cause: the page says "The image runs as uid 10001" and *also* tells me to `chmod 600` a file owned by me. The two instructions are three lines apart and contradict each other. The page warns about this exact ownership trap for `/app/state` ("A host bind mount arrives root-owned and the connector refuses to start") but not for the key it just told me to create.
- Fix I used: `chmod 644 data/signer.key` (world-readable signing key — not what I want on a real box; the honest fix is `chown 10001` which needs root, or `user:` in compose, and the page should say which).
- After restart: `GET http://127.0.0.1:33000/ilp` answers:
  `{"peerCarriages":[],"edgeIdentity":{"keyId":"connector-signer","publicKey":"0x04a7fe…"},"routes":[{"prefix":"g.sam.echo","price":"1000"}],"supportedVersions":[1],"defaultVersion":1}`
- **Node runs. GET /ilp answers.** 10 minutes, one trap.
- No settlement block yet, so nobody can actually pay me; the page says so ("A route with a price is only half of being paid"). For tonight the goal is reachability, so I'm leaving it.

### 22:31Z — Reading the off-site runbook (connector/docs/operators/onion-endpoint-bringup.md)
- Had to leave the site. The runbook is long (~300 lines), written for the project's own fleet ("No box on this fleet runs one", "Run `make local-verify LOCAL_TOPOLOGY=onion` before you run this" — I can't, I don't have the repo checked out and don't want to). But the actual operator content is small and should be on the Hidden services page:
  1. run `anon` beside the connector; `AgreeToTerms 1` in `anonrc` or it exits;
  2. `HiddenServicePort 80 <fixed-ip>:3000` — target resolved at parse time, daemon *crashes* on an unresolvable name;
  3. `HiddenServiceDir` on a persisted volume or the address changes on every restart;
  4. read `HiddenServiceDir/hostname` after `Bootstrapped 100%`;
  5. write `[node] http_endpoint = "http://<56>.anyone/ilp"` (and `addresses`), plus `peer_expose = "http"` (that key is on the *Peering* page, not the runbook, not Hidden services);
  6. `socks_proxy = "socks5h://…"` at root level, *before any [table]*, only if the node dials other .anyone nodes;
  7. plaintext `http://` is allowed for `.anyone` hosts without `peer_allow_plaintext_endpoints`.
- The runbook says "ghcr publishes no image for it" and points at `local/anon-image/` Dockerfile in the repo. The site's Hidden services page says the client downloads `anon-live-linux-amd64.zip (v0.4.10.2)` but not from where. **Left the site again**: found it at github.com/anyone-protocol/ator-protocol/releases. Ran the binary from my scratch dir instead of building a Docker image.
- Words met here before definition: **TLD era**, **carriage** (defined on Concepts, but not where I came in), **peer_expose**, **BTP**, **rendezvous**, **descriptor**.

### 22:30Z — Doing: the hidden service (off-site runbook + Hidden services page)
- Wrote `anonrc` by hand from the runbook's scattered facts: `AgreeToTerms 1`, `SocksPort 127.0.0.1:39050`, `HiddenServiceDir <scratch>/anon-data/hs`, `HiddenServicePort 80 127.0.0.1:33000`. Ran the downloaded `anon` binary directly. `Bootstrapped 100%` in 44 s. `hs/hostname` → `6z666pmpzho3pxj3nxlh4q3imhbfjifanreo2kunc36rie4j3omsh3id.anyone`.
- Nothing on the site says which connector port the hidden service should forward to (answer: `client_edge_addr`, i.e. 3000 in the container / my 33000 host port) or that virtual port 80 is what makes `http://<addr>.anyone/ilp` work without a `:port`. I guessed from the runbook's `http://<56-char-address>.anyone/ilp` example.
- Edited `connector.toml`: `peer_expose = "http"` at the top (a key the *Peering* page introduces; neither the Hidden services page nor the runbook tells you to set it, but the runbook says `http_endpoint` is "required whenever anything is exposed", and without `peer_expose` the self-description keeps `"peerCarriages": []`), plus `[node] addresses = ["g.sam"]` and `http_endpoint = "http://<addr>.anyone/ilp"`. Restart: clean. Local `GET /ilp` now shows the .anyone endpoint and `"peerCarriages":["http"]`.
- First `curl --socks5-hostname 127.0.0.1:39050 http://<addr>.anyone/ilp` timed out at 90 s (~1 min after bootstrap). Second try ~2.5 min after bootstrap: **HTTP 200 in 2.3 s**, body is my node's self-description. The daemon log says nothing about publishing the descriptor, so there is no way to know when to try other than trying. The runbook mentions `--dry-run` on `connector send` "to ask has a rendezvous happened yet", which I don't have (I run the image, not the binary).

### 22:33Z — Doing: buy one request from somebody else's node (Pay a node page)
- `npx toon-client init --password-file …` → phrase printed once, keystore at `<HOME>/.toon/keystore.json`, EVM `0x08F6…8dC0`, Solana `HerZ…km1L`. (`--password-file` isn't mentioned on the site; `init` prompts otherwise. Fine for a human.)
- `faucet` → "Faucet request accepted. chain evm". `balances` → `USDC 1000000000 (1000 USDC)`, `ETH 0`. (1000 devnet USDC is generous.) Solana side: 0 — the faucet only funded the chain the CLI picked, and nothing told me it picked EVM until the output said so.
- `channel open --deposit 100000` against `https://proxy.ario.devnet.toonprotocol.dev` → `Channel open. channel 0xb878…ac7e network eip155:84532 deposit 100000 (0.1 USDC)` in **3.0 s**, with zero ETH. The gasless deposit via the facilitator genuinely works and that is impressive.
- `send --body 'hello from sam' --json` → `"fulfilled": true, "status": 422, "text": "{\"accept\":false,\"code\":\"F00\",\"message\":\"Invalid request body\"}", "claim": {"cumulative":"1010","amount":"1010"}`. Exit 0, 1.2 s.
- **I bought a request. It cost 1010 base units = 0.00101 USDC (1000 + 10/KiB).** The app answered 422 and I paid for it, as the page warned ("A 404 from the app is a real, paid answer").
- But: the Pay a node page shows this exact command producing `"text": "delivered by stub app: json please"`. The live devnet store is not a stub: it wants `{ "event": { ...a signed Nostr event... } }` (store README, off-site). So the page's only worked example fails against the node the page itself names. Expected: an example body the devnet store accepts, or a devnet route that echoes.
- `channel status --connector-view` → `signed 1010 … connector claimed 1010 … available 98990`. Both sides agree. Good.

### 22:36Z — Doing: can another client reach my node at the .anyone address?
- Own daemon: `npx toon-client describe http://<addr> --socks socks5h://127.0.0.1:39050` → `toon-client: a keystore password is needed and stdin is not a terminal to ask on`. The help text says `describe … Free, needs no keys.` It needs the keystore anyway. Added `--password-file`.
- Managed daemon (the Hidden services page's headline path, `TOON_CONNECTOR=http://<addr>.anyone npx toon describe`): stderr matches the page's transcript line for line: `downloading anon-live-linux-amd64.zip (v0.4.10.2)… verified; extracting … starting anon v0.4.10.2 on 127.0.0.1:41057 … proxying through socks5h://127.0.0.1:41057`. Cached under `$XDG_CACHE_HOME/toon/anon/v0.4.10.2/` exactly as documented. Second run reused the cache. 41 s to reach the node, then:
  `toon-client: This connector publishes no settlement chains at all, so there is no channel to open and nothing can be paid for.`
- So: **yes, a second client reached the node at its .anyone address, both through my daemon and through the client's managed daemon.** But `describe` and `price` refuse to *show* a node that has no settlement block, so the "minimal config" from Run a node is one a client can't even describe. The Run a node page says the minimal config "has no endpoints and nothing to dial" but doesn't say the client will refuse it outright.
- Hand-rolled unpaid `POST /ilp` via curl → `400 invalid packet type byte: expected 12 (PREPARE)…`. The home page's "An unpaid request gets an x402 402 Payment Required" is true only for an ILP packet, not for a curl. A curl-and-jq person cannot see the greeting without the client.

### 22:38Z — Doing: the full loop, pay MY hidden node (Get paid + Hidden services)
- Added the Get paid page's "devnet values" `[settlement.evm]` block verbatim plus `facilitator_url = "https://onboard.devnet.toonprotocol.dev"` and a fresh `settlement.key` (same openssl line; same chmod trap). Node restarted clean; `GET /ilp` now has `batchSettlements[0].payTo = 0xb2e1…15c7`, `facilitator = https://onboard.devnet.toonprotocol.dev`, `voucherSigners`. The settlement key holds no ETH and the node boots anyway (EVM only; the page says Solana would not).
- `TOON_CONNECTOR=http://<addr>.anyone npx toon-client describe --json` via the managed daemon → my self-description, exit 0.
- `channel open --deposit 50000` against the .anyone URL → `Channel open. 0xda7e…df6e network eip155:84532 deposit 50000 (0.05 USDC)` in **8.5 s**, through the overlay, via the Onboarder facilitator, with zero ETH. That is the moment this stopped being a toy to me.
- `send --body 'knock knock'` (no destination, as Pay a node says is "deliberate") → exit 2: `This connector prices no route covering "g.sam", so there is no amount to put on the packet.` My `[node] addresses = ["g.sam"]`, my route is `g.sam.echo`. The devnet store's trick only works because its address *is* its route prefix (`g.toon.store`). Nothing on Run a node or Pay a node says to make them equal, or to pass the prefix.
- `send g.sam.echo --body 'knock knock' --json` → `{"fulfilled":true,"status":200,"text":"hello from sam\n","claim":{"channelId":"0xda7e…","chain":"evm","cumulative":"1000","amount":"1000"}}` in 8.3 s. `channel status --connector-view`: `signed 1000 / connector claimed 1000`.
- **A paid request reached my app behind my hidden-service node, through two anon daemons, for 0.001 devnet USDC.**
- My node's own log over these 5 minutes: one line (`connector listening`). No "channel admitted", no "claim accepted" at default log level. The only way to see I was paid is `[operator]` + a bearer token (operator surface page), which I never set up. From the operator's chair the node is silent when it works.

### 22:44Z — Gate (b) and teardown
- Restarted my `anon` (and, by a sloppy `pkill -f`, my own shell once). `hs/hostname` before and after: `6z666pmpzho3pxj3nxlh4q3imhbfjifanreo2kunc36rie4j3omsh3id.anyone` both times. Address persists because `HiddenServiceDir` is on disk.
- `docker compose down -v`: volume `sam-toon_connector-state` and network removed. My anon pid gone. `pgrep -x anon` shows only the host's own daemon under `~/.toon/agent-node`, which I never touched. No `sam-toon` containers, volumes or networks remain. No `toon-client` processes. Scratch dir left in place: `node/`, `anon-data/`, `anon-dl/`, `client/`, `home/`, `site/`, `offsite/`, `journal.md`.
- Nothing broken on the host that I know of. The one thing I could not clean is the 0.1 + 0.05 devnet USDC I left locked in two channels (`0xb878…ac7e` to the devnet store, `0xda7e…df6e` to my own, now-gone node). Leaving a channel needs Base Sepolia ETH, which I have none of, and the site says so. Devnet, worth nothing. On mainnet that second deposit would be stranded forever, since the receiver node no longer exists — and the Pay a node page's "Never delete that file for a live channel" is the only hint of this.
- End: 22:46Z. About 20 minutes of wall clock for the whole thing, plus reading.

## 2. Where I had to leave the site

| # | Where I went | Sent by | What I needed | Should it have been on the site? |
|---|---|---|---|---|
| 1 | `github.com/toon-protocol/connector/blob/main/docs/operators/onion-endpoint-bringup.md` | Hidden services, "The connector repository's onion endpoint bring-up is the operator runbook" | Everything about running a hidden service as an operator: `AgreeToTerms 1`, `HiddenServicePort` → connector port, persisted `HiddenServiceDir`, `cat hostname`, `[node] http_endpoint = http://<addr>.anyone/ilp`, `socks_proxy` rules | **Yes.** The ~12 lines an operator needs are buried in a 300-line fleet runbook that opens with "No box on this fleet runs one" and "run `make local-verify` before you run this". |
| 2 | `github.com/anyone-protocol/ator-protocol/releases` | Nobody. The Hidden services page names `anon-live-linux-amd64.zip (v0.4.10.2)` but not where it comes from; the runbook says "ghcr publishes no image" and points at a Dockerfile inside the connector repo | The `anon` binary | **Yes**, one link: "anon is Anyone Protocol's Tor fork; releases at …; the client downloads the same zip." |
| 3 | `npx toon-client --help` and `help <cmd>` (the program, not the web) | Nobody; `npx toon` failed | The real bin name; `--password-file`; `--socks`; `price <destination>`; `--chain` | **Yes** for the bin name (every page is wrong). The CLI reference page does list `--password-file` and `--socks`, I just hadn't needed it until the command failed. |
| 4 | `github.com/toon-protocol/store` README | Nobody; the Pay a node example returned a paid 422 | What body the devnet store accepts (`{ "event": { …signed Nostr event… } }`) | **Yes**: the page's only worked example should work against the node it names, or say "the store will refuse an arbitrary body with 422 and charge you; this is the proof the request was paid". |
| 5 | Peering page (on-site, but not where I was sent) | Nobody; `peerCarriages: []` after following Hidden services + runbook | `peer_expose = "http"` | The Hidden services operator section should list it with `[node]`. |

## 3. Words I met before they were defined

| Word | Page | Sentence |
|---|---|---|
| voucher | Home, hero | "The caller pays with a signed voucher. Your app sees a plain HTTP request." |
| ILP / `/ilp` | Home, diagram | "POST /ilp + voucher 1,000" — never expanded on the home page; "Interledger" is a footer chip |
| x402 channel / batch-settlement | Home, diagram | "Vouchers settle in batches on an x402 channel on Base or Solana." (I'd heard of x402; "channel" and "batch-settlement" are new) |
| sealed / unseals | Home, step 3 | "The node checks the voucher, unseals the request and forwards it." |
| settlement block | Home, "Price a route" | "A settlement block names the token you want to be paid in" |
| peering / peers | Home, "Start it" + Run a node | "a TOON node refuses plaintext peers" |
| onion address | Home, "Only TOON" | "a node can run at an onion address" — TOON uses `.anyone`, not Tor; the word `.anyone` first appears on the Hidden services page |
| endpoints | Run a node | "This minimal config's own self-description has no endpoints and nothing to dial." |
| peer_expose | Run a node | "once [node] and peer_expose are set" — neither is shown on that page |
| greeting | Get paid, "The shape" | "Nothing: GET /ilp, or the 402 greeting on an unpaid request." (Concepts defines it; I read Concepts first only because I'm the type who does) |
| carriage, BTP | Devnet reference | table column "Carriage", values "HTTP or BTP", "BTP only" |
| anon daemon, SOCKS5h, overlay | Hidden services | "Paying such a node needs one extra thing: a running anon daemon, and its SOCKS5h port." |
| socks_proxy, onion peers | Hidden services | "the connector publishes its .anyone address as its endpoint and reaches onion peers through its own socks_proxy" |
| facilitator | Pay a node, step 2 | "On Base an x402 facilitator relays the deposit and pays for it" |
| watermark | Pay a node, step 6 | "the connector accepts it only if it advances the connector's own watermark" |
| sealTo | Devnet reference | "you name the far node yourself with sealTo" |
| claim | Pay a node, step 5 JSON | `"claim": {…}` — Concepts says "Voucher (also claim)"; the site uses both |
| TLD era, rendezvous, descriptor | off-site runbook | — |

Not met tonight: zone, Persona, Observer (only listed in Concepts' "Agent node" line as "in spaceturtle"); I never needed the spaceturtle page.

## 4. Outcome

| Question | Answer |
|---|---|
| Did the node run? | **Yes.** `ghcr.io/toon-protocol/connector:rust-2026.09.29.1` on `127.0.0.1:33000`, one route `g.sam.echo` → `hashicorp/http-echo`. First boot crash-looped on `signer.key: Permission denied` (site's `chmod 600` vs. image uid 10001); fixed with `chmod 644`. |
| Did `GET /ilp` answer? | **Yes**, locally at once, and later with `ilpAddresses: ["g.sam"]`, `httpEndpoint: http://6z66….anyone/ilp`, `peerCarriages: ["http"]`, one `batchSettlements` entry on `eip155:84532`. |
| Did it become a hidden service? | **Yes.** `anon` v0.4.10.2 (downloaded from the Anyone Protocol GitHub releases, run from scratch dir), `HiddenServicePort 80 127.0.0.1:33000`, `Bootstrapped 100%` in 44 s, address `6z666pmpzho3pxj3nxlh4q3imhbfjifanreo2kunc36rie4j3omsh3id.anyone`. The address survived a daemon restart. The node published that address in `[node] http_endpoint`. |
| Could another client reach it at the `.anyone` address? | **Yes, three ways.** (a) `curl --socks5-hostname 127.0.0.1:39050 http://<addr>.anyone/ilp` → 200 in 2.3 s, but only ~2.5 min after bootstrap; the first try at ~1 min timed out at 90 s. (b) `toon-client describe --socks …` via my daemon. (c) `TOON_CONNECTOR=http://<addr>.anyone toon-client describe` with the client's managed daemon, which downloaded, verified and started its own `anon` exactly as the site's transcript shows (41 s first time). Before I added a settlement block, (b) and (c) refused to print anything: "This connector publishes no settlement chains at all". |
| Did I buy a request from a devnet node, and what did it cost? | **Yes.** From `https://proxy.ario.devnet.toonprotocol.dev` (the devnet store): channel `0xb878…ac7e` opened on Base Sepolia with 0.10 devnet USDC and zero ETH in 3.0 s; `send --body 'hello from sam'` → `fulfilled: true, status: 422, "Invalid request body"`, **cost 1010 base units = 0.00101 devnet USDC** (1000 + 10/KiB), 1.2 s. Paid for a refusal from the app because the site's example body is not what the live store accepts. |
| Bonus: did I buy a request from my own hidden node? | **Yes.** Channel `0xda7e…df6e`, 0.05 devnet USDC, opened through the overlay via the Onboarder facilitator in 8.5 s; `send g.sam.echo --body 'knock knock'` → `200 "hello from sam\n"`, **cost 1000 base units = 0.001 devnet USDC**, 8.3 s; connector watermark agrees. `send` with no destination failed with `prices no route covering "g.sam"` because my address isn't my route prefix. |
| What didn't work, and why | `npx toon` (bin is `toon-client`). `chmod 600 signer.key` with uid 10001. The site's `send --body 'hello'` against the store (422). `describe` on a settlement-less node. Seeing the greeting with curl (`400 invalid packet type byte`). Seeing that I was paid from the node's log (silent at default level; needs `[operator]`). Leaving the two channels (no Sepolia ETH; deposits stranded, devnet so irrelevant). |

## 5. Top ten changes to the site, ranked

1. **Hidden services page: add an operator section with the whole recipe.** Title it for both roles ("Running and paying a node at a .anyone address"). Under "Running one", show the four-line `anonrc` (`AgreeToTerms 1`, `SocksPort 127.0.0.1:9050`, `HiddenServiceDir /var/lib/anon/hs`, `HiddenServicePort 80 <connector-ip>:3000`), then `cat …/hs/hostname`, then the three TOML keys (`peer_expose = "http"`, `[node] addresses`, `http_endpoint = "http://<addr>.anyone/ilp"`), then "wait 2–3 minutes after `Bootstrapped 100%`; verify with `toon-client describe http://<addr>.anyone --socks socks5h://127.0.0.1:9050`". Say the compose sidecar is ~15 lines and show it. Keep the link to the runbook for the fleet-grade detail.

2. **Every page: `npx toon` → `npx toon-client`** (Pay a node, Hidden services, Devnet reference, CLI reference, the home page's "Paying is one install"), or ship a `toon` bin alias. Add a one-liner: "The package's executable is `toon-client`; `npx toon` is a different package."

3. **Run a node: fix the key-permissions trap in the shell block.** Replace `chmod 600 data/signer.key` with "the image reads it as uid 10001: `chmod 600 data/signer.key && sudo chown 10001 data/signer.key`" (or "`chmod 640` and `user: 10001`"), and move the "runs as uid 10001" sentence above the openssl line. Mention it applies to `settlement.key` too.

4. **Pay a node: make the worked example work.** The store returns a paid 422 to `--body 'hello'` and the page shows "delivered by stub app". Either point step 4 at a devnet route that echoes, or show the real output and say: "the store wants a signed Nostr event; an arbitrary body is a real, paid 422 — which is itself the proof you paid." And replace the stub-app JSON with what the devnet actually returns.

5. **Pay a node + Run a node: say when `send` needs a destination.** On Pay a node: "Omitting the destination works when the node's ILP address is also its priced route, as the devnet store's is. Otherwise name the route: `toon-client send g.your.route`." On Run a node, in the TOML: "`[node] addresses` — if you set it to your route prefix, callers can omit the destination."

6. **Run a node: include the devnet settlement block, or warn that the minimal config is unusable by the client.** Add one sentence after `curl http://localhost:3000/ilp`: "Until you add a settlement block (next page), `toon-client describe` and `price` refuse this node with 'publishes no settlement chains'; a client cannot pay a node that doesn't say how." Better: make the 8-line Base Sepolia block part of the page's TOML, labelled devnet.

7. **Home page + Overview: define the first use of each word inline.** Hero: "The caller pays with a signed voucher — an IOU against a deposit it locked on chain, which your node redeems in batches." Diagram: "`POST /ilp` (ILP, Interledger, is the packet format a node speaks; your app never does)". "Only TOON": "a node can run at a `.anyone` hidden-service address (Anyone Protocol, a Tor fork)" instead of "onion address". Link each first use to Concepts.

8. **Home page, "What happens to an unpaid request" / "The refusal names the price": say you can't see it with curl.** Add: "The 402 is carried inside an ILP packet. To see a node's prices from a shell use `curl …/ilp | jq .routes` or `toon-client price <route>`; a raw `curl -X POST /ilp` gets `400 invalid packet type byte`."

9. **Hidden services: name the daemon and where it comes from, and what the operator pays.** "`anon` is Anyone Protocol's Tor fork; releases at github.com/anyone-protocol/ator-protocol; the client downloads `anon-live-linux-amd64.zip` from the same place. v0.4.10.2 publishes `.anyone`; older builds publish `.onion` and the two cannot reach each other." Also: "A channel can be opened to a hidden node through the overlay; expect ~10 s rather than ~3 s."

10. **Get paid / operator surface: tell the operator how to see they were paid.** Run a node and Hidden services both end with the node running and silent. Add to Run a node's "Start it" step: "At default log level the node prints nothing when it is paid. To watch claims, set `[operator] bearer_token_file` and read `GET /claims` (The operator surface), or set `RUST_LOG=debug`." And in Pay a node step 6, say plainly: "Opening a channel to a node that later disappears strands the deposit; leaving needs native gas (Sepolia ETH / devnet SOL) that the faucet does not give you."

Runners-up: Overview "Pick your path" needs a fifth card, "I want to run a hidden service myself" → Run a node then Hidden services; FAQ "Where do I find other nodes" should link the Devnet reference; Pay a node should say the CLI picks the first chain the node offers that you hold a key for (EVM here) and that `faucet` funds only that chain, with `--chain solana` for the other; the Hidden services page should say descriptor publish takes a couple of minutes and the daemon log doesn't tell you when.

## 6. Verdict

Would I keep this node running? Honestly, yes, as a toy on the Hetzner box, and I'm surprised to be saying that. The product did more than the site led me to expect: a gasless channel opened to my own hidden-service node through two anonymity daemons in eight seconds, and a paid request came back with the app's answer and a receipt that both sides agreed on. That is the thing my friend described and it works. What nearly stopped me was the site, not the software: the command it tells me to type doesn't exist (`npx toon`), the key it tells me to create can't be read by the container it tells me to run, the one worked example buys a 422, and the page called "Hidden services" contains zero operator instructions and sends me to a fleet runbook that opens by telling me not to use it. I got through because I'm comfortable reading other people's runbooks and `--help`, and because the Concepts page is good. Someone one notch less patient leaves at `npx toon`. I would not point real money at it yet: I have no idea how to see that I was paid without setting up an operator surface the Run a node page never mentions, and I left two deposits stranded with no way to get them back, which on mainnet would have been my fault for following the docs.
