"""conflict_of_interest_finder.py – precision/recall ladder for *conflict‑of‑interest disclosures*.
Five variants (v1–v5):
    • v1 – high recall: sentence containing a conflict cue ("conflict of interest", "competing interests", disclosures, "no competing interests").
    • v2 – v1 **and** disclosure verb (declare, disclose, report, state) within ±4 tokens of the cue.
    • v3 – only inside a *Conflict of Interest / Disclosures / Competing Interests* heading block (first ≈400 characters).
    • v4 – v2 plus explicit company/payment or explicit negation phrase ("no competing interests", "no conflict") in same sentence.
    • v5 – tight template: “The authors declare no competing interests.”
Each finder returns tuples: (start_word_idx, end_word_idx, snippet).
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

TOKEN_RE = re.compile(r"\S+")

def _token_spans(text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_to_word(span: Tuple[int, int], spans: Sequence[Tuple[int, int]]):
    s, e = span
    w_s = next(i for i,(a,b) in enumerate(spans) if a<=s<b)
    w_e = next(i for i,(a,b) in reversed(list(enumerate(spans))) if a<e<=b)
    return w_s, w_e

COI_CUE_RE = re.compile(r"\b(?:conflicts?\s+of\s+interest|competing\s+interests?|conflict\s+disclosures?)\b", re.I)
VERB_RE = re.compile(r"\b(?:declare(?:s|d)?|disclose(?:s|d)?|report(?:s|ed)?|state(?:s|d)?)\b", re.I)
HEAD_COI_RE = re.compile(r"(?m)^(?:conflicts?\s+of\s+interest|competing\s+interests?|disclosures?)\s*[:\-]?\s*$", re.I)
COMPANY_RE = re.compile(r"\b(?:Pfizer|Novartis|Merck|Roche|AstraZeneca|Bayer|GSK|Sanofi|Johnson\s+&?\s*Johnson|Amgen|Lilly)\b", re.I)
NO_COI_RE = re.compile(r"\bno\s+(?:conflicts?|competing\s+interests?)\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"authors?\s+declare\s+no\s+competing\s+interests", re.I)
TRAP_RE = re.compile(r"\bconflict(?:ing)?\s+evidence|conflict\s+with\s+previous\s+studies\b", re.I)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans=_token_spans(text)
    out: List[Tuple[int,int,str]]=[]
    for patt in patterns:
        for m in patt.finditer(text):
            context=text[max(0,m.start()-40):m.end()+40]
            if TRAP_RE.search(context):
                continue
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_conflict_of_interest_v1(text: str):
    return _collect([COI_CUE_RE], text)

def find_conflict_of_interest_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    out = []
    for cue_match in COI_CUE_RE.finditer(text):
        cue_w_s, cue_w_e = _char_to_word(cue_match.span(), spans)
        for verb_match in VERB_RE.finditer(text):
            verb_w_s, verb_w_e = _char_to_word(verb_match.span(), spans)
            if verb_w_s > 0 and re.search(r"\bnot\b", tokens[verb_w_s - 1], re.I):
                continue
            if abs(verb_w_s - cue_w_s) <= window:
                out.append((cue_w_s, cue_w_e, cue_match.group(0)))
                break
    return out

def find_conflict_of_interest_v3(text: str, block_chars: int = 400):
    spans = _token_spans(text)
    blocks=[(h.end(), min(len(text), h.end()+block_chars)) for h in HEAD_COI_RE.finditer(text)]
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for i,(s,e) in enumerate(spans):
        if inside(s):
            out.append((i,i,text[s:e]))
    return out

def find_conflict_of_interest_v4(text: str, window: int = 6):
    spans = _token_spans(text)
    v2_matches = find_conflict_of_interest_v2(text, window)
    if not v2_matches:
        return []
    tech_positions = []
    for pattern in (COMPANY_RE, NO_COI_RE):
        for m in pattern.finditer(text):
            word_idx = _char_to_word((m.start(), m.end()), spans)[0]
            tech_positions.append(word_idx)
    out = []
    for w_s, w_e, snip in v2_matches:
        if any(w_s - window <= pos <= w_e + window for pos in tech_positions):
            out.append((w_s, w_e, snip))
    return out

def find_conflict_of_interest_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

CONFLICT_OF_INTEREST_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1": find_conflict_of_interest_v1,
    "v2": find_conflict_of_interest_v2,
    "v3": find_conflict_of_interest_v3,
    "v4": find_conflict_of_interest_v4,
    "v5": find_conflict_of_interest_v5,
}

__all__=[
    "find_conflict_of_interest_v1","find_conflict_of_interest_v2","find_conflict_of_interest_v3",
    "find_conflict_of_interest_v4","find_conflict_of_interest_v5","CONFLICT_OF_INTEREST_FINDERS"
]

find_conflict_of_interest_high_recall=find_conflict_of_interest_v1
find_conflict_of_interest_high_precision=find_conflict_of_interest_v5
