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

## [2026-09-11] setup | Firmen als eigene Area angelegt

`30_Areas/firmen/` mit sechs Steckbrief-Gerüsten (Coldewey Holding, helpingbrands,
lykkeandyou, CGT, Fastable, PaSa Ventures), Vorlage `templates/firma-steckbrief.md`.
`CLAUDE.md` aufgeräumt: Entwurfs-Marker raus, leerer Listenpunkt raus, Struktur ergänzt.
Quelle: Gespräch vom 11.09.2026 (nicht im Repo).

## [2026-09-14] setup | Schreibzugriff auf Google Sheets vorbereitet

Geprüft, warum Claude nicht in die CGT-Themenplanung schreiben kann: Der Drive-Connector kann
keine Zellen ändern, einen Sheets-Connector gibt es nicht, und die Sheets API verlangt auch
bei offener Link-Freigabe eine Identität. Skript `40_Resources/tools/gsheets.py` (lesen,
anhängen, überschreiben) und Anleitung `40_Resources/google-sheets-zugang.md` angelegt.
Offen: Service-Account-Key fehlt noch, ungetestet bis dahin.
Quelle: Gespräch vom 14.09.2026 (nicht im Repo).

## [2026-09-14] ingest | Pipedrive-Kontakte für CGT aufbereitet

224 Kontakte aus dem Pipedrive-Personenexport zu einer Tabelle gemacht (sortiert nach Firma,
Filter, Firmenübersicht, abgeleitetes Land) und an Sascha geliefert. Ziel ist die leere
Lasche „Kontakte" in „CGT – Themenplanung"; direkt hineinschreiben geht erst mit dem
Service-Account-Key. Skript `40_Resources/tools/pipedrive_kontakte.py`, Befunde in
`30_Areas/firmen/cgt/notizen.md`. Die Kontaktdaten selbst bleiben draußen.
Quelle: zwei hochgeladene Pipedrive-Exporte vom 14.09.2026 (nicht im Repo).

## [2026-09-14] setup | Sheets-Schreibzugriff auf Apps-Script-Brücke umgestellt

Der Dienstkonto-Weg ist tot: Google blockiert das Erzeugen von Dienstkontoschlüsseln per
Organisationsrichtlinie (`iam.disableServiceAccountKeyCreation`). Ersatz ist ein
eigenständiges Apps Script als Web-App unter Saschas Konto. `gsheets.py` kann beide Wege
und wählt den, der konfiguriert ist; neu sind `--from-csv` und ein `--dry-run`, der ohne
Zugangsdaten läuft. Brücken-Code in `40_Resources/tools/sheets_bruecke.gs`.
Quelle: Gespräch vom 14.09.2026 (nicht im Repo).

## [2026-09-14] setup | Slack-Zugang für CG TRADE vorbereitet

Der Claude-Connector kann nur einen Workspace; CG TRADE ist ein zweiter und damit außer
Reichweite. Ersatz ist eine eigene Slack-App mit Bot-Token. Lesewerkzeug
`40_Resources/tools/slack.py` (channels, read), Anleitung `40_Resources/slack-zugang.md`.
Offen: Token ins Environment, Takt und Ziel der Kontakt-Ablage.
Quelle: Gespräch vom 14.09.2026 (nicht im Repo).

## [2026-09-14] setup | Sheets-Brücke geprüft, Kontakte geschrieben, Slack blockiert

Beide Zugänge gegengeprüft. **Sheets:** `CGT_SHEETS_URL` und `CGT_SHEETS_SECRET` im
Environment, Brücke antwortet, Laschen der Themenplanung gelesen. Den Pipedrive-Personenexport
aufbereitet (224 Datensätze) und in die bis dahin leere Lasche „Kontakte" geschrieben,
Kopfzeile plus Daten ab Zeile 1. **Slack:** `SLACK_CGT_TOKEN` liegt im Environment, ist aus
einer Cloud-Session aber nicht nutzbar — der Egress-Proxy weist `slack.com:443` mit 403 ab
(Organisationsrichtlinie). Gegenprobe: der Claude-Connector erreicht CG TRADE weiterhin nicht
(`channel_not_found`). #kontakte konnte deshalb nicht gelesen werden. Behebungsweg in
`40_Resources/slack-zugang.md` festgehalten: Netzwerkzugriff des Environments von „Trusted"
auf „Custom" mit `slack.com` in den Allowed domains. Bis dahin läuft `slack.py` lokal.
Quelle: Session vom 14.09.2026, Exportdateien nicht im Repo.

## [2026-09-14] kompiliert | Pipedrive-CSV-Export verliert Datensätze

Neuer Eintrag `wissen/pipedrive-export.md`: Nur die erste Spalte des Exports ist unmaskiert,
daraus folgen drei Fehler — kaputte Umlaute, an Zeilenumbrüchen zerrissene Firmennamen und
ein unmaskiertes Komma, das eine Spalte zu viel erzeugt. Mit Reparaturregeln und der
Gegenprobe. Merksatz: wenn möglich den XLSX-Export nehmen.
Quelle: Aufbereitung des Personenexports am 14.09.2026.

## [2026-09-14] eingesortiert | Slack `#kontakte` gegen die Kontakte-Lasche

Sechs Kontaktposts aus dem CG-TRADE-Kanal gelesen, fünf waren Dubletten zum
Pipedrive-Export. Alexandra Ochsenkiel (Deichmann SE) nach Zeile 226 der Lasche
„Kontakte" geschrieben. Vier Abweichungen zwischen Signatur und Lasche notiert, nicht
verändert. Cloud-Sessions erreichen slack.com jetzt — `40_Resources/slack-zugang.md`
entsprechend korrigiert.
Quelle: `30_Areas/firmen/cgt/notizen.md`.

## [2026-09-14] gebaut | Kontakte-Routine Slack → Lasche

Der Abgleich von heute Vormittag läuft jetzt stündlich als Routine. `slack.py` um `scopes`,
`holen` (JSON plus Bilddownload) und typrichtiges Auspacken der Slack-Links erweitert,
`files:read` liegt vor. Anleitung in `40_Resources/kontakte-routine.md`. Zwei Entscheidungen
festgehalten: Abgleich statt Merkzettel, stündlich statt Echtzeit.
Quelle: `30_Areas/firmen/cgt/notizen.md`.


## [2026-09-14] lint | Lasche „Kontakte" gegen die Absprache geprüft

Inhalt stimmt: 225 Kontakte, Ochsenkiel in Zeile 226, Autofilter gesetzt. Die Lasche trägt
aber die Pipedrive-Rohstruktur — vier durchgehend leere Spalten, nicht nach Firma sortiert,
ohne Firmen-Zähler, ohne Land, Kopfzeile nicht fixiert. Befund in
`30_Areas/firmen/cgt/notizen.md`, Entscheidung über eine Umstellung offen.
Quelle: Export der Tabelle über den Drive-Zugang, 14.09.2026.

## [2026-09-14] umgebaut | Lasche „Kontakte" auf die aufbereitete Struktur

17 Pipedrive-Rohspalten zu 15 gepflegten: vier durchgehend leere raus, Firmen-Zähler und
abgeleitetes Land rein, sortiert nach Firma. 225 Zeilen rein, 225 raus. Werkzeug
`40_Resources/tools/kontakte_umbau.py`, Länderlogik nach `laender.py` herausgezogen und mit
`pipedrive_kontakte.py` geteilt. Routine-Runbook auf die neuen Spalten umgestellt. Gelernt:
deutsche Locale braucht Semikolons in Formeln, wachsende Bereiche müssen offen sein.
Quelle: `30_Areas/firmen/cgt/notizen.md`.

## [2026-09-15] gebaut | Slack-Auslöser für die Kontakte-Routine

Dem API-Trigger nachgegangen: Routinen haben einen `/fire`-Endpunkt (401 statt 404 belegt,
dass er unsere Routine kennt). `40_Resources/tools/slack_ausloeser.gs` nimmt Slacks Event an
und startet die Routine; Filterlogik gegen vierzehn Ereignisformen geprüft. Nicht
bereitgestellt — Token und Event-Subscription gehen nur von Hand. Alibaba-Routine für
Saschas zwei Wochen Abwesenheit pausiert.
Quelle: `30_Areas/firmen/cgt/notizen.md`.


## [2026-10-04] gebaut | Themenbaum, To-do-App nach Skizze

To-do-Web-App nach Saschas Skizze (Themen → Unterthemen
mit Kästchen) als Mockup abgestimmt, dann als eigene App mit Zugangscode und privatem
Vercel-Blob-Speicher umgesetzt; lokal getestet (Login, Speichern, Konflikt, Druck nur offene).
Noch nicht deployt — Vercel-Team offen. Quelle: `20_Projects/themenbaum/uebersicht.md`.

## [2026-10-04] umgebaut | Themenbaum auf Hetzner statt Vercel

Auf Saschas Vorgabe Vercel verworfen: App läuft als eigener Node-Server ohne Abhängigkeiten,
Daten als JSON-Datei, Fehlversuchs-Sperre beim Login. Lokal getestet. Cloud-Session kommt
nicht an den Server (kein SSH, Host gesperrt) — Installation per Anleitung in lokaler Session.
Quelle: `20_Projects/themenbaum/ANLEITUNG-DEPLOY.md`.

## [2026-10-05] gebaut | Themenbaum: Import für Themen und Unterthemen

Mit Sascha 11 Themen und 40 Unterthemen in `app/seed.json` gesammelt. `app/import.mjs`
ergänzt sie in den laufenden Bestand auf dem Server (nur hinzufügen, Abgleich über den Namen,
Häkchen bleiben). Lokal getestet: leerer Bestand, Teilbestand mit Erledigtem, Doppellauf.
Ausführung in lokaler Session nach `20_Projects/themenbaum/ANLEITUNG-IMPORT.md`.

## [2026-10-08] ingest | Vier Kontakte nachgetragen, Routine repariert

Die Routine lief seit dem 16.09. ins Leere: Ihrer Session fehlte das Repository, sie fand
weder Runbook noch Werkzeuge. Auftrag um einen Schritt 0 ergänzt, der das Repo holt. Vier
liegengebliebene Kontakte (Lambers/Getränke Hoffmann, Grunwald/EDEKA, Tifo Agency,
Fleury/MBS) in die Zeilen 227–230 geschrieben. Dabei zwei eigene Fehler behoben: `gsheets.py`
wiederholte schreibende Aufrufe und erzeugte sie vierfach, und die Zählformel stand mit Komma
statt Semikolon. Beides korrigiert, Duplikate aus 323–338 entfernt.
Quelle: Slack `#kontakte`, Tabelle CGT – Themenplanung, 08.10.2026.

## [2026-10-08] lint | Routine-Reparatur greift nicht, Neuanlage nötig

Testlauf nach der Prompt-Reparatur war nach 16 Sekunden ohne Ergebnis vorbei. Repositories
werden beim Sessionstart festgelegt; eine per MCP angelegte Routine hat keine Quelle, und
`add_repo` im Lauf reicht nicht. Die Routine muss über die Oberfläche mit ausgewähltem
Repository neu angelegt werden — Auftrag dafür steht in `40_Resources/kontakte-routine.md`.
Quelle: Testlauf `cse_017yAuzoab5Gn6cXWknLMmRT`, 08.10.2026.

## [2026-10-08] setup | Kontakte-Routine als Dauerläufer neu aufgesetzt

Session mit Repo-Quelle angelegt (`session_019d2GY4sPzwVj4J6SuX6R8M`) und die Routine
`trig_01Le1ggnBvKCwK7SYSfTBZyZ` daran gebunden, täglich 9:35. Damit hat jeder Lauf den
Checkout dabei. Alte Routine ohne Quelle deaktiviert. Preis der Lösung: Der Kontext der
Session wächst mit jedem Lauf — Bruchstelle und Gegenmittel in
`30_Areas/firmen/cgt/notizen.md`.
Quelle: Gespräch vom 08.10.2026 (nicht im Repo).

## [2026-10-09] ingest | Ein Kontakt aus #kontakte: Burmeister/Lagardère

Erster regulärer Lauf des Dauerläufers. Zehn Slack-Nachrichten gegen die Lasche abgeglichen,
einer war neu: Marco Burmeister, Lagardère Travel Retail Deutschland GmbH, Zeile 231. Fünf
Dubletten (Ochsenkiel, van Dijk, Lambers, Grunwald, Fleury), Tifo Agency stand schon drin.
Telefonnummer unter allgemeinem Telefon-Symbol in Spalte Telefon statt Mobil — vermerkt in
`30_Areas/firmen/cgt/notizen.md`.
Quelle: Slack `#kontakte`, Tabelle CGT – Themenplanung, 09.10.2026.

## [2026-10-10] ingest | Ein Kontakt aus #kontakte: Köller/REWE

Elf Slack-Nachrichten abgeglichen, eine war neu: Annika Köller, REWE Group Buying GmbH,
Zeile 232. Sechs Dubletten. Dabei ein Werkzeugfehler aufgefallen: `gsheets.py update` bricht
seit heute mit `KeyError: 'updated'` ab, obwohl der Schreibvorgang ankommt — die
Apps-Script-Brücke antwortet ohne diesen Schlüssel. Nicht repariert, Begründung und Risiko in
`30_Areas/firmen/cgt/notizen.md`.
Quelle: Slack `#kontakte`, Tabelle CGT – Themenplanung, 10.10.2026.

## [2026-10-16] ingest | Ein Kontakt aus #kontakte: Fischer/SAGAFLOR

Zwölf Slack-Nachrichten abgeglichen, eine war neu: Lea Caterina Fischer, SAGAFLOR AG - ZOO &
Co., Zeile 233. Acht Dubletten. Zwei unbeschriftete Rufnummern nach Reihenfolge und Vorwahl
auf Telefon und Mobil verteilt, vermerkt in `30_Areas/firmen/cgt/notizen.md`. Der
`KeyError`-Abbruch vom 10.10. trat nicht wieder auf.
Quelle: Slack `#kontakte`, Tabelle CGT – Themenplanung, 16.10.2026.

## [2026-10-17] ingest | Ein Kontakt aus #kontakte: Marschhausen/FITX

Dreizehn Slack-Nachrichten abgeglichen, eine war neu: Dennis Marschhausen, FITX SE, Zeile 234.
Neun Dubletten. Signatur stand in Versalien, auf normale Schreibweise gebracht; unbeschriftete
Mobilnummer nach Regel H in Spalte Telefon. Beides vermerkt in
`30_Areas/firmen/cgt/notizen.md`.
Quelle: Slack `#kontakte`, Tabelle CGT – Themenplanung, 17.10.2026.

## [2026-10-21] kompilieren | Reisekosten: Vorlage, Sätze 2026 und London-Abrechnung

Reisekostenabrechnung für die Coldewey Holding gebaut (London, 07.–08.10.2026). Dabei die
Sätze für 2026 nachgeschlagen und als `wissen/reisekosten.md` abgelegt: Inland 28/14 €,
London 66/44 €, Kilometersatz Dienstreise 0,30 € — nicht zu verwechseln mit der
Entfernungspauschale, die ab 2026 einheitlich 0,38 € beträgt und nur für den Arbeitsweg gilt.
Rechnende Vorlage unter `templates/reisekostenabrechnung-vorlage.xlsx`, Sätze an einer Stelle
änderbar.

Die Belege im Kontoauszug widersprechen dem genannten Reisedatum (06./07.10.): Abflug Frankfurt
und Rückflug Heathrow sprechen für 07./08.10. Abrechnung steht auf 07.–08.10., Rückfrage offen.
Kilometer nachgereicht (35 einfach, 70 hin und zurück = 21,00 €). Offen bleiben Flugpreis
und Hotelbetrag, beide als vorbereitete Zeile in der Datei. Die Londoner Pauschalen stammen
aus Sekundärquellen und sind noch nicht gegen die amtliche BMF-Tabelle geprüft.
Quelle: Kontoauszug Hauptkonto Juni–Oktober 2026, hochgeladen am 21.10.2026.

## [2026-10-21] korrektur | Reisedatum London: Sascha hatte recht

Ich hatte das Reisedatum aufgrund der Kartenumsätze auf 07.–08.10. korrigiert. Die
Flugbuchung (LH 919, LHR–FRA am 07.10., 19:30) und die eDreams-Rechnung
2026-B2B7-000199110 zeigen: richtig ist 06.–07.10., wie ursprünglich angegeben.
Ursache des Fehlschlusses: Kartenumsätze werden verzögert eingereicht, auch das Value
Date ist nicht das Kaufdatum. Korrigiert in `wissen/reisekosten.md`, Regel in
`wissen/feedback.md`.

Flug Rückreise 89,98 €: Rechnung läuft auf die Coldewey Holding GmbH, Zahlung fehlt im
privaten Konto — also von der Firma direkt gezahlt und in der Abrechnung unten wieder
abgezogen. Reisekosten gesamt 357,96 €, Erstattung an Sascha 267,98 €. Offen bleiben der
Hinflug Frankfurt–London und der Hotelbetrag.
Quelle: Opodo-Buchung 25549946153 und Rechnung 2026-B2B7-000199110, hochgeladen 21.10.2026.

## [2026-10-21] kompilieren | London-Reise: zwei Abrechnungen statt einer

Die Reise lief für CGT, nicht für die Coldewey Holding. Beide Flüge (BA Frankfurt–London
111,97 € und LH 919 zurück 89,98 €) hat die Holding gezahlt, alles Übrige Sascha privat.
Daraus zwei Papiere: Weiterbelastung Holding → CGT über 201,95 € und Reisekostenabrechnung
Sascha → CGT über 267,98 € zuzüglich Hotel.

Das Muster „eine Firma zahlt vor, eine andere trägt die Reise" in `wissen/reisekosten.md`
festgehalten, mit den zwei offenen Steuerfragen: Umsatzsteuer auf die Weiterbelastung und
ob CGT die Verpflegungspauschale überhaupt steuerfrei erstatten darf, da der Lohn von der
Holding kommt.
Quelle: Opodo-Buchungen 25549979827 und 25549946153, Rechnung 2026-B2B7-000199110.

## [2026-10-21] ingest | CGT: Anschrift und Reisezweck nachgetragen

CGT UG, Biebricher Allee 36, 65187 Wiesbaden — im Steckbrief ergänzt, Rechtsform und Sitz
waren dort offen. Handelsregisternummer weiterhin _(offen)_. Beide London-Abrechnungen
tragen jetzt die Anschrift und als Reisezweck den Messebesuch; der Name der Messe fehlt
noch und ist in beiden Dateien als offener Punkt vermerkt.
Quelle: Angabe Sascha, 21.10.2026.

## [2026-10-21] korrektur | Sascha ist bei CGT kein Angestellter

Ich hatte die Abrechnung als Reisekostenerstattung an einen Arbeitnehmer angelegt und gefragt,
ob CGT die Verpflegungspauschale steuerfrei zahlen darf. Falsche Annahme: Sascha bezieht von
CGT keinen Lohn, sondern stellt Rechnungen. Damit sind es weiterberechnete Spesen, die als
Teil des Entgelts mit 19 % in seine Rechnung gehören. Datei zur Spesenaufstellung als Anlage
zur Rechnung umgebaut, 267,98 € netto. Hotel liegt bei der Firma und ist draußen.
Regel in `wissen/reisekosten.md` ergänzt.
Quelle: Angabe Sascha, 21.10.2026.

## [2026-10-21] output | Rechnung Fahrrad, Sascha privat an die Holding

Rechnung über das Rose Backroad APEX AXS XPLR 1x12 erstellt, Werte aus der Rose-Rechnung
205006771 vom 06.05.2026: 2.057,94 € netto, 391,01 € USt, 2.448,95 € brutto. Bankdaten und
Steuernummer 26 026 70812 (Finanzamt Mainz-Süd) eingetragen, Rechnungsnummer und
Leistungsdatum bleiben offen.

Drei Punkte stehen als Warnung in der Datei: die angegebene USt-IdNr. DE278832927 ist
ausweislich der Flugrechnung die der Holding und nicht Saschas eigene; der Verkauf an die
eigene GmbH muss dem Fremdvergleich standhalten, ein fünf Monate altes Rad zum Neupreis
riskiert eine verdeckte Gewinnausschüttung; und ausgewiesene Umsatzsteuer verträgt sich
nicht mit einem Verkauf aus dem Privatvermögen.

Nebenbei die USt-IdNr. der Holding im Steckbrief nachgetragen.
Quelle: Rose-Rechnung 205006771 und Angaben Sascha, 21.10.2026.

## [2026-10-26] output | Fahrradrechnung abgeschlossen

Rechnungsnummer 2026-001, Rechnungs- und Leistungsdatum 26.10.2026 eingetragen, USt-IdNr.
auf Wunsch entfernt — die Steuernummer allein genügt nach § 14 UStG. Damit ist die Rechnung
vollständig: 2.057,94 € netto, 391,01 € USt, 2.448,95 € brutto. Datei auf das Rechnungsdatum
umbenannt. Offen bleibt allein der Fremdvergleich beim Verkauf an die eigene GmbH.
Quelle: Angaben Sascha, 26.10.2026.

## [2026-10-26] output | Nebenkostenabrechnung Ingelheim 2024 geprüft, 2025 erstellt

Neues Projekt `20_Projects/wohnung-ingelheim/`. Für 2024 die Abrechnung der Hausverwaltung
geprüft: Kabelfernsehen war für das ganze Jahr umgelegt, obwohl es seit dem 01.07.2024 nicht
mehr umlagefähig ist — rund 46,98 € zugunsten des Mieters. Für 2025 die Mieterabrechnung aus
der WEG-Einzelabrechnung gebaut: 2.005,51 € umlagefähig (1.992,51 € laut Verwaltung plus
13,00 € Grundsteuer), Guthaben 1.594,49 € bei angenommenen 3.600 € Vorauszahlung.

Aus dem Protokoll der 17. Eigentümerversammlung mitgenommen: die Verwaltung wartet auf
Saschas Bankverbindung für 1.090,50 € Guthaben, die Mieterin wendet sich mit Anliegen direkt
an die Verwaltung statt an den Vermieter, und ab 2026 kommt die Fensterreinigung als neue
Position dazu.
Quelle: Unterlagen der HCo Hausverwaltung, hochgeladen am 26.10.2026.

## [2026-10-26] ingest | Beide Mietwohnungen dokumentiert, Nießbrauch in Alzey gefunden

Unterlagen zu beiden Wohnungen eingearbeitet: Grundbuchauszüge, Mietverträge,
Grundsteuerbescheide, Vermieterbriefe. Neues Projekt `20_Projects/wohnung-alzey/`,
Ingelheim um Grundbuch- und Vertragsdaten ergänzt.

Zentraler Fund: Im Grundbuch Alzey 4850 steht in Abteilung II ein **Nießbrauch für Elimar
Coldewey, geb. 28.04.1942**. Solange der besteht, ist der Nießbraucher der Vermieter und
ihm stehen die Mieten zu — Saschas Mieterhöhungsverlangen und Zahlungserinnerung vom
13.03.2026 kommen damit vom Falschen. In Ingelheim ist dagegen kein Nießbrauch eingetragen;
dort nennt nur der Mietvertrag von 2018 den Vater als Vermieter, was ein Nachtrag heilt.

Nebenbei geklärt: Der Ingelheimer Mietvertrag listet „Sonstige Betriebskosten"
ausdrücklich auf, damit sind Rauchwarnmelder und Fensterreinigung umlagefähig.
Quelle: Unterlagen Sascha, hochgeladen am 26.10.2026.

## [2026-10-26] korrektur | Nießbrauch Alzey ist abgelöst

Nachtrag zum Eintrag von heute: Der Nießbrauch des Vaters ist erledigt. Elimar Coldewey ist
2025 verstorben, der Nießbrauch wurde abgelöst, der Notarvertrag liegt Sascha vor. Der
Grundbuchauszug vom 12.08.2025 bildete noch den alten Stand ab. Sascha ist damit Eigentümer
und Vermieter, seine Schreiben an die Mieter sind wirksam. Offen bleibt allein, ob die
Löschung im Grundbuch beantragt ist — die läuft nicht von selbst.
Quelle: Angabe Sascha, 26.10.2026.

## [2026-10-26] korrektur | Alzey: aktueller Mieter ist Mazineler, nicht Anlar

Die beiden Vermieterbriefe vom 13.03.2026 sind an Bükent Anlar adressiert, den Vormieter
bis 2021. Aktueller Mieter ist Abdurrahim Mazineler, seit 01.05.2021, mit 600 € statt 550 €
im Monat. Mieterhöhungsverlangen und Zahlungserinnerung müssen neu ausgestellt werden.
Quelle: Angabe Sascha, 26.10.2026.

## [2026-10-26] output | Mieterhöhungsverlangen Alzey neu aufgesetzt

Brief an Abdurrahim Mazineler, 360 € auf 400 € Kaltmiete, mit korrektem Mietbeginn
01.05.2021. Begründung über drei Vergleichswohnungen statt über einen Mietspiegel: Für
Alzey ist kein qualifizierter Mietspiegel auffindbar, und die Zahlen der Immobilienportale
sind Angebotsmieten, die § 558a BGB nicht genügen. Die drei Wohnungen muss Sascha noch
eintragen, sonst ist das Verlangen unwirksam.
Quelle: eigene Recherche und Mietvertrag Mazineler, 26.10.2026.
