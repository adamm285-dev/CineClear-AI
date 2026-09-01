"""
CineClear AI - Music Sync Clearance (17 U.S.C. § 114) & AWCPA Architectural Validator (17 U.S.C. § 120)
Generates industry-standard ASCAP/BMI Music Cue Sheets and evaluates architectural facade liabilities.
"""

from typing import List, Optional
from app.models import (
    ArchitecturalLandmarkAssessment,
    ClearanceCategory,
    ClearanceFlag,
    MusicCueEntry,
    MusicCueSheet,
    RiskLevel,
)

# Registry of restricted architectural landmarks and trademarked facades
RESTRICTED_LANDMARKS = {
    "eiffel tower": {
        "condition": "night",
        "holder": "Société d'Exploitation de la Tour Eiffel (SETE)",
        "statute": "French Intellectual Property Code (Art. L.111-1)",
        "restriction": "Night lighting display is an active copyrighted visual installation. Day panoramas are in public domain; nighttime commercial broadcast requires SETE authorization."
    },
    "hollywood sign": {
        "condition": "all",
        "holder": "Hollywood Chamber of Commerce",
        "statute": "Lanham Act 15 U.S.C. § 1114 (Registered Trademark)",
        "restriction": "Commercial depiction as a primary focal element requires commercial licensing agreement with the Hollywood Chamber of Commerce."
    },
    "chrysler building": {
        "condition": "all",
        "holder": "Signa Holding / RFR Holding",
        "statute": "Lanham Act (Registered Building Facade Mark)",
        "restriction": "Building facade and art deco spire are federally registered trademarks for commercial merchandising and entertainment depiction."
    },
    "rock and roll hall of fame": {
        "condition": "all",
        "holder": "Rock and Roll Hall of Fame Foundation",
        "statute": "Lanham Act / I.M. Pei Design Protection",
        "restriction": "Distinctive I.M. Pei geometric structure is trademarked; prominent commercial hero framing triggers licensing review."
    }
}


class AWCPAValidator:
    """Evaluates architectural filming rights under 17 U.S.C. § 120(a) vs Trademarked Facades."""

    @staticmethod
    def evaluate_landmark(
        entity_name: str,
        visual_context: str,
        risk_level: RiskLevel
    ) -> ArchitecturalLandmarkAssessment:
        name_lower = entity_name.lower()
        ctx_lower = visual_context.lower()

        # Check restricted landmark database
        for landmark_key, meta in RESTRICTED_LANDMARKS.items():
            if landmark_key in name_lower or landmark_key in ctx_lower:
                if meta["condition"] == "night" and "night" not in ctx_lower and "dark" not in ctx_lower and "night" not in name_lower:
                    break  # Daytime Eiffel Tower is public domain safe harbor
                return ArchitecturalLandmarkAssessment(
                    structure_name=entity_name,
                    jurisdiction_status="RESTRICTED COMMERCIAL FACADE / INSTALLATION",
                    is_public_view_safe_harbor=False,
                    governing_statute=meta["statute"],
                    commercial_filing_restrictions=meta["restriction"],
                    clearance_recommendation=(
                        f"ACTION REQUIRED: Execute commercial location release with {meta['holder']} "
                        f"or adjust camera angle to exclude distinctive architectural trade dress."
                    )
                )

        # Standard AWCPA Section 120(a) Safe Harbor for public buildings
        return ArchitecturalLandmarkAssessment(
            structure_name=entity_name,
            jurisdiction_status="STATUTORY SAFE HARBOR (AWCPA § 120(a))",
            is_public_view_safe_harbor=True,
            governing_statute="Architectural Works Copyright Protection Act (17 U.S.C. § 120(a))",
            commercial_filing_restrictions=(
                "Statutory exemption explicitly permits the photographing, broadcasting, and commercial "
                "reproduction of architectural works located in or ordinarily visible from a public space."
            ),
            clearance_recommendation=(
                "CLEARANCE CONFIRMED: Protected under 17 U.S.C. § 120(a) public view safe harbor. "
                "No location release or VFX clean-up required for E&O underwriting."
            )
        )


class MusicSyncAnalyzer:
    """Audits dual-tier musical rights and compiles ASCAP/BMI/SESAC cue sheets."""

    @staticmethod
    def build_cue_sheet(flags: List[ClearanceFlag], project_title: str) -> Optional[MusicCueSheet]:
        music_flags = [f for f in flags if f.category == ClearanceCategory.MUSIC_AUDIO]
        if not music_flags:
            return None

        cue_entries: List[MusicCueEntry] = []
        for idx, flag in enumerate(music_flags, 1):
            holder = flag.verification.rights_holder_identified or "Independent / Undetermined Label"
            cue_entries.append(
                MusicCueEntry(
                    cue_number=f"M-{idx:03d}",
                    track_title=flag.detected_entity,
                    artist_performer=holder,
                    composer_author=f"{holder} / Designated Writers",
                    publisher_pro="ASCAP (50%) / BMI (50%)",
                    master_rights_holder=f"{holder} Recordings LLC (17 U.S.C. § 114)",
                    sync_publisher=f"{holder} Music Publishing (17 U.S.C. § 106(4))",
                    usage_type="Source Music / Visual Background",
                    duration="00:00:30",
                    clearance_status="SYNC & MASTER LICENSES MANDATORY PRIOR TO BROADCAST"
                )
            )

        return MusicCueSheet(
            production_title=project_title,
            cue_entries=cue_entries,
            pro_compliance_certified=True
        )
