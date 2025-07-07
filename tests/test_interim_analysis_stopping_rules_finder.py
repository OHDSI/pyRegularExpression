"""Smoke tests for interim_analysis_stopping_rules finder."""
from pyregularexpression.interim_analysis_stopping_rules_finder import INTERIM_ANALYSIS_STOPPING_RULES_FINDERS

examples = {
    "hit_boundary": "Interim analysis at 6 months with O’Brien-Fleming boundary p < 0.001.",
    "hit_plan": "A stopping rule for futility was specified, and the DSMB could terminate early.",
    "miss_interim_results": "Interim results from another study suggested changes.",
    "miss_other": "We planned final analysis after all data collected."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in INTERIM_ANALYSIS_STOPPING_RULES_FINDERS.items():
        print(f" {name}: {fn(txt)}")
