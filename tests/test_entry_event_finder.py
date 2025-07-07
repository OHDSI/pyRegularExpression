"""Smoke tests for entry_event_finder variants."""
from pyregularexpression.entry_event_finder import ENTRY_EVENT_FINDERS

examples = {
    "hit_first_mi": "Entry event was first myocardial infarction between 2010 and 2015.",
    "hit_eligible_hosp": "Patients were eligible upon hospitalization for heart failure.",
    "miss_followup_mi": "Patients experienced myocardial infarctions during follow‑up.",
    "miss_data_entry": "The study relied on data entry by clinicians.",
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in ENTRY_EVENT_FINDERS.items():
        print(f" {name}: {fn(txt)}")
