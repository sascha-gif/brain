# Kontakte-Routine: Slack `#kontakte` → Lasche „Kontakte"

Was Thomas oder Sascha in den Kanal `#kontakte` (CG TRADE) posten, landet automatisch in der
Lasche **Kontakte** der Tabelle „CGT – Themenplanung". Diese Seite ist die Anleitung, der die
Routine folgt — sie wird bei jedem Lauf gelesen, nicht aus dem Gedächtnis wiederholt.

**Stand 15.09.2026:** läuft **täglich um 9:35** deutscher Zeit. Die Lasche wurde am 14.09. von
der Pipedrive-Rohstruktur (17 Spalten) auf die aufbereitete (15 Spalten) umgestellt — die
Spaltenzuordnung unten ist die neue. Bilderkennung gebaut, aber noch nie an einem echten Bild
gelaufen — im Kanal lag bis dahin keins.

## Takt

Täglich um 9:35 deutscher Zeit (Cron `35 7 * * *`, also 7:35 UTC), über die Routine
„Kontakte aus Slack anlegen (täglich 9:35)", `trig_012tHxtWTqGz3yqxmhm5AmCK`. Jeder Lauf
startet eine frische Session, es gibt kein Gedächtnis zwischen den Läufen.

Am 14.09. war die Routine stündlich eingerichtet; beim Bearbeiten in der Web-UI sprang der
Takt auf täglich, und dabei ist es geblieben. Rechnerisch ist das der bessere Schnitt: rund
0,45 $ pro Lauf (gemessen am ersten Testlauf), also etwa **14 $ im Monat** statt 320 $. Der
Preis ist bis zu ein Tag Verzug, was bei sechs Kontakten im Quartal niemandem wehtut.

Echtzeit („in dem Moment, in dem gepostet wird") geht über einen **API-Trigger**: Routinen
haben einen eigenen `/fire`-Endpunkt, den ein HTTP-POST mit Bearer-Token startet. Slack kann
selbst keinen Token mitschicken, aber die Apps-Script-Brücke läuft ohnehin dauerhaft bei
Google und könnte Slacks Event annehmen und weiterreichen. Damit liefe eine Session nur noch
bei einem echten Post — Echtzeit und billiger zugleich. Gebaut ist das nicht, siehe
[`slack-zugang.md`](slack-zugang.md#echtzeit-statt-takt-der-api-trigger) — _(offen)_.

Wer den Takt ändert, ändert ihn in der Routinenliste des Kontos, nicht hier.

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

    python3 40_Resources/tools/gsheets.py read --range "Kontakte!A1:O400"

Zeile 1 ist die Kopfzeile. Die letzte belegte Zeile ist zugleich die Zahl der Datensätze plus
eins; `append` hängt von allein an der richtigen Stelle an.

Die Brücke antwortet unter Last gelegentlich mit HTTP 404 oder 5xx, obwohl die Bereitstellung
steht. `gsheets.py` wiederholt das seit dem 14.09.2026 dreimal mit wachsendem Abstand. Bricht
es trotzdem ab, ist etwas echt kaputt — dann den Lauf abbrechen und **nicht** teilweise
schreiben.

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

    python3 40_Resources/tools/gsheets.py append --range "Kontakte" --row <15 Werte>

Erst mit `--dry-run` ansehen, dann schreiben. Die Lasche trägt seit dem 14.09.2026 die
aufbereitete Struktur mit **15** Spalten (vorher 17 Pipedrive-Rohspalten):

| # | Spalte | Was hinein gehört |
|---|---|---|
| A | Firma | Steht die Firma schon in der Lasche, **deren** Schreibweise übernehmen („Deichmann SE", nicht „Deichmann"). |
| B | Kontakte i. Firma | **Formel, nicht tippen.** Für eine neue Zeile *n*: `=IF(An="";"";COUNTIF($A$2:$A;An))` |
| C | Anrede | „Herr" oder „Frau" — nur wenn die Quelle es hergibt. **Nie** aus dem Vornamen raten. |
| D | Vorname | |
| E | Nachname | Mehrteilige Namen bleiben zusammen („van Dijk"). |
| F | Position | Alle Zeilen der Signatur zu einer zusammenziehen, nichts weglassen. |
| G | E-Mail | |
| H | Telefon | Was die Signatur als Phone/Tel/T führt. |
| I | Mobil | Mobile/Cell/M. |
| J | Land | Abgeleitet, nicht geraten: `laender.py` nimmt den ausgeschriebenen Landesnamen aus der Adresse, sonst die Vorwahl. Gibt beides nichts her, bleibt es leer. |
| K | PLZ | |
| L | Adresse | Aus der Signatur. Fehlt sie und die Firma steht schon in der Lasche: deren Adresse übernehmen. |
| M | Website | |
| N | Kategorie | Leer lassen. Wird in Pipedrive gepflegt, nicht hier geraten. |
| O | Label | Leer lassen, dito. |

Für Spalte J das Werkzeug benutzen, nicht selbst entscheiden:

    python3 -c "import sys; sys.path.insert(0, '40_Resources/tools'); \
      from laender import land_aus_adresse, land_aus_telefon; \
      print(land_aus_adresse('<Adresse>') or land_aus_telefon('<Tel>', '<Mobil>'))"

Was die Quelle nicht hergibt, bleibt leer. Nichts ausschmücken, nichts ableiten außer Land
nach Regel J und der Firmenadresse nach Regel L.

Steht in `text` eine Adresse als `a (Link: b)`, widersprechen sich Anzeigetext und Mailto-Link
der Signatur. Dann den **Anzeigetext** in die Spalte schreiben und den Widerspruch in der
Notiz vermerken — entscheiden kann das nur ein Mensch.

**Zwei Fallstricke bei Formeln in dieser Tabelle**, beide am 14.09.2026 einmal hineingelaufen:

- Der Argumenttrenner ist ein **Semikolon**, die Tabelle steht auf deutscher Locale. Mit
  Komma liefert jede Zelle `#ERROR!`.
- Der COUNTIF-Bereich ist nach unten **offen** (`$A$2:$A`, nicht `$A$2:$A$226`). Sonst zählt
  die Formel genau die Zeilen nicht mit, die diese Routine anhängt.

**Die Sortierung geht beim Anhängen verloren.** Die Lasche ist nach Firma sortiert, `append`
hängt aber unten an. Eine neue Zeile steht also am Ende, nicht bei ihrer Firma. Das ist
hingenommen: Neu-Einsortieren hieße, alle Zeilen neu zu schreiben, und der Autofilter sortiert
mit zwei Klicks. Wenn es stört, `kontakte_umbau.py` erneut laufen lassen.

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
- Committen und nach `main` pushen — davor `git pull --rebase origin main`. Es kann eine
  zweite Session am selben Repo arbeiten; am 14.09.2026 war das beim ersten Testlauf der Fall.
  Bei einem Konflikt in `notizen.md` oder `wissen/log.md` gilt: **beide** Einträge behalten,
  keinen verwerfen. Das sind Tagebücher, kein Code.

Wurde **nichts** geschrieben, wird auch nichts committet und keine Meldung abgesetzt. Ein
stiller Lauf ist der Normalfall.

### Was die Routine nicht tut

Sie hat einen Auftrag: neue Kontakte eintragen. Nicht dazu gehören Lint-Läufe, Aufräumen in
anderen Dateien, Nachbessern bestehender Zeilen oder das Prüfen anderer Laschen. Fällt beim
Arbeiten etwas auf, kommt es in die Notiz — erledigt wird es auf Zuruf, nicht nebenbei von
einem unbeaufsichtigten Lauf.

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

## Wenn niemand hinsieht

Die Routine läuft auf Anthropics Cloud-Infrastruktur, nicht auf Saschas Rechner. Ob der
Laptop zu ist, ob jemand im Urlaub ist, spielt keine Rolle — Token, Brücke und Repo liegen
alle außerhalb.

**Ein Ausfall heilt sich selbst.** Weil die Routine keinen Merkzettel führt, sondern jedes Mal
gegen die Lasche abgleicht, holt der erste wieder funktionierende Lauf alles nach, was
zwischenzeitlich liegen geblieben ist. Fällt sie eine Woche aus, fehlt am Ende nichts —
solange die Slack-Historie reicht (Free-Plan: 90 Tage).

**Was trotzdem unbemerkt bleibt:** Die Routine ist auf stumm gestellt (`notifications` alle
`false`). Scheitert ein Lauf — Token zurückgezogen, Bereitstellung der Brücke archiviert,
Scope verloren —, merkt das niemand, bis jemand in die Routinenliste schaut. Für längere
Abwesenheiten lohnt sich eine E-Mail-Benachrichtigung: Routinenliste → Routine → Stift →
Benachrichtigungen. Über das MCP-Werkzeug geht das nicht, nur in der Oberfläche.

**Tageslimit:** Routine-Läufe zählen gegen ein Kontingent pro Konto, das sich alle Routinen
teilen. Wer eine zweite Routine im Minutentakt laufen lässt, kann diese hier verdrängen.

## Abschalten

Die Routine steht in der Routinenliste des Kontos („Kontakte aus Slack anlegen"). Pausieren
oder löschen geht dort; ein Lauf ohne neue Kontakte tut ohnehin nichts. Wer nur das Schreiben
stoppen will, ohne die Routine anzufassen: das Secret in der Apps-Script-Brücke zurückziehen
(`40_Resources/google-sheets-zugang.md`).
