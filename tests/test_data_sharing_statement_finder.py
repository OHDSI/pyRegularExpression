"""Smoke tests for data_sharing_statement_finder."""
from pyregularexpression.data_sharing_statement_finder import DATA_SHARING_STATEMENT_FINDERS

examples = {
    "hit_repo": "Individual participant data will be available in Dryad after publication.",
    "hit_request": "Data are available from the corresponding author upon reasonable request.",
    "miss_open": "We analyzed open‑access census data from 2010.",
    "miss_none": "No new data were created."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in DATA_SHARING_STATEMENT_FINDERS.items():
        print(f" {name}: {fn(txt)}")
