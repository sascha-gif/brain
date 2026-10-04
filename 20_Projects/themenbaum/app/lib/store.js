// Speicher: eine JSON-Datei auf dem Server (DATA_DIR, Standard ./data).
// Konflikte zwischen Geräten fängt eine Versionsnummer ab. Einmal pro Tag eine Sicherungskopie.
import { readFile, writeFile, rename, mkdir, copyFile, readdir, unlink } from "node:fs/promises";
import { join } from "node:path";

const DIR = process.env.DATA_DIR || new URL("../data", import.meta.url).pathname;
const FILE = join(DIR, "themenbaum.json");
const KEEP_BACKUPS = 60;

export class Conflict extends Error {}

let queue = Promise.resolve(); // Schreibzugriffe nacheinander

async function read() {
  try {
    const raw = JSON.parse(await readFile(FILE, "utf8"));
    return { data: raw.data ?? { topics: [] }, etag: String(raw.version ?? 0) };
  } catch (e) {
    if (e.code === "ENOENT") return { data: { topics: [] }, etag: "0" };
    throw e;
  }
}

export async function load() {
  return read();
}

export function save(data, etag) {
  const job = queue.then(async () => {
    const cur = await read();
    if (String(etag ?? "0") !== cur.etag) throw new Conflict();
    const version = Number(cur.etag) + 1;
    await mkdir(DIR, { recursive: true });
    const tmp = FILE + ".tmp";
    await writeFile(tmp, JSON.stringify({ version, savedAt: new Date().toISOString(), data }));
    await rename(tmp, FILE); // atomar: nie eine halbe Datei
    await backup().catch(() => {});
    return { etag: String(version) };
  });
  queue = job.catch(() => {});
  return job;
}

async function backup() {
  const dir = join(DIR, "backups");
  await mkdir(dir, { recursive: true });
  await copyFile(FILE, join(dir, new Date().toISOString().slice(0, 10) + ".json"));
  const files = (await readdir(dir)).filter((f) => f.endsWith(".json")).sort();
  for (const f of files.slice(0, Math.max(0, files.length - KEEP_BACKUPS))) await unlink(join(dir, f));
}
