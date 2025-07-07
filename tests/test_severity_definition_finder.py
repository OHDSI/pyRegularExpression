# tests/test_severity_definition_finder.py
"""
Complete test suite for severity_definition_finder.py.
Covers five variants (v1–v5):
    • v1 – high recall (any severity cue)
    • v2 – cue + defining verb within window
    • v3 – inside Severity definition / Classification heading block
    • v4 – v2 + multi-level listing or threshold token nearby
    • v5 – tight template (explicit definition/classification statements)
"""
import pytest
from pyregularexpression.severity_definition_finder import (
    find_severity_definition_v1,
    find_severity_definition_v2,
    find_severity_definition_v3,
    find_severity_definition_v4,
    find_severity_definition_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Patients were classified as mild, moderate, or severe.", True, "v1_pos_listing"),
        ("Severity of disease was recorded.", True, "v1_pos_severity_cue"),
        ("Mild symptoms were observed.", True, "v1_pos_mild"),
        ("Severe weather affected enrollment.", False, "v1_neg_trap_nonclinical"),
    ],
)
def test_find_severity_definition_v1(text, should_match, test_id):
    matches = find_severity_definition_v1(text)
    assert bool(matches) == should_match, f"v1 failed for {test_id}"


# ────────────────────────────────────
# Robust Tests for v2 (Cue + Defining Verb)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Severity was defined as mild, moderate, or severe.", True, "v2_pos_defined"),
        ("Patients were classified by severity.", True, "v2_pos_classified"),
        ("Moderate cases were treated aggressively.", False, "v2_neg_no_verb"),
        ("Mild symptoms observed in all participants.", False, "v2_neg_no_defining_verb"),
    ],
)
def test_find_severity_definition_v2(text, should_match, test_id):
    matches = find_severity_definition_v2(text, window=5)
    assert bool(matches) == should_match, f"v2 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Severity Definition:\nPatients were mild, moderate, or severe.", True, "v3_pos_heading_block"),
        ("Classification:\nSeverity was recorded.", True, "v3_pos_classification_block"),
        ("Severity observed outside heading.", False, "v3_neg_outside_block"),
        ("No severity section provided.", False, "v3_neg_missing_heading"),
    ],
)
def test_find_severity_definition_v3(text, should_match, test_id):
    matches = find_severity_definition_v3(text)
    assert bool(matches) == should_match, f"v3 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v4 (Listing / Threshold)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Severity was defined as mild, moderate, severe based on IV antibiotics.", True, "v4_pos_listing_threshold"),
        ("Severity was assessed but no threshold or multi-level categories.", False, "v4_neg_no_listing_threshold"),
        ("Moderate cases treated; severe not defined.", False, "v4_neg_partial_definition"),
    ],
)
def test_find_severity_definition_v4(text, should_match, test_id):
    matches = find_severity_definition_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Severity was defined by oxygen requirement and hospital admission.", True, "v5_pos_tight_template"),
        ("Disease classified as mild/moderate/severe based on IV antibiotics usage.", True, "v5_pos_variant"),
        ("Severity recorded but no definition provided.", False, "v5_neg_no_definition"),
        ("Moderate patients observed; mild/severe not defined.", False, "v5_neg_incomplete_template"),
    ],
)
def test_find_severity_definition_v5(text, should_match, test_id):
    matches = find_severity_definition_v5(text)
    assert bool(matches) == should_match, f"v5 failed for {test_id}"
