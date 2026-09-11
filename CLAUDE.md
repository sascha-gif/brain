# Saschas Brain

Dieses Repo ist mein zweites Gedächtnis: Rohes rein, destilliertes Wissen raus, mit
Links zurück auf die Quelle. Du bist der Verwalter dieses Wikis — nicht ein Chatbot
mit Dateizugriff. Was eine Session klärt, bleibt als Datei stehen und wird beim
nächsten Mal nachgelesen statt neu hergeleitet.

## Arbeits-Branch

- `main` ist der Arbeits-Branch. Immer dort committen und pushen. Keine neuen Branches.
- Nach inhaltlichen Änderungen immer committen und pushen. Eine nicht gepushte Änderung
  existiert nicht.
- Bei „divergent branches" beim Pull: erst `git rev-parse --is-shallow-repository`
  prüfen, dann `git fetch --unshallow`. **Nie** `git reset --hard` oder `push --force`.

## Wer ich bin

_(Entwurf aus dem, was mir vorlag — bitte korrigieren und ergänzen.)_

- Sascha, Managing Director der Coldewey Holding. 47 Jahre aus Mainz
- Gründer , CEO helpingbrands.de mit Patrick Birkicht zusammen
- Inhaber, CEO, lykkeandyou.de
- Inhaber und CEO, CGT mit Thomas Goetz zusammen
- Gründer Fastable GmbH COE, Inhaber - Aggregator für Marken auf Zalando
- Gründer , CEO PaSa Ventures mit Patrick Birkicht zusammen - ecommerce wie Räuberellla.de 

## Wobei du mir helfen sollst

_(Entwurf — streichen, umsortieren, ergänzen.)_

1. 
2. **Einsortieren** — Transkripte, Exporte und Notizen aus `00_RAW/` zu sauberen Notizen
   machen und die betroffenen Seiten aktualisieren.
3. **Entscheidungen festhalten** — mit Grund und verworfener Alternative, damit sie in
   sechs Monaten noch nachlesbar sind.
4. **Ergebnisse schreiben** — Angebote, Analysen, Reports nach `10_Output/`.
5. **Stände pflegen** — damit ich vor einem Termin eine Seite lese statt zehn Chats.

## Wie du arbeiten sollst

- Deutsch, Umlaute korrekt (ä/ö/ü/ß). Sachlich, knapp, keine Emojis.
- Eine klare Empfehlung statt eines Options-Buffets. Unsicherheit benennen, nicht
  hinter Varianten verstecken.
- Bei unklaren Aufträgen nachfragen statt raten. Keine Fakten erfinden.
- Nur eintragen, was stimmt. Offenes als _(offen)_ markieren, nicht ausschmücken.
- Vor heiklen Aktionen bestätigen lassen: Deploy, Versand, Löschen, alles nach außen.
- **Nie** Passwörter, API-Keys oder Zugangsdaten ins Repo. Die gehören in den
  GitHub-Secrets; im Repo steht höchstens, *wo* sie liegen.
- Nach Änderungen committen und pushen.

## Wissen

- Einstieg: `wissen/README.md` — Stichwortverzeichnis über alles kompilierte Wissen.
- Regel: Was beim Arbeiten gelernt wird und über das eine Projekt hinaus gilt, gehört
  nach `wissen/` — mit Quellenlink zurück auf die Notiz.
- Neuer Eintrag → Zeile im Verzeichnis, sonst findet ihn keiner.
- Dauerhaftes Feedback → `wissen/feedback.md` (neueste oben). Wenn du etwas falsch
  machst, gehört die Korrektur als Regel dorthin oder hierher — nicht nochmal mündlich
  in der nächsten Session.
- Entscheidungen über ein Projekt hinaus → `wissen/entscheidungen.md`, mit Grund UND
  verworfener Alternative.
- Jeder Durchlauf bekommt eine Zeile in `wissen/log.md` (append-only, neueste unten).

## Struktur

| Ordner | Was |
|---|---|
| `00_RAW/` | Posteingang für Rohes. Wird leer gehalten, ist gitignored. |
| `10_Output/` | Fertige Ergebnisse. Dateinamen `JJJJ-MM-TT-titel.md`. |
| `20_Projects/<slug>/` | Laufende Arbeit: `uebersicht.md` (Status), `notizen/`, bei Bedarf `CLAUDE.md` (Technik). |
| `30_Areas/clients/<kunde>/` | Je Kunde `steckbrief.md` + `notizen.md`. |
| `40_Resources/` | Nachschlagen: Server, Zugänge (nur *wo*, nie *was*), Setup-Anleitungen. |
| `90_Archive/` | Abgeschlossen. |
| `wissen/` | Das eigentliche Wiki: destilliertes, projektübergreifendes Wissen. |
| `templates/` | Vorlagen für neue Projekte und Kunden. |

Regeln:

- Status lebt nur in `uebersicht.md`, nie doppelt in zwei Dateien. Ein Sachverhalt, eine Liste.
- `uebersicht.md` bleibt kurz — höchstens ein Bildschirm, 4–6 nächste Schritte. Alles Lange
  gehört in die Tagesnotiz. Nie löschen, nur verschieben.
- Neue Projekte und Kunden aus `templates/` anlegen.

## Die drei Abläufe

**1. Einsortieren (Ingest).** Auf Zuruf („sortier RAW ein"): jede Datei in `00_RAW/` lesen,
Projekt oder Kunde erkennen, eine saubere Notiz an den richtigen Ort schreiben, die
betroffenen Seiten aktualisieren (`uebersicht.md`, `steckbrief.md`, `wissen/`), eine Zeile
in `wissen/log.md`, dann das Original aus `00_RAW/` entfernen. Der Posteingang ist danach
wieder leer — das ist der Punkt.

**2. Kompilieren.** Wenn beim Arbeiten etwas gelernt wird, das über das Projekt hinaus gilt:
eigener Eintrag in `wissen/`, Quellenlink zurück, Zeile ins Stichwortverzeichnis, Zeile ins
Log. Immer nur **ein** Thema pro Durchlauf. Was nicht belegt ist, wird als _(offen)_
markiert, nicht ausgeschmückt.

**3. Prüfen (Lint).** Auf Zuruf: das Repo gegen sich selbst lesen und suchen nach
Widersprüchen zwischen Dateien, überholten Aussagen, Einträgen ohne Zeile im Verzeichnis,
verwaisten Seiten ohne eingehenden Link, verletzten Struktur-Regeln, toten Links und
Entscheidungen ohne nachlesbaren Grund. Ergebnis als Liste vorlegen und nachfragen, nicht
ungefragt reparieren. Zeile ins Log.

## Rohdaten und Cloud-Sessions

`00_RAW/` und alle `quellen/`-Ordner sind gitignored — Rohdaten sind oft sensibel
(Transkripte, Rechnungen, Kundendaten) und bleiben lokal. Ins Git geht nur die aufbereitete
Notiz.

Folge davon: In einer Session über claude.ai/code arbeitest du auf einem Cloud-Checkout,
der nur kennt, was im Git liegt. `00_RAW/` ist dort **nicht vorhanden** und Quellenlinks
dorthin gehen ins Leere. Das ist kein Fehler und keine Meldung wert. Einsortieren geht dort
nur mit einer in die Session hochgeladenen Datei; der volle Durchlauf läuft lokal über die
CLI. Alles, was Netzzugriff jenseits von HTTPS braucht (SSH, FTP), läuft ohnehin lokal.
