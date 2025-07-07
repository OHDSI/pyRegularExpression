"""competing_risk_analysis_finder.py – precision/recall ladder for *competing‑risk analyses*.
Five variants (v1–v5):
    • v1 – high recall: any sentence containing a competing‑risk cue ("competing risk", Fine‑Gray, sub‑hazard ratio, sHR, cumulative incidence competing risk).
    • v2 – v1 **and** a modelling verb (fitted, estimated, modelled, applied, used) within ±4 tokens of the cue.
    • v3 – only inside a *Competing Risk / Fine‑Gray / Cumulative Incidence* heading block (first ≈400 characters).
    • v4 – v2 plus an explicit technique keyword (Fine‑Gray, sub‑hazard, cumulative incidence function, sHR) in the same sentence.
    • v5 – tight template: “We fitted Fine‑Gray models to estimate sHRs for death vs transplant.”
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

CR_CUE_RE = re.compile(r"\b(?:competing\s+risk(?:s)?|fine[–-]?gray|sub[- ]?hazard\s+ratio|shr|subhazard|cumulative\s+incidence\s+competing\s+risk)\b", re.I)
VERB_RE = re.compile(r"\b(?:fitted|fit|estimated|model(?:led)?|applied|used|performed)\b", re.I)
TECH_RE = re.compile(r"\b(?:fine[–-]?gray|sub[- ]?hazard|cumulative\s+incidence\s+function|shr|cause[- ]specific)\b", re.I)
HEAD_CR_RE = re.compile(r"(?m)^(?:competing\s+risk(?:s)?|fine[–-]?gray|cumulative\s+incidence)\s*[:\-]?\s*$", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"fitted\s+fine[–-]?gray\s+model[s]?[^\.\n]{0,40}shr", re.I)
TRAP_RE = re.compile(r"\bcompetition\s+for\s+resources|risk\s+competition\b", re.I)
NEG_RE = re.compile(r"\b(?:without|not|no|absence(?:\s+of)?|lacking|lack|did\s+not|didn’t|didn't|never|rather\s+than)\b", re.I)

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

def find_competing_risk_analysis_v1(text: str):
    return _collect([CR_CUE_RE], text)

def find_competing_risk_analysis_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]

    # collect all matches of cues and verbs over the whole text
    cue_matches = [(m.start(), m.end()) for m in CR_CUE_RE.finditer(text)]
    verb_matches = [(m.start(), m.end()) for m in VERB_RE.finditer(text)]

    cue_idx = [_char_to_word(span, spans) for span in cue_matches]
    verb_idx = [_char_to_word(span, spans) for span in verb_matches]

    out = []
    for c_s, c_e in cue_idx:
        if any(abs(v_s - c_s) <= window or abs(v_e - c_e) <= window for v_s, v_e in verb_idx):
            snippet = text[spans[c_s][0]: spans[min(len(spans)-1, c_e)][1]]
            out.append((c_s, c_e, snippet))
    return out

def find_competing_risk_analysis_v3(text:str, block_chars:int=400):
    spans=_token_spans(text)
    blocks=[(h.end(),min(len(text),h.end()+block_chars)) for h in HEAD_CR_RE.finditer(text)]
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in CR_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_competing_risk_analysis_v4(text: str, window: int = 6):
    spans = _token_spans(text)
    matches = find_competing_risk_analysis_v2(text, window)
    if not matches:
        return []
    tech_positions: set[int] = set()
    for m in TECH_RE.finditer(text):
        w_s, w_e = _char_to_word((m.start(), m.end()), spans)
        lookback = 5
        left_idx = max(0, w_s - lookback)
        left_text = text[spans[left_idx][0]: m.start()]
        if NEG_RE.search(left_text):
            continue
        tech_positions.add(w_s)
    if not tech_positions:
        return []
    out = []
    for w_s, w_e, snip in matches:
        if any(w_s - window <= t <= w_e + window for t in tech_positions):
            out.append((w_s, w_e, snip))
    return out

def find_competing_risk_analysis_v5(text:str):
    return _collect([TIGHT_TEMPLATE_RE], text)

COMPETING_RISK_ANALYSIS_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1": find_competing_risk_analysis_v1,
    "v2": find_competing_risk_analysis_v2,
    "v3": find_competing_risk_analysis_v3,
    "v4": find_competing_risk_analysis_v4,
    "v5": find_competing_risk_analysis_v5,
}

__all__=["find_competing_risk_analysis_v1","find_competing_risk_analysis_v2","find_competing_risk_analysis_v3","find_competing_risk_analysis_v4","find_competing_risk_analysis_v5","COMPETING_RISK_ANALYSIS_FINDERS"]

find_competing_risk_analysis_high_recall=find_competing_risk_analysis_v1
find_competing_risk_analysis_high_precision=find_competing_risk_analysis_v5
