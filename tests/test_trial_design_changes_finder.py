"""Smoke tests for trial_design_changes_finder variants."""
from pyregularexpression.trial_design_changes_finder import TRIAL_DESIGN_CHANGES_FINDERS

examples = {
    "hit_amend": "Three months into the trial, the protocol was amended to increase dosage due to safety concerns.",
    "hit_unplanned": "During the study, unplanned adjustments were made to the inclusion criteria.",
    "miss_pretrial": "Before enrollment began, we made changes to the inclusion criteria.",
    "miss_results": "We observed changes in blood pressure over time."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in TRIAL_DESIGN_CHANGES_FINDERS.items():
        print(f" {name}: {fn(txt)}")
