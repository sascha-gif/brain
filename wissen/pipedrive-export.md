# Pipedrive-Export aufbereiten

Der CSV-Export aus Pipedrive ist nicht direkt verwendbar. Er hat drei Fehler, die immer
zusammen auftreten und sich alle auf dieselbe Ursache zurückführen lassen: **nur die erste
Spalte ist unmaskiert, alle anderen stehen in Anführungszeichen.** Wer das weiß, kann den
Export reparieren; wer es nicht weiß, verliert stillschweigend Datensätze.

Geprüft am 14.09.2026 an zwei Exporten: Personen (224 Datensätze) und Deals (61).

## Die drei Fehler

**1. Kaputte Umlaute.** Die Datei ist UTF-8, wird aber als Latin-1 ausgeliefert:
`Handtücher` wird zu `HandtÃ¼cher`, `Böttcher` zu `BÃ¶ttcher`. Teils doppelt kodiert
(`ALDI SÃœD`), teils gemischt — in derselben Zeile stehen kaputte und heile Umlaute
nebeneinander.

**2. Zeilenumbrüche in der ersten Spalte zerreißen den Datensatz.** Firmennamen in Pipedrive
dürfen mehrzeilig sein. Weil die erste Spalte unmaskiert ist, wird so ein Umbruch beim Export
zum Datensatz-Ende. Aus einem Kontakt werden zwei Bruchstücke:

    ECOVIS KSO Steuerberater + Rechtsanwälte
    Niederlassung Oberhausen,"Frau","Jessica",…

Im Personenexport betraf das 7 Zeilen, darunter vier Kontakte derselben Kanzlei.

**3. Kommas in der ersten Spalte erzeugen eine Spalte zu viel.** `Bridge Marketing Group, Inc`
zerfällt in zwei Felder, der Datensatz hat 18 statt 17 Spalten und alles verrutscht.

## Reparieren

- **Umlaute:** `ftfy.fix_text()` über den gesamten Text. Der naheliegende Einzeiler
  `s.encode('latin-1').decode('utf-8')` reicht **nicht** — sobald in einer Zeile ein heiler
  Umlaut steht, wirft er `UnicodeEncodeError` und die ganze Zeile bleibt kaputt.
- **Zerrissene Datensätze:** Ein echter Datensatzwechsel ist nur ein Zeilenumbruch außerhalb
  von Anführungszeichen, **dessen bisheriger Datensatz auf `"` endet** — die letzte Spalte ist
  immer maskiert. Jeder andere Umbruch außerhalb von Anführungszeichen gehört in den
  Firmennamen und wird zum Leerzeichen. Umbrüche *innerhalb* von Anführungszeichen sind echter
  Feldinhalt (mehrzeilige Adressen) und bleiben stehen.
- **Überzählige Spalten:** Hat ein Datensatz mehr Felder als die Kopfzeile, gehören die
  überzähligen vorne zusammen — mit `, ` wieder zu einem Firmennamen verbinden.
- **Gegenprobe:** Nach der Reparatur muss jeder Datensatz exakt so viele Spalten haben wie die
  Kopfzeile, und eine Suche nach `Ã`, `Â`, `â` darf nichts mehr finden.

## Besser: den XLSX-Export nehmen

`40_Resources/tools/pipedrive_kontakte.py` erwartet bewusst den **XLSX**-Export (Blatt
`person list`) und nennt den CSV-Export unbrauchbar — dort treten die drei Fehler nicht auf.
Wenn die Wahl besteht, also XLSX exportieren und das CSV gar nicht erst anfassen.

Achtung bei der Dateiendung: Ein Export kann `…CSV….xlsx` heißen und trotzdem rohes CSV sein,
das jemand in **eine einzige Tabellenspalte** geklebt hat. Dann ist jede Blattzeile eine
CSV-Zeile — mit allen drei Fehlern oben. Erkennen an `max_column == 1`.

## Telefonnummern behalten ihr Hochkomma

Pipedrive exportiert Nummern als `'+49711/ 28 44 13 - 12`. Das führende Hochkomma nicht
wegputzen: In Google Sheets markiert es den Wert als Text. Ohne das versucht Sheets, `+49…`
als Formel zu lesen.

**Quelle:** Aufbereitung des Personenexports für die Lasche „Kontakte" der CGT-Themenplanung,
Session vom 14.09.2026 (Exportdateien nicht im Repo, siehe
[`40_Resources/google-sheets-zugang.md`](../40_Resources/google-sheets-zugang.md)).
