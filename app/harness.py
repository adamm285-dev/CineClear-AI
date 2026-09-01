"""
CineClear AI - Dual Harness Architecture
Guards Role 1 (Extractor & Grounder) and Role 2 (Senior Counsel Critic)
with deterministic validation, deduplication, and statutory invariant boundaries.
"""

import logging
import re
from typing import List, Set, Dict, Any, Union, Optional
from app.models import (
    ClearanceFlag,
    RiskLevel,
    ClearanceCategory,
    UPL_LEGAL_DISCLAIMER,
    RogersTestAssessment,
)
from app.fair_use_analyzer import FairUseAnalyzer

logger = logging.getLogger("cineclear.harness")


class ExtractorHarness:
    """Guards Role 1: Ingest, Entity Extraction, and Search Dispatch."""

    @staticmethod
    def sanitize_and_deduplicate(candidates: List[Union[Dict[str, Any], Any]]) -> List[Dict[str, Any]]:
        """Convenience method combining deduplication and coordinate/field sanitization."""
        return ExtractorHarness.deduplicate_entities(candidates)

    @staticmethod
    def deduplicate_entities(candidates: List[Union[Dict[str, Any], Any]]) -> List[Dict[str, Any]]:
        """
        Prevents duplicate Parallel Search API calls and token waste
        across recurring video keyframes and repeated script mentions.
        """
        seen: Set[str] = set()
        unique_candidates: List[Dict[str, Any]] = []

        for c in candidates:
            if isinstance(c, dict):
                cat = c.get("category", "TRADEMARK_LOGO")
                entity = c.get("detected_entity", "").strip().lower()
                candidate_dict = c
            else:
                cat = getattr(c, "category", "TRADEMARK_LOGO")
                entity = getattr(c, "detected_entity", "").strip().lower()
                candidate_dict = c.model_dump() if hasattr(c, "model_dump") else dict(c)

            # Normalize entity name (strip special punctuation for deduplication key)
            clean_entity = re.sub(r'[^a-z0-9]', '', entity)
            cat_str = cat.value if hasattr(cat, "value") else str(cat)
            key = f"{cat_str}_{clean_entity}"

            if key not in seen and clean_entity:
                seen.add(key)
                unique_candidates.append(ExtractorHarness.sanitize_candidate(candidate_dict))

        return unique_candidates

    @staticmethod
    def sanitize_candidate(raw: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes timecodes, strips invalid values, and ensures required fields exist."""
        # Ensure timestamp/page format
        timecode = str(raw.get("timestamp_or_page") or "00:00:01").strip()
        if not timecode:
            timecode = "00:00:01"
        raw["timestamp_or_page"] = timecode

        # Ensure detected entity exists
        entity = str(raw.get("detected_entity") or "Unidentified Visual Entity").strip()
        if not entity:
            entity = "Unidentified Visual Entity"
        raw["detected_entity"] = entity

        # Ensure visual description exists
        if not raw.get("visual_description"):
            raw["visual_description"] = f"Visual depiction of {entity} in scene."

        # Sanitize and clamp box_2d coordinates to [0, 1000]
        box = raw.get("box_2d")
        if box and isinstance(box, list) and len(box) == 4:
            try:
                ymin, xmin, ymax, xmax = [max(0, min(1000, int(v))) for v in box]
                if ymin > ymax:
                    ymin, ymax = ymax, ymin
                if xmin > xmax:
                    xmin, xmax = xmax, xmin
                raw["box_2d"] = [ymin, xmin, ymax, xmax]
            except (ValueError, TypeError):
                raw["box_2d"] = None

        return raw


class CriticHarness:
    """Guards Role 2: Statutory Verification, Invariants, and Fallback Sanitization."""

    MODERN_CORPORATE_MARKS = {
        "nike", "apple", "starbucks", "coca-cola", "pepsi",
        "disney", "macbook", "swoosh", "sony", "ford", "chevy",
        "rolex", "louis vuitton", "gucci", "microsoft", "google",
        "amazon", "target", "walmart", "adidas", "red bull"
    }

    # Statutory Criminal Symbol & Emblem Bans (18 U.S.C. §§ 701, 706, 712)
    STATUTORY_SEAL_REGEX = re.compile(
        r"\b(red\s*cross|geneva\s*cross|fbi\s*badge|fbi\s*seal|cia\s*seal|secret\s*service\s*seal|"
        r"federal\s*badge|police\s*badge\s*replica|us\s*marshal\s*seal|dea\s*badge)\b",
        re.IGNORECASE
    )

    # RFC 2606 Reserved Safe Fictional Domains
    RFC_2606_RESERVED_DOMAINS = {
        "example.com", "example.org", "example.net", "example.edu",
        "localhost", "test", "invalid", "example"
    }
    RFC_2606_RESERVED_TLDS = {".example", ".invalid", ".localhost", ".test"}

    # Real Web Domain / URL Regex
    WEB_DOMAIN_REGEX = re.compile(
        r"\b([a-zA-Z0-9][-a-zA-Z0-9]*\.(?:com|org|net|io|co|ai|tv|gov|edu|uk|ca|de|fr|app))\b",
        re.IGNORECASE
    )

    # Prop Currency Regex (18 U.S.C. § 504)
    PROP_CURRENCY_REGEX = re.compile(
        r"\b(cash|dollar\s*bill|banknote|paper\s*money|currency\s*prop|100\s*dollar\s*bill|stack\s*of\s*cash|stack\s*of\s*money|us\s*currency)\b",
        re.IGNORECASE
    )

    @classmethod
    def enforce_invariants(cls, flags: List[ClearanceFlag]) -> List[ClearanceFlag]:
        """
        Deterministic Rule Engine (Runs regardless of whether LLM passes or fails).
        Guarantees zero invalid statutory claims or hallucinated public domain statuses
        reach the final E&O PDF Binder.
        """
        sanitized: List[ClearanceFlag] = []
        for flag in flags:
            entity_lower = flag.detected_entity.lower()
            vis_lower = flag.visual_description.lower()
            full_text = f"{flag.detected_entity} {flag.visual_description}".lower()

            # -------------------------------------------------------------
            # Invariant 1: Statutory Criminal Symbol & Emblem Bans (18 U.S.C. §§ 701, 706, 712)
            # -------------------------------------------------------------
            if cls.STATUTORY_SEAL_REGEX.search(full_text):
                flag.risk_level = RiskLevel.CRITICAL
                flag.verification.active_trademark_found = True
                flag.verification.is_public_domain = False
                flag.mitigation_action = (
                    "CRITICAL STATUTORY BAN (18 U.S.C. § 706 / § 701): Red Cross emblem / Federal law enforcement "
                    "seal is prohibited by federal criminal statute regardless of Fair Use. Replace with fictionalized prop "
                    "(e.g. green first-aid cross, fictional police department title)."
                )

            # -------------------------------------------------------------
            # Invariant 2: Modern corporate trademarks cannot be pre-1929 public domain
            # -------------------------------------------------------------
            elif any(mark in entity_lower for mark in cls.MODERN_CORPORATE_MARKS):
                flag.verification.is_public_domain = False
                flag.verification.active_trademark_found = True
                if any(w in vis_lower for w in ["wardrobe", "hero", "apparel", "clothing", "hoodie", "shirt"]):
                    flag.risk_level = RiskLevel.HIGH
                elif flag.risk_level == RiskLevel.LOW:
                    flag.risk_level = RiskLevel.MEDIUM
                if "public domain" in flag.mitigation_action.lower() or flag.mitigation_action.strip() in ("", "None", "none"):
                    flag.mitigation_action = (
                        "RECOMMENDED ACTION: Verify incidental de minimis use; if featured prominently "
                        "as hero prop/wardrobe, obtain written Product Placement Release or Greek logo in VFX."
                    )

            # -------------------------------------------------------------
            # Invariant 3: Active TM and Public Domain are mutually exclusive
            # -------------------------------------------------------------
            if flag.verification.active_trademark_found and flag.verification.is_public_domain:
                flag.verification.is_public_domain = False

            # -------------------------------------------------------------
            # Invariant 4: Real Phone PII must always be CRITICAL (NANPA Safe Harbor)
            # -------------------------------------------------------------
            if flag.category == ClearanceCategory.PHONE_PII:
                flag.risk_level = RiskLevel.CRITICAL
                if "555" not in flag.mitigation_action:
                    flag.mitigation_action = (
                        "MANDATORY FIX: Replace on-screen graphics and ADR dialogue with fictitious "
                        "NANPA reserved number in the 555-0100 to 555-0199 range."
                    )

            # -------------------------------------------------------------
            # Invariant 5: Fictional Web & Domain Safe Harbors (RFC 2606)
            # -------------------------------------------------------------
            domain_matches = cls.WEB_DOMAIN_REGEX.findall(full_text)
            for d in domain_matches:
                d_clean = d.lower()
                is_rfc_safe = (
                    d_clean in cls.RFC_2606_RESERVED_DOMAINS
                    or any(d_clean.endswith(tld) for tld in cls.RFC_2606_RESERVED_TLDS)
                )
                if not is_rfc_safe:
                    if flag.risk_level in (RiskLevel.LOW, RiskLevel.MEDIUM):
                        flag.risk_level = RiskLevel.HIGH
                    if "rfc 2606" not in flag.mitigation_action.lower():
                        flag.mitigation_action = (
                            f"MANDATORY FIX (RFC 2606 Safe Harbor): Real web domain '{d}' detected. "
                            f"Replace on-screen graphics and dialogue with RFC 2606 reserved fictional domain "
                            f"(e.g. example.com, test.example) to prevent cyber-trespass and trademark dilution."
                        )
                    break

            # -------------------------------------------------------------
            # Invariant 6: Architectural Works Safe Harbor (17 U.S.C. § 120(a) AWCPA)
            # -------------------------------------------------------------
            is_arch = (
                flag.category == ClearanceCategory.ARCHITECTURAL_RIGHTS
                or any(w in entity_lower for w in ["building", "facade", "skyline", "tower", "bridge", "monument", "exterior structure"])
                or any(w in vis_lower for w in ["exterior building", "city skyline", "street view", "public street", "visible from public"])
            )
            if is_arch:
                is_restricted_lighting = "eiffel" in full_text and ("night" in full_text or "illumination" in full_text or "light" in full_text)
                if not is_restricted_lighting:
                    flag.risk_level = RiskLevel.LOW
                    if "120(a)" not in flag.mitigation_action:
                        flag.mitigation_action = (
                            "EXEMPT (17 U.S.C. § 120(a) AWCPA Safe Harbor): Photographing or filming a completed building "
                            "located in or ordinarily visible from a public place is explicitly non-infringing."
                        )

            # -------------------------------------------------------------
            # Invariant 7: Prop Currency Compliance (18 U.S.C. § 504 / Counterfeit Detection Act)
            # -------------------------------------------------------------
            if cls.PROP_CURRENCY_REGEX.search(full_text):
                if flag.risk_level == RiskLevel.LOW:
                    flag.risk_level = RiskLevel.MEDIUM
                if "504" not in flag.mitigation_action:
                    flag.mitigation_action = (
                        "PROP CURRENCY MANDATE (18 U.S.C. § 504): Verify prop vendor certified single-sided motion "
                        "picture money under 18 U.S.C. § 504 (must be <75% or >150% size or marked 'FOR MOTION PICTURE USE ONLY')."
                    )

            # -------------------------------------------------------------
            # Invariant 8: Clamp low risk on un-cleared music audio to HIGH
            # -------------------------------------------------------------
            if flag.category == ClearanceCategory.MUSIC_AUDIO and flag.risk_level == RiskLevel.LOW and not flag.verification.is_public_domain:
                flag.risk_level = RiskLevel.HIGH

            # -------------------------------------------------------------
            # Invariant 9: The Rogers v. Grimaldi Artistic Relevance Evaluation
            # -------------------------------------------------------------
            if flag.category == ClearanceCategory.TRADEMARK_LOGO and not flag.rogers_assessment:
                flag.rogers_assessment = FairUseAnalyzer.evaluate_rogers_test(
                    entity_name=flag.detected_entity,
                    scene_context=flag.visual_description,
                    category=flag.category,
                    risk_level=flag.risk_level
                )

            sanitized.append(flag)

        return sanitized
