# tests/test_trial_design_changes_finder.py
"""
Complete test suite for trial_design_changes_finder.py.
This suite provides robust checks for v1 and v2 and lighter validation for v3, v4, and v5 variants,
using clinical/medical-style trial design/protocol change statements.
"""
import pytest
from pyregularexpression.trial_design_changes_finder import (
    find_trial_design_changes_v1,
    find_trial_design_changes_v2,
    find_trial_design_changes_v3,
    find_trial_design_changes_v4,
    find_trial_design_changes_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: simple protocol amendment
        ("The protocol was amended to include additional endpoints.", True, "v1_pos_protocol_amended"),
        # positive: design change cue
        ("There were changes to the study design after initiation.", True, "v1_pos_changes_to_design"),
        # trap: pre-trial planned design change
        ("Design changes planned before enrollment.", False, "v1_neg_pretrial_planned"),
        # trap: unrelated use of 'amend'
        ("They amended their report draft.", False, "v1_neg_non_protocol_amend"),
    ],
)
def test_find_trial_design_changes_v1(text, should_match, test_id):
    matches = find_trial_design_changes_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"


# ────────────────────────────────────
# Robust Tests for v2 (Cue + Temporal Window)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: cue + temporal within window
        ("The protocol was amended during the trial to address safety.", True, "v2_pos_during_trial"),
        # positive: numeric temporal phrase
        ("Two months into the study, changes to the trial protocol were made.", True, "v2_pos_two_months"),
        # negative: cue but no temporal
        ("The protocol was amended to adjust inclusion criteria.", False, "v2_neg_no_temporal"),
        # negative: temporal present but no cue
        ("Three years into the trial, enrollment was halted.", False, "v2_neg_temporal_only"),
    ],
)
def test_find_trial_design_changes_v2(text, should_match, test_id):
    matches = find_trial_design_changes_v2(text, window=4)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"


# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: inside heading block
        ("Protocol amendments:\nThe protocol was amended after initiation.\n\n", True, "v3_pos_heading_block"),
        # positive: alternative heading wording
        ("Changes to design:\nModified the trial protocol to include interim analyses.\n\n", True, "v3_pos_changes_heading"),
        # negative: heading present but no cue
        ("Protocol amendments:\n(No amendments made)\n\n", False, "v3_neg_empty_block"),
        # negative: cue outside block
        ("The protocol was amended.\n\nProtocol amendments:\nNot specified.", False, "v3_neg_outside_block"),
    ],
)
def test_find_trial_design_changes_v3(text, should_match, test_id):
    matches = find_trial_design_changes_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"


# ────────────────────────────────────
# Lighter Tests for v4 (Cue + Temporal + Explicit Amendment Keyword)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: temporal + explicit amendment
        ("After the trial began, a protocol amendment was introduced for safety.", True, "v4_pos_temporal_with_amendment"),
        # positive: amended protocol phrase
        ("Mid-study, the amended protocol included new eligibility rules.", True, "v4_pos_amended_protocol"),
        # negative: cue + temporal but no explicit amendment keyword
        ("During the trial, changes to the study design were implemented.", False, "v4_neg_no_amend_keyword"),
        # negative: explicit amendment keyword but no temporal
        ("A protocol amendment was described in the design document.", False, "v4_neg_no_temporal"),
    ],
)
def test_find_trial_design_changes_v4(text, should_match, test_id):
    matches = find_trial_design_changes_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"


# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: strict template with temporal + reason
        ("Three months into the trial, the protocol was amended due to safety concerns.", True, "v5_pos_three_months_reason"),
        # positive: temporal with amendment
        ("6 weeks into the study, the protocol was amended to add biomarkers.", True, "v5_pos_six_weeks"),
        # negative: loose phrase without numeric temporal
        ("The protocol was amended during the study.", False, "v5_neg_loose_during"),
        # negative: non-temporal amendment
        ("The protocol was amended for administrative reasons.", False, "v5_neg_non_temporal"),
    ],
)
def test_find_trial_design_changes_v5(text, should_match, test_id):
    matches = find_trial_design_changes_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
