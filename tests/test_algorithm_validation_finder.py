"""
Complete test suite for algorithm_validation_finder.py.

Includes:
- Robust tests for v1 and v2 (recall and context awareness)
- Lighter representative tests for v3, v4, and v5
- All examples inspired by real OHDSI or PubMed validation literature
"""

import pytest
from pyregularexpression.algorithm_validation_finder import (
    find_algorithm_validation_v1,
    find_algorithm_validation_v2,
    find_algorithm_validation_v3,
    find_algorithm_validation_v4,
    find_algorithm_validation_v5,
)

# ─────────────────────────────
# Robust Tests for v1 – High Recall
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("Algorithm validation was performed using chart review.", True, "v1_pos_algorithm_validation_phrase"),
        ("We assessed algorithm performance in identifying atrial fibrillation.", True, "v1_pos_validated_with_performance"),
        ("The sensitivity and PPV of the algorithm were evaluated.", True, "v1_pos_metric_keyword"),
        
        # Trap phrases (must not match)
        ("A validated questionnaire was used to assess symptoms.", False, "v1_trap_validated_questionnaire"),
        ("Analytical method validation showed acceptable results.", False, "v1_trap_method_validation"),
        
        # Negative examples
        ("The algorithm was applied to detect heart failure.", False, "v1_neg_applied_no_validation"),
        ("Our method uses rule-based logic.", False, "v1_neg_generic_method"),
    ]
)
def test_find_algorithm_validation_v1(text, should_match, test_id):
    matches = find_algorithm_validation_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"


# ─────────────────────────────
# Robust Tests for v2 – Windowed Context: algorithm + validation verb
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive examples
        ("The algorithm was externally validated on a claims database.", True, "v2_pos_algorithm_validated_near"),
        ("We evaluated the algorithm’s performance using test data.", True, "v2_pos_evaluated_algorithm_near"),
        
        # Negative examples
        ("Validated instrument used to collect survey data.", False, "v2_neg_trap_validated_instrument"),
        ("The cohort was defined using a known algorithm.", False, "v2_neg_no_validation_verb"),
    ]
)
def test_find_algorithm_validation_v2(text, should_match, test_id):
    matches = find_algorithm_validation_v2(text)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v3 – Inside validation/performance heading blocks
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Algorithm validation:\nThe algorithm was evaluated on EHR data.\n\n", True, "v3_pos_in_heading_block"),
        ("Performance evaluation:\nAccuracy and PPV were calculated.\n\n", True, "v3_pos_metric_in_heading_block"),
        ("Results:\nThe algorithm showed good performance.\n\n", False, "v3_neg_wrong_heading"),
    ]
)
def test_find_algorithm_validation_v3(text, should_match, test_id):
    matches = find_algorithm_validation_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v4 – v2 + metric keyword in window
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive: v2 + metric
        ("The algorithm was evaluated and achieved a PPV of 91%.", True, "v4_pos_eval_metric_combo"),
        
        # Negative: v2 match without metric
        ("We evaluated the algorithm for use in identifying asthma.", False, "v4_neg_no_metric_near"),
        ("Validated by comparing diagnoses with physician notes.", False, "v4_neg_no_metric_trap_like"),
    ]
)
def test_find_algorithm_validation_v4(text, should_match, test_id):
    matches = find_algorithm_validation_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v5 – Tight template match
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive: realistic template
        ("Algorithm was validated using chart review; PPV 91% and sensitivity 88%.", True, "v5_pos_chart_review_ppv"),
        ("The algorithm was validated in external data with accuracy 0.89 (95% CI).", True, "v5_pos_accuracy_with_algorithm"),
        
        # Negative: loose structure
        ("The algorithm was applied to identify cases; results were promising.", False, "v5_neg_applied_loose"),
        ("Validation included review of patient cases but no metrics reported.", False, "v5_neg_no_metric"),
    ]
)
def test_find_algorithm_validation_v5(text, should_match, test_id):
    matches = find_algorithm_validation_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
