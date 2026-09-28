# WeBuddhist puja controller

Two separate Tārā puja controllers, one per output:

- **[`tara-puja-overlay/`](tara-puja-overlay/)**: streaming version. The operator controller drives the OBS text overlays (Tibetan, English and Chinese) only. It never contacts the WeBuddhist app.
  Run `node server.js`, then open `http://localhost:8080/controller.html`. The OBS browser sources are `http://localhost:8080/overlay.html?lang=bo` (and `en`, `zh`).
- **[`tara-puja-inperson/`](tara-puja-inperson/)**: in-person version, with no overlays. The controller moves the WeBuddhist app only, one click per segment. See its [README](tara-puja-inperson/README.md) for Windows setup.

For an event that is streamed and also followed in the app, run both, each with its own controller. Both servers default to port 8080, so on one computer start one of them on another port, for example `PORT=8081 node server.js`.

Only the in-person server needs the emit token, and it is **never** stored in this repo. Supply it at start-up with the `RECITATION_EMIT_SECRET_TOKEN` environment variable (or paste it when `start-server.bat` asks).
