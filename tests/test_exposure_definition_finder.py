#tests/test_exposure_definition_finder.py
"""Smoke tests for exposure_definition_finder variants.
Covers:
- All five precision/recall variants (v1–v5)
- Examples derived from PubMed clinical trials and OHDSI study protocols
- Balanced coverage of positives and false-positive traps
"""

import pytest
from pyregularexpression.exposure_definition_finder import (
    find_exposure_definition_v1,
    find_exposure_definition_v2,
    find_exposure_definition_v3,
    find_exposure_definition_v4,
    find_exposure_definition_v5,
)

# ─────────────────────────────
# v1 – Any exposure cue (high recall)
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # ✅ PubMed/OHDSI-aligned
        ("We examined drug exposure in the target cohort.", True, "v1_pos_examined_drug_exposure"),
        ("Radiation exposure was analyzed over 12 months.", True, "v1_pos_radiation_exposure"),
        ("Exposure to opioids was tracked post-discharge.", True, "v1_pos_exposure_opioids_tracked"),

        # ❌ Traps or irrelevant mentions
        ("Participants were allocated to the exposure group.", False, "v1_neg_exposure_group_label"),
        ("Exposure pathway analysis was done post-hoc.", False, "v1_neg_exposure_as_analysis_type"),
    ]
)
def test_find_exposure_definition_v1(text, should_match, test_id):
    matches = find_exposure_definition_v1(text)
    assert bool(matches) == should_match, f"v1 failed on: {test_id}"


# ─────────────────────────────
# v2 – Exposure cue + defining verb within ±window
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # ✅ Confirmed from OHDSI cohort logic and PubMed methods
        ("Exposure was defined as two prescriptions of ACE inhibitors.", True, "v2_pos_defined_as_two_prescriptions"),
        ("We operationalized opioid exposure based on prescription records.", True, "v2_pos_operationalized_opioid_exposure"),
        ("Exposure was considered present if >=1 refill was observed.", True, "v2_pos_considered_present"),

        # ❌ Missing defining verb near exposure term
        ("Exposure was common among participants.", False, "v2_neg_exposure_without_definition"),
        ("We measured exposure but did not define it.", False, "v2_neg_exposure_mention_only"),
    ]
)
def test_find_exposure_definition_v2(text, should_match, test_id):
    matches = find_exposure_definition_v2(text)
    assert bool(matches) == should_match, f"v2 failed on: {test_id}"


# ─────────────────────────────
# v3 – Inside an “Exposure Definition” block
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # ✅ OHDSI-style or publication-aligned section headers
        ("Exposure Assessment:\nWe defined exposure as ≥2 prescriptions within 60 days.\n\n", True, "v3_pos_assessment_section"),
        ("Exposure Definition:\nPatients were required to have ≥1 fill within 30 days.\n\n", True, "v3_pos_definition_header"),

        # ❌ Appears outside a valid section
        ("Methods:\nExposure was evaluated descriptively.", False, "v3_neg_wrong_section"),
        ("Baseline characteristics included exposure.", False, "v3_neg_non_definition_context"),
    ]
)
def test_find_exposure_definition_v3(text, should_match, test_id):
    matches = find_exposure_definition_v3(text)
    assert bool(matches) == should_match, f"v3 failed on: {test_id}"


# ─────────────────────────────
# v4 – Cue + defining verb + numeric or logical criterion (≥, days, prescriptions)
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # ✅ Strong definitions with thresholds
        ("Exposure was defined as ≥2 prescriptions within 90 days.", True, "v4_pos_defined_plus_threshold"),
        ("We considered exposure present if patients had at least 30 days' supply.", True, "v4_pos_considered_with_criterion"),
        ("Operationalized exposure as 1 refill in 14 days.", True, "v4_pos_operationalized_refill"),

        # ❌ No numeric or time-based definition
        ("Exposure was defined as drug use.", False, "v4_neg_defined_but_no_criteria"),
        ("We examined exposure but did not define thresholds.", False, "v4_neg_no_thresholds_given"),
    ]
)
def test_find_exposure_definition_v4(text, should_match, test_id):
    matches = find_exposure_definition_v4(text)
    assert bool(matches) == should_match, f"v4 failed on: {test_id}"


# ─────────────────────────────
# v5 – Tight templates only (“Exposure was defined as ≥X prescriptions...”)
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # ✅ Tight, templated phrasing
        ("Exposure was defined as ≥2 prescriptions of metformin within 60 days.", True, "v5_pos_tight_defined_metformin"),
        ("Exposure = 3 fills of opioid within 30 days prior to index.", True, "v5_pos_tight_equals_style"),

        # ❌ Looser or implicit definitions
        ("We examined opioid exposure during follow-up.", False, "v5_neg_generic_mention"),
        ("Exposure was based on prescription activity.", False, "v5_neg_loose_definition"),
    ]
)
def test_find_exposure_definition_v5(text, should_match, test_id):
    matches = find_exposure_definition_v5(text)
    assert bool(matches) == should_match, f"v5 failed on: {test_id}"
