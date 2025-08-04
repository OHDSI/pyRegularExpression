# tests/test_eligibility_criteria_finder.py
"""
Test suite for eligibility_criteria_finder.py.

Covers v1–v5:
- Robust for v1 and v2.
- Light representative checks for v3–v5.
"""

import pytest
from pyregularexpression.eligibility_criteria_finder import (
    find_eligibility_criteria_v1,
    find_eligibility_criteria_v2,
    find_eligibility_criteria_v3,
    find_eligibility_criteria_v4,
    find_eligibility_criteria_v5,
)

# ─────────────────────────────
# Robust Tests for v1 (High Recall)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # … your existing cases …

        # More positive v1 examples
        ("Eligible individuals were screened at baseline.",        True, "v1_pos_individuals_were"),
        ("Enrollment criteria included patients with asthma.",   True, "v1_pos_enrollment_criteria_included"),
        ("Participants were not eligible if they refused consent.", True, "v1_pos_not_eligible_if"),
        ("Exclusion criteria included those with renal disease.", True, "v1_pos_exclusion_criteria_included"),
        ("Eligibility criteria were recently updated.",           True, "v1_pos_eligibility_criteria_phrase"),

        # More negative traps
        ("Classification criteria were reviewed.",                False, "v1_neg_classification_trap"),
        ("Performance criteria for assays were strict.",         False, "v1_neg_performance_trap"),
    ]
)
def test_find_eligibility_criteria_v1(text, should_match, test_id):
    matches = find_eligibility_criteria_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ─────────────────────────────
# Robust Tests for v2 (Cue + Qualifier within ±4 tokens)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Eligible patients were aged 45–70 years.", True, "v2_pos_eligible_age"),
        ("We excluded patients with history of stroke.", True, "v2_pos_excluded_history_of"),
        ("Inclusion criteria included diagnosed COPD.", True, "v2_pos_incl_diagnosed"),
        ("Patients were not eligible if they had diabetes.", True, "v2_pos_were_not_eligible_diabetes"),

        ("Eligible datasets were included in analysis.", False, "v2_neg_dataset_trap"),
        ("The trial excluded locations with limited access.", False, "v2_neg_excluded_nonpatient"),
        ("Eligible if participant consented verbally.", False, "v2_neg_no_qualifier"),
    ]
)
def test_find_eligibility_criteria_v2(text, should_match, test_id):
    matches = find_eligibility_criteria_v2(text, window=4)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ─────────────────────────────
# Light Tests for v3 (Must be in eligibility block)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Eligibility Criteria:\nEligible patients were aged 18–65.", True, "v3_pos_in_block"),
        ("Inclusion and Exclusion Criteria:\nWe excluded smokers.", True, "v3_pos_combo_heading"),

        ("Eligible patients were aged 18–65.\n\nEligibility Criteria:\n(no content)", False, "v3_neg_cue_before_heading"),
        ("Patient selection:\nEligible subjects were assessed.", False, "v3_neg_heading_not_matched"),
    ]
)
def test_find_eligibility_criteria_v3(text, should_match, test_id):
    matches = find_eligibility_criteria_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ─────────────────────────────
# Light Tests for v4 (Inclusion cue near Exclusion cue)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Eligible patients were included if they had diabetes and we excluded those with prior insulin use.", True, "v4_pos_incl_near_excl"),
        ("Patients were eligible; those with heart disease were excluded.", True, "v4_pos_semicolon_separation"),

        ("Eligible patients had COPD.", False, "v4_neg_no_exclusion"),
        ("We excluded those with cancer but did not specify inclusion criteria.", False, "v4_neg_exclusion_only"),
    ]
)
def test_find_eligibility_criteria_v4(text, should_match, test_id):
    matches = find_eligibility_criteria_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ─────────────────────────────
# Light Tests for v5 (Tight Template Matching)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Adults 18–65 with diabetes were eligible; prior insulin use was an exclusion criterion.", True, "v5_pos_full_template"),
        ("Children 6–12 were eligible; those with seizures were excluded.", True, "v5_pos_children_range"),

        ("Eligible patients were included if they had diabetes.", False, "v5_neg_soft_template"),
        ("Adults aged 45–75 were recruited; exclusion criteria not stated.", False, "v5_neg_missing_exclusion_cue"),
    ]
)
def test_find_eligibility_criteria_v5(text, should_match, test_id):
    matches = find_eligibility_criteria_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
