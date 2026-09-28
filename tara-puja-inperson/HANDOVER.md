# Tara Puja — In-Person Controller + App Sync — Handover

Developer notes for the WeBuddhist app output. For operator setup on Windows, see [README.md](README.md). The OBS overlays are a separate project, [`../tara-puja-overlay/`](../tara-puja-overlay/), which never talks to the app.

## 1. What this does

**In-person viewers** use the **WeBuddhist app**'s Text Reader, which auto-scrolls (like Spotify lyrics) to the current line in each user's chosen language. The operator advances `controller-inperson.html`; `server.js` POSTs each new position to the WeBuddhist live-recitation API, which the app follows.

```
   operator taps →  controller-inperson.html  (one click = one verse = one app segment)
                                    │ WebSocket {type:"set", index, cues:[{lang,text_id,segment_id}]}
                                    ▼
                    server.js  (Node, localhost:8080)
                     - serves the controller
                     - keeps the shared position (other open controllers follow it)
                     - POSTs each cue → api.webuddhist.com (secret stays server-side)
                                    │ HTTPS POST (position)
                                    ▼
                    api.webuddhist.com → WeBuddhist app follows
```

The app path is one HTTP POST per position change (not a persistent socket — deliberate, to save data). `server.js` coalesces rapid clicks to the latest position, spaces POSTs 150 ms apart, and only marks a segment sent on a `202`, so a throttled or failed POST is retried on the next advance.

## 2. Files

- `server.js` — Node HTTP + WebSocket server and the emit loop. Reads config from env (§4).
- `public/controller-inperson.html` — operator screen (Tibetan). Section menu (left), current section as tappable verses (right), prev/next, ↩ Back after Break/Tea. Sets `window.CHUNK_PER_VERSE` so each click moves exactly one segment.
- `public/sequence.js` — loads `content.json` and flattens it into chunks, copying `textIds` + `segmentIds` onto each so the controller can build cues.
- `public/content.json` — the content with per-verse app ids (§6).
- `emit-test.js` — standalone manual tester: `RECITATION_EMIT_SECRET_TOKEN=<secret> node emit-test.js 1-1` POSTs one 21-Tārās position; `... end` ends the session. Reads segments from `t21-segments.json`, whose `event_id` is the old dead event — pass `EVENT_ID` explicitly.
- `t21-segments.json` — the 21 Tārās recitation's 32 segments (reference + bo id) + event/text ids. Used only by `emit-test.js`.
- `start-server.bat` — Windows launcher that asks for the token and event ID.

## 3. How to run

```bash
RECITATION_EMIT_SECRET_TOKEN='<secret>' node server.js
```
Controller: `http://localhost:8080/`. The startup log prints `App emit: ON` when the secret is set, `OFF` otherwise (the controller still works, but the app won't follow). On a fresh server the controller publishes its current position as soon as it connects. Keep only one controller open against a live event.

## 4. Config / environment variables (read by server.js)

- `RECITATION_EMIT_SECRET_TOKEN` — **required to push to the app.** Shared secret; the WeBuddhist deployment must have this set too, or the endpoint returns `503 "not configured"`. Keep it out of the browser and out of this repo — server-side only.
- `EVENT_ID` — defaults to the current test event `3f3f8083-b32a-4628-b190-d249969e95db`. **Swap to the real event ID for the actual puja.** The authoritative UUID is always the one in the studio event-edit URL: `studio.webuddhist.com/groups/{group}/events/{EVENT-UUID}/edit`. It is a UUID (`xxxxxxxx-xxxx-…`), *not* the text/accumulator nanoid.
- `WB_HOST` — defaults to `api.webuddhist.com`.
- `PORT` — defaults to `8080` (the streaming server uses the same default; change one if both run on one computer).

## 5. WeBuddhist recitation API (reverse-engineered — the crux)

Backend doc: repo `Webuddhist-tech/WeBuddhist-Backend`, `documentation/live-recitation-sync-api.md` (develop branch). Key points, including things the doc doesn't spell out:

**Emit a position (what our server does), HTTP:**
```
POST https://api.webuddhist.com/api/v1/events/{event_id}/recitation/position
X-Recitation-Token: <RECITATION_EMIT_SECRET_TOKEN>
{ "text_id": "...", "segment_id": "...", "index": 12, "round_number": 1 }
→ 202 Accepted
```
`POST .../recitation/end` ends the session. Status codes (confirmed against backend source `pecha_api/events/recitation_live_views.py` + `recitation_live_service.py`):
- `202` = accepted (the emit loop prints nothing on success).
- `401` = wrong `X-Recitation-Token`.
- `404` = **no such event, or its group is unpublished.** This is the ONLY thing the emit route validates before fan-out (`assert_live_event`). **It never checks `text_id`/`segment_id`** — so a stale/moved text can NOT cause a 404. A wrong-but-present text just emits `202` and phones silently fail to scroll ("out of sync"), handled client-side. If you see 404: the event UUID is wrong/deleted, or its group is unpublished — fix in studio, not in `content.json`.
- `422` = bad body **or** a malformed `event_id` in the URL (e.g. angle brackets or a non-UUID pasted in — the response echoes the bad `input`, which is the fastest way to spot a paste error).
- `429` = past the 10/s per-event throttle (usually two controllers open at once).
- `503` = secret unset on the deployment, or Redis down.

**Auth gotcha (cost us time):** the recitation API validates the **consumer** audience `api.webuddhist.com`. A token from the CMS (`studio.webuddhist.com`) has audience `pecha-v2.org` and is rejected. For the WebSocket operator/viewer test pages you need a bearer token from logging into **webuddhist.com** (consumer), not studio. (Our controller uses the HTTP+secret path, so it doesn't need a bearer token at all.)

**Pairing rule (from the dev):** `text_id` and `segment_id` must be a **matched pair from the same language**. Each language has its own segment_id (and potentially its own text_id).

**Loading recitation content / getting segment IDs:**
```
POST https://api.webuddhist.com/api/v1/recitations/{id}   (bearer auth)
{ "language": "bo", "recitation": ["bo","en","zh"], "translations": [] }
```
Returns `{ text_id (root), title, segments: [ { recitation: { bo:{id,content}, en:{id,content}, zh:{id,content} }, translations:{}, transliterations:{}, adaptations:{} }, ... ] }`.
- **Critical:** with only `{language}` the segments come back **empty**. You must include the `recitation: [langs]` array to populate per-language `{id, content}`. The same goes for the other sub-objects (`translations`/`transliterations`/`adaptations`).
- Library segmentation IDs (`/library/v2/editions/{ed}/segmentation`) happen to equal the recitation's **bo** IDs for this text, but do NOT assume that in general — use the recitation load as source of truth.

**Cross-resolve:**
- The **reference test viewer** (`/api/v1/view/events/{id}/recitation`) loads only its *display* language's IDs, so it only follows a position in that same language.
- The **production app** loads all languages and cross-resolves: one operator sending the Tibetan pair drives every reader in their own language. The controller still sends one cue per mapped language (bo, en, zh).

**Hosted WebSocket service:** production sync is a single WebSocket, `wss://{host}/api/v1/events/{event_id}/recitation/live?token={bearer}`. Our HTTP-POST path is the officially supported route for a controller that can't hold a socket open (same validation, same fan-out). Reference pages: emitter `/api/v1/view/events/{event_id}/recitation/emitter` and viewer `/api/v1/view/events/{event_id}/recitation` (bearer from **webuddhist.com**, not studio). Use the emitter page to sanity-check an event independently of this rig.

## 6. Content mapping (`public/content.json`)

Section: `{ id, title:{bo,en,zh}, anytime?, app:{ text_ids:{bo,en,zh} }, verses:[...] }`. Verse: `{ id, kind, reference, rubric, lines:{bo,en,zh}, segment_ids:{bo,en,zh} }` (older entries may use single `text_id` / `segment_id`, read as bo).

Every section except Break (`s_break`, a stream-only title card that the in-person menu hides) is mapped in bo, en and zh. The controller skips any verse without ids, so an unmapped section simply doesn't move the app.

## 7. Key IDs

- **Current working event** (verified emitting `202` on 2026-09-23 and 2026-09-28): event_id **`3f3f8083-b32a-4628-b190-d249969e95db`**.
- **Old test event** "Tara Event" (a.k.a. "Dzongsar Drolma Bumtsok"), group **Compassionate Youth Association** — **now 404s** (deleted/recreated or group unpublished); kept only so old logs make sense: event_id `4aa33ef4-f5a0-4a38-ada4-a8f9d71ae5d1`, group_id `4cc9f2c0-da6c-41ab-85f3-4b569ff1a87d`.
- **21 Tārās recitation:** root text `HyUbHGlzS9LsSrgiFQNYE` (bo "སྒྲོལ་མ་ཉེར་གཅིག་ལ་བསྟོད་པ།"); bo edition / position text_id used by `emit-test.js` = `lEmYv8BrRQkOMPY9ymQpS`; 32 segments (3 front-matter, 21 praises `1-1..1-22`, 6 benefit `2-1..2-6`, 1 closing).
- CMS to edit the event: `https://studio.webuddhist.com/groups/{group}/events/{event}/edit`.

## 8. Gotchas / lessons

- **`emit 404` is event-level, not content-level.** Check the event UUID in the studio URL or re-publish the group; never touch `content.json`. Pasting the text nanoid (or a `<bracketed>` value) into `EVENT_ID` gives a `422 uuid_parsing` error that echoes the bad input.
- Some sandboxed tooling **can't reach `api.webuddhist.com`** (DNS blocked). Test live POSTs from a normal terminal.
- After editing `server.js`, **restart** it; after editing `public/*`, refresh the controller.

---
*Split out of `tara-puja-overlay/HANDOVER.md` on 2026-09-28, when the app emit moved from the streaming controller to this one.*
