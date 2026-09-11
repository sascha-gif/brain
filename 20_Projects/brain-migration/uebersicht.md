# Brain-Migration

**Status:** angelegt, noch nicht begonnen · **Stand:** 2026-09-11

## Worum es geht

Der Altbestand (Repos, Chat-Exporte, verstreute Markdown-Notizen) soll nicht importiert,
sondern schrittweise einsortiert werden — in der Reihenfolge Skelett zuerst, Inhalt danach.
Das Projekt ist fertig, wenn Kunden und aktive Projekte als Seiten existieren, die
erinnerbaren Entscheidungen nachgetragen sind und die Archive auffindbar indiziert sind.
Warum nicht importiert wird, steht in [`wissen/entscheidungen.md`](../../wissen/entscheidungen.md).

## Nächste Schritte

- [ ] Claude Code lokal einrichten — ohne lokalen Zugriff kein `00_RAW/`, siehe unten
- [ ] Gedächtnis-Liste schreiben: aus dem Kopf, was rein soll. Was nicht einfällt, bleibt draußen
- [ ] Kunden anlegen — je ein `steckbrief.md` aus der Vorlage, zehn Minuten, Lücken erlaubt
- [ ] Aktive Projekte anlegen, Abgeschlossenes direkt nach `90_Archive/`
- [ ] Entscheidungen nachtragen — mit Grund und verworfener Alternative
- [ ] Repos und Chat-Archive indizieren — je eine Seite nach `40_Resources/`, Inhalt bleibt draußen

Reihenfolge ist nicht beliebig: ohne Kunden- und Projektseiten fehlen die Orte, an die eine
Notiz gehört, und alles landet in `wissen/` oder nirgends. Nach jedem Batch ein Lint, sonst
stehen am Ende Seiten ohne Zeile im Verzeichnis und ohne eingehenden Link.

## Offene Fragen

- Was ist der größte Haufen und wo liegt er? _(offen)_
- Welche Repos sind aktiv genug für eine eigene Seite? _(offen)_
- Welche Kunden gehören nach `30_Areas/clients/`? _(offen)_

## Warum das lokal läuft

`00_RAW/` ist gitignored, ein Cloud-Checkout über claude.ai/code sieht die Dateien nicht.
Der Massen-Ingest braucht Claude Code auf dem Rechner; im Browser geht nur, was einzeln
in die Session hochgeladen wird.
