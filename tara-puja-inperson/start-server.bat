@echo off
title Tara Puja - In-Person Controller (keep this window open)
cd /d "%~dp0"

where node >nul 2>nul
if errorlevel 1 (
  echo.
  echo  Node.js is not installed. Install the LTS version from https://nodejs.org
  echo  then double-click start-server.bat again.
  echo.
  pause
  exit /b 1
)
node -e "process.exit(+process.versions.node.split('.')[0] < 18 ? 1 : 0)"
if errorlevel 1 (
  echo.
  echo  Node.js is too old. Install the current LTS version from https://nodejs.org
  echo.
  pause
  exit /b 1
)

echo.
if "%RECITATION_EMIT_SECRET_TOKEN%"=="" set /p RECITATION_EMIT_SECRET_TOKEN=Paste the emit token, then press Enter: 
if "%EVENT_ID%"=="" set /p EVENT_ID=Event ID (just press Enter to use the default): 
if "%RECITATION_EMIT_SECRET_TOKEN%"=="" (
  echo.
  echo  WARNING: no token entered - the WeBuddhist app will NOT follow the controller.
)
echo.

rem Open the controller in the browser a moment after the server starts.
start "" /b powershell -NoProfile -Command "Start-Sleep -Seconds 2; Start-Process 'http://localhost:8080/'"

node server.js

echo.
echo  The server has stopped. Close this window, or double-click start-server.bat to start again.
pause
