# WeBuddhist puja controller

Two separate versions of the Tārā puja controller. Each one runs on its own.

- **[`tara-puja-overlay/`](tara-puja-overlay/)**: **streaming / OBS only.** The operator controller drives the burned-in text overlays (Tibetan, English and Chinese) for the livestream. It does **not** connect to the WeBuddhist app.
  Run `node server.js`, then open `http://localhost:8080/controller.html`. The OBS browser sources are `http://localhost:8080/overlay.html?lang=bo` (and `en`, `zh`). See [`branch-output-setup-guide.md`](tara-puja-overlay/branch-output-setup-guide.md) for the OBS setup.
- **[`tara-puja-inperson/`](tara-puja-inperson/)**: **in-person / app only.** There are no overlays. The controller moves the WeBuddhist app, one click per segment. See its [README](tara-puja-inperson/README.md) for Windows setup.

For an event that is streamed and also followed in the app, run both. Both servers default to port 8080, so on one computer start one of them on another port, for example `PORT=8081 node server.js`.

The emit token (in-person version only) is **never** stored in this repo. Supply it at start-up with the `RECITATION_EMIT_SECRET_TOKEN` environment variable, or paste it when `start-server.bat` asks.
