"""event_adjudication_finder.py – precision/recall ladder for *event‑adjudication descriptions*.
Five variants (v1–v5):
    • v1 – high recall: any sentence with adjudication cues ("events were adjudicated", "clinical events committee", CEC, "endpoint committee", blinded adjudicators).
    • v2 – v1 **and** object keyword (event/endpoint) within ±5 tokens of “adjudicat*”.
    • v3 – only inside an *Event Adjudication / Clinical Events Committee / Endpoint Committee* heading block (first ≈400 characters).
    • v4 – v2 plus explicit independence/blinding term (independent, blinded) **or** committee acronym (CEC, DSMB) in the same sentence.
    • v5 – tight template: “All MI events were independently adjudicated by a blinded CEC.”
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

ADJ_CUE_RE   = re.compile(r"\b(adjudicat(?:e|ed|ion|ing))\b", re.I)
OBJ_RE       = re.compile(r"\b(?:events?|endpoints?)\b", re.I)
COMM_RE      = re.compile(r"\b(?:clinical\s+events?\s+committee|endpoint\s+committee|CEC|DSMB|DMC)\b", re.I)
BLIND_RE     = re.compile(r"\b(?:blinded|independent(?:ly)?|masked)\b", re.I)
HEAD_ADJ_RE  = re.compile(r"(?m)^(?:event\s+adjudication|clinical\s+events?\s+committee|endpoint\s+committee)\s*[:\-]?\s*$", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"independent(?:ly)?\s+adjudicated.+?CEC", re.I)

TRAP_RE = re.compile(r"\blegal\s+adjudicat|court\s+adjudicat|dispute\s+adjudicat\b", re.I)

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

def find_event_adjudication_v1(text: str):
    return _collect([ADJ_CUE_RE, COMM_RE], text)

def find_event_adjudication_v2(text: str, window: int = 5):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    cue_idx={i for i,t in enumerate(tokens) if ADJ_CUE_RE.search(t)}
    obj_idx={i for i,t in enumerate(tokens) if OBJ_RE.search(t)}
    out=[]
    for c in cue_idx:
        if any(abs(o-c)<=window for o in obj_idx):
            w_s,w_e=_char_to_word(spans[c],spans)
            out.append((w_s,w_e,tokens[c]))
    return out

def find_event_adjudication_v3(text: str, block_chars: int = 400):
    spans=_token_spans(text)
    blocks=[(h.end(),min(len(text),h.end()+block_chars)) for h in HEAD_ADJ_RE.finditer(text)]
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in ADJ_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_event_adjudication_v4(text: str, window: int = 6):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    extra_idx={i for i,t in enumerate(tokens) if COMM_RE.fullmatch(t) or BLIND_RE.fullmatch(t)}
    matches=find_event_adjudication_v2(text, window=window)
    out=[]
    for w_s,w_e,snip in matches:
        if any(w_s-window<=k<=w_e+window for k in extra_idx):
            out.append((w_s,w_e,snip))
    return out

def find_event_adjudication_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

EVENT_ADJUDICATION_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1": find_event_adjudication_v1,
    "v2": find_event_adjudication_v2,
    "v3": find_event_adjudication_v3,
    "v4": find_event_adjudication_v4,
    "v5": find_event_adjudication_v5,
}

__all__=[
    "find_event_adjudication_v1","find_event_adjudication_v2","find_event_adjudication_v3",
    "find_event_adjudication_v4","find_event_adjudication_v5","EVENT_ADJUDICATION_FINDERS"
]

find_event_adjudication_high_recall=find_event_adjudication_v1
find_event_adjudication_high_precision=find_event_adjudication_v5
