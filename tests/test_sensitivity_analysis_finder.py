
"""Smoke tests for sensitivity_analysis_finder variants."""
from pyregularexpression.sensitivity_analysis_finder import SENSITIVITY_ANALYSIS_FINDERS

examples = {
    "hit_excluding": "Excluding switchers in sensitivity analysis did not change results.",
    "hit_performed": "Sensitivity analyses were performed by varying the exposure window.",
    "miss_assay": "Assay sensitivity was 95 %.",
    "miss_subgroup": "A subgroup analysis was conducted in females."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in SENSITIVITY_ANALYSIS_FINDERS.items():
        print(f" {name}: {fn(txt)}")
