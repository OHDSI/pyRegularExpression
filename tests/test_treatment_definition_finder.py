
"""Smoke tests for treatment_definition_finder variants."""
from pyregularexpression.treatment_definition_finder import TREATMENT_DEFINITION_FINDERS

examples = {
    "hit_drug": "The treatment group received Drug X 10 mg daily × 12 weeks.",
    "hit_intervention": "Intervention consisted of 3 IU/kg every week for 8 weeks.",
    "miss_if_needed": "Patients were treated with Drug X if needed.",
    "miss_outcome": "Outcome of interest was time to first retreatment."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in TREATMENT_DEFINITION_FINDERS.items():
        print(f" {name}: {fn(txt)}")
