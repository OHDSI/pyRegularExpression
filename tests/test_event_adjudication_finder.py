"""Smoke tests for event_adjudication_finder."""
from pyregularexpression.event_adjudication_finder import EVENT_ADJUDICATION_FINDERS

examples = {
    "hit_cec": "All MI events were independently adjudicated by a blinded CEC.",
    "hit_committee": "A clinical events committee adjudicated suspected stroke endpoints.",
    "miss_physician": "Treatment decisions were adjudicated by the attending physician.",
    "miss_link": "We investigated the link between blood pressure and events."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in EVENT_ADJUDICATION_FINDERS.items():
        print(f" {name}: {fn(txt)}")
