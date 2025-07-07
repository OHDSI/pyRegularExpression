"""Smoke tests for index_date_finder variants."""
from pyregularexpression.index_date_finder import INDEX_DATE_FINDERS

examples = {
    "hit_defined": "Index date was defined as the first insulin prescription recorded.",
    "hit_equal": "Baseline date = first diagnosis of hypertension.",
    "miss_follow": "Patients were followed from the index date forward.",
    "miss_index_case": "The index case was reported in 2012."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in INDEX_DATE_FINDERS.items():
        print(f" {name}: {fn(txt)}")
