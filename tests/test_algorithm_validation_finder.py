
"""Smoke tests for algorithm_validation_finder variants."""
from pyregularexpression.algorithm_validation_finder import ALGORITHM_VALIDATION_FINDERS

examples = {
    "hit_metric": "Algorithm was validated against chart review; PPV 92 % and sensitivity 88 %.",
    "hit_accuracy": "Accuracy 0.89 (95 % CI) was achieved in external validation of the algorithm.",
    "miss_use": "We applied the algorithm to identify diabetic patients.",
    "miss_assay": "Assay sensitivity was 98 %."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in ALGORITHM_VALIDATION_FINDERS.items():
        print(f" {name}: {fn(txt)}")
