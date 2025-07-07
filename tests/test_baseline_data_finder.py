"""Smoke tests for baseline_data_finder."""
from pyregularexpression.baseline_data_finder import BASELINE_DATA_FINDERS

examples = {
    "hit_vs": "Baseline characteristics: Mean age 54 vs 55, 60 % female in both groups.",
    "hit_table": "Table 1 lists baseline demographics with BMI 28.5 ± 4.2 and 45% smokers.",
    "miss_single": "Baseline tumor size recorded for each patient.",
    "miss_nocue": "Patients had similar age distributions."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in BASELINE_DATA_FINDERS.items():
        print(f" {name}: {fn(txt)}")
