# tests/test_outcome_definition_finder.py
"""
Complete test suite for outcome_definition_finder.py.

This suite provides robust checks for v1 and v2
and lighter validation for v3, v4, and v5 variants,
using clinical/medical outcome definition statements.
"""

import pytest
from pyregularexpression.outcome_definition_finder import (
    find_outcome_definition_v1,
    find_outcome_definition_v2,
    find_outcome_definition_v3,
    find_outcome_definition_v4,
    find_outcome_definition_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The primary outcome was readmission within 30 days.", True, "v1_pos_primary_outcome"),
        ("Endpoints included MI and stroke.", True, "v1_pos_endpoint"),
        ("Overall outcome was satisfactory.", False, "v1_neg_trap_overall"),
        ("Results were reported.", False, "v1_neg_trap_results"),
    ]
)
def test_find_outcome_definition_v1(text, should_match, test_id):
    matches = find_outcome_definition_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ────────────────────────────────────
# Robust Tests for v2 (Cue + Defining Verb)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The outcome was defined as death from any cause.", True, "v2_pos_defined"),
        ("Endpoint considered as readmission within 30 days.", True, "v2_pos_considered"),
        ("Outcome mentioned but no verb.", False, "v2_neg_no_verb"),
        ("Secondary analysis outcomes were ignored.", False, "v2_neg_trap_secondary"),
    ]
)
def test_find_outcome_definition_v2(text, should_match, test_id):
    matches = find_outcome_definition_v2(text, window=5)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Outcome definition:\nReadmission within 30 days was primary.\n", True, "v3_pos_heading_block"),
        ("Primary outcome:\nDeath from any cause.\n", True, "v3_pos_primary_outcome_heading"),
        ("Readmission within 30 days.\n\nOutcome definition:\nNot specified.", False, "v3_neg_outside_block"),
        ("Outcome definition:\n(No outcome reported)\n", False, "v3_neg_empty_block"),
    ]
)
def test_find_outcome_definition_v3(text, should_match, test_id):
    matches = find_outcome_definition_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v4 (Cue + Defining Verb + Criterion)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Primary outcome: readmission within 30 days.", True, "v4_pos_readmission"),
        ("Outcome was defined as death from any cause.", True, "v4_pos_death"),
        ("Outcome defined vaguely.", False, "v4_neg_vague"),
        ("Secondary analysis endpoint considered.", False, "v4_neg_trap_secondary"),
    ]
)
def test_find_outcome_definition_v4(text, should_match, test_id):
    matches = find_outcome_definition_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Primary outcome: readmission within 30 days", True, "v5_pos_readmission_template"),
        ("Outcome was defined as death from any cause", True, "v5_pos_death_template"),
        ("Outcome mentioned without definition", False, "v5_neg_no_definition"),
        ("Secondary outcome listed", False, "v5_neg_secondary_outcome"),
    ]
)
def test_find_outcome_definition_v5(text, should_match, test_id):
    matches = find_outcome_definition_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
