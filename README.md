# website

The source of [toon.ar.io](https://toon.ar.io), the TOON Protocol landing page.

The site is one file, `index.html`, with no scripts, no external assets and no build
step. It is stored permanently on Arweave and reached through the ArNS name `toon`.
Each revision is bought as a paid TOON write through the live node, and embeds the
receipts of the revisions before it (the "Proof" section of the page).

## Preview

```sh
python3 -m http.server 8765
# open http://127.0.0.1:8765/
```

## Before publishing a revision

1. **Prices.** The pricing table is a snapshot read off the live node's `GET /ilp`. Reread
   it and update the date in the table's caption and footnote if it changed.
2. **Release tag.** The Docker tag in "Run a node" is the connector's latest release
   (`gh release list -R toon-protocol/connector`).
3. **Receipts.** Add the revision being replaced to the "Proof" list and to the JSON in
   the `<details>` block: its Arweave transaction id (the `x-arns-resolved-id` header of
   `curl -sI https://toon.ar.io`), `sha256sum` of the file as served, byte size, the
   claim on each hop, and the block date. A page cannot contain its own hash, so this is
   always done for the previous revision, never the current one.
4. **Links.** Every external link must answer 200:
   ```sh
   grep -o 'href="https\?://[^"]*"' index.html | sed 's/href="//;s/"$//' | sort -u \
     | while read u; do printf '%s %s\n' "$(curl -s -o /dev/null -w '%{http_code}' -L "$u")" "$u"; done | grep -v '^200'
   ```
   (npmjs.com answers 403 to curl; check it in a browser.)
5. **No scripts.** `grep -c '<script' index.html` must print 0. The page says so.

## Publishing

The write goes through the store app behind the live node, paid by the KiB with a
voucher on an x402 channel, then the ArNS record `toon` is pointed at the new
transaction id. The first paid writes are documented at
[boughtviatoonnode.ar.io](https://boughtviatoonnode.ar.io/).

## History

Revisions 1 to 8 (2026-08-27 to 2026-10-03) were authored directly as HTML and are
listed, with receipts, in the page itself. This repository starts at revision 9.
