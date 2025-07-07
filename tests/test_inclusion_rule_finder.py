
"""Smoke tests for inclusion_rule_finder variants."""
from pyregularexpression.inclusion_rule_finder import INCLUSION_RULE_FINDERS

examples = {
    "hit_colon_list": "Inclusion criteria: biopsy-confirmed cancer, age 30-65.",
    "hit_eligible_if": "Patients were eligible if they had at least one prescription for metformin.",
    "miss_included_patients": "Our study included patients with cancer.",
    "miss_simple_fact": "We report inclusion of baseline covariates."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in INCLUSION_RULE_FINDERS.items():
        print(f" {name}: {fn(txt)}")
