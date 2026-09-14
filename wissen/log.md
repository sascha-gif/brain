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
