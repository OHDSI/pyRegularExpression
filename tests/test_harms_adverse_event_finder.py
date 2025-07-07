"""Smoke tests for harms_adverse_event_finder."""
from pyregularexpression.harms_adverse_event_finder import HARMS_ADVERSE_EVENT_FINDERS

examples = {
    "hit_full": "15 % headaches in treatment vs 10 % placebo; no serious events.",
    "hit_numbers": "Adverse events: n = 12 in control group, n = 18 in intervention.",
    "miss_generic": "Treatment caused no harm to any participant.",
    "miss_nocount": "There were few mild side effects noted."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in HARMS_ADVERSE_EVENT_FINDERS.items():
        print(f" {name}: {fn(txt)}")
