"""adherence_compliance_finder.py – precision/recall ladder for *treatment adherence / compliance* metrics.
Five variants (v1–v5):
    • v1 – high recall: any sentence with an adherence cue ("adherence", "compliance", medication possession ratio, proportion of days covered, MPR, PDC, pill count).
    • v2 – v1 **and** analytic verb (defined, calculated, measured, assessed, evaluated) within ±4 tokens of the cue.
    • v3 – only inside an *Adherence / Compliance* heading block (first ≈400 characters).
    • v4 – v2 plus explicit numeric threshold or metric keyword (≥80 %, ≥0.8, MPR, PDC, pill count) in the same sentence.
    • v5 – tight template: “Adherence was defined as PDC ≥ 0.8 over 12 months.”
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

ADH_CUE_RE = re.compile(r"\b(?:adherence|compliance|medication\s+possession\s+ratio|mpr|proportion\s+of\s+days\s+covered|pdc|pill\s+count)\b", re.I)
VERB_RE = re.compile(r"\b(?:defined|calculated|measured|assessed|evaluated|determined|computed)\b", re.I)
THRESH_RE = re.compile(r"[≥>]?\s*\d+(?:\.\d+)?\s*(?:%|percent|proportion|ratio|pdc|mpr)?", re.I)
HEAD_ADH_RE = re.compile(r"(?m)^(?:adherence|compliance|medication\s+adherence)\s*[:\-]?\s*$", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"adherence\s+was\s+defined[^\.\n]{0,60}(?:pdc|mpr)[^≥>]*[≥>]\s*0?\.?(?:7|8|80)", re.I)
TRAP_RE = re.compile(r"\badherence\s+to\s+guidelines|baseline\s+adherence\b", re.I)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans=_token_spans(text)
    out: List[Tuple[int,int,str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            context = text[max(0, m.start()-40):m.end()+40]
            if TRAP_RE.search(context):
                continue
            w_s,w_e = _char_to_word((m.start(),m.end()), spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_adherence_compliance_v1(text: str):
    return _collect([ADH_CUE_RE], text)

def find_adherence_compliance_v2(text: str, window: int = 4):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    cue_idx={i for i,t in enumerate(tokens) if ADH_CUE_RE.fullmatch(t)}
    verb_idx={i for i,t in enumerate(tokens) if VERB_RE.fullmatch(t)}
    out=[]
    for c in cue_idx:
        if any(abs(v-c)<=window for v in verb_idx):
            w_s,w_e=_char_to_word(spans[c],spans)
            out.append((w_s,w_e,tokens[c]))
    return out

def find_adherence_compliance_v3(text: str, block_chars: int = 400):
    spans=_token_spans(text)
    blocks=[(h.end(),min(len(text),h.end()+block_chars)) for h in HEAD_ADH_RE.finditer(text)]
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in ADH_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_adherence_compliance_v4(text: str, window: int = 6):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    thr_idx={i for i,t in enumerate(tokens) if THRESH_RE.fullmatch(t)}
    matches=find_adherence_compliance_v2(text, window=window)
    out=[]
    for w_s,w_e,snip in matches:
        if any(w_s-window<=k<=w_e+window for k in thr_idx):
            out.append((w_s,w_e,snip))
    return out

def find_adherence_compliance_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

ADHERENCE_COMPLIANCE_FINDERS: Dict[str, Callable[[str], List[Tuple[int,int,str]]]] = {
    "v1": find_adherence_compliance_v1,
    "v2": find_adherence_compliance_v2,
    "v3": find_adherence_compliance_v3,
    "v4": find_adherence_compliance_v4,
    "v5": find_adherence_compliance_v5,
}

__all__ = [
    "find_adherence_compliance_v1", "find_adherence_compliance_v2", "find_adherence_compliance_v3", "find_adherence_compliance_v4", "find_adherence_compliance_v5", "ADHERENCE_COMPLIANCE_FINDERS",
]

find_adherence_compliance_high_recall = find_adherence_compliance_v1
find_adherence_compliance_high_precision = find_adherence_compliance_v5
