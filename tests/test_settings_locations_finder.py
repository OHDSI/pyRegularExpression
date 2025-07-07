"""Smoke tests for eligibility_criteria_finder variants."""
from pyregularexpression.eligibility_criteria_finder import ELIGIBILITY_CRITERIA_FINDERS

examples = {
    "hit_combo": "Adults 18–65 with diabetes were eligible; prior insulin use was an exclusion criterion.",
    "hit_incl": "Eligible patients were required to be male and diagnosed with COPD.",
    "miss_diag": "We applied standard diagnostic criteria to confirm diabetes.",
    "miss_analysis": "Eligible datasets were included in the analysis."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in ELIGIBILITY_CRITERIA_FINDERS.items():
        print(f" {name}: {fn(txt)}")
