# Tara Puja — Controller + OBS Overlay + App Sync — Handover

Hand this to a fresh agent to continue the work. It captures the whole system, how to run it, the WeBuddhist recitation API we reverse-engineered, current state, and what's left.

## 1. What this project is

A live multi-language experience for a Buddhist puja (the **Zabtik Drolchok / 21 Tārās**, Dzongsar Shedra Tara Puja). One operator (a Tibetan umdze) drives everything from a single controller:

- **Online viewers** watch a YouTube livestream with **OBS overlays** showing the current lines (one overlay per language: bo / en / zh).
- **In-person viewers** use the **WeBuddhist app**'s Text Reader, which auto-scrolls (like Spotify lyrics) to the current line in each user's chosen language.

Both are driven by the same controller: advancing it moves the OBS overlays (locally, over a WebSocket) **and** POSTs a position to the WeBuddhist live-recitation API, which the app follows.

## 2. Where the code lives

- **Active dev copy (the one to edit):** `~/Downloads/tara-puja-overlay/` on Evan's Mac (M-series MacBook Air, Node v22).
- There is also a **vault copy** in the Obsidian vault `~/WeBuddhist/21-taras-rails/` under `5 - OVERLAYS/tara-puja-overlay/` (GitHub-backed). **Changes in Downloads are NOT synced to the vault** — the Downloads copy has diverged and is the live one. Don't edit the vault copy unless asked.

## 3. Architecture / data flow

```
                    ┌─────────────────────────────────────────────┐
   operator taps →  │ controller.html  (Tibetan operator screen)  │
                    │  - left: section menu                        │
                    │  - right: current section as tappable verses │
                    │  - Round control, Send-language selector     │
                    └───────────────┬─────────────────────────────┘
                                    │ WebSocket {type:"set", index, cue}
                                    ▼
                    ┌─────────────────────────────────────────────┐
                    │ server.js  (Node, localhost:8080)           │
                    │  - serves the pages                          │
                    │  - broadcasts {type:"state",index} to overlays│
                    │  - POSTs cue → WeBuddhist recitation API     │
                    └──────┬───────────────────────┬──────────────┘
          broadcast (local)│                       │ HTTPS POST (position)
                           ▼                       ▼
           overlay.html?lang=bo|en|zh     api.webuddhist.com
           (OBS browser sources)          → WeBuddhist app follows (in-person)
```

- **OBS path** is entirely local (WebSocket on localhost), zero added latency, works with no internet dependency.
- **App path** is an HTTP POST per position change (not a persistent socket — deliberate, to save data). Secret stays server-side.

## 4. Files (in `~/Downloads/tara-puja-overlay/`)

- `server.js` — Node HTTP + WebSocket server. Serves `public/`, holds shared state `{index, pass}`, broadcasts `{type:"state",index}` to overlays, and POSTs positions to WeBuddhist on segment change. Reads config from env (see §6). Run with `node server.js`.
- `public/controller.html` — operator screen (Tibetan). Section menu (left), current section as tappable verse list (right) with teleprompter auto-scroll, prev/next, **Round** control, **Send** language selector.
- `public/overlay.html` — OBS browser source, one per language via `?lang=bo|en|zh|hi`. Two lines at a time, Jomolhari for Tibetan, fixed-width lower-third box, persistent **section-title tab** (top-left, online-only).
- `public/sequence.js` — loads `content.json`, flattens sections→verses→2-line "chunks" the controller/overlays step through. Carries per-language segment IDs onto each chunk.
- `public/content.json` — the content (see §8). 23 sections: `test-t21` (the mapped 21 Tārās test) + `s1..s22` (the full sadhana, bo only, unmapped).
- `emit-test.js` — standalone manual tester: `RECITATION_EMIT_SECRET_TOKEN=<secret> node emit-test.js 1-1` POSTs one 21-Tārās position; `... end` ends the session. Reads segments from `t21-segments.json`.
- `t21-segments.json` — the 21 Tārās recitation's 32 segments (reference + bo id) + event/text ids. Used by `emit-test.js`.
- `t21-section.json` — the built `test-t21` section (source of truth for that section).
- `build_sadhana.py` / `build_content.py` — parsers that built `content.json` from the Tibetan sadhana markdown.
- `README.md`, `branch-output-setup-guide.md`, `branch-output-background-and-troubleshooting.md` — OBS Branch Output docs (three-language streaming from one OBS instance; from an earlier arc).
- `*.bak*` — backups from each edit step; safe to ignore or delete.

## 5. How to run

```bash
cd ~/Downloads/tara-puja-overlay
RECITATION_EMIT_SECRET_TOKEN='<secret>' node server.js
```
Then:
- Controller: `http://localhost:8080/controller.html`
- Overlays (OBS browser sources, 1920×1080, transparent): `http://localhost:8080/overlay.html?lang=bo` (and `?lang=en`, `?lang=zh`)

Startup log prints `App emit: ON` when the secret is set, `OFF` otherwise (overlays still work when off). Hard-refresh OBS browser sources after any overlay change.

## 6. Config / environment variables (read by server.js)

- `RECITATION_EMIT_SECRET_TOKEN` — **required to push to the app.** Shared secret; the WeBuddhist deployment must have this set too, or the endpoint returns `503 "not configured"`. Keep it out of the browser — server-side only.
- `EVENT_ID` — the server.js default `4aa33ef4-f5a0-4a38-ada4-a8f9d71ae5d1` is **stale** (that event now 404s — it was deleted/recreated). The current working event UUID is **`3f3f8083-b32a-4628-b190-d249969e95db`** — pass it explicitly (`EVENT_ID='3f3f8083-…' node server.js`) until the default is updated. **Swap to the real event ID for the actual puja.** The authoritative UUID is always the one in the studio event-edit URL: `studio.webuddhist.com/groups/{group}/events/{EVENT-UUID}/edit`. It is a UUID (`xxxxxxxx-xxxx-…`), *not* the text/accumulator nanoid.
- `WB_HOST` — defaults to `api.webuddhist.com`.
- `PORT` — defaults to `8080`.

## 7. WeBuddhist recitation API (reverse-engineered — the crux)

Backend doc: repo `Webuddhist-tech/WeBuddhist-Backend`, `documentation/live-recitation-sync-api.md` (develop branch). Key points, including things the doc doesn't spell out:

**Emit a position (what our controller does), HTTP:**
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
- `429` = past the 10/s per-event throttle.
- `503` = secret unset on the deployment, or Redis down.

**Auth gotcha (cost us time):** the recitation API validates the **consumer** audience `api.webuddhist.com`. A token from the CMS (`studio.webuddhist.com`) has audience `pecha-v2.org` and is rejected. For the WebSocket operator/viewer test pages you need a bearer token from logging into **webuddhist.com** (consumer), not studio. (Our controller uses the HTTP+secret path, so it doesn't need a bearer token at all.)

**Pairing rule (from the dev):** `text_id` and `segment_id` must be a **matched pair from the same language**. Each language has its own segment_id (and potentially its own text_id).

**Loading recitation content / getting segment IDs:**
```
POST https://api.webuddhist.com/api/v1/recitations/{id}   (bearer auth)
{ "language": "bo", "recitation": ["bo","en","zh"], "translations": [] }
```
Returns `{ text_id (root), title, segments: [ { recitation: { bo:{id,content}, en:{id,content}, zh:{id,content} }, translations:{}, transliterations:{}, adaptations:{} }, ... ] }`.
- **Critical:** with only `{language}` the segments come back **empty**. You must include the `recitation: [langs]` array to populate per-language `{id, content}`.
- Library segmentation IDs (`/library/v2/editions/{ed}/segmentation`) happen to equal the recitation's **bo** IDs for this text, but do NOT assume that in general — use the recitation load as source of truth.

**Cross-resolve (the big question, now answered):**
- The **reference test viewer** (`/api/v1/view/events/{id}/recitation`) loads only its *display* language's IDs, so it only follows a position in that same language. That made us think cross-resolve was off.
- The **production app (test branch)** loads all languages and cross-resolves: **one operator sending the Tibetan pair drives every reader in their own language, plus the OBS overlays, simultaneously. Confirmed working.** So no per-language events or multi-language position is needed — the single Tibetan pair is enough.

## 8. Content data model (`public/content.json`)

Top level: `{ _README, languages:["bo","en","zh"], lines_per_screen:2, sections:[...] }`.

Section: `{ id, title:{bo,en,zh}, verses:[...] }`. The mapped test section also has `app:{ text_id, event_id }` and `_test:true`.

Verse: `{ id, kind, reference, rubric, lines:{bo:[...],en:[...],zh:[...]}, segment_id (bo, legacy), segment_ids:{bo,en,zh} }`.

`sequence.js` chunks each verse's lines into 2-line screens (1 line/screen when a line is long), merges short Namo/seed openers into the first sloka line, and copies `textId` + `segmentIds` onto each chunk so the controller can emit.

**Current sections:** `test-t21` (Praises to the 21 Tārās, fully mapped, all 3 languages' segment IDs) is section 0; `s1..s22` are the full sadhana (bo only, **not** app-mapped). `test-t21` is marked `_test:true` — remove it (one-line filter on the `sections` array) when done testing; it leaves the full sadhana intact.

## 9. Key IDs

- **Current working event** (verified emitting `202` on 2026-09-23): event_id **`3f3f8083-b32a-4628-b190-d249969e95db`** (its group is published, so HTTP emit works).
- **Old test event** "Tara Event" (a.k.a. "Dzongsar Drolma Bumtsok"), group **Compassionate Youth Association** — **now 404s** (deleted/recreated or group unpublished); kept here only so old logs make sense:
  - event_id `4aa33ef4-f5a0-4a38-ada4-a8f9d71ae5d1` (dead)
  - group_id `4cc9f2c0-da6c-41ab-85f3-4b569ff1a87d`
- **21 Tārās recitation:** root text `HyUbHGlzS9LsSrgiFQNYE` (bo "སྒྲོལ་མ་ཉེར་གཅིག་ལ་བསྟོད་པ།"); bo edition / position text_id used = `lEmYv8BrRQkOMPY9ymQpS`; 32 segments (3 front-matter, 21 praises `1-1..1-22`, 6 benefit `2-1..2-6`, 1 closing).
- CMS to edit the event: `https://studio.webuddhist.com/groups/{group}/events/{event}/edit`.

## 10. Controller features

- Tibetan-only operator screen. Left = section menu; Next scrolls down the current section then rolls into the next.
- Right pane = the whole current section as tappable verse lines (paper layout), current line highlighted; tap any line to jump (recover if the umdze skips). Teleprompter auto-scroll keeps the active line in a comfort band, only on advance.
- **Round control** (`− [N] +`, keys `[` / `]`): sends `round_number` with each position (the 21 Tārās repeats in rounds; the app uses it to disambiguate). Auto-resets to 1 when moving to a different section.
- **Send** selector (bo / EN / 中文): which language pair to emit. Default `bo` (the operator's language). Because the app cross-resolves, `bo` drives all languages; the selector is mainly for testing/fallback.

## 11. Overlay features (`overlay.html`)

- One per language via `?lang=`. Two lines per screen; long single lines wrap / show one-per-screen. Jomolhari font for Tibetan (fixes Sanskrit-in-Tibetan mantra stacking). Lower-third translucent box, **fixed width** (max 1200px, centered) — an earlier "hug the text" version was reverted because the resizing was distracting (`overlay.html.bak5` has it if wanted).
- **Section-title tab:** small persistent tab at the top-left (flush) of the box, showing the current section title in that overlay's language (falls back en→bo). Stays up continuously, only changes at section boundaries, doesn't fade with lines. **Online/OBS only — does not touch the app.**

## 12. Current state — what works

- ✅ Controller → server.js → OBS overlays (all languages) — local, live.
- ✅ Controller → server.js → HTTP POST → **WeBuddhist app**: one Tibetan operator drives the app in **all three languages** AND the OBS overlays **simultaneously** — verified on the app's test branch with OBS running.
- ✅ Round control and Send-language selector in the controller.
- ✅ Section-title tab + fixed-width box on overlays.
- ✅ `test-t21` fully mapped with all three languages' segment IDs.

## 13. What's left to do

1. **Map the rest of the sadhana to recitation IDs.** Only `test-t21` emits today. **Blocked:** the full sadhana has NOT been added to the WeBuddhist library yet, so there are no recitation IDs to map to. Once each sadhana section exists as a WeBuddhist recitation, map its verses the same way `test-t21` was (fetch via the recitation load endpoint, attach `segment_ids` per verse, set the section's `app.text_id`). Overlay-only sections just won't emit — that's fine.
2. **Production config:** set `EVENT_ID` to the real event (not the test one) and ensure `RECITATION_EMIT_SECRET_TOKEN` is set on the machine running `server.js` during the puja.
3. **Remove `test-t21`** (or fold the real 21 Tārās mapping into the sadhana's own 21 Tārās section, `s11` "ཕྱག་འཚལ་ཉེར་གཅིག") when moving past testing. Note: `s11` is a slightly different recension (opens with a "Tāre" line; the recitation opens with "Drölma") — reconcile which verse maps to which segment when mapping it.
4. **Optional polish:** overlay title tab styling, en/zh section titles (most sadhana sections have bo titles only), round-number UX.

## 14. Gotchas / lessons

- The device sandbox that runs shell commands **can't reach `api.webuddhist.com`** (DNS blocked). Test any live POST from Evan's own Terminal, not from tooling.
- Files here are edited in place on the Mac (`~/Downloads/tara-puja-overlay`). After editing `server.js`, **restart** `node server.js`; after editing `public/*`, **hard-refresh** the browser / OBS source.
- Editing tips used throughout: exact-match string replaces with a uniqueness assert; syntax-check `server.js`/`sequence.js` with `node --check`, and `controller.html`/`overlay.html` inline scripts by extracting the `<script>` and `new Function(...)`.
- The recitation-content sub-objects (`recitation`/`translations`/`transliterations`/`adaptations`) are only populated when you pass the matching array in the request body.

## 15. Update log — 2026-09-23

Corrections to the picture above, from a live debugging session. (§6/§7/§9 already patched inline; this is the consolidated "what changed and why".)

**A. The `emit 404` was event-level, not content-level.** Symptom: every position POST returned `404 {"detail":"Not found"}`. Cause: the test event UUID had been recreated. The emit route validates *only* that the event exists and its group is published — never the text/segment (see §7). Fix: point `EVENT_ID` at the current event `3f3f8083-b32a-4628-b190-d249969e95db`. Lesson: **404 ⇒ check the event UUID in the studio URL / re-publish the group; never touch `content.json`.** The text/accumulator id `lEmYv8BrRQkOMPY9ymQpS` is a nanoid (already our correct `text_id`) and is *not* an event id — pasting it (or a `<bracketed>` value) into `EVENT_ID` yields a `422 uuid_parsing` error that echoes the bad input.

**B. The hosted `wss://` service already exists** — the architecture handoff's "needs building" is out of date. Production sync is a single WebSocket: `wss://{host}/api/v1/events/{event_id}/recitation/live?token={bearer}`. Our `server.js` HTTP-POST path is the officially-supported "controller that can't hold a socket open" route (same validation, same fan-out) — **it needs no rewrite.** There are official reference pages too: emitter `/api/v1/view/events/{event_id}/recitation/emitter` and viewer `/api/v1/view/events/{event_id}/recitation` (bearer from **webuddhist.com**, not studio). Backend doc: `Webuddhist-tech/WeBuddhist-Backend` → `documentation/live-recitation-sync-api.md` (develop). Use the emitter page to sanity-check an event independently of our rig.

**C. Streaming audio model (Branch Output).** Branch Output does **not** inherit OBS's normal audio — each filter reads a specific audio track and is silent unless (a) its **Custom Audio Source** is enabled and pointed at a track, and (b) that track has a source ticked onto it in **Advanced Audio Properties**. Hearing audio in OBS (program/Track 1) does not mean the branch has it. For this puja **all three streams carry the same Tibetan chant audio** — only the overlays differ by script — so the guide's per-track split (Track 1/2/3) is *optional* for a chant-only event: point all three Custom Audio Sources at one shared, fed track. Keep the per-track routing only if a **teaching phase** with per-language translators is added. After fixing audio, restart that output in the Branch Outputs dock and reload the stream on the phone (YouTube caches the silent lead-in). Full detail: `branch-output-setup-guide.md` §4/§5 + the troubleshooting table.

---
*Written 2026-09-20. Updated 2026-09-23 (event UUID, 404 semantics, wss service, Branch Output audio). Active copy: `~/Downloads/tara-puja-overlay/`.*
