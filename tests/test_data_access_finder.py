# tests/test_data_access_finder.py
"""
Test suite for data_access_finder.py

Covers:
- v1 – high recall: any availability/permission keyword
- v2 – keyword within ±3 tokens of "data/dataset"
- v3 – inside a Data access/availability heading block
- v4 – v2 + formal permission cue or repository reference
- v5 – tight templates (deposited in repository, request + approval)
"""

import pytest
from pyregularexpression.data_access_finder import (
    find_data_access_v1,
    find_data_access_v2,
    find_data_access_v3,
    find_data_access_v4,
    find_data_access_v5,
)

# ─────────────────────────────
# Tests for v1 – High recall
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The dataset is available from the corresponding author upon request.", True, "v1_pos_available"),
        ("Data are deposited in Dryad.", True, "v1_pos_deposited"),
        ("There is an embargo on the dataset for 6 months.", True, "v1_pos_embargo"),
        ("Open access journal policy was described.", False, "v1_trap_open_access"),
        ("Patients had limited access to care.", False, "v1_trap_access_to_care"),
    ]
)
def test_find_data_access_v1(text, should_match, test_id):
    matches = find_data_access_v1(text)
    assert bool(matches) == should_match, f"v1 failed for {test_id}"


# ─────────────────────────────
# Tests for v2 – Near “data” token
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Data are available upon request from the PI.", True, "v2_pos_available_near_data"),
        ("Dataset is accessible via dbGaP.", True, "v2_pos_accessible_dataset"),
        ("The software is available online.", False, "v2_neg_no_data_token"),
        ("Clinical outcomes were accessible to investigators.", False, "v2_neg_outcomes_only"),
    ]
)
def test_find_data_access_v2(text, should_match, test_id):
    matches = find_data_access_v2(text)
    assert bool(matches) == should_match, f"v2 failed for {test_id}"


# ─────────────────────────────
# Tests for v3 – Inside Data access/availability block
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Data Availability:\nThe dataset is available upon request.\n\n", True, "v3_pos_heading_block"),
        ("Data Sharing:\nData are deposited in Zenodo.\n\n", True, "v3_pos_data_sharing"),
        ("Results:\nThe dataset is available upon request.", False, "v3_neg_wrong_section"),
        ("Acknowledgements:\nWe thank participants for providing data.", False, "v3_neg_ack_no_access"),
    ]
)
def test_find_data_access_v3(text, should_match, test_id):
    matches = find_data_access_v3(text)
    assert bool(matches) == should_match, f"v3 failed for {test_id}"


# ─────────────────────────────
# Tests for v4 – Near data + repository/permission keyword
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The dataset is available upon request with IRB approval.", True, "v4_pos_request_irb"),
        ("Data are deposited in Zenodo repository.", True, "v4_pos_repo_zenodo"),
        ("Data are available upon request from the author.", False, "v4_neg_no_repo_or_permission"),
        ("Dataset is accessible in supplementary files.", False, "v4_neg_no_permission_or_repo"),
    ]
)
def test_find_data_access_v4(text, should_match, test_id):
    matches = find_data_access_v4(text)
    assert bool(matches) == should_match, f"v4 failed for {test_id}"


# ─────────────────────────────
# Tests for v5 – Tight templates
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Data are available upon reasonable request with institutional approval.", True, "v5_pos_request_approval"),
        ("Dataset is deposited in the Dryad repository under accession 12345.", True, "v5_pos_repo_template"),
        ("The dataset is shared openly with collaborators.", False, "v5_neg_too_loose"),
        ("Data are available in the manuscript text.", False, "v5_neg_no_template"),
    ]
)
def test_find_data_access_v5(text, should_match, test_id):
    matches = find_data_access_v5(text)
    assert bool(matches) == should_match, f"v5 failed for {test_id}"
