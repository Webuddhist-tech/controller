# WeBuddhist puja controller

Two versions of the Tārā puja controller:

- **[`tara-puja-overlay/`](tara-puja-overlay/)**: streaming version. The operator controller drives the OBS text overlays (Tibetan, English and Chinese) and the WeBuddhist app.
  Run `node server.js`, then open `http://localhost:8080/controller.html`. The OBS browser sources are `http://localhost:8080/overlay.html?lang=bo` (and `en`, `zh`).
- **[`tara-puja-inperson/`](tara-puja-inperson/)**: in-person version, with no overlays. The controller moves the WeBuddhist app only, one click per segment. See its [README](tara-puja-inperson/README.md) for Windows setup.

The emit token is **never** stored in this repo. Supply it at start-up with the `RECITATION_EMIT_SECRET_TOKEN` environment variable (or paste it when `start-server.bat` asks).
