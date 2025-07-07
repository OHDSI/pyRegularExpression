"""Smoke tests for subgroup_analysis_finder."""
from pyregularexpression.subgroup_analysis_finder import SUBGROUP_ANALYSIS_FINDERS

examples = {
    "hit_interaction": "Subgroup analyses showed stronger effect in women <50 y (P-interaction = 0.02).",
    "hit_effectmod": "We tested for effect modification by age and sex.",
    "miss_baseline": "Baseline subgroup of diabetics was older.",
    "miss_none": "Primary analysis included all participants."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in SUBGROUP_ANALYSIS_FINDERS.items():
        print(f" {name}: {fn(txt)}")
