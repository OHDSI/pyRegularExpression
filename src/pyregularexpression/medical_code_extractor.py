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

import re

medical_code_pattern = {
    "ICD-10-CM":     re.compile(r"\b[A-Z]\d{2}\.\d{1,4}\b"),
    "ICD-10 sub":    re.compile(r"\b[A-Z]\d{2}\.[A-Z]\d{1,3}\b"),
    "ICD-9 numeric": re.compile(r"\b\d{3}\.\d{1,2}\b"),
    "ICD-9 V/E":     re.compile(r"\b[VE]\d{3}\.\d{1,2}\b"),
    # Only CPT codes beginning with 9
    "CPT":           re.compile(r"\b9\d{4}(?:-\d{2})?\b"),
    "LOINC":         re.compile(r"\b\d{1,5}-\d\b"),
    "NDC":           re.compile(r"\b\d{4,5}-\d{3,4}-\d{1,2}\b"),
    "SNOMED":        re.compile(r"\b\d{6,18}\b"),
    "ATC":           re.compile(r"\b[A-Z]\d{2}[A-Z]{2}\d{2}\b"),
}

def extract_medical_codes(
    text: str, return_offsets: bool = False, unique: bool = False
):
    """
    Extract medical codes from text.
    Args:
        text: The text to search.
        return_offsets: If True, return (start, end) character offsets instead of the codes.
        unique: If True, return only unique codes.
    Returns:
        A list of strings (codes) or a list of tuples (offsets).
    """
    # split only ICD-10 adjacency
    text = re.sub(r"(?<=\.\d)(?=[A-Z])", " ", text)

    matches = []
    for system, pat in medical_code_pattern.items():
        for m in pat.finditer(text):
            code = m.group(0)

            # drop ICD‑9 > 999.9
            if system == "ICD-9 numeric" and float(code) > 999.9:
                continue

            # skip short SNOMED so CPT gets precedence
            if system == "SNOMED" and re.fullmatch(r"\d{5}", code):
                continue

            matches.append({"start": m.start(), "end": m.end(), "code": code})

    matches.sort(key=lambda x: x["start"])

    if unique:
        seen = set()
        unique_matches = []
        for match in matches:
            if match["code"] not in seen:
                seen.add(match["code"])
                unique_matches.append(match)
        matches = unique_matches

    if return_offsets:
        return [(match["start"], match["end"], match["code"]) for match in matches]
    else:
        return [match["code"] for match in matches]
