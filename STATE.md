# CineClear AI - Current System State & Operational Runbook (STATE.md)

**Last Updated:** September 6, 2026  
**Status:** 🟢 **LIVE ON PRODUCTION** — cineclear.pro (Cloud Run `us-central1`)  
**Repository:** [https://github.com/adamm285-dev/CineClear-AI](https://github.com/adamm285-dev/CineClear-AI)  
**Demo video:** [https://www.youtube.com/watch?v=PgOzgVUBNso](https://www.youtube.com/watch?v=PgOzgVUBNso)

---

## 1. Live Environment & System Topology

| Parameter | Current Value | Notes |
| :--- | :--- | :--- |
| **Public studio** | `https://cineclear.pro` | Custom domain on Cloud Run service `cineclear-ai`. |
| **Judge VIP URL** | `https://cineclear.pro?access=cineclear-judge-2026` | One-click pass. No account. Header pill must read Judge VIP Active. |
| **FastAPI** | `0.0.0.0:8085` | Local: `python server.py`. Production container `CMD python server.py`. |
| **Gemini** | `gemini-3.8-flash` (preferred) | Cascade tries **2** live tiers then local harness. Ladder: 3.8-flash → 3.5-flash → 3.5-flash-lite → 3.6-flash → gemini-flash-latest. |
| **Parallel Search** | `https://api.parallel.ai/v1/search` | Live objective search; statutory corpus fallback if HTTP non-200. |
| **Audit transport** | `POST /api/audit/stream` (SSE) | Dashboard uses SSE. `POST /api/audit` remains JSON for CLI/tests. |
| **Auth** | `REQUIRE_JUDGE_AUTH_FOR_UPLOADS=true` | **All** live audits (samples + uploads) require `X-Judge-Access` / `?access=`. |
| **Quota shield** | 12 live audits / hour / IP | In-memory limiter on `/api/audit` and `/api/audit/stream`. |
| **TOS** | `/terms` version `2026-09-06` | Un-skippable UI gate. Decision-support only. $0 LoL on free/hackathon tier. |
| **Retention** | `app/retention.py` | User files under `uploads/` deleted when the audit finishes. Samples never deleted. |
| **Telemetry** | `app/telemetry.py` | Judge trace console: live `generateContent` and Parallel POST lines. |

---

## 2. Pipeline (what actually runs)

1. **Stage 1 — Extract** (`VisionAgent`): Gemini multimodal still / OpenCV keyframes (gathered) / PyMuPDF+Gemini script. `ExtractorHarness` dedupes.
2. **Stage 2 — Ground** (`asyncio.as_completed`): each flag Parallel Search **then** Gemini synthesis, concurrent across flags.
3. **Stage 3 — Critic** (`CineClearAuditor` + `CriticHarness`): statutory invariants (no modern TM as public domain; phones → CRITICAL).
4. **Stage 4 — Dispatch**: Form-4A drafts, VFX orders, NANPA fixes, cue sheet, ReportLab **evidence dossier** (counsel sign-off, not a certificate).

UI progress balls follow these four stages via SSE. Exports POST the completed JSON to `/api/export/pdf` and `/api/export/edl` so Cloud Run instance affinity is not required.

---

## 3. Component Notes (honest)

| Component | Status | Reality vs old SLA |
| :--- | :--- | :--- |
| Sample PDF/JPG/TXT ensure | 🟢 | `ensure_sample_media()` on startup and sample audit (PDF was gitignored historically). |
| Live Gemini extract | 🟢 | Wall clock often **8–25s** per extract, not 1–3s. |
| Parallel + Gemini per flag | 🟢 | Concurrent; 8s Parallel timeout; 8s Gemini timeout; 2 cascade tiers. |
| SSE progress + judge trace | 🟢 | Padded `text/event-stream` so Chrome/Cloud Run flush. |
| PDF / EDL export | 🟢 | Client blob download from report JSON. |
| Favicon | 🟢 | `/favicon.ico` + `static/favicon.svg`. |

Do **not** quote “sub-5-second E2E” in judge materials. Live partner APIs dominate latency.

---

## 4. Security & UPL (current)

* Language: **decision-support / counsel-review dossier**. Never “cleared for distribution.”
* PDF page chrome + `/terms` + results banner match that boundary. Sign-off is **licensed production attorney / E&O broker**.
* Random visitors: landing page only. Audits **401** without VIP pass (JS no longer auto-injects the key).
* Judge pass is public in the README (evaluators need it). Rate limit is the quota backstop.

---

## 5. Runbook

### Local
```powershell
cd C:\Users\adamm_000\Desktop\CineClearAi
python server.py
# http://localhost:8085?access=cineclear-judge-2026
```

### Tests
```powershell
python -m pytest tests/ -q
```
Modules: `test_auditor`, `test_cascade`, `test_edl_exporter`, `test_fair_use`, `test_harness`, `test_models`, `test_music_arch`, `test_parallel_client`, `test_remediation`, `test_retention`, `test_server`.

### Production deploy
```powershell
.\deploy_cloudrun.ps1
```
Sets `ENVIRONMENT=production`, `REQUIRE_JUDGE_AUTH_FOR_UPLOADS=true`, `JUDGE_ACCESS_KEY=cineclear-judge-2026`, plus Gemini/Parallel keys from `.env`.

### Judge evaluate path
1. [https://cineclear.pro?access=cineclear-judge-2026](https://cineclear.pro?access=cineclear-judge-2026)  
2. Accept TOS.  
3. 4K STILL (then PDF SCRIPT / TXT).  
4. Confirm GEMINI + PARALLEL lines in the judge trace.  
5. Export PDF + EDL.
