# tests/test_exit_criterion_finder.py
"""
Complete test suite for exit_criterion_finder.py.

This suite provides robust, comprehensive checks for v1 and v2,
with lighter validation for v3, v4, and v5 variants.
"""

import pytest
from pyregularexpression.exit_criterion_finder import (
    find_exit_criterion_v1,
    find_exit_criterion_v2,
    find_exit_criterion_v3,
    find_exit_criterion_v4,
    find_exit_criterion_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall with trap filtering)
# ────────────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Patients were followed until death or retransplantation.", True, "v1_pos_pubmed_death_transplant"),
        ("All patients were followed until death, transplantation or December 31st, 2017.", True, "v1_pos_pubmed_date"),
        ("Patients were censored at study end.", True, "v1_pos_censored_at"),
        ("Participants were followed until June 2010.", True, "v1_pos_followed_until_month"),
        ("Follow-up ended after 24 months.", True, "v1_pos_followup_ended_time"),
        ("Censored on the date of last contact.", True, "v1_pos_censored_last_contact"),
        ("The study ended in 2018.", False, "v1_neg_study_ended_trap"),
        ("Five individuals were lost to follow-up.", False, "v1_neg_lost_followup_trap"),
        ("Patients withdrew consent before the second visit.", False, "v1_neg_withdrew_consent"),
        ("Study completion was determined administratively.", False, "v1_neg_admin_completion"),
    ]
)
def test_find_exit_criterion_v1_robust(text, should_match, test_id):
    matches = find_exit_criterion_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ────────────────────────────────────
# Robust Tests for v2 (Cue + Temporal Keyword Window)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Patients were followed until death or transplant.", True, "v2_pos_followed_until_event"),
        ("All patients were followed until death, transplantation or December 31st, 2017.", True, "v2_pos_until_date"),
        ("Censored at whichever occurred first: death or graft loss.", True, "v2_pos_whichever_keyword"),
        ("Exit at the earlier of transplant or death.", True, "v2_pos_earlier_of"),
        ("Participants were censored when the event occurred.", True, "v2_pos_censored_when"),
        ("Follow-up ended whichever occurred later: visit or drop-out.", True, "v2_pos_whichever_later"),
        ("Participants were censored from the registry data.", False, "v2_neg_no_temporal_keyword"),
        ("Follow-up ended after baseline visit.", False, "v2_neg_no_keyword"),
        ("Exit strategy was not clearly defined.", False, "v2_neg_exit_ambiguous"),
        ("Censoring data was manually reviewed.", False, "v2_neg_contextual_usage"),
    ]
)
def test_find_exit_criterion_v2_robust(text, should_match, test_id):
    matches = find_exit_criterion_v2(text, window=5)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Checks for v3 (Heading-based block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Exit criteria:\nFollowed until death or transplant.\n\n", True, "v3_pos_heading_block"),
        ("Censoring:\nCensored at whichever occurred first.\n\n", True, "v3_pos_censoring_block"),
        ("Exit criteria:\n(None specified)\n\nStudy ended in 2018.", False, "v3_neg_no_match_in_block"),
        ("Methods:\nPatients were followed until transplant.", False, "v3_neg_wrong_heading"),
    ]
)
def test_find_exit_criterion_v3_light(text, should_match, test_id):
    matches = find_exit_criterion_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Checks for v4 (v2 + Event/Time Token)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Patients were followed until transplant or 31 Dec 2020.", True, "v4_pos_until_date_and_event"),
        ("Censored at death or end of study", True, "v4_pos_censored_at_death"),
        ("Participants were followed until outcome was reached.", False, "v4_neg_generic_until"),
        ("Exit when appropriate, whichever came first.", False, "v4_neg_no_event_token"),
        ("Recipients were censored at 5 years of follow-up, time of re-transplant, or administratively at end-of-study.", True, "v4_pos_censored_at_retransplant_or_end"),
        ("Kidney transplant recipients were censored at the time of graft loss, death, or the end of the study period.", True, "v4_pos_censored_at_multiple_events"),
        ("The primary endpoint was death-censored graft survival.", False, "v4_neg_death_censored_descriptive"),
        ("Follow-up was censored from registry data after baseline.", False, "v4_neg_censored_after_baseline"),
    ]
)
def test_find_exit_criterion_v4_light(text, should_match, test_id):
    matches = find_exit_criterion_v4(text, window=8)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Checks for v5 (Tight Template Match)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Patients were followed until transplant or death.", True, "v5_pos_followed_until"),
        ("Censored at death.", True, "v5_pos_censored_at"),
        ("Exit when patient dies.", True, "v5_pos_exit_when"),
        ("Follow-up concluded when patients withdrew.", False, "v5_neg_loose_phrase"),
        ("They were no longer followed after the trial.", False, "v5_neg_not_template"),
    ]
)
def test_find_exit_criterion_v5_light(text, should_match, test_id):
    matches = find_exit_criterion_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"