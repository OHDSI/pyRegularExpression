# tests/test_healthcare_setting_finder.py
"""
Complete test suite for healthcare_setting_finder.py.
This suite provides robust checks for v1 and v2 and lighter validation for v3, v4, and v5 variants,
using clinical/medical-style healthcare setting statements.
"""
import pytest
from pyregularexpression.healthcare_setting_finder import (
    find_healthcare_setting_v1,
    find_healthcare_setting_v2,
    find_healthcare_setting_v3,
    find_healthcare_setting_v4,
    find_healthcare_setting_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: basic facility
        ("The study included inpatient participants.", True, "v1_pos_inpatient"),
        ("Data were collected from the ICU.", True, "v1_pos_icu"),
        ("Community pharmacy records were analyzed.", True, "v1_pos_pharmacy"),
        # trap: non-healthcare 'clinic'
        ("The political clinic was closed.", False, "v1_neg_non_healthcare_clinic"),
        # trap: real-world setting phrase
        ("This was a real-world setting trial.", False, "v1_neg_real_world"),
    ],
)
def test_find_healthcare_setting_v1(text, should_match, test_id):
    matches = find_healthcare_setting_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"


# ────────────────────────────────────
# Robust Tests for v2 (Facility + Context Window)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: facility near context
        ("The inpatient setting was described in detail.", True, "v2_pos_inpatient_setting"),
        ("Treatment was provided in an outpatient clinic.", True, "v2_pos_outpatient_clinic"),
        # negative: facility but no context word nearby
        ("The hospital cafeteria served meals.", False, "v2_neg_cafeteria"),
        # negative: context word but no facility
        ("The care setting was supportive but not specified.", False, "v2_neg_context_only"),
    ],
)
def test_find_healthcare_setting_v2(text, should_match, test_id):
    matches = find_healthcare_setting_v2(text, window=3)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"


# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: facility inside heading block
        ("Healthcare setting:\nPatients were recruited from ICU wards.\n\n", True, "v3_pos_heading_block"),
        ("Study setting:\nPrimary care clinics participated in the trial.\n\n", True, "v3_pos_primary_care"),
        # negative: heading but no facility
        ("Healthcare setting:\n(Not specified)\n\n", False, "v3_neg_empty_block"),
        # negative: facility outside block
        ("Patients were enrolled from hospitals.\n\nHealthcare setting:\nNot provided.", False, "v3_neg_outside_block"),
    ],
)
def test_find_healthcare_setting_v3(text, should_match, test_id):
    matches = find_healthcare_setting_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"


# ────────────────────────────────────
# Lighter Tests for v4 (Facility + Context + Qualifier)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: qualifier + facility
        ("Patients were enrolled in primary care clinics.", True, "v4_pos_primary_care"),
        ("Treatment was provided at an academic hospital setting.", True, "v4_pos_academic_hospital"),
        # negative: facility + context but no qualifier
        ("Outpatient clinic visits were scheduled.", False, "v4_neg_no_qualifier"),
        # negative: qualifier but no facility
        ("Community support groups were active.", False, "v4_neg_no_facility"),
    ],
)
def test_find_healthcare_setting_v4(text, should_match, test_id):
    matches = find_healthcare_setting_v4(text, window=4)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"


# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: canonical template examples
        ("The trial was conducted in five primary-care clinics across the region.", True, "v5_pos_primary_care"),
        ("Data from an ICU inpatient setting were analyzed.", True, "v5_pos_icu_inpatient"),
        # negative: loose phrase without template structure
        ("The hospital was part of the study.", False, "v5_neg_loose_phrase"),
        ("Care was delivered in various settings.", False, "v5_neg_generic_setting"),
    ],
)
def test_find_healthcare_setting_v5(text, should_match, test_id):
    matches = find_healthcare_setting_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
