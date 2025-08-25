"""generalizability_finder.py – precision/recall ladder for *generalizability / external validity* statements.
Five variants (v1–v5):
    • v1 – high recall: sentence containing a generalizability cue (generalizable, external validity, applicability, apply only to).
    • v2 – v1 **and** uncertainty/caution modal (may, might, caution, should be interpreted) within ±4 tokens of cue.
    • v3 – only inside a *Generalizability / External Validity / Applicability* heading block (first ~400 characters).
    • v4 – v2 plus explicit population or setting qualifier (e.g., older adults, women, single center, high‑income countries) in same sentence.
    • v5 – tight template: “Findings may not generalize to older adults or women.”
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

GEN_CUE_RE = re.compile(r"\b(?:generalizability|generalizable|generalise|generalize|external\s+validity|applicability|apply\s+only\s+to|interpreted\s+with\s+caution)\b",re.I)
MODAL_RE = re.compile(r"\b(?:may|might|could|should|caution|care\s+should\s+be)\b", re.I)
POP_QUAL_RE = re.compile(r"\b(?:older\s+adults?|women|men|children|single\s+center|tertiary\s+care|high[- ]income|low[- ]income|specific\s+population|hospitalised|asian|european|us|multi[- ]center)\b", re.I)
HEAD_GEN_RE = re.compile(r"(?m)^(?:generalizability|external\s+validity|applicability)\s*[:\-]?\s*$", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"findings?\s+may\s+not\s+generaliz(?:e|e)\s+to\s+[^\".\n]{3,60}", re.I)
TRAP_RE = re.compile(r"\bmodel\s+is\s+generalizable|algorithm\s+generalizability\b", re.I)

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

def find_generalizability_v1(text: str):
    return _collect([GEN_CUE_RE], text)

def find_generalizability_v2(text: str, window: int = 4):
    import string
    spans = _token_spans(text)
    tokens = [text[s:e].strip(string.punctuation) for s, e in spans]  # strip punctuation
    cue_idx = {i for i,t in enumerate(tokens) if GEN_CUE_RE.fullmatch(t)}
    mod_idx = {i for i,t in enumerate(tokens) if MODAL_RE.fullmatch(t)}
    out=[]
    for c in cue_idx:
        if any(abs(m-c) <= window for m in mod_idx):
            w_s, w_e = _char_to_word(spans[c], spans)
            out.append((w_s, w_e, tokens[c]))
    return out

def find_generalizability_v3(text: str, block_chars: int = 400):
    spans=_token_spans(text)
    blocks=[]
    for h in HEAD_GEN_RE.finditer(text):
        s=h.end(); e=min(len(text),s+block_chars)
        blocks.append((s,e))
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in GEN_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_generalizability_v4(text: str, window: int = 8):
    import string
    spans = _token_spans(text)
    tokens = [text[s:e].strip(string.punctuation) for s,e in spans]  # strip punctuation
    pop_idx = {i for i, t in enumerate(tokens) if POP_QUAL_RE.fullmatch(t)}
    matches = find_generalizability_v2(text, window=window)
    out = []
    for w_s, w_e, snip in matches:
        if any(w_s - window <= p <= w_e + window for p in pop_idx):
            out.append((w_s, w_e, snip))
    return out

def find_generalizability_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

GENERALIZABILITY_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1": find_generalizability_v1,
    "v2": find_generalizability_v2,
    "v3": find_generalizability_v3,
    "v4": find_generalizability_v4,
    "v5": find_generalizability_v5,
}

__all__=["find_generalizability_v1","find_generalizability_v2","find_generalizability_v3","find_generalizability_v4","find_generalizability_v5","GENERALIZABILITY_FINDERS"]

find_generalizability_high_recall=find_generalizability_v1
find_generalizability_high_precision=find_generalizability_v5
