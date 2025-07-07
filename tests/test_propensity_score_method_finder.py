# tests/test_propensity_score_method_finder.py
"""
Test suite for propensity_score_method_finder.py

Variants v1–v5:
    • v1 – cue only
    • v2 – cue + nearby analysis verb
    • v3 – cue only inside Propensity Score/Confounding Control heading block
    • v4 – v2 + nearby technique qualifier
    • v5 – tight template (logistic regression + IPTW / PS matching / IPW)
"""

import pytest
from pyregularexpression.propensity_score_method_finder import (
    find_propensity_score_method_v1,
    find_propensity_score_method_v2,
    find_propensity_score_method_v3,
    find_propensity_score_method_v4,
    find_propensity_score_method_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: plain propensity score mention
        ("We used propensity score matching to reduce confounding.", True, "v1_pos_ps_matching"),
        # positive: IPTW abbreviation
        ("Treatment effects were estimated using IPTW.", True, "v1_pos_iptw"),
        # positive: doubly robust
        ("We implemented a doubly robust estimator.", True, "v1_pos_doubly_robust"),
        # negative: trap phrase "propensity to" should not match
        ("He had a propensity to smoke.", False, "v1_neg_propensity_to"),
        # negative: no propensity-related method at all
        ("Logistic regression was performed for all outcomes.", False, "v1_neg_no_cue"),
    ]
)
def test_find_propensity_score_method_v1(text, should_match, test_id):
    matches = find_propensity_score_method_v1(text)
    assert bool(matches) == should_match, f"v1 failed for {test_id}"

# ────────────────────────────────────
# Robust Tests for v2 (Cue + Verb ±4)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: cue + verb close by
        ("We estimated propensity scores for all patients.", True, "v2_pos_estimated_ps"),
        # positive: verb before cue
        ("Applied IPTW weighting to balance covariates.", True, "v2_pos_applied_iptw"),
        # negative: cue present but no analysis verb nearby
        ("The study design relied on propensity score methods.", False, "v2_neg_no_verb"),
        # negative: verb present but far away (>4 tokens)
        ("Propensity score methodology, as widely discussed in the literature, was later considered.", False, "v2_neg_verb_too_far"),
    ]
)
def test_find_propensity_score_method_v2(text, should_match, test_id):
    matches = find_propensity_score_method_v2(text, window=4)
    assert bool(matches) == should_match, f"v2 failed for {test_id}"

# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: inside block starting with "Propensity Score"
        ("Propensity Score\nWe applied IPTW weighting.", True, "v3_pos_block_heading"),
        # positive: inside "Confounding Control" block
        ("Confounding Control:\nPropensity score matching was used.", True, "v3_pos_confounding_heading"),
        # negative: cue outside heading block
        ("We applied IPTW weighting.\n\nPropensity Score Methods:\n(not described)", False, "v3_neg_outside_block"),
        # negative: heading present but no cue inside block
        ("Propensity Score:\n(no methods applied)", False, "v3_neg_empty_block"),
    ]
)
def test_find_propensity_score_method_v3(text, should_match, test_id):
    matches = find_propensity_score_method_v3(text)
    assert bool(matches) == should_match, f"v3 failed for {test_id}"

# ────────────────────────────────────
# Lighter Tests for v4 (Cue + Verb + Technique)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: estimated + propensity score + matching keyword
        ("We estimated propensity scores and performed matching.", True, "v4_pos_ps_matching"),
        # positive: applied IPTW weighting (verb + cue + weighting)
        ("Applied IPTW weighting for treatment effect estimation.", True, "v4_pos_iptw_weighting"),
        # negative: cue + verb but no explicit technique
        ("We estimated propensity scores for all patients.", False, "v4_neg_no_technique"),
        # negative: technique word present but no verb
        ("Propensity score weighting approach was discussed.", False, "v4_neg_no_verb"),
    ]
)
def test_find_propensity_score_method_v4(text, should_match, test_id):
    matches = find_propensity_score_method_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for {test_id}"

# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: strict template – estimated via logistic regression + applied IPTW
        ("We estimated propensity scores via logistic regression and applied IPTW.", True, "v5_pos_logistic_iptw"),
        # positive: estimated via logistic regression + applied PS matching
        ("We estimated propensity scores via logistic regression and applied PS matching.", True, "v5_pos_logistic_matching"),
        # negative: missing logistic regression part
        ("We applied IPTW after estimating propensity scores.", False, "v5_neg_missing_logistic"),
        # negative: descriptive but not template-like
        ("Propensity scores were estimated and IPTW was used.", False, "v5_neg_loose_style"),
    ]
)
def test_find_propensity_score_method_v5(text, should_match, test_id):
    matches = find_propensity_score_method_v5(text)
    assert bool(matches) == should_match, f"v5 failed for {test_id}"
