"""harms_adverse_event_finder.py – precision/recall ladder for *harms / adverse events*.
Five variants (v1–v5):
    • v1 – high recall: any harms cue (adverse events, side effects, complications) followed by a number / percent.
    • v2 – v1 **and** explicit group or comparison keyword (treatment, control, placebo, vs, compared to) within ±4 tokens.
    • v3 – only inside a *Harms / Adverse Events* heading block (first ~400 characters).
    • v4 – v2 plus serious/severity descriptor (serious, severe, grade ≥3) in the same sentence.
    • v5 – tight template: “15 % headaches in treatment vs 10 % placebo; no serious events.”
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

NUM_RE = r"\d+(?:\.\d+)?%?"
NUM_TOKEN_RE = re.compile(r"^\d+(?:\.\d+)?%?$")
AE_CUE_RE = re.compile(r"\b(?:adverse\s+events?|side\s+effects?|complications?)\b", re.I)
GROUP_RE = re.compile(r"\b(?:treatment|intervention|placebo|control|arm|group|vs|versus|compared\s+to)\b", re.I)
SEVERITY_RE = re.compile(r"\b(?:serious|severe|grade\s*[3-5]|grade\s*≥\s*3|no\s+serious)\b", re.I)
HEAD_AE_RE = re.compile(r"(?m)^(?:harms?|adverse\s+events?|safety|tolerability)\s*[:\-]?\s*$", re.I)
TIGHT_TEMPLATE_RE = re.compile(rf"{NUM_RE}\s+[^,;\n]+\s+vs\s+{NUM_RE}\s+[^,;\n]+;?\s+no\s+serious\s+events", re.I)
TRAP_RE = re.compile(r"\bharm\b", re.I)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans = _token_spans(text)
    out: List[Tuple[int,int,str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.fullmatch(m.group(0)): continue
            w_s,w_e = _char_to_word((m.start(),m.end()), spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_harms_adverse_event_v1(text: str):
    pattern = re.compile(rf"{AE_CUE_RE.pattern}[^\n]{{0,20}}{NUM_RE}", re.I)
    return _collect([pattern], text)

def find_harms_adverse_event_v2(text: str, window: int = 4):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    cue_idx={i for i,t in enumerate(tokens) if AE_CUE_RE.fullmatch(t)}
    num_idx={i for i,t in enumerate(tokens) if NUM_TOKEN_RE.fullmatch(t)}
    grp_idx={i for i,t in enumerate(tokens) if GROUP_RE.fullmatch(t)}
    out=[]
    for c in cue_idx:
        if any(abs(n-c)<=window for n in num_idx) and any(abs(g-c)<=window for g in grp_idx):
            w_s,w_e=_char_to_word(spans[c],spans)
            out.append((w_s,w_e,tokens[c]))
    return out

def find_harms_adverse_event_v3(text: str, block_chars: int = 400):
    spans=_token_spans(text)
    blocks=[]
    for h in HEAD_AE_RE.finditer(text):
        s=h.end(); e=min(len(text),s+block_chars)
        blocks.append((s,e))
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in AE_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_harms_adverse_event_v4(text: str, window: int = 6):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    sev_idx={i for i,t in enumerate(tokens) if SEVERITY_RE.fullmatch(t)}
    matches=find_harms_adverse_event_v2(text, window=window)
    out=[]
    for w_s,w_e,snip in matches:
        if any(w_s-window<=s<=w_e+window for s in sev_idx):
            out.append((w_s,w_e,snip))
    return out

def find_harms_adverse_event_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

HARMS_ADVERSE_EVENT_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1": find_harms_adverse_event_v1,
    "v2": find_harms_adverse_event_v2,
    "v3": find_harms_adverse_event_v3,
    "v4": find_harms_adverse_event_v4,
    "v5": find_harms_adverse_event_v5,
}

__all__=["find_harms_adverse_event_v1","find_harms_adverse_event_v2","find_harms_adverse_event_v3","find_harms_adverse_event_v4","find_harms_adverse_event_v5","HARMS_ADVERSE_EVENT_FINDERS"]

find_harms_adverse_event_high_recall = find_harms_adverse_event_v1
find_harms_adverse_event_high_precision = find_harms_adverse_event_v5
