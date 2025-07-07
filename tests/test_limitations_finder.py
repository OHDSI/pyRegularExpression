# tests/test_limitations_finder.py

import pytest
from pyregularexpression.limitations_finder import (
    find_limitations_v1,
    find_limitations_v2,
    find_limitations_v3,
    find_limitations_v4,
    find_limitations_v5,
)

# -----------------------------
# v1 – high recall: any limitations cue
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("The limitations of this study include small sample.", True, "v1_pos"),
    ("Potential bias may exist in the design.", True, "v1_pos_bias"),
    ("No issues were noted.", False, "v1_neg"),
])
def test_find_limitations_v1(text, expected, case_id):
    res = find_limitations_v1(text)
    assert (len(res) > 0) == expected, f"v1 failed for ID: {case_id}"


# -----------------------------
# v2 – v1 + explicit self-reference or 'we acknowledge'
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("This study has limitations due to sample size.", True, "v2_pos_selfref"),
    ("Limitations include small sample; we acknowledge bias.", True, "v2_pos_we_ack"),
    ("Limitations in prior studies were noted.", False, "v2_neg_trap"),
])
def test_find_limitations_v2(text, expected, case_id):
    res = find_limitations_v2(text, window=6)
    assert (len(res) > 0) == expected, f"v2 failed for ID: {case_id}"


# -----------------------------
# v3 – only inside Limitations / Strengths and Limitations heading block
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Limitations:\nThis study had a small sample.", True, "v3_pos_heading"),
    ("Strengths and Limitations - Our study may be biased.", True, "v3_pos_heading2"),
    ("Small sample noted outside heading.", False, "v3_neg_outside"),
])
def test_find_limitations_v3(text, expected, case_id):
    res = find_limitations_v3(text, block_chars=400)
    assert (len(res) > 0) == expected, f"v3 failed for ID: {case_id}"


# -----------------------------
# v4 – v2 + weakness keyword in same sentence
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("This study has limitations due to small sample.", True, "v4_pos_sample"),
    ("We acknowledge limitations: underpowered study.", True, "v4_pos_underpowered"),
    ("We acknowledge limitations but no bias detected.", False, "v4_neg_no_weakness"),
])
def test_find_limitations_v4(text, expected, case_id):
    res = find_limitations_v4(text, window=8)
    assert (len(res) > 0) == expected, f"v4 failed for ID: {case_id}"


# -----------------------------
# v5 – tight template: 'Limitations include ...'
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Limitations include small sample and short follow-up.", True, "v5_pos_template"),
    ("Limitations are discussed elsewhere.", False, "v5_neg_loose"),
])
def test_find_limitations_v5(text, expected, case_id):
    res = find_limitations_v5(text)
    assert (len(res) > 0) == expected, f"v5 failed for ID: {case_id}"
