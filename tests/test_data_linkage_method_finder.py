# tests/test_data_linkage_method_finder.py

import pytest
from pyregularexpression.data_linkage_method_finder import (
    find_data_linkage_method_v1,
    find_data_linkage_method_v2,
    find_data_linkage_method_v3,
    find_data_linkage_method_v4,
    find_data_linkage_method_v5,
)

# -----------------------------
# Test cases for v1 (high recall)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Records were linked across hospital episodes.", True, "v1_pos_basic_linked"),
    ("A data linkage procedure was performed.", True, "v1_pos_data_linkage"),
    ("Master patient index was used for record linkage.", True, "v1_pos_master_patient_index"),
    ("We examined the link between exposure and outcome.", False, "v1_neg_link_trap"),
    ("Hyperlink to supplementary materials was provided.", False, "v1_neg_hyperlink"),
])
def test_find_data_linkage_method_v1(text, expected, case_id):
    res = find_data_linkage_method_v1(text)
    assert (len(res) > 0) == expected, f"v1 failed for ID: {case_id}"


# -----------------------------
# Test cases for v2 (link cue + nearby object)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Records were linked across datasets.", True, "v2_pos_records_linked"),
    ("Hospital files linkage was performed.", True, "v2_pos_files_linkage"),
    ("The study described linkage without object terms.", False, "v2_neg_no_object"),
    ("A hyperlink was inserted in the document.", False, "v2_neg_hyperlink"),
])
def test_find_data_linkage_method_v2(text, expected, case_id):
    res = find_data_linkage_method_v2(text, window=3)
    assert (len(res) > 0) == expected, f"v2 failed for ID: {case_id}"


# -----------------------------
# Test cases for v3 (inside heading blocks)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Data Linkage:\nRecords were linked deterministically.", True, "v3_pos_heading_linked"),
    ("Record Linkage - We performed probabilistic matching.", True, "v3_pos_record_heading"),
    ("Methods: Records were linked across registries.", False, "v3_neg_no_heading"),
])
def test_find_data_linkage_method_v3(text, expected, case_id):
    res = find_data_linkage_method_v3(text, block_chars=400)
    assert (len(res) > 0) == expected, f"v3 failed for ID: {case_id}"


# -----------------------------
# Test cases for v4 (link cue + nearby method)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Records were probabilistically linked to registry data.", True, "v4_pos_probabilistic"),
    ("Files were deterministically matched to hospital records.", True, "v4_pos_deterministic"),
    ("Records were linked without specifying method.", False, "v4_neg_no_method"),
    ("Data linkage performed but method not described.", False, "v4_neg_method_missing"),
])
def test_find_data_linkage_method_v4(text, expected, case_id):
    res = find_data_linkage_method_v4(text, window=6)
    assert (len(res) > 0) == expected, f"v4 failed for ID: {case_id}"


# -----------------------------
# Test cases for v5 (tight template)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Hospital admissions were probabilistically linked to death-registry data using date of birth.", True, "v5_pos_template_probabilistic"),
    ("Patient files were deterministically matched to national registry.", True, "v5_pos_template_deterministic"),
    ("Records were linked but without template structure.", False, "v5_neg_loose_phrase"),
])
def test_find_data_linkage_method_v5(text, expected, case_id):
    res = find_data_linkage_method_v5(text)
    assert (len(res) > 0) == expected, f"v5 failed for ID: {case_id}"
