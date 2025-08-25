# tests/test_generalizability_finder.py

import pytest
from pyregularexpression.generalizability_finder import (
    find_generalizability_v1,
    find_generalizability_v2,
    find_generalizability_v3,
    find_generalizability_v4,
    find_generalizability_v5,
)

# -----------------------------
# Test cases for v1 (high recall)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("The results are generalizable to other populations.", True, "v1_pos_generalizable"),
    ("External validity is limited in this study.", True, "v1_pos_external_validity"),
    ("This was a small randomized trial.", False, "v1_neg_no_cue"),
])
def test_find_generalizability_v1(text, expected, case_id):
    res = find_generalizability_v1(text)
    assert (len(res) > 0) == expected, f"v1 failed for ID: {case_id}"


# -----------------------------
# Test cases for v2 (cue + modal/uncertainty)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Findings may generalize to women.", True, "v2_pos_modal_near_cue"),
    ("Results should be interpreted with caution regarding applicability.", True, "v2_pos_modal_caution"),
    ("The study was conducted in adults only.", False, "v2_neg_no_modal"),
])
def test_find_generalizability_v2(text, expected, case_id):
    res = find_generalizability_v2(text, window=4)
    assert (len(res) > 0) == expected, f"v2 failed for ID: {case_id}"


# -----------------------------
# Test cases for v3 (inside heading block)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Generalizability:\nThese results are generalizable to other populations.", True, "v3_pos_heading_block"),
    ("Applicability:\nExternal validity may be limited.", True, "v3_pos_applicability_block"),
    ("Methods: The study included adults aged 18-65.", False, "v3_neg_no_heading"),
])
def test_find_generalizability_v3(text, expected, case_id):
    res = find_generalizability_v3(text, block_chars=400)
    assert (len(res) > 0) == expected, f"v3 failed for ID: {case_id}"


# -----------------------------
# Test cases for v4 (v2 + population/setting qualifier)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Findings may not generalize to older adults or women.", True, "v4_pos_pop_qual"),
    ("The study may generalize.", False, "v4_neg_no_pop_qual"),
])
def test_find_generalizability_v4(text, expected, case_id):
    res = find_generalizability_v4(text, window=8)
    assert (len(res) > 0) == expected, f"v4 failed for ID: {case_id}"


# -----------------------------
# Test cases for v5 (tight template)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Findings may not generalize to older adults or women.", True, "v5_pos_template"),
    ("The results are generalizable to other populations.", False, "v5_neg_loose_phrase"),
])
def test_find_generalizability_v5(text, expected, case_id):
    res = find_generalizability_v5(text)
    assert (len(res) > 0) == expected, f"v5 failed for ID: {case_id}"
