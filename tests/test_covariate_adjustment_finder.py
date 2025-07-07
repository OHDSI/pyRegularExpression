
"""Smoke tests for covariate_adjustment_finder variants."""
from pyregularexpression.covariate_adjustment_finder import COVARIATE_ADJUSTMENT_FINDERS

examples = {
    "hit_adjusted": "Hazard ratios were adjusted for age, BMI, and smoking status.",
    "hit_multivariable": "A multivariable model including age and sex was fitted.",
    "miss_dose": "We adjusted medication dose based on therapeutic response.",
    "miss_baseline": "Baseline covariates included age, sex, and BMI."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in COVARIATE_ADJUSTMENT_FINDERS.items():
        print(f" {name}: {fn(txt)}")
