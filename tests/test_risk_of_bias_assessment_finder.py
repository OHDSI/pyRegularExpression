# tests/test_risk_of_bias_assessment_finder.py
"""
Complete test suite for risk_of_bias_assessment_finder.py.
Covers five variants (v1–v5):
    • v1 – high recall (bias-assessment cue or tool mention)
    • v2 – cue + assessment verb within window
    • v3 – inside Risk of Bias / Quality Assessment heading block
    • v4 – v2 + explicit rating or tool in same sentence
    • v5 – tight template
"""
import pytest
from pyregularexpression.risk_of_bias_assessment_finder import (
    find_risk_of_bias_assessment_v1,
    find_risk_of_bias_assessment_v2,
    find_risk_of_bias_assessment_v3,
    find_risk_of_bias_assessment_v4,
    find_risk_of_bias_assessment_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The risk of bias was evaluated using the Cochrane tool.", True, "v1_pos_cochrane"),
        ("Study quality assessment was performed with the Newcastle–Ottawa Scale.", True, "v1_pos_nos"),
        ("ROBINS-I was applied to non-randomized studies.", True, "v1_pos_robins_i"),
        ("Selection bias may affect the results.", False, "v1_neg_selection_bias_trap"),
    ],
)
def test_find_risk_of_bias_assessment_v1(text, should_match, test_id):
    matches = find_risk_of_bias_assessment_v1(text)
    assert bool(matches) == should_match, f"v1 failed for {test_id}"


# ────────────────────────────────────
# Robust Tests for v2 (Cue + Verb Window)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Risk of bias was assessed independently by two reviewers.", True, "v2_pos_rob_assessed"),
        ("Quality assessment was applied to all included trials.", True, "v2_pos_quality_applied"),
        ("The ROB 2 tool is available online.", False, "v2_neg_tool_without_action"),
        ("Bias was likely due to confounding factors.", False, "v2_neg_bias_without_assessment"),
    ],
)
def test_find_risk_of_bias_assessment_v2(text, should_match, test_id):
    matches = find_risk_of_bias_assessment_v2(text, window=4)
    assert bool(matches) == should_match, f"v2 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Risk of Bias:\nThe Cochrane tool was used for each RCT.", True, "v3_pos_heading_rob"),
        ("Quality Assessment:\nWe applied the Newcastle–Ottawa Scale.", True, "v3_pos_heading_quality"),
        ("Study Quality:\n(No further details provided)", False, "v3_neg_heading_empty"),
        ("Risk of bias mentioned outside of a heading block.", False, "v3_neg_outside_block"),
    ],
)
def test_find_risk_of_bias_assessment_v3(text, should_match, test_id):
    matches = find_risk_of_bias_assessment_v3(text)
    assert bool(matches) == should_match, f"v3 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v4 (Verb + Tool/Rating)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Risk of bias was assessed and rated as low or high using ROB 2.", True, "v4_pos_rating_tool"),
        ("Quality assessment was performed with the Newcastle–Ottawa Scale.", True, "v4_pos_quality_nos"),
        ("Risk of bias was assessed but no rating was given.", False, "v4_neg_no_rating_tool"),
    ],
)
def test_find_risk_of_bias_assessment_v4(text, should_match, test_id):
    matches = find_risk_of_bias_assessment_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Risk of bias was assessed with the ROBINS-I tool.", True, "v5_pos_robins"),
        ("Risk of bias was assessed using ROB 2.", True, "v5_pos_rob2"),
        ("The risk of bias was considered high but tool not specified.", False, "v5_neg_no_tool"),
        ("ROBINS-I was mentioned without the assessment phrase.", False, "v5_neg_tool_only"),
    ],
)
def test_find_risk_of_bias_assessment_v5(text, should_match, test_id):
    matches = find_risk_of_bias_assessment_v5(text)
    assert bool(matches) == should_match, f"v5 failed for {test_id}"
