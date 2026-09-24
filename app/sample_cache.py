"""
CineClear AI - Zero-Burn Golden Sample Report Cache
Provides instant, authentic Hollywood clearance dossiers for bundled sample assets
with ZERO external API quota consumption, preventing crawler/bot quota abuse.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict

from app.models import ClearanceAuditReport

CACHE_DIR = Path(__file__).parent.parent


def _load_raw_cache(filename: str) -> dict:
    cache_path = CACHE_DIR / filename
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))
    return {}


SAMPLE_CACHES: Dict[str, dict] = {
    "sample-photo": _load_raw_cache("sample_photo_cache.json"),
    "sample-screenplay": _load_raw_cache("sample_pdf_cache.json"),
    "sample-script-txt": _load_raw_cache("sample_txt_cache.json")
}


def get_cached_sample_report(sample_id: str, project_title: Optional[str] = None) -> Optional[ClearanceAuditReport]:
    """Returns a fresh, high-fidelity ClearanceAuditReport instance from golden cache."""
    raw_data = SAMPLE_CACHES.get(sample_id)
    if not raw_data:
        return None

    # Deep clone data so modifications don't mutate template
    report_dict = json.loads(json.dumps(raw_data))
    
    # Assign fresh runtime ID and timestamps
    report_dict["id"] = uuid.uuid4().hex[:12]
    report_dict["generated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    if project_title and project_title.strip() and project_title != "Untitled Production":
        report_dict["project_title"] = project_title.strip()

    return ClearanceAuditReport.model_validate(report_dict)
