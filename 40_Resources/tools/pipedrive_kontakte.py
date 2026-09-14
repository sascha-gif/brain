"""Pipedrive-Personenexport zu einer sauberen Kontakttabelle aufbereiten.

Erzeugt drei Blaetter: "Kontakte" (gefiltert, sortiert nach Firma), "Firmen"
(Uebersicht nach Anzahl Ansprechpartner) und "Hinweise" (Herkunft, Ableitungen).

    python3 40_Resources/tools/pipedrive_kontakte.py <export.xlsx> <ziel.xlsx>

Erwartet den Pipedrive-Export im XLSX-Format, Blatt "person list". Der CSV-Export
aus Pipedrive ist unbrauchbar: kaputte Umlaute, und Firmennamen mit Zeilenumbruch
zerfallen in Geisterzeilen.

Die Ausgabedatei enthaelt Kundendaten und gehoert nicht ins Repo.
"""

import sys

import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter

if len(sys.argv) != 3:
    sys.exit(__doc__)
QUELLE, OUT = sys.argv[1], sys.argv[2]
STAND = datetime.date.today().strftime('%d.%m.%Y')

from laender import LAENDER, VORWAHLEN, clean, land_aus_adresse, land_aus_telefon  # noqa: F401

# --- Quelle: nur die XLSX (die CSV ist derselbe Export mit kaputten Umlauten) ---
wb = openpyxl.load_workbook(QUELLE, read_only=True)
rohzeilen = [[clean(c) for c in r] for r in wb['person list'].iter_rows(values_only=True)]
wb.close()
quelle = [r for r in rohzeilen[1:] if any(r)]

kontakte = []
for r in quelle:
    firma, anrede, vor, nach, position = r[0], r[1], r[2], r[3], r[4]
    adresse, plz, tel, mobil = r[5], r[6], r[7], r[9]
    mail, website, kategorie, label = r[11], r[14], r[15], r[16]
    if not (firma or vor or nach or mail):
        continue
    land = land_aus_adresse(adresse) or land_aus_telefon(tel, mobil)
    kontakte.append(dict(firma=firma, anrede=anrede, vorname=vor, nachname=nach,
                         position=position, mail=mail, telefon=tel, mobil=mobil,
                         land=land, plz=plz, adresse=adresse, website=website,
                         kategorie=kategorie, label=label))

gesehen, eindeutig = set(), []
for k in kontakte:
    sig = (k['vorname'].lower(), k['nachname'].lower(), k['firma'].lower(), k['mail'].lower())
    if sig not in gesehen:
        gesehen.add(sig)
        eindeutig.append(k)

eindeutig.sort(key=lambda k: (k['firma'] == '', k['firma'].lower(),
                              k['nachname'].lower(), k['vorname'].lower()))

SPALTEN = [
    ('Firma', 'firma', 34), ('Kontakte i. Firma', None, 14), ('Anrede', 'anrede', 8),
    ('Vorname', 'vorname', 15), ('Nachname', 'nachname', 18), ('Position', 'position', 30),
    ('E-Mail', 'mail', 32), ('Telefon', 'telefon', 22), ('Mobil', 'mobil', 20),
    ('Land', 'land', 18), ('PLZ', 'plz', 10), ('Adresse', 'adresse', 42),
    ('Website', 'website', 28), ('Kategorie', 'kategorie', 18), ('Label', 'label', 11),
]

ARIAL = 'Arial'
kopf_fill = PatternFill('solid', fgColor='1F3864')
kopf_font = Font(name=ARIAL, size=10, bold=True, color='FFFFFF')
zell_font = Font(name=ARIAL, size=10)
rahmen = Border(bottom=Side(style='thin', color='D9D9D9'))
WRAP_TOP = Alignment(vertical='top', wrap_text=True)

wb = openpyxl.Workbook()

# === Blatt 1: Kontakte ===
ws = wb.active
ws.title = 'Kontakte'
for i, (titel, _, breite) in enumerate(SPALTEN, start=1):
    c = ws.cell(row=1, column=i, value=titel)
    c.font, c.fill = kopf_font, kopf_fill
    c.alignment = Alignment(vertical='center', wrap_text=True)
    ws.column_dimensions[get_column_letter(i)].width = breite
ws.row_dimensions[1].height = 28

ws.cell(row=1, column=2).comment = Comment(
    'Anzahl Kontakte derselben Firma. Formel, zaehlt neue Zeilen automatisch mit.', 'Brain')
ws.cell(row=1, column=10).comment = Comment(
    'Abgeleitet: zuerst aus dem Landesnamen in der Adresse, sonst aus der Telefonvorwahl. '
    'Leer = aus den Daten nicht sicher bestimmbar.', 'Brain')

letzte = len(eindeutig) + 1
for zeile, k in enumerate(eindeutig, start=2):
    for i, (_, feld, _) in enumerate(SPALTEN, start=1):
        wert = (f'=IF(A{zeile}="","",COUNTIF($A$2:$A${letzte},A{zeile}))'
                if feld is None else k[feld])
        c = ws.cell(row=zeile, column=i, value=wert)
        c.font = zell_font
        c.border = rahmen
        c.alignment = Alignment(vertical='top',
                                wrap_text=(feld in ('position', 'adresse', 'firma')))
ws.freeze_panes = 'C2'
ws.auto_filter.ref = f'A1:{get_column_letter(len(SPALTEN))}{letzte}'

# === Blatt 2: Firmen ===
firmen = {}
for k in eindeutig:
    if not k['firma']:
        continue
    e = firmen.setdefault(k['firma'], dict(n=0, kat=set(), land=set(), web=''))
    e['n'] += 1
    if k['kategorie']:
        e['kat'].add(k['kategorie'])
    if k['land']:
        e['land'].add(k['land'])
    if k['website'] and not e['web']:
        e['web'] = k['website']

wf = wb.create_sheet('Firmen')
F_SPALTEN = [('Firma', 40), ('Ansprechpartner', 15), ('Kategorie', 22), ('Land', 18), ('Website', 30)]
for i, (titel, breite) in enumerate(F_SPALTEN, start=1):
    c = wf.cell(row=1, column=i, value=titel)
    c.font, c.fill = kopf_font, kopf_fill
    c.alignment = Alignment(vertical='center')
    wf.column_dimensions[get_column_letter(i)].width = breite
wf.row_dimensions[1].height = 22

for zeile, (name, e) in enumerate(sorted(firmen.items(), key=lambda x: (-x[1]['n'], x[0].lower())), start=2):
    for i, wert in enumerate([name, e['n'], ', '.join(sorted(e['kat'])),
                              ', '.join(sorted(e['land'])), e['web']], start=1):
        c = wf.cell(row=zeile, column=i, value=wert)
        c.font = zell_font
        c.border = rahmen
        c.alignment = Alignment(vertical='top', wrap_text=(i == 1))
wf.freeze_panes = 'A2'
wf.auto_filter.ref = f'A1:E{len(firmen) + 1}'

# === Blatt 3: Hinweise ===
wh = wb.create_sheet('Hinweise')
wh.column_dimensions['A'].width = 110
zeilen = [
    ('Kontakte – Herkunft und Aufbereitung', True),
    ('', False),
    (f'Quelle: Pipedrive-Export "person list", aufbereitet am {STAND}.', False),
    (f'Datensaetze: {len(eindeutig)} Kontakte, {len(firmen)} Firmen.', False),
    ('', False),
    ('Was geaendert wurde:', True),
    ('- Spalten ohne einen einzigen Eintrag entfernt (Telefon privat/sonstige, E-Mail privat/sonstige).', False),
    ('- Zeilenumbrueche in Firmennamen und Adressen zu Leerzeichen zusammengezogen.', False),
    ('- Sortiert nach Firma, dann Nachname; Kontakte ohne Firma stehen am Ende.', False),
    ('- Spalte "Kontakte i. Firma" ist eine Formel (COUNTIF) und zaehlt neue Zeilen mit.', False),
    ('- Spalte "Land" ist abgeleitet: zuerst der Landesname aus der Adresse, sonst die', False),
    ('  Telefonvorwahl. Wo beides fehlt, bleibt das Feld leer - nichts geraten.', False),
    ('', False),
    ('Was NICHT geaendert wurde:', True),
    ('- Telefonnummern stehen im Originalformat (gemischt: +49..., 040..., (646)...).', False),
    ('- Firmennamen unveraendert, auch wo sie eine Domain sind ("bearaby.com").', False),
    ('- Keine Kontakte geloescht, keine Dubletten gefunden.', False),
    ('', False),
    ('Zur zweiten hochgeladenen Datei:', True),
    ('Der CSV-Export enthaelt dieselben Kontakte wie der XLSX-Export, aber mit zerstoerten', False),
    ('Umlauten (aus "Groß" wird "GroÃŸ") und mit Firmennamen, die an Zeilenumbruechen in', False),
    ('zusaetzliche Geisterzeilen zerfallen. Verwendet wurde deshalb nur der XLSX-Export.', False),
]
for i, (text, fett) in enumerate(zeilen, start=1):
    c = wh.cell(row=i, column=1, value=text)
    c.font = Font(name=ARIAL, size=10, bold=fett)

wb.save(OUT)

print(f'Kontakte : {len(eindeutig)}')
print(f'Firmen   : {len(firmen)}, davon {sum(1 for e in firmen.values() if e["n"] > 1)} mit mehreren Ansprechpartnern')
print(f'Land     : {sum(1 for k in eindeutig if k["land"])} von {len(eindeutig)} bestimmt')
print(f'Datei    : {OUT}')


# --- CSV-Fassung des Blattes "Kontakte" ---
import csv as _csv
CSV_OUT = OUT.replace('.xlsx', '.csv')
with open(CSV_OUT, 'w', newline='', encoding='utf-8') as f:
    w = _csv.writer(f)
    w.writerow([t for t, _, _ in SPALTEN])
    for zeile, k in enumerate(eindeutig, start=2):
        w.writerow([f'=IF(A{zeile}="","",COUNTIF($A$2:$A${letzte},A{zeile}))' if feld is None
                    else k[feld] for _, feld, _ in SPALTEN])
print(f'CSV      : {CSV_OUT}')
