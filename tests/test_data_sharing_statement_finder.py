# tests/test_data_sharing_statement_finder.py

import pytest
from pyregularexpression.data_sharing_statement_finder import (
    find_data_sharing_statement_v1,
    find_data_sharing_statement_v2,
    find_data_sharing_statement_v3,
    find_data_sharing_statement_v4,
    find_data_sharing_statement_v5,
)

# -----------------------------
# Test cases for v1 (high recall)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Data will be shared upon request.", True, "v1_pos_shared_request"),
    ("Datasets are available in Zenodo.", True, "v1_pos_repo_zenodo"),
    ("Data sharing statement included in manuscript.", True, "v1_pos_data_sharing_stmt"),
    ("Publicly available census data were used.", False, "v1_neg_trap_public"),
    ("Open access dataset description provided.", False, "v1_neg_trap_open_access"),
])
def test_find_data_sharing_statement_v1(text, expected, case_id):
    res = find_data_sharing_statement_v1(text)
    assert (len(res) > 0) == expected, f"v1 failed for ID: {case_id}"


# -----------------------------
# Test cases for v2 (cue + nearby availability verb)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Data will be shared upon request.", True, "v2_pos_shared_request"),
    ("Dataset deposited in Dryad after publication.", True, "v2_pos_repo_deposit"),
    ("Data available in repository.", True, "v2_pos_available_repo"),
    ("Data sharing statement included.", False, "v2_neg_no_verb"),
    ("Zenodo repository mentioned without dataset.", False, "v2_neg_no_availability"),
])
def test_find_data_sharing_statement_v2(text, expected, case_id):
    res = find_data_sharing_statement_v2(text, window=4)
    assert (len(res) > 0) == expected, f"v2 failed for ID: {case_id}"


# -----------------------------
# Test cases for v3 (inside heading blocks)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Data Availability:\nData will be shared upon request.", True, "v3_pos_heading_shared"),
    ("Availability Statement - Datasets deposited in Dryad.", True, "v3_pos_heading_dryad"),
    ("Methods: Data are available in Zenodo.", False, "v3_neg_no_heading"),
])
def test_find_data_sharing_statement_v3(text, expected, case_id):
    res = find_data_sharing_statement_v3(text, block_chars=400)
    assert (len(res) > 0) == expected, f"v3 failed for ID: {case_id}"


# -----------------------------
# Test cases for v4 (cue + verb + access mechanism)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Dataset deposited in Zenodo and accessible to researchers.", True, "v4_pos_repo_zenodo"),
    ("Data sharing statement included without access info.", False, "v4_neg_no_access_mech"),
    ("Data available but no repository or request info.", False, "v4_neg_missing_mech"),
])
def test_find_data_sharing_statement_v4(text, expected, case_id):
    res = find_data_sharing_statement_v4(text, window=6)
    assert (len(res) > 0) == expected, f"v4 failed for ID: {case_id}"


# -----------------------------
# Test cases for v5 (tight template)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Individual participant data will be available in Dryad after publication.", True, "v5_pos_template_dryad"),
    ("Data will be available upon request after study completion.", True, "v5_pos_template_request"),
    ("Datasets deposited but no access details provided.", False, "v5_neg_loose_phrase"),
])
def test_find_data_sharing_statement_v5(text, expected, case_id):
    res = find_data_sharing_statement_v5(text)
    assert (len(res) > 0) == expected, f"v5 failed for ID: {case_id}"
