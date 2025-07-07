"""subgroup_analysis_finder.py – precision/recall ladder for *subgroup / interaction analyses*.
Five variants (v1–v5):
    • v1 – high recall: any subgroup cue (subgroup analysis, effect modification, interaction term, tested in strata, stratified analysis).
    • v2 – v1 **and** analytic verb (tested, assessed, explored, evaluated, performed) within ±4 tokens of the cue.
    • v3 – only inside a *Subgroup Analysis / Effect Modification / Interaction* heading block (first ≈400 characters).
    • v4 – v2 plus explicit interaction/heterogeneity keyword (P-interaction, heterogeneity, effect modification) in the same sentence.
    • v5 – tight template: “Subgroup analyses showed stronger effect in women <50 y (P-interaction = 0.02).”
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

SG_CUE_RE = re.compile(r"\b(?:subgroup\s+analyses?|subgroup\s+analysis|effect\s+modification|interaction\s+term|tested\s+in\s+strata|stratified\s+analysis)\b", re.I)
VERB_RE = re.compile(r"\b(?:tested|assessed|explored|evaluated|performed|conducted|examined)\b", re.I)
INT_KEY_RE = re.compile(r"\b(?:p[- ]?interaction|interaction\s+p[- ]?value|heterogeneity|effect\s+modification)\b", re.I)
HEAD_SG_RE = re.compile(r"(?m)^(?:subgroup\s+analysis(?:es)?|effect\s+modification|interaction\s+analysis)\s*[:\-]?\s*$", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"subgroup\s+analyses?[^\.\n]{0,60}p[- ]?interaction", re.I)
TRAP_RE = re.compile(r"\bbaseline\s+subgroup|subgroup\s+of\s+patients\s+were\s+older\b", re.I)

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

def find_subgroup_analysis_v1(text: str):
    return _collect([SG_CUE_RE], text)

def find_subgroup_analysis_v2(text: str, window: int = 4):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    cue_idx={i for i,t in enumerate(tokens) if SG_CUE_RE.fullmatch(t)}
    verb_idx={i for i,t in enumerate(tokens) if VERB_RE.fullmatch(t)}
    out=[]
    for c in cue_idx:
        if any(abs(v-c)<=window for v in verb_idx):
            w_s,w_e=_char_to_word(spans[c],spans)
            out.append((w_s,w_e,tokens[c]))
    return out

def find_subgroup_analysis_v3(text: str, block_chars: int = 400):
    spans=_token_spans(text)
    blocks=[(h.end(),min(len(text),h.end()+block_chars)) for h in HEAD_SG_RE.finditer(text)]
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in SG_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_subgroup_analysis_v4(text: str, window: int = 6):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    key_idx={i for i,t in enumerate(tokens) if INT_KEY_RE.fullmatch(t)}
    matches=find_subgroup_analysis_v2(text, window=window)
    out=[]
    for w_s,w_e,snip in matches:
        if any(w_s-window<=k<=w_e+window for k in key_idx):
            out.append((w_s,w_e,snip))
    return out

def find_subgroup_analysis_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

SUBGROUP_ANALYSIS_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1": find_subgroup_analysis_v1,
    "v2": find_subgroup_analysis_v2,
    "v3": find_subgroup_analysis_v3,
    "v4": find_subgroup_analysis_v4,
    "v5": find_subgroup_analysis_v5,
}

__all__=["find_subgroup_analysis_v1","find_subgroup_analysis_v2","find_subgroup_analysis_v3","find_subgroup_analysis_v4","find_subgroup_analysis_v5","SUBGROUP_ANALYSIS_FINDERS"]

find_subgroup_analysis_high_recall=find_subgroup_analysis_v1
find_subgroup_analysis_high_precision=find_subgroup_analysis_v5
