"""demographic_restriction_finder.py – precision/recall ladder for demographic‑restriction statements.
Five variants (v1–v5) mirror the ladder pattern:
    • v1 – high recall (any demographic cue)
    • v2 – cue + gating verb within context window
    • v3 – only inside Eligibility/Inclusion‑style blocks
    • v4 – v2 plus guard against descriptive‑stat sentences (mean age)
    • v5 – tight template ("participants had to be …")
All functions return a list of tuples: (start_token_idx, end_token_idx, matched_snippet)
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

# ─────────────────────────────
# 0.  Shared utilities
# ─────────────────────────────
TOKEN_RE = re.compile(r"\S+")

def _token_spans(text: str) -> List[Tuple[int, int]]:
    """Return character‑level offset pairs for every non‑whitespace token."""    
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_span_to_word_span(char_span: Tuple[int, int], token_spans: Sequence[Tuple[int, int]]) -> Tuple[int, int]:
    """Convert a character slice to the *inclusive* token‑index span that covers it."""    
    s_char, e_char = char_span
    w_start = next(i for i, (s, e) in enumerate(token_spans) if s <= s_char < e)
    w_end = next(i for i, (s, e) in reversed(list(enumerate(token_spans))) if s < e_char <= e)
    return w_start, w_end

# ─────────────────────────────
# 1.  Regex assets
# ─────────────────────────────
DEMOGRAPHIC_TERM_RE = re.compile(
    r"\b(?:age(?:d)?|years?|yrs?|children|adults?|infants?|elderly|teenagers?|male[s]?|female[s]?|men|women|boys?|girls?|postmenopausal|pregnan(?:t|cy)|sex|gender|race|ethnicity|african[- ]american|black|white|caucasian|asian|hispanic|latino|indigenous|native|geograph(?:y|ical)|region|rural|urban)\b",
    re.I,
)

AGE_NUMERIC_RE = re.compile(r"\b\d{1,3}\s*(?:years?|yrs?)\b", re.I)

AGE_COMPARISON_RE = re.compile(r"\b(?:aged?|age)\s*(?:[<>]=?|at\s+least|under|over|≥|≤)\s*\d{1,3}\b", re.I)

GATING_VERB_RE = re.compile(r"\b(?:eligible|includ(?:e|ed|ing|s)|included\s+only|must\s+be|had\s+to\s+be|restricted\s+to|limited\s+to|enrol(?:led|lment)|enrolled)\b", re.I)

DESC_STATS_RE = re.compile(r"\b(?:mean|average|median)\b", re.I)

HEADING_DEMO_RE = re.compile(r"(?m)^(?:eligibility|inclusion|exclusion|participant[s]?|study\s+population)\s*[:\-]?\s*$", re.I)

# ─────────────────────────────
# 2.  Helper for collection
# ─────────────────────────────
def _collect(patterns: Sequence[re.Pattern[str]], text: str) -> List[Tuple[int, int, str]]:
    token_spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

# ─────────────────────────────
# 3.  Finder variants
# ─────────────────────────────
def find_demographic_restriction_v1(text: str) -> List[Tuple[int, int, str]]:
    """Tier 1: any demographic term or age numeric/comparison."""    
    return _collect([DEMOGRAPHIC_TERM_RE, AGE_NUMERIC_RE, AGE_COMPARISON_RE], text)

def find_demographic_restriction_v2(text: str, window: int = 5) -> List[Tuple[int, int, str]]:
    """Tier 2: demographic cue WITH a gating verb inside ±``window`` tokens."""    
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    gv_idx = {i for i, t in enumerate(tokens) if GATING_VERB_RE.search(t)}
    out: List[Tuple[int, int, str]] = []
    for patt in (DEMOGRAPHIC_TERM_RE, AGE_COMPARISON_RE, AGE_NUMERIC_RE):
        for m in patt.finditer(text):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            if any(g for g in gv_idx if w_s - window <= g <= w_e + window):
                out.append((w_s, w_e, m.group(0)))
    return out

def find_demographic_restriction_v3(text: str, block_chars: int = 400) -> List[Tuple[int, int, str]]:
    """Tier 3: same cues, but only inside Eligibility/Inclusion block headings."""    
    token_spans = _token_spans(text)
    blocks: List[Tuple[int, int]] = []
    for h in HEADING_DEMO_RE.finditer(text):
        start = h.end()
        next_blank = text.find("\n\n", start)
        end = next_blank if 0 <= next_blank - start <= block_chars else start + block_chars
        blocks.append((start, end))

    def _inside(p: int) -> bool:
        return any(s <= p < e for s, e in blocks)

    out: List[Tuple[int, int, str]] = []
    for patt in (DEMOGRAPHIC_TERM_RE, AGE_NUMERIC_RE, AGE_COMPARISON_RE):
        for m in patt.finditer(text):
            if _inside(m.start()):
                w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
                out.append((w_s, w_e, m.group(0)))
    return out

def find_demographic_restriction_v4(text: str, window: int = 5) -> List[Tuple[int, int, str]]:
    """Tier 4: like v2 but exclude sentences that look like descriptive stats (mean age)."""    
    matches = find_demographic_restriction_v2(text, window=window)
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    clean: List[Tuple[int, int, str]] = []
    for w_s, w_e, snippet in matches:
        neighbourhood = tokens[max(0, w_s - 2): w_e + 3]
        if not any(DESC_STATS_RE.fullmatch(t) for t in neighbourhood):
            clean.append((w_s, w_e, snippet))
    return clean

def find_demographic_restriction_v5(text: str) -> List[Tuple[int, int, str]]:
    """Tier 5: tight template – participants/patients had to be … (high precision)."""    
    TEMPLATE_RE = re.compile(
        rf"(?:participants?|patients?|subjects?)\s+(?:had\s+to\s+be|were|must\s+be|were\s+eligible\s+if|were\s+restricted\s+to|included\s+only)\s+(?:[^\n\.;]{{0,25}}?)?(?:{DEMOGRAPHIC_TERM_RE.pattern}|{AGE_COMPARISON_RE.pattern})",
        re.I,
    )
    return _collect([TEMPLATE_RE], text)

# ─────────────────────────────
# 4.  Public mapping & exports
# ─────────────────────────────
DEMOGRAPHIC_RESTRICTION_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_demographic_restriction_v1,
    "v2": find_demographic_restriction_v2,
    "v3": find_demographic_restriction_v3,
    "v4": find_demographic_restriction_v4,
    "v5": find_demographic_restriction_v5,
}

__all__ = [
    "find_demographic_restriction_v1",
    "find_demographic_restriction_v2",
    "find_demographic_restriction_v3",
    "find_demographic_restriction_v4",
    "find_demographic_restriction_v5",
    "DEMOGRAPHIC_RESTRICTION_FINDERS",
]

# handy aliases
find_demographics_v1 = find_demographic_restriction_v1
find_demographics_v5 = find_demographic_restriction_v5
