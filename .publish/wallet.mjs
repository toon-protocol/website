// The CI wallet is one secret, WALLET: the solana-keygen JSON array (64 numbers) of the key that
// controls the `toon` ArNS name. The connector is paid on Base, so the Base key is derived from it:
//
//   base private key = sha256( utf8(label) || the keypair's 32-byte seed )
//
// with the label in config.json (`toon-ci/evm/v1`). The rule is ADR 0001 in .agents/adr/. Changing
// the label, or the seed, gives a different Base address, and the channel's deposit stays behind at
// the old one; that is why config.json pins both addresses and loadWallet refuses a mismatch.
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { createKeyPairSignerFromPrivateKeyBytes } from '@solana/kit';
import { privateKeyToAccount } from 'viem/accounts';

/** The Base private key (0x-hex) for a 32-byte Solana seed under `label`. */
export function deriveBaseKey(seed, label) {
  if (seed.length !== 32) throw new Error(`a Solana seed is 32 bytes, not ${seed.length}`);
  const digest = createHash('sha256').update(Buffer.from(label, 'utf8')).update(seed).digest();
  return `0x${digest.toString('hex')}`;
}

/** Parse a solana-keygen keypair: a JSON array of 64 numbers, seed first, public key last. */
export function parseKeypair(text) {
  let bytes;
  try { bytes = JSON.parse(text); } catch { throw new Error('WALLET is not JSON: it should be the solana-keygen array of 64 numbers'); }
  if (!Array.isArray(bytes) || bytes.length !== 64 || !bytes.every((b) => Number.isInteger(b) && b >= 0 && b < 256)) {
    throw new Error('WALLET should be the solana-keygen array of 64 numbers');
  }
  return Uint8Array.from(bytes);
}

/**
 * The wallet from WALLET (the secret's text) or WALLET_FILE (a path to it), checked against the
 * addresses pinned in `expected`. Returns both keys and both addresses.
 */
export async function loadWallet(expected, env = process.env) {
  const text = env.WALLET ?? (env.WALLET_FILE ? readFileSync(env.WALLET_FILE, 'utf8') : undefined);
  if (!text) throw new Error('set WALLET (the secret) or WALLET_FILE (a path to the keypair file)');
  const keypair = parseKeypair(text.trim());
  const seed = keypair.slice(0, 32);
  const solana = await createKeyPairSignerFromPrivateKeyBytes(seed);
  const baseKey = deriveBaseKey(seed, expected.baseKeyLabel);
  const baseAddress = privateKeyToAccount(baseKey).address;
  if (solana.address !== expected.solanaAddress) {
    throw new Error(`WALLET is ${solana.address}, not the pinned ${expected.solanaAddress}`);
  }
  if (baseAddress !== expected.baseAddress) {
    throw new Error(`WALLET derives Base address ${baseAddress} under "${expected.baseKeyLabel}", not the pinned ${expected.baseAddress}: refusing, a new address would open a new channel`);
  }
  return { keypair, seed, solanaAddress: solana.address, baseKey, baseAddress };
}
