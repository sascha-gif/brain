# Themenbaum — Technik

Code liegt in `app/`. Kein Framework, kein Build-Schritt, keine npm-Abhängigkeiten (Node ≥ 20).

| Datei | Zweck |
|---|---|
| `app/public/index.html` | Komplette Oberfläche (HTML/CSS/JS). Drag & Drop über SortableJS vom cdnjs. |
| `app/server.mjs` | Node-Server: liefert die Seite und `/api/*`, lauscht nur auf 127.0.0.1 (hinter Webserver/TLS). |
| `app/api/login.js` | `POST` Code prüfen und Sitzungs-Cookie setzen (max. 8 Fehlversuche/IP in 15 min), `GET` Status, `DELETE` abmelden. |
| `app/api/data.js` | `GET` Daten laden, `PUT` speichern (nur mit gültigem Cookie). |
| `app/lib/auth.js` | Cookie = HMAC aus `ACCESS_CODE`. Code ändern meldet alle Geräte ab. |
| `app/lib/store.js` | Speicher: `DATA_DIR/themenbaum.json`, atomar geschrieben, Versionsnummer gegen gleichzeitiges Überschreiben, täglich Kopie unter `backups/` (60 Tage). |
| `app/lib/validate.js` | Prüft die Datenform vor dem Speichern. |
| `app/import.mjs` | Themen/Unterthemen aus einer JSON-Datei in den laufenden Bestand ergänzen (nur hinzufügen, nie löschen). Ablauf: `ANLEITUNG-IMPORT.md`. |
| `app/seed.json` | Startbestand, solange auf dem Server noch nichts gespeichert ist. Danach ohne Wirkung. |
| `app/deploy/` | systemd-Unit und nginx-Vorlage. |

## Lokal testen

`cd app && ACCESS_CODE=test DATA_DIR=/tmp/tb node server.mjs` → http://127.0.0.1:3100

## Hosting

- Hetzner-Server von milsh.com, Adresse `lykke.milsh.com`. Installation: `ANLEITUNG-DEPLOY.md`, Einträge übernehmen: `ANLEITUNG-IMPORT.md`.
- Auf dem Server: Code `/opt/themenbaum`, Daten `/var/lib/themenbaum`, Secret `/etc/themenbaum.env`
  (`ACCESS_CODE`, nie ins Repo), Dienst `themenbaum` (systemd).
- Datenform: `{ topics: [{ id, name, c (Farbe 1–12), subs: [{ id, t, d (erledigt) }] }] }`.
