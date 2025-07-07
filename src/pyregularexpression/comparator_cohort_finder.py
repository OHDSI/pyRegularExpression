
"""comparator_cohort_finder.py – precision/recall ladder for *comparator (control) cohort* statements.
Five variants (v1–v5):
    • v1 – high recall: any comparator/control keyword
    • v2 – comparator keyword + group/cohort term within ±window tokens
    • v3 – only inside a *Comparator / Control cohort* heading block
    • v4 – v2 plus explicit qualifier (unexposed, matched, reference) excluding generic comparisons
    • v5 – tight template: “Matched unexposed cohort served as comparator”, “Control group comprised patients receiving placebo”, etc.
Each finder returns a list of tuples: (start_token_idx, end_token_idx, matched_snippet)
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

# ─────────────────────────────
# Utilities
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
# Regex assets
# ─────────────────────────────
COMP_KEYWORD_RE = re.compile(
    r"\b(?:comparator\s+cohort|comparison\s+cohort|control\s+group|control\s+cohort|reference\s+group|reference\s+cohort|unexposed\s+cohort|matched\s+cohort)\b",
    re.I,
)

GROUP_TERM_RE = re.compile(r"\b(?:cohort|group|arm)\b", re.I)

QUALIFIER_RE = re.compile(r"\b(?:unexposed|matched|reference|placebo|standard\s+care)\b", re.I)

HEADING_COMP_RE = re.compile(r"(?m)^(?:comparator\s+cohort|control\s+group|comparison\s+group|reference\s+cohort)\s*[:\-]?\s*$", re.I)

TRAP_RE = re.compile(r"\b(?:compared\s+to|comparison\s+with|device\s+comparator|comparative\s+analysis)\b", re.I)

TIGHT_TEMPLATE_RE = re.compile(
    r"(?:matched|unexposed|reference|control)\s+(?:cohort|group)\s+(?:served\s+as|used\s+as|was\s+the)\s+comparator",
    re.I,
)

# ─────────────────────────────
# Helper
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
# Finder tiers
# ─────────────────────────────
def find_comparator_cohort_v1(text: str) -> List[Tuple[int, int, str]]:
    return _collect([COMP_KEYWORD_RE], text)

def find_comparator_cohort_v2(text: str, window: int = 5) -> List[Tuple[int, int, str]]:
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    grp_idx = {i for i, t in enumerate(tokens) if GROUP_TERM_RE.fullmatch(t)}
    out: List[Tuple[int, int, str]] = []
    for m in COMP_KEYWORD_RE.finditer(text):
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        if any(g for g in grp_idx if w_s - window <= g <= w_e + window):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_comparator_cohort_v3(text: str, block_chars: int = 300) -> List[Tuple[int, int, str]]:
    token_spans = _token_spans(text)
    blocks: List[Tuple[int, int]] = []
    for h in HEADING_COMP_RE.finditer(text):
        s = h.end()
        nxt = text.find("\n\n", s)
        e = nxt if 0 <= nxt - s <= block_chars else s + block_chars
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out: List[Tuple[int, int, str]] = []
    for m in COMP_KEYWORD_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_comparator_cohort_v4(text: str, window: int = 6) -> List[Tuple[int, int, str]]:
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    qual_idx = {i for i, t in enumerate(tokens) if QUALIFIER_RE.fullmatch(t)}
    matches = find_comparator_cohort_v2(text, window=window)
    out: List[Tuple[int, int, str]] = []
    for w_s, w_e, snippet in matches:
        if any(q for q in qual_idx if w_s - window <= q <= w_e + window):
            out.append((w_s, w_e, snippet))
    return out

def find_comparator_cohort_v5(text: str) -> List[Tuple[int, int, str]]:
    return _collect([TIGHT_TEMPLATE_RE], text)

# ─────────────────────────────
# Mapping & exports
# ─────────────────────────────
COMPARATOR_COHORT_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_comparator_cohort_v1,
    "v2": find_comparator_cohort_v2,
    "v3": find_comparator_cohort_v3,
    "v4": find_comparator_cohort_v4,
    "v5": find_comparator_cohort_v5,
}

__all__ = [
    "find_comparator_cohort_v1","find_comparator_cohort_v2","find_comparator_cohort_v3",
    "find_comparator_cohort_v4","find_comparator_cohort_v5","COMPARATOR_COHORT_FINDERS",
]

find_comparator_cohort_high_recall = find_comparator_cohort_v1
find_comparator_cohort_high_precision = find_comparator_cohort_v5
