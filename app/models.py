import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


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


def normalize_clearance_category(v: Any) -> ClearanceCategory:
    """Coerces fuzzy string labels from LLM extraction into canonical ClearanceCategory."""
    if isinstance(v, ClearanceCategory):
        return v
    s = str(v).upper().strip().replace(" ", "_").replace("-", "_")
    if any(k in s for k in ["TRADEMARK", "LOGO", "BRAND", "PROP"]):
        return ClearanceCategory.TRADEMARK_LOGO
    if any(k in s for k in ["ART", "PAINT", "SCULPT", "MURAL", "CANVAS", "GRAFFITI"]):
        return ClearanceCategory.COPYRIGHTED_ART
    if any(k in s for k in ["ARCHITECT", "BUILD", "FACADE", "LANDMARK", "TOWER", "STRUCTURE"]):
        return ClearanceCategory.ARCHITECTURAL_RIGHTS
    if any(k in s for k in ["MUSIC", "SONG", "AUDIO", "TRACK", "SOUND"]):
        return ClearanceCategory.MUSIC_AUDIO
    if any(k in s for k in ["PHONE", "PII", "NUMBER", "DIGIT", "ADDRESS", "SSN"]):
        return ClearanceCategory.PHONE_PII
    if any(k in s for k in ["NAME", "DEFAM", "PERSON", "LIBEL", "SLANDER"]):
        return ClearanceCategory.NAME_DEFAMATION
    return ClearanceCategory.TRADEMARK_LOGO


def normalize_risk_level(v: Any) -> RiskLevel:
    """Coerces fuzzy string labels from LLM extraction into canonical RiskLevel."""
    if isinstance(v, RiskLevel):
        return v
    s = str(v).upper().strip()
    if "CRIT" in s:
        return RiskLevel.CRITICAL
    if "HIGH" in s or "HI" == s:
        return RiskLevel.HIGH
    if "MED" in s:
        return RiskLevel.MEDIUM
    if "LOW" in s or "PD" in s or "PUBLIC" in s:
        return RiskLevel.LOW
    return RiskLevel.MEDIUM


class ParallelVerification(BaseModel):
    search_objective: str = Field(..., description="The query passed to Parallel Search API")
    sources_checked: List[str] = Field(default_factory=list, description="Verified web source URLs and legal registers")
    is_public_domain: bool = Field(default=False, description="Whether the work has expired into public domain")
    active_trademark_found: bool = Field(default=False, description="Whether active registered trademark was verified")
    rights_holder_identified: Optional[str] = Field(default=None, description="Identified legal owner or licensing body")
    statutory_context: str = Field(..., description="Legal rationale from Parallel web search and statutory citations")


class FairUseFactor(BaseModel):
    factor_name: str
    score: int = Field(..., ge=1, le=5, description="1 (Favors Infringement) to 5 (Strong Fair Use Defense)")
    rationale: str


class FairUseScorecard(BaseModel):
    purpose_and_character: FairUseFactor      # Factor 1: Transformative / Contextual vs Commercial
    nature_of_work: FairUseFactor             # Factor 2: Factual / Functional vs Highly Creative Fine Art
    amount_and_substantiality: FairUseFactor  # Factor 3: Incidental / Background vs Hero Focal Point
    market_harm: FairUseFactor                # Factor 4: Market Substitution & Licensing Impact
    composite_score: float                    # Average score out of 5.0
    defense_rating: str                       # "STRONG DEFENSE (DE MINIMIS)", "MODERATE DEFENSE", "HIGH LITIGATION RISK"


class TerritoryAssessment(BaseModel):
    territory: str                            # e.g., "United States", "United Kingdom", "European Union", "Canada"
    clearance_status: str                     # "EXPLICIT RELEASE REQUIRED", "INCIDENTAL SAFE HARBOR", "PERMITTED FAIR DEALING"
    governing_statute: str                    # e.g., "17 U.S.C. § 106", "CDPA 1988 § 31", "EU InfoSoc Dir. Art 5(3)(i)"
    jurisdictional_notes: str


class ArchitecturalLandmarkAssessment(BaseModel):
    structure_name: str
    jurisdiction_status: str
    is_public_view_safe_harbor: bool
    governing_statute: str
    commercial_filing_restrictions: str
    clearance_recommendation: str


TOS_VERSION = "2026-09-06"

UPL_LEGAL_DISCLAIMER: str = (
    "NOTICE — DECISION-SUPPORT ONLY: CineClear AI is a paralegal research and workflow "
    "accelerator for licensed production counsel and E&O brokers. This dossier organizes "
    "automated heuristics, multimodal detections, and public-registry search results on an "
    "AS-IS / AS-AVAILABLE basis. It is not legal advice, not a legal opinion, not an "
    "insurance certificate, and not a clearance, distribution, or underwriting approval. "
    "It does not create an attorney-client relationship. No output may be represented as "
    "'cleared for distribution' or as a guarantee that any work is free of copyright, "
    "trademark, privacy, or E&O risk. Final legal sign-off must be made by a licensed "
    "production attorney and/or E&O broker. Use of this software is subject to the Terms "
    "of Service at /terms (version " + TOS_VERSION + ")."
)


class RogersTestAssessment(BaseModel):
    is_expressive_work: bool = True
    artistic_relevance_passed: bool = Field(..., description="Whether trademark depiction meets threshold artistic relevance to narrative")
    explicitly_misleading: bool = Field(..., description="Whether mark explicitly misleads as to source, sponsorship, or endorsement")
    rogers_protection_applies: bool = Field(..., description="Whether Rogers v. Grimaldi defense shields expressive trademark use")
    statutory_rationale: str


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
    fair_use_scorecard: Optional[FairUseScorecard] = None
    territory_matrix: Optional[List[TerritoryAssessment]] = None
    arch_assessment: Optional[ArchitecturalLandmarkAssessment] = None
    rogers_assessment: Optional[RogersTestAssessment] = None

    @field_validator('category', mode='before')
    @classmethod
    def coerce_category(cls, v):
        return normalize_clearance_category(v)

    @field_validator('risk_level', mode='before')
    @classmethod
    def coerce_risk_level(cls, v):
        return normalize_risk_level(v)


class MusicCueEntry(BaseModel):
    cue_number: str
    track_title: str
    artist_performer: str
    composer_author: str
    publisher_pro: str = Field(..., description="e.g., 'ASCAP (50%) / BMI (50%)'")
    master_rights_holder: str = Field(..., description="Record label / Master recording owner (17 U.S.C. § 114)")
    sync_publisher: str = Field(..., description="Sync licensing publisher (17 U.S.C. § 106(4))")
    usage_type: str = Field(..., description="'Visual Vocal', 'Background Instrumental', 'Source Music / Radio'")
    duration: str
    clearance_status: str


class MusicCueSheet(BaseModel):
    production_title: str
    cue_entries: List[MusicCueEntry] = Field(default_factory=list)
    pro_compliance_certified: bool = True


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
    legal_disclaimer: str = Field(default=UPL_LEGAL_DISCLAIMER)


class ScriptFixDirective(BaseModel):
    page_number: str = Field(..., description="Screenplay page reference")
    original_text: str = Field(..., description="Original dialogue line or prop text containing PII")
    recommended_replacement: str = Field(..., description="Safe replacement (e.g., NANPA 555-01XX number)")
    rationale: str = Field(..., description="Legal rationale for script substitution")


class RemediationPackage(BaseModel):
    vfx_work_orders: List[VFXWorkOrder] = Field(default_factory=list)
    legal_releases: List[LegalReleaseAgreement] = Field(default_factory=list)
    script_fixes: List[ScriptFixDirective] = Field(default_factory=list)
    music_cue_sheet: Optional[MusicCueSheet] = None


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
    legal_disclaimer: str = Field(default=UPL_LEGAL_DISCLAIMER, description="Statutory UPL decision-support notice")


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
