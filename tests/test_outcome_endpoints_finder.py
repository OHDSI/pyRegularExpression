# tests/test_outcome_endpoints_finder.py
"""
Complete test suite for outcome_endpoints_finder.py.

This suite provides robust checks for v1 and v2
and lighter validation for v3, v4, and v5 variants,
using clinical/medical outcome endpoint statements.
"""

import pytest
from pyregularexpression.outcome_endpoints_finder import (
    find_outcome_endpoints_v1,
    find_outcome_endpoints_v2,
    find_outcome_endpoints_v3,
    find_outcome_endpoints_v4,
    find_outcome_endpoints_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Primary outcome was progression-free survival.", True, "v1_pos_primary"),
        ("Secondary endpoints included overall survival and response rate.", True, "v1_pos_secondary"),
        ("Clinical outcome was satisfactory.", False, "v1_neg_trap_clinical"),
        ("Outcome of the procedure was successful.", False, "v1_neg_trap_procedure"),
    ]
)
def test_find_outcome_endpoints_v1(text, should_match, test_id):
    matches = find_outcome_endpoints_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ────────────────────────────────────
# Robust Tests for v2 (Cue + Measurement Verb / Time)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Primary outcome was measured at 12 months.", True, "v2_pos_measured"),
        ("Secondary endpoints were assessed at 6 months.", True, "v2_pos_assessed"),
        ("Primary outcome mentioned without verb.", False, "v2_neg_no_verb"),
        ("Outcome of procedure assessed.", False, "v2_neg_trap_procedure"),
    ]
)
def test_find_outcome_endpoints_v2(text, should_match, test_id):
    matches = find_outcome_endpoints_v2(text, window=4)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Outcomes:\nPrimary outcome was PFS at 12 months.\n", True, "v3_pos_heading_block"),
        ("Outcome measures:\nSecondary endpoints included OS and response.\n", True, "v3_pos_measures_heading"),
        ("Primary outcome was PFS.\n\nOutcomes:\nNot specified.", False, "v3_neg_outside_block"),
        ("Outcome measures:\n(No endpoints reported)\n", False, "v3_neg_empty_block"),
    ]
)
def test_find_outcome_endpoints_v3(text, should_match, test_id):
    matches = find_outcome_endpoints_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v4 (Cue + Measurement + Primary/Secondary Distinction)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Primary outcome was PFS at 12 months; secondary outcomes included OS.", True, "v4_pos_primary_secondary"),
        ("Primary outcome measured at 6 months; secondary endpoint assessed at 12 months.", True, "v4_pos_multiple"),
        ("Primary outcome mentioned only.", False, "v4_neg_no_secondary"),
        ("Secondary outcome included only.", False, "v4_neg_no_primary"),
    ]
)
def test_find_outcome_endpoints_v4(text, should_match, test_id):
    matches = find_outcome_endpoints_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Primary outcome was progression-free survival at 12 months; secondary outcomes included overall survival.", True, "v5_pos_template"),
        ("Primary endpoint was assessed at 6 months; secondary endpoints included response rate.", True, "v5_pos_template_alt"),
        ("Primary outcome mentioned without secondary.", False, "v5_neg_missing_secondary"),
        ("Secondary outcome included only.", False, "v5_neg_missing_primary"),
    ]
)
def test_find_outcome_endpoints_v5(text, should_match, test_id):
    matches = find_outcome_endpoints_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
