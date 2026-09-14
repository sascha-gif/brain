# Google-Sheets-Zugang (Service Account)

Damit Claude in Google Sheets **schreiben** kann. Lesen geht ohne das hier — dafür reicht
der Google-Drive-Connector in Claude. Der kann aber nur lesen, suchen und neue Dateien
anlegen; einzelne Zellen in einer bestehenden Tabelle ändern kann er nicht. Dafür braucht es
den Weg über die Sheets API.

**Stand:** noch nicht eingerichtet — der Key fehlt. Das Skript liegt bereit,
`40_Resources/tools/gsheets.py`.

## Wo der Key liegt

Nicht im Repo. Der Service-Account-Key ist eine JSON-Datei und gehört:

| Wo gearbeitet wird | Wo der Key liegt |
|---|---|
| Lokal (CLI) | `~/.config/gcloud/brain-sheets.json`, Pfad in `GOOGLE_APPLICATION_CREDENTIALS` |
| Cloud-Session (claude.ai/code) | Umgebungsvariable `GOOGLE_SERVICE_ACCOUNT_JSON` im Environment, Inhalt = kompletter JSON-Text |

Der Key ist ein Passwort-Äquivalent: Wer ihn hat, kann alles, was der Service Account darf.
Nie in eine Datei im Repo, nie in einen Chat, nie in eine E-Mail.

## Einrichten (einmalig, ca. 15 Minuten)

1. [console.cloud.google.com](https://console.cloud.google.com) → Projekt anlegen,
   z. B. `brain-sheets`.
2. „APIs & Dienste" → Bibliothek → **Google Sheets API** aktivieren.
3. „APIs & Dienste" → Anmeldedaten → Anmeldedaten erstellen → **Dienstkonto**.
   Name z. B. `brain-writer`. Rollen kann man überspringen — die Rechte kommen vom Sheet,
   nicht vom Cloud-Projekt.
4. Im angelegten Dienstkonto → Tab „Schlüssel" → Schlüssel hinzufügen → **JSON**.
   Die Datei lädt einmalig herunter; Google zeigt sie nie wieder.
5. Die E-Mail-Adresse des Dienstkontos (`brain-writer@<projekt>.iam.gserviceaccount.com`)
   im Ziel-Sheet als **Bearbeiter** freigeben.
6. Key ablegen wie in der Tabelle oben.

Ohne Schritt 5 sieht der Service Account die Datei nicht — er hat ein eigenes Google-Konto
und ist nicht identisch mit dem eigenen. Eine Freigabe „Jeder mit Link: Bearbeiter" deckt ihn
zwar mit ab, öffnet die Datei aber für jeden, der den Link kennt oder weitergeleitet bekommt.
Gezielte Freigabe ist der bessere Weg.

## Benutzen

    pip install google-auth requests   # einmalig

    python3 40_Resources/tools/gsheets.py tabs   <sheet-id>
    python3 40_Resources/tools/gsheets.py read   <sheet-id> --range "Tabelle1!A1:I200"
    python3 40_Resources/tools/gsheets.py append <sheet-id> --range "Tabelle1!A:I" --row "Thema" "DELTEX" "" "Sascha"
    python3 40_Resources/tools/gsheets.py update <sheet-id> --range "Tabelle1!G12" --row "In Arbeit"

`--dry-run` bei `append` und `update` zeigt nur an, was geschrieben würde.
Die Sheet-ID steht in der URL zwischen `/d/` und `/edit`.

## Bekannte Tabellen

| Tabelle | ID | Eigentümer | Zweck |
|---|---|---|---|
| CGT – Themenplanung | `1p9_9S8D4GiQFz2dKggup7cqoMscewW7p86glvi5k3sA` | thomas.goetz@cg-trade.de | Themen, Fristen, Verantwortliche; zweites Blatt: Handels-Matrix |

Die Themenplanung stand am 14.09.2026 auf „Jeder mit Link: Bearbeiter". Für eine Datei mit
Kundenkontakten, Einkaufspreisen und Lieferantennamen ist das zu weit offen — nach dem
Einrichten des Dienstkontos wieder auf gezielte Freigabe zurückstellen.
