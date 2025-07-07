
"""Smoke tests for study_design_finder variants."""
from pyregularexpression.study_design_finder import STUDY_DESIGN_FINDERS

examples = {
    "hit_retrospective": "This was a retrospective cohort study using registry data.",
    "hit_rct": "The trial was a randomized controlled trial of drug X.",
    "miss_bias": "The study was designed to minimize bias.",
    "miss_other": "Random allocation was performed."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in STUDY_DESIGN_FINDERS.items():
        print(f" {name}: {fn(txt)}")
