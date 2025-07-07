"""data_linkage_method_finder.py – precision/recall ladder for *data‑linkage methods*.
Five variants (v1–v5):
    • v1 – high recall: sentence mentioning linkage cues ("records were linked", "data linkage", "linked files", master patient index) regardless of context.
    • v2 – v1 **and** object keywords (records/data/files/registries/datasets) within ±3 tokens of “linkage/linked”.
    • v3 – only inside a *Data Linkage / Record Linkage / Matching* heading block (first ≈400 characters).
    • v4 – v2 plus explicit method term (probabilistic, deterministic, exact match, fuzzy match, hashed, master patient index, MPI).
    • v5 – tight template: “Hospital admissions were probabilistically linked to death‑registry data using date of birth and NHS number.”
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

LINK_CUE_RE   = re.compile(r"\b(?:linkage|linked|linking|match(?:ed|ing)?)\b", re.I)
OBJ_RE        = re.compile(r"\b(?:records?|data(?:sets?)?|files?|registries|registry|databases?)\b", re.I)
METHOD_RE     = re.compile(r"\b(?:probabilistic|deterministic|exact\s+match|fuzzy\s+match|hashed|token[- ]?based|master\s+patient\s+index|MPI)\b", re.I)
HEAD_LINK_RE  = re.compile(r"(?m)^(?:data\s+linkage|record\s+linkage|data\s+matching|linkage\s+method)\s*[:\-]?\s*$", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"probabilistic(?:ally)?\s+linked\s+.+?registry|deterministic\s+match", re.I)

TRAP_RE = re.compile(r"\blink\s+between|link\s+to\s+outcome|hyperlink|website\s+link\b", re.I)

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

def find_data_linkage_method_v1(text: str):
    return _collect([LINK_CUE_RE], text)

def find_data_linkage_method_v2(text: str, window: int = 3):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    link_idx={i for i,t in enumerate(tokens) if LINK_CUE_RE.fullmatch(t)}
    obj_idx ={i for i,t in enumerate(tokens) if OBJ_RE.fullmatch(t)}
    out=[]
    for l in link_idx:
        if any(abs(o-l)<=window for o in obj_idx):
            w_s,w_e=_char_to_word(spans[l],spans)
            out.append((w_s,w_e,tokens[l]))
    return out

def find_data_linkage_method_v3(text: str, block_chars: int = 400):
    spans=_token_spans(text)
    blocks=[(h.end(),min(len(text),h.end()+block_chars)) for h in HEAD_LINK_RE.finditer(text)]
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in LINK_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_data_linkage_method_v4(text: str, window: int = 6):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    meth_idx={i for i,t in enumerate(tokens) if METHOD_RE.fullmatch(t)}
    matches=find_data_linkage_method_v2(text, window=window)
    out=[]
    for w_s,w_e,snip in matches:
        if any(w_s-window<=m<=w_e+window for m in meth_idx):
            out.append((w_s,w_e,snip))
    return out

def find_data_linkage_method_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

DATA_LINKAGE_METHOD_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1": find_data_linkage_method_v1,
    "v2": find_data_linkage_method_v2,
    "v3": find_data_linkage_method_v3,
    "v4": find_data_linkage_method_v4,
    "v5": find_data_linkage_method_v5,
}

__all__=[
    "find_data_linkage_method_v1","find_data_linkage_method_v2","find_data_linkage_method_v3",
    "find_data_linkage_method_v4","find_data_linkage_method_v5","DATA_LINKAGE_METHOD_FINDERS"
]

find_data_linkage_method_high_recall=find_data_linkage_method_v1
find_data_linkage_method_high_precision=find_data_linkage_method_v5
