# Google-Sheets-Zugang

Damit Claude in Google Sheets **schreiben** kann. Lesen geht ohne das hier — dafür reicht
der Google-Drive-Connector. Der kann aber nur lesen, suchen und neue Dateien anlegen;
einzelne Zellen in einer bestehenden Tabelle ändern kann er nicht.

**Stand 14.09.2026:** eingerichtet und geprüft. `CGT_SHEETS_URL` und
`CGT_SHEETS_SECRET` liegen im Environment, die Brücke antwortet; Lesen und Schreiben in
der Themenplanung laufen aus einer Cloud-Session heraus. Werkzeuge:
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

Der Weg zum Environment: auf [claude.ai/code](https://claude.ai/code) das **Wolken-Symbol**
in der Zeile über dem Eingabefeld anklicken (es zeigt den Namen des Environments, meist
„Default"). Eine Einstellungsseite oder direkte URL dafür gibt es nicht. Im Menü über das
Environment fahren, rechts das **Zahnrad** anklicken. Im Dialog das Feld
**Environment variables**, Format `.env`, eine Zuweisung pro Zeile, ohne Anführungszeichen.

**Wichtig:** Jede Session kopiert die Variablen einmal beim Start. Eine bereits laufende
Session sieht neue Variablen nicht — nach dem Eintragen also eine **neue Session** starten.
Weil Uploads und Scratchpad-Dateien eine Session nicht überleben, gehört die aufbereitete
Kontaktdatei dort erneut hochgeladen.

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

## Grenzen der Brücke

Sie schreibt Werte und Formeln, keine Formatierung: keine Kopfzeilen-Farbe, keine fixierte
Zeile, kein Autofilter. Das setzt man im Sheet mit zwei Klicks nach (Ansicht → Fixieren,
Daten → Filter erstellen) oder erweitert `sheets_bruecke.gs` um eine `format`-Aktion; dann
muss die Web-App aber neu bereitgestellt werden.

**Formeln brauchen Semikolons.** Die Themenplanung steht auf deutscher Locale, dort trennt
`;` die Argumente. `=COUNTIF(A2:A;"x")` mit Komma liefert in jeder Zelle `#ERROR!` — am
14.09.2026 einmal so eingebaut und wieder ausgebaut. Englische Funktionsnamen versteht Google
dagegen unabhängig von der Locale, `IF` und `COUNTIF` müssen also nicht übersetzt werden.

Bereiche in Formeln, die mit der Tabelle wachsen sollen, nach unten offen lassen
(`$A$2:$A` statt `$A$2:$A$226`). Sonst rechnet die Formel spätere Zeilen nicht mit — genau
die, die eine Routine anhängt.

## Bekannte Tabellen

| Tabelle | ID | Eigentümer | Laschen |
|---|---|---|---|
| CGT – Themenplanung | `1p9_9S8D4GiQFz2dKggup7cqoMscewW7p86glvi5k3sA` | thomas.goetz@cg-trade.de | Monats Plan, Themen, Sales Status, Kontakte |

Die Lasche **Kontakte** trägt seit dem 14.09.2026 die 225 Kontakte aus dem
Pipedrive-Personenexport plus einen aus Slack (Alexandra Ochsenkiel). Zur Aufbereitung des
Exports siehe [`wissen/pipedrive-export.md`](../wissen/pipedrive-export.md).

Am selben Tag von der Pipedrive-Rohstruktur auf die aufbereitete umgestellt
(`40_Resources/tools/kontakte_umbau.py`): **15 Spalten** statt 17, sortiert nach Firma, mit
Firmen-Zähler und abgeleitetem Land.

| A | B | C | D | E | F | G | H | I | J | K | L | M | N | O |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Firma | Kontakte i. Firma | Anrede | Vorname | Nachname | Position | E-Mail | Telefon | Mobil | Land | PLZ | Adresse | Website | Kategorie | Label |

Weggefallen sind vier Spalten, die in allen 225 Zeilen leer waren: Telefon privat, Telefon
sonstige, E-Mail privat, E-Mail sonstige. Land ist bei 173 von 225 bestimmt; leer heißt „aus
den Daten nicht sicher ableitbar", nicht „kein Land".

Die Lasche ist damit nicht mehr die Abbildung eines Exports: Wer sie gegen Pipedrive
vergleicht, muss mit Zeilen rechnen, die dort fehlen, und mit anderen Spaltennamen.

Freigabe am 14.09.2026: Thomas (Eigentümer), Sascha (beide Adressen) und Martin Lindegger
als Bearbeiter — dazu „Jeder mit Link: Bearbeiter". Letzteres ist für eine Datei mit
Einkaufspreisen, Lieferanten und Kundenkontakten zu weit offen und wird nicht gebraucht,
weil alle Beteiligten namentlich eingetragen sind. Sollte auf „Eingeschränkt".

## Slack

Steht in `slack-zugang.md` — CG TRADE ist ein eigener Workspace, den der Claude-Connector
nicht erreicht. Gelesen wird er über eine eigene Slack-App; seit dem 14.09.2026 geht das
auch aus einer Cloud-Session.
