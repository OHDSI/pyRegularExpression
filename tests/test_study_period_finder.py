
"""Smoke tests for study_period_finder variants."""
from pyregularexpression.study_period_finder import STUDY_PERIOD_FINDERS

examples = {
    "hit_study": "Study period: Jan 2015 – Dec 2019.",
    "hit_between": "Data were collected between 2000 and 2005.",
    "miss_follow": "Patients were followed from 2015 to 2019 individually.",
    "miss_unrelated": "Baseline characteristics were evaluated in 2018."
}

for label, sentence in examples.items():
    print(f"\n=== {label} ===\n{sentence}")
    for name, fn in STUDY_PERIOD_FINDERS.items():
        print(f" {name}: {fn(sentence)}")
