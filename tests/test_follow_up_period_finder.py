
"""Smoke tests for follow_up_period_finder variants."""
from pyregularexpression.follow_up_period_finder import FOLLOW_UP_PERIOD_FINDERS

examples = {
    "hit_median": "Median follow-up was 5 years.",
    "hit_followed_for": "Participants were followed for 24 months after index.",
    "miss_visit": "All patients attended follow-up visits at 3 months.",
    "miss_calendar": "The study observation period was from 2010 to 2020."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in FOLLOW_UP_PERIOD_FINDERS.items():
        print(f" {name}: {fn(txt)}")
