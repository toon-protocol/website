// The Base-key derivation is a commitment: the CI channel lives at the address it gives. These
// vectors pin it. The seed is the throwaway bytes 1..32; the expected values were computed
// independently (Python hashlib for the key, `cast wallet address` for the address).
import assert from 'node:assert/strict';
import test from 'node:test';
import { createKeyPairSignerFromPrivateKeyBytes, getAddressEncoder } from '@solana/kit';
import { privateKeyToAccount } from 'viem/accounts';
import { deriveBaseKey, loadWallet, parseKeypair } from './wallet.mjs';

const SEED = Uint8Array.from({ length: 32 }, (_, i) => i + 1);
const LABEL = 'toon-ci/evm/v1';
const KEY = '0xf7bf00b125b009adfc31c4b35976ef06d28922251dac9ef273bdeadd6a03278f';
const ADDRESS = '0x96b070B47eb9341Af8134588A48dEB3a4b38B2C5';
const SOLANA = '9C6hybhQ6Aycep9jaUnP6uL9ZYvDjUp1aSkFWPUFJtpj';

async function keypairText(seed) {
  const signer = await createKeyPairSignerFromPrivateKeyBytes(seed);
  return JSON.stringify([...seed, ...getAddressEncoder().encode(signer.address)]);
}

test('the Base key is sha256(label || seed)', () => {
  assert.equal(deriveBaseKey(SEED, LABEL), KEY);
  assert.equal(privateKeyToAccount(KEY).address, ADDRESS);
});

test('another label gives another address', () => {
  assert.notEqual(privateKeyToAccount(deriveBaseKey(SEED, 'toon-ci/evm/v2')).address, ADDRESS);
});

test('loadWallet returns both addresses when they match the pinned ones', async () => {
  const w = await loadWallet({ baseKeyLabel: LABEL, solanaAddress: SOLANA, baseAddress: ADDRESS }, { WALLET: await keypairText(SEED) });
  assert.equal(w.solanaAddress, SOLANA);
  assert.equal(w.baseAddress, ADDRESS);
  assert.equal(w.baseKey, KEY);
});

test('loadWallet refuses a Base address that differs from the pinned one', async () => {
  await assert.rejects(
    loadWallet({ baseKeyLabel: 'toon-ci/evm/v2', solanaAddress: SOLANA, baseAddress: ADDRESS }, { WALLET: await keypairText(SEED) }),
    /refusing, a new address would open a new channel/,
  );
});

test('loadWallet refuses another Solana key', async () => {
  const other = Uint8Array.from({ length: 32 }, () => 7);
  await assert.rejects(
    loadWallet({ baseKeyLabel: LABEL, solanaAddress: SOLANA, baseAddress: ADDRESS }, { WALLET: await keypairText(other) }),
    /not the pinned/,
  );
});

test('a keypair must be 64 numbers', () => {
  assert.throws(() => parseKeypair('[1,2,3]'), /64 numbers/);
  assert.throws(() => parseKeypair('5Kd3…base58'), /not JSON/);
});
