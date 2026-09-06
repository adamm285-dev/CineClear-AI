# Implementation Plan - CineClear AI: Agentic Film & TV Legal Clearance System

CineClear AI is an end-to-end agentic legal clearance and E&O (Errors & Omissions) insurance verification system for film, television, and commercial productions. It combines **Gemini Multimodal Vision & Audio Intelligence** with **Parallel Search Web-Grounding** to detect, research, and mitigate legal liabilities (trademarks, copyrighted art, architectural rights, defamatory names, and real phone numbers) before distribution.

## Proposed Architecture & File Structure

```
CineClearAi/
├── .env.example                     # Environment template (Gemini API, Parallel API, Server config)
├── requirements.txt                 # Project dependencies
├── README.md                        # Complete documentation, architecture, API & CLI guide
├── main.py                          # CLI and batch analysis entrypoint
├── server.py                        # FastAPI web server, REST API & interactive dashboard
├── app/
│   ├── __init__.py
│   ├── config.py                    # Pydantic Settings & environment manager
│   ├── models.py                    # Pydantic schemas (RiskLevel, ClearanceCategory, ParallelVerification, ClearanceFlag, ClearanceAuditReport)
│   ├── parallel_client.py           # Parallel Search API client with live search & resilient fallback mock
│   ├── vision_agent.py              # Gemini Multimodal parser for video frames, still photos, and script PDFs
│   ├── auditor.py                   # CineClearAuditor multi-turn legal reasoning & Parallel verification loop
│   └── report_generator.py          # ReportLab cinema-grade E&O Clearance Binder PDF generator
├── static/                          # Modern cinematic web UI assets (CSS, JS, icons)
│   ├── index.html                   # Interactive cinema studio dark-mode dashboard
│   ├── style.css                    # Polished film production aesthetics
│   └── app.js                       # Live upload, async analysis pipeline, filterable flag cards & PDF export
├── sample_media/                    # Bundled test footage stills, set photos, and sample script excerpts
│   ├── sample_set_photo.jpg         # Sample production still containing logo & art liabilities
│   ├── sample_screenplay.txt        # Sample screenplay excerpt with PII/phone & brand mentions
│   └── sample_screenplay.pdf        # Generated PDF script excerpt
└── tests/                           # Comprehensive test suite
    ├── __init__.py
    ├── test_models.py               # Schema and validation tests
    ├── test_parallel_client.py      # Parallel search client unit tests
    ├── test_auditor.py              # Clearance audit & reasoning tests
    └── test_report_generator.py     # PDF binder generation tests
```

---

## Proposed Changes & Components

### 1. Core Configuration & Data Models
#### [NEW] [requirements.txt](file:///c:/Users/adamm_000/Desktop/CineClearAi/requirements.txt)
- Define all required packages (`google-genai`, `google-generativeai`, `pydantic`, `pydantic-settings`, `requests`, `httpx`, `fastapi`, `uvicorn`, `python-multipart`, `pillow`, `opencv-python-headless`, `reportlab`, `python-dotenv`, `jinja2`, `pytest`).

#### [NEW] [.env.example](file:///c:/Users/adamm_000/Desktop/CineClearAi/.env.example)
- Configuration template for `GEMINI_API_KEY`, `GEMINI_MODEL`, `PARALLEL_API_KEY`, `PARALLEL_BASE_URL`, `HOST`, `PORT`, `ENVIRONMENT`.

#### [NEW] [app/config.py](file:///c:/Users/adamm_000/Desktop/CineClearAi/app/config.py)
- Pydantic `BaseSettings` loading `.env` variables with graceful fallbacks and API key validation.

#### [NEW] [app/models.py](file:///c:/Users/adamm_000/Desktop/CineClearAi/app/models.py)
- Complete legal clearance schemas:
  - `RiskLevel`: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`
  - `ClearanceCategory`: `TRADEMARK_LOGO`, `COPYRIGHTED_ART`, `ARCHITECTURAL_RIGHTS`, `MUSIC_AUDIO`, `NAME_DEFAMATION`, `PHONE_PII`
  - `ParallelVerification`: Search objective, sources checked, public domain flag, active trademark flag, rights holder, statutory context
  - `ClearanceFlag`: Timestamp/page, category, detected entity, visual description, risk level, verification, actionable mitigation
  - `ClearanceAuditReport`: Project title, filename, flag counts, itemized flags, timestamp
  - `AuditRequest` & `AuditResponse` schemas for API and CLI integration.

---

### 2. Parallel Search Client & Web Grounding
#### [NEW] [app/parallel_client.py](file:///c:/Users/adamm_000/Desktop/CineClearAi/app/parallel_client.py)
- Asynchronous `ParallelSearchClient` interacting with `https://api.parallel.ai/v1/search`.
- Structured search queries targeted for USPTO trademark status, copyright catalog entries, public domain expiration (pre-1929 rule / life + 70 years), architectural works copyright status (17 U.S.C. § 120), and music publishing/sync rights.
- Built-in resilient offline/demo mock database of common real-world trademarks and public domain assets so the entire app works seamlessly out of the box even before custom keys are entered.

---

### 3. Multimodal Vision & Script Agent
#### [NEW] [app/vision_agent.py](file:///c:/Users/adamm_000/Desktop/CineClearAi/app/vision_agent.py)
- Multimodal parser handling:
  1. **Still Images**: Production set photos, costume stills, location scouts.
  2. **Video Files**: Automatic keyframe extraction at dynamic intervals using OpenCV/Pillow.
  3. **Screenplay Documents (PDF/TXT)**: Script page-by-page legal scanner identifying non-555 phone numbers, real brand product placements, living celebrity/public figure mentions, and un-cleared songs.
- Structured Gemini prompting to output candidate clearance flags with precise bounding descriptions and category classifications.

---

### 4. Legal Reasoning & Verification Loop
#### [NEW] [app/auditor.py](file:///c:/Users/adamm_000/Desktop/CineClearAi/app/auditor.py)
- `CineClearAuditor`:
  - Multi-turn clearance reasoning pipeline.
  - Orchestrates candidate flag extraction -> Parallel Search grounding -> statutory risk synthesis.
  - Generates concrete, industry-standard mitigation directives (e.g. "Blur in VFX", "Obtain Artwork Release Form Form-4A", "Replace with 555-0149 prefix", "De minimis incidental use defense documented").

---

### 5. Production-Grade E&O PDF Binder Generator
#### [NEW] [app/report_generator.py](file:///c:/Users/adamm_000/Desktop/CineClearAi/app/report_generator.py)
- Professional ReportLab PDF generator creating an official **E&O Insurance Legal Clearance Binder**:
  - Executive Cover Page with project metadata and Underwriter sign-off block
  - Executive Risk Matrix & Category Breakdown Table
  - Itemized Clearance Ledger with color-coded risk badges
  - Detailed Flag Dossiers containing visual description, Parallel Search sources, statutory analysis, and specific mitigation checklists.

---

### 6. Web Dashboard & REST API
#### [NEW] [server.py](file:///c:/Users/adamm_000/Desktop/CineClearAi/server.py)
- FastAPI application with endpoints:
  - `POST /api/audit`: Submit file or sample for clearance audit
  - `GET /api/reports/{id}`: Retrieve audit result JSON
  - `GET /api/reports/{id}/pdf`: Download ReportLab E&O PDF Binder
  - `GET /api/samples`: List preloaded test media
  - `GET /health`: Health check endpoint
  - Static file serving for web UI.

#### [NEW] [static/index.html](file:///c:/Users/adamm_000/Desktop/CineClearAi/static/index.html), [static/style.css](file:///c:/Users/adamm_000/Desktop/CineClearAi/static/style.css), [static/app.js](file:///c:/Users/adamm_000/Desktop/CineClearAi/static/app.js)
- Responsive, dark-themed cinema production dashboard:
  - Drag-and-drop file upload zone (Video, Image, Screenplay PDF)
  - Quick "Load Sample Media" buttons for instant 1-click demonstration
  - Real-time pipeline status animation
  - Interactive risk cards with filter tabs (Critical, High, Medium, Low)
  - Parallel Search evidence drawer & source link inspector
  - 1-click "Download E&O Insurance Binder (PDF)" button.

---

### 7. CLI Entrypoint & Sample Media
#### [NEW] [main.py](file:///c:/Users/adamm_000/Desktop/CineClearAi/main.py)
- CLI tool supporting `--file`, `--title`, `--output-json`, `--output-pdf`, and `--demo`.

#### [NEW] [sample_media/](file:///c:/Users/adamm_000/Desktop/CineClearAi/sample_media/)
- Bundled test assets:
  - `sample_set_photo.jpg` (generated test image with synthetic logo/art)
  - `sample_screenplay.txt` & `sample_screenplay.pdf` (screenplay with PII and brand mentions).

---

## Verification Plan

### Automated Tests
- Run `pytest` on all test files:
  ```powershell
  python -m pytest tests/ -v
  ```
- Test unit functions: Pydantic schema validation, Parallel Search client queries, PDF binder generation, FastAPI endpoints.

### Manual Verification
1. **CLI Execution**:
   ```powershell
   python main.py --demo
   ```
   Verify JSON report output and generated PDF binder.
2. **Server & Web UI Test**:
   - Start server: `python server.py`
   - Test `/health` endpoint and UI page load in browser
   - Test sample media audit flow and PDF download
   - Validate risk category filtering and Parallel search evidence display.
