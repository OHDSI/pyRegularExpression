# tests/test_background_rationale_finder.py
"""
Complete test suite for background_rationale_finder.py.

Includes:
- Robust tests for v1 and v2 (basic gap/rationale cues and context-aware co-occurrence with "study")
- Functional checks for v3, v4, and v5 (block-based, unmet-need phrase filters, and tight template matches)
- All examples inspired by PubMed/OHDSI-style study introductions and rationales
"""

import pytest
from pyregularexpression.background_rationale_finder import (
    find_background_rationale_v1,
    find_background_rationale_v2,
    find_background_rationale_v3,
    find_background_rationale_v4,
    find_background_rationale_v5,
)

# ─────────────────────────────
# Robust Tests for v1 – High Recall: any gap/rationale cue
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples (PubMed/OHDSI-style)
        ("Prior studies have shown that adherence impacts outcomes.", True, "v1_pos_prior_studies"),
        ("However, little is known about long-term effects.", True, "v1_pos_little_known"),
        ("There is an important gap in understanding this population.", True, "v1_pos_important_gap"),
        ("This study aims to address these knowledge gaps.", True, "v1_pos_this_study"),

        # Trap / negative examples (from ethics approval old test code)
        ("Protocol approved by XYZ IRB #2021-45; informed consent obtained.", False, "v1_neg_irb"),
        ("The institutional review board waived the need for informed consent.", False, "v1_neg_waiver"),
        ("Study followed ethical principles of the Declaration of Helsinki.", False, "v1_neg_guidelines"),
        ("Ethically conducted research procedures were applied.", False, "v1_neg_generic"),
    ]
)
def test_find_background_rationale_v1(text, should_match, test_id):
    matches = find_background_rationale_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ─────────────────────────────
# Tests for v2 – Sentence containing ≥2 gap phrases or gap + 'study' nearby
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Prior studies have shown unknown effects of this therapy; this study investigates.", True, "v2_pos_multiple_gaps"),
        ("Little is known about these populations, and the study aims to examine it.", True, "v2_pos_gap_plus_study"),
        ("Important gap exists, and evidence is limited.", True, "v2_pos_two_gap_phrases"),
        ("This research explores known mechanisms.", False, "v2_neg_single_known_phrase"),
    ]
)
def test_find_background_rationale_v2(text, should_match, test_id):
    matches = find_background_rationale_v2(text)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ─────────────────────────────
# Tests for v3 – Only inside Introduction / Background heading block
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Introduction:\nPrior studies have shown limited evidence.", True, "v3_pos_introduction_heading"),
        ("Background:\nHowever, little is known about this topic.", True, "v3_pos_background_heading"),
        ("Results:\nPrior studies have shown limited evidence.", False, "v3_neg_wrong_heading"),
        ("Methods:\nLittle is known about this topic.", False, "v3_neg_not_in_heading"),
    ]
)
def test_find_background_rationale_v3(text, should_match, test_id):
    matches = find_background_rationale_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ─────────────────────────────
# Tests for v4 – v2 + unmet-need phrases
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Little is known about adherence, and this study investigates.", True, "v4_pos_unmet_need"),
        ("Not well understood mechanisms were explored in this study.", True, "v4_pos_not_well_understood"),
        ("Prior studies have shown effects.", False, "v4_neg_known_only"),
    ]
)
def test_find_background_rationale_v4(text, should_match, test_id):
    matches = find_background_rationale_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ─────────────────────────────
# Tests for v5 – Tight template matches
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("However, little is known about adherence; therefore this study aims to investigate.", True, "v5_pos_tight_template"),
        ("Yet unknown mechanisms exist; this study aims to examine them.", True, "v5_pos_tight_template_alt"),
        ("Little is known about adherence, and we explore it.", False, "v5_neg_missing_contrast_connector"),
        ("Prior studies have shown this effect.", False, "v5_neg_no_template"),
    ]
)
def test_find_background_rationale_v5(text, should_match, test_id):
    matches = find_background_rationale_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"

