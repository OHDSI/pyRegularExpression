from __future__ import annotations

import re

# ─────────────────────────────
# 1.  Cohort-logic regex assets
# ─────────────────────────────
CODE_TERM = (
    r"(?:icd(?:[- ]?(?:9|10|11))?|icd[- ]?cm|icd[- ]?o|international\s"
    r"classification\s+of\s+diseases(?:[- ]?(?:9|10|11))?)|cpt|current\s"
    r"procedural\s+terminology(?:[- ]?4)?|hcpcs|healthcare\s+common\s+"
    r"procedure\s+coding\s+system|snomed(?:[ -]?ct)?|rxnorm|loinc|read\s+"
    r"codes?|icpc|atc(?:\s+codes?)?|(?:diagnosis|procedure|billing|financial)"
    r"\s+codes?"
)
TEMPORAL_WINDOW = (
    r"(?:look[- ]?back|wash[- ]?out|baseline|observation|follow[- ]?up|"
    r"time[- ]?at[- ]?risk|index)\s+(?:period|window|date|time)|\d+\s*"
    r"(?:days|months|years)\s+of\s+(?:observation|enrollment|follow[- ]?up)|"
    r"(?:fixed\s+time|time\s+window|temporal)|within\s*\d+\s*(?:day|week|month|"
    r"year)s?|in\s+the\s+(?:past|previous)\s+\d+\s*(?:months?|years?)|at\s+"
    r"least\s+\d+\s*(?:months?|years?)|prior\s+to\s+(?:the\s+)?(?:index|"
    r"cohort\s+entry)\s+(?:date)?|pre[- ]?index|post[- ]?index|during\s+the\s+"
    r"\d+\s*(?:day|week|month|year)\s+baseline|after\s+(?:discharge|index)"
)
INCL_EXCL = (
    r"(?:inclusion|exclusion|eligibility|selection)\s+criteria|(?:included|"
    r"excluded)\s+(?:patients|subjects|participants|individuals)|(?:required|"
    r"criteria\s+for)\s+(?:inclusion|exclusion|eligibility)|cohort\s+"
    r"definition|phenotype\s+algorithm|(?:must|had)\s+to\s+have|must\s+have|"
    r"must\s+not\s+have|required\s+to\s+have|patients?\s+with.+?(?:were|was)"
    r"\s+excluded?"
)
CARE_SETTING = (
    r"(?:inpatient|outpatient|ambulatory)\s+(?:setting|visit|stay|care|record|"
    r"encounter|population|basis)|(?:hospitalized|hospitalization|admitted\s+"
    r"to\s+(?:hospital|inpatient))|(?:emergency\s+department|ed|emergency\s+"
    r"room|er)\s+(?:visit|setting|care|encounter)|(?:clinic|primary\s+care|"
    r"specialty\s+care)\s+(?:visit|setting|record|encounter)|primary\s+care|"
    r"specialist\s+visit|telehealth\s+visit|same[- ]?day\s+surgery|day[- ]?case"
)
WITHIN_2K = r"(?:\b\w+\b\W*){0,1999}"
COHORT_LOGIC_RE = re.compile(
    rf"(?xi)({CODE_TERM}|{TEMPORAL_WINDOW}|{INCL_EXCL}|{CARE_SETTING})"
)

# ─────────────────────────────
# 2.  Public helper
# ─────────────────────────────
def find_cohort_logic(
    text: str,
    *,
    return_offsets: bool = True,
) -> list[tuple[int, int, str]] | list[str]:
    """
    Identify fragments of OHDSI-style cohort-definition logic in *text*.

    Parameters
    ----------
    text            Free-text input (e.g., methods section, protocol, etc.).
    return_offsets  When True (default), return ``(start, end, snippet)``
                    tuples; otherwise return matching snippets as strings.
    """
    spans = [(m.start(), m.end(), m.group(0)) for m in COHORT_LOGIC_RE.finditer(text)]
    return spans if return_offsets else [s[-1] for s in spans]


# ─────────────────────────────
# 3.  Medical code extractor
# ─────────────────────────────
MEDICAL_CODE_RE = re.compile(
    r"""
    (
      \b\d{4}-\d{4}-\d{2}\b         # NDC hyphenated (0002-8215-01)
      |\b\d{10,11}\b                # NDC plain 10–11 digits (0002821501)
      |[A-Z]\d{2}[A-Z]{2}\d{2}      # ATC (A10BA02)
      |[A-Z]\d{1,2}\.\d+            # ICD (E11.9)
      |\b\d{4,5}\b                  # CPT (99213)
      |\b\d{6,8}\b                  # RxCUI / short SNOMED
      |\b\d{9,18}\b                 # long SNOMED
    )
    """,
    re.VERBOSE,
)


def extract_medical_codes(
    text: str,
    *,
    return_offsets: bool = False,
    unique: bool = True,
) -> list[tuple[int, int, str]] | list[str]:
    spans = [(m.start(), m.end(), m.group(0)) for m in MEDICAL_CODE_RE.finditer(text)]
    if unique:
        seen = set()
        deduped = []
        for s in spans:
            if s[-1] not in seen:
                seen.add(s[-1])
                deduped.append(s)
        spans = deduped
    return spans if return_offsets else [s[-1] for s in spans]
