# tests/test_harms_adverse_event_finder.py

import pytest
from pyregularexpression.harms_adverse_event_finder import (
    find_harms_adverse_event_v1,
    find_harms_adverse_event_v2,
    find_harms_adverse_event_v3,
    find_harms_adverse_event_v4,
    find_harms_adverse_event_v5,
)

# -----------------------------
# v1 – high recall (harms cue + number/percent)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Adverse events occurred in 15% of patients.", True, "v1_pos_basic"),
    ("Side effects were reported.", False, "v1_neg_no_number"),
    ("Complications: 5%", True, "v1_pos_number"),
])
def test_find_harms_adverse_event_v1(text, expected, case_id):
    res = find_harms_adverse_event_v1(text)
    assert (len(res) > 0) == expected, f"v1 failed for ID: {case_id}"


# -----------------------------
# v2 – v1 + group/comparison keyword within ±4 tokens
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Adverse events in treatment group: 15%", True, "v2_pos_group"),
    ("Side effects 5% observed", False, "v2_neg_no_group"),
    ("Complications 10% vs 5% placebo", True, "v2_pos_vs"),
])
def test_find_harms_adverse_event_v2(text, expected, case_id):
    res = find_harms_adverse_event_v2(text, window=4)
    assert (len(res) > 0) == expected, f"v2 failed for ID: {case_id}"


# -----------------------------
# v3 – only inside Harms/Adverse Events heading block
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Adverse Events:\n15% of patients experienced headache.", True, "v3_pos_heading_block"),
    ("Methods: Adverse events were recorded.", False, "v3_neg_no_heading"),
])
def test_find_harms_adverse_event_v3(text, expected, case_id):
    res = find_harms_adverse_event_v3(text, block_chars=400)
    assert (len(res) > 0) == expected, f"v3 failed for ID: {case_id}"


# -----------------------------
# v4 – v2 + severity descriptor
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Adverse events in treatment group 15% serious", True, "v4_pos_severity"),
    ("Side effects 5% observed", False, "v4_neg_no_severity"),
    ("Complications 10% vs 5% placebo grade ≥3", True, "v4_pos_grade"),
])
def test_find_harms_adverse_event_v4(text, expected, case_id):
    res = find_harms_adverse_event_v4(text, window=6)
    assert (len(res) > 0) == expected, f"v4 failed for ID: {case_id}"


# -----------------------------
# v5 – tight template
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("15 % headaches in treatment vs 10 % placebo; no serious events.", True, "v5_pos_template"),
    ("15 % headaches in treatment group; some events.", False, "v5_neg_loose_template"),
])
def test_find_harms_adverse_event_v5(text, expected, case_id):
    res = find_harms_adverse_event_v5(text)
    assert (len(res) > 0) == expected, f"v5 failed for ID: {case_id}"
