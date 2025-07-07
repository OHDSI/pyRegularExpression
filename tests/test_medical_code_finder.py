"""Simple smoke tests / demo for medical_code_finder variants."""
from pyregularexpression.medical_code_finder import MEDICAL_CODE_FINDERS

examples = {
    "good_hit": "Hypertension identified with ICD-10 code I10.",
    "good_cpt": "Patients with CPT code 99213 were included.",
    "generic_programming": "We coded the survey responses for analysis.",
    "generic_code_250": "We used code 250.00 for labeling.",
    "heading_block": "Diagnosis Codes:\nE11\nI10",
}

for label, text in examples.items():
    print(f"\n=== {label} ===\n{text}")
    for name, fn in MEDICAL_CODE_FINDERS.items():
        print(f" {name}: {fn(text)}")
