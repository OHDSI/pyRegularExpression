"""Smoke tests for losses_exclusion_finder."""
from pyregularexpression.losses_exclusion_finder import LOSSES_EXCLUSION_FINDERS

examples = {
    "hit_full": "During follow-up, 5 lost to follow-up, 2 withdrew due to side effects.",
    "hit_analysis": "Excluded from analysis (n = 4) because of missing data.",
    "miss_screen": "15 excluded during screening for ineligibility.",
    "miss_samples": "Lost samples were excluded from laboratory analysis."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in LOSSES_EXCLUSION_FINDERS.items():
        print(f" {name}: {fn(txt)}")
