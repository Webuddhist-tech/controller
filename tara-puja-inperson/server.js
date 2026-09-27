// Puja IN-PERSON server: serves the in-person controller and pushes the recitation
// position it sets to the WeBuddhist app (the secret token stays here, never in the browser).
//
// Run:  start-server.bat  (Windows)   or   node server.js
// Then: controller -> http://localhost:8080/

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

// WeBuddhist live-recitation emit (HTTP). The shared secret stays here, never in the browser.
const WB_HOST = process.env.WB_HOST || "api.webuddhist.com";
const EVENT_ID = process.env.EVENT_ID || "3f3f8083-b32a-4628-b190-d249969e95db";
const EMIT_TOKEN = process.env.RECITATION_EMIT_SECRET_TOKEN || "";
// The event holds ONE position; we only ever publish the LATEST one the operator landed on.
// A single pump coalesces rapid advances (and any reconnect / duplicate-client storm) down
// to the newest position, spaces the POSTs, and — crucially — marks a segment "sent" ONLY on
// a 202, so a throttled (429) or failed publish is retried later, never silently swallowed.
const EMIT_MIN_GAP_MS = 150;                 // ceiling ~6-7 POSTs/s, far under the per-event limit
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const lastSent = {};      // per stream: last SUCCESSFULLY published segment|round
let target = null;        // newest { cues, index } awaiting publish (latest wins)
let pumping = false;

async function publish(cue, index) {
  try {
    const r = await fetch(`https://${WB_HOST}/api/v1/events/${EVENT_ID}/recitation/position`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Recitation-Token": EMIT_TOKEN },
      body: JSON.stringify({ text_id: cue.text_id, segment_id: cue.segment_id, index, round_number: cue.round_number || 1 }),
    });
    if (r.status === 202) return true;
    console.log("emit", r.status, cue.segment_id, (await r.text()).slice(0, 160).replace(/\s+/g, " ").trim());
  } catch (e) { console.log("emit failed:", e.message); }
  return false;   // not marked sent -> retried on the next advance
}

async function pump() {
  if (pumping) return;
  pumping = true;
  try {
    while (target) {
      const p = target; target = null;                 // take the newest; drop anything older
      for (const cue of p.cues) {
        if (!cue || !cue.text_id || !cue.segment_id) continue;
        const stream = cue.lang || cue.text_id;
        const key = cue.segment_id + "|" + (cue.round_number || 1);
        if (lastSent[stream] === key) continue;         // already published this position
        if (await publish(cue, p.index)) lastSent[stream] = key;
        await sleep(EMIT_MIN_GAP_MS);
      }
    }
  } finally { pumping = false; }
}
function scheduleEmit(cues, index) {
  if (!EMIT_TOKEN) return;
  target = { cues, index };   // latest wins: connect/reconnect storms collapse to one position
  pump();
}

const MIME = { ".html": "text/html", ".json": "application/json", ".js": "text/javascript", ".css": "text/css", ".png": "image/png", ".jpg": "image/jpeg", ".svg": "image/svg+xml", ".webp": "image/webp" };

const server = http.createServer((req, res) => {
  let file = decodeURIComponent(req.url.split("?")[0]);
  if (file === "/" || file === "/controller.html") file = "/controller-inperson.html";
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
      // one or more cues (one per language edition); tolerate the old single-cue shape
      const cues = Array.isArray(msg.cues) ? msg.cues : (msg.cue ? [msg.cue] : []);
      scheduleEmit(cues, msg.index);   // debounced app POSTs (overlays already updated above)
    }
    // Hide/show overlays without moving the position — never emits to the app.
    if (msg.type === "hide" && typeof msg.hidden === "boolean") {
      state = { ...state, hidden: msg.hidden };
      broadcast();
    }
  });
});

server.listen(PORT, () => {
  console.log(`Puja in-person controller running — keep this window open.`);
  console.log(`  Controller: http://localhost:${PORT}/`);
  console.log(EMIT_TOKEN
    ? `  App emit:    ON  -> https://${WB_HOST} event ${EVENT_ID}`
    : "  App emit:    OFF (set RECITATION_EMIT_SECRET_TOKEN to push positions to the WeBuddhist app)");
});
