"""Smoke tests for blinding_masking_finder."""
from pyregularexpression.blinding_masking_finder import BLINDING_MASKING_FINDERS

examples = {
    "hit_double": "Double-blind study: participants and assessors were unaware of assignments.",
    "hit_single": "Single-blind trial where participants were masked.",
    "miss_review": "Investigators conducted a blinded review of pathology reports.",
    "miss_open": "The study was open label with no blinding."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in BLINDING_MASKING_FINDERS.items():
        print(f" {name}: {fn(txt)}")
