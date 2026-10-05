// Themen und Unterthemen in den laufenden Bestand übernehmen. Löscht nie etwas.
//   DATA_DIR=/var/lib/themenbaum node import.mjs seed.json            # nur anzeigen
//   DATA_DIR=/var/lib/themenbaum node import.mjs seed.json --apply    # übernehmen
// Abgleich über den Namen (Groß/Klein egal): vorhandene Themen werden ergänzt,
// vorhandene Unterthemen übersprungen, erledigte Häkchen bleiben unangetastet.
import { readFile } from "node:fs/promises";
import { randomBytes } from "node:crypto";
import { load, save } from "./lib/store.js";
import { clean } from "./lib/validate.js";

const [file, flag] = process.argv.slice(2);
if (!file) { console.error("Aufruf: node import.mjs <datei.json> [--apply]"); process.exit(1); }
const apply = flag === "--apply";

const incoming = clean(JSON.parse(await readFile(file, "utf8")));
if (!incoming) { console.error("Datei hat nicht die Form { topics: [...] }"); process.exit(1); }

const { data, etag } = await load();
if (etag === "0") {
  console.log("Auf dem Server ist noch nichts gespeichert. Die App zeigt beim ersten Öffnen den Startbestand aus seed.json.");
  if (!apply) console.log("Mit --apply wird der Bestand trotzdem jetzt fest gespeichert.");
}
const topics = structuredClone(data.topics);
for (const t of topics) t.subs = [...t.subs.filter((s) => !s.d), ...t.subs.filter((s) => s.d)];
const key = (s) => s.trim().toLowerCase();
const nid = () => randomBytes(4).toString("hex");
let newTopics = 0, newSubs = 0;

for (const t of incoming.topics) {
  let cur = topics.find((x) => key(x.name) === key(t.name));
  if (!cur) {
    const used = new Set(topics.map((x) => x.c));
    const c = [...Array(12)].map((_, i) => i + 1).find((x) => !used.has(x)) || (topics.length % 12) + 1;
    cur = { id: nid(), name: t.name, c, subs: [] };
    topics.push(cur); newTopics++;
    console.log(`+ Thema     ${t.name}`);
  }
  for (const s of t.subs) {
    if (cur.subs.some((x) => key(x.t) === key(s.t))) continue;
    const k = cur.subs.findIndex((x) => x.d); // offene vor erledigten einsortieren
    cur.subs.splice(k < 0 ? cur.subs.length : k, 0, { id: nid(), t: s.t, d: false });
    newSubs++;
    console.log(`+ Unterthema ${cur.name}: ${s.t}`);
  }
}

console.log(`\n${newTopics} neue Themen, ${newSubs} neue Unterthemen.`);
if (!newTopics && !newSubs && etag !== "0") process.exit(0);
if (!apply) { console.log("Nur Vorschau. Zum Übernehmen mit --apply erneut aufrufen."); process.exit(0); }
const out = clean({ topics });
const { etag: v } = await save(out, etag);
console.log(`Übernommen (Version ${v}). Offene Browserfenster laden den neuen Stand beim nächsten Speichern bzw. Neuladen.`);
