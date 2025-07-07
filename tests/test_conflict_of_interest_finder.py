"""Smoke tests for conflict_of_interest_finder."""
from pyregularexpression.conflict_of_interest_finder import CONFLICT_OF_INTEREST_FINDERS

examples = {
    "hit_positive": "J.D. reports advisory fees from PharmaCo; others declare no conflicts of interest.",
    "hit_negative": "The authors declare no competing interests.",
    "miss_conflict_word": "This is a matter of conflicting evidence and interpretation.",
    "miss_none": "Funding was provided by NIH R01."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in CONFLICT_OF_INTEREST_FINDERS.items():
        print(f" {name}: {fn(txt)}")
