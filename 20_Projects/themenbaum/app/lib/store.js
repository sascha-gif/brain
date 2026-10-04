// Speicher: eine JSON-Datei im privaten Vercel-Blob-Store.
// Konflikte zwischen Geräten fängt das ETag ab (ifMatch). Einmal pro Tag eine Sicherungskopie.
import { get, put, BlobPreconditionFailedError } from "@vercel/blob";

const FILE = "themenbaum.json";
const EMPTY = { topics: [] };

export class Conflict extends Error {}

// Lokaler Testmodus ohne Vercel: STORE=memory
const mem = { data: null, etag: null, n: 0, backups: {} };
const useMem = () => process.env.STORE === "memory";

export async function load() {
  if (useMem()) return { data: mem.data ?? EMPTY, etag: mem.etag };
  const res = await get(FILE, { access: "private", useCache: false });
  if (!res || res.statusCode !== 200) return { data: EMPTY, etag: null };
  const data = JSON.parse(await new Response(res.stream).text());
  return { data, etag: res.blob.etag };
}

export async function save(data, etag) {
  const body = JSON.stringify(data);
  if (useMem()) {
    if ((mem.etag ?? null) !== (etag ?? null)) throw new Conflict();
    mem.data = data; mem.etag = `"m${++mem.n}"`;
    mem.backups[new Date().toISOString().slice(0, 10)] = body;
    return { etag: mem.etag };
  }
  const opts = { access: "private", contentType: "application/json", addRandomSuffix: false };
  try {
    const out = etag
      ? await put(FILE, body, { ...opts, ifMatch: etag })
      : await put(FILE, body, { ...opts, allowOverwrite: false });
    await backup(body).catch(() => {});
    return { etag: out.etag };
  } catch (e) {
    if (e instanceof BlobPreconditionFailedError) throw new Conflict();
    // Erste Speicherung, aber Datei existiert schon (anderes Gerät war schneller)
    if (!etag && /already exists/i.test(String(e?.message))) throw new Conflict();
    throw e;
  }
}

async function backup(body) {
  const day = new Date().toISOString().slice(0, 10);
  await put(`backups/${day}.json`, body, {
    access: "private", contentType: "application/json", addRandomSuffix: false, allowOverwrite: true,
  });
}
