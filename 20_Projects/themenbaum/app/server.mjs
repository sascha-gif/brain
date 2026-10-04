// Themenbaum-Server. Keine Abhängigkeiten, nur Node >= 20.
// Start:  ACCESS_CODE=... PORT=3100 DATA_DIR=/var/lib/themenbaum node server.mjs
// Läuft hinter nginx/Caddy (TLS), lauscht nur auf 127.0.0.1.
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";

if (!process.env.ACCESS_CODE) { console.error("ACCESS_CODE fehlt"); process.exit(1); }
const routes = { "/api/login": await import("./api/login.js"), "/api/data": await import("./api/data.js") };
const PORT = Number(process.env.PORT || 3100);
const HOST = process.env.HOST || "127.0.0.1";

const SECURITY = {
  "x-frame-options": "DENY",
  "x-content-type-options": "nosniff",
  "referrer-policy": "same-origin",
  "x-robots-tag": "noindex, nofollow",
};

createServer(async (req, res) => {
  try {
    const proto = req.headers["x-forwarded-proto"] || "http";
    const url = new URL(req.url, `${proto}://${req.headers.host || "localhost"}`);
    const mod = routes[url.pathname];
    if (mod) {
      const chunks = []; let size = 0;
      for await (const c of req) { size += c.length; if (size > 2_000_000) { res.writeHead(413); return res.end(); } chunks.push(c); }
      const hasBody = !["GET", "HEAD"].includes(req.method);
      const headers = new Headers(); for (const [k, v] of Object.entries(req.headers)) if (typeof v === "string") headers.set(k, v);
      headers.set("x-client-ip", String(req.headers["x-real-ip"] || req.socket.remoteAddress || ""));
      const request = new Request(url, { method: req.method, headers, body: hasBody ? Buffer.concat(chunks) : undefined });
      const fn = mod[req.method];
      const out = fn ? await fn(request) : new Response("", { status: 405 });
      res.writeHead(out.status, { ...SECURITY, ...Object.fromEntries(out.headers) });
      return res.end(Buffer.from(await out.arrayBuffer()));
    }
    if (url.pathname !== "/" && url.pathname !== "/index.html") { res.writeHead(404, SECURITY); return res.end("Nicht gefunden"); }
    const file = await readFile(new URL("./public/index.html", import.meta.url));
    res.writeHead(200, { ...SECURITY, "content-type": "text/html; charset=utf-8", "cache-control": "no-cache" });
    res.end(file);
  } catch (e) {
    console.error(e);
    res.writeHead(500); res.end("Fehler");
  }
}).listen(PORT, HOST, () => console.log(`Themenbaum läuft auf http://${HOST}:${PORT}`));
