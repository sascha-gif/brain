# CGT — Notizen

Neueste oben.

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
