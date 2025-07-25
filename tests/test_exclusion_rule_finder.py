
"""Smoke tests for exclusion_rule_finder variants."""
from pyregularexpression.exclusion_rule_finder import EXCLUSION_RULE_FINDERS

examples = {
    "hit_colon_list": "Exclusion criteria: prior heart surgery or pregnancy.",
    "hit_excluded_if": "Participants were excluded if they had chronic kidney disease.",
    "miss_dropout": "Three patients withdrew consent after enrollment.",
    "miss_analysis": "We excluded variables with >10% missing data."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in EXCLUSION_RULE_FINDERS.items():
        print(f" {name}: {fn(txt)}")
