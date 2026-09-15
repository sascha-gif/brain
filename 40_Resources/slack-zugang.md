# Slack-Zugang

**Stand 14.09.2026:** eingerichtet und geprüft. `SLACK_CGT_TOKEN` liegt im Environment
(Bot-Token, `xoxb-…`), das Token ist gültig, und der Kanal `#kontakte` ließ sich **aus einer
Cloud-Session heraus** lesen. Die frühere Sperre ist weg, siehe „Netzzugang" unten.
Werkzeug: `40_Resources/tools/slack.py`. Was aus dem Kanal wird, steht in
[`kontakte-routine.md`](kontakte-routine.md) — seit dem 14.09.2026 läuft das stündlich.

## Warum eine eigene App

Der Claude-Slack-Connector hängt an **einem** Workspace. Verbunden ist der mit `#cubcoats`,
`#bcd_intern`, `#digital-roots`. Ein zweiter lässt sich nicht dazuschalten. Der Workspace
**CG TRADE** ist deshalb über den Connector nicht erreichbar — Kanal `C0A7M1Y1JTC` antwortet
mit `channel_not_found`.

Ersatz ist eine eigene Slack-App in CG TRADE mit Bot-Token. Sie sieht nur die Kanäle, in die
sie eingeladen wurde.

## Einrichten

1. [api.slack.com/apps](https://api.slack.com/apps) → **Create New App** → **From scratch**,
   Workspace **CG TRADE**.
2. **OAuth & Permissions** → *Bot Token Scopes*: `channels:history`, `channels:read`,
   `users:read`, `files:read` (letzteres für Visitenkarten-Bilder). Bei privaten Kanälen
   zusätzlich `groups:history`, `groups:read`. Was das Token tatsächlich hat, zeigt
   `slack.py scopes`.
3. **Install to Workspace**. Danach steht dort das **Bot User OAuth Token** (`xoxb-…`).
   Scopes später nachtragen heißt: App neu installieren, sonst greifen sie nicht.
4. In Slack im Zielkanal `/invite @NameDerApp` — ohne das sieht der Bot nichts
   (`not_in_channel`).
5. Token als Umgebungsvariable hinterlegen, nie ins Repo:

       SLACK_CGT_TOKEN=xoxb-...

   Weg zum Environment: siehe `google-sheets-zugang.md`. Variablen werden nur beim
   Sessionstart gelesen — danach eine neue Session starten.

Falls die App-Installation im Workspace auf Admins beschränkt ist, muss Thomas sie
freigeben; statt „Install" erscheint dann eine Anfrage-Maske.

## Netzzugang aus Cloud-Sessions

Anfangs war `slack.com` aus claude.ai/code nicht erreichbar: Der Aufruf endete mit
`Tunnel connection failed: 403 Forbidden`, weil das Environment auf Netzwerkzugriff
**Trusted** stand — eine feste Liste (Paketregister, GitHub, Cloud-SDKs) ohne Slack.

Seit dem 14.09.2026 steht das Environment auf **Custom** mit `slack.com` in der Liste;
`slack.py` läuft damit auch aus einer Cloud-Session. Falls die Sperre wiederkommt
(403 auf `slack.com:443`), so war sie eingestellt:

1. Auf [claude.ai/code](https://claude.ai/code) das **Wolken-Symbol** über dem Eingabefeld
   anklicken, im Menü über das Environment fahren, rechts das **Zahnrad**.
2. **Network access** von *Trusted* auf **Custom** stellen.
3. Im Feld **Allowed domains** je Zeile eine Domain:

       slack.com
       *.slack.com

4. **Also include default list of common package managers** ankreuzen. Ohne das Häkchen
   gelten *nur* die beiden Zeilen oben, und npm, pip und Konsorten fallen aus.
5. Speichern und eine **neue Session** starten — eine laufende behält ihre alte Richtlinie.

Der Claude-Slack-Connector bleibt trotzdem kein Ersatz: Er hängt am Workspace
`srpgruppe.slack.com` und antwortet für `C0A7M1Y1JTC` weiterhin mit `channel_not_found`.
GitHub ist von der Domainliste unberührt — der Git-Verkehr läuft über einen eigenen Proxy.

Quelle: [Configure cloud environments → Access levels](https://code.claude.com/docs/en/cloud-environments#access-levels).

## Benutzen

    python3 40_Resources/tools/slack.py scopes
    python3 40_Resources/tools/slack.py channels
    python3 40_Resources/tools/slack.py read --since 2026-09-01
    python3 40_Resources/tools/slack.py read --channel C0A7M1Y1JTC --limit 50 --json
    python3 40_Resources/tools/slack.py holen --ziel /tmp/kontakte

`scopes` sagt, was das Token darf — der erste Griff, wenn etwas mit `missing_scope` abbricht.
`channels` zeigt, in welchen Kanälen der Bot drin ist. `read` gibt Nachrichten älteste zuerst
aus, mit Zeit, Absender und Anhängen. `holen` ist die Maschinenfassung für die Routine: es
schreibt `nachrichten.json` und lädt Bildanhänge in einen Unterordner `bilder/`.

Slack verpackt jede Nummer und Adresse als Link `<tel:URL|Anzeige>`. `read --json` und `holen`
packen das aus — bei `tel:` gewinnt die Anzeige (die URL ist zu Ziffernbrei normalisiert), bei
`http:` die URL (die Anzeige ist oft gekürzt). Widersprechen sich bei einer Adresse Anzeige und
Link, steht beides da: `jacksam@haddad.com (Link: jacksh@haddad.com)`.

## Bekannte Kanäle

| Kanal | ID | Workspace | Inhalt |
|---|---|---|---|
| `#kontakte` | `C0A7M1Y1JTC` | CG TRADE | Kontaktdaten als Text, von Thomas und Sascha gepostet |

`#kontakte` hieß bis zum 14.09.2026 `#pipdrive`; die ID ist dieselbe geblieben.

Der Bot ist **nur** in `#kontakte`. Die übrigen Kanäle in CG TRADE sieht er zwar in der
Liste, lesen kann er sie nicht (`not_in_channel`) — dafür bräuchte es je ein
`/invite @Brain Reader`: `#fandom`, `#ktn`, `#herzbach`, `#deltex`, `#deals`, `#to_do`,
`#fressnapf`, `#miloy`, `#pets`, `#epsilon`, `#tracker`, `#pmt`, `#hard-rock`.

## Echtzeit statt Takt: der API-Trigger

Die Routine fragt Slack in festem Takt ab und laeuft dabei meistens leer. Umgekehrt geht auch:
Routinen haben einen **API-Trigger** — einen eigenen Endpunkt, den ein HTTP-POST startet.

    POST https://api.anthropic.com/v1/claude_code/routines/<trig_...>/fire
    Authorization: Bearer sk-ant-oat01-…
    anthropic-beta: experimental-cc-routine-2026-04-01
    anthropic-version: 2023-06-01

Slack kann diesen Aufruf nicht selbst machen — seine Events-API schickt zwar bei jeder
Nachricht einen POST, aber ohne Bearer-Token. Dazwischen steht deshalb ein Apps Script:
[`tools/slack_ausloeser.gs`](tools/slack_ausloeser.gs), ein eigenes Projekt neben der
Sheets-Brücke. Es läuft dauerhaft bei Google, ein Server wird nicht gebraucht.

    Slack #kontakte  →  Apps Script  →  /fire  →  Session

**Stand 15.09.2026:** Das Skript ist geschrieben und seine Filterlogik gegen vierzehn
Slack-Ereignisformen geprüft (normaler Post, Visitenkarte, Bot-Nachricht, Beitritt,
Umbenennung, Thread-Antwort, fremder Kanal …). Bereitgestellt ist es **nicht** — dafür
braucht es zwei Dinge, die nur von Hand gehen.

### Die zwei Handgriffe, die nur Sascha machen kann

1. **Token erzeugen.** `claude.ai/code/routines` → Routine öffnen → Stift →
   **Add another trigger** → **API** → **Generate token**. Das Token wird **einmal**
   angezeigt. Über CLI oder MCP-Werkzeug geht das nicht, es gibt keine API dafür.
2. **Event Subscriptions einschalten.** `api.slack.com/apps` → die App →
   **Event Subscriptions** → einschalten, Request-URL eintragen, unter *Subscribe to bot
   events* `message.channels` hinzufügen, speichern, App neu installieren.

Dazwischen liegt das Bereitstellen des Skripts; der Ablauf steht vollständig im Kopf von
[`slack_ausloeser.gs`](tools/slack_ausloeser.gs).

### Was das bringt

Eine Session läuft nur noch bei einem echten Post statt einmal täglich ins Leere. Bei sechs
Kontakten im Quartal sind das zwei Läufe im Monat statt dreißig — und sie laufen binnen zwei
Minuten statt am nächsten Morgen.

**Der tägliche Lauf bleibt trotzdem stehen.** Er ist das Netz: Verschluckt Slack ein Event,
ist das Skript kurz tot oder das Token zurückgezogen, fängt er alles auf, weil die Routine
ohnehin gegen die Lasche abgleicht statt einen Merkzettel zu führen.

### Zwei Einschränkungen, die man kennen muss

**Keine Signaturprüfung möglich.** Apps Script reicht keine HTTP-Header an `doPost` weiter,
also lässt sich Slacks `X-Slack-Signature` nicht prüfen. Stattdessen steht ein Geheimnis im
Query-String der URL. Wer die URL samt Geheimnis kennt, kann die Routine auslösen — mehr
nicht: Der Auslöser nimmt keine Daten entgegen, er startet einen Lauf, den es ohnehin täglich
gibt. Landet die URL irgendwo, wo sie nicht hingehört: neues Geheimnis, neue Bereitstellung.

**Slack wartet nur 3 Sekunden** und wiederholt sonst die Zustellung. Das Skript feuert deshalb
nicht sofort, sondern hinterlässt eine Marke und antwortet gleich; ein Minutentakt feuert
90 Sekunden später. Das fängt die Wiederholungen ab und bündelt nebenbei mehrere Posts zu
einem Lauf — wer drei Kontakte hintereinander postet, löst einen Lauf aus, nicht drei.

## Was noch offen ist## Was noch offen ist

- Der Free-Plan von Slack schneidet die Kanalhistorie nach 90 Tagen ab. Am 14.09.2026 reichte
  sie bis zum 29.06.2026 zurück — zehn Nachrichten. Für laufend neue Kontakte egal, für
  Altbestand nicht.
- Bilder sind vorbereitet, aber ungetestet: `files:read` liegt seit dem 14.09.2026 vor und
  `slack.py holen` lädt Anhänge herunter — im Kanal lag bis dahin nur Text. Der erste Lauf
  mit einer echten Visitenkarte gehört angesehen.
- Takt entschieden: stündlich, siehe [`kontakte-routine.md`](kontakte-routine.md).
- Ziel noch nicht entschieden: Pipedrive (dort ist das CRM, braucht einen API-Token) oder
  die Lasche „Kontakte" in der Themenplanung. Am 14.09.2026 wurde der Slack-Abgleich in die
  Lasche geschrieben, weil es für Pipedrive keinen Zugang gibt — das ist ein Behelf, keine
  Entscheidung.
- Ohne Zugang zu Pipedrive laufen Slack und CRM auseinander: Fünf der sechs Kontakte im
  Kanal standen bereits im Personenexport. Ein Abgleich gegen die Lasche fängt Dubletten ab,
  aber nur, solange die Lasche aktuell ist.
