# tests/test_event_adjudication_finder.py

import pytest
from pyregularexpression.event_adjudication_finder import (
    find_event_adjudication_v1,
    find_event_adjudication_v2,
    find_event_adjudication_v3,
    find_event_adjudication_v4,
    find_event_adjudication_v5,
)

# -----------------------------
# Test cases for v1 (high recall)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("All events were adjudicated by a committee.", True, "v1_pos_basic_cue"),
    ("The CEC reviewed the endpoint data.", True, "v1_pos_committee_acronym"),
    ("Participants reported adverse events.", False, "v1_neg_no_cue"),
])
def test_find_event_adjudication_v1(text, expected, case_id):
    res = find_event_adjudication_v1(text)
    assert (len(res) > 0) == expected, f"v1 failed for ID: {case_id}"


# -----------------------------
# Test cases for v2 (cue + object keyword)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("All MI events were adjudicated.", True, "v2_pos_event_near_cue"),
    ("The endpoint was adjudicated by the CEC.", True, "v2_pos_endpoint_near_cue"),
    ("The adjudication process was described.", False, "v2_neg_no_object"),
])
def test_find_event_adjudication_v2(text, expected, case_id):
    res = find_event_adjudication_v2(text, window=5)
    assert (len(res) > 0) == expected, f"v2 failed for ID: {case_id}"


# -----------------------------
# Test cases for v3 (inside heading block)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Event Adjudication:\nAll events were adjudicated by a committee.", True, "v3_pos_heading_block"),
    ("Clinical Events Committee:\nEndpoint adjudication was performed.", True, "v3_pos_committee_block"),
    ("Methods: Events were adjudicated by staff.", False, "v3_neg_no_heading"),
])
def test_find_event_adjudication_v3(text, expected, case_id):
    res = find_event_adjudication_v3(text, block_chars=400)
    assert (len(res) > 0) == expected, f"v3 failed for ID: {case_id}"


# -----------------------------
# Test cases for v4 (v2 + independence/blinding term or committee)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("All MI events were independently adjudicated by a blinded CEC.", True, "v4_pos_independent_blinded"),
    ("Endpoint adjudicated by an independent committee.", True, "v4_pos_committee_independent"),
    ("All events were adjudicated without committee oversight.", False, "v4_neg_no_blind_or_committee"),
])
def test_find_event_adjudication_v4(text, expected, case_id):
    res = find_event_adjudication_v4(text, window=6)
    assert (len(res) > 0) == expected, f"v4 failed for ID: {case_id}"


# -----------------------------
# Test cases for v5 (tight template)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("All MI events were independently adjudicated by a blinded CEC.", True, "v5_pos_template"),
    ("Events were adjudicated by committee members.", False, "v5_neg_loose_phrase"),
])
def test_find_event_adjudication_v5(text, expected, case_id):
    res = find_event_adjudication_v5(text)
    assert (len(res) > 0) == expected, f"v5 failed for ID: {case_id}"
