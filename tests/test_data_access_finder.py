
"""Smoke tests for data_access_finder variants."""
from pyregularexpression.data_access_finder import DATA_ACCESS_FINDERS

examples = {
    "hit_request": "The dataset is available upon request with ethics committee approval.",
    "hit_repo": "Data are deposited in the Zenodo repository under accession XYZ123.",
    "miss_care": "We measured patients' access to care.",
    "miss_open_access": "This article is published in an open-access journal."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in DATA_ACCESS_FINDERS.items():
        print(f" {name}: {fn(txt)}")
