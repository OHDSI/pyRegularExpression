"""Smoke tests for exit_criterion_finder variants."""
from pyregularexpression.exit_criterion_finder import EXIT_CRITERION_FINDERS

examples = {
    "hit_followed_until": "Participants were followed until transplant, death, or 31 Dec 2020.",
    "hit_censored_at": "Patients were censored at first heart failure hospitalization.",
    "miss_study_end": "The study ended in 2018.",
    "miss_attrition": "Five individuals were lost to follow-up."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in EXIT_CRITERION_FINDERS.items():
        print(f" {name}: {fn(txt)}")
