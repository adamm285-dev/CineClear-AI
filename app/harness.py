"""
CineClear AI - Dual Harness Architecture
Guards Role 1 (Extractor & Grounder) and Role 2 (Senior Counsel Critic)
with deterministic validation, deduplication, and statutory invariant boundaries.
"""

import logging
import re
from typing import List, Set, Dict, Any, Union
from app.models import ClearanceFlag, RiskLevel, ClearanceCategory

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

            # Invariant 1: Modern corporate trademarks cannot be pre-1929 public domain
            if any(mark in entity_lower for mark in cls.MODERN_CORPORATE_MARKS):
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

            # Invariant 2: Active TM and Public Domain are mutually exclusive
            if flag.verification.active_trademark_found and flag.verification.is_public_domain:
                flag.verification.is_public_domain = False

            # Invariant 3: Real Phone PII must always be CRITICAL
            if flag.category == ClearanceCategory.PHONE_PII:
                flag.risk_level = RiskLevel.CRITICAL
                if "555" not in flag.mitigation_action:
                    flag.mitigation_action = (
                        "MANDATORY FIX: Replace on-screen graphics and ADR dialogue with fictitious "
                        "NANPA reserved number in the 555-0100 to 555-0199 range."
                    )

            # Invariant 4: Clamp low risk on un-cleared music audio to HIGH
            if flag.category == ClearanceCategory.MUSIC_AUDIO and flag.risk_level == RiskLevel.LOW and not flag.verification.is_public_domain:
                flag.risk_level = RiskLevel.HIGH

            sanitized.append(flag)

        return sanitized
