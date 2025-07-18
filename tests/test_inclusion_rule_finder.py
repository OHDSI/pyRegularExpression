# tests/test_inclusion_rule_finder.py
"""
Complete test suite for inclusion_rule_finder.py.

This suite provides robust, comprehensive checks for v1 and v2, assuming their
core bugs have been fixed. It also includes lighter, representative checks for
v3, v4, and v5 to ensure their basic functionality.
"""

import pytest
from pyregularexpression.inclusion_rule_finder import (
    find_inclusion_rule_v1,
    find_inclusion_rule_v2,
    find_inclusion_rule_v3,
    find_inclusion_rule_v4,
    find_inclusion_rule_v5,
)

# ─────────────────────────────
# Robust Tests for v1 (High Recall, with effective trap filtering)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive Examples: Should match any basic inclusion cue.
        ("Participants were required to have a diagnosis of hypertension.", True, "v1_pos_required_to_have"),
        ("Subjects were eligible if they were aged between 18 and 65 years.", True, "v1_pos_eligible_if"),
        ("Inclusion criteria: male, aged 50–75 years, BMI <30.", True, "v1_pos_colon_criteria"),
        ("To be included, patients must have completed at least one cycle.", True, "v1_pos_must_have"),
        ("Exclusion criteria also included pregnancy or lactation.", True, "v1_pos_finds_keyword_in_exclusion_context"),

        # Negative Examples: Should not match sentences without cues OR sentences that are traps.
        ("The study was approved by the institutional review board.", False, "v1_neg_no_cue"),
        ("The primary endpoint was overall survival.", False, "v1_neg_no_cue_endpoint"),
        # The following tests assume the trap filtering is fixed and now works correctly.
        ("The study included 200 participants from five centers.", False, "v1_neg_trap_study_included"),
        ("Patients included in this analysis were observed for safety.", False, "v1_neg_trap_included_in_analysis"),
        ("Our analysis included adjustment for baseline covariates.", False, "v1_neg_trap_analysis_included"),
    ]
)
def test_find_inclusion_rule_v1_robust(text, should_match, test_id):
    """Tests v1's high-recall matching and its ability to correctly filter trap phrases."""
    matches = find_inclusion_rule_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"


# ─────────────────────────────
# Robust Tests for v2 (Cue + Gating Token, with multi-word fix)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive Examples: Inclusion cue must be near a gating token.
        ("Participants were eligible if they had one cardiovascular event.", True, "v2_pos_eligible_if"),
        ("Subjects included only those with chronic kidney disease.", True, "v2_pos_included_only"),
        ("To be eligible, a patient must have a signed consent form.", True, "v2_pos_fixed_multi_word_gate"),
        ("Patients are eligible and must have an ECOG status of 0-1.", True, "v2_pos_must_have_as_gate_2"),
        ("Inclusion criteria: patients with stage III cancer.", True, "v2_pos_fixed_colon_gate"),

        # Negative Examples: No match if gating token is absent or logic fails.
        ("Eligible subjects were adults aged 18 to 65 years.", False, "v2_neg_no_gating_token"),
        ("All included patients provided informed consent.", False, "v2_neg_no_gating_token_2"),
        ("Inclusion criteria were broad and generally inclusive.", False, "v2_neg_no_colon_gate"),
        ("This was a study about eligible patient populations.", False, "v2_neg_cue_without_gate"),
        ("The analysis included patients if they were enrolled before 2020.", False, "v2_neg_trap_analysis_included"),
    ]
)
def test_find_inclusion_rule_v2_robust(text, should_match, test_id):
    """
    Tests v2, which requires a gating token near the inclusion cue.
    Assumes the logic is fixed to handle multi-word gating tokens (e.g., 'must have').
    """
    matches = find_inclusion_rule_v2(text, window=5)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Checks for v3-v5
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive: Cue is inside a dedicated heading block.
        ("Inclusion criteria:\nPatients must have type 2 diabetes.\n\n", True, "v3_pos_simple_block"),
        ("eligibility criteria\n- Participants must have completed one vaccine dose.", True, "v3_pos_lowercase_heading"),

        # Negative: Cue is outside a recognized heading block.
        ("A patient must be eligible.\n\nInclusion criteria:\n(no rule here)", False, "v3_neg_cue_before_block"),
        ("PRIMARY INCLUSION CRITERIA:\nPatients must have failed prior therapy.", False, "v3_neg_unrecognized_heading"),
    ]
)
def test_find_inclusion_rule_v3_light(text, should_match, test_id):
    """Light checks for v3, assuming the greedy heading regex bug is fixed."""
    matches = find_inclusion_rule_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"


@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive: v2 match + a strong conditional verb.
        ("Eligible if they must have completed surgical resection.", True, "v4_pos_must_have_if"),

        # Negative: v2 match but without the required strong verb.
        ("Participants were eligible if they were over 18.", False, "v4_neg_no_strong_verb"),
        ("Subjects required to have ECOG status ≤ 1.", False, "v4_neg_no_gating_word"), # Fails v2 check
    ]
)
def test_find_inclusion_rule_v4_light(text, should_match, test_id):
    """Light checks for v4, assuming multi-word matching is fixed."""
    matches = find_inclusion_rule_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"


@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive: Must exactly match one of the tight templates.
        ("Inclusion criteria: adults aged 18–65, non-smokers.", True, "v5_pos_colon_list"),
        ("Patients were eligible if they exhibited symptoms of depression.", True, "v5_pos_plural_were_eligible_if"),

        # Negative: Do not match if template is violated.
        ("Patient was eligible if creatinine clearance > 50 mL/min.", False, "v5_neg_singular_was_eligible"),
        ("Eligible patients had to have hypertension to enroll.", False, "v5_neg_had_to_have_not_template"),
    ]
)
def test_find_inclusion_rule_v5_light(text, should_match, test_id):
    """Light checks for v5's high-precision template matching."""
    matches = find_inclusion_rule_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
