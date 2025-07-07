"""Smoke tests for propensity_score_method_finder."""
from pyregularexpression.propensity_score_method_finder import PROPENSITY_SCORE_METHOD_FINDERS

examples = {
    "hit_full": "We estimated propensity scores via logistic regression and applied IPTW.",
    "hit_matching": "Patients were PS-matched 1:1 using nearest neighbour matching.",
    "miss_propensity_to": "Participants with a high propensity to exercise were included.",
    "miss_none": "Confounding was adjusted using multivariable regression."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in PROPENSITY_SCORE_METHOD_FINDERS.items():
        print(f" {name}: {fn(txt)}")
