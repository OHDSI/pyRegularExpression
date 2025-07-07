# tests/test_allocation_concealment_finder.py
"""
Complete test suite for allocation_concealment_finder.py.

Includes:
- Robust tests for v1 and v2 (basic concealment cues and randomisation + cue)
- Functional checks for v3, v4, and v5 (block-based, descriptor-enhanced, and tight templates)
- All examples modeled on PubMed/OHDSI-style trial methodology descriptions
"""

import pytest
from pyregularexpression.allocation_concealment_finder import (
    find_allocation_concealment_v1,
    find_allocation_concealment_v2,
    find_allocation_concealment_v3,
    find_allocation_concealment_v4,
    find_allocation_concealment_v5,
)

# ─────────────────────────────
# Robust Tests for v1 – High Recall: any concealment cue
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples (PubMed/CONSORT-style)
        ("Assignments were placed in opaque sealed envelopes.", True, "v1_pos_opaque_envelopes"),
        ("Allocation concealment was achieved via central randomization.", True, "v1_pos_central_randomization"),
        ("A web-based randomization system ensured allocation concealment.", True, "v1_pos_web_based"),
        ("Pharmacy-controlled allocation was implemented to ensure concealment.", True, "v1_pos_pharmacy_controlled"),

        # Trap examples (common misreads)
        ("Concealed allocation was not possible in this trial.", False, "v1_trap_not_possible"),
        ("Blinded assessors evaluated outcomes independently.", False, "v1_trap_blinded_assessors"),
    ]
)
def test_find_allocation_concealment_v1(text, should_match, test_id):
    matches = find_allocation_concealment_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ─────────────────────────────
# Robust Tests for v2 – Cue + randomisation keyword within ±4 tokens
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Opaque sealed envelopes were used for the randomization sequence.", True, "v2_pos_envelopes_sequence"),
        ("Central allocation concealed the randomised treatment assignment.", True, "v2_pos_central_allocation"),
        ("Telephone randomization ensured allocation concealment.", True, "v2_pos_telephone_randomization"),

        # Negative examples
        ("Opaque envelopes were distributed, but not related to randomization.", False, "v2_neg_no_rand_keyword"),
        ("Allocation was described but concealment was not mentioned.", False, "v2_neg_allocation_without_concealment"),
        ("The randomization method was described, but no concealment details.", False, "v2_neg_randomization_without_cue"),
    ]
)
def test_find_allocation_concealment_v2(text, should_match, test_id):
    matches = find_allocation_concealment_v2(text)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ─────────────────────────────
# Lighter Tests for v3 – Inside Allocation Concealment/Randomisation heading blocks
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Allocation Concealment:\nOpaque sealed envelopes were used.", True, "v3_pos_heading_concealment"),
        ("Randomisation:\nCentral randomization ensured concealment.", True, "v3_pos_heading_randomisation"),

        # Negative examples
        ("Methods:\nOpaque envelopes were described.", False, "v3_neg_wrong_heading"),
        ("Baseline:\nCentral allocation was mentioned.", False, "v3_neg_not_in_concealment_heading"),
    ]
)
def test_find_allocation_concealment_v3(text, should_match, test_id):
    matches = find_allocation_concealment_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ─────────────────────────────
# Lighter Tests for v4 – Cue + randomisation keyword + explicit descriptor
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Sequentially numbered opaque envelopes were used for randomization.", True, "v4_pos_seq_num_envelopes"),
        ("Centralized randomisation via a pharmacy-controlled system concealed allocation.", True, "v4_pos_pharmacy_central"),
        ("A web-based randomization service ensured allocation concealment.", True, "v4_pos_web_based"),

        # Negative examples
        ("Opaque envelopes mentioned but no sequence or randomization cue.", False, "v4_neg_no_rand"),
        ("Randomisation described but descriptor missing.", False, "v4_neg_no_descriptor"),
    ]
)
def test_find_allocation_concealment_v4(text, should_match, test_id):
    matches = find_allocation_concealment_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ─────────────────────────────
# Lighter Tests for v5 – Tight template matches
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Assignments in sequentially numbered opaque envelopes ensured allocation concealment.", True, "v5_pos_tight_template"),
        ("Assignments in sequentially numbered opaque envelopes achieved allocation concealment.", True, "v5_pos_achieved_template"),

        # Negative examples
        ("Opaque envelopes were used but no mention of concealment.", False, "v5_neg_no_concealment"),
        ("Assignments were placed in envelopes but not sequentially numbered.", False, "v5_neg_not_sequential"),
        ("Concealment described but not in tight template form.", False, "v5_neg_broad_concealment"),
    ]
)
def test_find_allocation_concealment_v5(text, should_match, test_id):
    matches = find_allocation_concealment_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
