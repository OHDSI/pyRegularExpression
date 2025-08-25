# tests/test_objective_hypothesis_finder.py
"""
Complete test suite for objective_hypothesis_finder.py.

This suite provides robust checks for v1 and v2
and lighter validation for v3, v4, and v5 variants,
using clinical/medical-style study objective/hypothesis statements.
"""

import pytest
from pyregularexpression.objective_hypothesis_finder import (
    find_objective_hypothesis_v1,
    find_objective_hypothesis_v2,
    find_objective_hypothesis_v3,
    find_objective_hypothesis_v4,
    find_objective_hypothesis_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: aim of this study
        ("The aim of this study was to assess efficacy.", True, "v1_pos_aim_of_study"),
        # positive: we aimed to
        ("We aimed to determine the effect of X on Y.", True, "v1_pos_we_aimed_to"),
        # positive: hypothesis phrase
        ("We hypothesize that exposure increases risk.", True, "v1_pos_we_hypothesize"),
        # trap: generic objective measurement
        ("Objective measurement was performed.", False, "v1_neg_trap_objective_measurement"),
    ]
)
def test_find_objective_hypothesis_v1(text, should_match, test_id):
    matches = find_objective_hypothesis_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ────────────────────────────────────
# Robust Tests for v2 (Cue + Verb OR Hypothesis Phrase)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: cue + verb within window
        ("The objective of this study was to evaluate outcomes.", True, "v2_pos_objective_with_verb"),
        # positive: hypothesis phrase
        ("We hypothesized that treatment reduces symptoms.", True, "v2_pos_we_hypothesized"),
        # negative: cue without verb
        ("The objective of this protocol is unclear.", False, "v2_neg_no_verb"),
        # negative: generic aim
        ("Our aim is to measure blood pressure.", False, "v2_neg_generic_aim"),
    ]
)
def test_find_objective_hypothesis_v2(text, should_match, test_id):
    matches = find_objective_hypothesis_v2(text, window=3)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: inside Objectives heading
        ("Objectives:\nThe aim of this study was to evaluate efficacy.\n", True, "v3_pos_objectives_block"),
        # positive: inside Aims heading
        ("Aims:\nWe hypothesize that intervention reduces risk.\n", True, "v3_pos_aims_block"),
        # negative: cue outside heading
        ("We aimed to assess X.\n\nObjectives:\nNot reported.", False, "v3_neg_outside_block"),
        # negative: empty heading
        ("Objectives:\n(No aim reported)\n", False, "v3_neg_empty_block"),
    ]
)
def test_find_objective_hypothesis_v3(text, should_match, test_id):
    matches = find_objective_hypothesis_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v4 (Cue + Verb + Study Reference)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: cue + verb + study token
        ("The objective of this study was to assess outcomes.", True, "v4_pos_objective_study_token"),
        ("We hypothesized that this study would show benefit.", True, "v4_pos_hypothesis_study_token"),
        # negative: cue + verb but no study token
        ("The aim was to measure blood pressure.", False, "v4_neg_no_study_token"),
        # negative: study token present but no cue
        ("This study involved 50 participants.", False, "v4_neg_no_cue"),
    ]
)
def test_find_objective_hypothesis_v4(text, should_match, test_id):
    matches = find_objective_hypothesis_v4(text, window=4)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The objective of this study was to assess treatment efficacy.", True, "v5_pos_tight_template_objective"),
        ("We hypothesized that exposure increases risk of disease.", True, "v5_pos_tight_template_hypothesis"),
        # negative: cue + study token but outside template
        ("We aimed to study participants in this study.", False, "v5_neg_partial_template"),
        ("Objective measurement was recorded in the study.", False, "v5_neg_trap_template"),
    ]
)
def test_find_objective_hypothesis_v5(text, should_match, test_id):
    matches = find_objective_hypothesis_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
