"""background_rationale_finder.py – precision/recall ladder for *study background / rationale* statements.
Five variants (v1–v5):
    • v1 – high recall: any gap/rationale cue (e.g., “prior studies have shown”, “however, little is known”, “important gap”, “need for this study”, “to address this”).
    • v2 – sentence containing ≥2 gap phrases **or** a gap phrase plus “study/this study” within ±4 tokens.
    • v3 – only inside an *Introduction / Background* heading block (first ~500 chars after heading).
    • v4 – v2 plus unmet‑need phrases like “little is known”, “unknown”, “not well understood”, or explicit “rationale”. Filters generic facts.
    • v5 – tight template: statement with contrast connector (yet/however) + unmet‑need phrase (little is known/unknown) + motivation (“therefore/this study aims”).
Each function returns tuples: (start_word_idx, end_word_idx, snippet).
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

TOKEN_RE = re.compile(r"\S+")

def _token_spans(text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_to_word(span: Tuple[int, int], spans: Sequence[Tuple[int, int]]):
    s, e = span
    w_s = next(i for i, (a, b) in enumerate(spans) if a <= s < b)
    w_e = next(i for i, (a, b) in reversed(list(enumerate(spans))) if a < e <= b)
    return w_s, w_e

GAP_PHRASE_RE = re.compile(
    r"\b(?:prior\s+studies\s+have\s+shown|however,?\s+little\s+is\s+known|little\s+is\s+known|important\s+gap|knowledge\s+gap|evidence\s+is\s+limited|unknown|not\s+well\s+understood|need\s+for\s+this\s+study|to\s+address\s+(?:this|these)\b|rationale\s+for)\b",
    re.I,
)
STUDY_TOKEN_RE = re.compile(r"\b(?:this\s+study|the\s+study|study|research|work|investigation)\b", re.I)
HEADING_BG_RE = re.compile(r"(?m)^(?:introduction|background)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\bbackground\s+(?:therapy|medication|characteristics?)\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(
    r"(?:however|yet)[\s,;:]{0,5}[^\.\n]{0,100}?(?:little\s+is\s+known|unknown|not\s+well\s+understood)[^\.\n]{0,100}?(?:therefore|thus|to\s+address\s+this|this\s+study\s+aims)",
    re.I
)
RATIONALE_RE = re.compile(r"\b(little\s+is\s+known|not\s+well\s+understood|unknown|knowledge\s+gap|important\s+gap)\b", re.I)
UNMET_RE = re.compile(r"\b(little\s+is\s+known|not\s+well\s+understood|unknown|knowledge\s+gap|important\s+gap)\b", re.I)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0, m.start()-20):m.end()+20]):
                continue
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_background_rationale_v1(text: str):
    return _collect([GAP_PHRASE_RE], text)

def find_background_rationale_v2(text: str, window: int = 40) -> List[Tuple[int, int, str]]:
    """
    Finds snippets of text indicating background rationale or knowledge gaps.
    Returns a list of tuples: (start_index, end_index, snippet)
    """
    matches = []
    for match in RATIONALE_RE.finditer(text):
        start, end = match.start(), match.end()
        snippet_start = max(0, start - window)
        snippet_end = min(len(text), end + window)
        snippet = text[snippet_start:snippet_end].strip()
        matches.append((start, end, snippet))
    return matches

def find_background_rationale_v3(text: str, block_chars: int = 500):
    spans = _token_spans(text)
    blocks = []
    for h in HEADING_BG_RE.finditer(text):
        s = h.end(); e = min(len(text), s + block_chars)
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in GAP_PHRASE_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_background_rationale_v4(text: str, window: int = 40) -> List[Tuple[int, int, str]]:
    """
    Version 4: builds on v2, specifically targeting 'unmet need' phrases.
    """
    out = []
    for start, end, snippet in find_background_rationale_v2(text, window=window):
        if UNMET_RE.search(snippet):
            out.append((start, end, snippet))
    return out

def find_background_rationale_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

BACKGROUND_RATIONALE_FINDERS: Dict[str, Callable[[str], List[Tuple[int,int,str]]]] = {
    "v1": find_background_rationale_v1,
    "v2": find_background_rationale_v2,
    "v3": find_background_rationale_v3,
    "v4": find_background_rationale_v4,
    "v5": find_background_rationale_v5,
}

__all__ = ["find_background_rationale_v1","find_background_rationale_v2","find_background_rationale_v3","find_background_rationale_v4","find_background_rationale_v5","BACKGROUND_RATIONALE_FINDERS"]

find_background_rationale_high_recall = find_background_rationale_v1
find_background_rationale_high_precision = find_background_rationale_v5
