# tests/test_interim_analysis_stopping_rules_finder.py

"""Tests for interim_analysis_stopping_rules_finder.py"""

import pytest
from pyregularexpression.interim_analysis_stopping_rules_finder import (
    find_stopping_rule_v1,
    find_stopping_rule_v2,
    find_stopping_rule_v3
)

# ─────────────────────────────
# v1: Broad match
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The study included an interim analysis after 6 months.", True, "v1_pos_basic"),
        ("A DSMB meeting was scheduled.", True, "v1_pos_dsmb"),
        ("Final analysis was performed after all data was collected.", False, "v1_neg_no_interim"),
        ("This analysis did not involve any early stopping.", False, "v1_neg_explicit_no_stop"),
    ]
)
def test_v1(text, should_match, test_id):
    matches = find_stopping_rule_v1(text)
    assert bool(matches) == should_match, f"v1 failed: {test_id}"


# ─────────────────────────────
# v2: Keyword + boundary
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Interim analysis at 6 months with O’Brien-Fleming boundary p < 0.001.", True, "v2_pos_boundary"),
        ("A stopping rule was applied using p < 0.01.", True, "v2_pos_stat_only"),
        ("DSMB decided based on clinical judgment.", False, "v2_neg_no_stat"),
        ("Interim analysis but no statistical criteria mentioned.", False, "v2_neg_no_boundary"),
    ]
)
def test_v2(text, should_match, test_id):
    matches = find_stopping_rule_v2(text)
    assert bool(matches) == should_match, f"v2 failed: {test_id}"


# ─────────────────────────────
# v3: Tight template
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Interim analysis at 6 months with O’Brien-Fleming boundary p < 0.001.", True, "v3_pos_full_template"),
        ("Interim analysis at 12 weeks using Haybittle-Peto p < 0.01.", True, "v3_pos_alt_template"),
        ("Interim analysis with DSMB but no boundaries given.", False, "v3_neg_missing_boundary"),
        ("Final analysis planned at study completion.", False, "v3_neg_no_interim"),
    ]
)
def test_v3(text, should_match, test_id):
    matches = find_stopping_rule_v3(text)
    assert bool(matches) == should_match, f"v3 failed: {test_id}"
