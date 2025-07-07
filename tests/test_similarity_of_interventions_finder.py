# tests/test_similarity_of_interventions_finder.py
"""
Complete test suite for similarity_of_interventions_finder.py.
Covers five variants (v1–v5):
    • v1 – high recall (any similarity cue)
    • v2 – similarity cue + intervention form word
    • v3 – inside Similarity of Interventions heading block
    • v4 – v2 + explicit qualifier + form word nearby
    • v5 – tight template (explicit placebo injection matching active drug)
"""
import pytest
from pyregularexpression.similarity_of_interventions_finder import (
    find_similarity_of_interventions_v1,
    find_similarity_of_interventions_v2,
    find_similarity_of_interventions_v3,
    find_similarity_of_interventions_v4,
    find_similarity_of_interventions_v5,
)

# ────────────────────────────────────
# Robust Tests for v1 (High Recall)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The study used identical placebo capsules.", True, "v1_pos_identical_placebo"),
        ("Patients received a sham procedure.", True, "v1_pos_sham_procedure"),
        ("Treatment was double‑dummy controlled.", True, "v1_pos_double_dummy"),
        ("The control group received standard care.", False, "v1_neg_no_similarity_cue"),
    ],
)
def test_find_similarity_of_interventions_v1(text, should_match, test_id):
    matches = find_similarity_of_interventions_v1(text)
    assert bool(matches) == should_match, f"v1 failed for {test_id}"


# ────────────────────────────────────
# Robust Tests for v2 (Cue + Form Word)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Identical placebo injection was administered.", True, "v2_pos_identical_injection"),
        ("Sham procedure performed with device.", True, "v2_pos_sham_device"),
        ("Matched capsules given to the active arm.", True, "v2_pos_matched_capsule"),
        ("Identical appearance observed.", False, "v2_neg_no_form_word"),
    ],
)
def test_find_similarity_of_interventions_v2(text, should_match, test_id):
    matches = find_similarity_of_interventions_v2(text, window=4)
    assert bool(matches) == should_match, f"v2 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v3 (Heading Block)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Similarity of Interventions:\nControl arm received matched placebo.", True, "v3_pos_heading_block"),
        ("Blinding materials:\nDouble-dummy capsules were prepared.", True, "v3_pos_blinding_block"),
        ("Matched placebo injections used outside section.", False, "v3_neg_outside_block"),
        ("No intervention similarity section.", False, "v3_neg_missing_heading"),
    ],
)
def test_find_similarity_of_interventions_v3(text, should_match, test_id):
    matches = find_similarity_of_interventions_v3(text)
    assert bool(matches) == should_match, f"v3 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v4 (Qualifier + Form Word)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Control arm received placebo injection identical in appearance.", True, "v4_pos_qualifier_form"),
        ("Patients received indistinguishable capsules.", True, "v4_pos_indistinguishable_capsule"),
        ("Sham treatment administered without matching appearance.", False, "v4_neg_no_qualifier"),
        ("Placebo device used; not identical to active device.", False, "v4_neg_incomplete_match"),
    ],
)
def test_find_similarity_of_interventions_v4(text, should_match, test_id):
    matches = find_similarity_of_interventions_v4(text, window=6)
    assert bool(matches) == should_match, f"v4 failed for {test_id}"


# ────────────────────────────────────
# Lighter Tests for v5 (Tight Template)
# ────────────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Control arm received placebo injection identical in appearance to active drug.", True, "v5_pos_tight_template"),
        ("Placebo capsule identical to active treatment administered.", True, "v5_pos_variant"),
        ("Placebo administered, but no matching information provided.", False, "v5_neg_no_matching_info"),
        ("Active drug given; placebo not identical.", False, "v5_neg_incomplete_template"),
    ],
)
def test_find_similarity_of_interventions_v5(text, should_match, test_id):
    matches = find_similarity_of_interventions_v5(text)
    assert bool(matches) == should_match, f"v5 failed for {test_id}"
