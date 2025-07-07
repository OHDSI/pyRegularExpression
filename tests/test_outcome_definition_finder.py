
"""Smoke tests for outcome_definition_finder variants."""
from pyregularexpression.outcome_definition_finder import OUTCOME_DEFINITION_FINDERS

examples = {
    "hit_primary": "Primary outcome: readmission within 30 days.",
    "hit_defined": "The endpoint was defined as all-cause death.",
    "miss_list": "Outcomes were positive overall.",
    "miss_ascertain": "Outcomes were ascertained via hospital records."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in OUTCOME_DEFINITION_FINDERS.items():
        print(f" {name}: {fn(txt)}")
