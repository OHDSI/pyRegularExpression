# tests/test_washout_period_finder.py
"""
Test suite for washout_period_finder.py

This suite includes high-recall tests (v1), duration+cue (v2), heading-based (v3),
anchor-aware (v4), and strict-template (v5) tests.
"""

import pytest
from pyregularexpression.washout_period_finder import (
    find_washout_period_v1,
    find_washout_period_v2,
    find_washout_period_v3,
    find_washout_period_v4,
    find_washout_period_v5,
)

# ─────────────────────────────────────────────
# Robust Tests for v1 – high recall cues only
# ─────────────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Patients underwent a 4-week washout before randomization.", True, "v1_pos_washout_cue"),
        ("Subjects completed a run-in period prior to baseline.", True, "v1_pos_runin_cue"),
        ("Treatment-free intervals were documented.", True, "v1_pos_treatment_free"),
        ("No therapy was administered during the washout phase.", True, "v1_pos_no_therapy"),
        ("Cells were washed with PBS before incubation.", False, "v1_neg_lab_context"),
        ("Drug therapy was discontinued due to side-effects.", False, "v1_neg_side_effect_trap"),
    ]
)
def test_find_washout_period_v1(text, should_match, test_id):
    matches = find_washout_period_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ─────────────────────────────────────────────
# Robust Tests for v2 – cue + duration within window
# ─────────────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("A 6-week washout period was implemented before baseline.", True, "v2_pos_duration_near_cue"),
        ("Patients were drug-free for 2 months before index.", True, "v2_pos_drugfree_duration"),
        ("Run-in lasted 3 weeks prior to treatment.", True, "v2_pos_runin_duration"),
        ("Participants underwent a washout but no duration was specified.", False, "v2_neg_missing_duration"),
        ("Drug-free intervals were documented long ago.", False, "v2_neg_distance_too_far"),
        ("Antihypertensives were stopped due to adverse events.", False, "v2_neg_side_effect_trap"),
    ]
)
def test_find_washout_period_v2(text, should_match, test_id):
    matches = find_washout_period_v2(text, window=8)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ─────────────────────────────────────────────
# Lighter Checks for v3 – heading-based block
# ─────────────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Washout Period:\nSubjects discontinued medication for 4 weeks before index.\n\n", True, "v3_pos_heading_block"),
        ("Run-in:\nA 6-week drug-free period preceded the intervention.\n\n", True, "v3_pos_runin_block"),
        ("Clearance period:\nNo antihypertensives were used.\n\n", True, "v3_pos_clearance_block"),
        ("Methods:\nPatients underwent a 4-week washout before starting the drug.", False, "v3_neg_wrong_heading"),
        ("Introduction:\nNo therapy was given before treatment.", False, "v3_neg_heading_absent"),
    ]
)
def test_find_washout_period_v3(text, should_match, test_id):
    matches = find_washout_period_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ─────────────────────────────────────────────
# Lighter Checks for v4 – cue + duration + BEFORE anchor
# ─────────────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("A 3-month drug-free period was required before baseline.", True, "v4_pos_duration_and_before"),
        ("Patients had a washout phase of 6 weeks prior to randomization.", True, "v4_pos_washout_prior_index"),
        ("Subjects were treatment-free for 2 months preceding study start.", True, "v4_pos_preceding_start"),
        ("Run-in occurred for 2 weeks but no timing anchor given.", False, "v4_neg_missing_anchor"),
        ("Patients stopped due to adverse events before baseline.", False, "v4_neg_trap_side_effect"),
        ("Washout was described but before/after not mentioned.", False, "v4_neg_no_temporal_anchor"),
    ]
)
def test_find_washout_period_v4(text, should_match, test_id):
    matches = find_washout_period_v4(text, window=8)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ─────────────────────────────────────────────
# Lighter Checks for v5 – tight template match
# ─────────────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("A 12-month washout with no antihypertensives was required before index.", True, "v5_pos_pubmed_style_template"),
        ("Patients were drug-free for 6 months before index.", True, "v5_pos_drugfree_months_template"),
        ("Subjects completed a 4-week washout with no therapy.", True, "v5_pos_template_with_no_therapy"),
        ("A washout was done.", False, "v5_neg_no_duration"),
        ("Washout for 2 months, no comment on timing.", False, "v5_neg_missing_before_index"),
        ("Patients stopped due to intolerance.", False, "v5_neg_adverse_event_template"),
    ]
)
def test_find_washout_period_v5(text, should_match, test_id):
    matches = find_washout_period_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
