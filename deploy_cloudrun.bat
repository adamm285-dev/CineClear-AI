@echo off
setlocal

echo ======================================================
echo    CineClear AI - 1-Click Google Cloud Run Deployment
echo    Deploying to https://cineclear.pro
echo ======================================================
echo.

where gcloud >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Google Cloud SDK is not installed or not on PATH.
    echo Please install Google Cloud SDK: https://cloud.google.com/sdk/docs/install
    exit /b 1
)

if exist "C:\Python313\python.exe" set CLOUDSDK_PYTHON=C:\Python313\python.exe

echo [*] Building and deploying container to Google Cloud Run...
echo.

gcloud run deploy cineclear-ai --source . --region us-central1 --platform managed --allow-unauthenticated --port 8085 --set-env-vars ENVIRONMENT=production,REQUIRE_JUDGE_AUTH_FOR_UPLOADS=true,JUDGE_ACCESS_KEY=cineclear-judge-2026

if %ERRORLEVEL% equ 0 (
    echo.
    echo ======================================================
    echo [PASS] Cloud Run Service Deployed Successfully!
    echo.
    echo To map custom domain cineclear.pro:
    echo 1. In Google Cloud Console: Cloud Run -^> Custom Domains -^> Add Mapping
    echo 2. Select service: cineclear-ai
    echo 3. Add domain: cineclear.pro
    echo 4. Add the 4 provided DNS A-Records at your domain registrar.
    echo ======================================================
) else (
    echo.
    echo [ERROR] Deployment encountered an error. Check output above.
)
