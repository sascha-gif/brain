# Log

Append-only Protokoll. **Neueste unten.** Ein Eintrag pro Ingest, Kompilieren oder Lint.

Feste Präfixe, damit die Datei mit `grep` auswertbar bleibt:
`## [JJJJ-MM-TT] ingest | <Titel>` · `kompiliert` · `lint` · `setup`

## [2026-09-11] setup | Brain-Grundgerüst angelegt

Ordner, `.gitignore`, `CLAUDE.md`, `wissen/`-Startdateien und Templates angelegt.
Drei Entscheidungen dazu in `entscheidungen.md`.
Quelle: Anleitung „Ein Brain aufsetzen" vom 11.09.2026 (in die Session hochgeladen,
nicht im Repo) und Karpathys LLM-Wiki-Gist.

## [2026-09-11] kompiliert | Wie Altbestand ins Brain kommt

Regel nach `entscheidungen.md`: einsortieren statt importieren, Gedächtnis als Filter,
Skelett vor Inhalt, Chat-Archive und Repos indizieren statt einsortieren.
Operativer Ablauf als Projekt `20_Projects/brain-migration/` angelegt.
Quelle: Gespräch vom 11.09.2026 (nicht im Repo).

## [2026-09-11] setup | Firmen als eigene Area angelegt

`30_Areas/firmen/` mit sechs Steckbrief-Gerüsten (Coldewey Holding, helpingbrands,
lykkeandyou, CGT, Fastable, PaSa Ventures), Vorlage `templates/firma-steckbrief.md`.
`CLAUDE.md` aufgeräumt: Entwurfs-Marker raus, leerer Listenpunkt raus, Struktur ergänzt.
Quelle: Gespräch vom 11.09.2026 (nicht im Repo).

## [2026-09-14] setup | Schreibzugriff auf Google Sheets vorbereitet

Geprüft, warum Claude nicht in die CGT-Themenplanung schreiben kann: Der Drive-Connector kann
keine Zellen ändern, einen Sheets-Connector gibt es nicht, und die Sheets API verlangt auch
bei offener Link-Freigabe eine Identität. Skript `40_Resources/tools/gsheets.py` (lesen,
anhängen, überschreiben) und Anleitung `40_Resources/google-sheets-zugang.md` angelegt.
Offen: Service-Account-Key fehlt noch, ungetestet bis dahin.
Quelle: Gespräch vom 14.09.2026 (nicht im Repo).

## [2026-09-14] ingest | Pipedrive-Kontakte für CGT aufbereitet

224 Kontakte aus dem Pipedrive-Personenexport zu einer Tabelle gemacht (sortiert nach Firma,
Filter, Firmenübersicht, abgeleitetes Land) und an Sascha geliefert. Ziel ist die leere
Lasche „Kontakte" in „CGT – Themenplanung"; direkt hineinschreiben geht erst mit dem
Service-Account-Key. Skript `40_Resources/tools/pipedrive_kontakte.py`, Befunde in
`30_Areas/firmen/cgt/notizen.md`. Die Kontaktdaten selbst bleiben draußen.
Quelle: zwei hochgeladene Pipedrive-Exporte vom 14.09.2026 (nicht im Repo).

## [2026-09-14] setup | Sheets-Schreibzugriff auf Apps-Script-Brücke umgestellt

Der Dienstkonto-Weg ist tot: Google blockiert das Erzeugen von Dienstkontoschlüsseln per
Organisationsrichtlinie (`iam.disableServiceAccountKeyCreation`). Ersatz ist ein
eigenständiges Apps Script als Web-App unter Saschas Konto. `gsheets.py` kann beide Wege
und wählt den, der konfiguriert ist; neu sind `--from-csv` und ein `--dry-run`, der ohne
Zugangsdaten läuft. Brücken-Code in `40_Resources/tools/sheets_bruecke.gs`.
Quelle: Gespräch vom 14.09.2026 (nicht im Repo).

## [2026-09-14] setup | Slack-Zugang für CG TRADE vorbereitet

Der Claude-Connector kann nur einen Workspace; CG TRADE ist ein zweiter und damit außer
Reichweite. Ersatz ist eine eigene Slack-App mit Bot-Token. Lesewerkzeug
`40_Resources/tools/slack.py` (channels, read), Anleitung `40_Resources/slack-zugang.md`.
Offen: Token ins Environment, Takt und Ziel der Kontakt-Ablage.
Quelle: Gespräch vom 14.09.2026 (nicht im Repo).

## [2026-09-14] setup | Sheets-Brücke geprüft, Kontakte geschrieben, Slack blockiert

Beide Zugänge gegengeprüft. **Sheets:** `CGT_SHEETS_URL` und `CGT_SHEETS_SECRET` im
Environment, Brücke antwortet, Laschen der Themenplanung gelesen. Den Pipedrive-Personenexport
aufbereitet (224 Datensätze) und in die bis dahin leere Lasche „Kontakte" geschrieben,
Kopfzeile plus Daten ab Zeile 1. **Slack:** `SLACK_CGT_TOKEN` liegt im Environment, ist aus
einer Cloud-Session aber nicht nutzbar — der Egress-Proxy weist `slack.com:443` mit 403 ab
(Organisationsrichtlinie). Gegenprobe: der Claude-Connector erreicht CG TRADE weiterhin nicht
(`channel_not_found`). #kontakte konnte deshalb nicht gelesen werden. Behebungsweg in
`40_Resources/slack-zugang.md` festgehalten: Netzwerkzugriff des Environments von „Trusted"
auf „Custom" mit `slack.com` in den Allowed domains. Bis dahin läuft `slack.py` lokal.
Quelle: Session vom 14.09.2026, Exportdateien nicht im Repo.

## [2026-09-14] kompiliert | Pipedrive-CSV-Export verliert Datensätze

Neuer Eintrag `wissen/pipedrive-export.md`: Nur die erste Spalte des Exports ist unmaskiert,
daraus folgen drei Fehler — kaputte Umlaute, an Zeilenumbrüchen zerrissene Firmennamen und
ein unmaskiertes Komma, das eine Spalte zu viel erzeugt. Mit Reparaturregeln und der
Gegenprobe. Merksatz: wenn möglich den XLSX-Export nehmen.
Quelle: Aufbereitung des Personenexports am 14.09.2026.

## [2026-09-14] eingesortiert | Slack `#kontakte` gegen die Kontakte-Lasche

Sechs Kontaktposts aus dem CG-TRADE-Kanal gelesen, fünf waren Dubletten zum
Pipedrive-Export. Alexandra Ochsenkiel (Deichmann SE) nach Zeile 226 der Lasche
„Kontakte" geschrieben. Vier Abweichungen zwischen Signatur und Lasche notiert, nicht
verändert. Cloud-Sessions erreichen slack.com jetzt — `40_Resources/slack-zugang.md`
entsprechend korrigiert.
Quelle: `30_Areas/firmen/cgt/notizen.md`.

## [2026-09-14] gebaut | Kontakte-Routine Slack → Lasche

Der Abgleich von heute Vormittag läuft jetzt stündlich als Routine. `slack.py` um `scopes`,
`holen` (JSON plus Bilddownload) und typrichtiges Auspacken der Slack-Links erweitert,
`files:read` liegt vor. Anleitung in `40_Resources/kontakte-routine.md`. Zwei Entscheidungen
festgehalten: Abgleich statt Merkzettel, stündlich statt Echtzeit.
Quelle: `30_Areas/firmen/cgt/notizen.md`.


## [2026-09-14] lint | Lasche „Kontakte" gegen die Absprache geprüft

Inhalt stimmt: 225 Kontakte, Ochsenkiel in Zeile 226, Autofilter gesetzt. Die Lasche trägt
aber die Pipedrive-Rohstruktur — vier durchgehend leere Spalten, nicht nach Firma sortiert,
ohne Firmen-Zähler, ohne Land, Kopfzeile nicht fixiert. Befund in
`30_Areas/firmen/cgt/notizen.md`, Entscheidung über eine Umstellung offen.
Quelle: Export der Tabelle über den Drive-Zugang, 14.09.2026.

## [2026-09-14] umgebaut | Lasche „Kontakte" auf die aufbereitete Struktur

17 Pipedrive-Rohspalten zu 15 gepflegten: vier durchgehend leere raus, Firmen-Zähler und
abgeleitetes Land rein, sortiert nach Firma. 225 Zeilen rein, 225 raus. Werkzeug
`40_Resources/tools/kontakte_umbau.py`, Länderlogik nach `laender.py` herausgezogen und mit
`pipedrive_kontakte.py` geteilt. Routine-Runbook auf die neuen Spalten umgestellt. Gelernt:
deutsche Locale braucht Semikolons in Formeln, wachsende Bereiche müssen offen sein.
Quelle: `30_Areas/firmen/cgt/notizen.md`.

## [2026-09-15] gebaut | Slack-Auslöser für die Kontakte-Routine

Dem API-Trigger nachgegangen: Routinen haben einen `/fire`-Endpunkt (401 statt 404 belegt,
dass er unsere Routine kennt). `40_Resources/tools/slack_ausloeser.gs` nimmt Slacks Event an
und startet die Routine; Filterlogik gegen vierzehn Ereignisformen geprüft. Nicht
bereitgestellt — Token und Event-Subscription gehen nur von Hand. Alibaba-Routine für
Saschas zwei Wochen Abwesenheit pausiert.
Quelle: `30_Areas/firmen/cgt/notizen.md`.

