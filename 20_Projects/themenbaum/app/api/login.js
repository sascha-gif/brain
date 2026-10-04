import { checkCode, sessionCookie, clearCookie, isAuthed, json } from "../lib/auth.js";

export async function GET(request) {
  return json({ ok: isAuthed(request) });
}

// Höchstens 8 Fehlversuche pro IP in 15 Minuten
const fails = new Map();
const WINDOW = 15 * 60 * 1000, LIMIT = 8;

export async function POST(request) {
  const ip = request.headers.get("x-client-ip") || "?";
  const now = Date.now();
  const rec = fails.get(ip);
  if (rec && now - rec.since < WINDOW && rec.n >= LIMIT) {
    return json({ error: "Zu viele Fehlversuche. Bitte in 15 Minuten erneut versuchen." }, 429);
  }
  let code = "";
  try { code = (await request.json())?.code ?? ""; } catch {}
  if (!checkCode(code)) {
    const r = rec && now - rec.since < WINDOW ? rec : { since: now, n: 0 };
    r.n++; fails.set(ip, r);
    await new Promise((r) => setTimeout(r, 900)); // bremst Durchprobieren
    return json({ error: "Code stimmt nicht." }, 401);
  }
  fails.delete(ip);
  return json({ ok: true }, 200, { "set-cookie": sessionCookie(request) });
}

export async function DELETE() {
  return json({ ok: true }, 200, { "set-cookie": clearCookie() });
}
