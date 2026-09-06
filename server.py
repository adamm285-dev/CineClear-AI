import os
import re
import json
import shutil
import uuid
import time
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Response, Header, Query, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import ClearanceAuditReport, SampleMediaItem, AuditRequest
from app.auditor import CineClearAuditor
from app.edl_exporter import EDLExporter
from app.report_generator import generate_eo_clearance_binder
from generate_sample_media import ensure_sample_media
from app.retention import purge_upload_if_ephemeral
from app.models import TOS_VERSION

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
AUDIT_HITS: Dict[str, List[float]] = {}
auditor = CineClearAuditor()

# Mount static directory
STATIC_DIR = settings.BASE_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.middleware("http")
async def disable_chrome_asset_cache(request: Request, call_next):
    """Chrome caches /static/app.js aggressively; Opera often does not."""
    response = await call_next(request)
    path = request.url.path
    if path == "/" or path.endswith((".js", ".css", ".html")):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Mount sample media directory for image previews
ensure_sample_media(settings.SAMPLE_MEDIA_DIR)
app.mount("/sample_media", StaticFiles(directory=str(settings.SAMPLE_MEDIA_DIR)), name="sample_media")


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
        "environment": settings.ENVIRONMENT,
        "tos_version": TOS_VERSION,
        "decision_support_only": True
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


@app.get("/api/auth/verify")
async def verify_judge_auth(
    authorization: Optional[str] = Header(None),
    x_judge_access: Optional[str] = Header(None),
    access: Optional[str] = Query(None)
):
    """Validates whether client holds valid Hackathon Judge VIP access."""
    candidate = x_judge_access or access or authorization
    is_valid = settings.is_judge_authenticated(candidate)
    return {
        "authenticated": is_valid,
        "auth_required_for_uploads": settings.REQUIRE_JUDGE_AUTH_FOR_UPLOADS,
        "role": "VIP_JUDGE" if is_valid else "PUBLIC_GUEST"
    }


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _enforce_audit_rate_limit(request: Request, limit: int = 12, window_sec: int = 3600) -> None:
    """Caps live Gemini/Parallel audits per IP so a public passkey cannot drain quota."""
    ip = _client_ip(request)
    now = time.time()
    recent = [t for t in AUDIT_HITS.get(ip, []) if now - t < window_sec]
    if len(recent) >= limit:
        raise HTTPException(
            status_code=429,
            detail="Audit rate limit reached (12 live Gemini/Parallel jobs per hour from this network). Try again later."
        )
    recent.append(now)
    AUDIT_HITS[ip] = recent


def _require_judge_for_audit(
    access_key: Optional[str],
    authorization: Optional[str],
    x_judge_access: Optional[str],
) -> None:
    candidate = x_judge_access or access_key or authorization
    if not settings.is_judge_authenticated(candidate):
        raise HTTPException(
            status_code=401,
            detail="Judge Access Required: Live Gemini + Parallel audits need the VIP pass. "
                   "Open https://cineclear.pro?access=cineclear-judge-2026 or enter the passkey in the header."
        )


def _resolve_audit_target(
    sample_id: Optional[str],
    media_type: str,
    file: Optional[UploadFile],
    access_key: Optional[str],
    authorization: Optional[str],
    x_judge_access: Optional[str],
) -> Tuple[Path, str]:
    file_path_to_analyze: Optional[Path] = None

    if sample_id:
        ensure_sample_media(settings.SAMPLE_MEDIA_DIR)
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
        candidate = x_judge_access or access_key or authorization
        if not settings.is_judge_authenticated(candidate):
            raise HTTPException(
                status_code=401,
                detail="Judge Access Required: Custom footage uploads require judge VIP pass. "
                       "Open https://cineclear.pro?access=cineclear-judge-2026 or enter the judge passkey in the header."
            )

        raw_name = Path(file.filename or "uploaded_media").name
        clean_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', raw_name) or "uploaded_media"
        safe_filename = f"{uuid.uuid4().hex[:8]}_{clean_name}"
        file_path_to_analyze = settings.UPLOAD_DIR / safe_filename
        with open(file_path_to_analyze, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    else:
        raise HTTPException(status_code=400, detail="Must provide either an uploaded file or a valid sample_id.")

    if not file_path_to_analyze or not file_path_to_analyze.exists():
        raise HTTPException(status_code=404, detail="Target media file could not be found.")

    return file_path_to_analyze, media_type


@app.post("/api/audit")
async def audit_media_endpoint(
    request: Request,
    project_title: str = Form("Untitled Production"),
    media_type: str = Form("auto"),
    sample_id: Optional[str] = Form(None),
    access_key: Optional[str] = Form(None),
    authorization: Optional[str] = Header(None),
    x_judge_access: Optional[str] = Header(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Submits a media file or sample asset for multimodal vision analysis & Parallel search legal grounding.
    Public visitors can instantly audit bundled Hollywood sample assets.
    Custom footage uploads and sample audits require the Judge VIP Pass in production to protect Gemini/Parallel quota.
    """
    _require_judge_for_audit(access_key, authorization, x_judge_access)
    _enforce_audit_rate_limit(request)
    file_path_to_analyze, media_type = _resolve_audit_target(
        sample_id, media_type, file, access_key, authorization, x_judge_access
    )

    logger.info(f"Initiating clearance audit for: {file_path_to_analyze.name} (Project: {project_title})")
    try:
        report = await auditor.audit_media(
            file_path=str(file_path_to_analyze),
            project_title=project_title,
            media_type=media_type
        )
        if file:
            report.media_filename = Path(file.filename).name
        REPORTS_DB[report.id] = report
        return report
    finally:
        if file:
            purge_upload_if_ephemeral(file_path_to_analyze)


@app.post("/api/audit/stream")
async def audit_media_stream_endpoint(
    request: Request,
    project_title: str = Form("Untitled Production"),
    media_type: str = Form("auto"),
    sample_id: Optional[str] = Form(None),
    access_key: Optional[str] = Form(None),
    authorization: Optional[str] = Header(None),
    x_judge_access: Optional[str] = Header(None),
    file: Optional[UploadFile] = File(None)
):
    """SSE stream of real engine stages, then the completed report."""
    _require_judge_for_audit(access_key, authorization, x_judge_access)
    _enforce_audit_rate_limit(request)
    file_path_to_analyze, media_type = _resolve_audit_target(
        sample_id, media_type, file, access_key, authorization, x_judge_access
    )
    original_filename = Path(file.filename).name if file and file.filename else None

    logger.info(f"Streaming clearance audit for: {file_path_to_analyze.name} (Project: {project_title})")

    def _sse_bytes(evt: Dict[str, Any]) -> bytes:
        """SSE frame padded so Cloud Run / GFE flush each engine stage immediately."""
        payload = json.dumps(evt, default=str)
        pad = ":" + ("." * 2048) + "\n"
        return f"{pad}data: {payload}\n\n".encode("utf-8")

    async def event_gen():
        queue: asyncio.Queue = asyncio.Queue()
        yield _sse_bytes({
            "type": "stage",
            "step": 1,
            "status": "running",
            "label": "Stage 1/4: Engine connected — starting Gemini extraction...",
            "progress": 6,
        })

        async def on_progress(evt: Dict[str, Any]):
            await queue.put(evt)

        async def run_audit():
            try:
                report = await auditor.audit_media(
                    file_path=str(file_path_to_analyze),
                    project_title=project_title,
                    media_type=media_type,
                    on_progress=on_progress,
                )
                if original_filename:
                    report.media_filename = original_filename
                REPORTS_DB[report.id] = report
                await queue.put({"type": "complete", "report": json.loads(report.model_dump_json())})
            except Exception as e:
                logger.exception("Streaming audit failed")
                await queue.put({"type": "error", "message": str(e)})
            finally:
                if original_filename:
                    purge_upload_if_ephemeral(file_path_to_analyze)
                await queue.put(None)

        task = asyncio.create_task(run_audit())
        try:
            while True:
                evt = await queue.get()
                if evt is None:
                    break
                yield _sse_bytes(evt)
        finally:
            await task

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/reports/{report_id}")
async def get_report_json(report_id: str):
    """Retrieves JSON results for a completed clearance audit."""
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Audit report not found.")
    return REPORTS_DB[report_id]


def _pdf_filename(report: ClearanceAuditReport) -> str:
    safe_title = report.project_title.replace(" ", "_").replace("/", "_")
    return f"EO_Clearance_Binder_{safe_title}_{report.id[:8]}.pdf"


def _edl_filename(report: ClearanceAuditReport) -> str:
    safe_title = report.project_title.replace(" ", "_").replace("/", "_")
    return f"CineClear_Markers_{safe_title}_{report.id[:8]}.edl"


def _edl_response(report: ClearanceAuditReport) -> Response:
    edl_content = EDLExporter.generate_cmx3600_edl(report)
    return Response(
        content=edl_content,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{_edl_filename(report)}"'}
    )


def _pdf_file_response(report: ClearanceAuditReport) -> FileResponse:
    pdf_path = report.pdf_report_path
    if not pdf_path or not Path(pdf_path).exists():
        pdf_path = generate_eo_clearance_binder(report)
        report.pdf_report_path = pdf_path
        if report.id:
            REPORTS_DB[report.id] = report
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=_pdf_filename(report)
    )


@app.get("/api/reports/{report_id}/pdf")
async def download_report_pdf(report_id: str):
    """Downloads the generated Hollywood-grade ReportLab E&O Clearance Binder PDF."""
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Audit report not found.")
    return _pdf_file_response(REPORTS_DB[report_id])


@app.get("/api/reports/{report_id}/edl")
async def download_edl_markers(report_id: str):
    """Exports timecoded clearance flags as an importable CMX 3600 EDL for video editors."""
    if report_id not in REPORTS_DB:
        raise HTTPException(status_code=404, detail="Audit report not found.")
    return _edl_response(REPORTS_DB[report_id])


@app.post("/api/export/pdf")
async def export_pdf_from_report(report: ClearanceAuditReport):
    """Rebuilds the E&O PDF from the completed report JSON (works across Cloud Run instances)."""
    return _pdf_file_response(report)


@app.post("/api/export/edl")
async def export_edl_from_report(report: ClearanceAuditReport):
    """Builds a CMX 3600 EDL from the completed report JSON."""
    return _edl_response(report)


@app.get("/terms")
@app.get("/legal")
async def serve_terms():
    """Public Terms of Service / EULA for the UPL and liability shield."""
    legal = STATIC_DIR / "legal.html"
    if not legal.exists():
        raise HTTPException(status_code=404, detail="Terms of Service not found.")
    return FileResponse(path=legal, media_type="text/html")


@app.get("/favicon.ico")
async def favicon():
    """Serves the tab icon so browsers do not 404 /favicon.ico."""
    ico = STATIC_DIR / "favicon.ico"
    png = STATIC_DIR / "favicon.png"
    svg = STATIC_DIR / "favicon.svg"
    if ico.exists():
        return FileResponse(path=ico, media_type="image/x-icon")
    if png.exists():
        return FileResponse(path=png, media_type="image/png")
    if svg.exists():
        return FileResponse(path=svg, media_type="image/svg+xml")
    raise HTTPException(status_code=404, detail="Favicon not found.")


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the CineClear AI interactive Hollywood dark-mode web dashboard."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(
            content=index_file.read_text(encoding="utf-8"),
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
        )
    return HTMLResponse(content="<h1>CineClear AI API is running.</h1><p>Visit /static/index.html or /docs</p>")


if __name__ == "__main__":
    import uvicorn
    print("\n" + "=" * 65)
    print("   🎬 CineClear AI // Hollywood Legal & E&O Clearance Suite")
    print("=" * 65)
    print(f"  💻 Local Development:  http://localhost:{settings.PORT}")
    print(f"  🌐 Live Cloud Run:     https://cineclear.pro")
    print("=" * 65 + "\n")
    uvicorn.run(
        "server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )
