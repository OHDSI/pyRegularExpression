"""Smoke tests for data_linkage_method_finder."""
from pyregularexpression.data_linkage_method_finder import DATA_LINKAGE_METHOD_FINDERS

examples = {
    "hit_prob": "Hospital admissions were probabilistically linked to death-registry data using date of birth and NHS number.",
    "hit_det": "Records were deterministically matched on SSN and date of birth.",
    "miss_link": "We explored the link between obesity and asthma.",
    "miss_web": "See supplementary materials at the following web link."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in DATA_LINKAGE_METHOD_FINDERS.items():
        print(f" {name}: {fn(txt)}")
