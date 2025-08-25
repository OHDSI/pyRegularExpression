# tests/test_data_provenance_finder.py

import pytest
from pyregularexpression.algorithm_validation_finder import (
    find_algorithm_validation_v1,
    find_algorithm_validation_v2,
    find_algorithm_validation_v3,
    find_algorithm_validation_v4,
    find_algorithm_validation_v5,
)

# -----------------------------
# Test cases for v1 (high recall)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("The algorithm was validated against chart review.", True, "v1_pos_basic_validated"),
    ("Algorithm validation showed high performance metrics.", True, "v1_pos_validation_phrase"),
    ("Sensitivity and specificity were calculated for the algorithm.", True, "v1_pos_metric_only"),
    ("A validated questionnaire was used to collect responses.", False, "v1_neg_questionnaire"),
    ("Assay validation was performed in the lab.", False, "v1_neg_assay"),
])
def test_find_algorithm_validation_v1(text, expected, case_id):
    res = find_algorithm_validation_v1(text)
    assert (len(res) > 0) == expected, f"v1 failed for ID: {case_id}"


# -----------------------------
# Test cases for v2 (algorithm + nearby validation verb)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Algorithm validated in the test cohort.", True, "v2_pos_validated_near_algo"),
    ("We assessed the algorithm on external data.", True, "v2_pos_assessed_near_algo"),
    ("The algorithm was applied for prediction.", False, "v2_neg_no_validation_verb"),
    ("Validated questionnaire used in the study.", False, "v2_neg_trap_questionnaire"),
])
def test_find_algorithm_validation_v2(text, expected, case_id):
    res = find_algorithm_validation_v2(text, window=4)
    assert (len(res) > 0) == expected, f"v2 failed for ID: {case_id}"


# -----------------------------
# Test cases for v3 (inside heading blocks)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Algorithm Validation:\nThe algorithm was evaluated on hospital records.", True, "v3_pos_heading_eval"),
    ("Methods: The algorithm was validated externally.", False, "v3_neg_no_heading"),
])
def test_find_algorithm_validation_v3(text, expected, case_id):
    res = find_algorithm_validation_v3(text, block_chars=300)
    assert (len(res) > 0) == expected, f"v3 failed for ID: {case_id}"


# -----------------------------
# Test cases for v4 (algorithm + validation verb + nearby metric)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Algorithm validated with PPV 92% on chart review.", True, "v4_pos_ppv"),
    ("Algorithm evaluated but no metric reported.", False, "v4_neg_no_metric"),
    ("Algorithm applied to predict outcomes.", False, "v4_neg_no_validation"),
])
def test_find_algorithm_validation_v4(text, expected, case_id):
    res = find_algorithm_validation_v4(text, window=6)
    assert (len(res) > 0) == expected, f"v4 failed for ID: {case_id}"


# -----------------------------
# Test cases for v5 (tight template)
# -----------------------------
@pytest.mark.parametrize("text, expected, case_id", [
    ("Algorithm validated against chart review; PPV 92%.", True, "v5_pos_template_ppv"),
    ("Algorithm evaluated but without metrics.", False, "v5_neg_loose_phrase"),
])
def test_find_algorithm_validation_v5(text, expected, case_id):
    res = find_algorithm_validation_v5(text)
    assert (len(res) > 0) == expected, f"v5 failed for ID: {case_id}"
