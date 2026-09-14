#!/usr/bin/env python3
"""Die Lasche "Kontakte" von der Pipedrive-Rohstruktur auf die aufbereitete umbauen.

Aus 17 Exportspalten werden 15 gepflegte: vier durchgehend leere fallen weg, ein
Firmen-Zaehler und ein abgeleitetes Land kommen dazu, sortiert wird nach Firma.

    python3 40_Resources/tools/kontakte_umbau.py --dry-run    # nur zeigen
    python3 40_Resources/tools/kontakte_umbau.py --schreiben  # wirklich umbauen

Liest und schreibt ueber `gsheets.py`, also ueber die Apps-Script-Bruecke. Die kann
keine Formatierung — Kopfzeile fixieren und Autofilter bleiben Handarbeit, siehe
40_Resources/google-sheets-zugang.md.

Der Umbau ist einmalig gedacht (14.09.2026). Er liegt hier, weil er nachvollziehbar
sein soll und weil ein zweiter Pipedrive-Import ihn wieder braucht.
"""

import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from laender import clean, land_aus_adresse, land_aus_telefon   # noqa: E402

WERKZEUG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gsheets.py')
LASCHE = 'Kontakte'

# Aus welcher Spalte des Exports (0-basiert) das Zielfeld kommt. None = abgeleitet.
#   0 Organisation  1 Geschlecht  2 Vorname  3 Nachname  4 Position  5 Adresse
#   6 PLZ  7 Tel-Buero  8 Tel-Privat  9 Tel-Mobil  10 Tel-Sonstige  11 Mail-Buero
#   12 Mail-Privat  13 Mail-Sonstige  14 Website  15 Kategorie  16 Label
ZIEL = [
    ('Firma',             0),
    ('Kontakte i. Firma', None),   # COUNTIF-Formel
    ('Anrede',            1),
    ('Vorname',           2),
    ('Nachname',          3),
    ('Position',          4),
    ('E-Mail',            11),
    ('Telefon',           7),
    ('Mobil',             9),
    ('Land',              None),   # aus Adresse, sonst Vorwahl
    ('PLZ',               6),
    ('Adresse',           5),
    ('Website',           14),
    ('Kategorie',         15),
    ('Label',             16),
]
# Spalten des Exports, die ersatzlos wegfallen — vorher gegengeprueft, ob leer.
ENTFAELLT = {8: 'Telefon - Privat', 10: 'Telefon - Sonstiger',
             12: 'E-Mail - Privat', 13: 'E-Mail - Sonstiger'}


def gsheets(*argumente):
    ergebnis = subprocess.run([sys.executable, WERKZEUG, *argumente],
                              capture_output=True, text=True)
    if ergebnis.returncode:
        sys.exit(f'gsheets.py fehlgeschlagen:\n{ergebnis.stderr or ergebnis.stdout}')
    return ergebnis.stdout


def lesen():
    roh = gsheets('read', '--range', f'{LASCHE}!A1:Q400')
    zeilen = [z.split('\t') for z in roh.split('\n')]
    zeilen = [[clean(f) for f in z] for z in zeilen]
    return [z for z in zeilen if any(z)]


def umbauen(zeilen):
    kopf, daten = zeilen[0], zeilen[1:]
    if len(kopf) < 17 or not kopf[0].startswith('Person - Organisation'):
        sys.exit(f'Unerwartete Kopfzeile — schon umgebaut?\n  {kopf[:3]}')

    # Sicherheitsnetz: nur wegwerfen, was wirklich nirgends steht.
    for spalte, name in ENTFAELLT.items():
        gefuellt = [i + 2 for i, z in enumerate(daten)
                    if spalte < len(z) and z[spalte]]
        if gefuellt:
            sys.exit(f'Abbruch: Spalte "{name}" ist nicht leer (Zeile(n) '
                     f'{gefuellt[:5]}). Der Umbau wuerde Daten verlieren.')

    def feld(zeile, i):
        return zeile[i] if i is not None and i < len(zeile) else ''

    kontakte = []
    for z in daten:
        if not any(feld(z, i) for i in (0, 2, 3, 11)):    # Firma, Vor-, Nachname, Mail
            continue
        kontakte.append(z)

    # Nach Firma, dann Nachname, Vorname. Zeilen ohne Firma ans Ende.
    kontakte.sort(key=lambda z: (feld(z, 0) == '', feld(z, 0).lower(),
                                 feld(z, 3).lower(), feld(z, 2).lower()))

    letzte = len(kontakte) + 1
    raus = [[titel for titel, _ in ZIEL] + ['', '']]      # P und Q leeren
    for nr, z in enumerate(kontakte, start=2):
        zeile = []
        for titel, i in ZIEL:
            if titel == 'Kontakte i. Firma':
                # Zwei Fallstricke, beide am 14.09.2026 einmal hineingelaufen:
                # Semikolon statt Komma, weil die Tabelle auf deutscher Locale
                # steht (mit Komma liefert jede Zelle #ERROR!), und ein nach
                # unten offener Bereich $A$2:$A statt $A$2:$A$226 — sonst zaehlt
                # die Formel Zeilen nicht mit, die die Routine spaeter anhaengt.
                zeile.append(f'=IF(A{nr}="";"";COUNTIF($A$2:$A;A{nr}))')
            elif titel == 'Land':
                zeile.append(land_aus_adresse(feld(z, 5))
                             or land_aus_telefon(feld(z, 7), feld(z, 9)))
            else:
                zeile.append(feld(z, i))
        raus.append(zeile + ['', ''])
    return raus


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true', help='nur zeigen, nichts schreiben')
    g.add_argument('--schreiben', action='store_true', help='die Lasche wirklich umbauen')
    p.add_argument('--csv', metavar='DATEI', help='Ergebnis zusaetzlich als CSV ablegen')
    args = p.parse_args()

    alt = lesen()
    neu = umbauen(alt)
    datensaetze = len(neu) - 1

    print(f'{len(alt) - 1} Zeilen gelesen, {datensaetze} nach dem Umbau.')
    mit_land = sum(1 for z in neu[1:] if z[9])
    print(f'Land bestimmt: {mit_land} von {datensaetze}.')
    print(f'Entfallen: {", ".join(ENTFAELLT.values())} (alle leer, geprueft).')
    print('\nKopfzeile:  ' + ' | '.join(t for t, _ in ZIEL))
    print('Erste Zeile:' + ' | '.join(neu[1][:6]))
    print('Letzte:     ' + ' | '.join(neu[-1][:6]))

    if args.csv:
        import csv
        with open(args.csv, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerows(neu)
        print(f'\nCSV: {args.csv}')

    if args.dry_run:
        print('\n[dry-run] Nichts geschrieben.')
        return

    bereich = f'{LASCHE}!A1:Q{len(neu)}'
    print(f'\nSchreibe {bereich} …')
    # In Bloecken, damit die Bruecke nicht an einer Riesennutzlast scheitert.
    BLOCK = 50
    for start in range(0, len(neu), BLOCK):
        teil = neu[start:start + BLOCK]
        von, bis = start + 1, start + len(teil)
        argumente = ['update', '--range', f'{LASCHE}!A{von}:Q{bis}']
        for zeile in teil:
            argumente += ['--row', *zeile]
        gsheets(*argumente)
        print(f'  Zeilen {von}–{bis}')
    print(f'\nFertig. Kopfzeile fixieren und Autofilter auf A1:O{len(neu)} setzen geht '
          'ueber die Bruecke nicht — das sind zwei Klicks im Sheet '
          '(Ansicht → Fixieren → 1 Zeile, Daten → Filter erstellen).')


if __name__ == '__main__':
    main()
