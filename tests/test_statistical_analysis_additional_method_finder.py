# tests/test_statistical_analysis_additional_method_finder.py
"""
Complete test suite for statistical_analysis_additional_method_finder.py.
Covers five variants (v1–v5):
    • v1 – high recall: any secondary/subgroup/exploratory/post-hoc analysis + analysis verb
    • v2 – v1 + explicit statistical test/model within ±4 tokens
    • v3 – only inside Statistical Analysis / Secondary/Subgroup heading block
    • v4 – v2 + subgroup term or secondary/post-hoc/exploratory keyword nearby
    • v5 – tight template: “Secondary outcomes analysed with logistic regression; age subgroups examined.”
"""
import pytest
from pyregularexpression.statistical_analysis_additional_method_finder import (
    find_statistical_analysis_additional_method_v1,
    find_statistical_analysis_additional_method_v2,
    find_statistical_analysis_additional_method_v3,
    find_statistical_analysis_additional_method_v4,
    find_statistical_analysis_additional_method_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Secondary analyses were performed on the dataset.", True, "v1_pos_secondary_performed"),
        ("Subgroup analysis evaluated treatment effect.", True, "v1_pos_subgroup_evaluated"),
        ("Exploratory analysis modelled interactions.", True, "v1_pos_exploratory_modelled"),
        ("The primary endpoint was measured.", False, "v1_neg_no_secondary"),
    ],
)
def test_find_statistical_analysis_additional_method_v1(text, should_match, test_id):
    matches = find_statistical_analysis_additional_method_v1(text)
    assert bool(matches) == should_match, f"v1 failed for {test_id}"


# ────────────────────────────────────
# Robust Tests for v2 (Cue + Statistical Test)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Secondary outcomes analysed with logistic regression.", True, "v2_pos_logistic_regression"),
        ("Post-hoc evaluation with ANOVA performed.", True, "v2_pos_anova"),
        ("Secondary analyses were descriptive only.", False, "v2_neg_no_stat_test"),
    ],
)
def test_find_statistical_analysis_additional_method_v2(text, should_match, test_id):
    matches = find_statistical_analysis_additional_method_v2(text, window=4)
    assert bool(matches) == should_match, f"v2 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Statistical Analysis:\nSecondary outcomes analysed using logistic regression.", True, "v3_pos_stat_analysis_block"),
        ("Subgroup Analysis:\nCox regression applied to age groups.", True, "v3_pos_subgroup_block"),
        ("Secondary analysis outside any heading block.", False, "v3_neg_outside_block"),
        ("Exploratory analysis not mentioned.", False, "v3_neg_missing_heading"),
    ],
)
def test_find_statistical_analysis_additional_method_v3(text, should_match, test_id):
    matches = find_statistical_analysis_additional_method_v3(text)
    assert bool(matches) == should_match, f"v3 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v4 (Subgroup/Secondary + Stat Test)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Secondary outcomes analysed with logistic regression; age subgroups examined.", True, "v4_pos_secondary_age_subgroup"),
        ("Subgroup analyses with Cox regression performed by sex.", True, "v4_pos_cox_sex_subgroup"),
        ("Exploratory outcomes analysed using descriptive stats only.", False, "v4_neg_no_stat_test"),
        ("Post-hoc analysis reported, but no subgroup considered.", False, "v4_neg_no_subgroup"),
    ],
)
def test_find_statistical_analysis_additional_method_v4(text, should_match, test_id):
    matches = find_statistical_analysis_additional_method_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Secondary outcomes analysed with logistic regression; age subgroups examined.", True, "v5_pos_tight_template"),
        ("Subgroup analyses performed; logistic regression applied to baseline characteristics.", True, "v5_pos_variant"),
        ("Secondary outcomes analysed descriptively without regression.", False, "v5_neg_no_template_match"),
        ("Post-hoc evaluation reported; no logistic regression.", False, "v5_neg_incomplete_template"),
    ],
)
def test_find_statistical_analysis_additional_method_v5(text, should_match, test_id):
    matches = find_statistical_analysis_additional_method_v5(text)
    assert bool(matches) == should_match, f"v5 failed for {test_id}"
