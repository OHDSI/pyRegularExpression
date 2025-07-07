"""Smoke tests for outcome_endpoints_finder variants."""
from pyregularexpression.outcome_endpoints_finder import OUTCOME_ENDPOINTS_FINDERS

examples = {
    "hit_primary_secondary": "Primary outcome was progression-free survival at 12 months; secondary outcomes included overall survival.",
    "hit_defined": "The primary endpoint was defined as HbA1c reduction measured at 24 weeks.",
    "miss_result": "The outcome of the procedure was successful in most cases.",
    "miss_implicit": "We evaluated various parameters during follow-up."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in OUTCOME_ENDPOINTS_FINDERS.items():
        print(f" {name}: {fn(txt)}")
