# Google-Sheets-Zugang

Damit Claude in Google Sheets **schreiben** kann. Lesen geht ohne das hier — dafür reicht
der Google-Drive-Connector. Der kann aber nur lesen, suchen und neue Dateien anlegen;
einzelne Zellen in einer bestehenden Tabelle ändern kann er nicht.

**Stand 14.09.2026:** noch nicht eingerichtet. Werkzeuge liegen bereit:
`40_Resources/tools/gsheets.py` (Aufrufe) und `40_Resources/tools/sheets_bruecke.gs`
(die Web-App).

## Warum nicht der Standardweg

Der übliche Weg wäre ein Google-Dienstkonto mit JSON-Schlüssel. Der ist bei uns gesperrt:

> Das Erstellen von Dienstkontoschlüsseln ist deaktiviert.
> Organisationsrichtlinie: `iam.disableServiceAccountKeyCreation`

Die Richtlinie wird in Google-Organisationen automatisch erzwungen („Erzwingungen zur
standardmäßigen Sicherheit"). Aufheben kann sie nur, wer die Rolle
`roles/orgpolicy.policyAdmin` auf der Organisation hat. Das Dienstkonto selbst lässt sich
anlegen — nur eben kein Schlüssel dafür.

## Der Weg, den wir gehen: Apps-Script-Brücke

Ein eigenständiges Apps Script in Saschas Drive, bereitgestellt als Web-App. Es läuft unter
Saschas Google-Konto und braucht keinen Schlüssel — damit greift die Richtlinie nicht.

Einrichten:

1. [script.google.com](https://script.google.com) → **Neues Projekt**, Name z. B.
   „Brain Sheets-Brücke".
2. Inhalt von `40_Resources/tools/sheets_bruecke.gs` komplett einfügen.
3. Oben im Code setzen:
   - `SHEET_ID` — aus der Sheet-URL zwischen `/d/` und `/edit`
   - `SECRET` — lange Zufallskette, z. B. aus `openssl rand -hex 24`
4. **Bereitstellen** → **Neue Bereitstellung** → Typ **Web-App**
   - Ausführen als: **Ich**
   - Zugriff: **Jeder**
   - Bereitstellen, beim Rechtedialog bestätigen. Google warnt bei ungeprüften Skripten —
     „Erweitert" → „Weiter zu …" ist hier richtig, es ist das eigene Skript.
5. Die `/exec`-URL kopieren.

Zugangsdaten ablegen — nie ins Repo, nie in den Chat:

| Wo gearbeitet wird | Wie |
|---|---|
| Cloud-Session (claude.ai/code) | Umgebungsvariablen im Environment: `CGT_SHEETS_URL`, `CGT_SHEETS_SECRET` |
| Lokal (CLI) | dieselben zwei Variablen in der Shell-Konfiguration |

Zurückziehen: im Apps-Script-Projekt **Bereitstellungen verwalten** → archivieren. Damit ist
der Zugang sofort tot, ohne dass an der Tabelle etwas geändert werden muss.

Grenzen: Das Skript kann genau das, was Saschas Konto auch von Hand könnte, und nur auf der
Tabelle, deren ID oben eingetragen ist. Die Web-App-URL ist öffentlich erreichbar; geschützt
wird sie durch das Secret, das bei jedem Aufruf mitgeschickt wird.

## Falls die Richtlinie doch aufgehoben wird

`gsheets.py` kann beide Wege. Liegt `GOOGLE_SERVICE_ACCOUNT_JSON` (oder
`GOOGLE_APPLICATION_CREDENTIALS`) in der Umgebung und keine Brücke, läuft es über die
Sheets API. Dann zusätzlich: Sheets API im Cloud-Projekt aktivieren, Dienstkonto anlegen,
Schlüssel als JSON ziehen, und die `…iam.gserviceaccount.com`-Adresse im Sheet als
Bearbeiter freigeben. Die Aufrufe unten bleiben gleich.

## Benutzen

    pip install requests               # einmalig; für den Dienstkonto-Weg zusätzlich google-auth

    python3 40_Resources/tools/gsheets.py tabs
    python3 40_Resources/tools/gsheets.py read   --range "Kontakte!A1:O50"
    python3 40_Resources/tools/gsheets.py append --range "Kontakte" --from-csv kontakte.csv
    python3 40_Resources/tools/gsheets.py append --range "Themen" --row "Thema" "DELTEX" "" "Sascha"
    python3 40_Resources/tools/gsheets.py update --range "Themen!G12" --row "In Arbeit"

`--dry-run` bei `append` und `update` zeigt nur an, was geschrieben würde — funktioniert
auch ohne Zugangsdaten. Mit `--sheet-id` eine andere Tabelle ansprechen.

## Bekannte Tabellen

| Tabelle | ID | Eigentümer | Laschen |
|---|---|---|---|
| CGT – Themenplanung | `1p9_9S8D4GiQFz2dKggup7cqoMscewW7p86glvi5k3sA` | thomas.goetz@cg-trade.de | Monats Plan, Themen, Sales Status, Kontakte |

Freigabe am 14.09.2026: Thomas (Eigentümer), Sascha (beide Adressen) und Martin Lindegger
als Bearbeiter — dazu „Jeder mit Link: Bearbeiter". Letzteres ist für eine Datei mit
Einkaufspreisen, Lieferanten und Kundenkontakten zu weit offen und wird nicht gebraucht,
weil alle Beteiligten namentlich eingetragen sind. Sollte auf „Eingeschränkt".

## Nebenbefund: Slack-Workspaces

Der Slack-Connector hängt an **einem** Workspace. Erreichbar ist der mit `#cubcoats`,
`#bcd_intern`, `#digital-roots`. Der Workspace **CG TRADE** (`#deltex`, `#hard-rock`,
`#kontakte`, `#pets`) ist ein anderer — Kanal `C0A7M1Y1JTC` antwortet mit
`channel_not_found`. Damit Claude dort lesen kann, muss die Slack-App auch für CG TRADE
autorisiert werden (claude.ai → Einstellungen → Connectors → Slack).
