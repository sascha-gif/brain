# CGT — Notizen

Neueste oben.

## 2026-09-15 — Slack-Auslöser gebaut, Alibaba-Routine pausiert

**Auslöser.** Der Weg, den Sascha vermutet hatte, existiert: Routinen haben einen
`/fire`-Endpunkt, den ein HTTP-POST mit Bearer-Token startet. Gegengeprüft — der Endpunkt
antwortet für unsere Routine mit `401` (Token fehlt), nicht mit `404`; er kennt sie also.

Slack kann den Aufruf nicht selbst machen, weil seine Events-API keinen Token mitschickt.
Dazwischen steht jetzt [`40_Resources/tools/slack_ausloeser.gs`](../../../40_Resources/tools/slack_ausloeser.gs),
ein eigenes Apps-Script-Projekt neben der Sheets-Brücke. Filterlogik gegen vierzehn
Slack-Ereignisformen geprüft: normaler Post und Visitenkarte kommen durch, Bot-Nachrichten,
Beitritte, Umbenennungen, nachträgliche Edits, Thread-Antworten und fremde Kanäle nicht.

Zwei Konstruktionsentscheidungen, die im Skript begründet stehen:

- **Kein sofortiges Feuern.** Slack wartet nur drei Sekunden und wiederholt sonst die
  Zustellung. Das Skript setzt eine Marke und antwortet gleich; ein Minutentakt feuert
  90 Sekunden später. Nebeneffekt: Drei Posts hintereinander ergeben einen Lauf, nicht drei.
- **Geheimnis im Query-String statt Signaturprüfung.** Apps Script reicht keine HTTP-Header
  an `doPost` weiter, Slacks `X-Slack-Signature` ist damit unprüfbar. Wer die URL kennt, kann
  die Routine auslösen — mehr nicht, der Auslöser nimmt keine Daten entgegen.

Bereitgestellt ist nichts: Token erzeugen und Event Subscriptions einschalten gehen nur von
Hand, beides braucht Sascha. Der tägliche Lauf bleibt als Netz bestehen.

**Alibaba-Routine pausiert.** Auf Zuruf abgeschaltet (`trig_01VneSUhqCBuoNKXFuE9J28T`), weil
Sascha zwei Wochen nicht am Rechner ist. Sie lief alle 20–30 Minuten und hätte Lieferanten
angeschrieben, während acht Punkte auf ihrer Liste auf ihn warten — Gläser messen und
verschicken, Linda Wang 162,50 USD entscheiden, zwei Musterzahlungen. Beim Wiedereinschalten
ist zu beachten: Sie plant sich selbst per `run_once_at` weiter, und der gespeicherte
Zeitpunkt liegt dann in der Vergangenheit. Er muss neu gesetzt werden, sonst läuft sie nicht
wieder an.

## 2026-09-14 — Lasche „Kontakte" auf die aufbereitete Struktur umgestellt

Die Lasche trug die Pipedrive-Rohstruktur; jetzt trägt sie die aufbereitete. Aus 17 Spalten
wurden 15, gemacht mit `40_Resources/tools/kontakte_umbau.py`.

- **Vier Spalten raus** — Telefon privat, Telefon sonstige, E-Mail privat, E-Mail sonstige.
  Vor dem Löschen geprüft: in allen 225 Zeilen leer. Das Skript bricht ab, wenn eine davon
  doch etwas enthält.
- **Sortiert nach Firma**, innerhalb der Firma nach Nachname. Zeilen ohne Firma ans Ende.
- **Spalte „Kontakte i. Firma"** als COUNTIF-Formel. 98 Zeilen gehören zu Firmen mit mehreren
  Ansprechpartnern.
- **Spalte „Land"**, abgeleitet aus dem Landesnamen in der Adresse, sonst aus der
  Telefonvorwahl. Bei 173 von 225 bestimmt; die übrigen 52 bleiben leer, weil die Daten es
  nicht hergeben — nicht geraten.
- Spaltennamen sind jetzt lesbar („Firma" statt „Person - Organisation").

Gegengeprüft: 225 Zeilen rein, 225 raus, kein Kontakt verloren, keiner dazuerfunden. Die alte
Fassung liegt als Sicherung im Scratchpad dieser Session — die ist mit der Session weg.

**Was Sascha von Hand nachziehen muss:** Kopfzeile fixieren und den Autofilter auf A1:O226
setzen. Die Apps-Script-Brücke schreibt Werte und Formeln, keine Formatierung.

Zwei Dinge dabei gelernt, beide in `40_Resources/google-sheets-zugang.md` festgehalten:

- Die Tabelle steht auf **deutscher Locale**: Formeln brauchen Semikolons als
  Argumenttrenner. Mit Komma steht in jeder Zelle `#ERROR!` — erst so gebaut, dann korrigiert.
- Der COUNTIF-Bereich muss nach unten **offen** sein (`$A$2:$A`). Mit festem Ende hätte die
  Formel genau die Zeilen nicht mitgezählt, die die Routine später anhängt.

Die Kontakte-Routine war während des Umbaus abgeschaltet und läuft wieder; ihr Runbook und
ihr Prompt kennen jetzt die 15 Spalten. Eine Sache bleibt schief: `append` hängt unten an,
die Sortierung nach Firma gilt also nur bis zum nächsten neuen Kontakt. Das ist hingenommen —
neu sortieren heißt alle Zeilen neu schreiben, und der Autofilter macht es mit zwei Klicks.

## 2026-09-14 — Lasche „Kontakte" geprüft: Inhalt steht, Aufbereitung fehlt

Unabhängige Kontrolle des Ergebnisses über den Drive-Zugang (Export der Tabelle, nicht über
die Brücke gelesen). Stand der Lasche:

- **226 Zeilen**, also Kopfzeile plus 225 Kontakte. Alexandra Ochsenkiel steht in Zeile 226.
- **Autofilter gesetzt** (A1:Z226).
- 157 verschiedene Firmen.

Was gegenüber der ursprünglichen Absprache („gute Struktur mit Filter und
Firmenzugehörigkeit") noch fehlt — die Lasche trägt die **Pipedrive-Rohstruktur**:

- Spaltennamen sind die Exportnamen („Person - Organisation", „Person - Telefon - Büro").
- **Vier Spalten sind in allen 225 Zeilen leer**: Telefon privat, Telefon sonstige,
  E-Mail privat, E-Mail sonstige.
- **Nicht nach Firma sortiert** — es gilt die Pipedrive-Reihenfolge (Zeile 2 PowerHouse,
  Zeile 3 bearaby.com). Kontakte derselben Firma stehen dadurch verstreut.
- **Keine Spalte „Kontakte i. Firma"**, die zeigt, wo mehrere Ansprechpartner sitzen
  (32 Firmen haben mehr als einen).
- **Kein Land** — weder aus der Adresse noch aus der Vorwahl abgeleitet.
- **Kopfzeile nicht fixiert**, beim Scrollen verschwindet sie.

Die aufbereitete Fassung mit all dem existiert und wurde an Sascha geliefert; sie entsteht
neu mit `40_Resources/tools/pipedrive_kontakte.py`. Ob die Lasche darauf umgestellt wird,
ist offen — es hieße, 225 Zeilen zu ersetzen statt zu ergänzen, und die Routine schreibt
gegen die jetzige Spaltenfolge.

## 2026-09-14 — Kontakte aus Slack laufen jetzt automatisch in die Lasche

Der Abgleich von heute Vormittag ist eine Routine geworden: stündlich liest eine frische
Session den Kanal `#kontakte`, prüft gegen die Lasche „Kontakte" und hängt an, was neu ist.
Anleitung, Dublettenregeln und Spaltenzuordnung in
[`40_Resources/kontakte-routine.md`](../../../40_Resources/kontakte-routine.md).

Was dafür dazukam:

- `slack.py` bekam `scopes`, `holen` und eine JSON-Ausgabe. `holen` legt `nachrichten.json` ab
  und lädt Bildanhänge herunter.
- Thomas hat den Scope `files:read` nachgetragen — damit kann der Bot Visitenkarten-Bilder
  holen. Die Bilder bleiben im Scratchpad, nie im Repo.
- Beim Auspacken der Slack-Links gewinnt jetzt je nach Typ die richtige Hälfte. Slack
  normalisiert `tel:`-Links zu Ziffernbrei (`2126305440`), die lesbare Schreibweise steht nur
  im Anzeigetext — den nimmt das Skript jetzt. Bei `http:` ist es umgekehrt.

Zwei Dinge sind noch ungedeckt:

- **Bilderkennung ist ungetestet.** Der Weg steht, aber im Kanal lag noch nie ein Bild. Die
  erste echte Visitenkarte gehört angesehen, bevor man sich darauf verlässt.
- **Pipedrive bleibt außen vor.** Die Routine schreibt in die Lasche, nicht ins CRM. Damit
  laufen beide weiter auseinander. Das löst erst ein Pipedrive-API-Token.

## 2026-09-14 — Slack-Kanal `#kontakte` abgeglichen, ein Kontakt neu

Erster Durchlauf des Kanals `#kontakte` (CG TRADE) gegen die Lasche „Kontakte" in der
Themenplanung. Ertrag: **ein** neuer Kontakt.

Im Kanal liegen zehn Nachrichten (Historie reicht bis 29.06.2026, Free-Plan schneidet nach
90 Tagen ab), darunter sechs Kontaktposts von Thomas. Fünf davon standen schon im
Pipedrive-Export und damit in der Lasche: Jack Sam Haddad, Hank Shapiro, Joseph Favuzza,
Danielle Manna, Lidia van Dijk. Neu nach Zeile 226 geschrieben:

- **Alexandra Ochsenkiel**, Category Manager Purchasing & International Sourcing
  Accessories, Deichmann SE. Firmenadresse und PLZ aus dem bestehenden Deichmann-Eintrag
  der Lasche übernommen, alles andere aus dem Slack-Post.

Der Kanal hieß bis heute `#pipdrive` und wurde von Thomas in `#kontakte` umbenannt.

Beim Abgleich gefundene Abweichungen zwischen Slack und Lasche — **nicht** geändert,
gehören in Pipedrive korrigiert, nicht in der Tabelle nachgebessert:

- **Joseph Favuzza**: Position steht als „Chief Strategy Officer & President", die
  Signatur sagt „Chief Strategy Officer & President, Business Development".
- **Danielle Manna**: Die Nummer 631-220-6853 steht in der Spalte Telefon Büro, die
  Signatur weist sie als Mobilnummer aus. Ihre zweite Zugehörigkeit „Legacy Licensing
  Group" fehlt ganz.
- **Jack Sam Haddad**: Der Slack-Post widerspricht sich selbst — der Mailto-Link zeigt auf
  `jacksh@haddad.com`, der Anzeigetext auf `jacksam@haddad.com`. Die Lasche führt
  `jacksam@`. Welche stimmt, ist _(offen)_.
- **Hank Shapiro**: Mobilnummer in der Lasche ohne Pluszeichen („1 908.568.3103").

Zwei Nachrichten ohne Kontakt: ein Platzhalter aus X-en und die nackte Adresse
saborn-trading.com — die Firma steht als Saborn Trading mit Hein Holleman ohnehin in der
Lasche.

Nebenbefund: `slack.com` ist aus Cloud-Sessions inzwischen erreichbar, die im Repo
festgehaltene 403-Sperre gilt nicht mehr. Damit könnte der Abgleich als Routine laufen.
Siehe `40_Resources/slack-zugang.md`.

## 2026-09-14 — Pipedrive-Kontakte aufbereitet

224 Kontakte aus einem Pipedrive-Personenexport in eine Tabelle gebracht: sortiert nach
Firma, mit Filter, Spalte „Kontakte i. Firma" (Formel) und abgeleitetem Land. Dazu ein Blatt
„Firmen" (157 Firmen, 32 davon mit mehreren Ansprechpartnern) und ein Blatt „Hinweise".

Ziel ist die Lasche **Kontakte** in „CGT – Themenplanung" — die existiert und ist leer.
Direkt hineinschreiben geht noch nicht, siehe `40_Resources/google-sheets-zugang.md`.
Die aufbereitete Datei liegt nicht im Repo (Kundendaten, E-Mails, Telefonnummern).

Nachbaubar mit `40_Resources/tools/pipedrive_kontakte.py <export.xlsx> <ziel.xlsx>`.

Aus den Daten hängengeblieben:

- Der Pipedrive-**CSV**-Export ist unbrauchbar: Umlaute zerstört („Groß" → „GroÃŸ"), und
  Firmennamen mit Zeilenumbruch zerfallen in Geisterzeilen („powered by",
  „Niederlassung Oberhausen"). Nur der XLSX-Export taugt.
- Vier Spalten waren in allen 224 Zeilen leer: Telefon privat, Telefon sonstige,
  E-Mail privat, E-Mail sonstige.
- Kundenkategorie ist bei 126 von 224 leer. Gefüllt: Postenhändler (38), DELTEX (35),
  Herzbach (15), Lizenzen & Testimonials (5), Ambassador (3), Fandom (1).
- Label wird kaum benutzt: 6× Cold lead, 1× Hot lead.
- Eine Zeile ist in der Quelle kaputt: bei ALDI SÜD steht als Vorname „Infos folgen)" und
  als Nachname „Andy (Aldi Süd aus Hongkong". Unverändert übernommen, gehört in Pipedrive
  korrigiert.

## 2026-09-14 — Themenplanung liegt in Google Sheets

„CGT – Themenplanung", Eigentümer Thomas Goetz, vier Laschen: Monats Plan, Themen,
Sales Status, Kontakte. Rund 160 Themenzeilen, davon 9 auf Sascha. Die Sales-Status-Lasche
ist eine Matrix Händler × Thema (Aldi Nord bis Pepco gegen PET, Hard Rock, Maradonna, MIZU,
PMT) mit dem letzten Kontaktdatum je Feld.

ID und Freigabestand: `40_Resources/google-sheets-zugang.md`.
