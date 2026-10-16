# 0001 — One CI secret, and the Base key derived from it

**Status:** accepted, 2026-10-16.

## Context

CI publishes toon.ar.io through TOON (`.github/workflows/publish.yml`, `.publish/`). A publish
needs two keys on two chains:

- **Solana**: the ArNS name `toon` is a Solana ANT (`H5VJzteoQ1t2sZ1VgWvE1XDbyMKY9Qk4eZY6EBcKx8mn`).
  Changing its record needs a signature from its owner or a controller. The CI key
  `AXobAqdzsxhhEb85aduWBChkSrEjGmswJjozXHKfRKDj` is a controller.
- **Base**: the mainnet connector that fronts the store and the gas station is paid only in USDC on
  Base, over an x402 batch-settlement channel. The client signs that channel's deposit and every
  voucher on it with an EVM key, and pays its own channel's gas (no facilitator, no sponsored open).

A Solana key cannot sign for Base, and the client library opens a Solana channel only through the
connector's sponsor, which would have the connector pay for the client's channel.

## Decision

There is one secret, `WALLET`: the solana-keygen JSON array of the controller key. The Base key is
derived from it:

```
base private key = sha256( utf8("toon-ci/evm/v1") || the keypair's 32-byte seed )
```

`deriveBaseKey` in `.publish/wallet.mjs` is that rule, and `.publish/wallet.test.mjs` pins it on a
throwaway vector. `.publish/config.json` pins the two addresses the real secret must give:
`AXobAqdzsxhhEb85aduWBChkSrEjGmswJjozXHKfRKDj` and `0xC4Cd8ad303C68fDC50f0DE16Bb2D42dC1A145c39`.
`loadWallet` refuses to run when either differs.

## Consequences

- **The label is part of the address.** Changing `toon-ci/evm/v1`, or the secret, gives another Base
  address. The channel and its deposit stay behind at the old one, and a run from the new address
  would need a new channel. That is why the addresses are pinned and a mismatch stops the run before
  anything is paid. To change the label on purpose, close the old channel first (its deposit comes
  back after the withdraw delay), then update the label and the pinned address together.
- **No ordinary wallet shows the Base key.** Read it with `deriveBaseKey`, or check the address with
  `node .publish/publish.mjs plan`, which prints both addresses.
- **One secret to rotate.** Rotating `WALLET` means: add the new controller to the ANT, move the Base
  funds, open a new channel, and update the pinned addresses.
- **The same key holds both kinds of power,** to change what toon.ar.io serves and to spend the
  channel. Keep the secret scoped to this repository only.
