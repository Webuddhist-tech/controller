# Multi-language puja livestream — OBS setup guide

How to stream the puja in each language — Tibetan, English, Chinese (and Hindi if added) — to multiple YouTube channels and Facebook, all from **one** copy of OBS on **one** computer. One camera, one overlay controller, one operator.

*Companion reference (background, alternatives, deeper troubleshooting) lives in `branch-output-background-and-troubleshooting.md`. You don't need it to follow this guide.*

---

## Topology — OBS (local, on one Mac) + Castr (cloud)

Two layers, and they do different jobs:

- **OBS** is the **compositor + encoder**. It burns the live per-language overlays onto the camera, producing **3 distinct video programs** (bo / en / zh), and encodes each. This *must* be OBS — nothing else renders the WebSocket-driven overlays. It runs on **one Mac** (the same Mac as `server.js`, because the overlays load from `localhost:8080`).
- **Castr** is the **cloud distribution layer**. OBS sends each language up to Castr **once**; Castr fans that language out to all its channels. There is **no second computer** — Castr is a cloud service you configure in a browser; nothing installs or "runs" locally.

```
ONE Mac                                          Castr cloud            Destinations
─────────────────────────────────────           ───────────            ────────────────────
node server.js (localhost:8080)
controller.html  ─ operator drives ─┐
                                    ▼
OBS (one instance)
  Tibetan scene  = camera + overlay(bo) ─Branch Output─▶ Castr-Tibetan ─▶ Main YT + Client-2 YT + Main FB
  English scene  = camera + overlay(en) ─Branch Output─▶ Castr-English ─▶ Main YT + Client-2 YT
  Chinese scene  = camera + overlay(zh) ─Branch Output─▶ Castr-Chinese ─▶ Main YT + Client-2 YT
```

**Destination matrix** (this event): 3 OBS uploads → 7 destinations, all multiplied by Castr in the cloud.

| OBS composite | → Castr stream | Castr fans out to |
|---|---|---|
| **Tibetan** | Castr-Tibetan | Main-client YT + Client-2 YT + Main-client **Facebook** (3) |
| **English** | Castr-English | Main-client YT + Client-2 YT (2) |
| **Chinese** | Castr-Chinese | Main-client YT + Client-2 YT (2) |

**Why this is the right shape:** within a language it's the *same* video going to multiple channels, which is exactly what a cloud multistreamer is for. You upload **3 streams** from the venue instead of 7 — Castr does the multiplication — so the uplink is the win, not extra hardware.

> This is the **online-viewer** path only. In-person attendees use the WeBuddhist app's text-scroll, which is driven by the **separate** `tara-puja-inperson` controller, not by this one. It's unaffected by OBS or Castr.

---

## What you need

- **OBS Studio** (Apple Silicon build) with the **Branch Output** plugin installed.
- The **overlay system** in `~/tara-puja-overlay` (Node server + controller + per-language overlays).
- The **camera** (Logitech C920) and your **audio source(s)**.
- A **Castr account** (the client's) with enough plan headroom for **3 concurrent source streams** and the **total destination count** (7 here) — both are plan-tiered, so confirm before event day. The destination YouTube channels and Facebook page must be connected in Castr (see Step 6).
- A **wired internet connection** at the venue.
- The event runs on an **M5 MacBook Air (16 GB)**.

> ⚠️ The MacBook Air is fanless. For a multi-hour event, keep it **plugged into power** and **well-ventilated** (hard surface, cool room), and close other apps. The hardware encoder in Step 5 keeps heat low, but don't run it on a bed/couch or let the room get hot.

**Before you open OBS:** start the overlay server first —

```bash
cd ~/tara-puja-overlay
node server.js
```

Leave it running. The controller is at `http://localhost:8080/controller.html`.

---

## Step 1 — Install Branch Output

1. Download the macOS **Apple Silicon (arm64)** package from the [Branch Output plugin page](https://obsproject.com/forum/resources/branch-output-streaming-recording-filter-for-source-scene.1987/).
2. Quit OBS, run the installer, reopen OBS.
3. Open **Docks → Branch Outputs**. This dock starts, stops, and monitors every output. Keep it visible.

## Step 2 — One scene per language, one shared camera

1. Create three scenes: **Tibetan**, **English**, **Chinese** (add **Hindi** if needed).
2. In the Tibetan scene, add **Video Capture Device** → the C920. Name it `Camera-C920`.
3. Right-click `Camera-C920` → **Copy**. In each other scene, right-click Sources → **Paste (Reference)**.

> ⚠️ Use **Paste (Reference)**, not a new Video Capture Device — the camera can only be opened by one source.

## Step 3 — Add the overlays

1. In each scene, add a **Browser Source** as the top layer:
   - Tibetan → `http://localhost:8080/overlay.html?lang=bo`
   - English → `...?lang=en`
   - Chinese → `...?lang=zh` (Hindi → `...?lang=hi`)
2. Set each to **1920×1080**.
3. In each browser source's **Properties**, **uncheck "Shutdown source when not visible."**

> ⚠️ The "Shutdown source when not visible" box must be **unchecked** on every overlay, or the two scenes you're not currently viewing will go black on their streams.

## Step 4 — Route the audio

Each language stream reads its own **audio track**. Set this up in the mixer's **Advanced Audio Properties** (gear icon → Advanced Audio Properties), where each audio source has checkboxes for Tracks 1–6.

| Track | Stream | Chanting phase | Teaching phase |
|-------|--------|----------------|----------------|
| 1 | Tibetan | Tibetan chant | Rinpoche (Tibetan) |
| 2 | English | Tibetan chant | English translator |
| 3 | Chinese | Tibetan chant | Chinese translator |
| 4 | Hindi *(opt.)* | Tibetan chant | Hindi translator |

- **Chanting:** the Tibetan feed goes to every stream — tick it onto Tracks 1, 2, 3 (and 4). Overlays differ so viewers chant along; the audio is the same everywhere.
- **Teaching:** each translator leads its own stream. Bring up the translator on its track; keep the Tibetan feed as a quiet bed underneath, or drop it from tracks 2–4 so only the translator is heard.

> ⚠️ Every stream's audio must come from a track that actually has a source feeding it. If a track is empty, that stream goes out **silent** (audio bitrate 0 on YouTube). During a single-source test, tick your one source onto Tracks 1, 2, and 3.

## Step 5 — Add a Branch Output filter to each scene

Right-click a scene → **Filters** → **+** → **Branch Output**. Configure:

**Streaming** — check it, then:
- **Stream Count:** `1`. With Castr you send each language up **once**; Castr fans it out to every channel, so OBS never needs Stream Count 2+ (that was only for the old direct-to-YouTube-and-Facebook path).
- **Streaming 1 Server / Stream Key:** this language's **Castr ingest URL + Stream Key** (Step 6), *not* YouTube's. Leave **"Use authentication" unchecked**.

**Custom Audio Source** — check it and select this language's **Audio Track** (Tibetan → Track 1, English → Track 2, Chinese → Track 3).

**Video Encoder:**
- **Video Source:** `Independent Mix (Default)`
- **Video Encoder:** `Apple VT H264 Hardware`
- **Bitrate:** from the bandwidth formula in Step 8.
- **Keyframe Interval:** `2`
- **Resolution / Frame Rate:** 1080p is fine; 720p and/or 30 fps (Frame Rate Divider 1/2) reduce load and bandwidth, and are plenty for a puja.

**Audio Encoder:** AAC, 160 Kbps.

**Advanced Settings:** leave **"Blank output when source is not in Main Output" unchecked**.

Click **Apply**. Repeat for each scene.

> ⚠️ Set **Keyframe Interval to 2 *after* you've selected the Apple VT encoder** — changing the encoder resets it to 0. If you change any encoder setting on a running output, **stop and restart that output** (Branch Outputs dock) so the change takes effect.

## Step 6 — Set up the 3 Castr streams + their destinations

You make **one Castr Live Stream per language**. Each gives you an ingest OBS points at, and holds the list of channels Castr pushes to.

1. In the Castr dashboard, create **3 Live Streams**: name them clearly — `Puja — Tibetan`, `Puja — English`, `Puja — Chinese`.
2. For each stream, open its **Stream source / Encoder setup** panel — Castr shows an **RTMP ingest URL + Stream Key**. This pair goes into the matching scene's Branch Output (Step 5): Tibetan scene → Castr-Tibetan ingest, etc.
3. For each stream, add its **Platforms / Destinations** (*Add Platform / Add Destination*) — connect each YouTube channel (sign in to that channel) or Facebook page, or use **Custom RTMP** with that channel's own stream key. Add every channel a language must reach to that one stream; Castr multistreams to all of them:
   - **Tibetan** → Main-client YouTube, Client-2 YouTube, Main-client Facebook
   - **English** → Main-client YouTube, Client-2 YouTube
   - **Chinese** → Main-client YouTube, Client-2 YouTube
4. On **YouTube**, each connected channel still needs a live broadcast to receive the feed — Castr can create/manage these when you connect the channel; confirm each shows the incoming stream before going live. Two *different* YouTube channels = two separate destinations in Castr (each signed in to its own channel), never one key reused.

> ⚠️ Two YouTube channels must be **two distinct destinations / keys** in Castr. A reused key collapses them into one stream (same rule as the old direct path, just enforced in Castr now).

**Fallback (Castr down):** the old direct path still works — point each Branch Output at YouTube (`rtmp://a.rtmp.youtube.com/live2`) / Facebook (`rtmps://live-api-s.facebook.com:443/rtmp/`) with per-broadcast keys and Stream Count 2 for a scene that also needs Facebook. Heavier (up to 7 uploads from the venue) and no cloud fan-out, but no client dependency. Keep the keys handy as a break-glass option.

## Step 7 — Facebook (Tibetan only)

Facebook is just another **destination on the Castr-Tibetan stream** — add it in Step 6, no change in OBS. Connect the page in Castr (or Custom RTMP from **Facebook Live Producer → Streaming software**).

- Facebook usually allows **one live video per Page at a time**, so if more languages ever go to Facebook, each needs its own Page/event.

## Step 8 — Set the bitrate for your connection

> **per-stream bitrate ≈ (upload speed × 0.7) ÷ number of streams**

With Castr you upload **only 3 streams** from the venue (one per language) no matter how many channels each is fanned to — the multiplication happens in Castr's cloud. So the divisor is **3**, not 7. Example: 20 Mbps upload → ~4.5 Mbps each; 30 Mbps → ~7 Mbps each. Use a **wired** connection. (Without Castr, the same matrix would be 7 uploads — the main reason Castr is worth it here.)

> ⚠️ If YouTube reports "not receiving enough video" or buffering, your bitrate is above what the connection can carry — lower it. A message that your bitrate is *below* the recommended 6800 is only an FYI and safe to ignore for this content.

## Step 9 — Go live

1. Start `node server.js`, then open OBS.
2. In the **Branch Outputs dock**, start all outputs.
3. In YouTube, open each broadcast from **Content → Live** and confirm it shows **"Excellent."** Click **Go Live** on each.
4. Advance the **controller** — confirm all overlays move together.

**Pre-flight check per stream:**
- ☐ Correct overlay language on screen
- ☐ Audio present (not silent)
- ☐ Stream health "Excellent," no keyframe warning
- ☐ Overlay advances with the controller

> ⚠️ **Quick fixes if a stream looks wrong:**
> - **Silent** → that scene's audio track has no source feeding it (Step 4).
> - **Keyframe warning** → set Keyframe Interval to 2 *after* the encoder, restart the output (Step 5).
> - **Buffering / "not enough video"** → lower the bitrate (Step 8).
> - **Two YouTube channels look like one** → each needs its own distinct destination/key in Castr (Step 6).
> - **A channel is dark but Castr shows the stream arriving** → the problem is that channel's destination in Castr, not OBS — reconnect it in the Castr dashboard; OBS keeps running.

---

## Step 10 — Dry run with Castr (do this on a test day, NOT first at the event)

Learn Castr incrementally with **one** language before wiring all three. Each step proves one thing.

1. **Prove OBS → Castr.** In Castr, create the `Puja — Tibetan` stream, copy its ingest URL + key into the Tibetan scene's Branch Output (Step 5). Start `node server.js`, open OBS, start that one output in the **Branch Outputs dock**. In the Castr dashboard the stream should show **"live / receiving."** If it doesn't, the ingest URL/key or the output is wrong — fix this before anything else.
2. **Prove one destination.** Add **one** YouTube channel as a destination on that Castr stream. Use an **unlisted/private** test broadcast. Confirm video *and* audio arrive on that channel (watch on your phone). This also re-checks the audio routing (Custom Audio Source → a fed track, Step 4).
3. **Prove fan-out.** Add a **second** destination to the *same* Castr stream (the other channel, or a second unlisted test target). Confirm both light up from the one OBS upload. This is the whole point of Castr — see it work once.
4. **Prove 3 concurrent.** Start the English and Chinese outputs too (each to its own Castr stream). Confirm all three run together and each carries the right overlay language. Watch the venue upload — it should be ~3 streams' worth, not 7.
5. **Prove the controller.** Advance `controller.html`; confirm all overlays move together.
6. **Note the numbers you'll reuse:** which Castr stream = which language, each stream's ingest, and each channel's destination. Screenshot the Castr dashboard layout.

> Time this dry run end-to-end once; a multi-hour puja is not the moment to first meet Castr's UI.

## Step 11 — Backup laptop (optional but recommended for a client event)

Castr is cloud, so it needs no second machine — but a **standby Mac** protects against the primary dying or its uplink dropping mid-puja. It is a cold spare, not part of the live path:

- Pre-install OBS + Branch Output, copy the scene collection JSON (`~/<userDir>/basic/scenes/`) and the `tara-puja-overlay` folder.
- Same overlay setup (browser sources at `localhost:8080`, `node server.js` runnable).
- Have the Castr ingest URLs/keys and the camera ready to move. Only one machine can grab the camera at a time, so this is a *switch-over*, not simultaneous.
- If the primary fails: stop it, move the camera, start `server.js` + OBS on the spare, restart the Branch Outputs to the same Castr ingests. Castr and all destinations keep their config — they just start receiving again.
