# tests/test_funding_statement_finder.py
"""
Complete test suite for funding_statement_finder.py.

This suite provides robust, comprehensive checks for v1 and v5, assuming their
core bugs have been fixed. It also includes lighter, representative checks for
v2, v3, and v4 to ensure their basic functionality.
"""

import pytest
from pyregularexpression.funding_statement_finder import (
    find_funding_statement_v1,
    find_funding_statement_v2,
    find_funding_statement_v3,
    find_funding_statement_v4,
    find_funding_statement_v5,
)

# ─────────────────────────────
# Robust Tests for v1 (High Recall, multi-agency, flexible wording)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("This work was supported by the National Institutes of Health under award R01 LM006910.", True, "v1_pos_supported_by_nih_r01"),
        ("The study was partially funded by the US Food and Drug Administration and the NLM.", True, "v1_pos_partially_funded_multiple_agencies"),
        ("We received funding from the NIH (grant number R01 HG006139).", True, "v1_pos_received_funding_grant"),
        ("Research was supported through funding by Janssen Research and Development, LLC.", True, "v1_pos_janssen_funded"),
        ("No external funding was received for this work.", True, "v1_pos_negative_declaration"),

        # Negative examples
        ("This study utilized the OMOP CDM and OHDSI tools.", False, "v1_neg_no_funding_info"),
        ("All code used is available at github.com/OHDSI.", False, "v1_neg_open_source_note"),
    ]
)
def test_find_funding_statement_v1_robust(text, should_match, test_id):
    matches = find_funding_statement_v1(text)
    assert bool(matches) == should_match, f"v1 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v2 (Cue + Support Verb Nearby)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("The study was funded by the US FDA and partially supported by NIH R01 grants.", True, "v2_pos_funded_and_supported"),
        ("Janssen provided research funding for this project.", True, "v2_pos_provided_funding"),
        ("This was made possible with grant support from the National Library of Medicine.", True, "v2_pos_grant_support_phrase"),

        # Negative examples
        ("NIH R01 LM006910 appears in the disclosures.", False, "v2_neg_grant_mentioned_but_no_cue"),
    ]
)
def test_find_funding_statement_v2_light(text, should_match, test_id):
    matches = find_funding_statement_v2(text)
    assert bool(matches) == should_match, f"v2 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v3 (Block Heading Match)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Funding:\nSupported by NIH grant R01 LM006910 and NSF IIS 1251151.", True, "v3_pos_funding_block_heading"),
        ("Financial Support:\nJanssen contributed to infrastructure funding.", True, "v3_pos_financial_support_block"),

        # Negative examples
        ("Acknowledgements:\nThanks to the reviewers and collaborators.", False, "v3_neg_ack_no_funding"),
    ]
)
def test_find_funding_statement_v3_light(text, should_match, test_id):
    matches = find_funding_statement_v3(text)
    assert bool(matches) == should_match, f"v3 failed for ID: {test_id}"


# ─────────────────────────────
# Lighter Tests for v4 (Cue + Grant/Agency Token in Window)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Funding was provided by the National Institutes of Health through grant R01 LM006910.", True, "v4_pos_funded_with_grant"),
        ("This project was funded by Janssen and supported by NIH R01 LM006910.", True, "v4_pos_combo_janssen_and_nih"),

        # Negative
        ("Support was internal only; no external funders participated.", False, "v4_neg_internal_support_only"),
    ]
)
def test_find_funding_statement_v4_light(text, should_match, test_id):
    matches = find_funding_statement_v4(text)
    assert bool(matches) == should_match, f"v4 failed for ID: {test_id}"


# ─────────────────────────────
# Robust Tests for v5 (Tight Template Matching)
# ─────────────────────────────
@pytest.mark.parametrize(
    "text, should_match, test_id",
    [
        ("Supported by NIH grant R01 LM006910.", True, "v5_pos_supported_by_exact_template"),
        ("Supported by NSF grant IIS 1251151 and NIH grant R01 HG006139.", True, "v5_pos_supported_multiple_grants"),
        ("This work was supported by a grant from the FDA (R01 LM006910).", False, "v5_neg_indirect_wording"),
        ("Funding provided via collaborative agreement with no grant number.", False, "v5_neg_missing_grant_number"),
    ]
)
def test_find_funding_statement_v5_robust(text, should_match, test_id):
    matches = find_funding_statement_v5(text)
    assert bool(matches) == should_match, f"v5 failed for ID: {test_id}"
