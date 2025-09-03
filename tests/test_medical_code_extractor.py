# In tests/test_medical_code_extractor.py

import pytest
from pyregularexpression.medical_code_extractor import extract_medical_codes

@pytest.mark.parametrize(
    "text, expected_codes, test_id",
    [
        #ICD-10 valid examples
        ("Patient diagnosed with E11.9 and J09.X1.", ["E11.9", "J09.X1"], "valid_icd10_codes"),

        #ICD-like codes without dot (should not match)
        ("Study mentions codes A01 and B23.", [], "invalid_icd10_no_dot"),

        #ICD-9-CM numeric + V/E codes
        ("Older diagnosis used 250.00 and V12.2, also E999.1.", ["250.00", "V12.2", "E999.1"], "valid_icd9_codes"),

        #CPT codes (5-digit + optional modifier)
        ("Billed procedures include 99213 and 99213-25.", ["99213", "99213-25"], "valid_cpt_codes"),

        #Invalid CPT (not 5-digit)
        ("Old procedure code 1234 was outdated.", [], "invalid_cpt_too_short"),

        #SNOMED CT + RxNorm (numeric)
        ("SNOMED 44054006, RxNorm 1049223 and 313782 were referenced.", ["44054006", "1049223", "313782"], "valid_snomed_rxnorm"),

        #LOINC examples
        ("Lab tests included LOINC 4548-4 and 2951-2.", ["4548-4", "2951-2"], "valid_loinc"),

        #ATC codes
        ("Prescribed drugs: A10BA02, J01CA04, and C09AA05.", ["A10BA02", "J01CA04", "C09AA05"], "valid_atc"),

        #Short unrelated numbers
        ("Room 123 was booked, reference ID 4567 used.", [], "invalid_short_numbers"),

        #Mixed valid and invalid
        ("Used E11.9 and CPT 99214, but A01 is not valid.", ["E11.9", "99214"], "mixed_valid_invalid"),

        #Lowercase codes (should not match per strict pattern)
        ("Codes like e11.9 or j09.x1 were mentioned.", [], "invalid_lowercase_codes"),

        #Multiple types together
        ("This case used ICD10 N17.9, CPT 93000, ATC A10BA02 and SNOMED 195967001.", ["N17.9", "93000", "A10BA02", "195967001"], "all_valid_mixed"),

        # Boundary & punctuation cases
        ("E11.9, was noted.", ["E11.9"], "icd10_trailing_comma"),
        ("(250.00)", ["250.00"], "icd9_surrounded_parentheses"),
        ("[99213-25]", ["99213-25"], "cpt_in_brackets"),

        # Mixed/adjacent codes
        ("E11.9J09.X1", ["E11.9", "J09.X1"], "adjacent_icd10_codes"),

        # Overlapping numeric patterns
        ("SNOMED 123456789012", ["123456789012"], "long_snomed_only"),
        ("Mixed 12345 99213", ["99213"], "cpt_vs_snomed_priority"),

        # False‑positives on common text
        ("In 2020, reference ID 1234 was logged.", [], "year_and_short_number"),
        ("Outlier code 999.99 should be ignored.", [], "invalid_icd9_out_of_range"),

        # Case‑sensitivity noise
        ("Lower e11.9 and Jn17.9", [], "invalid_mixed_lowercase"),

        # Duplicate suppression
        ("Codes E11.9, E11.9, J09.X1", ["E11.9", "E11.9", "J09.X1"], "duplicate_codes"),

        # Edge‑of‑limits for each system
        ("Test A12.3456 and 123.45 and 1-1", ["A12.3456", "123.45", "1-1"], "max_length_codes")
    ]
)
def test_extract_medical_codes(text, expected_codes, test_id):
    result = extract_medical_codes(text)
    assert result == expected_codes, f"{test_id} failed: got {result}, expected {expected_codes}"


def test_extract_medical_codes_unique():
    text = "Codes E11.9, E11.9, J09.X1"
    expected_codes = ["E11.9", "J09.X1"]
    result = extract_medical_codes(text, unique=True)
    assert result == expected_codes, "unique=True failed"


def test_extract_medical_codes_offsets():
    text = "Patient diagnosed with E11.9 and J09.X1."
    expected_offsets = [(23, 28, 'E11.9'), (33, 39, 'J09.X1')]
    result = extract_medical_codes(text, return_offsets=True)
    assert result == expected_offsets, "return_offsets=True failed"


def test_extract_medical_codes_unique_and_offsets():
    text = "Codes E11.9, E11.9, J09.X1"
    expected_offsets = [(6, 11, 'E11.9'), (20, 26, 'J09.X1')]
    result = extract_medical_codes(text, unique=True, return_offsets=True)
    assert result == expected_offsets, "unique=True and return_offsets=True failed"
