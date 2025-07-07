# tests/test_demographic_restriction_finder.py

import pytest
from pyregularexpression.demographic_restriction_finder import (
    find_demographic_restriction_v1,
    find_demographic_restriction_v2,
    find_demographic_restriction_v3,
    find_demographic_restriction_v4,
    find_demographic_restriction_v5,
)

# -----------------------------
# Test cases for v1 (high recall)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Participants aged 18–65 were eligible.", True, "v1_pos_age_range"),
    ("Children under 12 were excluded.", True, "v1_pos_children"),
    ("The mean age of participants was 45.", True, "v1_pos_mean_age_detected"),
    ("The study was conducted in hospitals.", False, "v1_neg_no_demo"),
])
def test_find_demographic_restriction_v1(text, expected, case_id):
    res = find_demographic_restriction_v1(text)
    assert (len(res) > 0) == expected, f"v1 failed for ID: {case_id}"


# -----------------------------
# Test cases for v2 (cue + gating verb)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Participants aged 18–65 were included in the trial.", True, "v2_pos_age_included"),
    ("Children under 12 must be enrolled.", True, "v2_pos_children_enrolled"),
    ("Adults over 40 were analyzed.", False, "v2_neg_no_gating_verb"),
])
def test_find_demographic_restriction_v2(text, expected, case_id):
    res = find_demographic_restriction_v2(text, window=5)
    assert (len(res) > 0) == expected, f"v2 failed for ID: {case_id}"


# -----------------------------
# Test cases for v3 (inside eligibility/inclusion blocks)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Eligibility:\nParticipants aged 18–65 were recruited.", True, "v3_pos_block_age"),
    ("Methods: Adults aged 40–60 were analyzed.", False, "v3_neg_no_block"),
])
def test_find_demographic_restriction_v3(text, expected, case_id):
    res = find_demographic_restriction_v3(text, block_chars=400)
    assert (len(res) > 0) == expected, f"v3 failed for ID: {case_id}"


# -----------------------------
# Test cases for v4 (v2 + exclude descriptive stats)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Participants aged 18–65 were included.", True, "v4_pos_age_included"),
    ("Children under 12 must be enrolled.", True, "v4_pos_children_enrolled"),
    ("The mean age of participants was 45.", False, "v4_neg_mean_age"),
])
def test_find_demographic_restriction_v4(text, expected, case_id):
    res = find_demographic_restriction_v4(text, window=5)
    assert (len(res) > 0) == expected, f"v4 failed for ID: {case_id}"


# -----------------------------
# Test cases for v5 (tight template)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Participants had to be aged 18–65 to enroll.", True, "v5_pos_template_age"),
    ("Patients must be adults between 18 and 65.", True, "v5_pos_template_adults"),
    ("All participants' mean age was 45.", False, "v5_neg_loose_phrase"),
])
def test_find_demographic_restriction_v5(text, expected, case_id):
    res = find_demographic_restriction_v5(text)
    assert (len(res) > 0) == expected, f"v5 failed for ID: {case_id}"
