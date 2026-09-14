#!/usr/bin/env python3
"""Slack-Kanaele lesen — fuer Workspaces, die der Claude-Connector nicht erreicht.

Braucht ein Bot-Token aus einer eigenen Slack-App:

    SLACK_CGT_TOKEN     Bot User OAuth Token, beginnt mit xoxb-

Die App braucht die Scopes channels:history, channels:read, users:read
(bei privaten Kanaelen zusaetzlich groups:history, groups:read; fuer Bilder
zusaetzlich files:read) und muss im Kanal eingeladen sein: /invite @NameDerApp

Aufrufe:
    slack.py channels
    slack.py scopes
    slack.py read   --channel C0A7M1Y1JTC [--limit 100] [--since 2026-09-01] [--json]
    slack.py holen  --ziel ORDNER [--channel ...] [--since ...]

`holen` schreibt Nachrichten als JSON und laedt Bildanhaenge herunter — die
Vorstufe der Kontakt-Routine, siehe 40_Resources/kontakte-routine.md

Einrichtung: 40_Resources/slack-zugang.md
"""

import argparse
import datetime
import json
import os
import pathlib
import re
import sys

API = 'https://slack.com/api'
KANAL_KONTAKTE = 'C0A7M1Y1JTC'   # #kontakte im Workspace CG TRADE

# Was sich als Visitenkarte lohnt anzuschauen. PDFs koennen Signaturanhaenge sein.
BILD_TYPEN = ('image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp',
              'image/heic', 'application/pdf')


def fehlt(text):
    sys.exit(text + '\nDetails: 40_Resources/slack-zugang.md')


def sitzung():
    token = os.environ.get('SLACK_CGT_TOKEN')
    if not token:
        fehlt('SLACK_CGT_TOKEN fehlt.')
    if not token.startswith('xoxb-'):
        fehlt('SLACK_CGT_TOKEN sieht falsch aus: erwartet wird ein Bot-Token (xoxb-…). '
              'xoxp- ist ein Nutzer-Token, xapp- ein App-Level-Token.')
    try:
        import requests
    except ImportError:
        sys.exit('Fehlende Abhaengigkeit: pip install requests')
    s = requests.Session()
    s.headers['Authorization'] = f'Bearer {token}'
    return s


HINWEISE = {
    'not_in_channel': 'Der Bot ist nicht im Kanal. In Slack: /invite @NameDerApp',
    'channel_not_found': 'Kanal unbekannt — falsche ID oder falscher Workspace.',
    'missing_scope': 'Der App fehlt ein Scope. Noetig: channels:history, '
                     'channels:read, users:read (privat: groups:*, Bilder: files:read). '
                     'Nach dem Nachtragen die App neu installieren.',
    'invalid_auth': 'Token ungueltig oder zurueckgezogen.',
}


def ruf(s, methode, **parameter):
    antwort = s.get(f'{API}/{methode}', params=parameter, timeout=60).json()
    if not antwort.get('ok'):
        fehler = antwort.get('error', 'unbekannt')
        noetig = antwort.get('needed')
        text = f'Slack-Fehler: {fehler}\n' + HINWEISE.get(fehler, '')
        if noetig:
            text += f'\nFehlender Scope: {noetig}'
        sys.exit(text)
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


def historie(s, kanal, limit, seit=None):
    """Nachrichten eines Kanals, aelteste zuerst."""
    parameter = {'channel': kanal, 'limit': min(limit, 200)}
    if seit:
        try:
            tag = datetime.datetime.strptime(seit, '%Y-%m-%d')
        except ValueError:
            sys.exit('--since braucht das Format JJJJ-MM-TT')
        parameter['oldest'] = str(tag.timestamp())

    nachrichten, cursor = [], None
    while len(nachrichten) < limit:
        d = ruf(s, 'conversations.history', **parameter,
                **({'cursor': cursor} if cursor else {}))
        nachrichten.extend(d.get('messages', []))
        cursor = d.get('response_metadata', {}).get('next_cursor')
        if not cursor or not d.get('has_more'):
            break
    return list(reversed(nachrichten[:limit]))


MAIL = re.compile(r'^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$')


def entwirren(text):
    """Slack-Markup zu lesbarem Text.

    Slack macht aus jeder Nummer und Adresse einen Link: <tel:URL|Anzeige>.
    Welche Haelfte taugt, haengt vom Typ ab:

    tel     Anzeige — Slack normalisiert die URL zu Ziffernbrei (2126305440),
            die Anzeige behaelt die lesbare Schreibweise (212-630-5440).
    mailto  Anzeige, wenn sie eine Adresse ist — sie steht so in der Signatur.
            Weicht die URL ab, wird sie in Klammern angehaengt: die beiden
            widersprechen sich gelegentlich und die Wahl trifft nicht dieses Skript.
    http    URL — die Anzeige ist oft gekuerzt ("hier", "authentic.com").
    """
    if not text:
        return ''

    def tel(m):
        return (m.group(2) or '').lstrip('|').strip() or m.group(1)

    def mail(m):
        url = m.group(1).strip()
        anzeige = (m.group(2) or '').lstrip('|').strip()
        if not anzeige or not MAIL.match(anzeige):
            return url
        return anzeige if anzeige.lower() == url.lower() else f'{anzeige} (Link: {url})'

    text = re.sub(r'<mailto:([^|>]+)(\|[^>]*)?>', mail, text)
    text = re.sub(r'<tel:([^|>]+)(\|[^>]*)?>', tel, text)
    text = re.sub(r'<(https?://[^|>]+)(\|[^>]*)?>', r'\1', text)
    for roh, klar in (('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>')):
        text = text.replace(roh, klar)
    return text.strip()


def cmd_scopes(s, args):
    r = s.get(f'{API}/auth.test', timeout=30)
    d = r.json()
    if not d.get('ok'):
        sys.exit(f"Slack-Fehler: {d.get('error')}\n" + HINWEISE.get(d.get('error'), ''))
    hat = (r.headers.get('x-oauth-scopes') or '').split(',')
    print(f"Workspace: {d.get('team')}\nBot: {d.get('user')}\n")
    for scope in ('channels:history', 'channels:read', 'users:read',
                  'groups:history', 'groups:read', 'files:read'):
        print(f"  {'ja ' if scope in hat else 'NEIN'}  {scope}")
    if 'files:read' not in hat:
        print('\nOhne files:read bleiben Bildanhaenge (Visitenkarten) unlesbar.\n'
              'Nachtragen unter api.slack.com/apps -> OAuth & Permissions, '
              'danach die App neu installieren.')


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
    nachrichten = historie(s, args.channel, args.limit, args.since)
    leute = namen(s)

    if args.json:
        raus = []
        for m in nachrichten:
            raus.append({
                'ts': m['ts'],
                'zeit': datetime.datetime.fromtimestamp(float(m['ts'])).isoformat(' ', 'minutes'),
                'wer': leute.get(m.get('user', ''), m.get('username', 'unbekannt')),
                'text': entwirren(m.get('text', '')),
                'roh': m.get('text', ''),
                'dateien': [{'name': f.get('name'), 'mimetype': f.get('mimetype'),
                             'id': f.get('id')} for f in m.get('files', [])],
            })
        print(json.dumps(raus, ensure_ascii=False, indent=2))
        return

    for m in nachrichten:
        zeit = datetime.datetime.fromtimestamp(float(m['ts'])).strftime('%Y-%m-%d %H:%M')
        wer = leute.get(m.get('user', ''), m.get('username', 'unbekannt'))
        print(f'--- {zeit} | {wer} | ts={m["ts"]}')
        print(m.get('text', '').strip())
        for datei in m.get('files', []):
            print(f'    [Anhang: {datei.get("name", "?")} ({datei.get("mimetype", "?")})]')
        print()


def cmd_holen(s, args):
    """Nachrichten als JSON ablegen und Bildanhaenge herunterladen."""
    ziel = pathlib.Path(args.ziel)
    (ziel / 'bilder').mkdir(parents=True, exist_ok=True)

    nachrichten = historie(s, args.channel, args.limit, args.since)
    leute = namen(s)

    # Ohne files:read laufen die Downloads ins Leere. Einmal pruefen statt je Datei.
    kopf = s.get(f'{API}/auth.test', timeout=30)
    darf_dateien = 'files:read' in (kopf.headers.get('x-oauth-scopes') or '')

    eintraege, geladen, uebersprungen = [], 0, 0
    for m in nachrichten:
        e = {
            'ts': m['ts'],
            'zeit': datetime.datetime.fromtimestamp(float(m['ts'])).isoformat(' ', 'minutes'),
            'wer': leute.get(m.get('user', ''), m.get('username', 'unbekannt')),
            'text': entwirren(m.get('text', '')),
            'roh': m.get('text', ''),   # Beleg, falls die Aufbereitung etwas verschluckt
            'bilder': [],
        }
        for datei in m.get('files', []):
            if datei.get('mimetype') not in BILD_TYPEN:
                continue
            if not darf_dateien:
                uebersprungen += 1
                e['bilder'].append({'fehlt': 'files:read', 'name': datei.get('name')})
                continue
            url = datei.get('url_private_download') or datei.get('url_private')
            if not url:
                continue
            endung = pathlib.Path(datei.get('name') or '').suffix or '.bin'
            pfad = ziel / 'bilder' / f"{m['ts']}_{datei['id']}{endung}"
            antwort = s.get(url, timeout=120)
            antwort.raise_for_status()
            pfad.write_bytes(antwort.content)
            geladen += 1
            e['bilder'].append({'datei': str(pfad), 'name': datei.get('name'),
                                'mimetype': datei.get('mimetype')})
        eintraege.append(e)

    (ziel / 'nachrichten.json').write_text(
        json.dumps(eintraege, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'{len(eintraege)} Nachrichten -> {ziel / "nachrichten.json"}')
    print(f'{geladen} Bilder -> {ziel / "bilder"}')
    if uebersprungen:
        print(f'{uebersprungen} Anhaenge uebersprungen: der App fehlt files:read. '
              'Siehe `slack.py scopes`.')


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='befehl', required=True)
    sub.add_parser('channels', help='Kanaele auflisten, die der Bot sieht')
    sub.add_parser('scopes', help='zeigen, welche Scopes das Token hat')

    for name, hilfe in (('read', 'Nachrichten eines Kanals lesen'),
                        ('holen', 'Nachrichten als JSON ablegen, Bilder herunterladen')):
        c = sub.add_parser(name, help=hilfe)
        c.add_argument('--channel', default=KANAL_KONTAKTE,
                       help=f'Standard: {KANAL_KONTAKTE} (#kontakte)')
        c.add_argument('--limit', type=int, default=100, help='Anzahl Nachrichten (Standard 100)')
        c.add_argument('--since', metavar='JJJJ-MM-TT', help='nur ab diesem Tag')
        if name == 'read':
            c.add_argument('--json', action='store_true', help='als JSON ausgeben')
        else:
            c.add_argument('--ziel', required=True, metavar='ORDNER',
                           help='Ordner fuer nachrichten.json und bilder/')

    args = p.parse_args()
    {'channels': cmd_channels, 'scopes': cmd_scopes,
     'read': cmd_read, 'holen': cmd_holen}[args.befehl](sitzung(), args)


if __name__ == '__main__':
    main()
