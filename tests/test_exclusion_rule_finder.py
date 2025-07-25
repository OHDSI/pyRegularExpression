# tests/test_exclusion_rule_finder.py
"""
Complete test suite for exclusion_rule_finder.py.

This suite provides robust, comprehensive checks for v1 and v2,
with lighter validation for v3, v4, and v5 variants.
"""

import pytest
from pyregularexpression.exclusion_rule_finder import (
    find_exclusion_rule_v1,
    find_exclusion_rule_v2,
    find_exclusion_rule_v3,
    find_exclusion_rule_v4,
    find_exclusion_rule_v5,
)

# ─────────────────────────────
# Robust Tests for v1 (High Recall with trap filtering)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive: Basic exclusion cues
        ("Patients were excluded due to prior stroke.", True, "v1_pos_excluded_due_to"),
        ("Subjects not eligible if they had uncontrolled hypertension.", True, "v1_pos_not_eligible_if"),
        ("Exclusion criteria include pregnancy and lactation.", True, "v1_pos_criteria_include"),
        ("Must not have received prior radiation therapy.", True, "v1_pos_must_not_have"),
        ("Participants were excluded only if they failed screening.", True, "v1_pos_excluded_only_if"),

        # Negative: Traps and non-rule statements
        ("Twenty participants dropped out during follow-up.", False, "v1_neg_dropout_trap"),
        ("The analysis excluded patients with incomplete data.", False, "v1_neg_analysis_excluded"),
        ("We excluded variables from regression modeling.", False, "v1_neg_variable_excluded"),
        ("The trial excluded the possibility of bias by blinding.", False, "v1_neg_abstract_exclusion"),
        ("Subjects were included in the final safety cohort.", False, "v1_neg_inclusion_mislead"),
    ]
)
def test_find_exclusion_rule_v1_robust(text, should_match, test_id):
    matches = find_exclusion_rule_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ─────────────────────────────
# Robust Tests for v2 (Cue + Gating Token)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive: Cue plus token (if/only/:)
        ("Patients were excluded if they had liver cirrhosis.", True, "v2_pos_excluded_if"),
        ("Subjects not eligible: history of seizure.", True, "v2_pos_colon_list"),
        ("Must not have prior chemotherapy if enrolled.", True, "v2_pos_must_not_have_if"),
        ("Patients were excluded only if they failed liver panel tests.", True, "v2_pos_excluded_only"),
        ("Exclusion criteria: allergy to contrast agents.", True, "v2_pos_colon_exclusion"),

        # Negative: No gating token near cue
        ("Subjects were excluded due to clinician discretion.", False, "v2_neg_no_gate"),
        ("Patients excluded from the interim safety analysis.", False, "v2_neg_analysis_trap"),
        ("Exclusion was considered unlikely by the team.", False, "v2_neg_no_true_cue"),
        ("Subjects not eligible because of subjective reasons.", False, "v2_neg_because_not_token"),
        ("Must not have anemia per protocol.", False, "v2_neg_per_protocol_no_gate"),
    ]
)
def test_find_exclusion_rule_v2_robust(text, should_match, test_id):
    matches = find_exclusion_rule_v2(text, window=5)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"
    
# ─────────────────────────────
# Lighter Checks for v3 (Heading-based block)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive: Matches inside header block
        ("Exclusion criteria:\nPatients must not have HIV.\n\n", True, "v3_pos_block_match"),
        ("exclusions:\nHistory of cardiovascular disease.\n\n", True, "v3_pos_lower_heading"),

        # Negative: Cue outside exclusion block
        ("Exclusion criteria:\n(None specified)\n\nMust not have diabetes.", False, "v3_neg_outside_block"),
        ("PRIMARY EXCLUSION CRITERIA:\nPatients excluded for poor adherence.", False, "v3_neg_unrecognized_heading"),
    ]
)
def test_find_exclusion_rule_v3_light(text, should_match, test_id):
    matches = find_exclusion_rule_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ─────────────────────────────
# Lighter Checks for v4 (v2 + conditional verb)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive: Must not have + gate
        ("Participants must not have diabetes if enrolled in phase II.", True, "v4_pos_must_not_have_if"),

        # Negative: v2 passes but no conditional verb
        ("Subjects were excluded if they were under 18.", False, "v4_neg_no_conditional_verb"),
        ("Not eligible due to uncontrolled hypertension.", False, "v4_neg_no_gate_and_conditional"),
    ]
)
def test_find_exclusion_rule_v4_light(text, should_match, test_id):
    matches = find_exclusion_rule_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ─────────────────────────────
# Lighter Checks for v5 (Tight templates)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive: Exact tight templates
        ("Exclusion criteria: uncontrolled diabetes or recent MI.", True, "v5_pos_colon_template"),
        ("Patients were excluded if they had prior stroke.", True, "v5_pos_were_excluded_if"),

        # Negative: Template doesn't match tightly
        ("Patient was excluded if diagnosed with epilepsy.", False, "v5_neg_singular_was_excluded"),
        ("Subjects must not have HIV to be eligible.", False, "v5_neg_not_a_template"),
    ]
)
def test_find_exclusion_rule_v5_light(text, should_match, test_id):
    matches = find_exclusion_rule_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
