
"""Smoke tests for comparator_cohort_finder variants."""
from pyregularexpression.comparator_cohort_finder import COMPARATOR_COHORT_FINDERS

examples = {
    "hit_matched": "A matched unexposed cohort served as comparator.",
    "hit_control_group": "The control group comprised patients receiving placebo.",
    "miss_benchmark": "Results were compared to national benchmarks.",
    "miss_device": "Device comparator readings were recorded."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in COMPARATOR_COHORT_FINDERS.items():
        print(f" {name}: {fn(txt)}")
