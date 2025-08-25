# tests/test_participant_flow_finder.py
"""
Complete test suite for participant_flow_finder.py.

This suite provides robust checks for v1 and v2
and lighter validation for v3, v4, and v5 variants,
using CONSORT-style participant flow statements common in PubMed/OHDSI reports.
"""

import pytest
from pyregularexpression.participant_flow_finder import (
    find_participant_flow_v1,
    find_participant_flow_v2,
    find_participant_flow_v3,
    find_participant_flow_v4,
    find_participant_flow_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: randomized + number after cue (PubMed-style)
        ("We randomized 120 participants to study arms.", True, "v1_pos_randomized_120"),
        # positive: allocated + number within 15 chars
        ("Participants were allocated 80 to the intervention group.", True, "v1_pos_allocated_80"),
        # positive: completed + n= style still has digits after cue
        ("Follow-up was completed in (n = 180) participants.", True, "v1_pos_completed_n_equals"),
        # negative: trap phrase "a total of <num>" near cue should be excluded
        ("We randomized a total of 220 participants across centers.", False, "v1_neg_total_of_trap"),
        # negative: flow cue present but no following number within window
        ("Participants were screened but numbers were not reported.", False, "v1_neg_no_number"),
    ]
)
def test_find_participant_flow_v1(text, should_match, test_id):
    matches = find_participant_flow_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ────────────────────────────────────
# Robust Tests for v2 (Cue + Number + Group/Stage Window)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: randomized + number + group within ±4 tokens
        ("Randomized 120 participants to treatment arm.", True, "v2_pos_randomized_group"),
        # positive: allocated + number + intervention keyword near cue
        ("Allocated 80 participants to the intervention group.", True, "v2_pos_allocated_intervention"),
        # positive: screened + number + stage keyword (screening/follow-up/analysis)
        ("Screened 300 individuals at baseline prior to randomization.", True, "v2_pos_screened_stage"),
        # negative: randomized + group but missing number token
        ("Randomized participants to control arm.", False, "v2_neg_no_number"),
        # negative: randomized + number but no group/stage near cue
        ("Randomized 150 participants across sites.", False, "v2_neg_no_group_or_stage"),
    ]
)
def test_find_participant_flow_v2(text, should_match, test_id):
    matches = find_participant_flow_v2(text, window=4)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: inside "Participant Flow" header block (CONSORT-style)
        ("Participant Flow:\nRandomized 300; allocated 150 treatment and 150 control.", True, "v3_pos_participant_flow_header"),
        # positive: inside "CONSORT Flow" header
        ("CONSORT Flow\nExcluded 25; withdrew 10; completed in 190.", True, "v3_pos_consort_header"),
        # negative: cue outside the header block
        ("Randomized 200 participants.\n\nParticipant Flow:\n(figure not shown)", False, "v3_neg_outside_block"),
        # negative: header present but no cue inside
        ("Figure 1:\n(No participant flow reported)\n", False, "v3_neg_empty_block"),
    ]
)
def test_find_participant_flow_v3(text, should_match, test_id):
    matches = find_participant_flow_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v4 (Cue + Group/Stage + ≥2 Numbers)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: split counts (OHDSI/CONSORT style)
        ("Randomized 200 participants: 100 treatment and 100 placebo.", True, "v4_pos_split_counts"),
        # positive: allocated with two numeric group counts
        ("Allocated 120 participants: 60 intervention and 60 control.", True, "v4_pos_allocated_two_counts"),
        # negative: only one number near cue
        ("Randomized 120 participants to treatment arm.", False, "v4_neg_single_number"),
        # negative: group labels present but only one numeric token
        ("Allocated participants to intervention (n=80) and control groups.", False, "v4_neg_one_numeric_token"),
    ]
)
def test_find_participant_flow_v4(text, should_match, test_id):
    matches = find_participant_flow_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: strict CONSORT-like template
        ("200 randomized (100 treatment, 100 placebo); 180 completed follow-up.", True, "v5_pos_tight_template"),
        # positive: variant with intervention/control labels
        ("180 randomized (90 control, 90 intervention); 170 completed.", True, "v5_pos_tight_template_variant"),
        # negative: lacks parenthesized split
        ("200 randomized to two arms; 180 completed follow-up.", False, "v5_neg_missing_parenthesis_split"),
        # negative: descriptive narrative not matching template
        ("Participants were randomized and most completed follow-up.", False, "v5_neg_loose_narrative"),
    ]
)
def test_find_participant_flow_v5(text, should_match, test_id):
    matches = find_participant_flow_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
