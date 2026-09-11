# Entscheidungen

Entscheidungen, die über ein einzelnes Projekt hinaus gelten. **Neueste oben.**

Eine Entscheidung ohne verworfene Alternative ist keine. Der verworfene Weg ist der
eigentliche Wert des Eintrags: ein halbes Jahr später schlägt sonst jemand genau den Weg
vor, den wir aus gutem Grund verworfen haben.

## 2026-09-11 — Altbestand wird einsortiert, nicht importiert

**Entschieden:** Alles, was schon existiert (Repos, Chat-Exporte, verstreute Notizen), kommt
als Serie einzelner Ingests ins Brain, nie als Massen-Import. Filter ist das Gedächtnis: was
mir nicht aus dem Kopf einfällt, wird nicht gesucht. Reihenfolge ist Skelett zuerst (Kunden,
Projekte), Inhalt danach. Chat-Archive und Repos werden **indiziert statt einsortiert** — je
eine Seite in `40_Resources/` mit Pfad, Datum und Umfang, der Inhalt bleibt draußen.
**Grund:** Ein Brain, das nach einem Wochenende voll aussieht, ist trotzdem wertlos — der Wert
entsteht beim Destillieren, nicht beim Kopieren. Bei großen Stapeln lässt sich außerdem nicht
mehr prüfen, was verzerrt oder dazuerfunden wurde, und dann glaubt man den eigenen Einträgen
nicht mehr. Chat-Exporte sind zu 95 Prozent Wegwerf; einzeln durchgehen kostet Tage und bringt
nichts.
**Verworfen:** Den Altbestand komplett durcharbeiten und einsortieren. Fühlt sich gründlich an,
wird aber nach zwei Abenden abgebrochen und hinterlässt ein halb migriertes Repo, dem niemand
traut. Ebenfalls verworfen: Chat-Exporte ins Repo legen — sie enthalten alles, auch Sensibles,
und stünden dauerhaft in der Git-Historie.
**Folge:** Der operative Ablauf steht als Projekt in
[`20_Projects/brain-migration/uebersicht.md`](../20_Projects/brain-migration/uebersicht.md).
**Quelle:** Gespräch vom 11.09.2026 (nicht im Repo).

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
