# tests/test_medical_code_finder.py
"""
Complete test suite for medical_code_finder.py.

This suite provides robust checks for v1 and v2
and lighter validation for v3, v4, and v5 variants,
using clinical/medical code strings (ICD, CPT, LOINC, RxNorm, SNOMED, etc.).
"""

import pytest
from pyregularexpression.medical_code_finder import (
    find_medical_code_v1,
    find_medical_code_v2,
    find_medical_code_v3,
    find_medical_code_v4,
    find_medical_code_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: ICD-10-CM
        ("Patient diagnosed with E11.9 diabetes.", True, "v1_pos_icd10"),
        # positive: CPT
        ("Procedure code 99213 was billed.", True, "v1_pos_cpt"),
        # trap: short numeric unrelated
        ("Age 45 years, no code.", False, "v1_neg_short_numeric"),
        # trap: generic programming code
        ("Python source code used for analysis.", False, "v1_neg_generic_code"),
    ]
)
def test_find_medical_code_v1(text, should_match, test_id):
    matches = find_medical_code_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ────────────────────────────────────
# Robust Tests for v2 (Anchor ±window tokens)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: CPT near keyword
        ("The procedure CPT 99213 was completed.", True, "v2_pos_cpt_keyword"),
        # negative: code isolated, no keyword
        ("E11.9 noted.", False, "v2_neg_no_keyword"),
        # negative: short numeric near keyword but not a code
        ("Program 123 executed.", False, "v2_neg_short_numeric"),
    ]
)
def test_find_medical_code_v2(text, should_match, test_id):
    matches = find_medical_code_v2(text, window=5)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v3 (Heading-anchored block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: inside diagnosis heading
        ("Diagnosis Codes:\nE11.9 Diabetes Mellitus\n", True, "v3_pos_diagnosis_block"),
        # positive: inside procedure heading
        ("Procedure Codes:\n99213 Office visit\n", True, "v3_pos_procedure_block"),
        # negative: code outside heading
        ("E11.9 Diabetes Mellitus\n\nDiagnosis Codes:\nNone reported", False, "v3_neg_outside_block"),
        # negative: empty heading
        ("Procedure Codes:\n(No codes)\n", False, "v3_neg_empty_block"),
    ]
)
def test_find_medical_code_v3(text, should_match, test_id):
    matches = find_medical_code_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v4 (Defensive look-arounds)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: valid ICD
        ("Patient with ICD-10-CM code E11.9 observed.", True, "v4_pos_icd_valid"),
        # positive: SNOMED code
        ("SNOMED 123456 documented.", True, "v4_pos_snomed"),
        # negative: short numeric preceeded by mg
        ("50 mg 123 administered.", False, "v4_neg_pre_token"),
        # negative: generic trap phrase
        ("Python source code used.", False, "v4_neg_generic_trap"),
    ]
)
def test_find_medical_code_v4(text, should_match, test_id):
    matches = find_medical_code_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ────────────────────────────────────
# Lighter Tests for v5 (Strict stand-alone)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # positive: strict token
        ("E11.9", True, "v5_pos_strict_icd"),
        # positive: strict token with ATC
        ("A10BA02", True, "v5_pos_strict_atc"),
        # negative: lower-case or partial token
        ("e11.9", False, "v5_neg_lowercase"),
    ]
)
def test_find_medical_code_v5(text, should_match, test_id):
    matches = find_medical_code_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
