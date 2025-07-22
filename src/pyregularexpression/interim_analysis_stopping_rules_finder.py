# In src/pyregularexpression/interim_analysis_stopping_rules_finder.py
'''
INTERIM_ANALYSIS_STOPPING_RULES_FINDERS = {
    "rule1": lambda text: "Interim analysis rule 1 applied to " + text,
    "rule2": lambda text: "Interim analysis rule 2 applied to " + text,
    "rule3": lambda text: "Interim analysis rule 3 applied to " + text,
}

# You can expand this dictionary with more rules and their corresponding functions as per the requirements.


interim_analysis_stopping_rules_finder.py – multi-tiered finder for interim analysis stopping rules.

Variants:
    • v1 – broad pattern match on keywords like 'interim analysis', 'DSMB', 'stopping rule'
    • v2 – match must include statistical boundary mention (e.g. p < 0.001)
    • v3 – tight template for planned interim analysis with named boundaries
'''

import re
from typing import List, Tuple, Callable, Dict

# ─────────────────────────────
# 1.  Patterns
# ─────────────────────────────
INTERIM_ANALYSIS_RE = re.compile(r"\b(interim\s+analysis|DSMB|stopping\s+rule|stopping\s+boundar(y|ies))\b", re.I)
STATISTICAL_BOUNDARY_RE = re.compile(r"(p\s*[<≤]\s*0\.\d+|\bO[’']Brien[-\s]?Fleming\b|\bHaybittle[-\s]?Peto\b)", re.I)
TEMPLATE_RE = re.compile(r"(Interim analysis at \d+ (weeks|months).+?(O[’']Brien[-\s]?Fleming|Haybittle[-\s]?Peto).+?p\s*[<≤]\s*0\.\d+)", re.I)

# ─────────────────────────────
# 2.  Finders
# ─────────────────────────────
def find_stopping_rule_v1(text: str) -> List[Tuple[int, int, str]]:
    """v1: Broad keyword match for interim analysis mentions."""
    return [(m.start(), m.end(), m.group()) for m in INTERIM_ANALYSIS_RE.finditer(text)]


def find_stopping_rule_v2(text: str) -> List[Tuple[int, int, str]]:
    """v2: Must include both interim/stopping cue and statistical boundary."""
    out = []
    for m in INTERIM_ANALYSIS_RE.finditer(text):
        span_text = text[max(0, m.start()-50):m.end()+50]
        if STATISTICAL_BOUNDARY_RE.search(span_text):
            out.append((m.start(), m.end(), m.group()))
    return out


def find_stopping_rule_v3(text: str) -> List[Tuple[int, int, str]]:
    """v3: Match a tight template like 'Interim analysis at X months... p < 0.001'."""
    return [(m.start(), m.end(), m.group()) for m in TEMPLATE_RE.finditer(text)]

# ─────────────────────────────
# 3.  Mapping
# ─────────────────────────────
INTERIM_ANALYSIS_STOPPING_RULES_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_stopping_rule_v1,
    "v2": find_stopping_rule_v2,
    "v3": find_stopping_rule_v3,
}

__all__ = ["find_stopping_rule_v1", "find_stopping_rule_v2", "find_stopping_rule_v3", "INTERIM_ANALYSIS_STOPPING_RULES_FINDERS"]
