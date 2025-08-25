# tests/test_changes_to_outcomes_finder.py
"""
Complete test suite for changes_to_outcomes_finder.py.

Includes:
- Robust tests for v1 and v2 (high recall and context-aware temporal detection)
- Functional checks for v3, v4, and v5 (block-based, reason-based, and template-based)
- Examples based on typical trial protocol/clinical study texts
"""

import pytest
from pyregularexpression.changes_to_outcomes_finder import (
    find_changes_to_outcomes_v1,
    find_changes_to_outcomes_v2,
    find_changes_to_outcomes_v3,
    find_changes_to_outcomes_v4,
    find_changes_to_outcomes_v5,
)

# ─────────────────────────────
# Robust Tests for v1 – High Recall: any modification cue
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("The primary outcome was changed after the first interim analysis.", True, "v1_pos_primary_changed"),
        ("We added a new secondary outcome to measure quality of life.", True, "v1_pos_added_secondary"),
        ("Outcome measures were revised due to protocol update.", True, "v1_pos_revised_outcome"),
        ("The study amended the outcomes in response to regulatory feedback.", True, "v1_pos_amended_outcomes"),

        # Trap / negatives
        ("There were significant changes in patient outcomes.", False, "v1_trap_significant_change"),
        ("Outcome changes were noted in historical trials.", False, "v1_trap_historical"),
        ("No modifications were made.", False, "v1_neg_no_modification"),
    ]
)
def test_find_changes_to_outcomes_v1(text, should_match, test_id):
    matches = find_changes_to_outcomes_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ─────────────────────────────
# Robust Tests for v2 – Cue + temporal context
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("After the trial began, we added a new secondary outcome.", True, "v2_pos_after_trial_began"),
        ("Primary outcome was changed midway through the study.", True, "v2_pos_midstudy_change"),
        ("The outcomes were revised 3 months into the trial.", True, "v2_pos_3_months_into_trial"),

        # Trap / negatives
        ("We changed the primary outcome last year.", False, "v2_trap_outside_trial"),
        ("Protocol amendments in prior studies revised outcomes.", False, "v2_trap_prior_study"),
        ("The primary outcome remained unchanged.", False, "v2_neg_no_change"),
    ]
)
def test_find_changes_to_outcomes_v2(text, should_match, test_id):
    matches = find_changes_to_outcomes_v2(text)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ─────────────────────────────
# Lighter Tests for v3 – Only inside headings
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Protocol amendments:\nThe primary outcome was changed due to interim analysis.\n", True, "v3_pos_heading_change"),
        ("Outcome changes:\nWe added a secondary outcome to measure fatigue.\n", True, "v3_pos_heading_added"),

        # Negative: correct cue outside heading
        ("Results:\nThe primary outcome was changed midway through the study.", False, "v3_neg_outside_heading"),
        ("Discussion:\nWe added a secondary outcome.", False, "v3_neg_wrong_section"),
    ]
)
def test_find_changes_to_outcomes_v3(text, should_match, test_id):
    matches = find_changes_to_outcomes_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ─────────────────────────────
# Lighter Tests for v4 – Cue + temporal + reason phrase
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Due to low recruitment, the primary outcome was changed midway.", True, "v4_pos_due_to_low_recruitment"),
        ("Because of safety concerns, we amended the secondary outcome during the trial.", True, "v4_pos_because_of_safety"),

        # Negative examples
        ("The primary outcome was changed midway through the trial.", False, "v4_neg_no_reason"),
        ("We added a secondary outcome after trial began.", False, "v4_neg_no_reason_phrase"),
    ]
)
def test_find_changes_to_outcomes_v4(text, should_match, test_id):
    matches = find_changes_to_outcomes_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ─────────────────────────────
# Lighter Tests for v5 – Tight template
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Due to low event rate, the primary outcome was changed from OS to DFS midway.", True, "v5_pos_template_low_event"),
        ("Because of slow accrual, the primary outcome was changed from PFS to DFS after 50 events.", True, "v5_pos_template_slow_accrual"),

        # Negative examples
        ("The primary outcome was changed midway through the study.", False, "v5_neg_no_template_phrase"),
        ("Outcomes were amended due to regulatory guidance in general.", False, "v5_neg_different_reason_format"),
    ]
)
def test_find_changes_to_outcomes_v5(text, should_match, test_id):
    matches = find_changes_to_outcomes_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
