# tests/test_covariate_adjustment_finder.py
"""
Complete test suite for covariate_adjustment_finder.py.

Includes:
- Robust tests for v1 and v2 (basic adjustment cues and cue+linking token detection)
- Functional checks for v3, v4, and v5 (block-based, covariate-aware, and template-based)
- All examples drawn from PubMed / OHDSI-style reporting of covariate adjustment
"""

import pytest
from pyregularexpression.covariate_adjustment_finder import (
    find_covariate_adjustment_v1,
    find_covariate_adjustment_v2,
    find_covariate_adjustment_v3,
    find_covariate_adjustment_v4,
    find_covariate_adjustment_v5,
)

# ─────────────────────────────
# Robust Tests for v1 – High Recall: any adjustment or multivariable model cue
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive PubMed/OHDSI-style examples
        ("Hazard ratios were adjusted for age and sex.", True, "v1_pos_adjusted"),
        ("A multivariable logistic regression model was fitted including baseline covariates.", True, "v1_pos_multivariable"),
        ("The model controlled for comorbidities and smoking status.", True, "v1_pos_controlled"),

        # Traps and negatives
        ("Drug dose was adjusted based on renal function.", False, "v1_trap_dose_adjustment"),
        ("Treatment regimens were adjusted according to response.", False, "v1_trap_treatment_adjustment"),
        ("Baseline covariates were listed but no adjustment applied.", False, "v1_neg_baseline_listing"),
    ]
)
def test_find_covariate_adjustment_v1(text, should_match, test_id):
    matches = find_covariate_adjustment_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"


# ─────────────────────────────
# Robust Tests for v2 – Adjustment cue + linking token (e.g., “for”, “with”)
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive
        ("Outcomes were adjusted for age, BMI, and smoking.", True, "v2_pos_for_covariates"),
        ("We controlled with baseline variables including diabetes and hypertension.", True, "v2_pos_with_covariates"),

        # Negative / traps
        ("Dose was adjusted for patient weight.", False, "v2_trap_dose_for_weight"),
        ("Adjusted values are reported in Supplementary Table 1.", False, "v2_neg_generic_adjusted"),
    ]
)
def test_find_covariate_adjustment_v2(text, should_match, test_id):
    matches = find_covariate_adjustment_v2(text)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v3 – Within “Statistical analysis” or “Covariate adjustment” blocks
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Statistical analysis:\nModels were adjusted for age and sex.\n\n", True, "v3_pos_statistical_analysis"),
        ("Covariate adjustment:\nThe analysis controlled for smoking and BMI.\n\n", True, "v3_pos_covariate_adjustment"),

        # Negative: adjustment cue but outside heading block
        ("Results:\nHazard ratios were adjusted for age and sex.", False, "v3_neg_wrong_section"),
        ("Baseline characteristics:\nPatients’ age and BMI were recorded.", False, "v3_neg_baseline_only"),
    ]
)
def test_find_covariate_adjustment_v3(text, should_match, test_id):
    matches = find_covariate_adjustment_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v4 – Cue + linking token + explicit covariate keyword
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive
        ("Models were adjusted for age, sex, and smoking.", True, "v4_pos_with_covariates"),
        ("The hazard ratios were controlled for baseline BMI.", True, "v4_pos_with_bmi"),

        # Negative
        ("Adjusted for treatment regimen only.", False, "v4_neg_no_covariate_keyword"),
        ("Values were adjusted with respect to dose response.", False, "v4_trap_dose_response"),
    ]
)
def test_find_covariate_adjustment_v4(text, should_match, test_id):
    matches = find_covariate_adjustment_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v5 – Tight templates (e.g., “HRs adjusted for age, sex”)
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive
        ("Hazard ratios adjusted for age, BMI, and smoking.", True, "v5_pos_hr_adjusted"),
        ("Multivariable model adjusted including age and sex.", True, "v5_pos_multivariable_template"),

        # Negative
        ("The patient lost weight adjusted for baseline measures.", False, "v5_neg_irrelevant_use"),
        ("Unadjusted models were reported in Table 2.", False, "v5_neg_unadjusted"),
    ]
)
def test_find_covariate_adjustment_v5(text, should_match, test_id):
    matches = find_covariate_adjustment_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
