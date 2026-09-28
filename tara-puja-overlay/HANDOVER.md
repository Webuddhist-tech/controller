# Tara Puja — Streaming Controller + OBS Overlay — Handover

Hand this to a fresh agent to continue the work. It captures the streaming system, how to run it, current state, and what's left.

> **Split on 2026-09-28:** this project now drives the **OBS overlays only**. The WeBuddhist app sync (emit token, event ID, recitation API, segment-ID mapping, `emit-test.js`) moved to the in-person controller — see [`../tara-puja-inperson/HANDOVER.md`](../tara-puja-inperson/HANDOVER.md).

## 1. What this project is

A live multi-language experience for a Buddhist puja (the **Zabtik Drolchok / 21 Tārās**, Dzongsar Shedra Tara Puja). Two outputs, each driven by its own operator controller:

- **Online viewers** watch a YouTube livestream with **OBS overlays** showing the current lines (one overlay per language: bo / en / zh).
- **In-person viewers** use the **WeBuddhist app**'s Text Reader, which auto-scrolls to the current line. That is driven by a **separate** controller, [`../tara-puja-inperson/`](../tara-puja-inperson/), not by this one.

This controller moves the OBS overlays only (locally, over a WebSocket). It never contacts the WeBuddhist API. At an event that is both streamed and followed in the app, run both controllers.

## 2. Where the code lives

- **Active dev copy (the one to edit):** `~/Downloads/tara-puja-overlay/` on Evan's Mac (M-series MacBook Air, Node v22).
- There is also a **vault copy** in the Obsidian vault `~/WeBuddhist/21-taras-rails/` under `5 - OVERLAYS/tara-puja-overlay/` (GitHub-backed). **Changes in Downloads are NOT synced to the vault** — the Downloads copy has diverged and is the live one. Don't edit the vault copy unless asked.

## 3. Architecture / data flow

```
   operator taps →  controller.html  (Tibetan operator screen: section menu + tappable verses)
                                    │ WebSocket {type:"set", index, hidden}  /  {type:"hide", hidden}
                                    ▼
                    server.js  (Node, localhost:8080)
                     - serves the pages
                     - broadcasts {type:"state", index, hidden, set} to every overlay
                                    │ broadcast (local)
                                    ▼
                    overlay.html?lang=bo|en|zh  (OBS browser sources)
```

- Entirely local (WebSocket on localhost): zero added latency, no internet dependency except the web fonts.

## 4. Files (in `~/Downloads/tara-puja-overlay/`)

- `server.js` — Node HTTP + WebSocket server. Serves `public/`, holds shared state `{index, pass, hidden, set}` and broadcasts it to the overlays. Run with `node server.js`.
- `public/controller.html` — operator screen (Tibetan). Section menu (left), current section as tappable verse list (right) with teleprompter auto-scroll, prev/next, **Hide overlays**.
- `public/overlay.html` — OBS browser source, one per language via `?lang=bo|en|zh|hi`. Two lines at a time, Jomolhari for Tibetan, fixed-width lower-third box, persistent **section-title tab** (top-left, online-only).
- `public/sequence.js` — loads `content.json`, flattens sections→verses→2-line "chunks" the controller/overlays step through.
- `public/content.json` — the content (see §8).
- `t21-section.json` — the built `test-t21` section (source of truth for that section).
- `build_sadhana.py` / `build_content.py` — parsers that built `content.json` from the Tibetan sadhana markdown.
- `README.md`, `branch-output-setup-guide.md`, `branch-output-background-and-troubleshooting.md` — OBS Branch Output docs (three-language streaming from one OBS instance; from an earlier arc).
- `*.bak*` — backups from each edit step; safe to ignore or delete.

## 5. How to run

```bash
cd ~/Downloads/tara-puja-overlay
node server.js
```
Then:
- Controller: `http://localhost:8080/controller.html`
- Overlays (OBS browser sources, 1920×1080, transparent): `http://localhost:8080/overlay.html?lang=bo` (and `?lang=en`, `?lang=zh`)

No token or event ID is needed. Hard-refresh OBS browser sources after any overlay change.

## 6. Config / environment variables (read by server.js)

- `PORT` — defaults to `8080`. The in-person server uses the same default, so change one of them if both run on one computer (then update the OBS browser-source URLs to match).

## 7. WeBuddhist recitation API

Moved to [`../tara-puja-inperson/HANDOVER.md`](../tara-puja-inperson/HANDOVER.md) §5, with the app-side config and key IDs.

## 8. Content data model (`public/content.json`)

Top level: `{ _README, languages:["bo","en","zh"], lines_per_screen:2, sections:[...] }`.

Section: `{ id, title:{bo,en,zh}, anytime?, verses:[...] }`.

Verse: `{ id, kind, reference, rubric, lines:{bo:[...],en:[...],zh:[...]}, tr, tr_zh, image, title }`.

`sequence.js` chunks each verse's lines into 2-line screens (1 line/screen when a line is long) and merges short Namo/seed openers into the first sloka line.

Sections and verses also carry `app` / `segment_ids` (WeBuddhist app ids). The streaming controller ignores them; they are there so this file keeps the same shape as the in-person copy.

## 9. Controller features

- Tibetan-only operator screen. Left = section menu; Next scrolls down the current section then rolls into the next.
- Right pane = the whole current section as tappable verse lines (paper layout), current line highlighted; tap any line to jump (recover if the umdze skips). Teleprompter auto-scroll keeps the active line in a comfort band, only on advance.
- **Hide overlays** (button or `H`): fades every overlay out without moving the position; press again to bring them back.

## 10. Overlay features (`overlay.html`)

- One per language via `?lang=`. Two lines per screen; long single lines wrap / show one-per-screen. Jomolhari font for Tibetan (fixes Sanskrit-in-Tibetan mantra stacking). Lower-third translucent box, **fixed width** (max 1200px, centered) — an earlier "hug the text" version was reverted because the resizing was distracting (`overlay.html.bak5` has it if wanted).
- **Section-title tab:** small persistent tab at the top-left (flush) of the box, showing the current section title in that overlay's language (falls back en→bo). Stays up continuously, only changes at section boundaries, doesn't fade with lines. **Online/OBS only — does not touch the app.**

## 11. Current state — what works

- ✅ Controller → server.js → OBS overlays (all languages) — local, live.
- ✅ Section-title tab + fixed-width box on overlays.

## 12. What's left to do

1. **Optional polish:** overlay title tab styling, en/zh section titles (most sadhana sections have bo titles only).

App-side work (event ID for the real puja, recitation mapping) is tracked in the in-person handover.

## 13. Gotchas / lessons

- Files here are edited in place on the Mac (`~/Downloads/tara-puja-overlay`). After editing `server.js`, **restart** `node server.js`; after editing `public/*`, **hard-refresh** the browser / OBS source.
- Editing tips used throughout: exact-match string replaces with a uniqueness assert; syntax-check `server.js`/`sequence.js` with `node --check`, and `controller.html`/`overlay.html` inline scripts by extracting the `<script>` and `new Function(...)`.

## 14. Update log — 2026-09-23

Corrections to the picture above, from a live debugging session. (Items A and B — the event 404 and the hosted `wss://` service — were about the app sync and moved to the in-person handover.)

**C. Streaming audio model (Branch Output).** Branch Output does **not** inherit OBS's normal audio — each filter reads a specific audio track and is silent unless (a) its **Custom Audio Source** is enabled and pointed at a track, and (b) that track has a source ticked onto it in **Advanced Audio Properties**. Hearing audio in OBS (program/Track 1) does not mean the branch has it. For this puja **all three streams carry the same Tibetan chant audio** — only the overlays differ by script — so the guide's per-track split (Track 1/2/3) is *optional* for a chant-only event: point all three Custom Audio Sources at one shared, fed track. Keep the per-track routing only if a **teaching phase** with per-language translators is added. After fixing audio, restart that output in the Branch Outputs dock and reload the stream on the phone (YouTube caches the silent lead-in). Full detail: `branch-output-setup-guide.md` §4/§5 + the troubleshooting table.

## 15. Update log — 2026-09-28

**Split streaming from the app.** `server.js` no longer POSTs to the WeBuddhist API and ignores any cues; the controller sends only `{type:"set", index, hidden}`. `emit-test.js` and `t21-segments.json` moved to `../tara-puja-inperson/`.

---
*Written 2026-09-20. Updated 2026-09-23 (event UUID, 404 semantics, wss service, Branch Output audio) and 2026-09-28 (app sync split out). Active copy: `~/Downloads/tara-puja-overlay/`.*
