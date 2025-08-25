"""missing_data_handling_finder.py – precision/recall ladder for *missing‑data handling methods*.
Five variants (v1–v5):
    • v1 – high recall: any missing‑data cue (missing data were, imputed, multiple imputation, complete‑case analysis, LOCF, last observation carried forward) in a sentence.
    • v2 – v1 **and** analysis verb (imputed, handled, performed, used, applied) within ±4 tokens of cue.
    • v3 – only inside a *Missing Data / Imputation* heading block (first ~400 characters).
    • v4 – v2 plus explicit technique keyword (multiple imputation, chained equations, MICE, LOCF, complete‑case, maximum likelihood) in same sentence.
    • v5 – tight template: “Missing covariates were imputed using chained equations (mice).”
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

MISS_CUE_RE = re.compile(r"\b(?:missing\s+data|imputed|imputation|complete[- ]case|last\s+observation\s+carried\s+forward|locf|mice|multiple\s+imputation)\b", re.I)
VERB_RE = re.compile(r"\b(?:imputed|handled|performed|used|applied|conducted)\b", re.I)
TECH_RE = re.compile(r"\b(?:multiple\s+imputation|chained\s+equations|mice|locf|last\s+observation\s+carried\s+forward|complete[- ]case|maximum\s+likelihood|inverse\s+probability\s+weighting|pattern\s+mixture)\b", re.I)
HEAD_MISS_RE = re.compile(r"(?m)^(?:missing\s+data|imputation|handling\s+of\s+missing|data\s+imputation)\s*[:\-]?\s*$", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"missing[^\.\n]{0,20}imputed[^\.\n]{0,40}(?:chained\s+equations|mice|multiple\s+imputation)", re.I)
TRAP_RE = re.compile(r"\bmissing\s+values?\s+reported|percent\s+missing\b", re.I)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans=_token_spans(text)
    out: List[Tuple[int,int,str]]=[]
    for patt in patterns:
        for m in patt.finditer(text):
            context=text[max(0,m.start()-30):m.end()+30]
            if TRAP_RE.search(context):
                continue
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_missing_data_handling_v1(text: str):
    return _collect([MISS_CUE_RE], text)

def find_missing_data_handling_v2(text: str, window: int = 4):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    cue_idx={i for i,t in enumerate(tokens) if MISS_CUE_RE.search(t)}
    verb_idx={i for i,t in enumerate(tokens) if VERB_RE.search(t)}
    out=[]
    for c in cue_idx:
        if any(abs(v-c)<=window for v in verb_idx):
            w_s,w_e=_char_to_word(spans[c],spans)
            out.append((w_s,w_e,tokens[c]))
    return out

def find_missing_data_handling_v3(text: str, block_chars: int = 400):
    spans=_token_spans(text)
    blocks=[]
    for h in HEAD_MISS_RE.finditer(text):
        s=h.end(); e=min(len(text),s+block_chars)
        blocks.append((s,e))
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in MISS_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_missing_data_handling_v4(text: str, window: int = 6):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    tech_idx={i for i,t in enumerate(tokens) if TECH_RE.search(t)}
    matches=find_missing_data_handling_v2(text, window=window)
    out=[]
    for w_s,w_e,snip in matches:
        if any(w_s-window<=t<=w_e+window for t in tech_idx):
            out.append((w_s,w_e,snip))
    return out

def find_missing_data_handling_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

MISSING_DATA_HANDLING_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1": find_missing_data_handling_v1,
    "v2": find_missing_data_handling_v2,
    "v3": find_missing_data_handling_v3,
    "v4": find_missing_data_handling_v4,
    "v5": find_missing_data_handling_v5,
}

__all__=["find_missing_data_handling_v1","find_missing_data_handling_v2","find_missing_data_handling_v3","find_missing_data_handling_v4","find_missing_data_handling_v5","MISSING_DATA_HANDLING_FINDERS"]

find_missing_data_handling_high_recall=find_missing_data_handling_v1
find_missing_data_handling_high_precision=find_missing_data_handling_v5
