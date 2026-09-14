# Kontakte-Routine: Slack `#kontakte` → Lasche „Kontakte"

Was Thomas oder Sascha in den Kanal `#kontakte` (CG TRADE) posten, landet automatisch in der
Lasche **Kontakte** der Tabelle „CGT – Themenplanung". Diese Seite ist die Anleitung, der die
Routine folgt — sie wird bei jedem Lauf gelesen, nicht aus dem Gedächtnis wiederholt.

**Stand 14.09.2026:** eingerichtet, läuft stündlich. Bilderkennung gebaut, aber noch nie an
einem echten Bild gelaufen — im Kanal lag bis dahin keins.

## Takt

Stündlich, jeweils zur vollen Stunde, über eine Routine (Trigger `trig_…`, siehe unten).
Jeder Lauf startet eine frische Session, es gibt kein Gedächtnis zwischen den Läufen.

Echtzeit („in dem Moment, in dem gepostet wird") ginge nur mit einem Server, der dauerhaft an
Slacks Events-API hängt. Den gibt es nicht und er wäre für ein paar Kontakte im Monat zu viel
Apparat. Eine Stunde Verzug ist der Preis dafür.

## Kein Merkzettel, sondern Abgleich

Die Routine merkt sich **nicht**, was sie zuletzt gesehen hat. Sie liest jedes Mal die volle
Kanalhistorie und gleicht gegen die Lasche ab. Gründe:

- Der Slack-Free-Plan schneidet nach 90 Tagen ab, die Historie bleibt also klein.
- Ein Merkzettel kann veralten, verlorengehen oder überspringen. Der Abgleich gegen die
  Zieltabelle ist selbstheilend: Was drinsteht, steht drin, egal welcher Lauf es geschrieben hat.
- Nachträglich bearbeitete oder spät entdeckte Posts werden so mitgenommen.

Der Preis: Bilder werden bei jedem Lauf neu heruntergeladen und angesehen. Bei der aktuellen
Menge ist das nicht der Rede wert. Wenn der Kanal einmal Dutzende Bilder trägt, gehört hier
ein Merkzettel hin.

## Ablauf

### 1. Holen

    python3 40_Resources/tools/slack.py holen --ziel <scratchpad>/kontakte --limit 200

Schreibt `nachrichten.json` (Feld `text` aufbereitet, `roh` als Beleg) und lädt Bildanhänge
nach `bilder/`. Bricht das ab, ist meist der Grund in `40_Resources/slack-zugang.md` erklärt;
`slack.py scopes` zeigt, ob ein Scope fehlt.

**Die Bilder bleiben im Scratchpad.** Visitenkarten sind Kundendaten und gehören nie ins Repo,
wie `00_RAW/` auch nicht.

### 2. Zieltabelle lesen

    python3 40_Resources/tools/gsheets.py read --range "Kontakte!A1:Q400"

Zeile 1 ist die Kopfzeile. Die letzte belegte Zeile ist zugleich die Zahl der Datensätze plus
eins; `append` hängt von allein an der richtigen Stelle an.

### 3. Kontakte erkennen

Jede Nachricht durchgehen. Bildanhänge mit dem Read-Werkzeug ansehen — Visitenkarten und
Screenshots von Signaturen zählen wie Text.

Kein Kontakt und damit zu überspringen sind: Systemmeldungen („ist dem Channel beigetreten",
Umbenennungen), Platzhalter, nackte Firmenadressen ohne Person, Gesprächsbeiträge.

Ein Kontakt braucht mindestens einen **Namen**. Alles andere darf fehlen.

### 4. Dubletten aussortieren

Gegen die Lasche prüfen, in dieser Reihenfolge:

1. **E-Mail** — gleiche Adresse (Groß/Kleinschreibung egal) ist dieselbe Person.
2. **Vor- und Nachname** — gleiche Schreibweise ist dieselbe Person.
3. **Nachname + Organisation** — fängt „Alexandra" gegen „Alex" ab.

Bei einem Treffer wird **nichts** geschrieben, auch dann nicht, wenn der Slack-Post ein Feld
trägt, das in der Lasche leer ist. Bestehende Zeilen ändert die Routine nicht — dafür gibt es
Punkt 6.

Am 14.09.2026 waren fünf von sechs Posts Dubletten. Das ist der Normalfall, nicht der Ausnahmefall.

### 5. Neue Zeilen anhängen

    python3 40_Resources/tools/gsheets.py append --range "Kontakte" --row <17 Werte>

Erst mit `--dry-run` ansehen, dann schreiben. Die 17 Spalten in dieser Reihenfolge:

| # | Spalte | Was hinein gehört |
|---|---|---|
| A | Person - Organisation | Firmenname. Steht die Firma schon in der Lasche, **deren** Schreibweise übernehmen („Deichmann SE", nicht „Deichmann"). |
| B | Person - Geschlecht | „Herr" oder „Frau" — nur wenn die Quelle es hergibt. **Nie** aus dem Vornamen raten. |
| C | Person - Vorname | |
| D | Person - Nachname | Mehrteilige Namen bleiben zusammen („van Dijk"). |
| E | Person - Position | Alle Zeilen der Signatur zu einer zusammenziehen, nichts weglassen. |
| F | Organisation - Adresse | Aus der Signatur. Fehlt sie und die Firma steht schon in der Lasche: deren Adresse übernehmen. |
| G | Organisation - PLZ | |
| H | Person - Telefon - Büro | Was die Signatur als Phone/Tel/T führt. |
| I | Person - Telefon - Privat | War im Export durchgehend leer. |
| J | Person - Telefon - Mobil | Mobile/Cell/M. |
| K | Person - Telefon - Sonstiger | |
| L | Person - E-Mail-Adresse - Büro | |
| M | Person - E-Mail-Adresse - Privat | War im Export durchgehend leer. |
| N | Person - E-Mail-Adresse - Sonstiger | |
| O | Organisation - Website | |
| P | Person - Kundenkategorie | Leer lassen. Wird in Pipedrive gepflegt, nicht hier geraten. |
| Q | Person - Label | Leer lassen, dito. |

Was die Quelle nicht hergibt, bleibt leer. Nichts ausschmücken, nichts ableiten außer der
Firmenadresse nach Regel F.

Steht in `text` eine Adresse als `a (Link: b)`, widersprechen sich Anzeigetext und Mailto-Link
der Signatur. Dann den **Anzeigetext** in die Spalte schreiben und den Widerspruch in der
Notiz vermerken — entscheiden kann das nur ein Mensch.

### 6. Auffälligkeiten notieren, nicht reparieren

Weicht ein Slack-Post von einer bestehenden Zeile ab (andere Position, Nummer in der falschen
Spalte, fehlende Zweitfirma), wird die Zeile **nicht** geändert. Die Lasche ist eine Kopie aus
Pipedrive; dort gehört es korrigiert, sonst ist es beim nächsten Export wieder weg. Solche
Funde kommen in die Notiz.

### 7. Festhalten

Nur wenn etwas geschrieben wurde:

- Notiz in `30_Areas/firmen/cgt/notizen.md`, neueste oben: was neu ist, was Dublette war, was
  auffiel.
- Zeile in `wissen/log.md`, unten angehängt.
- Committen und nach `main` pushen.

Wurde **nichts** geschrieben, wird auch nichts committet und keine Meldung abgesetzt. Ein
stiller Lauf ist der Normalfall.

## Grenzen

- **Eine Stunde Verzug**, siehe „Takt".
- **Bilderkennung ungetestet.** Der Weg ist gebaut (`files:read` liegt seit 14.09.2026 vor,
  `slack.py holen` lädt herunter), aber im Kanal lag noch nie ein Bild. Der erste Lauf mit
  einer echten Visitenkarte gehört angesehen.
- **Pipedrive bleibt außen vor.** Dort ist das CRM, aber es gibt keinen Zugang. Die Lasche ist
  der Behelf. Solange das so ist, laufen beide auseinander: Was direkt in Pipedrive angelegt
  wird, sieht diese Routine nicht, und was sie schreibt, kommt nicht in Pipedrive an.
- **Threads werden nicht gelesen.** Nur Nachrichten im Kanal selbst. Bisher postet niemand
  Kontakte in Threads.
- **Nur `#kontakte`.** Der Bot ist in keinem anderen Kanal, siehe `40_Resources/slack-zugang.md`.

## Abschalten

Die Routine steht in der Routinenliste des Kontos („Kontakte aus Slack anlegen"). Pausieren
oder löschen geht dort; ein Lauf ohne neue Kontakte tut ohnehin nichts. Wer nur das Schreiben
stoppen will, ohne die Routine anzufassen: das Secret in der Apps-Script-Brücke zurückziehen
(`40_Resources/google-sheets-zugang.md`).
