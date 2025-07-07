# tests/test_sensitivity_analysis_finder.py
"""
Complete test suite for sensitivity_analysis_finder.py.
Covers five variants (v1–v5):
    • v1 – high recall (any “sensitivity analysis/analyses”)
    • v2 – phrase + analysis verb within window
    • v3 – inside Sensitivity analysis heading block
    • v4 – v2 + scenario/assumption token nearby
    • v5 – tight template
"""
import pytest
from pyregularexpression.sensitivity_analysis_finder import (
    find_sensitivity_analysis_v1,
    find_sensitivity_analysis_v2,
    find_sensitivity_analysis_v3,
    find_sensitivity_analysis_v4,
    find_sensitivity_analysis_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("A sensitivity analysis was conducted to assess robustness.", True, "v1_pos_simple"),
        ("Sensitivity analyses explored different cut-offs for inclusion.", True, "v1_pos_plural"),
        ("The assay sensitivity was measured.", False, "v1_neg_trap_assay"),
        ("We measured sensitivity 95% confidence interval.", False, "v1_neg_numeric_sensitivity"),
    ],
)
def test_find_sensitivity_analysis_v1(text, should_match, test_id):
    matches = find_sensitivity_analysis_v1(text)
    assert bool(matches) == should_match, f"v1 failed for {test_id}"


# ────────────────────────────────────
# Robust Tests for v2 (Phrase + Verb Window)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Sensitivity analysis was performed for missing data.", True, "v2_pos_performed"),
        ("We repeated sensitivity analyses using alternative assumptions.", True, "v2_pos_repeated"),
        ("Sensitivity analysis should be considered.", False, "v2_neg_no_verb"),
        ("Sensitivity analyses in the study were discussed.", False, "v2_neg_discussed_only"),
    ],
)
def test_find_sensitivity_analysis_v2(text, should_match, test_id):
    matches = find_sensitivity_analysis_v2(text, window=4)
    assert bool(matches) == should_match, f"v2 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Sensitivity analysis:\nExcluding switchers did not change outcomes.", True, "v3_pos_heading_block"),
        ("Sensitivity analyses:\nAlternative cut-offs were explored.", True, "v3_pos_heading_plural"),
        ("Sensitivity analysis mentioned outside heading.", False, "v3_neg_outside_block"),
        ("No sensitivity analysis section in this study.", False, "v3_neg_missing_heading"),
    ],
)
def test_find_sensitivity_analysis_v3(text, should_match, test_id):
    matches = find_sensitivity_analysis_v3(text)
    assert bool(matches) == should_match, f"v3 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v4 (Verb + Scenario/Assumption)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Sensitivity analysis was repeated excluding protocol violators.", True, "v4_pos_excluding"),
        ("We conducted sensitivity analyses with alternative cut-offs.", True, "v4_pos_alternative"),
        ("Sensitivity analysis was performed without scenario-specific restrictions.", False, "v4_neg_no_scenario_token"),
        ("Sensitivity analyses were discussed in the text.", False, "v4_neg_generic_mention"),
    ],
)
def test_find_sensitivity_analysis_v4(text, should_match, test_id):
    matches = find_sensitivity_analysis_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Excluding switchers in sensitivity analysis did not affect results.", True, "v5_pos_excluding_switchers"),
        ("Sensitivity analyses repeated with alternative cut-offs confirmed robustness.", True, "v5_pos_repeated_alternative"),
        ("Sensitivity analysis was performed for all outcomes.", False, "v5_neg_generic"),
        ("Switchers were analyzed but not in a sensitivity analysis context.", False, "v5_neg_trap_context"),
    ],
)
def test_find_sensitivity_analysis_v5(text, should_match, test_id):
    matches = find_sensitivity_analysis_v5(text)
    assert bool(matches) == should_match, f"v5 failed for {test_id}"
