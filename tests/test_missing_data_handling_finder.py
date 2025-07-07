"""Smoke tests for missing_data_handling_finder."""
from pyregularexpression.missing_data_handling_finder import MISSING_DATA_HANDLING_FINDERS

examples = {
    "hit_mice": "Missing covariates were imputed using chained equations (mice).",
    "hit_locf": "We applied last observation carried forward to handle missing outcomes.",
    "miss_report": "BMI was missing in 12 % of records.",
    "miss_none": "Data were complete for all variables."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in MISSING_DATA_HANDLING_FINDERS.items():
        print(f" {name}: {fn(txt)}")
