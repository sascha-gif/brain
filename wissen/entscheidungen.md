# Entscheidungen

Entscheidungen, die über ein einzelnes Projekt hinaus gelten. **Neueste oben.**

Eine Entscheidung ohne verworfene Alternative ist keine. Der verworfene Weg ist der
eigentliche Wert des Eintrags: ein halbes Jahr später schlägt sonst jemand genau den Weg
vor, den wir aus gutem Grund verworfen haben.

## 2026-09-14 — Wiederkehrende Übernahmen gleichen gegen das Ziel ab, statt sich zu merken

**Entschieden:** Eine Routine, die regelmäßig Daten von A nach B schaufelt, führt keinen
Merkzettel über das zuletzt Verarbeitete. Sie liest jedes Mal die Quelle und prüft gegen den
Zielbestand, was schon da ist. Erstmals gebaut für Slack `#kontakte` → Lasche „Kontakte"
(`40_Resources/kontakte-routine.md`).
**Grund:** Der Abgleich ist selbstheilend. Ein Merkzettel hat drei Wege zu versagen — er
veraltet, er geht verloren, oder ein Lauf bricht nach dem Schreiben des Merkzettels und vor
dem Schreiben der Daten ab; danach fehlt ein Datensatz, ohne dass es jemand merkt. Der
Zielbestand dagegen ist die Wahrheit: Was drinsteht, steht drin, egal welcher Lauf es
geschrieben hat. Nachträglich bearbeitete oder spät entdeckte Quellsätze werden mitgenommen.
**Verworfen:** Zeitstempel des letzten Laufs in einer Zustandsdatei — der übliche Weg und bei
großen Mengen der richtige, weil er nicht jedes Mal alles liest. Der Preis des Abgleichs ist
genau das: volle Quelle bei jedem Lauf. Vertretbar, solange die Quelle klein bleibt (bei Slack
sorgt der Free-Plan mit seinen 90 Tagen selbst dafür). Wird sie groß, kippt die Rechnung und
der Merkzettel gehört nachgerüstet.

## 2026-09-14 — Automatische Übernahmen laufen als stündliche Routine, nicht in Echtzeit

**Entschieden:** „Sobald etwas gepostet wird" heißt bei uns: zur nächsten vollen Stunde. Die
Kontakte-Routine läuft stündlich als Trigger, der eine frische Session startet.
**Grund:** Echtzeit bräuchte einen Dienst, der dauerhaft an Slacks Events-API hängt, also
einen Server mit öffentlicher URL, Zertifikat, Überwachung und jemandem, der ihn im Blick
behält. Für ein paar Kontakte im Monat steht das in keinem Verhältnis. Eine Stunde Verzug tut
niemandem weh; niemand wartet vor der Tabelle.
**Verworfen:** Ein Events-API-Endpunkt (zu viel Apparat für die Menge) und ein Lauf einmal
täglich (billiger, aber dann ist ein am Vormittag geposteter Kontakt erst am nächsten Tag da —
und genau dann fragt jemand danach).
**Nachtrag vom selben Tag:** Der erste Testlauf kostete 0,45 $, stündlich also rund 320 $ im
Monat — für sechs Kontakte im vorangegangenen Vierteljahr. Sascha wurde die Rechnung samt
billigerer Takte vorgelegt (4× werktags ≈ 36 $, 2× werktags ≈ 18 $, täglich ≈ 9 $) und hat
sich bewusst für stündlich entschieden. Die Bereitschaft ist ihm den Posten wert. Wer das
später kippen will, braucht ein neues Argument, nicht dieses.

## 2026-09-14 — Schreibzugriff auf Google Sheets über eine Apps-Script-Brücke

**Entschieden:** Schreiben in Google Sheets läuft über ein eigenständiges Apps Script in
Saschas Drive, bereitgestellt als Web-App (`40_Resources/tools/sheets_bruecke.gs`),
angesprochen von `40_Resources/tools/gsheets.py` über URL und Secret aus der Umgebung.
**Grund:** Der geplante Weg über ein Dienstkonto scheitert an einer Organisationsrichtlinie:
`iam.disableServiceAccountKeyCreation` blockiert das Erzeugen von Dienstkontoschlüsseln,
aufheben kann das nur ein Organization Policy Administrator. Das Apps Script läuft unter
Saschas eigenem Konto, braucht keinen Schlüssel und ist damit von der Richtlinie nicht
betroffen. Es kann genau das, was das Konto auch von Hand könnte, und nur auf der einen
eingetragenen Tabelle; Zurückziehen heißt Bereitstellung archivieren.
**Verworfen:** Die Richtlinie für ein Projekt ausnehmen — geht nur mit Org-Admin-Rechten und
schwächt eine Sicherheitsvorgabe für einen Einzelfall. Verworfen auch: das Skript an die
fremde Tabelle binden (Code in Thomas' Datei), OAuth mit Refresh-Token (Browser-Flow, Token
läuft bei Test-Apps nach sieben Tagen ab), Workload Identity Federation (braucht einen
Identitätsanbieter, den es hier nicht gibt).
**Quelle:** Gespräch vom 14.09.2026, `40_Resources/google-sheets-zugang.md`.

## 2026-09-14 — Verworfen: Schreibzugriff über einen Service Account

**Hinfällig seit demselben Tag** — die Richtlinie oben macht diesen Weg unmöglich. Steht
hier, damit ihn niemand ein zweites Mal vorschlägt. `gsheets.py` kann ihn weiterhin, falls
die Sperre je fällt.

**Entschieden war:** Schreiben über ein eigenes Dienstkonto und die Sheets API.
**Grund:** Der Google-Drive-Connector in Claude kann lesen, suchen und Dateien anlegen, aber
keine Zellen in einer bestehenden Tabelle ändern — im Connector-Verzeichnis gibt es auch
keinen Google-Sheets-Connector, der das könnte. Die Sheets API verlangt für jeden Aufruf eine
Identität; eine offene Link-Freigabe allein reicht nicht (geprüft: HTTP 403,
„Method doesn't allow unregistered callers"). Ein Dienstkonto braucht keinen Browser-Flow,
läuft unbeaufsichtigt und kann einzeln wieder entzogen werden.
**Verworfen:** OAuth mit dem eigenen Google-Konto — braucht einen Browser zum Anmelden, das
Token läuft ab, in Cloud-Sessions unbrauchbar. Ebenfalls verworfen: ein Apps Script im Sheet
mit Web-App-Endpunkt — funktioniert, aber der Eigentümer der Tabelle müsste fremden Code in
seiner Datei anlegen und pflegen.
**Quelle:** Gespräch vom 14.09.2026 (nicht im Repo), `40_Resources/google-sheets-zugang.md`.

## 2026-09-11 — Eigene Firmen liegen in `30_Areas/firmen/`, nicht unter `clients/`

**Entschieden:** `30_Areas/` bekommt zwei Unterordner: `firmen/` für eigene Firmen und
Beteiligungen, `clients/` für Kunden. Eigene Vorlage `templates/firma-steckbrief.md`.
**Grund:** Sechs eigene Firmen und Beteiligungen (Coldewey Holding, helpingbrands,
lykkeandyou, CGT, Fastable, PaSa Ventures) sind keine Kunden und keine Projekte — sie laufen
dauerhaft, genau das ist eine Area. Die Kundenvorlage passt inhaltlich nicht: „seit wann,
worüber gekommen" ergibt bei der eigenen Firma keinen Sinn, dafür fehlen Rolle, Beteiligung
und Mitgesellschafter.
**Verworfen:** Firmen unter `clients/` mitführen. Spart einen Ordner, vermischt aber die
beiden Rollen — beim Suchen und beim Einsortieren muss man dann jedes Mal wissen, ob eine
Zeile „Kunde" oder „meine Firma" meint. Ebenfalls verworfen: je Firma ein Projektordner in
`20_Projects/` — Projekte haben ein Ende, Firmen nicht.
**Quelle:** Gespräch vom 11.09.2026 (nicht im Repo), `CLAUDE.md` Abschnitt „Wer ich bin".

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
