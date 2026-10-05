# Auftrag: Themenbaum auf lykke.milsh.com installieren

_Für eine lokale Claude-Code-Session (CLI) mit SSH-Zugang zum Hetzner-Server von milsh.com.
Der Code liegt (Stand 2026-10-04) auf Branch `claude/repo-identification-smujr1`, ggf. erst
`git fetch origin claude/repo-identification-smujr1` und nach `main` übernehmen.
Einfach diese Datei in der Session nennen: „Lies `20_Projects/themenbaum/ANLEITUNG-DEPLOY.md` und
führ sie aus.“_

## Ziel

Die To-do-App „Themenbaum“ läuft unter **https://lykke.milsh.com**, geschützt mit einem
Zugangscode. Kein Vercel. Die App ist ein kleiner Node-Server ohne Abhängigkeiten; die Daten
liegen als JSON-Datei auf dem Server. Code: `20_Projects/themenbaum/app/`
(Technik-Details: `20_Projects/themenbaum/CLAUDE.md`).

## Regeln für diese Session

- Erst **schauen, dann ändern**. Vor jedem Eingriff in bestehende Konfiguration (Webserver,
  Firewall, andere Seiten auf milsh.com) Sascha kurz sagen, was du vorhast, und bestätigen lassen.
- Nichts an bestehenden Seiten von milsh.com verändern; nur eine neue Seite für `lykke.milsh.com` dazu.
- Zugangscode **nie** ins Repo, nie in eine Datei im Repo. Er steht nur in `/etc/themenbaum.env`
  auf dem Server und wird Sascha einmal im Chat genannt.
- Wo SSH-Host/Benutzer liegen, steht ggf. in `~/.ssh/config` bzw. `40_Resources/`. Fehlt es:
  Sascha fragen, nicht raten.

## Schritt 1 — Bestand aufnehmen (nur lesen)

Auf dem Server prüfen und Sascha zusammenfassen:

1. Betriebssystem (`cat /etc/os-release`), ist `node` installiert und Version ≥ 20 (`node -v`)?
2. Welcher Webserver läuft auf Port 80/443 (`ss -tlnp`): nginx, Apache, Caddy, Plesk/ISPConfig?
3. Zeigt `lykke.milsh.com` schon auf diesen Server (`dig +short lykke.milsh.com` vs. Server-IP)?
4. Ist Port 3100 frei (`ss -tlnp | grep 3100`)?

Falls Node fehlt: Node 22 LTS installieren (NodeSource oder Paketquelle) — vorher bestätigen lassen.
Falls DNS fehlt: Sascha muss einen A-Eintrag `lykke` → Server-IP beim DNS-Anbieter setzen
(bei Hetzner: DNS-Konsole). Ohne DNS kein Zertifikat.

## Schritt 2 — App hochladen

Aus dem lokalen Repo (Branch mit `20_Projects/themenbaum/app/`):

```bash
sudo useradd --system --home /opt/themenbaum --shell /usr/sbin/nologin themenbaum   # auf dem Server
sudo mkdir -p /opt/themenbaum /var/lib/themenbaum
rsync -av --delete --exclude data --exclude node_modules \
  20_Projects/themenbaum/app/ <host>:/tmp/themenbaum/                                # lokal
sudo rsync -a --delete /tmp/themenbaum/ /opt/themenbaum/                             # auf dem Server
sudo chown -R root:root /opt/themenbaum && sudo chown -R themenbaum:themenbaum /var/lib/themenbaum
```

## Schritt 3 — Zugangscode setzen

```bash
CODE=$(openssl rand -base64 18 | tr -dc 'A-Za-z0-9' | head -c 10)
echo "ACCESS_CODE=$CODE" | sudo tee /etc/themenbaum.env >/dev/null
sudo chmod 600 /etc/themenbaum.env
echo "$CODE"   # Sascha einmal nennen, sonst nirgends ablegen
```

Code später ändern = Datei bearbeiten + `sudo systemctl restart themenbaum`. Alle Geräte sind
dann abgemeldet.

## Schritt 4 — Dienst starten

```bash
sudo cp /opt/themenbaum/deploy/themenbaum.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now themenbaum
systemctl status themenbaum --no-pager
curl -s localhost:3100/api/login     # erwartet: {"ok":false}
```

Liegt `node` nicht unter `/usr/bin/env node` im PATH (z. B. nvm), `ExecStart` in der Unit anpassen.

## Schritt 5 — Webserver + HTTPS

- **nginx:** Vorlage `deploy/nginx-lykke.milsh.com.conf` nach `/etc/nginx/sites-available/`,
  verlinken nach `sites-enabled/`, `sudo nginx -t && sudo systemctl reload nginx`, dann
  `sudo certbot --nginx -d lykke.milsh.com`.
- **Apache:** gleichwertigen VirtualHost mit `ProxyPass / http://127.0.0.1:3100/`,
  `RequestHeader set X-Forwarded-Proto "https"`, Module `proxy proxy_http headers`; Zertifikat
  mit `certbot --apache -d lykke.milsh.com`.
- **Caddy:** `lykke.milsh.com { reverse_proxy 127.0.0.1:3100 }` — Zertifikat kommt automatisch.
- **Plesk/ISPConfig o. ä.:** Subdomain dort anlegen und Proxy auf `127.0.0.1:3100` eintragen;
  nicht an den Konfigurationsdateien vorbei arbeiten.

Wichtig: Der Proxy muss `X-Forwarded-Proto` und `X-Real-IP` setzen (sonst fehlt am Cookie das
`Secure` bzw. die Fehlversuchs-Sperre greift für alle gleichzeitig).

## Schritt 6 — Prüfen

1. `https://lykke.milsh.com` zeigt die Code-Abfrage; falscher Code → „Code stimmt nicht.“
2. Mit richtigem Code: Thema + Unterthema anlegen, abhaken, Seite neu laden → bleibt.
3. `sudo ls /var/lib/themenbaum` zeigt `themenbaum.json` und `backups/`.
4. „Drucken (nur offene)“ öffnet den Druckdialog, Vorschau zeigt nur offene Aufgaben.

## Schritt 6b — Einträge übernehmen

Beim ersten Öffnen zeigt die App den Startbestand aus `seed.json`. Falls auf dem Server schon
Daten liegen: `ANLEITUNG-IMPORT.md` ausführen.

## Schritt 7 — Festhalten

- `20_Projects/themenbaum/uebersicht.md`: Status auf „läuft“, erledigte Schritte abhaken,
  Webserver-Art und Pfade eintragen (ohne Code, ohne Passwörter).
- Zeile in `wissen/log.md` (Format wie die bestehenden Einträge).
- Commit und Push.

## Updates später

Neue Version hochladen wie in Schritt 2 (ohne `data/`!), dann `sudo systemctl restart themenbaum`.
Die Daten in `/var/lib/themenbaum` bleiben unberührt.
