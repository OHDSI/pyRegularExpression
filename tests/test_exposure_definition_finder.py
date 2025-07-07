
"""Smoke tests for exposure_definition_finder variants."""
from pyregularexpression.exposure_definition_finder import EXPOSURE_DEFINITION_FINDERS

examples = {
    "hit_defined": "Exposure was defined as ≥2 prescriptions of drug X within 30 days.",
    "hit_equals": "Exposure = use of drug Y at least 3 times prior to index.",
    "miss_generic": "We examined radiation exposure in the cohort.",
    "miss_trial": "Participants were randomised to the exposure group."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in EXPOSURE_DEFINITION_FINDERS.items():
        print(f" {name}: {fn(txt)}")
