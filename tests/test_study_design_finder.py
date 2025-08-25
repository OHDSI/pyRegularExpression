# tests/test_study_design_finder.py
"""
Complete test suite for study_design_finder.py.
Covers five variants (v1–v5):
    • v1 – high recall: any design keyword
    • v2 – design keyword + linking phrase within ±window tokens
    • v3 – only inside Study design / Methods heading block
    • v4 – v2 + canonical design pair or temporal qualifier
    • v5 – tight template (Retrospective cohort study …)
"""
import pytest
from pyregularexpression.study_design_finder import (
    find_study_design_v1,
    find_study_design_v2,
    find_study_design_v3,
    find_study_design_v4,
    find_study_design_v5,
)

# ─────────────────────────────
# v1 – high recall
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("We conducted a randomized controlled trial in 2020.", True, "v1_pos_rct"),
        ("This is a retrospective cohort study of patients with diabetes.", True, "v1_pos_retrospective_cohort"),
        ("We designed to test the hypothesis.", False, "v1_neg_trap_design_to"),
    ],
)
def test_v1(text, should_match, test_id):
    matches = find_study_design_v1(text)
    assert bool(matches) == should_match, f"v1 failed for {test_id}"


# ─────────────────────────────
# v2 – keyword + linking phrase
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("This was a randomized controlled trial of aspirin.", True, "v2_pos_linking_phrase_rct"),
        ("The study was a case-control study in Sweden.", True, "v2_pos_case_control"),
        ("A prospective cohort study was conducted in Japan.", True, "v2_pos_prospective_cohort"),
        ("Randomized controlled trial reported in registry.", False, "v2_neg_no_linking_phrase"),
    ],
)
def test_v2(text, should_match, test_id):
    matches = find_study_design_v2(text, window=4)
    assert bool(matches) == should_match, f"v2 failed for {test_id}"


# ─────────────────────────────
# v3 – only inside heading block
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Study design:\nThis was a prospective cohort study of patients with hypertension.", True, "v3_pos_inside_heading"),
        ("Methods:\nWe conducted a randomized controlled trial.", True, "v3_pos_methods_heading"),
        ("Background:\nThis was a randomized controlled trial.", False, "v3_neg_wrong_heading"),
        ("The study was a cohort study outside heading.", False, "v3_neg_outside_block"),
    ],
)
def test_v3(text, should_match, test_id):
    matches = find_study_design_v3(text)
    assert bool(matches) == should_match, f"v3 failed for {test_id}"


# ─────────────────────────────
# v4 – canonical pair or temporal qualifier
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("This was a randomized controlled trial conducted at 5 centers.", True, "v4_pos_rct_canonical"),
        ("This was a prospective cohort study of stroke patients.", True, "v4_pos_prospective_cohort"),
        ("This was a cohort study, but details unclear.", False, "v4_neg_non_canonical"),
    ],
)
def test_v4(text, should_match, test_id):
    matches = find_study_design_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for {test_id}"


# ─────────────────────────────
# v5 – tight template
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Retrospective cohort study using registry data in Denmark.", True, "v5_pos_retrospective_template"),
        ("Randomized controlled trial of drug X in heart failure.", True, "v5_pos_rct_template"),
        ("We performed a cohort analysis.", False, "v5_neg_loose_phrase"),
        ("Case series report.", False, "v5_neg_not_template"),
    ],
)
def test_v5(text, should_match, test_id):
    matches = find_study_design_v5(text)
    assert bool(matches) == should_match, f"v5 failed for {test_id}"
