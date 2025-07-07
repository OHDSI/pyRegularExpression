
"""study_period_finder.py – precision/recall ladder for *study period* calendar windows.

Five variants (v1–v5):

    • v1 – high recall: any date/year range pattern
    • v2 – date range + study-period cue (study/study period/from/between) within ±window tokens
    • v3 – only inside a *Study period / Study window* heading block
    • v4 – v2 plus explicit start–end keywords (from/to/between) and month name or year range; excludes follow-up traps
    • v5 – tight template: “Study period: Jan 2015–Dec 2019.”, “Data were collected between 2000 and 2005”, etc.

Each finder returns list of tuples: (start_token_idx, end_token_idx, snippet)
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

# ─────────────────────────────
# 0. Shared utilities
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
# 1. Regex assets
# ─────────────────────────────
MONTH = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
YEAR = r"(?:19|20)\d{2}"
MONTH_YEAR = rf"{MONTH}\s+{YEAR}"
DATE_RANGE_RE = re.compile(rf"(?:{MONTH_YEAR}|{YEAR})\s*(?:–|-|to|through|and|until)\s*(?:{MONTH_YEAR}|{YEAR})", re.I)

STUDY_TERM_RE = re.compile(r"\b(?:study\s+period|study\s+window|data\s+collection|study\s+years?|between|from)\b", re.I)

FROM_TO_RE = re.compile(r"\b(?:from|between)\b", re.I)

HEADING_STUDY_RE = re.compile(r"(?m)^(?:study\s+period|study\s+window|data\s+collection\s+period)\s*[:\-]?\s*$", re.I)

TRAP_RE = re.compile(r"\bfollow[- ]?up\b", re.I)

TIGHT_TEMPLATE_RE = re.compile(r"(?:study\s+period|data\s+collection)\s*[:\-]?\s+[^\.\n]{0,60}(?:\d{4}|Jan)\b[^\.\n]{0,60}", re.I)

# ─────────────────────────────
# 2. Helper
# ─────────────────────────────
def _collect(patterns: Sequence[re.Pattern[str]], text: str) -> List[Tuple[int, int, str]]:
    token_spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0, m.start()-20): m.end()+20]):
                continue
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

# ─────────────────────────────
# 3. Finder variants
# ─────────────────────────────
def find_study_period_v1(text: str) -> List[Tuple[int, int, str]]:
    """Tier 1 – any date/year range."""    
    return _collect([DATE_RANGE_RE], text)

def find_study_period_v2(text: str, window: int = 5) -> List[Tuple[int, int, str]]:
    """Tier 2 – date range + study-term cue within ±window tokens."""    
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    term_idx = {i for i, t in enumerate(tokens) if STUDY_TERM_RE.fullmatch(t)}
    out: List[Tuple[int, int, str]] = []
    for m in DATE_RANGE_RE.finditer(text):
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        if any(t for t in term_idx if w_s - window <= t <= w_e + window):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_study_period_v3(text: str, block_chars: int = 300) -> List[Tuple[int, int, str]]:
    """Tier 3 – inside Study period heading blocks."""    
    token_spans = _token_spans(text)
    blocks: List[Tuple[int, int]] = []
    for h in HEADING_STUDY_RE.finditer(text):
        start = h.end()
        nxt_blank = text.find("\n\n", start)
        end = nxt_blank if 0 <= nxt_blank - start <= block_chars else start + block_chars
        blocks.append((start, end))
    def _inside(pos: int): return any(s <= pos < e for s, e in blocks)
    out: List[Tuple[int, int, str]] = []
    for m in DATE_RANGE_RE.finditer(text):
        if _inside(m.start()):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_study_period_v4(text: str, window: int = 6) -> List[Tuple[int, int, str]]:
    """Tier 4 – v2 + explicit from/to keywords."""    
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    from_idx = {i for i, t in enumerate(tokens) if FROM_TO_RE.fullmatch(t)}
    matches = find_study_period_v2(text, window=window)
    out: List[Tuple[int, int, str]] = []
    for w_s, w_e, snip in matches:
        if any(f for f in from_idx if w_s - window <= f <= w_e + window):
            out.append((w_s, w_e, snip))
    return out

def find_study_period_v5(text: str) -> List[Tuple[int, int, str]]:
    """Tier 5 – tight template form."""    
    return _collect([TIGHT_TEMPLATE_RE], text)

# ─────────────────────────────
# 4. Public mapping & exports
# ─────────────────────────────
STUDY_PERIOD_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_study_period_v1,
    "v2": find_study_period_v2,
    "v3": find_study_period_v3,
    "v4": find_study_period_v4,
    "v5": find_study_period_v5,
}

__all__ = [
    "find_study_period_v1", "find_study_period_v2", "find_study_period_v3",
    "find_study_period_v4", "find_study_period_v5", "STUDY_PERIOD_FINDERS",
]

find_study_period_high_recall = find_study_period_v1
find_study_period_high_precision = find_study_period_v5
