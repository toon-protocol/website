// Publish toon.ar.io through TOON. Run from the repository root or from .publish/:
//
//   node .publish/publish.mjs plan      what would be uploaded and what it costs; spends nothing
//   node .publish/publish.mjs upload    upload the changed files and a manifest; leaves `toon` alone
//   node .publish/publish.mjs publish   upload, then point `toon` at the new manifest and check it
//
// Add --open-channel (never in CI) to let the client open or top up its one channel to the
// connector; without it a run that has no channel, or not enough left in it, stops before paying.
// The wallet is WALLET (the secret's text) or WALLET_FILE (a path to the keypair file): see
// wallet.mjs. Everything else is config.json.
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, extname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadWallet } from './wallet.mjs';
import { makeClient, readRecord, setRecord, upload } from './toon.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, '..');
const CHANNEL_STORE = join(HERE, 'channel', 'channels.json');
const BINDING = join(HERE, 'channel', 'channels.peers.json');
const OUT = join(HERE, 'out');
const config = JSON.parse(readFileSync(join(HERE, 'config.json'), 'utf8'));
process.on('uncaughtException', (e) => { console.error(`Stopped: ${e.shortMessage ?? e.message}`); process.exit(1); });

const args = process.argv.slice(2);
const mode = args.find((a) => !a.startsWith('--'));
const openChannel = args.includes('--open-channel');
const manifestAt = args.indexOf('--manifest');
const promote = manifestAt === -1 ? undefined : args[manifestAt + 1];
if (!['plan', 'upload', 'publish'].includes(mode)) {
  console.error('usage: node .publish/publish.mjs plan|upload|publish [--open-channel] [--manifest <id>]');
  process.exit(2);
}
if (manifestAt !== -1 && (mode !== 'publish' || !/^[A-Za-z0-9_-]{43}$/.test(promote ?? ''))) {
  console.error('--manifest <id> goes with publish, and names a 43-character Arweave transaction id.');
  process.exit(2);
}
if (openChannel && process.env.CI) {
  console.error('--open-channel is for a run on your own machine: CI never opens or tops up a channel.');
  process.exit(2);
}

const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.ico': 'image/x-icon',
  '.woff2': 'font/woff2', '.txt': 'text/plain; charset=utf-8', '.sh': 'text/plain; charset=utf-8',
  '.xml': 'application/xml', '.webmanifest': 'application/manifest+json',
};
const typeOf = (p) => TYPES[extname(p).toLowerCase()] ?? 'application/octet-stream';
const usdc = (units) => `${(Number(units) / 1e6).toFixed(6)} USDC`;
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const log = (...a) => console.log(...a);

/** The connector's own terms, read live; the run stops if they are not the ones config.json expects. */
async function readTerms() {
  const ilp = await (await fetch(`${config.connector}/ilp`)).json();
  const terms = ilp.batchSettlements?.find((b) => b.network === config.settlement.network && b.asset.toLowerCase() === config.settlement.asset.toLowerCase());
  if (!terms) throw new Error(`${config.connector} is not paid in ${config.settlement.asset} on ${config.settlement.network}`);
  const price = (prefix) => {
    const route = ilp.routes?.find((r) => r.prefix === prefix);
    if (!route) throw new Error(`${config.connector} serves no route ${prefix}`);
    return { price: BigInt(route.price), perKib: BigInt(route.pricePerKib ?? 0) };
  };
  return { terms, store: price(config.routes.store), quote: price(config.routes.gasQuote), execute: price(config.routes.gasExecute) };
}

/** What the last publish uploaded, as the live site serves it; nothing if it is not there yet. */
async function previousIndex() {
  try {
    const res = await fetch(`${config.site}/${config.publishIndex}`);
    if (!res.ok) return { files: {} };
    const index = await res.json();
    return index?.version === 1 && typeof index.files === 'object' ? index : { files: {} };
  } catch {
    return { files: {} }; // the gateway answers an unknown path with the landing page
  }
}

/** A write's price: the route's flat price plus its per-KiB price on the sealed payload (estimated). */
const writeCost = (store, bytes) => store.price + store.perKib * BigInt(Math.ceil((Math.ceil(bytes / 3) * 4 + 1024) / 1024));

/** The channel this client holds with the connector, from the committed binding file. */
function binding() {
  if (!existsSync(BINDING)) return undefined;
  // The client keys each channel `batch|<connector>|<network>|<asset>`, at the top level of the file.
  const key = `batch|${config.connector}|${config.settlement.network}|${config.settlement.asset}`.toLowerCase();
  const entries = Object.entries(JSON.parse(readFileSync(BINDING, 'utf8')));
  const [, channel] = entries.find(([k]) => k.toLowerCase() === key) ?? [];
  return channel && { channelId: channel.channelId, deposit: BigInt(channel.depositTotal), signed: BigInt(channel.lastVoucherAmount ?? 0) };
}

const wallet = await loadWallet(config.wallet);
log(`wallet     ${wallet.solanaAddress} (Solana, controls ${config.arns.name}) and ${wallet.baseAddress} (Base, pays the channel)`);
const live = await readTerms();
log(`connector  ${config.connector}: paid to ${live.terms.payTo} in ${live.terms.name} on ${live.terms.network}`);

const template = JSON.parse(readFileSync(join(ROOT, 'manifest.template.json'), 'utf8'));
// publish --manifest <id>: point the name at a manifest an earlier upload made, after checking that it
// holds exactly this commit's files. What the preview showed is then what goes live, with no second upload.
if (promote) {
  const res = await fetch(`${config.previewGateway}/${promote}/${config.publishIndex}`);
  const index = res.ok ? await res.json().catch(() => undefined) : undefined;
  if (index?.version !== 1) throw new Error(`${config.previewGateway}/${promote}/${config.publishIndex} is not a publish index`);
  const expected = Object.keys(template.paths);
  const mismatched = expected.filter((path) => index.files[path]?.sha256 !== sha256(readFileSync(join(ROOT, path))));
  const extra = Object.keys(index.files).filter((path) => !template.paths[path]);
  if (mismatched.length || extra.length) {
    throw new Error(`manifest ${promote} does not hold this commit's files: ${[...mismatched, ...extra].slice(0, 5).join(', ')}${mismatched.length + extra.length > 5 ? ', …' : ''}`);
  }
  log(`manifest   ${promote}: all ${expected.length} files match this commit`);
  if (!binding()) throw new Error('no channel binding is committed: the gas station is paid on the channel');
  mkdirSync(OUT, { recursive: true });
  mkdirSync(dirname(CHANNEL_STORE), { recursive: true });
  const receipt = { mode, manifest: promote, started: new Date().toISOString(), commit: process.env.GITHUB_SHA, spent: 0n };
  const client = await makeClient(config, wallet, CHANNEL_STORE, false);
  try {
    const set = await setRecord(client, config, wallet, promote);
    receipt.spent += set.cost;
    receipt.record = set;
    log(`record     ${config.arns.name} -> ${promote}: ${set.signature ?? JSON.stringify(set)} (${usdc(set.cost)}, fee paid by ${set.feePayer})`);
    const now = await readRecord(config);
    if (now?.transactionId !== promote) throw new Error(`the ANT's '@' record reads ${now?.transactionId}, not ${promote}`);
    log(`on chain   '@' = ${now.transactionId}, TTL ${now.ttlSeconds}`);
  } finally {
    receipt.finished = new Date().toISOString();
    writeFileSync(join(OUT, 'receipt.json'), JSON.stringify(receipt, (_, v) => (typeof v === 'bigint' ? v.toString() : v), 2));
    await client.close();
    log(`spent      ${usdc(receipt.spent)} (receipt: .publish/out/receipt.json)`);
  }
  process.exit(0);
}

const before = await previousIndex();
const files = Object.keys(template.paths).map((path) => {
  const bytes = readFileSync(join(ROOT, path));
  const hash = sha256(bytes);
  const known = before.files[path];
  return { path, bytes, sha256: hash, txId: known?.sha256 === hash ? known.txId : undefined };
});
const changed = files.filter((f) => !f.txId);
const indexBytes = 120 * files.length; // publish-index.json, roughly
let estimate = changed.reduce((n, f) => n + writeCost(live.store, f.bytes.length), 0n)
  + writeCost(live.store, indexBytes) + writeCost(live.store, 60 * files.length);
if (mode !== 'upload') estimate += 2n * live.quote.price + live.execute.price; // two quotes and the execute

log(`files      ${files.length} in the manifest, ${changed.length} to upload (${files.length - changed.length} unchanged since the live publish-index)`);
for (const f of changed) log(`  upload   ${f.path} (${f.bytes.length} bytes)`);
log(`estimate   ${usdc(estimate)} for ${mode === 'plan' ? 'a publish' : `this ${mode}`}, at the connector's live prices`);
const held = binding();
if (held) log(`channel    ${held.channelId}: deposited ${usdc(held.deposit)}, signed ${usdc(held.signed)}, about ${usdc(held.deposit - held.signed)} left`);
else log('channel    none committed yet (.publish/channel/channels.peers.json)');
if (held && held.deposit - held.signed < estimate) log(`warning    the channel has less left than the estimate: top it up with --open-channel on your own machine`);
if (mode === 'plan') process.exit(0);

if (!held && !openChannel) throw new Error('no channel binding is committed: open the channel once on your own machine with --open-channel, then commit .publish/channel/channels.peers.json');
if (estimate > BigInt(config.maxSpendPerRun)) throw new Error(`the estimate ${usdc(estimate)} is over maxSpendPerRun ${usdc(config.maxSpendPerRun)} in config.json`);

mkdirSync(OUT, { recursive: true });
const receipt = { mode, started: new Date().toISOString(), commit: process.env.GITHUB_SHA, files: {}, spent: 0n };
const saveReceipt = () => writeFileSync(join(OUT, 'receipt.json'), JSON.stringify(receipt, (_, v) => (typeof v === 'bigint' ? v.toString() : v), 2));
mkdirSync(dirname(CHANNEL_STORE), { recursive: true });
const client = await makeClient(config, wallet, CHANNEL_STORE, openChannel);
try {
  const write = async (label, bytes, contentType) => {
    const r = await upload(client, config.routes.store, bytes, contentType, label);
    receipt.spent += r.cost;
    if (!r.ok) throw new Error(`${label}: ${r.code} ${r.message}`);
    log(`  ok       ${label} ${r.receipt.txId} (${usdc(r.cost)})`);
    return r.receipt.txId;
  };
  for (const f of changed) {
    f.txId = await write(f.path, f.bytes, typeOf(f.path));
    receipt.files[f.path] = { txId: f.txId, sha256: f.sha256 };
    saveReceipt();
  }

  // The index of what this publish holds, served beside the site so the next run can skip what is unchanged.
  const index = { version: 1, commit: process.env.GITHUB_SHA ?? null, files: Object.fromEntries(files.map((f) => [f.path, { sha256: f.sha256, txId: f.txId }])) };
  const indexId = await write(config.publishIndex, Buffer.from(JSON.stringify(index, null, 1)), 'application/json');
  const manifest = { ...template, paths: { ...Object.fromEntries(files.map((f) => [f.path, { id: f.txId }])), [config.publishIndex]: { id: indexId } } };
  receipt.manifest = await write('manifest', Buffer.from(JSON.stringify(manifest)), 'application/x.arweave-manifest+json');
  log(`manifest   ${receipt.manifest}\npreview    ${config.previewGateway}/${receipt.manifest}/`);
  saveReceipt();

  if (mode === 'publish') {
    const set = await setRecord(client, config, wallet, receipt.manifest);
    receipt.spent += set.cost;
    receipt.record = set;
    log(`record     ${config.arns.name} -> ${receipt.manifest}: ${set.signature ?? JSON.stringify(set)} (${usdc(set.cost)}, fee paid by ${set.feePayer})`);
    const now = await readRecord(config);
    if (now?.transactionId !== receipt.manifest) throw new Error(`the ANT's '@' record reads ${now?.transactionId}, not ${receipt.manifest}`);
    log(`on chain   '@' = ${now.transactionId}, TTL ${now.ttlSeconds}`);
  }
} finally {
  receipt.finished = new Date().toISOString();
  saveReceipt();
  await client.close();
  log(`spent      ${usdc(receipt.spent)} (receipt: .publish/out/receipt.json)`);
}
if (openChannel) log('commit     .publish/channel/channels.peers.json, so CI uses this channel');
