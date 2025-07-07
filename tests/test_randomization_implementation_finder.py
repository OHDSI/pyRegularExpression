"""Smoke tests for randomization_implementation_finder."""
from pyregularexpression.randomization_implementation_finder import RANDOMIZATION_IMPLEMENTATION_FINDERS

examples = {
    "hit_full": "Statistician generated the sequence; investigators enrolled participants; central web system assigned interventions.",
    "hit_partial": "An independent pharmacist generated the randomization list which was then used to assign groups.",
    "miss_treatment": "Surgeons implemented the treatment protocol.",
    "miss_other": "Randomization procedures were described elsewhere."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in RANDOMIZATION_IMPLEMENTATION_FINDERS.items():
        print(f" {name}: {fn(txt)}")
