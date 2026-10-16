// Paying through the one mainnet connector: store writes (kind:5094) and the ArNS record update,
// which the controller signs and the gas station (kind:5096) pays the fee for and broadcasts.
import { randomUUID } from 'node:crypto';
import {
  ToonClient,
  buildJobEvent,
  parseSolanaWireTransaction,
  patchSolanaRecentBlockhash,
  signSolanaWireTransaction,
  solanaKeypair,
} from '@toon-protocol/client';
import { MAINNET_PROGRAM_IDS, MAINNET_RPC_URL, SolanaANTReadable, SolanaANTWriteable } from '@ar.io/sdk/solana';
import {
  address,
  appendTransactionMessageInstructions,
  compileTransaction,
  createKeyPairSignerFromPrivateKeyBytes,
  createSolanaRpc,
  createSolanaRpcSubscriptions,
  createTransactionMessage,
  getBase64EncodedWireTransaction,
  pipe,
  setTransactionMessageFeePayer,
  setTransactionMessageLifetimeUsingBlockhash,
} from '@solana/kit';
import { getSetComputeUnitLimitInstruction } from '@solana-program/compute-budget';

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
export const solanaRpcUrl = () => process.env.SOLANA_RPC_URL || MAINNET_RPC_URL;

/**
 * The paying client. It opens or tops up a channel only when `open` is set; otherwise a send that
 * needs one throws ChannelNotOpenError instead of locking a new deposit.
 */
export function makeClient(config, wallet, channelStore, open) {
  return ToonClient.create({
    connector: config.connector,
    evmPrivateKey: wallet.baseKey,
    chain: 'evm',
    rpcUrl: process.env.BASE_RPC_URL || config.settlement.rpcUrl,
    channelStore,
    deposit: BigInt(config.deposit),
    autoOpenChannel: open,
    // The client pays its own channel's gas: no facilitator, no sponsored open.
    depositGas: 'self',
    facilitatorUrl: '',
    timeoutMs: 120_000,
  });
}

/** Pay for one job. Returns { ok, receipt } or { ok: false, code, message }, with what it cost. */
export async function job(client, destination, eventParams) {
  const answer = await client.send(destination, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: { event: buildJobEvent(eventParams) },
  });
  const cost = answer.claim?.amount ?? 0n;
  if (!answer.fulfilled) return { ok: false, code: answer.code, message: `${answer.refusedBy}: ${answer.message}`, cost };
  let body;
  try { body = answer.json(); } catch { return { ok: false, code: 'F00', message: `HTTP ${answer.status}: ${answer.text().slice(0, 300)}`, cost }; }
  if (body.accept !== true) return { ok: false, code: body.code ?? String(answer.status), message: body.message ?? JSON.stringify(body).slice(0, 300), cost };
  let receipt;
  if (typeof body.data === 'string') {
    const raw = Buffer.from(body.data, 'base64').toString('utf8');
    try { receipt = JSON.parse(raw); if (typeof receipt !== 'object') receipt = { txId: raw }; } catch { receipt = { txId: raw }; }
  } else if (body.result && typeof body.result === 'object') receipt = body.result;
  else if (typeof body.txId === 'string') receipt = { txId: body.txId };
  return { ok: true, receipt, cost };
}

/** One kind:5094 write. A channel opened moments ago is refused (F01) until the connector sees the deposit: retry. */
export async function upload(client, route, bytes, contentType, label) {
  let paid = 0n;
  for (let attempt = 1; ; attempt++) {
    const r = await job(client, route, {
      kind: 5094,
      params: {},
      tags: [['i', bytes.toString('base64'), 'blob'], ['bid', '0', 'usdc'], ['output', contentType]],
    });
    paid += r.cost;
    if (r.ok) return { ...r, cost: paid };
    const notYet = r.code === 'F01' && /does not admit/.test(r.message);
    if (!notYet || attempt >= 6) return { ...r, cost: paid };
    console.error(`  ${label}: the channel is not admitted yet, retry ${attempt} in 15 s`);
    await sleep(15_000);
  }
}

/** The set_record instructions the SDK would send, captured instead of sent. */
class CapturingAnt extends SolanaANTWriteable {
  async sendTransaction(instructions) { this.captured = instructions; return 'captured'; }
}

async function gasQuote(client, routes, transaction) {
  const r = await job(client, routes.gasQuote, { kind: 5096, params: { phase: 'quote', transaction } });
  if (!r.ok) throw new Error(`gas quote refused: ${r.code} ${r.message}`);
  if (r.receipt.status === 'failed') throw new Error(`gas quote declined: ${r.receipt.reason} ${r.receipt.detail}`);
  return { ...r.receipt, cost: r.cost };
}

/**
 * Point the ANT's '@' record at `manifestId`. The controller signs; the gas station is the fee
 * payer, so its quote comes first: the fee payer and the blockhash are part of what is signed.
 */
export async function setRecord(client, config, wallet, manifestId) {
  const rpcUrl = solanaRpcUrl();
  const ant = new CapturingAnt({
    rpc: createSolanaRpc(rpcUrl),
    rpcSubscriptions: createSolanaRpcSubscriptions(rpcUrl.replace(/^http/, 'ws')),
    processId: config.arns.ant,
    signer: await createKeyPairSignerFromPrivateKeyBytes(wallet.seed),
    antProgramId: MAINNET_PROGRAM_IDS.ant,
  });
  await ant.setBaseNameRecord({ transactionId: manifestId, ttlSeconds: config.arns.ttlSeconds });
  const instructions = [getSetComputeUnitLimitInstruction({ units: 400_000 }), ...ant.captured];

  // 1. Who pays the fee. 2. A signed draft, priced by the gas station. 3. Its blockhash, then sign.
  const first = await gasQuote(client, config.routes, undefined);
  const compile = (blockhash) => getBase64EncodedWireTransaction(compileTransaction(pipe(
    createTransactionMessage({ version: 'legacy' }),
    (m) => setTransactionMessageFeePayer(address(first.feePayer), m),
    (m) => setTransactionMessageLifetimeUsingBlockhash({ blockhash, lastValidBlockHeight: 0n }, m),
    (m) => appendTransactionMessageInstructions(instructions, m),
  )));
  const controller = solanaKeypair(wallet.seed);
  const draft = signSolanaWireTransaction(compile(first.recentBlockhash), [controller]);
  const priced = await gasQuote(client, config.routes, draft);
  const executable = signSolanaWireTransaction(patchSolanaRecentBlockhash(draft, priced.recentBlockhash), [controller]);
  if (parseSolanaWireTransaction(executable).signers[0] !== first.feePayer) throw new Error('the fee payer is not in slot 0');

  const idempotencyKey = randomUUID();
  const r = await job(client, config.routes.gasExecute, {
    kind: 5096,
    params: { phase: 'execute', transaction: executable, quoteId: priced.quoteId, idempotencyKey },
  });
  if (!r.ok) throw new Error(`gas execute refused: ${r.code} ${r.message} (idempotencyKey ${idempotencyKey})`);
  if (r.receipt.status === 'failed') throw new Error(`gas execute declined: ${r.receipt.reason} ${r.receipt.detail} (idempotencyKey ${idempotencyKey})`);
  return { ...r.receipt, feePayer: first.feePayer, idempotencyKey, cost: first.cost + priced.cost + r.cost };
}

/** What the ANT's '@' record points at now, read from Solana. */
export async function readRecord(config) {
  const reader = new SolanaANTReadable({ rpc: createSolanaRpc(solanaRpcUrl()), processId: config.arns.ant, antProgramId: MAINNET_PROGRAM_IDS.ant });
  return reader.getRecord({ undername: '@' });
}
