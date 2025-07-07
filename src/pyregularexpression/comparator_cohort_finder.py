
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
    r"""
    \b(                                  
        (?:control|comparator|comparison|placebo|reference)(?:\s+(?:group|arm|cohort|subjects))?|(?:intervention\s+and\s+control|control\s+and\s+intervention)\s+groups?
    )\b
    """,
    re.I | re.VERBOSE
)

GROUP_TERM_RE = re.compile(r"\b(?:cohort|group|arm)\b", re.I)

QUALIFIER_RE = re.compile(r"\b(?:unexposed|matched|reference|placebo|standard\s+care)\b", re.I)

HEADING_COMP_RE = re.compile(
    r"(?m)^(?:control\s+cohort|control\s+group|comparator\s+group|comparison\s+group|reference\s+cohort)\s*[:\-]?\s*$",
    re.I
)

DIVIDED_GROUPS_RE = re.compile(
    r"\bdivided\s+into\s+(intervention\s+and\s+control|control\s+and\s+intervention)\s+groups\b",
    re.I
)

TRAP_RE = re.compile(r"\b(?:compared\s+to|comparison\s+with|device\s+comparator|comparative\s+analysis)\b", re.I)

TIGHT_TEMPLATE_RE = re.compile(
    r"""(?x)
        (?:
            (?:matched|unexposed|reference|control)\s+(?:cohort|group)\s+
                (?:served\s+as|used\s+as|was\s+the)\s+comparator |
            (?:control\s+group)\s+comprised\s+patients\s+receiving\s+(?:placebo|standard\s+care|usual\s+care)
        )
    """,
    re.I
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

def is_quoted(token: str) -> bool:
    return re.fullmatch(r"['\"].+['\"]", token) is not None

# ─────────────────────────────
# Finder tiers
# ─────────────────────────────
def find_comparator_cohort_v1(text: str) -> List[Tuple[int, int, str]]:
    matches = []
    token_spans = _token_spans(text)
    tokens = [text[start:end] for start, end in token_spans]
    # Match regular comparator/control keywords
    for i, token in enumerate(tokens):
        if COMP_KEYWORD_RE.fullmatch(token):
            window_start = max(i - 5, 0)
            window_end = min(i + 6, len(tokens))
            window_tokens = tokens[window_start:window_end]
            if any(GROUP_TERM_RE.fullmatch(t) for t in window_tokens):
                matches.append((i, i, token))
    # Additional match for "divided into intervention and control groups"
    for m in DIVIDED_GROUPS_RE.finditer(text):
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        matches.append((w_s, w_e, m.group(0)))

    return matches

def find_comparator_cohort_v2(text: str, window: int = 15) -> List[Tuple[int, int, str]]:
    token_spans = _token_spans(text)
    tokens = [text[start:end] for start, end in token_spans]
    matches = []
    for i, token in enumerate(tokens):
        if COMP_KEYWORD_RE.search(token) and not is_quoted(token):
            # Look for nearby cohort/group word
            for j in range(max(0, i - window), min(len(tokens), i + window + 1)):
                if GROUP_TERM_RE.fullmatch(tokens[j]):
                    matches.append((i, i, token))
                    break
    return matches

def find_comparator_cohort_v3(text: str, block_chars: int = 300) -> List[Tuple[int, int, str]]:
    matches = []

    for heading_match in HEADING_COMP_RE.finditer(text):
        # Always accept the heading itself as a match
        matches.append((heading_match.start(), heading_match.end(), heading_match.group()))
    return matches

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
