# tests/test_dose_response_analysis_finder.py

import pytest
from pyregularexpression.dose_response_analysis_finder import (
    find_dose_response_analysis_v1,
    find_dose_response_analysis_v2,
    find_dose_response_analysis_v3,
    find_dose_response_analysis_v4,
    find_dose_response_analysis_v5,
)

# -----------------------------
# Test cases for v1 (high recall)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("A dose-response relationship was observed.", True, "v1_pos_basic_cue"),
    ("Exposure-response trends were significant.", True, "v1_pos_exposure_cue"),
    ("Patients received different treatments.", False, "v1_neg_no_cue"),
])
def test_find_dose_response_analysis_v1(text, expected, case_id):
    res = find_dose_response_analysis_v1(text)
    assert (len(res) > 0) == expected, f"v1 failed for ID: {case_id}"


# -----------------------------
# Test cases for v2 (cue + analytic verb)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("A dose-response was tested in the cohort.", True, "v2_pos_tested"),
    ("Exposure-response was evaluated for outcomes.", True, "v2_pos_evaluated"),
    ("A dose-response trend without analysis was noted.", False, "v2_neg_no_verb"),
])
def test_find_dose_response_analysis_v2(text, expected, case_id):
    res = find_dose_response_analysis_v2(text, window=4)
    assert (len(res) > 0) == expected, f"v2 failed for ID: {case_id}"


# -----------------------------
# Test cases for v3 (inside dose-response heading block)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Dose-Response:\nWe observed a clear trend.", True, "v3_pos_heading_block"),
    ("Methods: Dose-response was analyzed.", False, "v3_neg_no_heading"),
])
def test_find_dose_response_analysis_v3(text, expected, case_id):
    res = find_dose_response_analysis_v3(text, block_chars=400)
    assert (len(res) > 0) == expected, f"v3 failed for ID: {case_id}"


# -----------------------------
# Test cases for v4 (v2 + trend keyword)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("A dose-response was tested (p-trend < 0.01).", True, "v4_pos_ptrend"),
    ("Exposure-response was evaluated using restricted cubic spline.", True, "v4_pos_spline"),
    ("A dose-response was observed but no trend test performed.", False, "v4_neg_no_trend_keyword"),
])
def test_find_dose_response_analysis_v4(text, expected, case_id):
    res = find_dose_response_analysis_v4(text, window=6)
    assert (len(res) > 0) == expected, f"v4 failed for ID: {case_id}"


# -----------------------------
# Test cases for v5 (tight template)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("A clear dose-response was observed (p-trend < 0.001).", True, "v5_pos_template"),
    ("Dose-response relationship noted but no p-trend.", False, "v5_neg_loose_phrase"),
])
def test_find_dose_response_analysis_v5(text, expected, case_id):
    res = find_dose_response_analysis_v5(text)
    assert (len(res) > 0) == expected, f"v5 failed for ID: {case_id}"
