"""Smoke tests for risk_of_bias_assessment_finder."""
from pyregularexpression.risk_of_bias_assessment_finder import RISK_OF_BIAS_ASSESSMENT_FINDERS

examples = {
    "hit_tool": "Two reviewers rated risk of bias using the ROBINS-I framework.",
    "hit_quality": "Risk of bias was assessed with the Cochrane risk of bias tool, scoring studies as low or high.",
    "miss_discussion": "Selection bias may threaten validity in observational studies.",
    "miss_none": "The primary endpoint was mortality."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in RISK_OF_BIAS_ASSESSMENT_FINDERS.items():
        print(f" {name}: {fn(txt)}")
