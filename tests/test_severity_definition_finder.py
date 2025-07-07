
"""Smoke tests for severity_definition_finder variants."""
from pyregularexpression.severity_definition_finder import SEVERITY_DEFINITION_FINDERS

examples = {
    "hit_defined": "Severity was defined as IV antibiotics or hospital admission.",
    "hit_list": "Disease was classified as mild, moderate, severe according to clinical score.",
    "miss_descriptive": "Several patients had severe disease.",
    "miss_no_threshold": "The infection was considered moderate in many cases."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in SEVERITY_DEFINITION_FINDERS.items():
        print(f" {name}: {fn(txt)}")
