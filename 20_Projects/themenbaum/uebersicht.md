# Themenbaum

**Status:** Code fertig und lokal getestet, Installation auf Hetzner steht aus · **Stand:** 2026-10-04

## Worum es geht

Persönliche To-do-Web-App nach Saschas Skizze: Themen (T1, T2 …, z. B. Lykke) als Spalten
nebeneinander, darunter Unterthemen (UT1.1 …) mit Kästchen. Erledigtes rutscht nach unten.
Bearbeiten, Löschen, Verschieben per Ziehen. Drucken zeigt nur offene Aufgaben.
Eigene Datenbank (JSON-Datei auf dem Server), geschützt mit Zugangscode. Läuft auf dem
Hetzner-Server von milsh.com unter `lykke.milsh.com`. Technik: `CLAUDE.md`.

## Nächste Schritte

- [ ] Installation in lokaler CLI-Session nach `ANLEITUNG-DEPLOY.md` (Cloud-Session hat keinen SSH-Zugang)
- [ ] DNS: `lykke.milsh.com` zeigt auf den Hetzner-Server _(offen, wird in Schritt 1 geprüft)_
- [ ] Auf Handy + Rechner testen, inkl. Drucken

## Entscheidungen

- 2026-10-04: Hosting auf dem eigenen Hetzner-Server statt Vercel — Saschas Vorgabe, Server und
  Domain milsh.com sind vorhanden. Verworfen: Vercel mit Blob-Speicher (fremde Teams, zusätzlicher Dienst).
- 2026-10-04: Speicher als JSON-Datei statt Datenbank-Server — eine Person, wenige hundert
  Einträge; tägliche Kopie reicht als Sicherung. Verworfen: SQLite/Postgres (mehr Betrieb ohne Nutzen).

## Offene Fragen

- Weitere Felder (Fälligkeit, Priorität)? Bisher nicht gewünscht.
