"""
CineClear AI - Agent 3: Autonomous Remediation & Production Dispatcher
Generates pre-filled Form-4A Art Releases, Trademark Placement Releases,
timecoded VFX paint/Greeking work orders, and NANPA script PII substitutions.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional
from app.models import (
    ClearanceFlag,
    ClearanceCategory,
    RiskLevel,
    VFXWorkOrder,
    LegalReleaseAgreement,
    ScriptFixDirective,
    RemediationPackage,
    UPL_LEGAL_DISCLAIMER,
)

logger = logging.getLogger("cineclear.remediation")

FORM_4A_TEMPLATE = """ENTERTAINMENT ARTWORK RELEASE AGREEMENT (FORM-4A)
PRODUCTION TITLE: {project_title}
DATE: {date_str}

1. PARTIES:
   - PRODUCER: Production Company & Assigns
   - LICENSOR / ARTIST: {rights_holder}
   - ARTWORK TITLE / DESCRIPTION: {property_description}

2. GRANT OF RIGHTS:
   Licensor hereby grants to Producer the non-exclusive, worldwide, perpetual right and license 
   to photograph, record, display, and reproduce the Artwork in connection with the Production, 
   its distribution, advertising, and promotion in all media now known or hereafter devised, 
   mitigating statutory liability under 17 U.S.C. § 106 and § 501.

3. REPRESENTATIONS & WARRANTIES:
   Licensor represents that they are the sole creator and copyright owner of the Artwork with full 
   authority to execute this release.

4. CONSIDERATION: Standard industry screen credit and/or agreed production consideration.

AGREED & ACCEPTED:
Licensor Signature: _______________________ Date: ______________
Producer Representative: __________________ Date: ______________

NOTICE: Decision-support analysis compiled for production counsel review. Does not constitute formal legal counsel or create an attorney-client relationship pursuant to State Bar regulations.
"""

TRADEMARK_PLACEMENT_TEMPLATE = """TRADEMARK PRODUCT PLACEMENT & RELEASE AGREEMENT
PRODUCTION TITLE: {project_title}
DATE: {date_str}

1. MARKS & PRODUCTS COVERED:
   - REGISTERED MARK / TRADE DRESS: {property_description}
   - TRADEMARK OWNER: {rights_holder}

2. USAGE AUTHORIZATION:
   Trademark Owner grants Producer authorization to depict the designated trademark and product 
   in the Production in a non-disparaging, nominative or contextual manner, fulfilling E&O 
   clearance standards under the Lanham Act (15 U.S.C. § 1125).

AGREED & ACCEPTED:
Brand Representative: _____________________ Date: ______________
Producer Representative: __________________ Date: ______________

NOTICE: Decision-support analysis compiled for production counsel review. Does not constitute formal legal counsel or create an attorney-client relationship pursuant to State Bar regulations.
"""


class RemediationAgent:
    """Harnessed Agent 3: Dispatches actionable deliverables across Production Departments."""

    def __init__(self):
        pass

    def generate_remediation_package(
        self,
        flags: List[ClearanceFlag],
        project_title: str = "Production"
    ) -> RemediationPackage:
        vfx_orders: List[VFXWorkOrder] = []
        releases: List[LegalReleaseAgreement] = []
        script_fixes: List[ScriptFixDirective] = []

        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        for flag in flags:
            # 1. Route Living Artist Visual Art -> Form-4A Legal Release & Backup VFX Blur
            if flag.category == ClearanceCategory.COPYRIGHTED_ART:
                holder = flag.verification.rights_holder_identified or "Artist / Rights Holder of Record"
                releases.append(
                    LegalReleaseAgreement(
                        form_type="Form-4A Artwork Release",
                        licensor_entity=holder,
                        property_description=f"{flag.detected_entity} ({flag.visual_description})",
                        governing_statute="17 U.S.C. § 106 / 17 U.S.C. § 501",
                        agreement_text=FORM_4A_TEMPLATE.format(
                            project_title=project_title,
                            date_str=date_str,
                            rights_holder=holder,
                            property_description=f"{flag.detected_entity} - {flag.visual_description}"
                        )
                    )
                )
                vfx_orders.append(
                    VFXWorkOrder(
                        timestamp_or_page=flag.timestamp_or_page,
                        target_entity=flag.detected_entity,
                        action_type="Digital Paint / Replacement Art Insertion",
                        tracking_notes=f"Planar track {flag.visual_description}. Replace with cleared stock asset if Form-4A is unexecuted.",
                        priority="HIGH" if flag.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] else "MEDIUM"
                    )
                )

            # 2. Route Trademarks -> Placement Release & VFX Greeking Work Order
            elif flag.category == ClearanceCategory.TRADEMARK_LOGO:
                holder = flag.verification.rights_holder_identified or f"{flag.detected_entity} Rights Holder"
                if flag.risk_level in [RiskLevel.HIGH, RiskLevel.MEDIUM]:
                    releases.append(
                        LegalReleaseAgreement(
                            form_type="Trademark Product Placement Release",
                            licensor_entity=holder,
                            property_description=flag.detected_entity,
                            governing_statute="Lanham Act (15 U.S.C. § 1114 / § 1125)",
                            agreement_text=TRADEMARK_PLACEMENT_TEMPLATE.format(
                                project_title=project_title,
                                date_str=date_str,
                                rights_holder=holder,
                                property_description=flag.detected_entity
                            )
                        )
                    )
                    vfx_orders.append(
                        VFXWorkOrder(
                            timestamp_or_page=flag.timestamp_or_page,
                            target_entity=flag.detected_entity,
                            action_type="2D Greeking / Logo Obscure",
                            tracking_notes=f"Track {flag.detected_entity} on {flag.visual_description}. Apply de-brand matte or 35% Gaussian Blur.",
                            priority="HIGH" if flag.risk_level == RiskLevel.HIGH else "MEDIUM"
                        )
                    )

            # 3. Route Real Phone Numbers / PII -> NANPA Non-Working Substitutions
            elif flag.category == ClearanceCategory.PHONE_PII:
                script_fixes.append(
                    ScriptFixDirective(
                        page_number=flag.timestamp_or_page,
                        original_text=flag.detected_entity,
                        recommended_replacement="212-555-0149 (NANPA Fictitious Range)",
                        rationale="Replaces active public switched telephone network number with FCC/NANPA safe theatrical range (555-0100 to 555-0199)."
                    )
                )

        return RemediationPackage(
            vfx_work_orders=vfx_orders,
            legal_releases=releases,
            script_fixes=script_fixes
        )
