# tests/test_index_date_finder.py

import pytest
from pyregularexpression.index_date_finder import (
    find_index_date_v1,
    find_index_date_v2,
    find_index_date_v3,
    find_index_date_v4,
    find_index_date_v5,
)

# -----------------------------
# v1 – high recall (any index/baseline date)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("The index date was recorded as 2020-01-01.", True, "v1_pos_basic"),
    ("Baseline date needs to be considered.", True, "v1_pos_baseline"),
    ("No date mentioned here.", False, "v1_neg_none"),
])
def test_find_index_date_v1(text, expected, case_id):
    res = find_index_date_v1(text)
    assert (len(res) > 0) == expected, f"v1 failed for ID: {case_id}"


# -----------------------------
# v2 – cue + defining verb within ±5 tokens
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("The index date was defined as the first visit.", True, "v2_pos_defined"),
    ("Baseline date assigned on admission.", True, "v2_pos_assigned"),
    ("Index date recorded without defining verb.", False, "v2_neg_no_verb"),
])
def test_find_index_date_v2(text, expected, case_id):
    res = find_index_date_v2(text, window=5)
    assert (len(res) > 0) == expected, f"v2 failed for ID: {case_id}"


# -----------------------------
# v3 – only inside dedicated Index/Baseline heading blocks
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Index date:\n2020-01-01 recorded.", True, "v3_pos_heading"),
    ("Baseline date - assigned later.", True, "v3_pos_heading_dash"),
    ("The index date was recorded in methods section.", False, "v3_neg_no_heading"),
])
def test_find_index_date_v3(text, expected, case_id):
    res = find_index_date_v3(text, block_chars=300)
    assert (len(res) > 0) == expected, f"v3 failed for ID: {case_id}"


# -----------------------------
# v4 – v2 + explicit '=' or defining verb, excludes traps
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Index date = 2020-01-01", True, "v4_pos_equal"),
    ("Baseline date was defined as 2020-01-01", True, "v4_pos_defined"),
    ("Index patient was set on admission", False, "v4_neg_trap"),
])
def test_find_index_date_v4(text, expected, case_id):
    res = find_index_date_v4(text, window=5)
    assert (len(res) > 0) == expected, f"v4 failed for ID: {case_id}"


# -----------------------------
# v5 – tight template with '=' or 'was defined as'
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Index date = 2020-01-01", True, "v5_pos_equal"),
    ("Baseline date was defined as the first visit", True, "v5_pos_defined_as"),
    ("Index date assigned later", False, "v5_neg_loose"),
])
def test_find_index_date_v5(text, expected, case_id):
    res = find_index_date_v5(text)
    assert (len(res) > 0) == expected, f"v5 failed for ID: {case_id}"
