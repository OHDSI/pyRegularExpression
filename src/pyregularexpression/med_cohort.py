from __future__ import annotations
import re
from typing import List, Tuple

# ─────────────────────────────
# 1.  Cohort-logic regex assets
# ─────────────────────────────
CODE_TERM = r"(?:icd(?:[- ]?(?:9|10|11))?|icd[- ]?cm|icd[- ]?o|international\ classification\ of\ diseases(?:[- ]?(?:9|10|11))?)|cpt|current\ procedural\ terminology(?:[- ]?4)?|hcpcs|healthcare\ common\ procedure\ coding\ system|snomed(?:[ -]?ct)?|rxnorm|loinc|read\ codes?|icpc|atc(?:\s+codes?)?|(?:diagnosis|procedure|billing|financial)\s+codes?"
TEMPORAL_WINDOW = r"(?:look[- ]?back|wash[- ]?out|baseline|observation|follow[- ]?up|time[- ]?at[- ]?risk|index)\s+(?:period|window|date|time)|(?:prior|subsequent)\s+(?:to|observation|enrollment|index)|\d+\s*(?:days|months|years)\s+of\s+(?:observation|enrollment|follow[- ]?up)|(?:fixed\ time|time\ window|temporal)|within\s*\d+\s*(?:day|week|month|year)s?|in\s+the\s+(?:past|previous)\s+\d+\s*(?:months?|years?)|at\s+least\s+\d+\s*(?:months?|years?)|prior\s+to\s+(?:the\s+)?(?:index|cohort\s+entry)\s+date?|pre[- ]?index|post[- ]?index|during\s+the\s+\d+\s*(?:day|week|month|year)\s+baseline|after\s+(?:discharge|index)|\bindex\b"
INCL_EXCL = r"(?:inclusion|exclusion|eligibility|selection)\s+criteria|(?:included|excluded)\s+(?:patients|subjects|participants|individuals)|(?:required|criteria\ for)\s+(?:inclusion|exclusion|eligibility)|cohort\ definition|phenotype\ algorithm|(?:must|had)\s+to\s+have|must\s+have|must\s+not\s+have|required\s+to\s+have|patients?\s+with.+?(?:were|was)\s+excluded?"
CARE_SETTING = r"(?:inpatient|outpatient|ambulatory)\s+(?:setting|visit|stay|care|record|encounter|population|basis)|(?:hospitalized|hospitalization|admitted\s+to\s+(?:hospital|inpatient))|(?:emergency\s+department|ed|emergency\s+room|er)\s+(?:visit|setting|care|encounter)|(?:clinic|primary\ care|specialty\ care)\s+(?:visit|setting|record|encounter)|primary\ care|specialist\ visit|telehealth\ visit|same[- ]?day\ surgery|day[- ]?case"
WITHIN_2K = r"(?:\b\w+\b\W*){0,1999}"

COHORT_LOGIC_RE = re.compile(
    rf"(?xi)(?={WITHIN_2K}{CODE_TERM})(?={WITHIN_2K}(?:{TEMPORAL_WINDOW}|{INCL_EXCL}|{CARE_SETTING}))(?:{CODE_TERM}|{TEMPORAL_WINDOW}|{INCL_EXCL}|{CARE_SETTING})"
)

# ─────────────────────────────
# 2.  Public helper
# ─────────────────────────────
def find_cohort_logic(
    text: str,
    *,
    return_offsets: bool = True,
) -> List[Tuple[int, int, str]] | List[str]:
    """
    Identify fragments of OHDSI-style cohort-definition logic in *text*.

    Parameters
    ----------
    text            Free-text input (e.g., methods section, protocol, etc.).
    return_offsets  When True (default), return ``(start, end, snippet)`` tuples;
                    otherwise return the matching snippets as plain strings.
    """
    spans = [(m.start(), m.end(), m.group(0)) for m in COHORT_LOGIC_RE.finditer(text)]
    return spans if return_offsets else [s[-1] for s in spans]
