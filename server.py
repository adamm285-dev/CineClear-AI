import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import ClearanceAuditReport, SampleMediaItem, AuditRequest
from app.auditor import CineClearAuditor

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("cineclear.server")

app = FastAPI(
    title="CineClear AI - Agentic Legal & E&O Clearance System",
    description="Multimodal Vision + Parallel Grounding E&O Clearance Binder Generator for Film & TV",
    version="1.0.0"
)

# Enable CORS for local development and integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache for recent reports
REPORTS_DB: Dict[str, ClearanceAuditReport] = {}
auditor = CineClearAuditor()

# Mount static directory
STATIC_DIR = settings.BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health")
async def health_check():
    """Returns application health and API configuration status."""
    return {
        "status": "healthy",
        "service": "CineClear AI",
        "version": "1.0.0",
        "gemini_configured": settings.is_gemini_configured(),
        "gemini_model": settings.GEMINI_MODEL,
        "parallel_configured": settings.is_parallel_configured(),
        "parallel_base_url": settings.PARALLEL_BASE_URL,
        "environment": settings.ENVIRONMENT
    }


@app.get("/api/samples", response_model=List[SampleMediaItem])
async def list_sample_media():
    """Lists preloaded Hollywood sample media available for instant 1-click legal clearance audit."""
    return [
        SampleMediaItem(
            id="sample-photo",
            title="Hero Living Room - Production Set Still",
            media_type="image",
            filename="sample_set_photo.jpg",
            description="High-resolution production still featuring Nike hero wardrobe, Starbucks prop, and contemporary background artwork.",
            thumbnail_url="/sample_media/sample_set_photo.jpg"
        ),
        SampleMediaItem(
            id="sample-screenplay",
            title="Feature Screenplay Excerpt (PDF)",
            media_type="script",
            filename="sample_screenplay.pdf",
            description="Screenplay scene with non-555 private telephone number, Apple laptop dialogue, and un-cleared commercial music cue.",
            thumbnail_url=None
        ),
        SampleMediaItem(
            id="sample-script-txt",
            title="Screenplay Scene 1-3 (Text Format)",
            media_type="script",
            filename="sample_screenplay.txt",
            description="Raw screenplay text with character actions, trademarked tech hardware, and Paris architecture references.",
            thumbnail_url=None
        )
    ]


@app.post("/api/audit")
async def audit_media_endpoint(
    project_title: str = Form("Untitled Production"),
    media_type: str = Form("auto"),
    sample_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Submits a media file or sample asset for multimodal vision analysis & Parallel search legal grounding.
    """
    file_path_to_analyze: Optional[Path] = None

    if sample_id:
        if sample_id == "sample-photo":
            file_path_to_analyze = settings.SAMPLE_MEDIA_DIR / "sample_set_photo.jpg"
            if media_type == "auto":
                media_type = "image"
        elif sample_id == "sample-screenplay":
            file_path_to_analyze = settings.SAMPLE_MEDIA_DIR / "sample_screenplay.pdf"
            if media_type == "auto":
                media_type = "script"
        elif sample_id == "sample-script-txt":
            file_path_to_analyze = settings.SAMPLE_MEDIA_DIR / "sample_screenplay.txt"
            if media_type == "auto":
                media_type = "script"
        else:
            raise HTTPException(status_code=400, detail=f"Unknown sample ID: {sample_id}")

    elif file:
        file_path_to_analyze = settings.UPLOAD_DIR / file.filename
        with open(file_path_to_analyze, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    else:
        raise HTTPException(status_code=400, detail="Must provide either an uploaded file or a valid sample_id.")

    if not file_path_to_analyze or not file_path_to_analyze.exists():
        raise HTTPException(status_code=404, detail="Target media file could not be found.")

    logger.info(f"Initiating clearance audit for: {file_path_to_analyze.name} (Project: {project_title})")
    
    # Run full multi-turn audit
    report = await auditor.audit_media(
        file_path=str(file_path_to_analyze),
        project_title=project_title,
        media_type=media_type
    )

    # Store in memory cache
    REPORTS_DB[report.id] = report

    return report


@app.get("/api/reports/{report_id}")
async def get_report_json(report_id: str):
    """Retrieves JSON results for a completed clearance audit."""
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Audit report not found.")
    return REPORTS_DB[report_id]


@app.get("/api/reports/{report_id}/pdf")
async def download_report_pdf(report_id: str):
    """Downloads the generated Hollywood-grade ReportLab E&O Clearance Binder PDF."""
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Audit report not found.")
    
    report = REPORTS_DB[report_id]
    if not report.pdf_report_path or not Path(report.pdf_report_path).exists():
        raise HTTPException(status_code=404, detail="PDF report file is not available.")

    filename = Path(report.pdf_report_path).name
    return FileResponse(
        path=report.pdf_report_path,
        media_type="application/pdf",
        filename=filename
    )


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the CineClear AI interactive Hollywood dark-mode web dashboard."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>CineClear AI API is running.</h1><p>Visit /static/index.html or /docs</p>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
