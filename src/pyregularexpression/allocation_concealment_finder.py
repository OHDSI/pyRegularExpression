"""allocation_concealment_finder.py – precision/recall ladder for *allocation concealment* methods.
Five variants (v1–v5):
    • v1 – high recall: any concealment cue (opaque sealed envelopes, central randomization, allocation concealment phrase, assignments sealed).
    • v2 – concealment cue + randomisation keyword (allocation, sequence, randomized) within ±4 tokens.
    • v3 – within an *Allocation Concealment / Randomisation* heading block.
    • v4 – v2 plus explicit descriptor (central, telephone, web-based, pharmacy-controlled, sequentially numbered) nearby.
    • v5 – tight template: “Assignments in sequentially numbered opaque envelopes ensured concealment.”
Each finder returns (start_word_idx, end_word_idx, snippet) tuples.
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

TOKEN_RE = re.compile(r"\S+" )

def _token_spans(text:str)->List[Tuple[int,int]]:
    return [(m.start(),m.end()) for m in TOKEN_RE.finditer(text)]

def _char_to_word(span:Tuple[int,int], spans:Sequence[Tuple[int,int]]):
    s,e=span
    w_s=next(i for i,(a,b) in enumerate(spans) if a<=s<b)
    w_e=next(i for i,(a,b) in reversed(list(enumerate(spans))) if a<e<=b)
    return w_s,w_e

CONCEAL_CUE_RE = re.compile(r"\b(?:opaque\s+sealed\s+envelopes?|sealed\s+opaque\s+envelopes?|sequentially\s+numbered\s+opaque\s+envelopes?|central(?:ised|ized)?\s+randomi[sz]ation|central\s+allocation|telephone\s+randomi[sz]ation|web[- ]?based\s+randomi[sz]ation|pharmacy[- ]?controlled|allocation\s+concealment)\b", re.I)
RAND_KEY_RE = re.compile(r"\b(?:allocation|sequence|randomi[sz]ed|randomi[sz]ation)\b", re.I)
DESC_RE = re.compile(r"\b(?:central(?:ised|ized)?|telephone|web[- ]?based|pharmacy[- ]?controlled|sequentially|numbered)\b", re.I)
HEADING_CONC_RE = re.compile(r"(?m)^(?:allocation\s+concealment|concealment|randomi[sz]ation)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\bconcealed\s+allocation\s+was\s+not\s+possible|blinded\s+assessors\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"assignments?\s+in\s+sequentially\s+numbered\s+opaque\s+envelopes?\s+(?:ensured|achieved)\s+allocation\s+concealment", re.I)

def _collect(patterns:Sequence[re.Pattern[str]], text:str):
    spans=_token_spans(text)
    out=[]
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0,m.start()-30):m.end()+30]):
                continue
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_allocation_concealment_v1(text:str):
    return _collect([CONCEAL_CUE_RE], text)


def find_allocation_concealment_v2(text:str, window:int=6):
    spans = _token_spans(text)
    tokens = [text[s:e] for s,e in spans]

    conc_matches = list(CONCEAL_CUE_RE.finditer(text))
    rand_matches = list(RAND_KEY_RE.finditer(text))
    rand_idx = [_char_to_word((m.start(), m.end()), spans)[0] for m in rand_matches]

    out = []
    for m in conc_matches:
        w_s, w_e = _char_to_word((m.start(), m.end()), spans)
        # Check if any randomization keyword is within ±window tokens of the concealment cue
        if any(w_s - window <= r <= w_e + window for r in rand_idx):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_allocation_concealment_v3(text:str, block_chars:int=400):
    spans=_token_spans(text)
    blocks=[]
    for h in HEADING_CONC_RE.finditer(text):
        s=h.end(); e=min(len(text),s+block_chars)
        blocks.append((s,e))
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in CONCEAL_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_allocation_concealment_v4(text:str, window:int=6):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    desc_idx={i for i,t in enumerate(tokens) if DESC_RE.fullmatch(t)}
    matches=find_allocation_concealment_v2(text, window=window)
    out=[]
    for w_s,w_e,snip in matches:
        if any(d for d in desc_idx if w_s-window<=d<=w_e+window):
            out.append((w_s,w_e,snip))
    return out

def find_allocation_concealment_v5(text:str):
    return _collect([TIGHT_TEMPLATE_RE], text)

ALLOCATION_CONCEALMENT_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1":find_allocation_concealment_v1,
    "v2":find_allocation_concealment_v2,
    "v3":find_allocation_concealment_v3,
    "v4":find_allocation_concealment_v4,
    "v5":find_allocation_concealment_v5,
}

__all__=["find_allocation_concealment_v1","find_allocation_concealment_v2","find_allocation_concealment_v3","find_allocation_concealment_v4","find_allocation_concealment_v5","ALLOCATION_CONCEALMENT_FINDERS"]

find_allocation_concealment_high_recall = find_allocation_concealment_v1
find_allocation_concealment_high_precision = find_allocation_concealment_v5
