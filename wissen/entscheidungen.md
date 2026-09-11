# Entscheidungen

Entscheidungen, die über ein einzelnes Projekt hinaus gelten. **Neueste oben.**

Eine Entscheidung ohne verworfene Alternative ist keine. Der verworfene Weg ist der
eigentliche Wert des Eintrags: ein halbes Jahr später schlägt sonst jemand genau den Weg
vor, den wir aus gutem Grund verworfen haben.

## 2026-09-11 — `main` ist der einzige Arbeits-Branch

**Entschieden:** Alle Sessions committen und pushen direkt auf `main`. Keine Feature-Branches,
keine Pull Requests.
**Grund:** Das Brain ist ein Wiki mit einem Autor, kein Softwareprojekt mit Review. Ein
Branch-Workflow kostet bei jedem Eintrag Reibung und bringt ohne Reviewer nichts.
**Verworfen:** Arbeit auf Claude-Branches mit Merge nach `main` — das ist der Default vieler
Claude-Code-Umgebungen und musste hier bewusst abgeschaltet werden.
**Quelle:** `CLAUDE.md`, Abschnitt „Arbeits-Branch".

## 2026-09-11 — `00_RAW/` bleibt gitignored

**Entschieden:** Rohdaten (Transkripte, Exporte, `quellen/`-Ordner) bleiben lokal, ins Git
geht nur die aufbereitete Notiz.
**Grund:** Rohes ist regelmäßig sensibel — Meeting-Mitschriften, Rechnungen, Kundendaten.
Ein privates Repo ist kein Grund, das dauerhaft abzulegen.
**Verworfen:** Rohes mit einchecken (so macht es Karpathys Vorbild). Bequemer, weil dann auch
Cloud-Sessions einsortieren könnten und Quellenlinks überall auflösen — aber der Preis ist,
dass jede sensible Datei dauerhaft in der Git-Historie steht.
**Folge:** In Cloud-Sessions über claude.ai/code existiert `00_RAW/` nicht; Einsortieren läuft
dort über hochgeladene Dateien, der volle Durchlauf lokal.
**Quelle:** `CLAUDE.md`, Abschnitt „Rohdaten und Cloud-Sessions".

## 2026-09-11 — Struktur nach PARA statt nach Karpathys `raw/` + `wiki/`

**Entschieden:** Nummerierte Ordner (`00_RAW` … `90_Archive`) plus `wissen/` als Wiki-Teil.
**Grund:** Das Brain trägt nicht nur Wissen, sondern auch laufende Arbeit, Kunden und
Ergebnisse. Die Nummern erzwingen in jeder Ansicht dieselbe Reihenfolge.
**Verworfen:** Karpathys flaches `raw/` + `wiki/{sources,entities,concepts,analyses}`. Sauberer
für ein reines Recherche-Wiki, hat aber keinen Platz für Projekte und Kunden. Die Unterteilung
in `entities/` und `concepts/` kann später in `wissen/` nachgezogen werden, wenn es dort eng wird.
**Quelle:** Anleitung „Ein Brain aufsetzen" vom 11.09.2026 (nicht im Repo).
