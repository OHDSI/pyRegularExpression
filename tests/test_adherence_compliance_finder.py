# tests/test_adherence_compliance_finder.py
"""
Complete test suite for adherence_compliance_finder.py.

Includes:
- Robust tests for v1 and v2 (basic cues and context-aware analytic verbs)
- Functional checks for v3, v4, and v5 (block-based, numeric/threshold-based, and template-based)
- All examples based on PubMed/OHDSI-style descriptions of adherence/compliance
"""

import pytest
from pyregularexpression.adherence_compliance_finder import (
    find_adherence_compliance_v1,
    find_adherence_compliance_v2,
    find_adherence_compliance_v3,
    find_adherence_compliance_v4,
    find_adherence_compliance_v5,
)

# ─────────────────────────────
# Robust Tests for v1 – High Recall: any adherence/compliance cue
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Medication adherence was reported for all patients.", True, "v1_pos_medication_adherence"),
        ("Compliance with therapy was assessed annually.", True, "v1_pos_compliance_with_therapy"),
        ("We calculated the proportion of days covered (PDC).", True, "v1_pos_pdc"),
        ("The medication possession ratio (MPR) was used.", True, "v1_pos_mpr"),
        ("Adherence was measured by pill count.", True, "v1_pos_pill_count"),

        # Trap examples
        ("Adherence to guidelines was encouraged.", False, "v1_trap_guidelines"),
        ("Baseline adherence was described.", False, "v1_trap_baseline"),
        ("Good adherence to study procedures was expected.", False, "v1_trap_study_procedures"),
    ]
)
def test_find_adherence_compliance_v1(text, should_match, test_id):
    matches = find_adherence_compliance_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ─────────────────────────────
# Robust Tests for v2 – Cue + analytic verb within ±4 tokens
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Adherence was defined as the proportion of days covered.", True, "v2_pos_adherence_defined"),
        ("We calculated compliance using pill counts.", True, "v2_pos_compliance_calculated"),
        ("MPR was measured across all patients.", True, "v2_pos_mpr_measured"),

        # Negative examples
        ("Adherence was high among participants.", False, "v2_neg_adherence_no_verb"),
        ("Compliance to treatment was encouraged.", False, "v2_neg_compliance_encouraged"),
        ("Medication adherence rates were noted.", False, "v2_neg_not_analytic"),
    ]
)
def test_find_adherence_compliance_v2(text, should_match, test_id):
    matches = find_adherence_compliance_v2(text)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ─────────────────────────────
# Lighter Tests for v3 – Inside Adherence/Compliance heading blocks
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Adherence:\nPDC was calculated over 12 months.", True, "v3_pos_adherence_heading"),
        ("Compliance:\nWe measured pill counts weekly.", True, "v3_pos_compliance_heading"),

        # Negative: correct cue but outside relevant heading
        ("Results:\nAdherence was calculated using MPR.", False, "v3_neg_wrong_heading"),
        ("Baseline:\nMedication adherence was noted.", False, "v3_neg_not_adherence_heading"),
    ]
)
def test_find_adherence_compliance_v3(text, should_match, test_id):
    matches = find_adherence_compliance_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ─────────────────────────────
# Lighter Tests for v4 – Cue + analytic verb + numeric threshold/metric
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Adherence was defined as PDC ≥ 0.8 over 12 months.", True, "v4_pos_pdc_threshold"),
        ("Compliance was measured and MPR > 75% was recorded.", True, "v4_pos_mpr_threshold"),
        ("Adherence was calculated; pill count ≥ 90% was used.", True, "v4_pos_pillcount_threshold"),

        # Negative examples
        ("Adherence was defined but no numeric threshold given.", False, "v4_neg_no_threshold"),
        ("Compliance was measured qualitatively.", False, "v4_neg_no_numeric"),
        ("MPR mentioned but not calculated.", False, "v4_neg_no_verb_with_threshold"),
    ]
)
def test_find_adherence_compliance_v4(text, should_match, test_id):
    matches = find_adherence_compliance_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ─────────────────────────────
# Lighter Tests for v5 – Tight template matches
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Adherence was defined as PDC ≥ 0.8 over 12 months.", True, "v5_pos_tight_template"),
        ("Adherence was defined as MPR > 80% across the cohort.", True, "v5_pos_mpr_threshold"),

        # Negative examples
        ("Adherence was encouraged by providing counseling.", False, "v5_neg_encouraged"),
        ("PDC values were reported but no threshold defined.", False, "v5_neg_no_definition"),
        ("Adherence was defined broadly without metrics.", False, "v5_neg_no_metric"),
    ]
)
def test_find_adherence_compliance_v5(text, should_match, test_id):
    matches = find_adherence_compliance_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
