"""propensity_score_method_finder.py – precision/recall ladder for *propensity-score methods*.
Five variants (v1–v5):
    • v1 – high recall: any sentence with a propensity‑score cue (propensity score, PS-matched, IPTW, inverse probability weighting, doubly robust).
    • v2 – v1 **and** analysis verb (calculated, estimated, applied, used, performed) within ±4 tokens.
    • v3 – only inside a *Propensity Score / Confounding Control* heading block (first ~400 characters).
    • v4 – v2 plus explicit technique qualifier (matching, weighting, stratification, IPTW, SMR, stabilized) in the same sentence.
    • v5 – tight template: “We estimated propensity scores via logistic regression and applied IPTW.”
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

PS_CUE_RE = re.compile(
    r"\b(?:propensity\s+scores?|ps[- ]?matched|ps[- ]?weight(?:ed|ing)|iptw|ipw|smr\s+weight(?:ed|ing)?|inverse\s+probability\s+weight(?:ed|ing)?|doubly\s+robust|augmented\s+iptw)\b",
    re.I,
)
VERB_RE = re.compile(r"\b(?:calculated|estimated|computed|derived|applied|used|performed|implemented)\b", re.I)
TECH_RE = re.compile(r"\b(?:matching|weighting|stratification|iptw|inverse\s+probability|smr|stabilized|fine\s+stratification|doubly\s+robust)\b", re.I)
HEAD_PS_RE = re.compile(r"(?m)^(?:propensity\s+score|confounding\s+control|ps\s+method)\s*[:\-]?\s*$", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"estimated\s+propensity\s+scores?[^\.\n]{0,40}?applied\s+(?:iptw|ps[- ]?matching|inverse\s+probability\s+weight(?:ed|ing))", re.I)
TRAP_RE = re.compile(r"\bpropensity\s+to\b", re.I)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans=_token_spans(text)
    out: List[Tuple[int,int,str]]=[]
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0,m.start()-10):m.end()+10]):
                continue
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_propensity_score_method_v1(text: str):
    return _collect([PS_CUE_RE], text)

def find_propensity_score_method_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    cue_spans = []
    for m in PS_CUE_RE.finditer(text):
        w_s, w_e = _char_to_word((m.start(), m.end()), spans)
        cue_spans.append((w_s, w_e, m.group(0)))
    verb_positions = []
    for m in VERB_RE.finditer(text):
        w_s, w_e = _char_to_word((m.start(), m.end()), spans)
        verb_positions.extend(range(w_s, w_e + 1))
    out = []
    for w_s, w_e, snip in cue_spans:
        if any(min(abs(v - w_s), abs(v - w_e)) <= window for v in verb_positions):
            out.append((w_s, w_e, snip))
    return out

def find_propensity_score_method_v3(text: str, block_chars: int = 400):
    spans=_token_spans(text)
    blocks=[]
    for h in HEAD_PS_RE.finditer(text):
        s=h.end(); e=min(len(text),s+block_chars)
        blocks.append((s,e))
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in PS_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_propensity_score_method_v4(text: str, window: int = 6):
    spans = _token_spans(text)
    tech_positions = []
    for m in TECH_RE.finditer(text):
        w_s, w_e = _char_to_word((m.start(), m.end()), spans)
        tech_positions.extend(range(w_s, w_e + 1))
    matches = find_propensity_score_method_v2(text, window=window)
    out = []
    for w_s, w_e, snip in matches:
        if any(w_s - window <= t <= w_e + window for t in tech_positions):
            out.append((w_s, w_e, snip))
    return out

def find_propensity_score_method_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

PROPENSITY_SCORE_METHOD_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1": find_propensity_score_method_v1,
    "v2": find_propensity_score_method_v2,
    "v3": find_propensity_score_method_v3,
    "v4": find_propensity_score_method_v4,
    "v5": find_propensity_score_method_v5,
}

__all__=["find_propensity_score_method_v1","find_propensity_score_method_v2","find_propensity_score_method_v3","find_propensity_score_method_v4","find_propensity_score_method_v5","PROPENSITY_SCORE_METHOD_FINDERS"]

find_propensity_score_method_high_recall=find_propensity_score_method_v1
find_propensity_score_method_high_precision=find_propensity_score_method_v5
