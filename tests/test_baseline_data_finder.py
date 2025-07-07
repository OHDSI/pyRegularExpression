#tests/test_baseline_data_finder.py

import pytest
from pyregularexpression.baseline_data_finder import (
    find_baseline_data_v1,
    find_baseline_data_v2,
    find_baseline_data_v3,
    find_baseline_data_v4,
    find_baseline_data_v5,
)

# ─────────────────────────────
# Robust Tests for v1 – High Recall: baseline cue + number/%
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Baseline characteristics: Mean age 63 years, 45% male.", True, "v1_pos_age_pct"),
        ("At baseline, BMI was 27.5 ± 4.1.", True, "v1_pos_at_baseline_numeric"),
        ("Table 1 shows demographics including 30% smokers.", True, "v1_pos_table_with_percentage"),

        # Negative examples
        ("Baseline tumor location was recorded.", False, "v1_neg_no_number"),
        ("Participants were enrolled from multiple centers.", False, "v1_neg_no_baseline_cue"),
        ("The majority were male.", False, "v1_neg_no_baseline_or_number"),
    ]
)
def test_find_baseline_data_v1(text, should_match, test_id):
    matches = find_baseline_data_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"


# ─────────────────────────────
# Robust Tests for v2 – v1 + group comparison cue (e.g., vs, placebo)
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Mean age at baseline was 54 vs 55 years in treatment and placebo groups.", True, "v2_pos_vs_with_groups"),
        ("Table 1: 60% female in the treatment group, 58% in placebo.", True, "v2_pos_group_labels"),
        ("Baseline BMI was 29.4 ± 5.1 compared to 27.1 ± 4.9.", True, "v2_pos_compared_to"),

        # Negative examples
        ("Baseline BMI was 27.3 for the entire cohort.", False, "v2_neg_no_group_comparison"),
        ("Baseline characteristics: Mean age 63.", False, "v2_neg_number_but_no_group_term"),
    ]
)
def test_find_baseline_data_v2(text, should_match, test_id):
    matches = find_baseline_data_v2(text)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v3 – In heading blocks (Baseline Characteristics / Table 1)
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Baseline Characteristics:\nMean age 56 years, BMI 28.4 ± 3.7\n\n", True, "v3_pos_heading_block"),
        ("Table 1\nDemographics: 49% female and 31% smokers.\n\n", True, "v3_pos_table_heading"),

        # Negative examples
        ("Demographics summary: age 54, 60% male.", False, "v3_neg_wrong_heading"),
        ("Patient characteristics:\nSmoking status was reported.", False, "v3_neg_not_in_baseline_block"),
    ]
)
def test_find_baseline_data_v3(text, should_match, test_id):
    matches = find_baseline_data_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v4 – v2 + ≥2 variables or multiple numeric values
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("At baseline: age 55 vs 57, BMI 29.3 vs 27.4.", True, "v4_pos_multiple_variables"),
        ("Baseline characteristics: 63% male vs 60%, mean age 54 vs 55.", True, "v4_pos_pct_and_age"),
        ("Baseline: BMI 29.4 in treatment vs 28.7 placebo.", True, "v4_pos_two_numbers_one_var"),

        # Negative examples
        ("At baseline, heart rate was measured.", False, "v4_neg_no_group_no_multiple_numbers"),
    ]
)
def test_find_baseline_data_v4(text, should_match, test_id):
    matches = find_baseline_data_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v5 – Tight template match
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Mean age 54 vs 55; 60 % female in both groups at baseline.", True, "v5_pos_mean_age_pct_both_groups"),
        ("Baseline: 70% male vs 68% male; median age 52 vs 50.", True, "v5_pos_compact_template"),

        # Negative examples
        ("Baseline BMI 28.5 in treatment and 28.3 in placebo.", False, "v5_neg_not_enough_structure"),
        ("At baseline: mean age 54; no gender data reported.", False, "v5_neg_missing_comparison_structure"),
    ]
)
def test_find_baseline_data_v5(text, should_match, test_id):
    matches = find_baseline_data_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
