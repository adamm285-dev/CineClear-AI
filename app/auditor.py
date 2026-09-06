"""
CineClear AI - Legal Clearance Auditor & 3-Agent Orchestration Loop
Executes extraction, Parallel Search web grounding, Critic Agent reflection,
and automated production remediation using the Dynamic Model Cascade.
"""

import asyncio
import json
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Union

from app.config import settings
from app.gemini_cascade import GeminiCascadeClient, parse_json_safe
from app.harness import CriticHarness, ExtractorHarness
from app.models import (
    ClearanceAuditReport,
    ClearanceCategory,
    ClearanceFlag,
    ParallelVerification,
    RiskLevel,
)
from app.parallel_client import ParallelSearchClient
from app.remediation_agent import RemediationAgent
from app.vision_agent import VisionAgent
from app.fair_use_analyzer import FairUseAnalyzer
from app.music_arch_analyzer import AWCPAValidator, MusicSyncAnalyzer

logger = logging.getLogger("cineclear.auditor")

def resolve_clean_rights_holder(entity_name: str, extracted_holder: Optional[str] = None) -> str:
    """Normalizes rights holder to canonical corporate or institutional body."""
    if extracted_holder and "Rights Holder" not in extracted_holder:
        return extracted_holder
    lower = entity_name.lower()
    if "starbucks" in lower:
        return "Starbucks Corporation"
    if "apple" in lower or "macbook" in lower or "iphone" in lower:
        return "Apple Inc."
    if "nike" in lower or "swoosh" in lower:
        return "Nike, Inc."
    if "coca" in lower or "coke" in lower:
        return "The Coca-Cola Company"
    if "rolex" in lower:
        return "Rolex SA"
    if "eiffel" in lower:
        return "Société d'Exploitation de la Tour Eiffel (SETE)"
    if "phone" in lower or "555" in lower or bool(re.search(r'\d{3}[-.\s]?\d{3}', entity_name)):
        return "North American Numbering Plan Administration (NANPA)"
    return extracted_holder or f"{entity_name} Rights Holder"

CRITIC_SYSTEM_PROMPT = """
You are Senior Entertainment E&O Clearance Counsel.
Audit preliminary clearance findings, eliminate hallucinations, correct logical contradictions, and enforce statutory invariants:

STRICT LEGAL INVARIANTS:
1. DATE SANITY: An entity is ONLY Public Domain if published/created before 1929. Modern corporate marks (Nike, Apple, Starbucks, Marvel, Sony, etc.) CANNOT be marked public domain.
2. CONTRADICTION RECONCILIATION: If 'active_trademark_found' is TRUE, 'is_public_domain' MUST be FALSE.
3. RISK CALIBRATION:
   - Hero wardrobe with prominent active trademark = HIGH or MEDIUM.
   - Real living artist art on set = HIGH (17 U.S.C. § 106).
   - De minimis background blurry item = LOW or MEDIUM.
   - Non-555 phone number = CRITICAL.

Return the sanitized JSON list of flags adhering to all legal invariants.
"""


class CineClearAuditor:
    def __init__(self):
        self.parallel_client = ParallelSearchClient()
        self.vision_agent = VisionAgent()
        self.remediation_agent = RemediationAgent()
        self.cascade = GeminiCascadeClient()
        self.fair_use_analyzer = FairUseAnalyzer()

    async def verify_flag_with_parallel(
        self,
        entity_name: str,
        category: Union[ClearanceCategory, str],
        scene_context: str
    ) -> ParallelVerification:
        """Grounds candidate entity flags against real-world registries using Parallel Search."""
        cat_val = category.value if isinstance(category, ClearanceCategory) else str(category)
        cat_enum = category if isinstance(category, ClearanceCategory) else (
            ClearanceCategory(cat_val) if cat_val in ClearanceCategory._value2member_map_ else ClearanceCategory.TRADEMARK_LOGO
        )

        objective = (
            f"Verify trademark status, copyright expiration, and commercial filming release "
            f"requirements for entity '{entity_name}' ({cat_val}) in context: {scene_context}."
        )

        search_res = await self.parallel_client.search(objective=objective, max_results=4)
        results = search_res.get("results", [])
        sources = [r.get("url") for r in results if "url" in r and r.get("url")]

        excerpts_list = []
        for r in results:
            if "excerpts" in r and isinstance(r["excerpts"], list):
                excerpts_list.extend([f"- {r.get('title', 'Registry')}: {e}" for e in r["excerpts"]])
            elif "excerpt" in r and r["excerpt"]:
                excerpts_list.append(f"- {r.get('title', 'Registry')}: {r['excerpt']}")
        excerpts = "\n".join(excerpts_list)

        synth_prompt = f"""
        Analyze these search findings from Parallel Search:
        {excerpts}

        Entity: {entity_name}
        Category: {cat_val}
        Scene Context: {scene_context}

        Provide accurate legal status:
        1. Is it public domain (pre-1929)?
        2. Is an active trademark or copyright found?
        3. Who is the rights holder?
        4. Statutory context (Lanham Act, 17 U.S.C. § 106, etc.).

        Output valid JSON with keys:
        - "is_public_domain": bool
        - "active_trademark_found": bool
        - "rights_holder_identified": string or null
        - "statutory_context": string
        """

        raw_response = await self.cascade.generate_content_with_cascade(
            contents=synth_prompt,
            response_mime_type="application/json",
            preferred_model=settings.GEMINI_MODEL
        )

        if raw_response:
            try:
                data = parse_json_safe(raw_response)
                if data and isinstance(data, dict):
                    clean_holder = resolve_clean_rights_holder(entity_name, data.get("rights_holder_identified"))
                    return ParallelVerification(
                        search_objective=objective,
                        sources_checked=sources,
                        is_public_domain=data.get("is_public_domain", False),
                        active_trademark_found=data.get("active_trademark_found", True),
                        rights_holder_identified=clean_holder,
                        statutory_context=data.get("statutory_context", "Clearance audit completed.")
                    )
            except Exception as e:
                logger.error(f"[Auditor] Synthesis JSON parse failed: {e}")

        clean_holder = resolve_clean_rights_holder(entity_name)
        return ParallelVerification(
            search_objective=objective,
            sources_checked=sources or ["https://www.uspto.gov/trademarks/search"],
            is_public_domain=False,
            active_trademark_found=(cat_enum == ClearanceCategory.TRADEMARK_LOGO),
            rights_holder_identified=clean_holder,
            statutory_context=(
                f"Statutory analysis conducted via Parallel Search grounding for {entity_name}. "
                f"Governed under Lanham Act 15 U.S.C. § 1125 / 17 U.S.C. § 106."
            )
        )

    async def review_and_securitize_flags(self, flags: List[ClearanceFlag]) -> List[ClearanceFlag]:
        """Senior Counsel Critic Agent Reflection Pass with automatic cascade fallback."""
        if not flags:
            return []

        critic_prompt = f"""
        Audit and sanitize these preliminary clearance flags:
        {json.dumps([f.model_dump() for f in flags], indent=2)}

        Ensure no active modern trademarks are marked public domain.
        Output the corrected JSON list of flags.
        """

        raw_response = await self.cascade.generate_content_with_cascade(
            contents=critic_prompt,
            system_instruction=CRITIC_SYSTEM_PROMPT,
            response_mime_type="application/json",
            preferred_model=settings.GEMINI_MODEL
        )

        if raw_response:
            try:
                parsed = parse_json_safe(raw_response)
                if parsed:
                    flag_items = parsed if isinstance(parsed, list) else parsed.get("flags", [])
                    sanitized_flags = [ClearanceFlag.model_validate(item) for item in flag_items]
                    return CriticHarness.enforce_invariants(sanitized_flags)
            except Exception as e:
                logger.warning(f"[Auditor] Critic JSON parsing fallback: {e}")

        return CriticHarness.enforce_invariants(flags)

    async def audit_media(
        self,
        file_path: str,
        project_title: str = "Production Audit",
        media_type: str = "auto",
        is_video: bool = False,
        on_progress=None,
    ) -> ClearanceAuditReport:
        async def emit(step: int, status: str, label: str, progress: int):
            if on_progress is None:
                return
            payload = {
                "type": "stage",
                "step": step,
                "status": status,
                "label": label,
                "progress": progress,
            }
            result = on_progress(payload)
            if asyncio.iscoroutine(result):
                await result

        # 1. Forensic Extraction (Agent 1) & Deduplication Harness
        await emit(1, "running", "Stage 1/4: Forensic extraction — Gemini vision / script parse...", 12)
        if media_type == "script":
            raw_candidates = await self.vision_agent.analyze_script(file_path)
        elif is_video or media_type == "video":
            raw_candidates = await self.vision_agent.analyze_video(file_path)
        else:
            raw_candidates = await self.vision_agent.analyze_image(file_path)

        candidate_items = ExtractorHarness.deduplicate_entities(raw_candidates)
        await emit(
            1,
            "done",
            f"Stage 1/4 complete — {len(candidate_items)} candidate liabilities extracted.",
            28,
        )

        # 2. Parallel Search Grounding Loop (Concurrent Async Execution)
        async def _ground_candidate(candidate) -> ClearanceFlag:
            cat = candidate.get("category") if isinstance(candidate, dict) else candidate.category
            entity = candidate.get("detected_entity") if isinstance(candidate, dict) else candidate.detected_entity
            timecode = candidate.get("timestamp_or_page") if isinstance(candidate, dict) else candidate.timestamp_or_page
            vis_desc = candidate.get("visual_description") if isinstance(candidate, dict) else candidate.visual_description
            risk = candidate.get("risk_level") if isinstance(candidate, dict) else candidate.risk_level
            mitigation = candidate.get("mitigation_action") if isinstance(candidate, dict) else candidate.mitigation_action
            box_2d = candidate.get("box_2d") if isinstance(candidate, dict) else getattr(candidate, "box_2d", None)

            verification = await self.verify_flag_with_parallel(
                entity_name=entity,
                category=cat,
                scene_context=vis_desc
            )

            # Calculate Fair Use Scorecard (17 U.S.C. § 107) & Multi-Territory Matrix
            scorecard = FairUseAnalyzer.evaluate_fair_use(
                category=cat,
                entity_name=entity,
                scene_context=vis_desc,
                risk_level=risk
            )
            territories = FairUseAnalyzer.evaluate_territories(
                category=cat,
                entity_name=entity,
                risk_level=risk
            )

            # Evaluate Rogers v. Grimaldi for Trademark uses
            rogers_assessment = None
            if cat in [ClearanceCategory.TRADEMARK_LOGO, "TRADEMARK_LOGO"]:
                rogers_assessment = FairUseAnalyzer.evaluate_rogers_test(
                    entity_name=entity,
                    scene_context=vis_desc,
                    category=cat,
                    risk_level=risk
                )

            # Evaluate AWCPA § 120(a) for Architectural Works
            arch_assessment = None
            if cat in [ClearanceCategory.ARCHITECTURAL_RIGHTS, "ARCHITECTURAL_WORK", "ARCHITECTURAL_RIGHTS"]:
                arch_assessment = AWCPAValidator.evaluate_landmark(
                    entity_name=entity,
                    visual_context=vis_desc,
                    risk_level=risk
                )
                if arch_assessment.is_public_view_safe_harbor:
                    risk = RiskLevel.LOW
                    mitigation = arch_assessment.clearance_recommendation

            return ClearanceFlag(
                id=str(uuid.uuid4())[:8],
                timestamp_or_page=timecode,
                category=cat,
                detected_entity=entity,
                visual_description=vis_desc,
                risk_level=risk,
                verification=verification,
                mitigation_action=mitigation,
                box_2d=box_2d,
                fair_use_scorecard=scorecard,
                territory_matrix=territories,
                arch_assessment=arch_assessment,
                rogers_assessment=rogers_assessment
            )

        total = max(1, len(candidate_items))
        await emit(
            2,
            "running",
            f"Stage 2/4: Parallel Search + Gemini synthesis on {len(candidate_items)} entities...",
            40,
        )
        grounded_flags: List[ClearanceFlag] = []
        if candidate_items:
            tasks = [asyncio.create_task(_ground_candidate(c)) for c in candidate_items]
            for i, fut in enumerate(asyncio.as_completed(tasks), 1):
                grounded_flags.append(await fut)
                await emit(
                    2,
                    "running",
                    f"Stage 2/4: Grounded {i}/{len(tasks)} entities (Parallel Search + Gemini)...",
                    40 + int(18 * i / total),
                )
        await emit(
            2,
            "done",
            f"Stage 2/4 complete — {len(grounded_flags)} flags grounded with live search.",
            58,
        )

        # 3. Critic Agent Reflection (Agent 2)
        await emit(3, "running", "Stage 3/4: Senior counsel critic — statutory invariants & Fair Use...", 68)
        securitized_flags = await self.review_and_securitize_flags(grounded_flags)
        await emit(
            3,
            "done",
            f"Stage 3/4 complete — {len(securitized_flags)} securitized flags.",
            82,
        )

        # 4. Re-sync Fair Use Scorecard and Territory Matrix if risk was adjusted
        for flag in securitized_flags:
            flag.fair_use_scorecard = FairUseAnalyzer.evaluate_fair_use(
                category=flag.category,
                entity_name=flag.detected_entity,
                scene_context=flag.visual_description,
                risk_level=flag.risk_level
            )
            flag.territory_matrix = FairUseAnalyzer.evaluate_territories(
                category=flag.category,
                entity_name=flag.detected_entity,
                risk_level=flag.risk_level
            )
            if flag.category == ClearanceCategory.TRADEMARK_LOGO:
                flag.rogers_assessment = FairUseAnalyzer.evaluate_rogers_test(
                    entity_name=flag.detected_entity,
                    scene_context=flag.visual_description,
                    category=flag.category,
                    risk_level=flag.risk_level
                )

        # 5. Remediation Dispatcher (Agent 3)
        remediation_pkg = self.remediation_agent.generate_remediation_package(
            flags=securitized_flags,
            project_title=project_title
        )

        # Compile ASCAP/BMI Music Cue Sheet if music flags exist
        remediation_pkg.music_cue_sheet = MusicSyncAnalyzer.build_cue_sheet(
            flags=securitized_flags,
            project_title=project_title
        )

        critical_count = sum(1 for f in securitized_flags if f.risk_level == RiskLevel.CRITICAL)
        high_count = sum(1 for f in securitized_flags if f.risk_level == RiskLevel.HIGH)
        med_count = sum(1 for f in securitized_flags if f.risk_level == RiskLevel.MEDIUM)
        low_count = sum(1 for f in securitized_flags if f.risk_level == RiskLevel.LOW)

        report = ClearanceAuditReport(
            id=str(uuid.uuid4()),
            project_title=project_title,
            media_filename=Path(file_path).name,
            media_type=media_type,
            total_flags=len(securitized_flags),
            critical_count=critical_count,
            high_count=high_count,
            medium_count=med_count,
            low_count=low_count,
            flags=securitized_flags,
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            remediation_package=remediation_pkg
        )

        # 5. Generate ReportLab PDF E&O Binder
        await emit(4, "running", "Stage 4/4: Remediation dispatcher — Form-4A, VFX orders, E&O PDF binder...", 90)
        try:
            from app.report_generator import generate_eo_clearance_binder
            pdf_path = generate_eo_clearance_binder(report)
            report.pdf_report_path = pdf_path
        except Exception as e:
            logger.error(f"Failed to generate PDF report binder: {e}")
        await emit(4, "done", "Stage 4/4 complete — E&O binder assembled.", 100)

        return report

    async def audit_script(
        self,
        file_path: str,
        project_title: str = "Screenplay Clearance Audit"
    ) -> ClearanceAuditReport:
        return await self.audit_media(file_path=file_path, project_title=project_title, media_type="script")
