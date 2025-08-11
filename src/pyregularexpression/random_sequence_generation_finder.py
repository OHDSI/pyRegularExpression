"""random_sequence_generation_finder.py – precision/recall ladder for *random allocation-sequence generation* methods.
Five variants (v1–v5):
    • v1 – high recall: any generation cue (computer-generated, random number table, coin toss, shuffled envelopes, block randomization).
    • v2 – generation cue + randomisation keyword (sequence, allocation, randomization) within ±4 tokens.
    • v3 – within a *Randomisation / Sequence Generation* heading block.
    • v4 – v2 plus explicit method modifier (block, stratified, permuted, envelopes) nearby.
    • v5 – tight template: “Allocation sequence computer-generated using block randomization (block size = 4).”
Each finder returns (start_word_idx, end_word_idx, snippet).
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

TOKEN_RE = re.compile(r"\S+")

def _token_spans(text:str)->List[Tuple[int,int]]:
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_to_word(span:Tuple[int,int], spans:Sequence[Tuple[int,int]]):
    s,e = span
    w_s = next(i for i,(a,b) in enumerate(spans) if a <= s < b)
    w_e = next(i for i,(a,b) in reversed(list(enumerate(spans))) if a < e <= b)
    return w_s, w_e

GEN_CUE_RE = re.compile(r"\b(?:computer[- ]?generated|computerised|computerized|random\s+number\s+table|coin\s+toss|shuffled\s+(?:opaque\s+)?envelopes?|sealed\s+opaque\s+envelopes?|permuted\s+block|block\s+randomi[sz]ation|stratified\s+randomi[sz]ation)\b", re.I)
RAND_KEY_RE = re.compile(r"\b(?:randomi[sz]ation|randomi[sz]ed|allocation|sequence|list)\b", re.I)
METHOD_MOD_RE = re.compile(r"\b(?:block|blocks?|permuted|stratified)\b", re.I)
HEADING_RAND_RE = re.compile(r"(?m)^(?:randomi[sz]ation|sequence\s+generation|allocation\s+sequence)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\brandom(?:ly)?\s+(?:assigned|selected)|random\s+sampling|random\s+effects?\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"allocation\s+sequence.*?computer[- ]?generated.*?block\s+randomi[sz]ation", re.I)

def _collect(patterns:Sequence[re.Pattern[str]], text:str):
    spans=_token_spans(text)
    out=[]
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0,m.start()-25):m.end()+25]):
                continue
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_random_sequence_generation_v1(text:str):
    return _collect([GEN_CUE_RE], text)

def find_random_sequence_generation_v2(text:str, window:int=80): # window in chars
    spans=_token_spans(text)
    gen_matches = list(GEN_CUE_RE.finditer(text))
    key_matches = list(RAND_KEY_RE.finditer(text))
    out=[]
    for g in gen_matches:
        if TRAP_RE.search(text[max(0,g.start()-25):g.end()+25]):
            continue
        for k in key_matches:
            # check if the spans are close
            if abs(g.start() - k.end()) < window or abs(k.start() - g.end()) < window:
                w_s,w_e=_char_to_word((g.start(),g.end()),spans)
                out.append((w_s,w_e,g.group(0)))
                break # avoid duplicates
    return out

def find_random_sequence_generation_v3(text:str, block_chars:int=400):
    spans=_token_spans(text)
    blocks=[]
    for h in HEADING_RAND_RE.finditer(text):
        s=h.end(); e=min(len(text), s+block_chars)
        blocks.append((s,e))
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in GEN_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_random_sequence_generation_v4(text:str, window:int=80): # window in chars
    spans=_token_spans(text)
    mod_matches = list(METHOD_MOD_RE.finditer(text))
    v2_matches = find_random_sequence_generation_v2(text) # uses window=80 by default
    out = []
    for w_s, w_e, snip in v2_matches:
        v2_start_char = spans[w_s][0]
        v2_end_char = spans[w_e][1]
        for m in mod_matches:
            # check if the v2 match and the modifier match are close
            if abs(v2_start_char - m.end()) < window or abs(m.start() - v2_end_char) < window:
                out.append((w_s, w_e, snip))
                break
    return out

def find_random_sequence_generation_v5(text:str):
    return _collect([TIGHT_TEMPLATE_RE], text)

RANDOM_SEQUENCE_GENERATION_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1":find_random_sequence_generation_v1,
    "v2":find_random_sequence_generation_v2,
    "v3":find_random_sequence_generation_v3,
    "v4":find_random_sequence_generation_v4,
    "v5":find_random_sequence_generation_v5,
}

__all__=["find_random_sequence_generation_v1","find_random_sequence_generation_v2","find_random_sequence_generation_v3","find_random_sequence_generation_v4","find_random_sequence_generation_v5","RANDOM_SEQUENCE_GENERATION_FINDERS"]

find_random_sequence_generation_high_recall = find_random_sequence_generation_v1
find_random_sequence_generation_high_precision = find_random_sequence_generation_v5
