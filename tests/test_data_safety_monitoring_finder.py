"""Smoke tests for data_safety_monitoring_finder."""
from pyregularexpression.data_safety_monitoring_finder import DATA_SAFETY_MONITORING_FINDERS

examples = {
    "hit_dsm": "An independent DSMB met quarterly to review adverse events.",
    "hit_dmc": "The Data Monitoring Committee reviewed safety data annually.",
    "miss_monitor": "We monitored safety parameters weekly.",
    "miss_quality": "Data safety sheets were completed for each patient."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in DATA_SAFETY_MONITORING_FINDERS.items():
        print(f" {name}: {fn(txt)}")
