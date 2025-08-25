# tests/test_losses_exclusion_finder.py

import pytest
from pyregularexpression.losses_exclusion_finder import (
    find_losses_exclusion_v1,
    find_losses_exclusion_v2,
    find_losses_exclusion_v3,
    find_losses_exclusion_v4,
    find_losses_exclusion_v5,
)

# -----------------------------
# v1 – high recall: any dropout/loss cue + number
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("5 lost to follow-up.", True, "v1_pos_lost"),
    ("2 withdrew consent.", True, "v1_pos_withdrew"),
    ("No participants dropped.", False, "v1_neg"),
])
def test_find_losses_exclusion_v1(text, expected, case_id):
    res = find_losses_exclusion_v1(text)
    assert (len(res) > 0) == expected, f"v1 failed for ID: {case_id}"


# -----------------------------
# v2 – v1 + follow-up/analysis stage within ±4 tokens
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("5 lost to follow-up during analysis.", True, "v2_pos_stage"),
    ("2 withdrew consent in study period.", True, "v2_pos_stage2"),
    ("3 lost without stage info.", False, "v2_neg_no_stage"),
])
def test_find_losses_exclusion_v2(text, expected, case_id):
    res = find_losses_exclusion_v2(text, window=4)
    assert (len(res) > 0) == expected, f"v2 failed for ID: {case_id}"


# -----------------------------
# v3 – only inside Participant Flow / Losses heading block
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Participant Flow:\n5 lost to follow-up.", True, "v3_pos_heading"),
    ("Losses and Exclusions - 2 withdrew consent.", True, "v3_pos_heading2"),
    ("Outside heading: 5 dropped out.", False, "v3_neg_outside"),
])
def test_find_losses_exclusion_v3(text, expected, case_id):
    res = find_losses_exclusion_v3(text, block_chars=500)
    assert (len(res) > 0) == expected, f"v3 failed for ID: {case_id}"


# -----------------------------
# v4 – v2 + explicit reason phrase in same sentence
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("5 lost to follow-up due to side effects.", True, "v4_pos_reason"),
    ("2 withdrew because of adverse event.", True, "v4_pos_reason2"),
    ("3 dropped out with no reason reported.", False, "v4_neg_no_reason"),
])
def test_find_losses_exclusion_v4(text, expected, case_id):
    res = find_losses_exclusion_v4(text, window=6)
    assert (len(res) > 0) == expected, f"v4 failed for ID: {case_id}"


# -----------------------------
# v5 – tight template: '5 lost to follow-up, 2 withdrew due to ...'
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("5 lost to follow-up, 2 withdrew due to side effects.", True, "v5_pos_template"),
    ("5 lost to follow-up; 2 withdrew consent.", False, "v5_neg_not_template"),
])
def test_find_losses_exclusion_v5(text, expected, case_id):
    res = find_losses_exclusion_v5(text)
    assert (len(res) > 0) == expected, f"v5 failed for ID: {case_id}"
