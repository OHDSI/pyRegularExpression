
"""Smoke tests for washout_period_finder variants."""
from pyregularexpression.washout_period_finder import WASHOUT_PERIOD_FINDERS

examples = {
    "hit_12m": "A 12-month washout period with no antihypertensives was required before index.",
    "hit_drug_free": "Participants were drug-free for 6 months prior to baseline.",
    "miss_side_effect": "Patients stopped meds due to side-effects.",
    "miss_lab_wash": "The protocol included a PBS wash step between incubations."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in WASHOUT_PERIOD_FINDERS.items():
        print(f" {name}: {fn(txt)}")
