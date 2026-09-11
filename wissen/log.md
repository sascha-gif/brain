# Log

Append-only Protokoll. **Neueste unten.** Ein Eintrag pro Ingest, Kompilieren oder Lint.

Feste Präfixe, damit die Datei mit `grep` auswertbar bleibt:
`## [JJJJ-MM-TT] ingest | <Titel>` · `kompiliert` · `lint` · `setup`

## [2026-09-11] setup | Brain-Grundgerüst angelegt

Ordner, `.gitignore`, `CLAUDE.md`, `wissen/`-Startdateien und Templates angelegt.
Drei Entscheidungen dazu in `entscheidungen.md`.
Quelle: Anleitung „Ein Brain aufsetzen" vom 11.09.2026 (in die Session hochgeladen,
nicht im Repo) und Karpathys LLM-Wiki-Gist.

## [2026-09-11] kompiliert | Wie Altbestand ins Brain kommt

Regel nach `entscheidungen.md`: einsortieren statt importieren, Gedächtnis als Filter,
Skelett vor Inhalt, Chat-Archive und Repos indizieren statt einsortieren.
Operativer Ablauf als Projekt `20_Projects/brain-migration/` angelegt.
Quelle: Gespräch vom 11.09.2026 (nicht im Repo).
