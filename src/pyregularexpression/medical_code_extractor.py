# In src/pyregularexpression/medical_code_extractor.py

import re

'''
Extract medical codes from the given text.
    For this example, we're using a simple regex pattern to simulate medical code extraction.
    
    Supported Code Systems:
    - ICD-10-CM: Diagnosis codes (e.g., "N17.9", "U07.1", "J09.X1")
    - ICD-9-CM: Legacy diagnosis codes (e.g., "250.00", "V12.2", "E999.1")
    - CPT: Procedure codes with optional modifiers (e.g., "99213", "99213-25")
    - LOINC: Lab codes (e.g., "718-7", "2951-2")
    - SNOMED CT / RxNorm: Numeric identifiers (e.g., "44054006", "1049223")
    - ATC: Drug codes (e.g., "A10BA02", "J01CA04", "C09AA05")
'''

medical_code_pattern = {
    "ICD-10-CM": re.compile(r"\b[A-Z]\d{2}\.\d{1,4}\b"),
    "ICD-10 with alphanumeric subcode": re.compile(r"\b[A-Z]\d{2}\.[A-Z]\d{1,3}\b"),
    "ICD-9-CM numeric": re.compile(r"\b\d{3}\.\d{1,2}\b"),
    "ICD-9-CM V/E codes": re.compile(r"\b[VE]\d{3}\.\d{1,2}\b"),
    "CPT": re.compile(r"\b\d{5}(?:-\d{2})?\b"),
    "LOINC": re.compile(r"\b\d{3,5}-\d\b"),
    "SNOMED CT or RxNorm": re.compile(r"\b\d{6,9}\b"),
    "ATC": re.compile(r"\b[A-Z]\d{2}[A-Z]{2}\d{2}\b")
}

def extract_medical_codes(text: str):
    matches = []
    for pattern in medical_code_pattern.values():
        for match in pattern.finditer(text):
            matches.append((match.start(), match.group()))
    
    # Sort by position in text
    matches.sort()
    
    return [code for _, code in matches]





    
