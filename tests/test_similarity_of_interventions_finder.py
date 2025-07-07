"""Smoke tests for similarity_of_interventions_finder."""
from pyregularexpression.similarity_of_interventions_finder import SIMILARITY_OF_INTERVENTIONS_FINDERS

examples = {
    "hit_identical": "Control arm received placebo injection identical in appearance to active drug.",
    "hit_sham": "Patients in the control group underwent a sham procedure indistinguishable from the real surgery.",
    "miss_duration": "Both regimens were similar in duration and cost.",
    "miss_open": "This open‑label trial did not attempt to mask interventions."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in SIMILARITY_OF_INTERVENTIONS_FINDERS.items():
        print(f" {name}: {fn(txt)}")
