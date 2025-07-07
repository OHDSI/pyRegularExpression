"""Smoke tests for randomization_type_restriction_finder."""
from pyregularexpression.randomization_type_restriction_finder import RANDOMIZATION_TYPE_RESTRICTION_FINDERS

examples = {
    "hit_full": "Randomized 2:1 to drug vs placebo using permuted blocks of six, stratified by site.",
    "hit_block": "Patients were assigned by block randomization (blocks of 4).",
    "miss_simple": "Patients were randomly assigned to two groups.",
    "miss_sampling": "We used random sampling to select survey respondents."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in RANDOMIZATION_TYPE_RESTRICTION_FINDERS.items():
        print(f" {name}: {fn(txt)}")
