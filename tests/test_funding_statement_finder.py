"""Smoke tests for funding_statement_finder."""
from pyregularexpression.funding_statement_finder import FUNDING_STATEMENT_FINDERS

examples = {
    "hit_grant": "Supported by NIH grant R01-HL123456.",
    "hit_corporate": "This study was sponsored by Pfizer.",
    "miss_coi": "Authors received no personal fees from any company.",
    "miss_irb": "Protocol approved by IRB 12345."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in FUNDING_STATEMENT_FINDERS.items():
        print(f" {name}: {fn(txt)}")
