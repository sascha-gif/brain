#!/usr/bin/env python3
"""Lesen und Schreiben in Google Sheets ueber die Sheets API v4.

Authentifizierung ueber einen Service Account. Der Key kommt aus der Umgebung,
nie aus dem Repo:

    GOOGLE_SERVICE_ACCOUNT_JSON   Inhalt der Key-Datei (JSON als String)
    GOOGLE_APPLICATION_CREDENTIALS  alternativ: Pfad zur Key-Datei

Das Ziel-Sheet muss fuer den Service Account (oder per Link) beschreibbar sein.

Aufrufe:
    gsheets.py tabs   <sheet-id>
    gsheets.py read   <sheet-id> --range "Tabelle1!A1:I200"
    gsheets.py append <sheet-id> --range "Tabelle1!A:I" --row "Wert" "Wert" ...
    gsheets.py update <sheet-id> --range "Tabelle1!G5" --row "In Arbeit"

Mit --dry-run wird nur angezeigt, was geschrieben wuerde.
"""

import argparse
import json
import os
import sys

API = "https://sheets.googleapis.com/v4/spreadsheets"
SCOPE = "https://www.googleapis.com/auth/spreadsheets"


def credentials():
    """Service-Account-Credentials aus der Umgebung laden."""
    try:
        from google.oauth2 import service_account
    except ImportError:
        sys.exit(
            "Fehlende Abhaengigkeit. Einmalig installieren:\n"
            "    pip install google-auth requests"
        )

    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if raw:
        return service_account.Credentials.from_service_account_info(
            json.loads(raw), scopes=[SCOPE]
        )

    path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if path and os.path.exists(path):
        return service_account.Credentials.from_service_account_file(
            path, scopes=[SCOPE]
        )

    sys.exit(
        "Kein Service-Account-Key gefunden. Setze GOOGLE_SERVICE_ACCOUNT_JSON\n"
        "oder GOOGLE_APPLICATION_CREDENTIALS. Details: "
        "40_Resources/google-sheets-zugang.md"
    )


def session():
    """Authentifizierte HTTP-Session."""
    import google.auth.transport.requests
    import requests

    creds = credentials()
    creds.refresh(google.auth.transport.requests.Request())
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {creds.token}"
    return s


def check(response):
    """Fehlermeldung der API lesbar machen."""
    if response.ok:
        return response.json()
    try:
        message = response.json()["error"]["message"]
    except (ValueError, KeyError):
        message = response.text[:500]
    sys.exit(f"API-Fehler {response.status_code}: {message}")


def cmd_tabs(s, args):
    data = check(s.get(f"{API}/{args.sheet_id}", params={"fields": "sheets.properties"}))
    for sheet in data.get("sheets", []):
        p = sheet["properties"]
        grid = p.get("gridProperties", {})
        print(f"{p['title']}\t{grid.get('rowCount', '?')} Zeilen x {grid.get('columnCount', '?')} Spalten")


def cmd_read(s, args):
    data = check(s.get(f"{API}/{args.sheet_id}/values/{args.range}"))
    for row in data.get("values", []):
        print("\t".join(row))


def cmd_append(s, args):
    if args.dry_run:
        print(f"[dry-run] anhaengen an {args.range}: {args.row}")
        return
    data = check(
        s.post(
            f"{API}/{args.sheet_id}/values/{args.range}:append",
            params={"valueInputOption": "USER_ENTERED", "insertDataOption": "INSERT_ROWS"},
            json={"values": [args.row]},
        )
    )
    print("Angehaengt:", data.get("updates", {}).get("updatedRange", "?"))


def cmd_update(s, args):
    if args.dry_run:
        print(f"[dry-run] {args.range} setzen auf: {args.row}")
        return
    data = check(
        s.put(
            f"{API}/{args.sheet_id}/values/{args.range}",
            params={"valueInputOption": "USER_ENTERED"},
            json={"values": [args.row]},
        )
    )
    print("Geschrieben:", data.get("updatedRange", "?"), f"({data.get('updatedCells', 0)} Zellen)")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    for name, help_text in [
        ("tabs", "Tabellenblaetter auflisten"),
        ("read", "Bereich lesen"),
        ("append", "Zeile anhaengen"),
        ("update", "Bereich ueberschreiben"),
    ]:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("sheet_id", help="ID aus der Sheet-URL")
        if name != "tabs":
            p.add_argument("--range", required=True, help='z. B. "Tabelle1!A1:I200"')
        if name in ("append", "update"):
            p.add_argument("--row", nargs="+", required=True, help="Zellwerte der Zeile")
            p.add_argument("--dry-run", action="store_true", help="nur anzeigen, nichts schreiben")

    args = parser.parse_args()
    handler = {"tabs": cmd_tabs, "read": cmd_read, "append": cmd_append, "update": cmd_update}[args.command]
    handler(session(), args)


if __name__ == "__main__":
    main()
