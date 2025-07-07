"""Smoke tests for generalizability_finder."""
from pyregularexpression.generalizability_finder import GENERALIZABILITY_FINDERS

examples = {
    "hit_findings": "Findings may not generalize to older adults or women.",
    "hit_external": "The external validity is limited; results apply only to tertiary care centers.",
    "miss_model": "Our machine-learning model is generalizable to other datasets.",
    "miss_noqual": "These results are encouraging."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in GENERALIZABILITY_FINDERS.items():
        print(f" {name}: {fn(txt)}")
