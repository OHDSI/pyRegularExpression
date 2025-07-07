"""Smoke tests for limitations_finder."""
from pyregularexpression.limitations_finder import LIMITATIONS_FINDERS

examples = {
    "hit_small": "Limitations include small sample and short follow-up.",
    "hit_bias": "We acknowledge potential bias and confounding in our study.",
    "miss_prev": "Limitations of previous studies were short follow-up.",
    "miss_none": "This study had no limitations."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in LIMITATIONS_FINDERS.items():
        print(f" {name}: {fn(txt)}")
