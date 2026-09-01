"""
CineClear AI - Statutory Fair Use (17 U.S.C. § 107) & Multi-Territory Jurisdictional Engine
Calculates objective 4-factor fair use defense ratings and evaluates global distribution compliance.
"""

from typing import List, Optional
from app.models import (
    ClearanceCategory,
    FairUseFactor,
    FairUseScorecard,
    RiskLevel,
    TerritoryAssessment,
)


class FairUseAnalyzer:
    """Evaluates statutory fair use defenses and international copyright/trademark safe harbors."""

    @staticmethod
    def evaluate_fair_use(
        category: ClearanceCategory,
        entity_name: str,
        scene_context: str,
        risk_level: RiskLevel
    ) -> FairUseScorecard:
        """
        Computes statutory 4-factor scoring rubric under 17 U.S.C. § 107.
        Scores: 1 (Strongly favors rights holder) to 5 (Strong fair use defense).
        """
        ctx_lower = scene_context.lower()

        # 1. Purpose and Character of Use
        if "hero" in ctx_lower or "prominent" in ctx_lower:
            f1 = FairUseFactor(
                factor_name="Purpose & Character (17 U.S.C. § 107(1))",
                score=2,
                rationale="Commercial production context with prominent prop/wardrobe focus; commercial exploitation weighs against fair use."
            )
        else:
            f1 = FairUseFactor(
                factor_name="Purpose & Character (17 U.S.C. § 107(1))",
                score=3,
                rationale="Incidental background context in commercial media; intermediate transformative value."
            )

        # 2. Nature of the Copyrighted Work
        if category == ClearanceCategory.COPYRIGHTED_ART:
            f2 = FairUseFactor(
                factor_name="Nature of Work (17 U.S.C. § 107(2))",
                score=1,
                rationale="Original expressive visual fine art receives the highest tier of statutory copyright protection."
            )
        elif category == ClearanceCategory.TRADEMARK_LOGO:
            f2 = FairUseFactor(
                factor_name="Nature of Work (17 U.S.C. § 107(2))",
                score=3,
                rationale="Commercial mark and trade dress evaluated under nominative fair use doctrine rather than core expressive copyright."
            )
        else:
            f2 = FairUseFactor(
                factor_name="Nature of Work (17 U.S.C. § 107(2))",
                score=2,
                rationale="Expressive commercial asset with active statutory protections."
            )

        # 3. Amount and Substantiality of Portion Used
        if "background" in ctx_lower or "midground" in ctx_lower or "desk" in ctx_lower:
            f3 = FairUseFactor(
                factor_name="Amount & Substantiality (17 U.S.C. § 107(3))",
                score=3,
                rationale="Partial, out-of-focus, or contextual visual inclusion supports a de minimis defense argument."
            )
        else:
            f3 = FairUseFactor(
                factor_name="Amount & Substantiality (17 U.S.C. § 107(3))",
                score=1,
                rationale="Substantial, recognizable display of the whole asset in primary focal plane."
            )

        # 4. Effect on Potential Market or Value
        if category == ClearanceCategory.COPYRIGHTED_ART:
            f4 = FairUseFactor(
                factor_name="Market Impact (17 U.S.C. § 107(4))",
                score=2,
                rationale="Unlicensed depiction impacts the customary licensing market for movie/set artwork display."
            )
        elif category == ClearanceCategory.TRADEMARK_LOGO:
            f4 = FairUseFactor(
                factor_name="Market Impact (17 U.S.C. § 107(4))",
                score=4,
                rationale="Depiction does not create a competing commercial product or substitute for brand's core business."
            )
        else:
            f4 = FairUseFactor(
                factor_name="Market Impact (17 U.S.C. § 107(4))",
                score=2,
                rationale="Potential exposure to customary licensing and clearance market harm."
            )

        # Composite computation
        composite = round((f1.score + f2.score + f3.score + f4.score) / 4.0, 2)
        if composite >= 3.5:
            defense_rating = "STRONG DEFENSE (DE MINIMIS / NOMINATIVE FAIR USE)"
        elif composite >= 2.5:
            defense_rating = "MODERATE DEFENSE (E&O UNDERWRITER SCRUTINY REQUIRED)"
        else:
            defense_rating = "HIGH LITIGATION RISK (NO STATUTORY SAFE HARBOR)"

        return FairUseScorecard(
            purpose_and_character=f1,
            nature_of_work=f2,
            amount_and_substantiality=f3,
            market_harm=f4,
            composite_score=composite,
            defense_rating=defense_rating
        )

    @staticmethod
    def evaluate_territories(
        category: ClearanceCategory,
        entity_name: str,
        risk_level: RiskLevel
    ) -> List[TerritoryAssessment]:
        """Maps global legal clearance requirements across major distribution territories."""
        if category == ClearanceCategory.COPYRIGHTED_ART:
            return [
                TerritoryAssessment(
                    territory="United States",
                    clearance_status="EXPLICIT RELEASE REQUIRED",
                    governing_statute="17 U.S.C. § 106 & § 501",
                    jurisdictional_notes="US copyright law provides no blanket incidental inclusion exemption for fine art on film sets (Form-4A required)."
                ),
                TerritoryAssessment(
                    territory="United Kingdom",
                    clearance_status="INCIDENTAL SAFE HARBOR",
                    governing_statute="CDPA 1988 § 31",
                    jurisdictional_notes="Section 31 of Copyright, Designs and Patents Act provides broad statutory safe harbor for incidental inclusion of artistic works in film."
                ),
                TerritoryAssessment(
                    territory="European Union",
                    clearance_status="MEMBER STATE SPECIFIC",
                    governing_statute="EU InfoSoc Directive Art 5(3)(i)",
                    jurisdictional_notes="Incidental inclusion exceptions vary across EU member states; theatrical distribution requires pan-European clearance."
                ),
                TerritoryAssessment(
                    territory="Canada",
                    clearance_status="INCIDENTAL INCLUSION EXEMPTION",
                    governing_statute="Copyright Act (R.S.C. c. C-42) § 30.7",
                    jurisdictional_notes="Section 30.7 explicitly permits incidental and non-deliberate inclusion of visual artwork in media recordings."
                )
            ]
        elif category == ClearanceCategory.TRADEMARK_LOGO:
            return [
                TerritoryAssessment(
                    territory="United States",
                    clearance_status="NOMINATIVE FAIR USE / PRODUCT PLACEMENT",
                    governing_statute="Lanham Act 15 U.S.C. § 1114 / § 1125",
                    jurisdictional_notes="Nominative fair use permits incidental depiction unless false endorsement, tarnishment, or dilution is demonstrated."
                ),
                TerritoryAssessment(
                    territory="United Kingdom",
                    clearance_status="HONEST PRACTICES DEFENSE",
                    governing_statute="Trade Marks Act 1994 § 11(2)",
                    jurisdictional_notes="Depiction permitted provided use complies with honest commercial practices and does not take unfair advantage of distinctive character."
                ),
                TerritoryAssessment(
                    territory="European Union",
                    clearance_status="EU TRADE MARK REGULATION (EUTMR)",
                    governing_statute="Regulation (EU) 2017/1001 Art 14",
                    jurisdictional_notes="Strict enforcement against dilution for marks with high reputation across EU member states; greeking recommended for hero props."
                ),
                TerritoryAssessment(
                    territory="Canada",
                    clearance_status="TRADEMARKS ACT COMPLIANT",
                    governing_statute="Trademarks Act (R.S.C. 1985, c. T-13) § 22",
                    jurisdictional_notes="Depiction actionable only if it depreciates the value of the goodwill attached to the trademark."
                )
            ]
        else:
            return [
                TerritoryAssessment(
                    territory="United States",
                    clearance_status="STATUTORY COMPLIANCE MANDATE",
                    governing_statute="FCC / NANPA Regulations & Restatement (Second) of Torts",
                    jurisdictional_notes="Strict privacy and telecommunications safe-harbor standards require 555-01XX range."
                ),
                TerritoryAssessment(
                    territory="United Kingdom & EU",
                    clearance_status="GDPR & OFCOM COMPLIANCE",
                    governing_statute="UK GDPR / EU GDPR Art 6 & OFCOM Drama Code",
                    jurisdictional_notes="Displaying unallocated living individual contact information triggers statutory personal data liability."
                )
            ]
