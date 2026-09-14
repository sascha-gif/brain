#!/usr/bin/env python3
"""Slack-Kanaele lesen — fuer Workspaces, die der Claude-Connector nicht erreicht.

Braucht ein Bot-Token aus einer eigenen Slack-App:

    SLACK_CGT_TOKEN     Bot User OAuth Token, beginnt mit xoxb-

Die App braucht die Scopes channels:history, channels:read, users:read,
files:read (bei privaten Kanaelen zusaetzlich groups:history, groups:read) und
muss im Kanal eingeladen sein: /invite @NameDerApp

Aufrufe:
    slack.py channels
    slack.py read --channel C0A7M1Y1JTC [--limit 100] [--since 2026-09-01]
    slack.py read --files-to ./anhaenge      # Anhaenge mit herunterladen

Einrichtung: 40_Resources/slack-zugang.md
"""

import argparse
import datetime
import os
import sys

API = 'https://slack.com/api'
KANAL_KONTAKTE = 'C0A7M1Y1JTC'   # #kontakte im Workspace CG TRADE


def sitzung():
    token = os.environ.get('SLACK_CGT_TOKEN')
    if not token:
        sys.exit('SLACK_CGT_TOKEN fehlt. Details: 40_Resources/slack-zugang.md')
    if not token.startswith('xoxb-'):
        sys.exit('SLACK_CGT_TOKEN sieht falsch aus: erwartet wird ein Bot-Token (xoxb-…). '
                 'xoxp- ist ein Nutzer-Token, xapp- ein App-Level-Token.')
    try:
        import requests
    except ImportError:
        sys.exit('Fehlende Abhaengigkeit: pip install requests')
    s = requests.Session()
    s.headers['Authorization'] = f'Bearer {token}'
    return s


def ruf(s, methode, **parameter):
    antwort = s.get(f'{API}/{methode}', params=parameter, timeout=60).json()
    if not antwort.get('ok'):
        fehler = antwort.get('error', 'unbekannt')
        hinweise = {
            'not_in_channel': 'Der Bot ist nicht im Kanal. In Slack: /invite @NameDerApp',
            'channel_not_found': 'Kanal unbekannt — falsche ID oder falscher Workspace.',
            'missing_scope': 'Der App fehlt ein Scope. Noetig: channels:history, '
                             'channels:read, users:read (privat: groups:*). Nach dem '
                             'Nachtragen die App neu installieren.',
            'invalid_auth': 'Token ungueltig oder zurueckgezogen.',
        }
        sys.exit(f'Slack-Fehler: {fehler}\n' + hinweise.get(fehler, ''))
    return antwort


def namen(s):
    """user_id -> Anzeigename, einmal geladen."""
    tabelle, cursor = {}, None
    while True:
        d = ruf(s, 'users.list', limit=200, **({'cursor': cursor} if cursor else {}))
        for u in d.get('members', []):
            profil = u.get('profile', {})
            tabelle[u['id']] = (profil.get('display_name') or profil.get('real_name')
                                or u.get('name') or u['id'])
        cursor = d.get('response_metadata', {}).get('next_cursor')
        if not cursor:
            return tabelle


def sicherer_name(name):
    """Dateinamen auf Unverfaengliches reduzieren."""
    behalten = ''.join(c if (c.isalnum() or c in '._- ') else '_' for c in name)
    return behalten.strip().replace(' ', '_')[:80] or 'datei'


def datei_laden(s, datei, ordner):
    """Einen Slack-Anhang herunterladen. Gibt den Pfad zurueck oder None."""
    url = datei.get('url_private_download') or datei.get('url_private')
    if not url:
        return None
    antwort = s.get(url, timeout=180)
    if not antwort.ok:
        return None
    # Ohne files:read liefert Slack eine HTML-Anmeldeseite statt der Datei.
    if antwort.headers.get('Content-Type', '').startswith('text/html'):
        return None
    os.makedirs(ordner, exist_ok=True)
    pfad = os.path.join(ordner, f"{datei.get('id', 'F')}_{sicherer_name(datei.get('name', 'datei'))}")
    with open(pfad, 'wb') as f:
        f.write(antwort.content)
    return pfad


def cmd_channels(s, args):
    cursor = None
    while True:
        d = ruf(s, 'conversations.list', limit=200, exclude_archived='true',
                types='public_channel,private_channel', **({'cursor': cursor} if cursor else {}))
        for k in d.get('channels', []):
            mitglied = 'Bot drin' if k.get('is_member') else '—'
            print(f"{k['id']}\t#{k['name']}\t{mitglied}")
        cursor = d.get('response_metadata', {}).get('next_cursor')
        if not cursor:
            return


def cmd_read(s, args):
    parameter = {'channel': args.channel, 'limit': min(args.limit, 200)}
    if args.since:
        try:
            tag = datetime.datetime.strptime(args.since, '%Y-%m-%d')
        except ValueError:
            sys.exit('--since braucht das Format JJJJ-MM-TT')
        parameter['oldest'] = str(tag.timestamp())

    nachrichten, cursor = [], None
    while len(nachrichten) < args.limit:
        d = ruf(s, 'conversations.history', **parameter,
                **({'cursor': cursor} if cursor else {}))
        nachrichten.extend(d.get('messages', []))
        cursor = d.get('response_metadata', {}).get('next_cursor')
        if not cursor or not d.get('has_more'):
            break

    leute = namen(s)
    for m in reversed(nachrichten[:args.limit]):          # aelteste zuerst
        zeit = datetime.datetime.fromtimestamp(float(m['ts'])).strftime('%Y-%m-%d %H:%M')
        wer = leute.get(m.get('user', ''), m.get('username', 'unbekannt'))
        print(f'--- {zeit} | {wer} | ts={m["ts"]}')
        print(m.get('text', '').strip())
        for datei in m.get('files', []):
            beschreibung = f'{datei.get("name", "?")} ({datei.get("mimetype", "?")})'
            if args.files_to:
                pfad = datei_laden(s, datei, args.files_to)
                if pfad:
                    print(f'    [Anhang: {beschreibung} -> {pfad}]')
                else:
                    print(f'    [Anhang: {beschreibung} — Download fehlgeschlagen. '
                          f'Scope files:read gesetzt und App danach neu installiert?]')
            else:
                print(f'    [Anhang: {beschreibung} — mit --files-to VERZEICHNIS herunterladen]')
        print()


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='befehl', required=True)
    sub.add_parser('channels', help='Kanaele auflisten, die der Bot sieht')
    r = sub.add_parser('read', help='Nachrichten eines Kanals lesen')
    r.add_argument('--channel', default=KANAL_KONTAKTE, help=f'Standard: {KANAL_KONTAKTE} (#kontakte)')
    r.add_argument('--limit', type=int, default=100, help='Anzahl Nachrichten (Standard 100)')
    r.add_argument('--since', metavar='JJJJ-MM-TT', help='nur ab diesem Tag')
    r.add_argument('--files-to', metavar='VERZEICHNIS',
                   help='Anhaenge dorthin herunterladen (braucht den Scope files:read)')

    args = p.parse_args()
    {'channels': cmd_channels, 'read': cmd_read}[args.befehl](sitzung(), args)


if __name__ == '__main__':
    main()
