# tests/test_data_source_type_finder.py

import pytest
from pyregularexpression.data_source_type_finder import (
    find_data_source_type_v1,
    find_data_source_type_v2,
    find_data_source_type_v3,
    find_data_source_type_v4,
    find_data_source_type_v5,
)

# -----------------------------
# Test cases for v1 (high recall)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("We used EHR data from multiple hospitals.", True, "v1_pos_ehr"),
    ("Claims data were obtained from insurance records.", True, "v1_pos_claims"),
    ("National inpatient sample was analyzed.", True, "v1_pos_nis"),
    ("SQL database was queried for patient info.", False, "v1_neg_trap_sql"),
    ("DataTable software used for analysis.", False, "v1_neg_trap_datatable"),
])
def test_find_data_source_type_v1(text, expected, case_id):
    res = find_data_source_type_v1(text)
    assert (len(res) > 0) == expected, f"v1 failed for ID: {case_id}"


# -----------------------------
# Test cases for v2 (keyword near data/records/dataset)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("EHR dataset was collected from hospitals.", True, "v2_pos_ehr_dataset"),
    ("Registry data were obtained nationwide.", True, "v2_pos_registry_data"),
    ("Survey information was collected.", False, "v2_neg_no_data_token"),
])
def test_find_data_source_type_v2(text, expected, case_id):
    res = find_data_source_type_v2(text, window=2)
    assert (len(res) > 0) == expected, f"v2 failed for ID: {case_id}"


# -----------------------------
# Test cases for v3 (inside heading blocks)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Data Source:\nEHR data were analyzed.", True, "v3_pos_heading_ehr"),
    ("Data Type - Claims records were used.", True, "v3_pos_heading_claims"),
    ("Methods: Registry data collected.", False, "v3_neg_no_heading"),
])
def test_find_data_source_type_v3(text, expected, case_id):
    res = find_data_source_type_v3(text, block_chars=250)
    assert (len(res) > 0) == expected, f"v3 failed for ID: {case_id}"


# -----------------------------
# Test cases for v4 (v2 + qualifier tokens)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Population-based registry data were analyzed.", True, "v4_pos_pop_based_registry"),
    ("EHR data without qualifier mentioned.", False, "v4_neg_no_qualifier"),
])
def test_find_data_source_type_v4(text, expected, case_id):
    res = find_data_source_type_v4(text, window=3)
    assert (len(res) > 0) == expected, f"v4 failed for ID: {case_id}"


# -----------------------------
# Test cases for v5 (tight template)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("We used nationwide insurance claims data from 2010-2020.", True, "v5_pos_template_claims"),
    ("EHR-derived database from 2005-2015 was analyzed.", True, "v5_pos_template_ehr"),
    ("Registry data analyzed without qualifier.", False, "v5_neg_loose_phrase"),
])
def test_find_data_source_type_v5(text, expected, case_id):
    res = find_data_source_type_v5(text)
    assert (len(res) > 0) == expected, f"v5 failed for ID: {case_id}"
