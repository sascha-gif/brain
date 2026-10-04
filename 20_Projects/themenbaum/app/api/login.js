import { checkCode, sessionCookie, clearCookie, isAuthed, json } from "../lib/auth.js";

export async function GET(request) {
  return json({ ok: isAuthed(request) });
}

export async function POST(request) {
  let code = "";
  try { code = (await request.json())?.code ?? ""; } catch {}
  if (!checkCode(code)) {
    await new Promise((r) => setTimeout(r, 900)); // bremst Durchprobieren
    return json({ error: "Code stimmt nicht." }, 401);
  }
  return json({ ok: true }, 200, { "set-cookie": sessionCookie(request) });
}

export async function DELETE() {
  return json({ ok: true }, 200, { "set-cookie": clearCookie() });
}
