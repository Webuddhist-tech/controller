// Puja overlay server (streaming / OBS only): serves the pages and keeps one shared
// "current position" that the controller sets and every language overlay listens to.
// It does not talk to the WeBuddhist app — that is the separate in-person version.
//
// Run:  node server.js       (needs the 'ws' package: npm install ws)
// Then: controller  -> http://localhost:8080/controller.html
//       OBS sources -> http://localhost:8080/overlay.html?lang=en  (zh, hi, bo)

const http = require("http");
const fs = require("fs");
const path = require("path");
const { WebSocketServer } = require("ws");

const PORT = process.env.PORT || 8080;
const PUBLIC = path.join(__dirname, "public");

// Shared state: which step of the sequence, and which pass of the Taras loop.
// hidden = overlays blanked (only when the operator presses Hide); position is kept.
// set = a controller has published since start (overlays stay blank until then, so a
// fresh server never flashes screen 0 — even an older controller clears this by moving).
let state = { index: 0, pass: 1, hidden: false, set: false };

const MIME = { ".html": "text/html", ".json": "application/json", ".js": "text/javascript", ".css": "text/css", ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".webp": "image/webp" };

const server = http.createServer((req, res) => {
  let file = decodeURIComponent(req.url.split("?")[0]);
  if (file === "/") file = "/controller.html";
  const full = path.join(PUBLIC, path.normalize(file));
  if (!full.startsWith(PUBLIC)) { res.writeHead(403); return res.end("Forbidden"); }
  fs.readFile(full, (err, data) => {
    if (err) { res.writeHead(404); return res.end("Not found"); }
    // no-store: OBS/CEF caches aggressively; without this, edits to content.json
    // and the overlay pages don't show up on a plain Refresh.
    res.writeHead(200, { "Content-Type": MIME[path.extname(full)] || "application/octet-stream", "Cache-Control": "no-store" });
    res.end(data);
  });
});

const wss = new WebSocketServer({ server });

function broadcast() {
  const msg = JSON.stringify({ type: "state", ...state });
  for (const client of wss.clients) {
    if (client.readyState === 1) client.send(msg);
  }
}

wss.on("connection", (ws) => {
  // Send current state immediately so a freshly-loaded overlay catches up.
  ws.send(JSON.stringify({ type: "state", ...state }));
  ws.on("message", (raw) => {
    let msg;
    try { msg = JSON.parse(raw); } catch { return; }
    if (msg.type === "set" && typeof msg.index === "number") {
      state = { ...state, index: msg.index, pass: msg.pass || 1, set: true };
      if (typeof msg.hidden === "boolean") state.hidden = msg.hidden;
      broadcast();
    }
    // Hide/show overlays without moving the position.
    if (msg.type === "hide" && typeof msg.hidden === "boolean") {
      state = { ...state, hidden: msg.hidden };
      broadcast();
    }
  });
});

server.listen(PORT, () => {
  console.log(`Puja overlay running:`);
  console.log(`  Controller: http://localhost:${PORT}/controller.html`);
  console.log(`  Overlays:   http://localhost:${PORT}/overlay.html?lang=bo  (also en, zh)`);
});
