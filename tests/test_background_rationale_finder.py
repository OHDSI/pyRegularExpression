
"""Smoke tests for ethics_approval_finder variants."""
from pyregularexpression.ethics_approval_finder import ETHICS_APPROVAL_FINDERS

examples = {
    "hit_irb": "Protocol approved by XYZ IRB #2021-45; informed consent obtained from all participants.",
    "hit_waiver": "The institutional review board waived the need for informed consent.",
    "miss_guidelines": "Study followed ethical principles of the Declaration of Helsinki.",
    "miss_generic": "Ethically conducted research procedures were applied."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in ETHICS_APPROVAL_FINDERS.items():
        print(f" {name}: {fn(txt)}")
