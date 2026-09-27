// Manual test emitter for WeBuddhist live-recitation sync (21 Tārās).
// POSTs one position to the event over HTTP (no persistent socket).
// The shared secret must be in the env — never hard-code it here.
//   RECITATION_EMIT_SECRET_TOKEN=<secret> node emit-test.js <ref|index|end> [round]
// examples:
//   node emit-test.js 1-1     first praise verse
//   node emit-test.js 3       4th segment (0-based index)
//   node emit-test.js end     end the session (releases followers)

const fs = require("fs");
const cfg = JSON.parse(fs.readFileSync(__dirname + "/t21-segments.json", "utf8"));

const HOST = process.env.WB_HOST || "api.webuddhist.com";
const EVENT_ID = process.env.EVENT_ID || cfg.event_id;
const TEXT_ID = process.env.TEXT_ID || cfg.text_id;
const TOKEN = process.env.RECITATION_EMIT_SECRET_TOKEN;
const SEGMENTS = cfg.segments;

async function main() {
  if (!TOKEN) { console.error("Set RECITATION_EMIT_SECRET_TOKEN in the env first."); process.exit(1); }
  const arg = process.argv[2];
  const round = Number(process.argv[3] || 1);

  if (arg === "end") {
    const r = await fetch(`https://${HOST}/api/v1/events/${EVENT_ID}/recitation/end`,
      { method: "POST", headers: { "X-Recitation-Token": TOKEN } });
    console.log("end ->", r.status, await r.text());
    return;
  }

  let seg = SEGMENTS.find(s => s.reference === arg);
  if (!seg && /^\d+$/.test(arg || "")) seg = SEGMENTS[Number(arg)];
  if (!seg) { console.error("Usage: node emit-test.js <ref e.g. 1-1 | index 0-31 | end> [round]"); process.exit(1); }

  const body = { text_id: TEXT_ID, segment_id: seg.id, index: SEGMENTS.indexOf(seg), round_number: round };
  const r = await fetch(`https://${HOST}/api/v1/events/${EVENT_ID}/recitation/position`,
    { method: "POST", headers: { "Content-Type": "application/json", "X-Recitation-Token": TOKEN }, body: JSON.stringify(body) });
  console.log(`POST ${seg.reference} (${seg.id}) round ${round} ->`, r.status);
  console.log(await r.text());
}
main().catch(e => { console.error(e); process.exit(1); });
