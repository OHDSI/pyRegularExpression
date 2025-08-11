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
    "text, expected_matches, test_id",
    [
        ("This trial was prospectively registered at ClinicalTrials.gov (NCT04567890).", ["trial was prospectively registered", "prospectively registered", "registered at", "ClinicalTrials.gov", "NCT04567890"], "v1_pos_nct_id"),
        ("Trial registration: ISRCTN12345678.", ["Trial registration", "ISRCTN12345678"], "v1_pos_isrctn"),
        ("Registered at EudraCT 2019-000123-45 prior to enrollment.", ["Registered at", "EudraCT 2019-000123-45"], "v1_pos_eudract"),
        ("The study was registered in the ChiCTR system.", ["study was registered", "registered in", "ChiCTR"], "v1_pos_chictr"),
        ("The study was registered with the JPRN-UMIN000000001.", ["study was registered", "registered with", "JPRN-UMIN000000001"], "v1_pos_jprn"),
        ("The trial is registered at ANZCTR under ACTRN12600000000000.", ["trial is registered", "registered at", "ANZCTR", "ACTRN12600000000000"], "v1_pos_anzctr"),

        # Trap tests: Mention registry but it's a false positive context
        ("The IRB registration was filed on time.", [], "v1_trap_irb_registration"),
        ("Ethical approval was recorded in the registry of deeds.", [], "v1_trap_registry_of_deeds"),
    ]
)
def test_find_trial_registration_v1(text, expected_matches, test_id):
    matches = find_trial_registration_v1(text)
    matched_snippets = [snippet for _, _, snippet in matches]
    assert sorted(matched_snippets) == sorted(expected_matches), f"v1 failed for ID: {test_id}"

# ─────────────────────────────
# Tests for v2 – cue + nearby verb
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, window, expected_matches, test_id",
    [
        ("Trial registration was recorded as NCT04567890.", 6, ["Trial registration", "recorded as", "NCT04567890"], "v2_pos_recorded_nct"),
        ("The study was registered at ClinicalTrials.gov.", 6, ["study was registered", "registered at", "ClinicalTrials.gov"], "v2_pos_registered_ctgov"),
        ("Trial was prospectively registered at ISRCTN12345678.", 6, ["Trial was prospectively registered", "prospectively registered", "registered at", "ISRCTN12345678"], "v2_pos_registered_isrctn"),

        # Negative: Cue without registration verb nearby
        ("Trial registration: NCT04567890", 6, [], "v2_neg_id_only"),
        ("Study listed on ClinicalTrials.gov for information.", 6, [], "v2_neg_listed_without_registration"),
        ("The trial registration is important. Many words separate this from the verb, which was recorded.", 4, [], "v2_neg_cue_and_verb_far_apart"),
    ]
)
def test_find_trial_registration_v2(text, window, expected_matches, test_id):
    matches = find_trial_registration_v2(text, window=window)
    matched_snippets = [snippet for _, _, snippet in matches]
    assert sorted(matched_snippets) == sorted(expected_matches), f"v2 failed for ID: {test_id}"

# ─────────────────────────────
# Tests for v3 – within Trial Registration heading
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, expected_matches, test_id",
    [
        ("Trial Registration:\nThis trial was registered at ClinicalTrials.gov (NCT04567890).", ["trial was registered", "registered at", "ClinicalTrials.gov", "NCT04567890"], "v3_pos_heading_block"),
        ("Registration:\nISRCTN12345678", ["ISRCTN12345678"], "v3_pos_simple_heading"),

        # Negative: Cue appears outside of block
        ("This trial was registered at ClinicalTrials.gov.\n\nRegistration:\n(no details)", [], "v3_neg_cue_before_heading"),
    ]
)
def test_find_trial_registration_v3(text, expected_matches, test_id):
    matches = find_trial_registration_v3(text)
    matched_snippets = [snippet for _, _, snippet in matches]
    assert sorted(matched_snippets) == sorted(expected_matches), f"v3 failed for ID: {test_id}"

# ─────────────────────────────
# Tests for v4 – v2 + valid registry ID
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, expected_matches, test_id",
    [
        ("The study was registered at ClinicalTrials.gov under NCT01234567.", ["study was registered", "registered at", "ClinicalTrials.gov", "NCT01234567"], "v4_pos_v2_plus_id"),
        ("Trial registration was recorded as EudraCT 2020-001234-22.", ["Trial registration", "recorded as", "EudraCT 2020-001234-22"], "v4_pos_eudract_id"),

        # Negative: Registration verb and cue, but missing valid ID
        ("Trial was registered in our internal database.", [], "v4_neg_no_valid_id"),
        ("This study was prospectively registered but no ID was provided.", [], "v4_neg_prospective_no_id"),
    ]
)
def test_find_trial_registration_v4(text, expected_matches, test_id):
    matches = find_trial_registration_v4(text)
    matched_snippets = [snippet for _, _, snippet in matches]
    assert sorted(matched_snippets) == sorted(expected_matches), f"v4 failed for ID: {test_id}"

# ─────────────────────────────
# Tests for v5 – tight template only
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, expected_matches, test_id",
    [
        ("This trial was prospectively registered at ClinicalTrials.gov (NCT01234567).", ["This trial was prospectively registered at ClinicalTrials.gov (NCT01234567)"], "v5_pos_tight_ctgov"),
        ("Trial was prospectively registered (ISRCTN12345678).", ["Trial was prospectively registered (ISRCTN12345678)"], "v5_pos_tight_isrctn"),

        # Negative: Template not exact
        ("This trial is registered at ClinicalTrials.gov.", [], "v5_neg_wrong_verb_tense"),
        ("Registered at ClinicalTrials.gov under NCT01234567.", [], "v5_neg_not_template_structure"),
    ]
)
def test_find_trial_registration_v5(text, expected_matches, test_id):
    matches = find_trial_registration_v5(text)
    matched_snippets = [snippet for _, _, snippet in matches]
    matched_snippets = [s.strip('.') for s in matched_snippets]
    assert sorted(matched_snippets) == sorted(expected_matches), f"v5 failed for ID: {test_id}"

#
