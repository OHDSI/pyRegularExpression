"""outcome_endpoints_finder.py – precision/recall ladder for *primary and secondary outcomes / endpoints* statements.
Five variants (v1–v5):
    • v1 – high recall: any outcome cue (primary outcome was, secondary endpoints included, outcome measures, endpoint defined as, assessed X at Y months).
    • v2 – outcome cue + measurement verb (measured, assessed, defined) within ±4 tokens **or** explicit time point (at X months/weeks).
    • v3 – only inside an *Outcome(s) / Endpoints / Outcome Measures* heading block (first ~500 characters).
    • v4 – v2 plus distinction of primary vs secondary (both terms or ordinal adjectives) in same sentence for precision.
    • v5 – tight template: “Primary outcome was progression‑free survival at 12 months; secondary outcomes included overall survival.”
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
    w_s = next(i for i, (a, b) in enumerate(spans) if a <= s < b)
    w_e = next(i for i, (a, b) in reversed(list(enumerate(spans))) if a < e <= b)
    return w_s, w_e

OUTCOME_CUE_RE = re.compile(
    r"\b(?:primary|secondary)\s+outcomes?\b|\b(?:primary|secondary)\s+endpoints?\b|"
    r"\boutcomes?\s+measures?\b|\bendpoints?\s+defined\s+as\b", re.I
)
MEASURE_VERB_RE = re.compile(r"\b(?:was|were|measured|assessed|defined|evaluated|collected)\b", re.I)
TIME_CUE_RE = re.compile(r"\bat\s+\d+\s*(?:days?|weeks?|months?|years?)\b", re.I)
HEADING_OUT_RE = re.compile(r"(?m)^(?:outcomes?|endpoints?|outcome\s+measures?)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\boutcome\s+of\s+the\s+procedure|good\s+outcome|clinical\s+outcome\s+was\s+successful\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"primary\s+(?:outcome|endpoint)\s+was\s+[^\.\n]{0,80}?\bat\s+\d+\s*(?:months?|years?|weeks?)\b[^\.\n]{0,120}?secondary\s+(?:outcomes?|endpoints?)\s+included\b", re.I)
PRIMARY_RE = re.compile(r"\bprimary\s+(?:outcome|endpoint)\b", re.I)
SECONDARY_RE = re.compile(r"\bsecondary\s+(?:outcome|endpoint|outcomes|endpoints)\b", re.I)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0, m.start()-30):m.end()+30]):
                continue
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_outcome_endpoints_v1(text: str):
    return _collect([OUTCOME_CUE_RE], text)

def find_outcome_endpoints_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    verb_idx = {i for i, t in enumerate(tokens) if MEASURE_VERB_RE.fullmatch(t) or TIME_CUE_RE.fullmatch(t)}
    out = []
    for m in OUTCOME_CUE_RE.finditer(text):
        w_s, w_e = _char_to_word((m.start(), m.end()), spans)
        if any(v for v in verb_idx if w_s - window <= v <= w_e + window):
            snippet = " ".join(tokens[w_s:w_e+1])
            out.append((w_s, w_e, snippet))
    return out

def find_outcome_endpoints_v3(text: str, block_chars: int = 500):
    spans = _token_spans(text)
    blocks = []
    for h in HEADING_OUT_RE.finditer(text):
        s = h.end(); e = min(len(text), s + block_chars)
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in OUTCOME_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_outcome_endpoints_v4(text: str, window: int = 10):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    out = []
    prim_matches = list(PRIMARY_RE.finditer(text))
    sec_matches = list(SECONDARY_RE.finditer(text))
    for p in prim_matches:
        for s in sec_matches:
            w_s, _ = _char_to_word((p.start(), p.end()), spans)
            _, w_e = _char_to_word((s.start(), s.end()), spans)
            if w_e >= w_s:  
                snippet = " ".join(tokens[w_s:w_e+1])
                out.append((w_s, w_e, snippet))
                break 
    return out

def find_outcome_endpoints_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

OUTCOME_ENDPOINTS_FINDERS: Dict[str, Callable[[str], List[Tuple[int,int,str]]]] = {
    "v1": find_outcome_endpoints_v1,
    "v2": find_outcome_endpoints_v2,
    "v3": find_outcome_endpoints_v3,
    "v4": find_outcome_endpoints_v4,
    "v5": find_outcome_endpoints_v5,
}

__all__ = ["find_outcome_endpoints_v1","find_outcome_endpoints_v2","find_outcome_endpoints_v3","find_outcome_endpoints_v4","find_outcome_endpoints_v5","OUTCOME_ENDPOINTS_FINDERS"]

find_outcome_endpoints_high_recall = find_outcome_endpoints_v1
find_outcome_endpoints_high_precision = find_outcome_endpoints_v5
