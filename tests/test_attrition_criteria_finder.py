#tests\test_attrition_criteria_finder.py
"""
Complete test suite for attrition_criteria_finder.py.

Includes:
- Robust tests for v1 and v2 (basic cues and context-aware loss detection)
- Functional checks for v3, v4, and v5 (block-based, numeric-based, and template-based)
- All examples based on PubMed/OHDSI-style descriptions of follow-up loss
"""

import pytest
from pyregularexpression.attrition_criteria_finder import (
    find_attrition_criteria_v1,
    find_attrition_criteria_v2,
    find_attrition_criteria_v3,
    find_attrition_criteria_v4,
    find_attrition_criteria_v5,
)

# ─────────────────────────────
# Robust Tests for v1 – High Recall: any attrition cue
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Ten participants were lost to follow-up during the trial.", True, "v1_pos_lost_to_follow_up"),
        ("Three patients withdrew consent after enrollment.", True, "v1_pos_withdrew_consent"),
        ("Five subjects dropped out due to adverse events.", True, "v1_pos_dropped_out"),

        # Trap examples
        ("Screen failures were excluded before randomization.", False, "v1_trap_screen_failures"),
        ("Patients were censored at transplant or death.", False, "v1_trap_censored_event"),
        ("Exit criteria included severe disease.", False, "v1_trap_exit_criteria"),
    ]
)
def test_find_attrition_criteria_v1(text, should_match, test_id):
    matches = find_attrition_criteria_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ─────────────────────────────
# Robust Tests for v2 – Cue + study context (e.g., during study)
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Ten patients dropped out during follow-up due to side effects.", True, "v2_pos_during_followup"),
        ("Seven participants withdrew consent during the study.", True, "v2_pos_during_study"),

        # Trap examples and negatives
        ("Participants were excluded at screening.", False, "v2_trap_screening_excluded"),
        ("Dropped out due to insurance issues before enrollment.", False, "v2_trap_before_enrollment"),
        ("Lost contact with some participants post-study.", False, "v2_neg_after_study_context"),
    ]
)
def test_find_attrition_criteria_v2(text, should_match, test_id):
    matches = find_attrition_criteria_v2(text)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ─────────────────────────────
# Lighter Tests for v3 – Inside attrition/loss heading blocks
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Attrition:\nSeven subjects dropped out due to side effects.\n\n", True, "v3_pos_attrition_heading"),
        ("Loss to follow-up:\nThree patients withdrew consent.\n\n", True, "v3_pos_loss_heading"),

        # Negative: correct cue outside block or in unrelated section
        ("Results:\nFive participants withdrew consent during follow-up.", False, "v3_neg_wrong_heading"),
        ("Cohort characteristics:\nSome participants were lost.", False, "v3_neg_not_attrition_heading"),
    ]
)
def test_find_attrition_criteria_v3(text, should_match, test_id):
    matches = find_attrition_criteria_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"
    
# ─────────────────────────────
# Lighter Tests for v4 – Cue + context + numeric evidence (e.g., "10 participants", "5%")
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Ten participants were lost to follow-up during the study.", True, "v4_pos_count_during_study"),
        ("5% of patients withdrew consent during follow-up.", True, "v4_pos_percent_with_context"),

        # Negative examples
        ("Withdrew consent due to side effects.", False, "v4_neg_no_numeric"),
        ("Lost to follow-up noted in the chart.", False, "v4_neg_no_context_or_number"),
        ("Dropouts occurred mostly before baseline.", False, "v4_neg_prebaseline"),
    ]
)
def test_find_attrition_criteria_v4(text, should_match, test_id):
    matches = find_attrition_criteria_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ─────────────────────────────
# Lighter Tests for v5 – Tight template matches
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("12 participants were lost to follow-up.", True, "v5_pos_participants_lost"),
        ("Withdrew consent during follow-up due to adverse events.", True, "v5_pos_withdrew_during"),

        # Negative examples
        ("Patients lost their ID cards during follow-up.", False, "v5_neg_irrelevant_use_lost"),
        ("Consent withdrawn prior to randomization.", False, "v5_neg_pre_randomization"),
    ]
)
def test_find_attrition_criteria_v5(text, should_match, test_id):
    matches = find_attrition_criteria_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
