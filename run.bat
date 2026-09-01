@echo off
title CineClear AI - 1-Click Studio Launcher
cd /d "%~dp0"

echo ========================================================================
echo    CINECLEAR AI // AGENTIC HOLLYWOOD LEGAL & E&O CLEARANCE SYSTEM       
echo ========================================================================
echo.

REM 1. Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] ERROR: Python 3.10+ is not found on your PATH.
    echo     Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 2. Create virtual environment if not present
if not exist ".venv" (
    echo [*] Initializing isolated virtual environment (.venv)...
    python -m venv .venv
)

REM 3. Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM 4. Execute 1-Click Auto-Deployer
python deploy.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Server exited. Press any key to close this window.
    pause
)
