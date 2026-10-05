# Auftrag: Themen und Unterthemen in den Themenbaum übernehmen

_Für eine lokale Claude-Code-Session mit SSH-Zugang zum Server von lykke.milsh.com.
Aufruf in der Session: „Lies `20_Projects/themenbaum/ANLEITUNG-IMPORT.md` und übernimm die Themen.“
Voraussetzung: die App läuft schon (`ANLEITUNG-DEPLOY.md`)._

## Was übernommen wird

- **Standard:** alles aus `app/seed.json` (Stand 2026-10-05: 11 Themen, 40 Unterthemen,
  in der Cloud-Session mit Sascha zusammengetragen).
- **Oder neu diktiert:** Sascha nennt Themen/Unterthemen im Chat. Dann schreibst du daraus eine
  Datei im selben Format (siehe unten) und übernimmst diese statt `seed.json`.

Das Werkzeug `app/import.mjs` **ergänzt nur**: neue Themen kommen hinten dazu, neue Unterthemen
zu den offenen Punkten des Themas. Abgleich über den Namen (Groß/Klein egal), Doppeltes wird
übersprungen. Es löscht und ändert nichts, Häkchen bleiben, wie sie sind. Mehrfach ausführen
ist unschädlich.

## Ablauf

1. Aktuellen Code auf den Server bringen (wie Schritt 2 in `ANLEITUNG-DEPLOY.md`, ohne `data/`) —
   `import.mjs` und `seed.json` müssen unter `/opt/themenbaum/` liegen.
2. **Vorschau** (ändert nichts) und Sascha zeigen:
   ```bash
   cd /opt/themenbaum
   sudo -u themenbaum DATA_DIR=/var/lib/themenbaum node import.mjs seed.json
   ```
3. Nach Saschas Okay **übernehmen**:
   ```bash
   sudo -u themenbaum DATA_DIR=/var/lib/themenbaum node import.mjs seed.json --apply
   ```
   Vorher legt die App ohnehin täglich eine Kopie an (`/var/lib/themenbaum/backups/`);
   zusätzlich vor dem ersten Import: `sudo cp /var/lib/themenbaum/themenbaum.json{,.vor-import}`
   (falls die Datei existiert).
4. Prüfen: https://lykke.milsh.com neu laden, Themen sind da. Ein offenes Browserfenster
   lädt den neuen Stand spätestens beim nächsten Speichern automatisch nach.
5. Zeile in `wissen/log.md`, Commit, Push.

Ein Neustart des Dienstes ist nicht nötig.

## Dateiformat für neu diktierte Einträge

```json
{
  "topics": [
    { "name": "Haus", "subs": [ { "t": "Carport streichen" } ] },
    { "name": "Neues Thema", "subs": [ { "t": "Erster Punkt" }, { "t": "Zweiter Punkt" } ] }
  ]
}
```

- `name` = Thema, `t` = Unterthema. IDs und Farben vergibt das Werkzeug selbst.
- Schreibweise glätten wie bisher (Umlaute, Großschreibung am Anfang), Tippfehler nur
  korrigieren, wenn eindeutig — sonst nachfragen.
- Die Datei nicht ins Repo legen, sie ist nach dem Import überflüssig (z. B. `/tmp/import.json`).
