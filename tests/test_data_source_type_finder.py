
"""Smoke tests for data_source_type_finder variants."""
from pyregularexpression.data_source_type_finder import DATA_SOURCE_TYPE_FINDERS

examples = {
    "hit_claims": "We used nationwide insurance claims data from 2005 to 2015.",
    "hit_ehr": "An EHR-derived database was analyzed.",
    "miss_generic": "Data were compiled for analysis.",
    "miss_software": "SQL database software was utilized."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in DATA_SOURCE_TYPE_FINDERS.items():
        print(f" {name}: {fn(txt)}")
