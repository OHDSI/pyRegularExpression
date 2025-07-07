# tests/test_randomization_type_restriction_finder.py
"""
Complete test suite for randomization_type_restriction_finder.py.
Covers five variants (v1–v5):
    • v1 – high recall (restriction cue)
    • v2 – restriction cue + randomisation keyword within window
    • v3 – inside Allocation/Randomisation heading block
    • v4 – v2 + explicit ratio or ≥2 modifiers
    • v5 – tight template
"""
import pytest
from pyregularexpression.randomization_type_restriction_finder import (
    find_randomization_type_restriction_v1,
    find_randomization_type_restriction_v2,
    find_randomization_type_restriction_v3,
    find_randomization_type_restriction_v4,
    find_randomization_type_restriction_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Patients were assigned using block randomization.", True, "v1_pos_block_randomization"),
        ("Randomization used permuted blocks of size six.", True, "v1_pos_permuted_blocks"),
        ("The trial applied minimization methods.", True, "v1_pos_minimization"),
        ("Participants were randomly assigned (random sampling).", False, "v1_neg_random_sampling_trap"),
    ],
)
def test_find_randomization_type_restriction_v1(text, should_match, test_id):
    matches = find_randomization_type_restriction_v1(text)
    assert bool(matches) == should_match, f"v1 failed for {test_id}"


# ────────────────────────────────────
# Robust Tests for v2 (Cue + Rand Keyword)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Participants were randomized 1:1 using block randomization.", True, "v2_pos_ratio_block"),
        ("The allocation sequence used permuted blocks.", True, "v2_pos_allocation_permuted"),
        ("Permuted blocks of size four were applied.", False, "v2_neg_no_rand_keyword"),
        ("Random sampling was used.", False, "v2_neg_trap_sampling"),
    ],
)
def test_find_randomization_type_restriction_v2(text, should_match, test_id):
    matches = find_randomization_type_restriction_v2(text, window=4)
    assert bool(matches) == should_match, f"v2 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Randomisation:\nBlock randomization was used with ratio 2:1.", True, "v3_pos_heading_block"),
        ("Allocation:\nMinimization was applied.", True, "v3_pos_allocation_block"),
        ("Randomisation:\n(No details provided)", False, "v3_neg_empty_block"),
        ("Block randomization mentioned.\nAllocation: Not specified.", False, "v3_neg_outside_block"),
    ],
)
def test_find_randomization_type_restriction_v3(text, should_match, test_id):
    matches = find_randomization_type_restriction_v3(text)
    assert bool(matches) == should_match, f"v3 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v4 (Ratio/Multiple Modifiers)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Patients were randomized 2:1 using permuted blocks.", True, "v4_pos_ratio_present"),
        ("Stratified and block randomization were both applied.", True, "v4_pos_multiple_modifiers"),
        ("Block randomization was described without ratio.", False, "v4_neg_single_modifier"),
        ("Ratio 1:1 mentioned but no randomisation keyword.", False, "v4_neg_ratio_without_rand_keyword"),
    ],
)
def test_find_randomization_type_restriction_v4(text, should_match, test_id):
    matches = find_randomization_type_restriction_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Randomized 2:1 to drug vs placebo using permuted blocks of six, stratified by site.", True, "v5_pos_tight_template"),
        ("Randomized 3:1 using permuted blocks, stratified by gender.", True, "v5_pos_variant"),
        ("Randomized participants using stratified blocks (no ratio).", False, "v5_neg_no_ratio"),
        ("Permuted blocks mentioned loosely without stratification.", False, "v5_neg_incomplete"),
    ],
)
def test_find_randomization_type_restriction_v5(text, should_match, test_id):
    matches = find_randomization_type_restriction_v5(text)
    assert bool(matches) == should_match, f"v5 failed for {test_id}"
