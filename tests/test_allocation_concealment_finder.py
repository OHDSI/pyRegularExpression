"""Smoke tests for allocation_concealment_finder."""
from pyregularexpression.allocation_concealment_finder import ALLOCATION_CONCEALMENT_FINDERS

examples = {
    "hit_envelopes": "Assignments in sequentially numbered opaque envelopes ensured allocation concealment.",
    "hit_central": "Central randomization via a web-based system concealed allocation.",
    "miss_blinding": "Treatment allocation was not revealed to outcome assessors.",
    "miss_other": "Patients were randomly allocated to treatment groups."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in ALLOCATION_CONCEALMENT_FINDERS.items():
        print(f" {name}: {fn(txt)}")
