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

COI_CUE_RE = re.compile(r"\b(?:conflicts?\s+of\s+interest|competing\s+interests?|disclosures?)\b", re.I)
VERB_RE = re.compile(r"\b(?:declare[d]?|disclos(?:e|ed)|report(?:ed)?|state(?:d)?)\b", re.I)
COMPANY_RE = re.compile(r"\b(?:Pfizer|Novartis|Merck|Roche|AstraZeneca|Bayer|GSK|Sanofi|Johnson\s+&?\s*Johnson|Amgen|Lilly)\b", re.I)
NO_COI_RE = re.compile(r"\bno\s+(?:conflicts?|competing\s+interests?)\b", re.I)
HEAD_COI_RE = re.compile(r"(?m)^(?:conflicts?\s+of\s+interest|competing\s+interests?|disclosures?)\s*[:\-]?\s*$", re.I)
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
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    cue_idx={i for i,t in enumerate(tokens) if COI_CUE_RE.fullmatch(t)}
    verb_idx={i for i,t in enumerate(tokens) if VERB_RE.fullmatch(t)}
    out=[]
    for c in cue_idx:
        if any(abs(v-c)<=window for v in verb_idx):
            w_s,w_e=_char_to_word(spans[c],spans)
            out.append((w_s,w_e,tokens[c]))
    return out

def find_conflict_of_interest_v3(text: str, block_chars: int = 400):
    spans=_token_spans(text)
    blocks=[(h.end(),min(len(text),h.end()+block_chars)) for h in HEAD_COI_RE.finditer(text)]
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in COI_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_conflict_of_interest_v4(text: str, window: int = 6):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    extra_idx={i for i,t in enumerate(tokens) if COMPANY_RE.fullmatch(t) or NO_COI_RE.fullmatch(t)}
    matches=find_conflict_of_interest_v2(text, window=window)
    out=[]
    for w_s,w_e,snip in matches:
        if any(w_s-window<=k<=w_e+window for k in extra_idx):
            out.append((w_s,w_e,snip))
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
