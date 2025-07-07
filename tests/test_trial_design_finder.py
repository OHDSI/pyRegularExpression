"""Smoke tests for trial_design_finder variants."""
from pyregularexpression.trial_design_finder import TRIAL_DESIGN_FINDERS

examples = {
    "hit_rct": "We conducted a double-blind, placebo-controlled randomized trial in three hospitals.",
    "hit_cohort": "This was a prospective multicenter cohort study of 5,000 participants.",
    "miss_designing": "The trial was designed to minimize bias through careful methodology.",
    "miss_context": "Our design team developed the study interface."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in TRIAL_DESIGN_FINDERS.items():
        print(f" {name}: {fn(txt)}")
