# tests/test_missing_data_handling_finder.py

import pytest
from pyregularexpression.missing_data_handling_finder import (
    find_missing_data_handling_v1,
    find_missing_data_handling_v2,
    find_missing_data_handling_v3,
    find_missing_data_handling_v4,
    find_missing_data_handling_v5,
)

# -----------------------------
# v1 – high recall: any missing-data cue
# -----------------------------
@pytest.mark.parametrize("text, expected_count, case_id", [
    ("Missing data were imputed using LOCF", 3, "v1_multiple_cues"),
    ("No missing values reported", 0, "v1_trap_excluded"),
])
def test_find_missing_data_handling_v1(text, expected_count, case_id):
    res = find_missing_data_handling_v1(text)
    assert len(res) == expected_count, f"v1 failed: {case_id}"


# -----------------------------
# v2 – cue ± window around analysis verb
# -----------------------------
@pytest.mark.parametrize("text, expected_count, case_id", [
    ("Missing data were imputed", 1, "v2_valid_window"),
    ("Multiple imputation performed", 1, "v2_valid_mi"),
    ("Missing data without verb nearby", 0, "v2_no_verb"),
])
def test_find_missing_data_handling_v2(text, expected_count, case_id):
    res = find_missing_data_handling_v2(text, window=4)
    assert len(res) == expected_count, f"v2 failed: {case_id}"


# -----------------------------
# v3 – only inside heading-anchored block
# -----------------------------
@pytest.mark.parametrize("text, expected_count, case_id", [
    ("Some other text\nImputed LOCF", 0, "v3_outside_heading"),
])
def test_find_missing_data_handling_v3(text, expected_count, case_id):
    res = find_missing_data_handling_v3(text, block_chars=400)
    assert len(res) == expected_count, f"v3 failed: {case_id}"


# -----------------------------
# v4 – v2 + explicit technique keyword
# -----------------------------
@pytest.mark.parametrize("text, expected_count, case_id", [
    ("Missing data handled without technique", 0, "v4_no_tech"),
])
def test_find_missing_data_handling_v4(text, expected_count, case_id):
    res = find_missing_data_handling_v4(text, window=6)
    assert len(res) == expected_count, f"v4 failed: {case_id}"


# -----------------------------
# v5 – tight template
# -----------------------------
@pytest.mark.parametrize("text, expected_count, case_id", [
    ("Missing covariates were imputed using chained equations (mice).", 1, "v5_template_match"),
    ("Missing data were imputed with LOCF.", 0, "v5_template_nomatch"),
])
def test_find_missing_data_handling_v5(text, expected_count, case_id):
    res = find_missing_data_handling_v5(text)
    assert len(res) == expected_count, f"v5 failed: {case_id}"
