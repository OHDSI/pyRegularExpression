"""participant_flow_finder.py – precision/recall ladder for *participant flow* statements (CONSORT flow).
Five variants (v1–v5):
    • v1 – high recall: any flow cue (randomized to, allocated to, completed the study, n = xx, flow diagram) with a number.
    • v2 – v1 **and** explicit group label or stage keyword (treatment, placebo, intervention, control, follow‑up, analysis) within ±4 tokens.
    • v3 – only inside a *Participant Flow* / *CONSORT Flow* / *Figure 1* heading block (first ~600 characters).
    • v4 – v2 plus at least two numeric group counts in same sentence/line (captures split counts 100 vs 100).
    • v5 – tight template: “200 randomized (100 treatment, 100 placebo); 180 completed follow‑up.”
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

NUM_RE = r"\d{1,4}"
FLOW_CUE_RE = re.compile(rf"\b(?:randomi[sz]ed|allocated|assigned|completed|analysed|lost\s+to\s+follow[- ]up|withdrew|excluded|screened)\b", re.I)
GROUP_RE = re.compile(r"\b(?:treatment|intervention|placebo|control|drug\s+\w+|arm|group|cohort)\b", re.I)
STAGE_RE = re.compile(r"\b(?:enrol(?:led|ment)|follow[- ]up|analysis|baseline|screening|randomi[sz]ation)\b", re.I)
HEADING_FLOW_RE = re.compile(r"(?m)^(?:participant\s+flow|consort\s+flow|figure\s+1)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\btotal\s+of\s+\d+\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(rf"{NUM_RE}\s+randomi[sz]ed\s*\(\s*{NUM_RE}\s+[^,]+,\s*{NUM_RE}\s+[^\)]+\)\s*;\s*{NUM_RE}\s+completed", re.I)
NUM_TOKEN_RE = re.compile(r"^\d{1,4}$")


def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans = _token_spans(text)
    out: List[Tuple[int,int,str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0,m.start()-20):m.end()+20]):
                continue
            w_s,w_e = _char_to_word((m.start(),m.end()), spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_participant_flow_v1(text:str):
    pattern = re.compile(rf"{FLOW_CUE_RE.pattern}[^\n]{{0,15}}{NUM_RE}", re.I)
    return _collect([pattern], text)

def find_participant_flow_v2(text:str, window:int=4):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    cue_idx={i for i,t in enumerate(tokens) if FLOW_CUE_RE.fullmatch(t)}
    num_idx={i for i,t in enumerate(tokens) if NUM_TOKEN_RE.fullmatch(t)}
    grp_idx={i for i,t in enumerate(tokens) if GROUP_RE.fullmatch(t) or STAGE_RE.fullmatch(t)}
    out=[]
    for c in cue_idx:
        if any(abs(n-c)<=window for n in num_idx) and any(abs(g-c)<=window for g in grp_idx):
            w_s,w_e=_char_to_word(spans[c],spans)
            out.append((w_s,w_e,tokens[c]))
    return out

def find_participant_flow_v3(text:str, block_chars:int=600):
    spans=_token_spans(text)
    blocks=[]
    for h in HEADING_FLOW_RE.finditer(text):
        s=h.end(); e=min(len(text),s+block_chars)
        blocks.append((s,e))
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in FLOW_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_participant_flow_v4(text:str, window:int=6):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    matches=find_participant_flow_v2(text,window=window)
    out=[]
    for w_s,w_e,snip in matches:
        nums_near=sum(1 for i in range(max(0,w_s-window),min(len(tokens),w_e+window)) if NUM_TOKEN_RE.fullmatch(tokens[i]))
        if nums_near>=2:
            out.append((w_s,w_e,snip))
    return out

def find_participant_flow_v5(text:str):
    return _collect([TIGHT_TEMPLATE_RE], text)

PARTICIPANT_FLOW_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1":find_participant_flow_v1,
    "v2":find_participant_flow_v2,
    "v3":find_participant_flow_v3,
    "v4":find_participant_flow_v4,
    "v5":find_participant_flow_v5,
}

__all__=["find_participant_flow_v1","find_participant_flow_v2","find_participant_flow_v3","find_participant_flow_v4","find_participant_flow_v5","PARTICIPANT_FLOW_FINDERS"]

find_participant_flow_high_recall = find_participant_flow_v1
find_participant_flow_high_precision = find_participant_flow_v5
