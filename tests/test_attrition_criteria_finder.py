
"""Smoke tests for attrition_criteria_finder variants."""
from pyregularexpression.attrition_criteria_finder import ATTRITION_CRITERIA_FINDERS

examples = {
    "hit_lost": "Ten participants (5 %) were lost to follow-up during the study.",
    "hit_withdrew": "Five patients withdrew consent during follow-up.",
    "miss_screen_failure": "Screen failures excluded before randomization.",
    "miss_exit": "Participants were censored at death or transplant."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in ATTRITION_CRITERIA_FINDERS.items():
        print(f" {name}: {fn(txt)}")
