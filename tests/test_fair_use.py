import pytest
from app.fair_use_analyzer import FairUseAnalyzer
from app.models import ClearanceCategory, RiskLevel


def test_fair_use_scorecard_calculation():
    # Test fine art (low fair use, high litigation risk under 17 U.S.C. 106)
    scorecard_art = FairUseAnalyzer.evaluate_fair_use(
        category=ClearanceCategory.COPYRIGHTED_ART,
        entity_name="Modern Abstract Oil Canvas",
        scene_context="Large orange canvas mounted on the upper-left wall",
        risk_level=RiskLevel.HIGH
    )
    assert scorecard_art.composite_score < 3.0
    assert "HIGH LITIGATION RISK" in scorecard_art.defense_rating
    assert scorecard_art.nature_of_work.score == 1

    # Test incidental trademark
    scorecard_tm = FairUseAnalyzer.evaluate_fair_use(
        category=ClearanceCategory.TRADEMARK_LOGO,
        entity_name="Starbucks Cup",
        scene_context="Incidental white paper cup in background on desk",
        risk_level=RiskLevel.MEDIUM
    )
    assert scorecard_tm.composite_score >= 3.0
    assert scorecard_tm.market_harm.score == 4


def test_territory_matrix_resolutions():
    terr_art = FairUseAnalyzer.evaluate_territories(
        category=ClearanceCategory.COPYRIGHTED_ART,
        entity_name="Modern Abstract Oil Canvas",
        risk_level=RiskLevel.HIGH
    )
    assert len(terr_art) == 4
    
    # Assert statutory distinctions
    us_statute = next(t for t in terr_art if t.territory == "United States")
    uk_statute = next(t for t in terr_art if t.territory == "United Kingdom")
    
    assert "17 U.S.C. § 106" in us_statute.governing_statute
    assert us_statute.clearance_status == "EXPLICIT RELEASE REQUIRED"
    assert "CDPA 1988 § 31" in uk_statute.governing_statute
    assert uk_statute.clearance_status == "INCIDENTAL SAFE HARBOR"
