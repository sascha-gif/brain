# CGT — Notizen

Neueste oben.

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
