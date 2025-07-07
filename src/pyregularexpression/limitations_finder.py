"""limitations_finder.py – precision/recall ladder for *study limitations* sections.
Five variants (v1–v5):
    • v1 – high recall: any limitations cue (limitations of this study, limitation, potential bias, small sample) in a sentence.
    • v2 – v1 **and** explicit self‑reference (this study/our study) or phrase “we acknowledge” near the cue.
    • v3 – only inside a *Limitations* or *Strengths and Limitations* heading block (first ~400 characters).
    • v4 – v2 plus at least one weakness keyword (bias, power, sample, generalisability, confounding) in the same sentence.
    • v5 – tight template: “Limitations include small sample and short follow‑up.”
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

LIMIT_CUE_RE = re.compile(r"\b(?:limitations?|limitation|bias|small\s+sample|underpowered)\b", re.I)
SELF_REF_RE = re.compile(r"\b(?:this\s+study|our\s+study|we\s+acknowledge|we\s+recognise)\b", re.I)
WEAKNESS_RE = re.compile(r"\b(?:bias|small\s+sample|underpowered|not\s+powered|short\s+follow[- ]up|confound(?:ing|ers?)|generalisa?bility|selection\s+bias)\b", re.I)
HEAD_LIMIT_RE = re.compile(r"(?mi)^(?:limitations|strengths?\s+and\s+limitations)\b.*", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"limitations?\s+include[s]?\s+[^\".\n]{0,80}(?:sample|follow[- ]up|bias)", re.I)
TRAP_RE = re.compile(r"\blimitations?\s+of\s+(?:previous|prior|other)\s+studies\b", re.I)
NEGATION_RE = re.compile(r"\b(?:no|not|without)\b", re.I)

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

def find_limitations_v1(text: str):
    return _collect([LIMIT_CUE_RE], text)

def find_limitations_v2(text: str, window: int = 6):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    cue_idx = {i for i, t in enumerate(tokens) if LIMIT_CUE_RE.search(t)}
    self_matches = list(SELF_REF_RE.finditer(text))
    self_idx = set()
    for m in self_matches:
        w_s, w_e = _char_to_word((m.start(), m.end()), spans)
        self_idx.update(range(w_s, w_e + 1))
    out = []
    for c in cue_idx:
        if any(abs(s - c) <= window for s in self_idx):
            w_s, w_e = _char_to_word(spans[c], spans)
            out.append((w_s, w_e, tokens[c]))
    return out

def find_limitations_v3(text: str, block_chars: int = 400):
    spans = _token_spans(text)
    blocks = []
    for h in HEAD_LIMIT_RE.finditer(text):
        line_end = text.find("\n", h.start())
        if line_end == -1:
            line_end = len(text)
        s = h.start()
        e = min(line_end + block_chars, len(text))
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in LIMIT_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_limitations_v4(text: str, window: int = 8):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    matches = find_limitations_v2(text, window=window)
    out = []
    for w_s, w_e, snip in matches:
        sent_start = max(0, w_s - 5)
        sent_end = min(len(tokens), w_e + 5)
        sentence = " ".join(tokens[sent_start:sent_end+1])
        if WEAKNESS_RE.search(sentence):
            if not NEGATION_RE.search(sentence):
                out.append((w_s, w_e, snip))
    return out

def find_limitations_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

LIMITATIONS_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1": find_limitations_v1,
    "v2": find_limitations_v2,
    "v3": find_limitations_v3,
    "v4": find_limitations_v4,
    "v5": find_limitations_v5,
}

__all__=["find_limitations_v1","find_limitations_v2","find_limitations_v3","find_limitations_v4","find_limitations_v5","LIMITATIONS_FINDERS"]

find_limitations_high_recall=find_limitations_v1
find_limitations_high_precision=find_limitations_v5
