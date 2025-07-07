"""Smoke tests for objective_hypothesis_finder variants."""
from pyregularexpression.objective_hypothesis_finder import OBJECTIVE_HYPOTHESIS_FINDERS

examples = {
    "hit_objective": "The objective of this study was to assess the impact of diet on blood pressure.",
    "hit_hypothesis": "We hypothesized that higher sugar intake increases BMI.",
    "miss_measurement": "Objective measurements were obtained using a calibrated scale.",
    "miss_other_study": "The aim of the earlier trial was different."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in OBJECTIVE_HYPOTHESIS_FINDERS.items():
        print(f" {name}: {fn(txt)}")
