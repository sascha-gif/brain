import { createHmac, timingSafeEqual } from "node:crypto";

const COOKIE = "tb_session";
const MAX_AGE = 60 * 60 * 24 * 180; // 180 Tage

function secret() {
  const code = process.env.ACCESS_CODE;
  if (!code) throw new Error("ACCESS_CODE fehlt");
  return code;
}

// Sitzungstoken leitet sich vom Zugangscode ab: Code ändern = alle Geräte abgemeldet.
function token() {
  return createHmac("sha256", secret()).update("themenbaum-session-v1").digest("hex");
}

function same(a, b) {
  const x = Buffer.from(String(a)), y = Buffer.from(String(b));
  return x.length === y.length && timingSafeEqual(x, y);
}

export function checkCode(code) {
  return same(code ?? "", secret());
}

export function isAuthed(request) {
  const raw = request.headers.get("cookie") || "";
  const m = raw.match(new RegExp(`(?:^|;\\s*)${COOKIE}=([a-f0-9]+)`));
  return !!m && same(m[1], token());
}

export function sessionCookie(request) {
  const secure = new URL(request.url).protocol === "https:" ? "; Secure" : "";
  return `${COOKIE}=${token()}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${MAX_AGE}${secure}`;
}

export function clearCookie() {
  return `${COOKIE}=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0`;
}

export function json(body, status = 200, headers = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store", ...headers },
  });
}
