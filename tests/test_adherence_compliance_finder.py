"""Smoke tests for adherence_compliance_finder."""
from pyregularexpression.adherence_compliance_finder import ADHERENCE_COMPLIANCE_FINDERS

examples = {
    "hit_pdc": "Adherence was defined as PDC ≥ 0.8 over 12 months.",
    "hit_mpr": "We calculated medication possession ratio (MPR) for each patient.",
    "miss_guidelines": "Adherence to guidelines was encouraged.",
    "miss_no_metric": "We encouraged adherence through counseling sessions."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in ADHERENCE_COMPLIANCE_FINDERS.items():
        print(f" {name}: {fn(txt)}")
