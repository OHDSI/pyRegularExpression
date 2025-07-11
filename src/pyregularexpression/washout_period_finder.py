
"""washout_period_finder.py – precision/recall ladder for *washout period* definitions.
Five variants (v1‑v5):
    • v1 – high recall: any washout/run‑in/drug‑free cue
    • v2 – cue + explicit duration (months / weeks / years) or “drug‑free / treatment‑free” within ±window tokens
    • v3 – only inside a *Washout period / Clearance period / Run‑in* heading block
    • v4 – v2 plus temporal anchor before index/baseline (before / prior to / preceding), excludes side‑effect stoppage traps
    • v5 – tight template: “12‑month washout with no antihypertensives”, “patients were drug‑free for 6 months before index”, etc.
Each function returns a list of tuples: (start_token_idx, end_token_idx, matched_snippet)
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

# ─────────────────────────────
# 0.  Shared utilities
# ─────────────────────────────
TOKEN_RE = re.compile(r"\S+")

def _token_spans(text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_span_to_word_span(span: Tuple[int, int], token_spans: Sequence[Tuple[int, int]]) -> Tuple[int, int]:
    s_char, e_char = span
    w_start = next(i for i, (s, e) in enumerate(token_spans) if s <= s_char < e)
    w_end = next(i for i, (s, e) in reversed(list(enumerate(token_spans))) if s < e_char <= e)
    return w_start, w_end

# ─────────────────────────────
# 1.  Regex assets
# ─────────────────────────────
WASHOUT_CUE_RE = re.compile(
    r"\b(?:washout\s+period|washout|run[- ]?in|clearance\s+period|drug[- ]?free|treatment[- ]?free|no\s+therapy)\b",
    re.I,
)

DURATION_RE = re.compile(r"\b\d+\s*(?:day|week|month|year)s?\b", re.I)

BEFORE_ANCHOR_RE = re.compile(r"\b(?:before|prior\s+to|preceding|pre[- ]index|pre[- ]baseline)\b", re.I)

HEADING_WASHOUT_RE = re.compile(r"(?m)^(?:washout\s+period|run[- ]?in|clearance\s+period)\s*[:\-]?\s*$", re.I)

TRAP_RE = re.compile(r"\b(?:stopped|discontinued|due\s+to\s+side[- ]?effects|adverse\s+events?)\b", re.I)

TIGHT_TEMPLATE_RE = re.compile(
    r"(?:\d+\s*(?:month|week|year)s?\s+washout\s+(?:period\s+)?with\s+no\s+[A-Za-z\s]{1,40}|drug[- ]?free\s+for\s+\d+\s*(?:month|week|year)s?\s+before\s+index)",
    re.I,
)

# ─────────────────────────────
# 2.  Helper
# ─────────────────────────────
def _collect(patterns: Sequence[re.Pattern[str]], text: str) -> List[Tuple[int, int, str]]:
    token_spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(m.group(0)):
                continue
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

# ─────────────────────────────
# 3.  Finder variants
# ─────────────────────────────
def find_washout_period_v1(text: str) -> List[Tuple[int, int, str]]:
    """Tier 1 – any washout/run‑in cue."""    
    return _collect([WASHOUT_CUE_RE], text)

def find_washout_period_v2(text: str, window: int = 5) -> List[Tuple[int, int, str]]:
    """Tier 2 – cue + duration or ‘drug‑free’ phrase nearby."""    
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    dur_idx = {i for i, t in enumerate(tokens) if DURATION_RE.fullmatch(t)}
    out: List[Tuple[int, int, str]] = []
    for m in WASHOUT_CUE_RE.finditer(text):
        if TRAP_RE.search(text[max(0, m.start()-30):m.end()+30]):
            continue
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        if any(d for d in dur_idx if w_s - window <= d <= w_e + window):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_washout_period_v3(text: str, block_chars: int = 400) -> List[Tuple[int, int, str]]:
    """Tier 3 – inside Washout / Run‑in heading blocks."""    
    token_spans = _token_spans(text)
    blocks: List[Tuple[int, int]] = []
    for h in HEADING_WASHOUT_RE.finditer(text):
        start = h.end()
        nxt_blank = text.find("\n\n", start)
        end = nxt_blank if 0 <= nxt_blank - start <= block_chars else start + block_chars
        blocks.append((start, end))
    def _inside(p): return any(s <= p < e for s, e in blocks)
    out: List[Tuple[int, int, str]] = []
    for m in WASHOUT_CUE_RE.finditer(text):
        if _inside(m.start()):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_washout_period_v4(text: str, window: int = 6) -> List[Tuple[int, int, str]]:
    """Tier 4 – v2 + temporal anchor before index/baseline."""    
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    anchor_idx = {i for i, t in enumerate(tokens) if BEFORE_ANCHOR_RE.fullmatch(t)}
    matches = find_washout_period_v2(text, window=window)
    out: List[Tuple[int, int, str]] = []
    for w_s, w_e, snip in matches:
        if any(a for a in anchor_idx if w_s - window <= a <= w_e + window):
            out.append((w_s, w_e, snip))
    return out

def find_washout_period_v5(text: str) -> List[Tuple[int, int, str]]:
    """Tier 5 – tight template with duration and drug‑free cue."""    
    return _collect([TIGHT_TEMPLATE_RE], text)

# ─────────────────────────────
# 4.  Public mapping & exports
# ─────────────────────────────
WASHOUT_PERIOD_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_washout_period_v1,
    "v2": find_washout_period_v2,
    "v3": find_washout_period_v3,
    "v4": find_washout_period_v4,
    "v5": find_washout_period_v5,
}

__all__ = [
    "find_washout_period_v1",
    "find_washout_period_v2",
    "find_washout_period_v3",
    "find_washout_period_v4",
    "find_washout_period_v5",
    "WASHOUT_PERIOD_FINDERS",
]

# handy aliases
find_washout_period_high_recall = find_washout_period_v1
find_washout_period_high_precision = find_washout_period_v5
