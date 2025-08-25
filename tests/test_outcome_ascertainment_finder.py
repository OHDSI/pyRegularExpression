# tests/test_outcome_ascertainment_finder.py
"""
Complete test suite for outcome_ascertainment_finder.py.

This suite provides robust checks for v1 and v2
and lighter validation for v3, v4, and v5 variants,
using clinical/medical-style outcome ascertainment statements.
"""

import pytest
from pyregularexpression.outcome_ascertainment_finder import (
    find_outcome_ascertainment_v1,
    find_outcome_ascertainment_v2,
    find_outcome_ascertainment_v3,
    find_outcome_ascertainment_v4,
    find_outcome_ascertainment_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Outcomes were ascertained via medical records.", True, "v1_pos_ascertained"),
        ("Events were identified by chart review.", True, "v1_pos_identified"),
        ("Bias in ascertainment was noted.", False, "v1_neg_trap_bias"),
        ("No confirmation of events.", False, "v1_neg_no_verb"),
    ]
)
def test_find_outcome_ascertainment_v1(text, should_match, test_id):
    matches = find_outcome_ascertainment_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ────────────────────────────────────
# Robust Tests for v2 (Cue + Source/Preposition)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Outcomes were ascertained via medical records.", True, "v2_pos_via"),
        ("Events confirmed through imaging.", True, "v2_pos_through"),
        ("Outcomes ascertained, no source mentioned.", False, "v2_neg_no_source"),
        ("Bias ascertainment via chart review.", False, "v2_neg_trap_bias"),
    ]
)
def test_find_outcome_ascertainment_v2(text, should_match, test_id):
    matches = find_outcome_ascertainment_v2(text, window=5)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Outcome ascertainment:\nEvents were confirmed via chart review.\n", True, "v3_pos_heading_block"),
        ("Event verification:\nStroke events identified.\n", True, "v3_pos_event_verification"),
        ("Events confirmed.\n\nOutcome ascertainment:\nNone reported.", False, "v3_neg_outside_block"),
        ("Outcome ascertainment:\n(No events reported)\n", False, "v3_neg_empty_block"),
    ]
)
def test_find_outcome_ascertainment_v3(text, should_match, test_id):
    matches = find_outcome_ascertainment_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v4 (Cue + Source + Outcome/Imaging)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Stroke events were verified via imaging.", True, "v4_pos_stroke"),
        ("Outcomes confirmed by medical record review.", True, "v4_pos_medical_record"),
        ("Events ascertained via survey.", False, "v4_neg_non_outcome_source"),
        ("Bias ascertainment via chart review.", False, "v4_neg_trap_bias"),
    ]
)
def test_find_outcome_ascertainment_v4(text, should_match, test_id):
    matches = find_outcome_ascertainment_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Stroke events verified via imaging.", True, "v5_pos_stroke_template"),
        ("Outcomes were confirmed by medical record review.", True, "v5_pos_medical_record_template"),
        ("Events captured.", False, "v5_neg_missing_source"),
        ("Bias ascertainment via registry.", False, "v5_neg_trap_bias"),
    ]
)
def test_find_outcome_ascertainment_v5(text, should_match, test_id):
    matches = find_outcome_ascertainment_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
