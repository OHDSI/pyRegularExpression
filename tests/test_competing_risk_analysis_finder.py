# tests/test_competing_risk_analysis_finder.py
"""
Complete test suite for competing_risk_analysis_finder.py.

Includes:
- Robust tests for v1 and v2 (basic cues and context-aware detection)
- Functional checks for v3, v4, and v5 (heading blocks, numeric/technique context, and tight templates)
- All examples are based on biomedical competing-risk usage (Fine-Gray, sub-hazard ratio, cumulative incidence).
"""

import pytest
from pyregularexpression.competing_risk_analysis_finder import (
    find_competing_risk_analysis_v1,
    find_competing_risk_analysis_v2,
    find_competing_risk_analysis_v3,
    find_competing_risk_analysis_v4,
    find_competing_risk_analysis_v5,
)

# ─────────────────────────────
# Robust Tests for v1 – High Recall: any competing-risk cue
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Competing risk analysis was performed for death vs transplant.", True, "v1_pos_competing_risk"),
        ("Fine-Gray models were applied to assess event probability.", True, "v1_pos_fine_gray"),
        ("The sub-hazard ratio (sHR) was reported.", True, "v1_pos_shr"),

        # Trap / negative examples
        ("There is high competition for resources in the ICU.", False, "v1_trap_resource_competition"),
        ("Risk of fracture was compared using Cox regression.", False, "v1_trap_cox_regression"),
    ]
)
def test_find_competing_risk_analysis_v1(text, should_match, test_id):
    matches = find_competing_risk_analysis_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"


# ─────────────────────────────
# Robust Tests for v2 – Cue + modelling verb nearby
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("We fitted Fine-Gray models to estimate competing risk outcomes.", True, "v2_pos_fitted_finegray"),
        ("Sub-hazard ratio was estimated in a competing risk framework.", True, "v2_pos_estimated_shr"),

        # Trap examples
        ("Fine-Gray method described in discussion without modelling.", False, "v2_trap_no_modeling_verb"),
        ("Competition for resources was used as an example.", False, "v2_trap_resource_usage"),
    ]
)
def test_find_competing_risk_analysis_v2(text, should_match, test_id):
    matches = find_competing_risk_analysis_v2(text)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v3 – Inside competing-risk heading blocks
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Competing Risk:\nWe used Fine-Gray methods for transplant analysis.", True, "v3_pos_heading_competing"),
        ("Fine-Gray:\nThe sub-hazard ratio was estimated.", True, "v3_pos_heading_finegray"),

        # Negative: correct cue outside a heading
        ("Results:\nCompeting risk analysis was mentioned here.", False, "v3_neg_wrong_heading"),
        ("Methods:\nFine-Gray models were described.", False, "v3_neg_not_in_block"),
    ]
)
def test_find_competing_risk_analysis_v3(text, should_match, test_id):
    matches = find_competing_risk_analysis_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v4 – Cue + verb + technique keyword
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("We fitted Fine-Gray models to estimate sHRs for competing risk.", True, "v4_pos_fitted_finegray_shr"),
        ("Competing risk analysis was performed using the cumulative incidence function.", True, "v4_pos_cif"),

        # Negative examples
        ("We applied models to study competing risk without specifying Fine-Gray.", False, "v4_neg_missing_technique"),
        ("Fine-Gray was mentioned, but no modelling verb was present.", False, "v4_neg_missing_verb"),
    ]
)
def test_find_competing_risk_analysis_v4(text, should_match, test_id):
    matches = find_competing_risk_analysis_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v5 – Tight template match
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("We fitted Fine-Gray models to estimate sHRs for death vs transplant.", True, "v5_pos_fitted_finegray_template"),

        # Negative examples
        ("We applied Fine-Gray models but did not report sHRs.", False, "v5_neg_missing_shr"),
        ("Sub-hazard ratios were estimated, but no Fine-Gray fitting was described.", False, "v5_neg_missing_fitted_template"),
    ]
)
def test_find_competing_risk_analysis_v5(text, should_match, test_id):
    matches = find_competing_risk_analysis_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
