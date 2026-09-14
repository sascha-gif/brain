#!/usr/bin/env python3
"""Lesen und Schreiben in Google Sheets.

Zwei Wege, gleiche Aufrufe. Der erste, der konfiguriert ist, wird genommen:

  1. Apps-Script-Bruecke (Standard bei uns, siehe sheets_bruecke.gs)
       CGT_SHEETS_URL      /exec-URL der Web-App
       CGT_SHEETS_SECRET   dasselbe Secret wie im Skript

  2. Dienstkonto ueber die Sheets API — nur nutzbar, wenn die Organisation
     Dienstkontoschluessel erlaubt (bei uns per Richtlinie gesperrt)
       GOOGLE_SERVICE_ACCOUNT_JSON     Inhalt der Key-Datei
       GOOGLE_APPLICATION_CREDENTIALS  alternativ Pfad zur Key-Datei

Aufrufe:
    gsheets.py tabs   [--sheet-id ID]
    gsheets.py read   --range "Kontakte!A1:O50"
    gsheets.py append --range "Kontakte" --row "Wert" "Wert" ...
    gsheets.py append --range "Kontakte" --from-csv kontakte.csv [--skip-header]
    gsheets.py update --range "Themen!G12" --row "In Arbeit"

--dry-run zeigt bei append und update nur an, was geschrieben wuerde.
Einrichtung und Ablage der Zugangsdaten: 40_Resources/google-sheets-zugang.md
"""

import argparse
import csv
import json
import os
import re
import sys

SHEET_ID_STANDARD = '1p9_9S8D4GiQFz2dKggup7cqoMscewW7p86glvi5k3sA'  # CGT – Themenplanung
API = 'https://sheets.googleapis.com/v4/spreadsheets'
SCOPE = 'https://www.googleapis.com/auth/spreadsheets'


def fehlt(text):
    sys.exit(text + '\nDetails: 40_Resources/google-sheets-zugang.md')


def bereich_zerlegen(angabe):
    """'Kontakte!A1:O50' -> ('Kontakte', 'A1:O50'); 'Kontakte' -> ('Kontakte', '')."""
    if '!' in angabe:
        blatt, _, zellen = angabe.partition('!')
        return blatt.strip("'"), zellen
    return angabe.strip("'"), ''


# --------------------------------------------------------------- Bruecke

class Bruecke:
    """Schreibt ueber die Apps-Script-Web-App."""

    name = 'Apps-Script-Bruecke'

    def __init__(self, url, secret, sheet_id):
        self.url, self.secret, self.sheet_id = url, secret, sheet_id

    def ruf(self, **nutzlast):
        import requests
        nutzlast['secret'] = self.secret
        antwort = requests.post(self.url, json=nutzlast, timeout=120,
                                headers={'Content-Type': 'application/json'})
        if not antwort.ok:
            sys.exit(f'HTTP {antwort.status_code} von der Bruecke: {antwort.text[:300]}')
        try:
            daten = antwort.json()
        except ValueError:
            sys.exit('Die Bruecke hat kein JSON geliefert. Ist die Web-App auf '
                     '"Zugriff: Jeder" bereitgestellt?\n' + antwort.text[:300])
        if 'error' in daten:
            sys.exit('Fehler aus der Bruecke: ' + str(daten['error']))
        return daten

    def tabs(self):
        return self.ruf(action='tabs')['tabs']

    def read(self, blatt, zellen):
        return self.ruf(action='read', tab=blatt, range=zellen)['values']

    def append(self, blatt, zeilen):
        d = self.ruf(action='append', tab=blatt, rows=zeilen)
        return f"{d['appended']} Zeilen ab Zeile {d['from']}"

    def update(self, blatt, zellen, zeilen):
        d = self.ruf(action='update', tab=blatt, range=zellen, rows=zeilen)
        return f"{d['updated']} ueberschrieben ({d['rows']} Zeilen)"


# ------------------------------------------------------------ Sheets API

class SheetsApi:
    """Schreibt direkt ueber die Sheets API mit einem Dienstkonto."""

    name = 'Sheets API (Dienstkonto)'

    def __init__(self, sheet_id):
        self.sheet_id = sheet_id
        self._sitzung = None

    @property
    def sitzung(self):
        if self._sitzung:
            return self._sitzung
        try:
            import google.auth.transport.requests
            import requests
            from google.oauth2 import service_account
        except ImportError:
            fehlt('Fehlende Abhaengigkeit: pip install google-auth requests')

        roh = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
        pfad = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if roh:
            creds = service_account.Credentials.from_service_account_info(
                json.loads(roh), scopes=[SCOPE])
        elif pfad and os.path.exists(pfad):
            creds = service_account.Credentials.from_service_account_file(pfad, scopes=[SCOPE])
        else:
            fehlt('Kein Zugang konfiguriert.')
        creds.refresh(google.auth.transport.requests.Request())
        self._sitzung = requests.Session()
        self._sitzung.headers['Authorization'] = f'Bearer {creds.token}'
        return self._sitzung

    def pruef(self, antwort):
        if antwort.ok:
            return antwort.json()
        try:
            meldung = antwort.json()['error']['message']
        except (ValueError, KeyError):
            meldung = antwort.text[:300]
        sys.exit(f'API-Fehler {antwort.status_code}: {meldung}')

    def tabs(self):
        d = self.pruef(self.sitzung.get(f'{API}/{self.sheet_id}',
                                        params={'fields': 'sheets.properties.title'}))
        return [s['properties']['title'] for s in d.get('sheets', [])]

    def read(self, blatt, zellen):
        bereich = f'{blatt}!{zellen}' if zellen else blatt
        return self.pruef(self.sitzung.get(f'{API}/{self.sheet_id}/values/{bereich}')).get('values', [])

    def append(self, blatt, zeilen):
        d = self.pruef(self.sitzung.post(
            f'{API}/{self.sheet_id}/values/{blatt}:append',
            params={'valueInputOption': 'USER_ENTERED', 'insertDataOption': 'INSERT_ROWS'},
            json={'values': zeilen}))
        return d.get('updates', {}).get('updatedRange', '?')

    def update(self, blatt, zellen, zeilen):
        d = self.pruef(self.sitzung.put(
            f'{API}/{self.sheet_id}/values/{blatt}!{zellen}',
            params={'valueInputOption': 'USER_ENTERED'}, json={'values': zeilen}))
        return f"{d.get('updatedRange', '?')} ({d.get('updatedCells', 0)} Zellen)"


def zugang(sheet_id):
    url, secret = os.environ.get('CGT_SHEETS_URL'), os.environ.get('CGT_SHEETS_SECRET')
    if url and secret:
        return Bruecke(url, secret, sheet_id)
    if os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON') or os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
        return SheetsApi(sheet_id)
    fehlt('Kein Zugang konfiguriert. Entweder CGT_SHEETS_URL und CGT_SHEETS_SECRET '
          '(Apps-Script-Bruecke) oder GOOGLE_SERVICE_ACCOUNT_JSON setzen.')


def zeilen_aus_csv(pfad, kopf_ueberspringen):
    with open(pfad, newline='', encoding='utf-8') as f:
        zeilen = [z for z in csv.reader(f) if any(feld.strip() for feld in z)]
    return zeilen[1:] if kopf_ueberspringen else zeilen


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--sheet-id', default=SHEET_ID_STANDARD, help='Standard: CGT – Themenplanung')
    sub = p.add_subparsers(dest='befehl', required=True)

    sub.add_parser('tabs', help='Laschen auflisten')
    for name, hilfe in [('read', 'Bereich lesen'), ('append', 'Zeilen anhaengen'),
                        ('update', 'Bereich ueberschreiben')]:
        s = sub.add_parser(name, help=hilfe)
        s.add_argument('--range', required=True, help='"Lasche" oder "Lasche!A1:O50"')
        if name != 'read':
            s.add_argument('--row', nargs='+', action='append', metavar='WERT',
                           help='eine Zeile; mehrfach angebbar')
            s.add_argument('--from-csv', metavar='DATEI', help='Zeilen aus einer CSV lesen')
            s.add_argument('--skip-header', action='store_true', help='erste CSV-Zeile ueberspringen')
            s.add_argument('--dry-run', action='store_true', help='nur anzeigen, nichts schreiben')

    args = p.parse_args()

    if args.befehl == 'tabs':
        for t in zugang(args.sheet_id).tabs():
            print(t)
        return

    blatt, zellen = bereich_zerlegen(args.range)

    if args.befehl == 'read':
        for zeile in zugang(args.sheet_id).read(blatt, zellen):
            print('\t'.join(str(z) for z in zeile))
        return

    if args.from_csv:
        zeilen = zeilen_aus_csv(args.from_csv, args.skip_header)
    elif args.row:
        zeilen = args.row
    else:
        sys.exit('--row oder --from-csv noetig')

    if args.dry_run:
        print(f'[dry-run] {args.befehl} nach "{blatt}"'
              + (f'!{zellen}' if zellen else '') + f': {len(zeilen)} Zeilen')
        for z in zeilen[:3]:
            print('   ', z[:6], '...' if len(z) > 6 else '')
        if len(zeilen) > 3:
            print(f'    ... und {len(zeilen) - 3} weitere')
        return

    ziel = zugang(args.sheet_id)
    print(f'[{ziel.name}]', end=' ')
    if args.befehl == 'append':
        print('Angehaengt:', ziel.append(blatt, zeilen))
    else:
        if not zellen:
            sys.exit('update braucht einen Zellbereich, z. B. "Kontakte!A1:O225"')
        print('Geschrieben:', ziel.update(blatt, zellen, zeilen))


if __name__ == '__main__':
    main()
