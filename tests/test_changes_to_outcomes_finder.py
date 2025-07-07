
"""Smoke tests for changes_to_outcomes_finder variants."""
from pyregularexpression.changes_to_outcomes_finder import CHANGES_TO_OUTCOMES_FINDERS

examples = {
    "hit_change": "Due to low event rate, the primary outcome was changed from OS to DFS midway through the study.",
    "hit_added": "After the trial began, we added a new secondary outcome to assess quality of life.",
    "miss_value": "The intervention led to significant changes in patient outcomes.",
    "miss_baseline": "The original protocol listed the primary outcome as overall survival."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in CHANGES_TO_OUTCOMES_FINDERS.items():
        print(f" {name}: {fn(txt)}")
