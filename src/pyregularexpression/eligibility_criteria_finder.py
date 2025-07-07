"""eligibility_criteria_finder.py – precision/recall ladder for *inclusion / exclusion eligibility criteria* statements.
Five variants (v1–v5):
    • v1 – high recall: any eligibility cue (eligible patients were, inclusion criteria included, we excluded participants who, exclusion criteria, criteria for enrollment, eligible if).
    • v2 – explicit inclusion OR exclusion cue + condition within ±4 tokens (numeric/age/diagnosis etc.).
    • v3 – only inside an *Eligibility / Inclusion and Exclusion Criteria* heading block (first ~500 characters).
    • v4 – v2 plus both an inclusion and an exclusion cue in the same sentence/nearby to maximise precision.
    • v5 – tight template: paired statement listing age/diagnosis eligibility and exclusion of specific conditions (e.g., “Adults 18–65 with diabetes were eligible; prior insulin use was an exclusion”).
Each finder returns tuples: (start_word_idx, end_word_idx, snippet).
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

TOKEN_RE = re.compile(r"\\S+")

def _token_spans(text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_to_word(span: Tuple[int, int], spans: Sequence[Tuple[int, int]]):
    s, e = span
    w_s = next(i for i, (a, b) in enumerate(spans) if a <= s < b)
    w_e = next(i for i, (a, b) in reversed(list(enumerate(spans))) if a < e <= b)
    return w_s, w_e

INCL_CUE_RE = re.compile(r"\\b(?:eligible\\s+(?:patients|participants|subjects|individuals)\\s+were|inclusion\\s+criteria\\s+(?:included|were|consisted\\s+of)|eligible\\s+if|criteria\\s+for\\s+enrollment|patients?\\s+were\\s+eligible|we\\s+included|must\\s+meet\\s+all\\s+of\\s+the\\s+following|required\\s+to\\s+have)\\b", re.I)
EXCL_CUE_RE = re.compile(r"\\b(?:we\\s+excluded|exclusion\\s+criteria|excluded\\s+patients?|patients?\\s+were\\s+excluded|exclusion\\s+included|were\\s+not\\s+eligible|must\\s+not\\s+have)\\b", re.I)
ELIG_CUE_RE = re.compile(r"\\b(?:inclusion\\s+criteria|exclusion\\s+criteria|eligible|enrollment\\s+criteria)\\b", re.I)
HEADING_ELIG_RE = re.compile(r"(?m)^(?:eligibility|inclusion\\s+and\\s+exclusion\\s+criteria|study\\s+population|participants?)\\s*[:\\-]?\\s*$", re.I)
TRAP_RE = re.compile(r"\\b(?:diagnostic\\s+criteria|classification\\s+criteria|performance\\s+criteria)\\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(
    r"\\b(?:adults?|children)\\s+\\d{1,3}(?:–|-|\\s+to\\s+)\\d{1,3}\\s+[^\\.\\n]{0,80}(?:eligible|inclusion\\s+criteria)[^\\.\\n]{0,120}(?:exclusion\\s+criteria|were\\s+excluded)\\b",
    re.I,
)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans = _token_spans(text)
    out = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0, m.start()-25):m.end()+25]):
                continue
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_eligibility_criteria_v1(text: str):
    return _collect([INCL_CUE_RE, EXCL_CUE_RE, ELIG_CUE_RE], text)

def find_eligibility_criteria_v2(text: str, window: int = 4):
    qualifier_re = re.compile(r"\\b(age\\s+\\d{1,3}|\\d{1,3}\\s*(?:years?|yrs?)|male|female|men|women|diagnosed|history\\s+of)\\b", re.I)
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    qual_idx = {i for i, t in enumerate(tokens) if qualifier_re.fullmatch(t)}
    cue_idx = {i for i, t in enumerate(tokens) if INCL_CUE_RE.fullmatch(t) or EXCL_CUE_RE.fullmatch(t)}
    out = []
    for i in cue_idx:
        if any(q for q in qual_idx if abs(q - i) <= window):
            w_s, w_e = _char_to_word(spans[i], spans)
            out.append((w_s, w_e, tokens[i]))
    return out

def find_eligibility_criteria_v3(text: str, block_chars: int = 500):
    spans = _token_spans(text)
    blocks = []
    for h in HEADING_ELIG_RE.finditer(text):
        s = h.end(); e = min(len(text), s + block_chars)
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in (INCL_CUE_RE, EXCL_CUE_RE):
        for x in m.finditer(text):
            if inside(x.start()):
                w_s, w_e = _char_to_word((x.start(), x.end()), spans)
                out.append((w_s, w_e, x.group(0)))
    return out

def find_eligibility_criteria_v4(text: str, window: int = 6):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    incl_idx = {i for i, t in enumerate(tokens) if INCL_CUE_RE.fullmatch(t)}
    excl_idx = {i for i, t in enumerate(tokens) if EXCL_CUE_RE.fullmatch(t)}
    out = []
    for i in incl_idx:
        if any(e for e in excl_idx if abs(e - i) <= window):
            w_s, w_e = _char_to_word(spans[i], spans)
            out.append((w_s, w_e, tokens[i]))
    return out

def find_eligibility_criteria_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

ELIGIBILITY_CRITERIA_FINDERS: Dict[str, Callable[[str], List[Tuple[int,int,str]]]] = {
    "v1": find_eligibility_criteria_v1,
    "v2": find_eligibility_criteria_v2,
    "v3": find_eligibility_criteria_v3,
    "v4": find_eligibility_criteria_v4,
    "v5": find_eligibility_criteria_v5,
}

__all__ = [
    "find_eligibility_criteria_v1", "find_eligibility_criteria_v2", "find_eligibility_criteria_v3",
    "find_eligibility_criteria_v4", "find_eligibility_criteria_v5", "ELIGIBILITY_CRITERIA_FINDERS",
]

find_eligibility_criteria_high_recall = find_eligibility_criteria_v1
find_eligibility_criteria_high_precision = find_eligibility_criteria_v5