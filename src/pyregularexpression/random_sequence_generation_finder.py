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
RAND_KEY_RE = re.compile(r"\b(?:randomi[sz]ation|randomi[sz]ed|allocation|sequence)\b", re.I)
METHOD_MOD_RE = re.compile(r"\b(?:block|blocks?|permuted|stratified|opaque\s+envelopes?|shuffled)\b", re.I)
HEADING_RAND_RE = re.compile(r"(?m)^(?:randomi[sz]ation|sequence\s+generation|allocation\s+sequence)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\brandom(?:ly)?\s+(?:assigned|selected)|random\s+sampling|random\s+effects?\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(
    r"(?:the\s+)?allocation\s+sequence(?:\s+was)?\s+computer[- ]?generated(?:\s+\w+){0,10}?\s+block\s+randomi[sz]ation",
    re.I,
)

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

def find_random_sequence_generation_v2(text:str, window:int=4):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    key_idx={i for i,t in enumerate(tokens) if RAND_KEY_RE.search(t)}
    gen_idx={i for i,t in enumerate(tokens) if GEN_CUE_RE.search(t)}
    out=[]
    for i in gen_idx:
        if any(k for k in key_idx if abs(k-i)<=window):
            w_s,w_e=_char_to_word(spans[i],spans)
            out.append((w_s,w_e,tokens[i]))
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

def find_random_sequence_generation_v4(text:str, window:int=6):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    mod_idx={i for i,t in enumerate(tokens) if METHOD_MOD_RE.fullmatch(t)}
    matches=find_random_sequence_generation_v2(text, window=window)
    out=[]
    for w_s,w_e,snip in matches:
        if any(m for m in mod_idx if w_s-window<=m<=w_e+window):
            out.append((w_s,w_e,snip))
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
