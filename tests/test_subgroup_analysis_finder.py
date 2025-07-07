# tests/test_subgroup_analysis_finder.py
"""
Test suite for subgroup_analysis_finder.py.
Covers five variants (v1–v5):
    • v1 – high recall: subgroup cue
    • v2 – cue + analytic verb
    • v3 – inside Subgroup/Effect Modification/Interaction heading block
    • v4 – v2 + explicit interaction/heterogeneity keyword
    • v5 – tight template
"""
import pytest
from pyregularexpression.subgroup_analysis_finder import (
    find_subgroup_analysis_v1,
    find_subgroup_analysis_v2,
    find_subgroup_analysis_v3,
    find_subgroup_analysis_v4,
    find_subgroup_analysis_v5,
)

# ───────────────────────────────
# Tests for v1 (High Recall)
# ───────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("A subgroup analysis was performed by age group.", True, "v1_pos_subgroup_analysis"),
        ("The investigators assessed effect modification by sex.", True, "v1_pos_effect_modification"),
        ("Interaction term was included in the regression model.", True, "v1_pos_interaction_term"),
        ("We describe baseline subgroups of patients by age.", False, "v1_neg_trap_baseline"),
    ],
)
def test_find_subgroup_analysis_v1(text, should_match, test_id):
    matches = find_subgroup_analysis_v1(text)
    assert bool(matches) == should_match, f"v1 failed for {test_id}"


# ───────────────────────────────
# Tests for v2 (Cue + Analytic Verb)
# ───────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Subgroup analysis tested in strata of BMI.", True, "v2_pos_tested_in_strata"),
        ("Effect modification was assessed by gender.", True, "v2_pos_effect_modification_assessed"),
        ("Subgroup analysis reported without details.", False, "v2_neg_no_analytic_verb"),
        ("We performed stratified analysis of outcomes.", True, "v2_pos_stratified_performed"),
    ],
)
def test_find_subgroup_analysis_v2(text, should_match, test_id):
    matches = find_subgroup_analysis_v2(text, window=4)
    assert bool(matches) == should_match, f"v2 failed for {test_id}"


# ───────────────────────────────
# Tests for v3 (Heading Block)
# ───────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Subgroup Analysis:\nSubgroup analysis was performed by sex.", True, "v3_pos_heading_block"),
        ("Effect Modification:\nInteraction term was tested.", True, "v3_pos_effect_mod_heading"),
        ("Methods:\nSubgroup analysis was performed.", False, "v3_neg_wrong_heading"),
    ],
)
def test_find_subgroup_analysis_v3(text, should_match, test_id):
    matches = find_subgroup_analysis_v3(text)
    assert bool(matches) == should_match, f"v3 failed for {test_id}"


# ───────────────────────────────
# Tests for v4 (Cue + Verb + Interaction/Heterogeneity Keyword)
# ───────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Subgroup analysis was tested with P-interaction = 0.04.", True, "v4_pos_p_interaction"),
        ("Effect modification assessed with heterogeneity tests.", True, "v4_pos_heterogeneity"),
        ("Subgroup analysis performed without interaction term.", False, "v4_neg_no_key_term"),
    ],
)
def test_find_subgroup_analysis_v4(text, should_match, test_id):
    matches = find_subgroup_analysis_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for {test_id}"


# ───────────────────────────────
# Tests for v5 (Tight Template)
# ───────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Subgroup analyses showed stronger effect in women <50 y (P-interaction = 0.02).", True, "v5_pos_tight_template"),
        ("The study reported subgroup analyses with no P-value.", False, "v5_neg_missing_interaction"),
        ("Exploratory subgroup analysis assessed differences.", False, "v5_neg_not_template"),
    ],
)
def test_find_subgroup_analysis_v5(text, should_match, test_id):
    matches = find_subgroup_analysis_v5(text)
    assert bool(matches) == should_match, f"v5 failed for {test_id}"
