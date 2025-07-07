"""Smoke tests for participant_flow_finder."""
from pyregularexpression.participant_flow_finder import PARTICIPANT_FLOW_FINDERS

examples = {
    "hit_full": "A total of 200 participants were randomized (100 treatment, 100 placebo); 180 completed follow-up.",
    "hit_simple": "Screened 250, excluded 30, 220 allocated to study arms.",
    "miss_total": "We recruited a total of 300 participants for the study.",
    "miss_general": "The participant flow diagram is shown in Figure 1."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in PARTICIPANT_FLOW_FINDERS.items():
        print(f" {name}: {fn(txt)}")
