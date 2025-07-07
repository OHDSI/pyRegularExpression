"""Smoke tests for dose_response_analysis_finder."""
from pyregularexpression.dose_response_analysis_finder import DOSE_RESPONSE_ANALYSIS_FINDERS

examples = {
    "hit_ptrend": "A clear dose-response was observed (p-trend < 0.001).",
    "hit_spline": "We fitted restricted cubic spline models to evaluate dose–effect.",
    "miss_doses": "Patients received two possible doses (5 or 10 mg).",
    "miss_none": "Outcome was compared between treated and untreated groups."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in DOSE_RESPONSE_ANALYSIS_FINDERS.items():
        print(f" {name}: {fn(txt)}")
