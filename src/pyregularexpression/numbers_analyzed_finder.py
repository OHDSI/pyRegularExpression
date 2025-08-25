"""numbers_analyzed_finder.py – precision/recall ladder for *numbers analysed* in each analysis population.
Five variants (v1–v5):
    • v1 – high recall: any analysis‑count cue (participants analysed, analysed, included in analysis, n = …) plus a number.
    • v2 – v1 **and** explicit group keyword (treatment, control, placebo, intervention, arm, group) within ±4 tokens.
    • v3 – only inside a *Numbers Analysed / Analysis Population* heading block (first ~400 characters).
    • v4 – v2 plus analysis‑set label (intention‑to‑treat, ITT, per‑protocol, PP, safety set) in the same sentence.
    • v5 – tight template: “98 intervention and 102 control participants analysed (ITT).”
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

NUM_RE = r"\d{1,5}"
NUM_TOKEN_RE = re.compile(r"^\d{1,5}$")
ANALYZE_CUE_RE = re.compile(r"\b(?:analys(?:ed|is)|included\s+in\s+analysis|participants?\s+analys(?:ed|is)|evaluated|assessed)\b", re.I)
N_EQUALS_RE = re.compile(r"n\s*=\s*\d+", re.I)
GROUP_RE = re.compile(r"\b(?:treatment|intervention|placebo|control|arm|group|cohort)\b", re.I)
POP_RE = re.compile(r"\b(?:intention[- ]to[- ]treat|itt|per[- ]protocol|pp|safety\s+set)\b", re.I)
HEAD_COUNT_RE = re.compile(r"(?m)^(?:numbers?\s+analys(?:ed|ed)|analysis\s+population|participants?\s+analys(?:ed|is))\s*[:\-]?\s*$", re.I)
TIGHT_TEMPLATE_RE = re.compile(rf"{NUM_RE}\s+[^ ,;]+\s+and\s+{NUM_RE}\s+[^ ,;]+\s+participants?\s+analys(?:ed|is).*?(?:itt|intention[- ]to[- ]treat)", re.I)
TRAP_RE = re.compile(r"\benrolled|recruited|randomi[sz]ed\b", re.I)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans=_token_spans(text)
    out: List[Tuple[int,int,str]]=[]
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0,m.start()-20):m.end()+20]):
                continue
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_numbers_analyzed_v1(text: str):
    pattern = re.compile(rf"(?:{ANALYZE_CUE_RE.pattern}|{N_EQUALS_RE.pattern})(?:[^\n]{{0,15}}{NUM_RE})?", re.I)
    return _collect([pattern], text)

def find_numbers_analyzed_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    tokens = [text[s:e] for s,e in spans]
    matches = []
    for m in _collect([ANALYZE_CUE_RE, N_EQUALS_RE], text):
        cue_start, cue_end, cue_snip = m
        for i, t in enumerate(tokens):
            if GROUP_RE.search(t):
                if abs(i - cue_start) <= window or abs(i - cue_end) <= window:
                    matches.append(m)
                    break
    return matches

def find_numbers_analyzed_v3(text: str, block_chars: int = 400):
    spans=_token_spans(text)
    blocks=[]
    for h in HEAD_COUNT_RE.finditer(text):
        s=h.end(); e=min(len(text),s+block_chars)
        blocks.append((s,e))
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in ANALYZE_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_numbers_analyzed_v4(text: str, window: int = 6):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    pop_idx={i for i,t in enumerate(tokens) if POP_RE.search(t)}
    matches=find_numbers_analyzed_v2(text, window=window)
    out=[]
    for w_s,w_e,snip in matches:
        if any(w_s-window<=p<=w_e+window for p in pop_idx):
            out.append((w_s,w_e,snip))
    return out

def find_numbers_analyzed_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

NUMBERS_ANALYZED_FINDERS: Dict[str, Callable[[str], List[Tuple[int,int,str]]]] = {
    "v1": find_numbers_analyzed_v1,
    "v2": find_numbers_analyzed_v2,
    "v3": find_numbers_analyzed_v3,
    "v4": find_numbers_analyzed_v4,
    "v5": find_numbers_analyzed_v5,
}

__all__ = ["find_numbers_analyzed_v1","find_numbers_analyzed_v2","find_numbers_analyzed_v3","find_numbers_analyzed_v4","find_numbers_analyzed_v5","NUMBERS_ANALYZED_FINDERS"]

find_numbers_analyzed_high_recall = find_numbers_analyzed_v1
find_numbers_analyzed_high_precision = find_numbers_analyzed_v5
