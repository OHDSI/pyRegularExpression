# tests/test_med_cohort.py
import re
import pytest
from pyregularexpression import (
    extract_medical_codes,
    find_cohort_logic,
    MEDICAL_CODE_RE,
    COHORT_LOGIC_RE,
)

# ──────────────────────────────────────────────────────────────
# 1.  Medical-code extraction
# ──────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "text,expected",
    [
        pytest.param(
            "Diagnosed with ICD-10 E11.9 and CPT 99213.",
            ["E11.9", "99213"],
            id="icd10_and_cpt",
        ),
        pytest.param(
            "RXCUI: 12345678 maps to ATC A10BA02.",
            ["12345678", "A10BA02"],
            id="rxcui_and_atc",
        ),
        pytest.param(
            "NDC 0002-8215-01 dispensed; duplicate NDC 0002821501 noted.",
            ["0002-8215-01", "0002821501"],
            id="ndc_hyphen_and_plain",
        ),
    ],
)
def test_extract_medical_codes_basic(text, expected):
    assert extract_medical_codes(text) == expected


def test_extract_medical_codes_offsets():
    txt = "SNOMED 44054006 recorded during visit."
    spans = extract_medical_codes(txt, return_offsets=True, unique=False)
    assert spans == [(7, 15, "44054006")]


def test_short_numeric_filtered():
    """Numeric ‘365’ should be ignored because it is a duration, not a code."""
    txt = "Patient required 365 days of observation."
    assert extract_medical_codes(txt) == []


# ──────────────────────────────────────────────────────────────
# 2.  Cohort-logic extraction
# ──────────────────────────────────────────────────────────────
def test_find_cohort_logic_basic():
    txt = (
        "We required 365 days of observation prior to the index date "
        "and excluded patients with CPT 99213."
    )
    snippets = find_cohort_logic(txt, return_offsets=False)
    # Expect at least the temporal window phrase and the code family
    assert any("prior to the index date" in s for s in snippets)
    assert any("CPT" in s for s in snippets)


# ──────────────────────────────────────────────────────────────
# 3.  Regex sanity checks (compile once, reuse)
# ──────────────────────────────────────────────────────────────
def test_regex_objects_can_be_reused():
    # Compiled patterns should match fresh copies of the same strings
    assert MEDICAL_CODE_RE.search("ICD10 E11.9")
    assert COHORT_LOGIC_RE.search(
        "Look-back period of 180 days prior to index with ICD-9 250.00."
    )
