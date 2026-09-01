import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "LOW"            # Likely fair use / de minimis / public domain
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
    search_objective: str = Field(..., description="The query passed to Parallel Search API")
    sources_checked: List[str] = Field(default_factory=list, description="Verified web source URLs and legal registers")
    is_public_domain: bool = Field(default=False, description="Whether the work has expired into public domain")
    active_trademark_found: bool = Field(default=False, description="Whether active registered trademark was verified")
    rights_holder_identified: Optional[str] = Field(default=None, description="Identified legal owner or licensing body")
    statutory_context: str = Field(..., description="Legal rationale from Parallel web search and statutory citations")


class ClearanceFlag(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8], description="Unique identifier for the flag")
    timestamp_or_page: str = Field(..., description="Timecode (00:01:24) or script page number (Page 4)")
    category: ClearanceCategory = Field(..., description="Legal risk category")
    detected_entity: str = Field(..., description="Name of the detected logo, art, building, or entity")
    visual_description: str = Field(..., description="Where and how the object appears in frame or script")
    risk_level: RiskLevel = Field(..., description="E&O Insurance risk tier")
    verification: ParallelVerification = Field(..., description="Parallel Search ground truth legal verification")
    mitigation_action: str = Field(..., description="Actionable fix (e.g., 'Obtain location release', 'Blur in VFX', 'Replace with 555-number')")
    box_2d: Optional[List[int]] = Field(
        default=None,
        description="Normalized 2D bounding box [ymin, xmin, ymax, xmax] scaled 0 to 1000"
    )


class VFXWorkOrder(BaseModel):
    timestamp_or_page: str = Field(..., description="Timecode or script page reference")
    target_entity: str = Field(..., description="Visual mark, artwork, or prop to be remediated")
    action_type: str = Field(..., description="e.g., '2D Greeking / Logo Obscure', 'Gaussian Blur', 'Clean Plate Paint'")
    tracking_notes: str = Field(..., description="Specific VFX tracking and paint instructions")
    priority: str = Field(default="MEDIUM", description="Production priority: CRITICAL, HIGH, MEDIUM, LOW")


class LegalReleaseAgreement(BaseModel):
    form_type: str = Field(..., description="e.g., 'Form-4A Artwork Release', 'Trademark Placement Release'")
    licensor_entity: str = Field(..., description="Name of rights holder or licensor")
    property_description: str = Field(..., description="Description of protected artwork or trademark")
    governing_statute: str = Field(..., description="Applicable statutory code (e.g., 17 U.S.C. § 106, Lanham Act)")
    agreement_text: str = Field(..., description="Complete pre-filled legal agreement text ready for execution")


class ScriptFixDirective(BaseModel):
    page_number: str = Field(..., description="Screenplay page reference")
    original_text: str = Field(..., description="Original dialogue line or prop text containing PII")
    recommended_replacement: str = Field(..., description="Safe replacement (e.g., NANPA 555-01XX number)")
    rationale: str = Field(..., description="Legal rationale for script substitution")


class RemediationPackage(BaseModel):
    vfx_work_orders: List[VFXWorkOrder] = Field(default_factory=list)
    legal_releases: List[LegalReleaseAgreement] = Field(default_factory=list)
    script_fixes: List[ScriptFixDirective] = Field(default_factory=list)


class ClearanceAuditReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Audit report identifier")
    project_title: str = Field(..., description="Production / Film / TV Project Title")
    media_filename: str = Field(..., description="Filename of analyzed footage, image, or screenplay")
    media_type: str = Field(default="image", description="Asset type: 'video', 'image', 'script'")
    total_flags: int = Field(default=0, description="Total count of clearance liabilities flagged")
    critical_count: int = Field(default=0, description="Count of CRITICAL risk flags")
    high_count: int = Field(default=0, description="Count of HIGH risk flags")
    medium_count: int = Field(default=0, description="Count of MEDIUM risk flags")
    low_count: int = Field(default=0, description="Count of LOW risk flags")
    flags: List[ClearanceFlag] = Field(default_factory=list, description="List of itemized clearance flags")
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
    remediation_package: Optional[RemediationPackage] = Field(default=None, description="Departmental remediation deliverables")
    pdf_report_path: Optional[str] = Field(default=None, description="Path to generated ReportLab PDF binder")


class AuditRequest(BaseModel):
    project_title: str = Field(default="Untitled Production", description="Project title")
    media_type: Optional[str] = Field(default="auto", description="Media type: 'video', 'image', 'script', or 'auto'")
    sample_id: Optional[str] = Field(default=None, description="Preloaded sample identifier")


class SampleMediaItem(BaseModel):
    id: str
    title: str
    media_type: str
    filename: str
    description: str
    thumbnail_url: Optional[str] = None
