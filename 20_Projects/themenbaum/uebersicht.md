# Themenbaum

**Status:** Code fertig und lokal getestet, noch nicht online · **Stand:** 2026-10-04

## Worum es geht

Persönliche To-do-Web-App nach Saschas Skizze: Themen (T1, T2 …, z. B. Lykke) als Spalten
nebeneinander, darunter Unterthemen (UT1.1 …) mit Kästchen. Erledigtes rutscht nach unten.
Bearbeiten, Löschen, Verschieben per Ziehen. Drucken zeigt nur offene Aufgaben.
Eigene Datenbank, geschützt mit Zugangscode. Technik: `CLAUDE.md`.

## Nächste Schritte

- [ ] Vercel-Team festlegen, in dem die App läuft _(offen — zur Auswahl: BCD Intern, BCD, VILLA CASPAR, U25)_
- [ ] Projekt + privaten Blob-Store anlegen, Zugangscode als Secret `ACCESS_CODE` setzen
- [ ] Deployen und auf Handy + Rechner testen (inkl. Drucken)
- [ ] Adresse `lykke.milsh.com`: in Vercel am Projekt eintragen, beim DNS-Anbieter von milsh.com CNAME `lykke` → `cname.vercel-dns.com` setzen _(DNS-Anbieter offen)_

## Offene Fragen

- Weitere Felder (Fälligkeit, Priorität)? Bisher nicht gewünscht.
