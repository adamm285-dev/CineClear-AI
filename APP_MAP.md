# CineClear AI - Application Architecture Map (APP_MAP.md)

This document provides the definitive architectural map and component directory of the **CineClear AI Legal & E&O Clearance System**.

---

## 1. System Overview & 3-Agent Triad

```mermaid
graph TD
    Media[🎬 Input Production Media: Video / Stills / Script PDF] --> ExtractorHarness[🛡️ Role 1: Extractor Harness]
    
    ExtractorHarness -->|Deduplicate & Sanitize| VisionAgent[👁️ Agent 1: Gemini Multimodal Vision & PyMuPDF Scanner]
    VisionAgent --> CandidateFlags[⚠️ Candidate Clearance Liabilities]
    
    CandidateFlags --> ParallelClient[🌐 Parallel Search Grounding Client]
    ParallelClient -->|Query: https://api.parallel.ai/v1/search| ParallelAPI[🔍 Parallel Semantic Search API]
    ParallelAPI --> RealWorldData[📚 Real-World Ground Truth: USPTO, Copyright Office, NANPA]
    RealWorldData --> GroundedFlags[⚖️ Grounded Legal Flags]
    
    GroundedFlags --> CriticHarness[🛡️ Role 2: Critic & Securitization Harness]
    CriticHarness --> CriticAgent[🧑‍⚖️ Agent 2: Senior Counsel Critic Reflection Pass]
    CriticAgent -->|Enforce Invariants & Reconcile Contradictions| SecuritizedFlags[🎯 Securitized Clearance Flags]
    
    SecuritizedFlags --> RemediationAgent[⚡ Agent 3: Autonomous Remediation & Dispatcher]
    
    RemediationAgent --> Form4A[📄 Pre-Filled Form-4A Art Releases]
    RemediationAgent --> TMReleases[🏷️ Trademark Placement Agreements]
    RemediationAgent --> VFXOrders[🎨 Timecoded VFX Paint / Greeking Work Orders]
    RemediationAgent --> ScriptFixes[📞 NANPA 555-01XX Script Substitutions]
    
    SecuritizedFlags --> ReportGenerator[📑 ReportLab E&O PDF Clearance Binder Generator]
    SecuritizedFlags --> StudioDashboard[💻 Interactive Cinema Dark-Mode Dashboard]
```

---

## 2. API Endpoint Directory

| Method | Endpoint | Handler Function | Purpose / Description |
| :--- | :--- | :--- | :--- |
| **GET** | `/` | `serve_dashboard` | Serves the interactive cinema studio dark-mode web dashboard. |
| **GET** | `/health` | `health_check` | Service health status, active API key status, model configuration, and environment check. |
| **GET** | `/api/samples` | `list_sample_media` | Returns pre-loaded cinema test assets (set photos, screenplay PDF, scene text) for instant 1-click evaluation. |
| **POST** | `/api/audit` | `audit_media_endpoint` | Primary analysis endpoint. Ingests uploaded footage, set photo, or sample ID; executes multimodal vision and Parallel search grounding; returns `ClearanceAuditReport`. |
| **GET** | `/api/reports/{report_id}` | `get_report_json` | Retrieves cached JSON audit report containing all itemized flags, risk tallies, and search grounding metadata. |
| **GET** | `/api/reports/{report_id}/pdf` | `download_report_pdf` | Serves the generated cinema-grade ReportLab E&O Clearance Binder PDF with headers, ledgers, and sign-off blocks. |
| **GET** | `/static/*` | StaticFiles Mount | Serves client CSS, JavaScript, and UI assets. |

---

## 3. Data Model & Schema Definitions

### Legal Clearance & Remediation Schemas (`app/models.py`)

```python
class RiskLevel(str, Enum):
    LOW = "LOW"            # Fair use / de minimis / public domain
    MEDIUM = "MEDIUM"      # Incidental mark / ambiguous rights / verify release
    HIGH = "HIGH"          # Explicit trademark, uncleared music, modern art
    CRITICAL = "CRITICAL"  # Defamatory placement, living person likeness risk, real PII

class ClearanceCategory(str, Enum):
    TRADEMARK_LOGO = "TRADEMARK_LOGO"
    COPYRIGHTED_ART = "COPYRIGHTED_ART"
    ARCHITECTURAL_RIGHTS = "ARCHITECTURAL_RIGHTS"
    MUSIC_AUDIO = "MUSIC_AUDIO"
    NAME_DEFAMATION = "NAME_DEFAMATION"
    PHONE_PII = "PHONE_PII"

class ParallelVerification(BaseModel):
    search_objective: str
    sources_checked: List[str]
    is_public_domain: bool = False
    active_trademark_found: bool = False
    rights_holder_identified: Optional[str] = None
    statutory_context: str

class ClearanceFlag(BaseModel):
    id: str
    timestamp_or_page: str
    category: ClearanceCategory
    detected_entity: str
    visual_description: str
    risk_level: RiskLevel
    verification: ParallelVerification
    mitigation_action: str

class VFXWorkOrder(BaseModel):
    timestamp_or_page: str
    target_entity: str
    action_type: str
    tracking_notes: str
    priority: str

class LegalReleaseAgreement(BaseModel):
    form_type: str
    licensor_entity: str
    property_description: str
    governing_statute: str
    agreement_text: str

class ScriptFixDirective(BaseModel):
    page_number: str
    original_text: str
    recommended_replacement: str
    rationale: str

class RemediationPackage(BaseModel):
    vfx_work_orders: List[VFXWorkOrder] = Field(default_factory=list)
    legal_releases: List[LegalReleaseAgreement] = Field(default_factory=list)
    script_fixes: List[ScriptFixDirective] = Field(default_factory=list)

class ClearanceAuditReport(BaseModel):
    id: str
    project_title: str
    media_filename: str
    media_type: str
    total_flags: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    flags: List[ClearanceFlag]
    generated_at: str
    remediation_package: Optional[RemediationPackage] = None
    pdf_report_path: Optional[str] = None
```

---

## 4. Storage & Persistence Mapping

```text
C:\Users\adamm_000\Desktop\CineClearAi\
├── .env.example                     # Environment template (Gemini & Parallel keys, server port)
├── .env                             # Local environment configuration
├── .gitignore                       # Standard Python / artifact ignore rules
├── requirements.txt                 # Project dependencies
├── README.md                        # Primary documentation & build guide
├── STATE.md                         # Operational state, component health & runbook
├── APP_MAP.md                       # Application architectural map & schemas
├── SPINE.md                         # Core system invariants & clearance lifecycles
├── generate_sample_media.py         # Test asset generator for stills and screenplays
├── main.py                          # Terminal CLI & batch analysis engine
├── server.py                        # FastAPI web server (port 8085)
├── run.bat                          # Local one-click server & browser launcher
├── app/
│   ├── __init__.py
│   ├── config.py                    # Pydantic Settings & environment manager
│   ├── models.py                    # Pydantic legal clearance & remediation schemas
│   ├── harness.py                   # ExtractorHarness & CriticHarness boundaries
│   ├── gemini_cascade.py            # Dynamic Model Cascade Ladder & failover manager
│   ├── edl_exporter.py              # CMX 3600 NLE Timeline Marker & EDL Exporter
│   ├── fair_use_analyzer.py         # 4-Factor Fair Use (17 U.S.C. § 107) & Multi-Territory Engine
│   ├── music_arch_analyzer.py       # Music Sync (17 U.S.C. § 114) & AWCPA Architectural Validator (§ 120)
│   ├── parallel_client.py           # Parallel Search API client with live search & mock engine
│   ├── vision_agent.py              # Agent 1: Gemini Multimodal visual & audio parser
│   ├── auditor.py                   # Agent 2: Multi-turn reasoning & Senior Counsel Critic loop
│   ├── remediation_agent.py         # Agent 3: Departmental Remediation & Dispatcher
│   └── report_generator.py          # ReportLab PDF E&O Clearance Binder generator
├── static/
│   ├── index.html                   # Cinematic dark-mode studio dashboard with SVG BBox overlay
│   ├── style.css                    # Production styling & risk color variables
│   └── app.js                       # Interactive UI controller & remediation package renderer
├── sample_media/
│   ├── sample_set_photo.jpg         # Sample production still (wardrobe logos, set art)
│   ├── sample_screenplay.pdf        # Screenplay PDF with PII/phone & brand mentions
│   └── sample_screenplay.txt        # Screenplay scene text
├── uploads/                         # Temporary storage for uploaded footage & scripts
├── reports/                         # Generated E&O Insurance PDF Clearance Binders
└── tests/                           # Automated test suite
    ├── __init__.py
    ├── test_models.py               # Schema & validation tests
    ├── test_harness.py              # Dual harness eval suite
    ├── test_cascade.py              # Dynamic Model Cascade failover tests
    ├── test_edl_exporter.py         # CMX 3600 NLE timeline marker export tests
    ├── test_fair_use.py             # 4-Factor Fair Use & multi-territory tests
    ├── test_music_arch.py           # AWCPA architectural safe harbor & music cue sheet tests
    ├── test_parallel_client.py      # Parallel search client tests
    ├── test_auditor.py              # Clearance audit & critic reflection tests
    ├── test_remediation.py          # Agent 3 remediation dispatcher tests
    └── test_server.py               # FastAPI endpoint tests
```

---

## 5. Security, Grounding & Legal Defense Architecture

1. **Grounded Legal Chain of Custody:**
   * Every clearance flag maintains an immutable `ParallelVerification` payload recording the exact search objective query, sources examined, rights holder identified, and statutory context.
2. **Statutory Safe Harbor Verification:**
   * Automatically cross-references architectural landmarks against **17 U.S.C. § 120(a)** (AWCPA) to avoid unnecessary licensing costs for public buildings.
   * Enforces **NANPA 555-0100 through 555-0199** reservation range to eliminate civil privacy liability.
3. **Dual Harness Boundaries & De-biasing:**
   * `ExtractorHarness` protects API budgets from duplicate recurring video keyframe queries.
   * `CriticHarness` prevents modern corporate marks from hallucinating into public domain status.
4. **Court-Ready E&O Binder Deliverables:**
   * PDF output adheres to entertainment insurance underwriting specifications, including clear executive summaries, risk matrices, itemized ledgers, and attorney/underwriter signature certification blocks.
