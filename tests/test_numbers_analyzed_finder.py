"""Smoke tests for numbers_analyzed_finder."""
from pyregularexpression.numbers_analyzed_finder import NUMBERS_ANALYZED_FINDERS

examples = {
    "hit_counts": "98 intervention and 102 control participants analysed (ITT).",
    "hit_n": "Participants included in analysis: n = 45 treatment, n = 50 control.",
    "miss_enrol": "A total of 200 participants were enrolled in the study.",
    "miss_randomized": "150 patients were randomized (75 per arm)."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in NUMBERS_ANALYZED_FINDERS.items():
        print(f" {name}: {fn(txt)}")
