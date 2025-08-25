# tests/test_ethics_approval_finder.py
"""
Complete test suite for ethics_approval_finder.py.
This suite provides robust checks for v1 and v2 and lighter validation for v3, v4, and v5 variants,
using clinical/medical-style ethics approval and consent statements.
"""
import pytest
from pyregularexpression.ethics_approval_finder import (
    find_ethics_approval_v1,
    find_ethics_approval_v2,
    find_ethics_approval_v3,
    find_ethics_approval_v4,
    find_ethics_approval_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: IRB
        ("The protocol was submitted to the IRB for review.", True, "v1_pos_irb"),
        ("Approval was granted by the ethics committee.", True, "v1_pos_ethics_committee"),
        ("All participants provided informed consent.", True, "v1_pos_informed_consent"),
        # trap: ethics as principle, not approval
        ("The study followed ethical principles of the Declaration of Helsinki.", False, "v1_neg_principles"),
        # trap: unrelated use
        ("She had an ethical dilemma.", False, "v1_neg_ethics_unrelated"),
    ],
)
def test_find_ethics_approval_v1(text, should_match, test_id):
    matches = find_ethics_approval_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"


# ────────────────────────────────────
# Robust Tests for v2 (Verb + IRB/Ethics)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: approved near IRB
        ("The IRB approved the protocol.", True, "v2_pos_irb_approved"),
        ("Ethics committee reviewed and approved the study.", True, "v2_pos_committee_reviewed"),
        # negative: IRB present but no approval verb
        ("The IRB was notified of the trial.", False, "v2_neg_no_verb"),
        # negative: approval verb but no IRB
        ("The protocol was approved by investigators.", False, "v2_neg_no_irb"),
    ],
)
def test_find_ethics_approval_v2(text, should_match, test_id):
    matches = find_ethics_approval_v2(text, window=4)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"


# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: inside heading block
        ("Ethics approval:\nThe IRB approved the trial protocol.\n\n", True, "v3_pos_irb_heading"),
        ("Ethical considerations:\nReviewed by the ethics committee.\n\n", True, "v3_pos_committee_heading"),
        # negative: heading but no cue
        ("Ethics approval:\n(Not applicable)\n\n", False, "v3_neg_empty_block"),
        # negative: cue outside heading
        ("IRB approved the protocol.\n\nEthics approval:\nNot described.", False, "v3_neg_outside_block"),
    ],
)
def test_find_ethics_approval_v3(text, should_match, test_id):
    matches = find_ethics_approval_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"


# ────────────────────────────────────
# Lighter Tests for v4 (Verb + IRB + Consent/Number)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: IRB + approved + consent nearby
        ("The IRB approved the protocol and written informed consent was obtained.", True, "v4_pos_with_consent"),
        # positive: IRB + reviewed + protocol number nearby
        ("Ethics committee reviewed protocol #2021-45.", True, "v4_pos_with_protocol_number"),
        # negative: IRB + verb but no consent/number
        ("The IRB approved the protocol for review.", False, "v4_neg_no_consent_number"),
        # negative: consent but no IRB
        ("Informed consent was obtained from all participants.", False, "v4_neg_consent_only"),
    ],
)
def test_find_ethics_approval_v4(text, should_match, test_id):
    matches = find_ethics_approval_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"


# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: strict template
        ("Protocol approved by XYZ IRB #2021-45; informed consent obtained.", True, "v5_pos_irb_number_consent"),
        ("Protocol was approved by the ethics committee of ABC Hospital; informed consent was waived.", True, "v5_pos_committee_waived"),
        # negative: loose approval statement
        ("The IRB approved the study protocol.", False, "v5_neg_loose"),
        # negative: consent obtained but no IRB mention
        ("Informed consent was obtained from all subjects.", False, "v5_neg_consent_only"),
    ],
)
def test_find_ethics_approval_v5(text, should_match, test_id):
    matches = find_ethics_approval_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
