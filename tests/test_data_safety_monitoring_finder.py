# tests/test_data_safety_monitoring_finder.py

import pytest
from pyregularexpression.data_safety_monitoring_finder import (
    find_data_safety_monitoring_v1,
    find_data_safety_monitoring_v2,
    find_data_safety_monitoring_v3,
    find_data_safety_monitoring_v4,
    find_data_safety_monitoring_v5,
)

# -----------------------------
# Test cases for v1 (high recall)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("The Data Safety Monitoring Board reviewed the trial.", True, "v1_pos_dsmb"),
    ("An independent DMC monitored the study.", True, "v1_pos_dmc"),
    ("Periodic safety review was performed by the DSMB.", True, "v1_pos_periodic_review"),
    ("Monitoring of data quality was performed.", False, "v1_neg_data_quality_trap"),
    ("Safety sheet was submitted by the investigators.", False, "v1_neg_sheet_trap"),
])
def test_find_data_safety_monitoring_v1(text, expected, case_id):
    res = find_data_safety_monitoring_v1(text)
    assert (len(res) > 0) == expected, f"v1 failed for ID: {case_id}"


# -----------------------------
# Test cases for v2 (cue + nearby safety verb)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("DSMB reviewed the adverse events.", True, "v2_pos_reviewed"),
    ("DMC met quarterly to evaluate safety.", True, "v2_pos_met_quarterly"),
    ("DSMB provided guidance but did not meet.", False, "v2_neg_no_verb"),
    ("Monitoring of DSMB activities was described.", False, "v2_neg_trap_monitoring"),
])
def test_find_data_safety_monitoring_v2(text, expected, case_id):
    res = find_data_safety_monitoring_v2(text, window=4)
    assert (len(res) > 0) == expected, f"v2 failed for ID: {case_id}"


# -----------------------------
# Test cases for v3 (inside heading blocks)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Data Safety Monitoring:\nThe DSMB met quarterly.", True, "v3_pos_heading_dsmb"),
    ("DSMB - Independent committee reviewed adverse events.", True, "v3_pos_heading_dmc"),
    ("Methods: The DSMB reviewed safety data.", False, "v3_neg_no_heading"),
])
def test_find_data_safety_monitoring_v3(text, expected, case_id):
    res = find_data_safety_monitoring_v3(text, block_chars=400)
    assert (len(res) > 0) == expected, f"v3 failed for ID: {case_id}"


# -----------------------------
# Test cases for v4 (cue + verb + extra frequency/independence/safety)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("An independent DSMB reviewed safety data quarterly.", True, "v4_pos_independent_quarterly"),
    ("DSMB monitored AE reports periodically.", True, "v4_pos_periodic_monitoring"),
    ("DMC met but did not review safety data.", False, "v4_neg_no_extra"),
    ("DSMB met; study safety information not mentioned.", False, "v4_neg_missing_safety"),
])
def test_find_data_safety_monitoring_v4(text, expected, case_id):
    res = find_data_safety_monitoring_v4(text, window=6)
    assert (len(res) > 0) == expected, f"v4 failed for ID: {case_id}"


# -----------------------------
# Test cases for v5 (tight template)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("An independent DSMB met quarterly to review safety data.", True, "v5_pos_template"),
    ("Independent DMC met to review safety data for adverse events.", True, "v5_pos_template_dmc"),
    ("DSMB met but did not review safety data.", False, "v5_neg_loose_phrase"),
])
def test_find_data_safety_monitoring_v5(text, expected, case_id):
    res = find_data_safety_monitoring_v5(text)
    assert (len(res) > 0) == expected, f"v5 failed for ID: {case_id}"
