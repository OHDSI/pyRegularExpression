# tests/test_statistical_analysis_primary_analysis_finder.py
"""
Pytest suite for statistical_analysis_primary_analysis_finder.py
Ladder v1–v5:
    • v1 – primary endpoint/outcome + analysis verb OR ITT/per-protocol phrase
    • v2 – v1 + statistical test/model nearby
    • v3 – only inside Statistical Analysis / Primary Analysis heading block
    • v4 – v2 + adjustment phrase / modelling details nearby
    • v5 – tight template
"""
import pytest
from pyregularexpression.statistical_analysis_primary_analysis_finder import (
    find_statistical_analysis_primary_analysis_v1,
    find_statistical_analysis_primary_analysis_v2,
    find_statistical_analysis_primary_analysis_v3,
    find_statistical_analysis_primary_analysis_v4,
    find_statistical_analysis_primary_analysis_v5,
)

# ─────────────────────────────
# v1 – high recall
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The primary endpoint was analysed using standard methods.", True, "v1_pos_endpoint_analysed"),
        ("The primary outcome was assessed in a per-protocol population.", True, "v1_pos_itt_phrase"),
        ("Secondary outcomes analysed descriptively.", False, "v1_neg_secondary_only"),
    ],
)
def test_v1_primary_analysis(text, should_match, test_id):
    matches = find_statistical_analysis_primary_analysis_v1(text)
    assert bool(matches) == should_match, f"v1 failed for {test_id}"


# ─────────────────────────────
# v2 – primary + statistical test nearby
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Primary endpoint analysed using mixed-effects model.", True, "v2_pos_stat_test_nearby"),
        ("Primary outcome assessed without statistical model.", False, "v2_neg_no_stat_test"),
    ],
)
def test_v2_primary_analysis(text, should_match, test_id):
    matches = find_statistical_analysis_primary_analysis_v2(text, window=4)
    assert bool(matches) == should_match, f"v2 failed for {test_id}"


# ─────────────────────────────
# v3 – inside heading block
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Statistical Analysis:\nPrimary endpoint analysed using Cox model.", True, "v3_pos_heading"),
        ("Primary endpoint analysed using Cox model outside block.", False, "v3_neg_outside_heading"),
    ],
)
def test_v3_primary_analysis(text, should_match, test_id):
    matches = find_statistical_analysis_primary_analysis_v3(text)
    assert bool(matches) == should_match, f"v3 failed for {test_id}"


# ─────────────────────────────
# v4 – statistical test + adjustment phrase nearby
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Primary endpoint analysed with mixed-effects model adjusting for baseline covariates.", True, "v4_pos_adjustment_near"),
        ("Primary endpoint analysed with mixed-effects model without covariates.", False, "v4_neg_no_adjustment_near"),
    ],
)
def test_v4_primary_analysis(text, should_match, test_id):
    matches = find_statistical_analysis_primary_analysis_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for {test_id}"


# ─────────────────────────────
# v5 – tight template
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Primary endpoint analysed with mixed-effects linear model adjusting for baseline covariates.", True, "v5_pos_tight"),
        ("Primary outcome assessed descriptively.", False, "v5_neg_not_template"),
    ],
)
def test_v5_primary_analysis(text, should_match, test_id):
    matches = find_statistical_analysis_primary_analysis_v5(text)
    assert bool(matches) == should_match, f"v5 failed for {test_id}"
