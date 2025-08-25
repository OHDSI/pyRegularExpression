# tests/test_random_sequence_generation_finder.py
"""
Complete test suite for random_sequence_generation_finder.py.
Covers five variants (v1–v5):
    • v1 – high recall (any generation cue)
    • v2 – cue + randomisation keyword window
    • v3 – heading block
    • v4 – cue + duration + method modifier
    • v5 – tight template
"""
import pytest
from pyregularexpression.random_sequence_generation_finder import (
    find_random_sequence_generation_v1,
    find_random_sequence_generation_v2,
    find_random_sequence_generation_v3,
    find_random_sequence_generation_v4,
    find_random_sequence_generation_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Allocation sequence was computer-generated.", True, "v1_pos_computer_generated"),
        ("Random number table was used for sequence generation.", True, "v1_pos_random_number_table"),
        ("Patients were randomly assigned to groups (random sampling).", False, "v1_neg_random_sampling_trap"),
        ("Random effects model was applied.", False, "v1_neg_random_effects_trap"),
    ],
)
def test_find_random_sequence_generation_v1(text, should_match, test_id):
    matches = find_random_sequence_generation_v1(text)
    assert bool(matches) == should_match, f"v1 failed for {test_id}"


# ────────────────────────────────────
# Robust Tests for v2 (Cue + Rand Keyword)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The allocation sequence was computer-generated.", True, "v2_pos_seq_computer_generated"),
        ("Block randomization was computerised for allocation.", True, "v2_pos_block_allocation"),
        ("Computer-generated list of numbers was prepared.", False, "v2_neg_no_rand_keyword"),
        ("The allocation procedure was described, using random effects.", False, "v2_neg_trap_random_effects"),
    ],
)
def test_find_random_sequence_generation_v2(text, should_match, test_id):
    matches = find_random_sequence_generation_v2(text, window=4)
    assert bool(matches) == should_match, f"v2 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Randomisation:\nThe sequence was generated using a random number table.", True, "v3_pos_heading_block"),
        ("Sequence Generation:\nComputer-generated randomisation list prepared.", True, "v3_pos_sequence_generation"),
        ("Randomisation:\n(No method described)\n", False, "v3_neg_empty_block"),
        ("The allocation was computer-generated.\nRandomisation: Not described.", False, "v3_neg_outside_block"),
    ],
)
def test_find_random_sequence_generation_v3(text, should_match, test_id):
    matches = find_random_sequence_generation_v3(text)
    assert bool(matches) == should_match, f"v3 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v4 (Cue + Method Modifier)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Allocation sequence was computer-generated using block randomization.", True, "v4_pos_block_modifier"),
        ("Sequence was computer-generated (no modifier present).", False, "v4_neg_no_modifier"),
        ("Block method was described but no random sequence.", False, "v4_neg_block_only"),
    ],
)
def test_find_random_sequence_generation_v4(text, should_match, test_id):
    matches = find_random_sequence_generation_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Allocation sequence computer-generated using block randomization (block size = 4).", True, "v5_pos_tight_template"),
        ("The allocation sequence was computer-generated using block randomisation.", True, "v5_pos_variation"),
        ("Computer-generated allocation list was used.", False, "v5_neg_loose_phrase"),
        ("Block randomization without explicit allocation sequence.", False, "v5_neg_incomplete"),
    ],
)
def test_find_random_sequence_generation_v5(text, should_match, test_id):
    matches = find_random_sequence_generation_v5(text)
    assert bool(matches) == should_match, f"v5 failed for {test_id}"
