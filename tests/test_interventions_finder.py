# tests/test_interventions_finder.py

import pytest
from pyregularexpression.interventions_finder import (
    find_interventions_v1,
    find_interventions_v2,
    find_interventions_v3,
    find_interventions_v4,
    find_interventions_v5,
)

# -----------------------------
# v1 – high recall (any arm/treatment cue)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("The intervention group received the drug.", True, "v1_pos_intervention"),
    ("Control group was given placebo.", True, "v1_pos_control"),
    ("Participants were observed only.", False, "v1_neg_none"),
])
def test_find_interventions_v1(text, expected, case_id):
    res = find_interventions_v1(text)
    assert (len(res) > 0) == expected, f"v1 failed for ID: {case_id}"


# -----------------------------
# v2 – arm cue + treatment/action/agent within ±4 tokens
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("The intervention group received the drug.", True, "v2_pos_intervention_action"),
    ("Control group administered placebo.", True, "v2_pos_control_action"),
    ("Intervention group observed only.", False, "v2_neg_no_action"),
])
def test_find_interventions_v2(text, expected, case_id):
    res = find_interventions_v2(text, window=4)
    assert (len(res) > 0) == expected, f"v2 failed for ID: {case_id}"


# -----------------------------
# v3 – only inside Intervention/Treatment heading blocks
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Interventions:\nExperimental arm received drug.", True, "v3_pos_heading"),
    ("Treatments - Control group given placebo.", True, "v3_pos_heading_dash"),
    ("Experimental arm received drug outside heading.", False, "v3_neg_no_heading"),
])
def test_find_interventions_v3(text, expected, case_id):
    res = find_interventions_v3(text, block_chars=400)
    assert (len(res) > 0) == expected, f"v3 failed for ID: {case_id}"


# -----------------------------
# v4 – v2 + explicit control arm or comparator cue
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Experimental arm received drug; control group given placebo.", True, "v4_pos_control"),
    ("Intervention arm treated with medication, no control.", False, "v4_neg_no_control"),
])
def test_find_interventions_v4(text, expected, case_id):
    res = find_interventions_v4(text, window=6)
    assert (len(res) > 0) == expected, f"v4 failed for ID: {case_id}"


# -----------------------------
# v5 – tight template: paired description of experimental vs control arms
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Experimental arm received drug; control arm received placebo.", True, "v5_pos_template"),
    ("Experimental arm received drug only.", False, "v5_neg_loose"),
])
def test_find_interventions_v5(text, expected, case_id):
    res = find_interventions_v5(text)
    assert (len(res) > 0) == expected, f"v5 failed for ID: {case_id}"
