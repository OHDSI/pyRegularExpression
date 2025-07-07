
"""Smoke tests for outcome_ascertainment_finder variants."""
from pyregularexpression.outcome_ascertainment_finder import OUTCOME_ASCERTAINMENT_FINDERS

examples = {
    "hit_verified": "Stroke events were verified via imaging.",
    "hit_confirmed": "Outcomes were confirmed by medical record review.",
    "miss_bias": "Ascertainment bias may affect interpretation.",
    "miss_primary": "Primary outcome was stroke."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in OUTCOME_ASCERTAINMENT_FINDERS.items():
        print(f" {name}: {fn(txt)}")
