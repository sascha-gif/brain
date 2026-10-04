// Lokaler Test ohne Vercel: STORE=memory ACCESS_CODE=test node dev-server.mjs
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";

process.env.STORE ??= "memory";
const routes = { "/api/login": await import("./api/login.js"), "/api/data": await import("./api/data.js") };

createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const mod = routes[url.pathname];
  if (mod) {
    const chunks = []; for await (const c of req) chunks.push(c);
    const body = chunks.length ? Buffer.concat(chunks) : undefined;
    const request = new Request(url, { method: req.method, headers: req.headers, body: ["GET", "HEAD"].includes(req.method) ? undefined : body });
    const fn = mod[req.method];
    const out = fn ? await fn(request) : new Response("", { status: 405 });
    res.writeHead(out.status, Object.fromEntries(out.headers));
    return res.end(Buffer.from(await out.arrayBuffer()));
  }
  try {
    const file = await readFile(new URL("./public" + (url.pathname === "/" ? "/index.html" : url.pathname), import.meta.url));
    res.writeHead(200, { "content-type": url.pathname.endsWith(".js") ? "text/javascript" : "text/html; charset=utf-8" });
    res.end(file);
  } catch { res.writeHead(404); res.end("not found"); }
}).listen(process.env.PORT || 3000, () => console.log("http://localhost:" + (process.env.PORT || 3000)));
