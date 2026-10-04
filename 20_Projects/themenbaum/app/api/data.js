import { isAuthed, json } from "../lib/auth.js";
import { load, save, Conflict } from "../lib/store.js";
import { clean } from "../lib/validate.js";

export async function GET(request) {
  if (!isAuthed(request)) return json({ error: "Nicht angemeldet." }, 401);
  const { data, etag } = await load();
  return json({ data, etag });
}

export async function PUT(request) {
  if (!isAuthed(request)) return json({ error: "Nicht angemeldet." }, 401);
  let body;
  try { body = await request.json(); } catch { return json({ error: "Ungültige Daten." }, 400); }
  const data = clean(body?.data);
  if (!data) return json({ error: "Ungültige Daten." }, 400);
  try {
    const { etag } = await save(data, body.etag ?? null);
    return json({ etag });
  } catch (e) {
    if (e instanceof Conflict) {
      const cur = await load();
      return json({ error: "Auf einem anderen Gerät wurde inzwischen etwas geändert.", ...cur }, 409);
    }
    console.error(e);
    return json({ error: "Speichern fehlgeschlagen." }, 500);
  }
}
