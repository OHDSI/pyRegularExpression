"""Smoke tests for competing_risk_analysis_finder."""
from pyregularexpression.competing_risk_analysis_finder import COMPETING_RISK_ANALYSIS_FINDERS

examples = {
    "hit_finegray": "We fitted Fine-Gray models to estimate sHRs for competing risk of death vs transplant.",
    "hit_shr": "Sub-hazard ratio (sHR) was estimated using a competing risk model.",
    "miss_competition": "There is high competition for resources in the ICU setting.",
    "miss_regular": "Risk of fracture was compared between groups using Cox regression."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in COMPETING_RISK_ANALYSIS_FINDERS.items():
        print(f" {name}: {fn(txt)}")
