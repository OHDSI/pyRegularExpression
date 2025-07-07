"""Smoke tests for recruitment_timeline_finder."""
from pyregularexpression.recruitment_timeline_finder import RECRUITMENT_TIMELINE_FINDERS

examples = {
    "hit_full": "Enrolled March 2015–July 2017; each followed 12 months.",
    "hit_simple": "Patients were recruited between 2000 and 2005 and followed for 2 years.",
    "miss_challenge": "Recruitment was challenging due to rare disease.",
    "miss_nodates": "The study period was long."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in RECRUITMENT_TIMELINE_FINDERS.items():
        print(f" {name}: {fn(txt)}")
