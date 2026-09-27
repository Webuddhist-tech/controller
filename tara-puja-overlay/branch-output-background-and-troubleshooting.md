# Puja livestream — background, decisions & troubleshooting

Companion to the setup guide. This holds the *why* — why the architecture is what it is, what was tried and ruled out, and deeper troubleshooting. Not needed to run the stream; useful when something breaks or someone asks "why not just…".

---

## Why one OBS instance (not several)

The whole system runs in a **single** OBS instance because of a macOS limitation: OBS's built-in browser (CEF, which renders the overlays) only initializes in **one OBS app bundle at a time**. Launching a second instance with `--multi` fails with `CEF failed to initialize. Exit code 24`, and all browser sources in that second instance render **black**.

So "one OBS instance per language" is not viable on macOS with a single OBS.app. Everything — all three/four scenes and overlays — lives in one instance, and the **Branch Output** plugin fans each scene out to its own destination. Branch Output keeps streaming a scene even when it isn't the active Program scene, which is what makes simultaneous different-program outputs possible.

## Approaches considered and ruled out

- **Separate OBS instances sharing the camera over NDI.** Abandoned. Only the first-launched instance's overlays worked; the others showed black browser sources (the CEF limit above). What looked like success was the second/third instances displaying the *first* instance's overlay baked into the shared NDI camera feed — not their own. NDI is not part of the final design.
- **Multiple copies of OBS.app (OBS-1.app, OBS-2.app) or Parall.** A valid fallback — separate app bundles get independent CEF — but heavier: triple the app footprint, per-copy updates and permission prompts, and still needs a way to share the camera. Kept only as a last resort; not used.
- **obs-multi-rtmp (sorayuki).** Works and can send a different scene per output, but its macOS builds lag OBS releases and needed the OBS-32 arm64 build. Branch Output was chosen instead — more current, actively maintained, and reviewed as more stable.
- **Aitum Multistream / Vertical.** Multistream fans the *same* program to many destinations (not different scenes). Aitum Vertical adds extra canvases, but that's a "one program per canvas" model — more setup for three arbitrary programs than Branch Output's one-filter-per-scene.
- **Source Record.** Record-to-file oriented, not a live RTMP streamer, with a weaker stability record. Not the right tool.

## YouTube multi-broadcast — the full picture

- The instant **"Go Live"** button runs exactly one broadcast and keeps reopening it; it can't do concurrency.
- Concurrent streams must be **separate scheduled broadcasts** (Content → Live), each with its **own distinct stream key**. As of a 2026 change, YouTube enforces a "shared ingestion concurrency" limit — multiple live streams on one key get blocked or merged.
- A channel can run roughly **10 concurrent streams** (2026, enforcement uneven). Scheduled broadcasts **may overlap in time** — that's the supported case.
- Facebook typically allows **one live video per Page** simultaneously, so multiple Facebook streams need multiple Pages/events.

## Bandwidth math

**per-stream bitrate ≈ (upload × 0.7) ÷ number of streams.** Three YouTube streams at 6000 Kbps ≈ 18 Mbps up; six (YouTube + Facebook) at 5000 ≈ 30 Mbps. A puja is low-motion, so lower bitrates look clean. The venue uplink — wired, not Wi-Fi — sets the quality ceiling; confirm it before the event.

## Troubleshooting (symptom → cause → fix)

| Symptom | Cause | Fix |
|---------|-------|-----|
| Second OBS instance: black overlays, `Exit code 24` | macOS CEF is one-per-bundle | Run everything in one instance |
| Overlay black on an inactive scene | Browser source unloaded | Uncheck "Shutdown source when not visible" |
| Only one language's overlay on every stream | Overlays baked into a shared camera feed, or same scene on all filters | One scene + one overlay + one filter per language |
| Output silent (audio bitrate 0) | No Custom Audio Source, or the track has no source feeding it | Enable Custom Audio Source → a fed track; tick the source onto that track in Advanced Audio Properties |
| Two YouTube streams show as one / same name | Shared stream key | One distinct key per broadcast |
| Can't start a 2nd YouTube stream | Using the instant "Go Live" button | Create separate scheduled broadcasts (Content → Live) |
| "keyframes not sent often enough (8.3s)" | Keyframe Interval = 0/auto | Set to 2, then stop/start that output |
| Keyframe still 8.3s after setting 2 | Changing the Video Encoder reset Keyframe Interval to 0 | Re-set to 2 *after* choosing the encoder, Apply, restart output |
| "not receiving enough video" / buffering | Upload or encode ceiling | Lower bitrate; use Apple VT hardware encoder |
| "bitrate lower than recommended (6800)" | Informational only | Ignore for low-motion content |
| Camera won't appear in a second scene | Device can only be grabbed once | Add once, Paste (Reference) into other scenes |

## Environment reference

- OBS Studio 32.2.2 (native arm64) · Branch Output v1.0.9 (OPENSPHERE) · macOS 26.6
- Proof-of-concept on MacBook Air M3; event on **M5 MacBook Air (16 GB)**. Fanless — the Apple VT hardware encoder keeps load off the CPU, so multi-stream encoding stays cool, but keep it on power and ventilated for a multi-hour run.
- Overlay system: `~/tara-puja-overlay` — Node server on `localhost:8080`, WebSocket controller drives all overlays in sync, one browser source per language.
- Scene collection JSON (for moving machines): `~/<userDir>/basic/scenes/`.

## Sources

- Branch Output (streams inactive scenes; Paste Reference; recording): https://github.com/OPENSPHERE-Inc/branch-output · https://obsproject.com/forum/resources/branch-output-streaming-recording-filter-for-source-scene.1987/
- Browser source stops rendering off-program: https://github.com/obsproject/obs-studio/issues/6074
- Capture device grabbed once: https://obsproject.com/forum/threads/one-webcam-in-multiple-scenes-seems-not-be-possible.119967/
- YouTube concurrent streams / distinct keys (2026): https://alanspicer.com/how-to-have-multiple-livestreams-on-one-youtube-channel/ · https://developers.google.com/youtube/v3/live/broadcasts-and-streams
- Ingest URLs: https://support.google.com/youtube/answer/2907883 · https://www.facebook.com/help/587160588142067
