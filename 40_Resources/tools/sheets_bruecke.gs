/**
 * Schreibbruecke fuer Google Sheets — als Apps Script Web-App bereitstellen.
 *
 * Hintergrund: Dienstkontoschluessel sind in unserer Google-Organisation per
 * Richtlinie gesperrt (iam.disableServiceAccountKeyCreation). Diese Bruecke
 * laeuft stattdessen unter dem eigenen Google-Konto und braucht keinen Key.
 *
 * Einrichten:
 *   1. script.google.com -> Neues Projekt, Name z. B. "Brain Sheets-Bruecke"
 *   2. Diesen Code komplett einfuegen, SHEET_ID und SECRET setzen
 *   3. Bereitstellen -> Neue Bereitstellung -> Typ "Web-App"
 *        Ausfuehren als : Ich
 *        Zugriff        : Jeder
 *   4. Die /exec-URL und das SECRET als Umgebungsvariablen hinterlegen:
 *        CGT_SHEETS_URL, CGT_SHEETS_SECRET
 *
 * Das Skript kann nur, was das eigene Konto auch von Hand koennte, und nur
 * auf der einen Tabelle unten. Zurueckziehen: Bereitstellung archivieren.
 */

const SHEET_ID = 'HIER_DIE_SHEET_ID';   // aus der URL zwischen /d/ und /edit
const SECRET   = 'HIER_DAS_SECRET';     // lange Zufallskette, identisch zu CGT_SHEETS_SECRET

function doPost(e) {
  try {
    const req = JSON.parse(e.postData.contents);
    if (!SECRET || req.secret !== SECRET) {
      return antwort({ error: 'unauthorized' });
    }

    const ss = SpreadsheetApp.openById(SHEET_ID);

    if (req.action === 'tabs') {
      return antwort({ tabs: ss.getSheets().map(function (s) { return s.getName(); }) });
    }

    const blatt = ss.getSheetByName(req.tab);
    if (!blatt) {
      return antwort({ error: 'Lasche nicht gefunden: ' + req.tab });
    }

    switch (req.action) {
      case 'read': {
        const bereich = req.range ? blatt.getRange(req.range) : blatt.getDataRange();
        return antwort({ values: bereich.getValues(), range: bereich.getA1Notation() });
      }

      case 'append': {
        const zeilen = req.rows;
        if (!zeilen || !zeilen.length) return antwort({ error: 'keine Zeilen uebergeben' });
        const start = blatt.getLastRow() + 1;
        const breite = Math.max.apply(null, zeilen.map(function (z) { return z.length; }));
        const gefuellt = zeilen.map(function (z) {
          const kopie = z.slice();
          while (kopie.length < breite) kopie.push('');
          return kopie;
        });
        blatt.getRange(start, 1, gefuellt.length, breite).setValues(gefuellt);
        return antwort({ appended: gefuellt.length, from: start });
      }

      case 'update': {
        const zeilen = req.rows;
        if (!req.range || !zeilen || !zeilen.length) {
          return antwort({ error: 'range und rows noetig' });
        }
        blatt.getRange(req.range).setValues(zeilen);
        return antwort({ updated: req.range, rows: zeilen.length });
      }

      case 'clear': {
        if (!req.confirm) return antwort({ error: 'clear braucht confirm: true' });
        blatt.clear();
        return antwort({ cleared: req.tab });
      }

      default:
        return antwort({ error: 'unbekannte Aktion: ' + req.action });
    }
  } catch (err) {
    return antwort({ error: String(err) });
  }
}

function doGet() {
  return antwort({ status: 'Bruecke laeuft. Schreibzugriffe nur per POST.' });
}

function antwort(objekt) {
  return ContentService
    .createTextOutput(JSON.stringify(objekt))
    .setMimeType(ContentService.MimeType.JSON);
}
