@echo off
setlocal enabledelayedexpansion

echo ======================================================
echo    CineClear AI - 1-Click Google Cloud Run Deployment
echo    Deploying to https://cineclear.pro
echo ======================================================
echo.

where gcloud >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [X] Google Cloud SDK (gcloud) is not installed or not on PATH.
    echo     Please install the Google Cloud SDK: https://cloud.google.com/sdk/docs/install
    exit /b 1
)

echo [*] Building and deploying container to Google Cloud Run (us-central1)...
echo.

gcloud run deploy cineclear-ai ^
  --source . ^
  --region us-central1 ^
  --platform managed ^
  --allow-unauthenticated ^
  --port 8085 ^
  --set-env-vars ENVIRONMENT=production,REQUIRE_JUDGE_AUTH_FOR_UPLOADS=true,JUDGE_ACCESS_KEY=cineclear-judge-2026

if %ERRORLEVEL% equ 0 (
    echo.
    echo ======================================================
    echo [PASS] Cloud Run Service Deployed Successfully!
    echo.
    echo To map custom domain cineclear.pro:
    echo 1. In Google Cloud Console: Cloud Run ^> Custom Domains ^> Add Mapping
    echo 2. Select service: cineclear-ai
    echo 3. Add domain: cineclear.pro
    echo 4. Add the 4 provided DNS A-Records at your domain registrar.
    echo ======================================================
) else (
    echo.
    echo [X] Deployment encountered an error. Check gcloud output above.
)
