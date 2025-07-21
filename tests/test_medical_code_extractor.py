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
        ("This case used ICD10 N17.9, CPT 93000, ATC A10BA02 and SNOMED 195967001.", ["N17.9", "93000", "A10BA02", "195967001"], "all_valid_mixed")
    ]
)
def test_extract_medical_codes(text, expected_codes, test_id):
    result = extract_medical_codes(text)
    assert result == expected_codes, f"{test_id} failed: got {result}, expected {expected_codes}"
    
