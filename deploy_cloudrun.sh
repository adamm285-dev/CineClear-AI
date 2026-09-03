#!/usr/bin/env bash
set -e

echo "======================================================"
echo "   CineClear AI - 1-Click Google Cloud Run Deployment"
echo "   Deploying to https://cineclear.pro"
echo "======================================================"
echo ""

if ! command -v gcloud &> /dev/null; then
    echo "[X] Google Cloud SDK (gcloud) is not installed."
    echo "    Please install: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "[*] Building and deploying container to Google Cloud Run (us-central1)..."
echo ""

gcloud run deploy cineclear-ai \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8085 \
  --set-env-vars ENVIRONMENT=production,REQUIRE_JUDGE_AUTH_FOR_UPLOADS=true,JUDGE_ACCESS_KEY=cineclear-judge-2026

echo ""
echo "======================================================"
echo "[PASS] Cloud Run Service Deployed Successfully!"
echo ""
echo "To map custom domain cineclear.pro:"
echo "1. In Google Cloud Console: Cloud Run > Custom Domains > Add Mapping"
echo "2. Select service: cineclear-ai"
echo "3. Add domain: cineclear.pro"
echo "4. Add the 4 provided DNS A-Records at your domain registrar."
echo "======================================================"
