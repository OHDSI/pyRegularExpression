"""study_design_finder.py – precision/recall ladder for *study design* declarations.

Five variants (v1–v5):

    • v1 – high recall: any design keyword (cohort, case‑control, randomized controlled trial, etc.)
    • v2 – design keyword preceded by linking phrase ("was a", "this was", “conducted as”) within ±window tokens
    • v3 – only inside a *Study design / Methods / Study type* heading block
    • v4 – v2 plus canonical design pair (e.g., “randomized controlled trial”, “prospective cohort study”) or design + temporal qualifier (prospective/retrospective)
    • v5 – tight template: “Retrospective cohort study using registry data”, “Randomized controlled trial of drug X”, etc.

Each function returns a list of tuples: (start_token_idx, end_token_idx, matched_snippet)
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

# ─────────────────────────────
# 0.  Utilities
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
DESIGN_KEYWORD_RE = re.compile(
    r"\b(?:randomi(?:s|z)ed\s+controlled\s+trial|rct|cohort\s+study|prospective\s+cohort|retrospective\s+cohort|case[- ]?control\s+study|cross[- ]?sectional\s+study|nested\s+case[- ]?control|case\s+series|case\s+report|ecological\s+study|registry\s+study)\b",
    re.I,
)

LINK_PHRASE_RE = re.compile(r"\b(?:was|were|is|study\s+was|this\s+was|conducted\s+as)\b", re.I)

CANONICAL_PAIR_RE = re.compile(
    r"\b(?:randomi(?:s|z)ed\s+controlled\s+trial|prospective\s+cohort\s+study|retrospective\s+cohort\s+study|case[- ]?control\s+study|cross[- ]?sectional\s+study)\b",
    re.I,
)

HEADING_DESIGN_RE = re.compile(r"(?m)^(?:study\s+design|methods?|design)\s*[:\-]?\s*$", re.I)

TRAP_RE = re.compile(r"\bdesign(?:ed)?\s+to\b", re.I)

TIGHT_TEMPLATE_RE = re.compile(
    r"(?:prospective|retrospective|randomi(?:s|z)ed|cross[- ]?sectional|case[- ]?control|cohort)\s+(?:cohort\s+)?study|randomi(?:s|z)ed\s+controlled\s+trial",
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
            if TRAP_RE.search(text[max(0, m.start()-20):m.end()+20]):
                continue
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

# ─────────────────────────────
# 3.  Finder tiers
# ─────────────────────────────
def find_study_design_v1(text: str) -> List[Tuple[int, int, str]]:
    return _collect([DESIGN_KEYWORD_RE], text)

def find_study_design_v2(text: str, window: int = 4) -> List[Tuple[int, int, str]]:
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    link_idx = {i for i, t in enumerate(tokens) if LINK_PHRASE_RE.fullmatch(t)}
    out = []
    for m in DESIGN_KEYWORD_RE.finditer(text):
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        if any(l for l in link_idx if w_s - window <= l <= w_e + window):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_study_design_v3(text: str, block_chars: int = 300) -> List[Tuple[int, int, str]]:
    token_spans = _token_spans(text)
    blocks = []
    for h in HEADING_DESIGN_RE.finditer(text):
        s = h.end()
        nxt = text.find("\n\n", s)
        e = nxt if 0 <= nxt - s <= block_chars else s + block_chars
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in DESIGN_KEYWORD_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_study_design_v4(text: str, window: int = 5) -> List[Tuple[int, int, str]]:
    token_spans = _token_spans(text)
    matches = find_study_design_v2(text, window)
    out = []
    for w_s, w_e, snippet in matches:
        sentence = text[max(0, text.rfind('.', 0, w_s)): text.find('.', w_e) + 1 or len(text)]
        if CANONICAL_PAIR_RE.search(sentence):
            out.append((w_s, w_e, snippet))
    return out

def find_study_design_v5(text: str) -> List[Tuple[int, int, str]]:
    return _collect([TIGHT_TEMPLATE_RE], text)

# ─────────────────────────────
# 4. Mapping & exports
# ─────────────────────────────
STUDY_DESIGN_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_study_design_v1,
    "v2": find_study_design_v2,
    "v3": find_study_design_v3,
    "v4": find_study_design_v4,
    "v5": find_study_design_v5,
}

__all__ = [
    "find_study_design_v1","find_study_design_v2","find_study_design_v3",
    "find_study_design_v4","find_study_design_v5","STUDY_DESIGN_FINDERS",
]

find_study_design_high_recall = find_study_design_v1
find_study_design_high_precision = find_study_design_v5
