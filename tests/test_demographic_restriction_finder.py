"""Smoke tests for demographic_restriction_finder variants."""
from pyregularexpression.demographic_restriction_finder import DEMOGRAPHIC_RESTRICTION_FINDERS

examples = {
    "hit_age_gate": "Participants had to be at least 18 years to be eligible.",
    "hit_gender_gate": "Only females aged 50–70 years were included in the study.",
    "hit_heading_block": "Eligibility:\nAdults aged >=18 years\n",
    "miss_mean_age": "The average age was 45 years.",
    "miss_descriptive_gender": "Among participants, 60% were women.",
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt.strip()}")
    for name, fn in DEMOGRAPHIC_RESTRICTION_FINDERS.items():
        print(f" {name}: {fn(txt)}")
