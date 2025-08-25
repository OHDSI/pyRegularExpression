# tests/test_numbers_analyzed_finder.py
"""
Complete test suite for numbers_analyzed_finder.py.

This suite provides robust checks for v1 and v2
and lighter validation for v3, v4, and v5 variants,
using clinical/medical-style "numbers analyzed" statements.
"""

import pytest
from pyregularexpression.numbers_analyzed_finder import (
    find_numbers_analyzed_v1,
    find_numbers_analyzed_v2,
    find_numbers_analyzed_v3,
    find_numbers_analyzed_v4,
    find_numbers_analyzed_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: simple "participants analysed" cue
        ("Participants were analysed for efficacy.", True, "v1_pos_simple_analyzed"),
        # positive: n=123 cue
        ("n=50 participants were included in the analysis.", True, "v1_pos_n_equals"),
        # trap: enrolled, not analyzed
        ("120 participants were enrolled in the study.", False, "v1_neg_enrolled_trap"),
        # trap: random text with numbers
        ("The mean age was 45.", False, "v1_neg_number_only"),
    ]
)
def test_find_numbers_analyzed_v1(text, should_match, test_id):
    matches = find_numbers_analyzed_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ────────────────────────────────────
# Robust Tests for v2 (Cue + Group Keyword)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: cue + group + number
        ("50 treatment participants analysed.", True, "v2_pos_treatment_group"),
        ("n=42 control participants included in analysis.", True, "v2_pos_control_group"),
        # negative: cue + number but no group
        ("30 participants analysed.", False, "v2_neg_no_group"),
        # negative: group + number but no cue
        ("50 intervention subjects were measured.", False, "v2_neg_no_cue"),
    ]
)
def test_find_numbers_analyzed_v2(text, should_match, test_id):
    matches = find_numbers_analyzed_v2(text, window=4)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: inside heading block
        ("Numbers Analysed:\n50 participants were analysed in the trial.\n", True, "v3_pos_heading_block"),
        ("Analysis Population:\nn=120 included in analysis.\n", True, "v3_pos_analysis_population"),
        # negative: cue outside block
        ("50 participants analysed.\n\nNumbers Analysed:\nNot reported.", False, "v3_neg_outside_block"),
        # negative: empty block
        ("Numbers Analysed:\n(No participants reported)\n", False, "v3_neg_empty_block"),
    ]
)
def test_find_numbers_analyzed_v3(text, should_match, test_id):
    matches = find_numbers_analyzed_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v4 (Cue + Group + Population Label)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: cue + group + analysis set
        ("50 intervention participants analysed (ITT).", True, "v4_pos_itt_intervention"),
        ("n=40 control participants included in analysis per-protocol.", True, "v4_pos_pp_control"),
        # negative: cue + group but no analysis set
        ("30 treatment participants analysed.", False, "v4_neg_no_pop_label"),
        # negative: analysis set mentioned but no cue
        ("ITT population had 45 participants enrolled.", False, "v4_neg_no_cue"),
    ]
)
def test_find_numbers_analyzed_v4(text, should_match, test_id):
    matches = find_numbers_analyzed_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("98 intervention and 102 control participants analysed (ITT).", True, "v5_pos_tight_template"),
        ("50 treatment and 50 placebo participants analysed (intention-to-treat).", True, "v5_pos_alt_template"),
        # negative: numbers and groups but not full template
        ("30 intervention participants analysed.", False, "v5_neg_partial_template"),
        ("n=45 control participants included in analysis.", False, "v5_neg_partial_template2"),
    ]
)
def test_find_numbers_analyzed_v5(text, should_match, test_id):
    matches = find_numbers_analyzed_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
