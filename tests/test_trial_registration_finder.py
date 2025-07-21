# tests/test_trail_registration_finder.py
"""
Smoke tests for trial_registration_finder.

Summarizes versions v1–v5 of trial registration detection,moving from
high-recall heuristicsto increasingly precise and structured matching,
culminating in strict template-based identification.
"""

import pytest
from pyregularexpression.trial_registration_finder import (
    find_trial_registration_v1,
    find_trial_registration_v2,
    find_trial_registration_v3,
    find_trial_registration_v4,
    find_trial_registration_v5,
)

# ─────────────────────────────
# Tests for v1 – high recall + trap filter
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("This trial was prospectively registered at ClinicalTrials.gov (NCT04567890).", True, "v1_pos_nct_id"),
        ("Trial registration: ISRCTN12345678.", True, "v1_pos_isrctn"),
        ("Registered at EudraCT 2019-000123-45 prior to enrollment.", True, "v1_pos_eudract"),
        ("The study was registered in the ChiCTR system.", True, "v1_pos_chictr"),

        # Trap tests: Mention registry but it's a false positive context
        ("The IRB registration was filed on time.", False, "v1_trap_irb_registration"),
        ("Ethical approval was recorded in the registry of deeds.", False, "v1_trap_registry_of_deeds"),
    ]
)
def test_find_trial_registration_v1(text, should_match, test_id):
    matches = find_trial_registration_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ─────────────────────────────
# Tests for v2 – cue + nearby verb
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Trial registration was recorded as NCT04567890.", True, "v2_pos_recorded_nct"),
        ("The study was registered at ClinicalTrials.gov.", True, "v2_pos_registered_ctgov"),
        ("Trial was prospectively registered at ISRCTN12345678.", True, "v2_pos_registered_isrctn"),

        # Negative: Cue without registration verb nearby
        ("Trial registration: NCT04567890", False, "v2_neg_id_only"),
        ("Study listed on ClinicalTrials.gov for information.", False, "v2_neg_listed_without_registration"),
    ]
)
def test_find_trial_registration_v2(text, should_match, test_id):
    matches = find_trial_registration_v2(text)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ─────────────────────────────
# Tests for v3 – within Trial Registration heading
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Trial Registration:\nThis trial was registered at ClinicalTrials.gov (NCT04567890).", True, "v3_pos_heading_block"),
        ("Registration:\nISRCTN12345678", True, "v3_pos_simple_heading"),

        # Negative: Cue appears outside of block
        ("This trial was registered at ClinicalTrials.gov.\n\nRegistration:\n(no details)", False, "v3_neg_cue_before_heading"),
    ]
)
def test_find_trial_registration_v3(text, should_match, test_id):
    matches = find_trial_registration_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ─────────────────────────────
# Tests for v4 – v2 + valid registry ID
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The study was registered at ClinicalTrials.gov under NCT01234567.", True, "v4_pos_v2_plus_id"),
        ("Trial registration was recorded as EudraCT 2020-001234-22.", True, "v4_pos_eudract_id"),

        # Negative: Registration verb and cue, but missing valid ID
        ("Trial was registered in our internal database.", False, "v4_neg_no_valid_id"),
        ("This study was prospectively registered but no ID was provided.", False, "v4_neg_prospective_no_id"),
    ]
)
def test_find_trial_registration_v4(text, should_match, test_id):
    matches = find_trial_registration_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ─────────────────────────────
# Tests for v5 – tight template only
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("This trial was prospectively registered at ClinicalTrials.gov (NCT01234567).", True, "v5_pos_tight_ctgov"),
        ("Trial was prospectively registered (ISRCTN12345678).", True, "v5_pos_tight_isrctn"),

        # Negative: Template not exact
        ("This trial is registered at ClinicalTrials.gov.", False, "v5_neg_wrong_verb_tense"),
        ("Registered at ClinicalTrials.gov under NCT01234567.", False, "v5_neg_not_template_structure"),
    ]
)
def test_find_trial_registration_v5(text, should_match, test_id):
    matches = find_trial_registration_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"

#
