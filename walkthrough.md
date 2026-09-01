# Walkthrough - CineClear AI: Agentic Legal & E&O Clearance System

**CineClear AI** has been created in `C:\Users\adamm_000\Desktop\CineClearAi` for [https://github.com/adamm285-dev/CineClear-AI](https://github.com/adamm285-dev/CineClear-AI).

It provides an end-to-end autonomous clearance and E&O (Errors & Omissions) insurance risk intelligence pipeline for Hollywood studios, indie filmmakers, and commercial productions.

---

## 🛠 What Was Built

```
CineClearAi/
├── .env.example                     # Environment template (Gemini 2.5 Pro, Parallel Search API)
├── .env                             # Local environment configuration
├── .gitignore                       # Python / OS / upload gitignore
├── requirements.txt                 # Project dependencies
├── README.md                        # Documentation, architecture, and guides
├── generate_sample_media.py         # Utility script to generate sample test media
├── main.py                          # CLI and batch analysis entrypoint
├── server.py                        # FastAPI server & REST API
├── app/
│   ├── __init__.py
│   ├── config.py                    # Pydantic Settings & environment manager
│   ├── models.py                    # Pydantic clearance schemas (RiskLevel, ClearanceFlag, etc.)
│   ├── parallel_client.py           # Parallel Search API client with live search & mock engine
│   ├── vision_agent.py              # Gemini Multimodal parser for video frames, set photos, and script PDFs
│   ├── auditor.py                   # Multi-turn legal reasoning & Parallel verification loop
│   └── report_generator.py          # ReportLab Hollywood E&O Clearance Binder PDF generator
├── static/
│   ├── index.html                   # Cinematic dark-mode studio dashboard
│   ├── style.css                    # Polished film UI aesthetics & animations
│   └── app.js                       # Live upload, async analysis pipeline, filterable flag cards & PDF export
├── sample_media/
│   ├── sample_set_photo.jpg         # Sample production still containing logo & art liabilities
│   ├── sample_screenplay.pdf        # Screenplay PDF with PII/phone & brand mentions
│   └── sample_screenplay.txt        # Screenplay scene text
└── tests/
    ├── __init__.py
    ├── test_models.py               # Schema and validation tests
    ├── test_parallel_client.py      # Parallel search client unit tests
    ├── test_auditor.py              # Clearance audit & reasoning tests
    └── test_server.py               # FastAPI endpoint tests
```

---

## 🧪 Verification & Test Results

### 1. Automated Unit & Integration Tests
All 8 automated tests passed successfully in 0.58s:
```powershell
python -m pytest tests/ -v
```
- `test_models.py::test_models_instantiation` (PASSED)
- `test_parallel_client.py::test_parallel_search_mock` (PASSED)
- `test_parallel_client.py::test_parallel_search_phone_pii` (PASSED)
- `test_auditor.py::test_cineclear_auditor_script` (PASSED)
- `test_auditor.py::test_cineclear_auditor_image` (PASSED)
- `test_server.py::test_health_endpoint` (PASSED)
- `test_server.py::test_samples_endpoint` (PASSED)
- `test_server.py::test_audit_sample_photo` (PASSED)

### 2. CLI Execution Test
Tested `main.py --demo` and `main.py --file sample_media/sample_screenplay.pdf`:
- Accurately detected and classified `PHONE_PII` (CRITICAL), `TRADEMARK_LOGO` (MEDIUM/CRITICAL), `COPYRIGHTED_ART` (HIGH), and `MUSIC_AUDIO` (HIGH).
- Grounded all flags with Parallel Search and statutory citations (Lanham Act, 17 U.S.C. § 106, § 120, NANPA FCC standards).
- Generated official ReportLab E&O PDF binders in `reports/`.

---

## 🚀 How to Run

### Start the Web Dashboard
```powershell
cd C:\Users\adamm_000\Desktop\CineClearAi
python server.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

### Run via CLI
```powershell
# Instant Demo Audit
python main.py --demo

# Audit a Script PDF
python main.py --file sample_media/sample_screenplay.pdf --title "Midnight Drive"
```
