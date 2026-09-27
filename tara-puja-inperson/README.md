# Tārā Puja — In-Person Controller

## Setup (one time)

Install **Node.js LTS** from https://nodejs.org with the default options. Keep this whole folder together, including `node_modules`.

## Start

Double-click **`start-server.bat`**, paste the emit token, and press Enter twice. The controller opens at **http://localhost:8080/**.

Or type one of these, replacing `paste-token-here` with the token.

**PowerShell:**
```powershell
cd $HOME\Desktop\tara-puja-inperson; $env:RECITATION_EMIT_SECRET_TOKEN="paste-token-here"; node server.js
```

**Command Prompt:**
```bat
cd /d %USERPROFILE%\Desktop\tara-puja-inperson && set RECITATION_EMIT_SECRET_TOKEN=paste-token-here&& node server.js
```
In the Command Prompt version, keep `&&` right after the token, with no space.

The window must say **`App emit: ON`**. Keep it open for the whole event.

If the event isn't the default one, paste its ID when `start-server.bat` asks, or add it to the typed command the same way:
- **PowerShell:** `$env:EVENT_ID="3f3f8083-b32a-4628-b190-d249969e95db";` before `node server.js`
- **Command Prompt:** `set EVENT_ID=3f3f8083-b32a-4628-b190-d249969e95db&& ` before `node server.js`

## Troubleshooting

| Problem | Fix |
|---|---|
| `'node' is not recognized` | Install Node.js, then restart the computer. |
| Says `App emit: OFF` | No token was entered. Close the window and start again. |
| `EADDRINUSE` / port in use | A copy is already running. Close all black windows and start again. |
| Controller says **reconnecting…** | The black window was closed. Start it again; the controller picks up where it was. |
| App doesn't scroll | In the black window, `emit 401` means the token is wrong. `emit 404` means the event isn't found or isn't published. `emit 429` means more than one controller is open. |
| Tibetan shows boxes | The computer needs internet access for the font. |
