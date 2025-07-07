"""Smoke tests for statistical_analysis_additional_method_finder."""
from pyregularexpression.statistical_analysis_additional_method_finder import STATISTICAL_ANALYSIS_ADDITIONAL_METHOD_FINDERS

examples = {
    "hit_secondary": "Secondary outcomes were analysed using logistic regression, and age subgroups examined.",
    "hit_posthoc": "Post-hoc subgroup analysis was modelled with Cox regression.",
    "miss_primary": "Primary endpoint analysed with mixed-effects model.",
    "miss_result": "Secondary outcomes were significant (p < 0.05)."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in STATISTICAL_ANALYSIS_ADDITIONAL_METHOD_FINDERS.items():
        print(f" {name}: {fn(txt)}")
