# tests/test_trial_design_finder.py
"""
Smoke tests for trial_design_finder variants.

This suite checks the accuracy of trial/study design detection across
five tiers (v1–v5), from high-recall keyword matching to precise,
template-based pattern recognition. Each tier progressively filters
out contextual false positives.
"""

import pytest
from pyregularexpression.trial_design_finder import (
    find_trial_design_v1,
    find_trial_design_v2,
    find_trial_design_v3,
    find_trial_design_v4,
    find_trial_design_v5,
)

# ─────────────────────────────
# Tests for v1 – high recall + type term nearby
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("We conducted a randomized trial to assess outcomes.", True, "v1_pos_randomized_trial"),
        ("A case-control study was used for analysis.", True, "v1_pos_case_control_study"),
        ("Study design was discussed but not executed.", False, "v1_neg_design_context_only"),
        ("The design involved collaboration between teams.", False, "v1_neg_non_study_use"),
    ]
)
def test_find_trial_design_v1(text, should_match, test_id):
    matches = find_trial_design_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ─────────────────────────────
# Tests for v2 – design term + qualifier or two design terms nearby
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("This was a double-blind randomized trial.", True, "v2_pos_double_blind_rct"),
        ("A placebo-controlled phase II trial was conducted.", True, "v2_pos_phase_ii_placebo"),
        ("A retrospective design was considered.", False, "v2_neg_qualifier_only"),
        ("Study was conducted in multiple sites.", False, "v2_neg_no_design_term"),
    ]
)
def test_find_trial_design_v2(text, should_match, test_id):
    matches = find_trial_design_v2(text)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ─────────────────────────────
# Tests for v3 – within Study/Trial Design heading block
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Study Design:\nWe used a double-blind randomized trial structure.", True, "v3_pos_in_heading_block"),
        ("Trial Design:\nA cohort study was implemented.", True, "v3_pos_heading_cohort"),
        ("A randomized trial was used.\n\nStudy Design:\n(No method details provided)", False, "v3_neg_outside_heading_block"),
    ]
)
def test_find_trial_design_v3(text, should_match, test_id):
    matches = find_trial_design_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ─────────────────────────────
# Tests for v4 – v2 + type term near match
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("This was a prospective cohort study involving 5,000 participants.", True, "v4_pos_prospective_cohort"),
        ("We conducted a randomized, double-blind trial.", True, "v4_pos_rct"),
        ("The prospective method was used to design our recruitment flow.", False, "v4_neg_no_trial_type"),
    ]
)
def test_find_trial_design_v4(text, should_match, test_id):
    matches = find_trial_design_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ─────────────────────────────
# Tests for v5 – tight template match only
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("This was a double-blind, placebo-controlled randomized trial in three hospitals.", True, "v5_pos_tight_rct"),
        ("A prospective multicenter cohort study was conducted.", True, "v5_pos_cohort_template"),
        ("The study was randomized but not double-blind.", False, "v5_neg_incomplete_template"),
        ("A phase III trial was executed but not placebo-controlled.", False, "v5_neg_phase_only"),
    ]
)
def test_find_trial_design_v5(text, should_match, test_id):
    matches = find_trial_design_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
