"""Smoke tests for interventions_finder variants."""
from pyregularexpression.interventions_finder import INTERVENTIONS_FINDERS

examples = {
    "hit_pair": "Experimental arm received a 12-week aerobic program; control arm continued routine activities.",
    "hit_drug": "The treatment group was treated with Drug X 50 mg daily while the placebo group received matching capsules.",
    "miss_policy": "Government health interventions during the year may have influenced outcomes.",
    "miss_generic": "We discussed various intervention strategies in healthcare."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in INTERVENTIONS_FINDERS.items():
        print(f" {name}: {fn(txt)}")
