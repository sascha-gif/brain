/**
 * Slack-Ausloeser: ein Post in #kontakte startet die Kontakte-Routine.
 *
 * Bisher fragt die Routine Slack in festem Takt ab und laeuft meistens leer.
 * Hiermit laeuft sie nur noch, wenn wirklich jemand etwas postet.
 *
 * Der Weg: Slack schickt sein Event hierher, dieses Skript ruft den
 * /fire-Endpunkt der Routine auf. Ein eigener Server wird nicht gebraucht,
 * Apps Script laeuft dauerhaft bei Google.
 *
 *   Slack #kontakte  ->  diese Web-App  ->  api.anthropic.com/.../fire  ->  Session
 *
 * Eigenes Projekt, NICHT in die Sheets-Bruecke hineinschreiben. Die beiden
 * haben nichts miteinander zu tun und sollen sich nicht gegenseitig
 * abschiessen, wenn eine neu bereitgestellt wird.
 *
 * ---------------------------------------------------------------------------
 * EINRICHTEN
 *
 * 1. script.google.com -> Neues Projekt, Name z. B. "Brain Slack-Ausloeser".
 *    Diesen Code komplett einfuegen.
 *
 * 2. Projekteinstellungen (Zahnrad) -> Skripteigenschaften. Vier Stueck:
 *
 *      SCHLUESSEL      lange Zufallskette, z. B. aus `openssl rand -hex 24`
 *      FIRE_URL        https://api.anthropic.com/v1/claude_code/routines/<trig_...>/fire
 *      FIRE_TOKEN      sk-ant-oat01-…  (einmalig sichtbar, sofort kopieren)
 *      KANAL           C0A7M1Y1JTC
 *
 *    FIRE_URL und FIRE_TOKEN stammen aus claude.ai/code/routines: Routine
 *    oeffnen -> Stift -> "Add another trigger" -> API -> "Generate token".
 *
 * 3. Im Editor einmal `einrichten` ausfuehren. Das legt den Minutentakt an,
 *    der das Abfeuern uebernimmt, und prueft die Eigenschaften.
 *
 * 4. Bereitstellen -> Neue Bereitstellung -> Typ "Web-App"
 *      Ausfuehren als : Ich
 *      Zugriff        : Jeder
 *    Die /exec-URL kopieren und SCHLUESSEL anhaengen:
 *      https://script.google.com/macros/s/…/exec?k=<SCHLUESSEL>
 *
 * 5. api.slack.com/apps -> die App -> Event Subscriptions -> einschalten,
 *    die URL aus Schritt 4 als Request URL eintragen (Slack prueft sie sofort
 *    mit einer Challenge, das beantwortet dieses Skript), dann unter
 *    "Subscribe to bot events" `message.channels` hinzufuegen und speichern.
 *    Danach die App neu installieren.
 *
 * Gegenprobe: im Kanal etwas posten. Unter "Ausfuehrungen" im Apps Script
 * stehen dann ein `doPost` und kurz darauf ein `abfeuern`. Die neue Session
 * taucht in claude.ai/code auf.
 *
 * ---------------------------------------------------------------------------
 * ZWEI EINSCHRAENKUNGEN, DIE MAN KENNEN MUSS
 *
 * Apps Script reicht **keine HTTP-Header** an `doPost` weiter. Slacks
 * Signaturpruefung (X-Slack-Signature) ist damit unmoeglich — deshalb der
 * SCHLUESSEL in der URL. Wer die URL samt Schluessel kennt, kann die Routine
 * ausloesen. Mehr nicht: Der Ausloeser nimmt keine Daten entgegen, er startet
 * nur einen Lauf, der ohnehin taeglich stattfindet. Wird die URL verstreut,
 * reicht ein neuer SCHLUESSEL plus neue Bereitstellung.
 *
 * Slack erwartet **innerhalb von 3 Sekunden** eine Antwort, sonst wiederholt es
 * die Zustellung. Deshalb feuert `doPost` nicht selbst, sondern hinterlaesst nur
 * eine Marke und antwortet sofort. Das Abfeuern macht `abfeuern` im Minutentakt.
 * Das hat einen zweiten Nutzen: Wer drei Kontakte hintereinander postet, loest
 * damit **einen** Lauf aus statt drei — jeder Lauf kostet, und die Session liest
 * ohnehin den ganzen Kanal.
 */

const EIGENSCHAFTEN = PropertiesService.getScriptProperties();

// Wie lange nach dem letzten Post gewartet wird, bevor gefeuert wird. Faengt
// Slack-Wiederholungen ab und buendelt mehrere Posts zu einem Lauf.
const RUHE_SEKUNDEN = 90;

// Der einzige Subtyp, der ein echter Kontaktpost sein kann: eine Nachricht mit
// Anhang, also die Visitenkarte. Alles andere ist Kanal-Geraeusch — Beitritte,
// Umbenennungen, Pins, nachtraegliche Edits. Eine Nachricht ohne Subtyp ist der
// Normalfall und kommt weiter unten durch.
const ERLAUBTE_SUBTYPEN = ['file_share'];


/** Slack liefert hier ab. Nur markieren, nicht feuern — siehe Kopf. */
function doPost(e) {
  try {
    const roh = e && e.postData ? e.postData.contents : '';
    const req = JSON.parse(roh || '{}');

    // Slack prueft die URL einmalig mit einer Challenge. Die kommt, bevor
    // irgendetwas anderes funktioniert, und wird ohne Schluessel beantwortet —
    // sie enthaelt nichts Schuetzenswertes.
    if (req.type === 'url_verification') {
      return ContentService.createTextOutput(req.challenge || '');
    }

    if (e.parameter.k !== EIGENSCHAFTEN.getProperty('SCHLUESSEL')) {
      return text('nein');
    }

    if (req.type !== 'event_callback' || !req.event) {
      return text('ok');
    }

    const ereignis = req.event;
    if (!istKontaktpost(ereignis)) {
      return text('ok');
    }

    // Marke setzen: "seit <jetzt> liegt etwas an". Jeder weitere Post schiebt
    // den Zeitpunkt nach hinten, bis RUHE_SEKUNDEN lang Ruhe ist.
    EIGENSCHAFTEN.setProperty('ANLIEGEND_SEIT', String(Date.now()));
    return text('ok');

  } catch (err) {
    // Slack darf nie einen Fehler sehen, sonst wiederholt es die Zustellung
    // endlos. Der Fehler steht im Ausfuehrungsprotokoll.
    console.error('doPost: ' + err);
    return text('ok');
  }
}


/** Laeuft jede Minute. Feuert, wenn lange genug Ruhe ist. */
function abfeuern() {
  const seit = Number(EIGENSCHAFTEN.getProperty('ANLIEGEND_SEIT') || 0);
  if (!seit) return;

  const gewartet = (Date.now() - seit) / 1000;
  if (gewartet < RUHE_SEKUNDEN) return;     // noch tröpfeln Posts nach

  // Marke zuerst loeschen. Faellt der Aufruf unten aus, ist ein Lauf verloren —
  // das faengt der taegliche Lauf auf. Andersherum (erst feuern, dann loeschen)
  // wuerde ein Fehler beim Loeschen jede Minute erneut feuern, und das kostet.
  EIGENSCHAFTEN.deleteProperty('ANLIEGEND_SEIT');

  const url = EIGENSCHAFTEN.getProperty('FIRE_URL');
  const token = EIGENSCHAFTEN.getProperty('FIRE_TOKEN');
  if (!url || !token) {
    console.error('FIRE_URL oder FIRE_TOKEN fehlt in den Skripteigenschaften.');
    return;
  }

  const antwort = UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    muteHttpExceptions: true,
    headers: {
      'Authorization': 'Bearer ' + token,
      'anthropic-version': '2023-06-01',
      'anthropic-beta': 'experimental-cc-routine-2026-04-01'
    },
    payload: JSON.stringify({
      text: 'Ausgeloest durch einen neuen Post im Slack-Kanal #kontakte. '
          + 'Welcher, steht nicht in dieser Nachricht — lies den Kanal, '
          + 'wie im Runbook beschrieben.'
    })
  });

  const code = antwort.getResponseCode();
  const rumpf = antwort.getContentText();

  if (code === 200) {
    console.log('Routine gestartet: ' + rumpf);
    return;
  }

  // 401 Token zurueckgezogen | 400 Routine pausiert | 429 Kontingent erschoepft
  console.error('Fire fehlgeschlagen, HTTP ' + code + ': ' + rumpf);

  // Bei Ueberlast oder Serverfehler die Marke zurueckholen, dann versucht es
  // die naechste Minute erneut. Bei 400/401/403/404/429 waere das sinnlos:
  // die beheben sich nicht von selbst, und jeder Versuch laeuft ins Leere.
  if (code === 500 || code === 503) {
    EIGENSCHAFTEN.setProperty('ANLIEGEND_SEIT', String(Date.now() - RUHE_SEKUNDEN * 1000));
  }
}


/** Ist das ein Post, der einen Kontakt tragen koennte? */
function istKontaktpost(ereignis) {
  if (ereignis.type !== 'message') return false;
  if (ereignis.channel !== EIGENSCHAFTEN.getProperty('KANAL')) return false;
  if (ereignis.bot_id) return false;                  // auch der eigene Bot
  if (ereignis.subtype && ERLAUBTE_SUBTYPEN.indexOf(ereignis.subtype) < 0) return false;
  if (ereignis.thread_ts && ereignis.thread_ts !== ereignis.ts) return false;  // Thread-Antwort
  return true;
}


/** Einmal im Editor ausfuehren: Minutentakt anlegen und Konfiguration pruefen. */
function einrichten() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'abfeuern') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('abfeuern').timeBased().everyMinutes(1).create();

  const fehlt = ['SCHLUESSEL', 'FIRE_URL', 'FIRE_TOKEN', 'KANAL']
    .filter(function (n) { return !EIGENSCHAFTEN.getProperty(n); });

  if (fehlt.length) {
    throw new Error('Minutentakt steht, aber diese Skripteigenschaften fehlen: '
                    + fehlt.join(', '));
  }
  console.log('Minutentakt steht, alle vier Eigenschaften sind gesetzt.');
}


/** Zum Testen von Hand: feuert sofort, ohne auf Slack zu warten. */
function jetztFeuern() {
  EIGENSCHAFTEN.setProperty('ANLIEGEND_SEIT', String(Date.now() - RUHE_SEKUNDEN * 1000));
  abfeuern();
}


/** Aufraeumen: Minutentakt entfernen. Die Bereitstellung bleibt bestehen. */
function abschalten() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    if (t.getHandlerFunction() === 'abfeuern') ScriptApp.deleteTrigger(t);
  });
  EIGENSCHAFTEN.deleteProperty('ANLIEGEND_SEIT');
  console.log('Minutentakt entfernt. Slack-Events laufen jetzt ins Leere.');
}


function doGet() {
  return text('Slack-Ausloeser laeuft. Events nur per POST.');
}

function text(s) {
  return ContentService.createTextOutput(s);
}
