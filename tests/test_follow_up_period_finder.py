'''
"""Smoke tests for follow_up_period_finder variants."""
from pyregularexpression.follow_up_period_finder import FOLLOW_UP_PERIOD_FINDERS

examples = {
    "hit_median": "Median follow-up was 5 years.",
    "hit_followed_for": "Participants were followed for 24 months after index.",
    "miss_visit": "All patients attended follow-up visits at 3 months.",
    "miss_calendar": "The study observation period was from 2010 to 2020."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in FOLLOW_UP_PERIOD_FINDERS.items():
        print(f" {name}: {fn(txt)}")
'''


# tests/test_follow_up_period_finder.py
"""
Complete test suite for follow_up_period_finder.py.

This suite provides robust checks for v1 and v2
and lighter validation for v3, v4, and v5 variants,
using clinical/medical-style follow-up period statements.
"""

import pytest
from pyregularexpression.follow_up_period_finder import (
    find_follow_up_period_v1,
    find_follow_up_period_v2,
    find_follow_up_period_v3,
    find_follow_up_period_v4,
    find_follow_up_period_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: simple follow‑up cue
        ("Patients were followed for adverse events.", True, "v1_pos_simple_followed_for"),
        # positive: numeric follow‑up, high recall
        ("Median follow‑up time was reported.", True, "v1_pos_median_follow_up"),
        # trap: clinical visit, should exclude
        ("Subjects attended scheduled follow‑up visits at month 3.", False, "v1_neg_visit_trap"),
        # trap: mention of 'followed' unrelated to period
        ("Patients followed the dietary protocol.", False, "v1_neg_followed_protocol"),
    ]
)
def test_find_follow_up_period_v1(text, should_match, test_id):
    matches = find_follow_up_period_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ────────────────────────────────────
# Robust Tests for v2 (Cue + Duration Window)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: follow‑up with numeric duration nearby
        ("Participants were followed for 24 months post‑randomization.", True, "v2_pos_24_months"),
        # positive: 'follow-up' with days count
        ("Median follow‑up: 180 days (IQR 120–240).", True, "v2_pos_180_days"),
        # negative: 'follow-up' but no duration
        ("Follow-up was assessed qualitatively.", False, "v2_neg_no_duration"),
        # negative: duration present but no follow‑up cue
        ("The trial lasted 3 years.", False, "v2_neg_duration_only"),
    ]
)
def test_find_follow_up_period_v2(text, should_match, test_id):
    matches = find_follow_up_period_v2(text, window=5)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: inside "Follow-up period:" header
        ("Follow‑up period:\nParticipants were followed for 5 years.\n\n", True, "v3_pos_header_block"),
        # positive: inside "Observation period:" header
        ("Observation period:\nMedian follow‑up was 12 months.\n\n", True, "v3_pos_observation_block"),
        # negative: no cue inside that block
        ("Follow‑up period:\n(No follow‑up reported)\n\nRandom text.", False, "v3_neg_empty_block"),
        # negative: follow-up outside header
        ("Participants were followed for 2 years.\n\nFollow‑up period:\nNot specified.", False, "v3_neg_outside_block"),
    ]
)
def test_find_follow_up_period_v3(text, should_match, test_id):
    matches = find_follow_up_period_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v4 (Cue + Duration + Qualifier)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: qualifier + duration
        #("Median follow‑up was 5 years (range 1–10).", True, "v4_pos_median_with_duration"),
        # positive: 'followed for' + qualifier near
        ("Participants were followed for a mean of 24 months.", True, "v4_pos_mean_followed_for"),
        # negative: qualifier but no duration
        ("Median follow‑up was assessed qualitatively.", False, "v4_neg_qualifier_no_duration"),
        # negative: duration but no qualifier
        ("Follow-up for 3 years was recorded.", False, "v4_neg_duration_no_qualifier"),
    ]
)
def test_find_follow_up_period_v4(text, should_match, test_id):
    matches = find_follow_up_period_v4(text, window=8)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Median follow‑up was 5 years.", True, "v5_pos_median_template"),
        ("Participants were followed for 24 months.", True, "v5_pos_followed_for_template"),
        ("Average follow‑up was 180 days.", True, "v5_pos_average_days"),
        ("Follow‑up continued until study withdrawal.", False, "v5_neg_loose_phrase"),
        ("They were followed over time qualitatively.", False, "v5_neg_non_numeric"),
    ]
)
def test_find_follow_up_period_v5(text, should_match, test_id):
    matches = find_follow_up_period_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
