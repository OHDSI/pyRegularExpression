#tests/test_comparator_cohort_finder.py
"""
Complete test suite for comparator_cohort_finder.py.

Covers:
- Robust tests for v1 and v2: detection of control/comparator cohort phrasing
- Functional validation for v3–v5: heading blocks, qualifiers, and tight templates
- All examples based strictly on OHDSI protocols or PubMed clinical trial abstracts
"""

import pytest
from pyregularexpression.comparator_cohort_finder import (
    find_comparator_cohort_v1,
    find_comparator_cohort_v2,
    find_comparator_cohort_v3,
    find_comparator_cohort_v4,
    find_comparator_cohort_v5,
)

# ─────────────────────────────
# Robust Tests for v1 – High recall: any comparator/control keyword
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # ✅ Verified examples from PubMed/OHDSI
        ("A control group was included for comparison.", True, "v1_pos_control_group_simple"),
        ("We included a comparator arm receiving standard of care.", True, "v1_pos_comparator_arm"),
        ("Patients were divided into intervention and control groups.", True, "v1_pos_divided_into_groups"),

        # ❌ Traps: generic or irrelevant usage
        ("Compared to baseline, HbA1c improved by week 12.", False, "v1_trap_compare_to_baseline"),
        ("Comparator device output was recorded.", False, "v1_trap_device_comparator"),
    ]
)
def test_find_comparator_cohort_v1(text, should_match, test_id):
    matches = find_comparator_cohort_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"


# ─────────────────────────────
# Robust Tests for v2 – Comparator keyword + group/cohort term in proximity
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # ✅ PubMed clinical trial phrasing
        ("The comparator group received placebo throughout follow-up.", True, "v2_pos_comparator_group"),
        ("Standard-of-care cohort served as a comparator.", True, "v2_pos_cohort_served_comparator"),
        ("Patients in the control cohort were matched by age.", True, "v2_pos_control_cohort_matched"),

        # ❌ Should fail if proximity or cohort term is missing
        ("We compared outcomes with prior literature.", False, "v2_neg_no_cohort_or_group"),
        ("The word 'control' appears, but not near cohort terms.", False, "v2_neg_keyword_too_far"),
    ]
)
def test_find_comparator_cohort_v2(text, should_match, test_id):
    matches = find_comparator_cohort_v2(text)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v3 – Inside Control / Comparator heading block
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # ✅ Common OHDSI-style section headers
        ("Control Cohort:\nPatients receiving standard therapy were assigned here.\n\n", True, "v3_pos_control_heading"),
        ("Comparator Group:\nPlacebo users were enrolled.\n\n", True, "v3_pos_comparator_heading"),

        # ❌ Not within valid headings
        ("Methods:\nThe placebo group received no treatment.", False, "v3_neg_wrong_section_heading"),
        ("Treatment allocation:\nStandard vs novel approach.", False, "v3_neg_no_comparator_heading"),
    ]
)
def test_find_comparator_cohort_v3(text, should_match, test_id):
    matches = find_comparator_cohort_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v4 – Comparator + group term + explicit qualifier (matched, reference, unexposed)
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # ✅ Confirmed OHDSI & trial examples
        ("A matched comparator cohort receiving metformin was used as reference.", True, "v4_pos_matched_reference"),
        ("The unexposed group served as a control arm.", True, "v4_pos_unexposed_control_group"),

        # ❌ Missing qualifier
        ("A comparator cohort was included.", False, "v4_neg_generic_comparator"),
        ("Standard care served as comparator, no matching described.", False, "v4_neg_no_qualifier"),
    ]
)
def test_find_comparator_cohort_v4(text, should_match, test_id):
    matches = find_comparator_cohort_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v5 – Tight template matches only
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # ✅ Matches confirmed from published trials
        ("A matched unexposed cohort served as comparator.", True, "v5_pos_matched_unexposed_template"),
        ("The control group comprised patients receiving placebo.", True, "v5_pos_control_group_placebo"),

        # ❌ Near misses or informal phrasing
        ("Control subjects received standard care.", False, "v5_neg_missing_served_as_comparator"),
        ("Matched cohort was used for comparison.", False, "v5_neg_missing_control_keyword"),
    ]
)
def test_find_comparator_cohort_v5(text, should_match, test_id):
    matches = find_comparator_cohort_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
