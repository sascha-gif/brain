# Slack-Zugang

**Stand 14.09.2026:** Bot-Token liegt vor, noch nicht im Environment hinterlegt.
Werkzeug: `40_Resources/tools/slack.py`.

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
  die Lasche „Kontakte" in der Themenplanung.
