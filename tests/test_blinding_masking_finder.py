#tests/test_blinding_masking_finder.py

"""
Complete test suite for blinding_masking_finder.py.

Includes:
- Variants v1–v5 (high recall → tight template)
- Positive examples (various blinding/masking scenarios)
- Negative/trap examples (blinded review, open label)
- Smoke-test examples included
"""

import pytest
from pyregularexpression.blinding_masking_finder import (
    find_blinding_masking_v1,
    find_blinding_masking_v2,
    find_blinding_masking_v3,
    find_blinding_masking_v4,
    find_blinding_masking_v5,
)

# ─────────────────────────────
# Examples
# ─────────────────────────────

SMOKE_EXAMPLES = {
    "hit_double": "Double-blind study: participants and assessors were unaware of assignments.",
    "hit_single": "Single-blind trial where participants were masked.",
    "miss_review": "Investigators conducted a blinded review of pathology reports.",
    "miss_open": "The study was open label with no blinding."
}

# ─────────────────────────────
# v1 – High recall: any blinding cue
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Double-blind study: participants and assessors were unaware of assignments.", True, "v1_hit_double"),
        ("Single-blind trial where participants were masked.", True, "v1_hit_single"),
        ("Investigators conducted a blinded review of pathology reports.", False, "v1_miss_review"),
        ("The study was open label with no blinding.", True, "v1_miss_open"),
        ("Masked outcome assessors recorded all events.", True, "v1_hit_masked_assessors"),
        ("No blinding applied in this trial.", True, "v1_hit_unblinded"),
    ]
)
def test_find_blinding_masking_v1(text, should_match, test_id):
    from pyregularexpression.blinding_masking_finder import find_blinding_masking_v1
    matches = find_blinding_masking_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"

# ─────────────────────────────
# v2 – Blinding cue + role keyword within ±4 tokens
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Double-blind study: participants and assessors were unaware of assignments.", True, "v2_hit_double_roles"),
        ("Single-blind trial: participants were masked.", True, "v2_hit_single_roles"),
        ("Masked outcome assessors recorded all events.", True, "v2_hit_masked_assessor"),
        ("Double-blind protocol: investigators conducted analysis.", True, "v2_hit_double_investigators"),
        ("Unblinded study design with no role mentioned.", False, "v2_miss_no_role"),
        ("Blinded review conducted by pathologists.", False, "v2_miss_trap_review"),
    ]
)
def test_find_blinding_masking_v2(text, should_match, test_id):
    from pyregularexpression.blinding_masking_finder import find_blinding_masking_v2
    matches = find_blinding_masking_v2(text)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"

# ─────────────────────────────
# v3 – Only inside a Blinding/Masking heading block
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Blinding:\nDouble-blind study with masked participants.", True, "v3_hit_heading_block"),
        ("Masking:\nSingle-blind trial for outcome assessors.", True, "v3_hit_heading_block_single"),
        ("Introduction:\nDouble-blind study for participants.", False, "v3_miss_wrong_block"),
        ("No heading here but masked participants.", False, "v3_miss_no_heading"),
    ]
)
def test_find_blinding_masking_v3(text, should_match, test_id):
    from pyregularexpression.blinding_masking_finder import find_blinding_masking_v3
    matches = find_blinding_masking_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"

# ─────────────────────────────
# v4 – v2 + ≥2 roles or explicit double/triple/quadruple blind
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Double-blind study: participants and assessors were unaware.", True, "v4_hit_double_two_roles"),
        ("Triple-blind trial with participants, assessors, and clinicians masked.", True, "v4_hit_triple_multiple_roles"),
        ("Single-blind trial: participants were masked.", False, "v4_miss_single_one_role"),
        ("Unblinded study with no roles mentioned.", False, "v4_miss_unblinded_no_roles"),
    ]
)
def test_find_blinding_masking_v4(text, should_match, test_id):
    from pyregularexpression.blinding_masking_finder import find_blinding_masking_v4
    matches = find_blinding_masking_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"

# ─────────────────────────────
# v5 – Tight template: “Double-blind study: participants and assessors were unaware…”
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Double-blind study: participants and assessors were unaware of assignments.", True, "v5_hit_double_template"),
        ("Single-blind trial: participants were masked.", False, "v5_miss_single_template"),
        ("Triple-blind study: participants and assessors were unaware.", False, "v5_miss_triple_template"),
        ("Masked participants in an open-label study.", False, "v5_miss_masked_open_label"),
    ]
)
def test_find_blinding_masking_v5(text, should_match, test_id):
    from pyregularexpression.blinding_masking_finder import find_blinding_masking_v5
    matches = find_blinding_masking_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
