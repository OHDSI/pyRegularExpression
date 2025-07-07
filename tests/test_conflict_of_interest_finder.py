# tests/test_conflict_of_interest_finder.py
"""
Test suite for conflict_of_interest_finder.py

Variants:
- v1: high recall — any sentence with a conflict cue
- v2: cue + disclosure verb within ±4 tokens
- v3: only inside Conflict of Interest / Disclosures / Competing Interests heading block
- v4: v2 + explicit company/payment mention OR explicit negation phrase
- v5: tight template — "The authors declare no competing interests."
"""

import pytest
from pyregularexpression.conflict_of_interest_finder import (
    find_conflict_of_interest_v1,
    find_conflict_of_interest_v2,
    find_conflict_of_interest_v3,
    find_conflict_of_interest_v4,
    find_conflict_of_interest_v5,
)

# ─────────────────────────────
# v1 – High Recall: any COI cue
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive PubMed / OHDSI-like examples
        ("The authors disclosed no conflicts of interest.", True, "v1_pos_disclosed_no_conflicts"),
        ("Competing interests are reported in the appendix.", True, "v1_pos_competing_interests"),
        ("Conflict of interest statement: none declared.", True, "v1_pos_conflict_statement"),

        # Trap / negatives
        ("This study had conflicting evidence regarding outcomes.", False, "v1_trap_conflicting_evidence"),
        ("The risk conflicts with prior assumptions.", False, "v1_trap_conflicts_with"),
        ("No disclosures were available from the database.", False, "v1_trap_nonfinancial_disclosure"),
    ]
)
def test_find_conflict_of_interest_v1(text, should_match, test_id):
    matches = find_conflict_of_interest_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"


# ─────────────────────────────
# v2 – Cue + disclosure verb nearby
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive
        ("J.D. reports no conflicts of interest related to this work.", True, "v2_pos_reports_conflicts"),
        ("The investigators declared competing interests regarding funding.", True, "v2_pos_declared_competing"),
        ("No conflicts of interest were stated by the authors.", True, "v2_pos_stated_conflicts"),

        # Trap examples
        ("Conflicts of interest are a concern in general science.", False, "v2_trap_generic_statement"),
        ("Competing interests section (not disclosed here).", False, "v2_trap_no_disclosure_verb"),
    ]
)
def test_find_conflict_of_interest_v2(text, should_match, test_id):
    matches = find_conflict_of_interest_v2(text)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"


# ─────────────────────────────
# v3 – Inside Conflict-of-Interest heading block
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive
        ("Conflicts of Interest:\nThe authors disclose consultancy fees from Pfizer.", True, "v3_pos_heading_conflicts"),
        ("Competing Interests:\nNo competing interests declared.", True, "v3_pos_heading_competing"),

        # Negative
        ("Methods:\nConflicts of interest were not assessed.", False, "v3_neg_wrong_section"),
        ("Discussion:\nThe authors disclose limitations.", False, "v3_neg_heading_not_coi"),
    ]
)
def test_find_conflict_of_interest_v3(text, should_match, test_id):
    matches = find_conflict_of_interest_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"


# ─────────────────────────────
# v4 – Cue + verb + company/negation
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive
        ("Dr. Smith disclosed honoraria from Novartis; others report no conflicts of interest.", True, "v4_pos_disclosed_company"),
        ("The authors declared no competing interests.", True, "v4_pos_declared_no_competing"),

        # Negative
        ("The authors reported conflicts of interest but did not name companies.", False, "v4_neg_missing_company_or_no_phrase"),
        ("Competing interests were mentioned, but no declaration was made.", False, "v4_neg_missing_verb"),
    ]
)
def test_find_conflict_of_interest_v4(text, should_match, test_id):
    matches = find_conflict_of_interest_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"


# ─────────────────────────────
# v5 – Tight template match
# ─────────────────────────────

@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        # Positive
        ("The authors declare no competing interests.", True, "v5_pos_exact_template"),
        ("Authors declare no competing interests.", True, "v5_pos_short_template"),

        # Negative
        ("The authors declare no conflicts of interest related to this work.", False, "v5_neg_conflicts_variation"),
        ("No competing interests were disclosed.", False, "v5_neg_wrong_wording"),
    ]
)
def test_find_conflict_of_interest_v5(text, should_match, test_id):
    matches = find_conflict_of_interest_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
