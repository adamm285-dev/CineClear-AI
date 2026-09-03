Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "   CineClear AI - 1-Click Google Cloud Run Deployment" -ForegroundColor Cyan
Write-Host "   Deploying to https://cineclear.pro" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Google Cloud SDK (gcloud) is not found in PATH." -ForegroundColor Red
    exit 1
}

# Auto-bind Python 3.13 to prevent Microsoft Store app execution alias intercept
if (Test-Path "C:\Python313\python.exe") {
    $env:CLOUDSDK_PYTHON = "C:\Python313\python.exe"
}

Write-Host "[*] Building and deploying container to Google Cloud Run (us-central1)..." -ForegroundColor Yellow
Write-Host ""

# Parse keys from .env if present
$geminiKey = ""
$parallelKey = ""
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^GEMINI_API_KEY=(.+)$") { $geminiKey = $matches[1].Trim() }
        if ($_ -match "^PARALLEL_API_KEY=(.+)$") { $parallelKey = $matches[1].Trim() }
    }
}

$envVars = "ENVIRONMENT=production,REQUIRE_JUDGE_AUTH_FOR_UPLOADS=true,JUDGE_ACCESS_KEY=cineclear-judge-2026"
if ($geminiKey) { $envVars += ",GEMINI_API_KEY=$geminiKey" }
if ($parallelKey) { $envVars += ",PARALLEL_API_KEY=$parallelKey" }

gcloud run deploy cineclear-ai `
  --source . `
  --region us-central1 `
  --platform managed `
  --allow-unauthenticated `
  --port 8085 `
  --set-env-vars $envVars

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host "[PASS] Cloud Run Service Deployed Successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To map custom domain cineclear.pro:" -ForegroundColor White
    Write-Host "1. In Google Cloud Console: Cloud Run -> Custom Domains -> Add Mapping" -ForegroundColor White
    Write-Host "2. Select service: cineclear-ai" -ForegroundColor White
    Write-Host "3. Add domain: cineclear.pro" -ForegroundColor White
    Write-Host "4. Add the 4 provided DNS A-Records at your domain registrar." -ForegroundColor White
    Write-Host "======================================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[ERROR] Deployment encountered an error. Check gcloud output above." -ForegroundColor Red
}
