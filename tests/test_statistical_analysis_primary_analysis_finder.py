"""Smoke tests for statistical_analysis_primary_analysis_finder."""
from pyregularexpression.statistical_analysis_primary_analysis_finder import STATISTICAL_ANALYSIS_PRIMARY_ANALYSIS_FINDERS

examples = {
    "hit_model": "Primary endpoint analysed with mixed-effects linear model adjusting for baseline covariates.",
    "hit_cox": "The primary outcome was assessed by Cox proportional hazards regression.",
    "miss_result": "The treatment reduced the primary outcome (p < 0.05).",
    "miss_secondary": "Secondary outcomes were analysed with similar methods."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in STATISTICAL_ANALYSIS_PRIMARY_ANALYSIS_FINDERS.items():
        print(f" {name}: {fn(txt)}")
