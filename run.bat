@echo off
title CineClear AI - Studio Server
echo ========================================================================
echo    CINECLEAR AI // AGENTIC HOLLYWOOD LEGAL & E&O CLEARANCE SYSTEM       
echo ========================================================================
echo.
echo [*] Starting CineClear AI Web Server on http://localhost:8085 ...
echo [*] Opening browser in 2 seconds...
echo.

cd /d "%~dp0"

REM Open browser after 2 seconds in background
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:8085"

REM Start server
python server.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Server exited with an error.
    pause
)
