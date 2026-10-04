# Themenbaum — Technik

Code liegt in `app/`. Kein Framework, kein Build-Schritt.

| Datei | Zweck |
|---|---|
| `app/public/index.html` | Komplette Oberfläche (HTML/CSS/JS). Drag & Drop über SortableJS vom cdnjs. |
| `app/api/login.js` | `POST` Code prüfen und Sitzungs-Cookie setzen, `GET` Status, `DELETE` abmelden. |
| `app/api/data.js` | `GET` Daten laden, `PUT` speichern (nur mit gültigem Cookie). |
| `app/lib/auth.js` | Cookie = HMAC aus `ACCESS_CODE`. Code ändern meldet alle Geräte ab. |
| `app/lib/store.js` | Speicher: eine Datei `themenbaum.json` im **privaten** Vercel-Blob-Store, Schutz gegen gleichzeitiges Überschreiben per ETag (`ifMatch`), täglich eine Kopie unter `backups/JJJJ-MM-TT.json`. |
| `app/lib/validate.js` | Prüft die Datenform vor dem Speichern. |
| `app/dev-server.mjs` | Lokaler Test ohne Vercel: `cd app && npm i && ACCESS_CODE=test node dev-server.mjs` (Speicher im RAM). |

## Hosting

- Vercel, Projekt-Root `20_Projects/themenbaum/app`, Framework „Other“, Output `public`.
- Secrets in Vercel (nie ins Repo): `ACCESS_CODE` (Zugangscode), `BLOB_READ_WRITE_TOKEN`
  (kommt automatisch, wenn der Blob-Store mit dem Projekt verbunden wird).
- Datenform: `{ topics: [{ id, name, c (Farbe 1–6), subs: [{ id, t, d (erledigt) }] }] }`.
