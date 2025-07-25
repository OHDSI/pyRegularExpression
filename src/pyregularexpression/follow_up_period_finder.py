"""follow_up_period_finder.py – precision/recall ladder for *follow‑up period* definitions.

Five variants (v1‑v5):

    • v1 – high recall: any follow‑up/followed cue
    • v2 – cue + explicit numeric duration nearby
    • v3 – only inside a *Follow‑up period / Observation period* heading block
    • v4 – v2 plus qualifier words (median/mean/followed for), excludes single‑visit traps
    • v5 – tight template: “Median follow‑up was 5 years”, “participants were followed for 24 months”, etc.

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
HYPHEN = r"[-\u2011]"  # matches ASCII hyphen or non‐breaking hyphen

FOLLOW_UP_CUE_RE = re.compile(
    rf"\b(?:follow{HYPHEN}?up|followed)\b",
    re.I,
)

DURATION_RE = re.compile(r"\b\d+\s*(?:day|week|month|year)s?\b", re.I)

QUALIFIER_RE = re.compile(r"\b(?:median|mean|average|followed\s+for)\b", re.I)

HEADING_FOLLOW_RE = re.compile(
    rf"(?m)^(?:follow{HYPHEN}?up\s+period|observation\s+period|duration\s+of\s+follow{HYPHEN}?up)\s*[:\-]?\s*$",
    re.I,
)

TRAP_RE = re.compile(
    rf"\b(?:follow{HYPHEN}?up\s+visit|clinic\s+visit|scheduled\s+follow{HYPHEN}?up)\b",
    re.I,
)

TIGHT_TEMPLATE_RE = re.compile(
    rf"(?:median|mean|average)?\s*follow{HYPHEN}?up\s+(?:was\s+)?\d+\s*(?:day|week|month|year)s?\b"
    r"|followed\s+for\s+\d+\s*(?:day|week|month|year)s?",
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

def _char_span_to_char_index(span: Tuple[int,int], text: str) -> int:
    # If you’re storing char‑spans alongside token‑spans anyway, use that.
    # But since _collect already knows the char‐span, you could also
    # return m.end() directly there instead of (w_s, w_e).
    return span[1]  # end‐char index

# ─────────────────────────────
# 3.  Finder variants
# ─────────────────────────────
def find_follow_up_period_v1(text: str) -> List[Tuple[int,int,str]]:
    # Tier 1 – high recall, but if the entire text mentions a visit-trap, bail out immediately
    if TRAP_RE.search(text):
        return []

    results: List[Tuple[int,int,str]] = []
    for m in FOLLOW_UP_CUE_RE.finditer(text):
        snippet = m.group(0)
        # 1) Skip any mini‐trap inside the match itself
        if TRAP_RE.search(snippet):
            continue
        # 2) If it’s exactly “followed”, require it to be followed by “for”
        if snippet.lower() == 'followed' and not re.match(r"\s+for\b", text[m.end():], re.I):
            continue
        # 3) Map char indices to token indices, then record
        token_spans = _token_spans(text)
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        results.append((w_s, w_e, snippet))
    return results

def find_follow_up_period_v2(text: str, window: int = 5):
    token_spans = _token_spans(text)
    # find all durations anywhere in the text, map their start positions to word‑indices
    dur_spans = [ (m.start(),m.end()) for m in DURATION_RE.finditer(text) ]
    dur_idx   = {
        _char_span_to_word_span(span, token_spans)[0]
        for span in dur_spans
    }

    out = []
    for m in FOLLOW_UP_CUE_RE.finditer(text):
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        # same window logic now sees your multi‑token durations
        if any(d for d in dur_idx if w_s - window <= d <= w_e + window):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_follow_up_period_v3(text: str, block_chars: int = 400) -> List[Tuple[int, int, str]]:
    """Tier 3 – inside Follow‑up period heading blocks."""
    token_spans = _token_spans(text)
    blocks: List[Tuple[int, int]] = []
    for h in HEADING_FOLLOW_RE.finditer(text):
        start = h.end()
        nxt_blank = text.find("\n\n", start)
        end = nxt_blank if 0 <= nxt_blank - start <= block_chars else start + block_chars
        blocks.append((start, end))
    def _inside(pos: int): return any(s <= pos < e for s, e in blocks)
    out: List[Tuple[int, int, str]] = []
    for m in FOLLOW_UP_CUE_RE.finditer(text):
        if _inside(m.start()):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_follow_up_period_v4(text: str, window: int = 6) -> List[Tuple[int, int, str]]:
    """Tier 4 – v2 + qualifier (median/mean/followed for) near cue."""
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    qual_idx = {i for i, t in enumerate(tokens) if QUALIFIER_RE.fullmatch(t)}
    matches = find_follow_up_period_v2(text, window=window)
    out: List[Tuple[int, int, str]] = []
    for w_s, w_e, snip in matches:
        if any(q for q in qual_idx if w_s - window <= q <= w_e + window):
            out.append((w_s, w_e, snip))
    return out

def find_follow_up_period_v5(text: str) -> List[Tuple[int, int, str]]:
    """Tier 5 – tight template form."""
    return _collect([TIGHT_TEMPLATE_RE], text)

# ─────────────────────────────
# 4.  Public mapping & exports
# ─────────────────────────────
FOLLOW_UP_PERIOD_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_follow_up_period_v1,
    "v2": find_follow_up_period_v2,
    "v3": find_follow_up_period_v3,
    "v4": find_follow_up_period_v4,
    "v5": find_follow_up_period_v5,
}

__all__ = [
    "find_follow_up_period_v1",
    "find_follow_up_period_v2",
    "find_follow_up_period_v3",
    "find_follow_up_period_v4",
    "find_follow_up_period_v5",
    "FOLLOW_UP_PERIOD_FINDERS",
]

# aliases
find_follow_up_period_high_recall = find_follow_up_period_v1
find_follow_up_period_high_precision = find_follow_up_period_v5
