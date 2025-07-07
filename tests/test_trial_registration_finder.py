"""Smoke tests for trial_registration_finder."""
from pyregularexpression.trial_registration_finder import TRIAL_REGISTRATION_FINDERS

examples = {
    "hit_nct": "This trial was prospectively registered at ClinicalTrials.gov (NCT04567890).",
    "hit_isrctn": "Trial registration: ISRCTN12345678.",
    "miss_irb": "Protocol was filed with the IRB.",
    "miss_observ": "Our observational study was recorded in a local registry."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in TRIAL_REGISTRATION_FINDERS.items():
        print(f" {name}: {fn(txt)}")
