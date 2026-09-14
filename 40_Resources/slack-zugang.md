# Slack-Zugang

**Stand 14.09.2026:** `SLACK_CGT_TOKEN` liegt im Environment (Bot-Token, `xoxb-…`).
**Aus Cloud-Sessions trotzdem nicht nutzbar** — siehe „Grenze" unten; ob das Token gültig
ist, konnte dort deshalb nicht geprüft werden. Werkzeug: `40_Resources/tools/slack.py`.

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
   `users:read`. Bei privaten Kanälen zusätzlich `groups:history`, `groups:read`.
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

## Grenze: Cloud-Sessions erreichen slack.com nicht

Der Egress-Proxy von claude.ai/code lässt nur Hosts durch, die die Organisationsrichtlinie
erlaubt. `slack.com` ist nicht darunter: Der Aufruf endet mit
`Tunnel connection failed: 403 Forbidden`, der Proxy protokolliert
`connect_rejected … gateway answered 403 to CONNECT` für `slack.com:443`. Das ist eine
Richtlinienentscheidung, kein Fehler im Werkzeug und nichts, was sich umgehen ließe.

Damit gilt: **`slack.py` läuft lokal über die CLI**, nicht in einer Cloud-Session. Der
Claude-Slack-Connector ist auch kein Ersatz — er hängt an einem anderen Workspace und
antwortet für `C0A7M1Y1JTC` weiterhin mit `channel_not_found` (am 14.09.2026 gegengeprüft).

### Beheben: Netzwerkzugriff des Environments auf „Custom" stellen

Das Environment steht auf Netzwerkzugriff **Trusted** — eine feste Liste (Paketregister,
GitHub, Cloud-SDKs), in der Slack nicht vorkommt. Ergänzen kann man diese Liste nicht; man
wechselt auf **Custom** und gibt eine eigene Liste an:

1. Auf [claude.ai/code](https://claude.ai/code) das **Wolken-Symbol** über dem Eingabefeld
   anklicken, im Menü über das Environment fahren, rechts das **Zahnrad**.
2. **Network access** von *Trusted* auf **Custom** stellen.
3. Im Feld **Allowed domains** je Zeile eine Domain:

       slack.com
       *.slack.com

4. **Also include default list of common package managers** ankreuzen. Ohne das Häkchen
   gelten *nur* die beiden Zeilen oben, und npm, pip und Konsorten fallen aus.
5. Speichern und eine **neue Session** starten — eine laufende behält ihre alte Richtlinie.

Danach erreicht `slack.py` den Workspace auch aus der Cloud, und eine Routine kann
unbeaufsichtigt laufen. GitHub bleibt davon unberührt: der Git-Verkehr läuft über einen
eigenen Proxy, nicht über diese Liste.

Quelle: [Configure cloud environments → Access levels](https://code.claude.com/docs/en/cloud-environments#access-levels).

## Benutzen

    python3 40_Resources/tools/slack.py channels
    python3 40_Resources/tools/slack.py read --since 2026-09-01
    python3 40_Resources/tools/slack.py read --channel C0A7M1Y1JTC --limit 50

`channels` zeigt auch, in welchen Kanälen der Bot drin ist — der erste Test nach der
Einrichtung. `read` gibt Nachrichten älteste zuerst aus, mit Zeit, Absender und Anhängen.

## Bekannte Kanäle

| Kanal | ID | Workspace | Inhalt |
|---|---|---|---|
| `#kontakte` | `C0A7M1Y1JTC` | CG TRADE | Kontaktdaten als Text, von Thomas und Sascha gepostet |

Weitere Kanäle in CG TRADE: `#deltex`, `#hard-rock`, `#pets`.

## Was noch offen ist

- Der Free-Plan von Slack schneidet die Kanalhistorie nach 90 Tagen ab. Für laufend neue
  Kontakte egal, für Altbestand nicht.
- Kontakte kommen als Text, nicht als Foto — Visitenkarten-Bilder muss niemand auslesen.
  Sollte das später doch vorkommen, braucht die App zusätzlich `files:read`.
- Takt noch nicht entschieden: Routine einmal täglich oder auf Zuruf.
- Ziel noch nicht entschieden: Pipedrive (dort ist das CRM, braucht einen API-Token) oder
  die Lasche „Kontakte" in der Themenplanung. In der Lasche liegt seit dem 14.09.2026 der
  Pipedrive-Personenexport — das war eine einmalige Befüllung auf Zuruf und legt die
  Richtung für den laufenden Betrieb noch nicht fest.
- Erst recht offen, solange der Kanal aus Cloud-Sessions nicht lesbar ist (siehe „Grenze").
