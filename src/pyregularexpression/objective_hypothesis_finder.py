"""objective_hypothesis_finder.py – precision/recall ladder for *study objectives / hypotheses* statements.
Five variants (v1–v5):
    • v1 – high recall: any objective/aim/hypothesis cue (e.g., “the aim of this study”, “we aimed to”, “our objective was”, “we hypothesize that”, “to determine whether”).
    • v2 – objective/aim cue + verb tense (was/were/aimed) within ±3 tokens **or** hypothesis phrase (“we hypothesize/hypothesized that”).
    • v3 – only inside an *Objectives / Aims / Purpose* heading block.
    • v4 – v2 plus explicit study reference token (“this study”, “the study”) to avoid generic uses like “objective measurement”.
    • v5 – tight template: “The objective of this study was to assess…”, “We hypothesized that exposure X increases risk Y…”.

Each function returns tuples: (start_word_idx, end_word_idx, snippet).
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

# ─────────────────────────────
# Token utilities
# ─────────────────────────────
TOKEN_RE = re.compile(r"\S+")

def _token_spans(text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_to_word(span: Tuple[int, int], spans: Sequence[Tuple[int, int]]):
    s, e = span
    w_s = next(i for i, (a, b) in enumerate(spans) if a <= s < b)
    w_e = next(i for i, (a, b) in reversed(list(enumerate(spans))) if a < e <= b)
    return w_s, w_e

# ─────────────────────────────
# Regex assets
# ─────────────────────────────
OBJ_CUE_RE = re.compile(
    r"\b(?:the\s+aim\s+of\s+this\s+study|we\s+aim(?:ed)?\s+to|our\s+objective\s+was|the\s+objective\s+of\s+this\s+study|this\s+study\s+seeks\s+to|purpose\s+of\s+this\s+study|to\s+determine\s+whether)\b",
    re.I | re.UNICODE,
)
HYP_CUE_RE = re.compile(r"\bwe\s+hypothes(?:is|iz)(?:e|ed)?\s+that\b", re.I)
STUDY_TOKEN_RE = re.compile(r"\b(?:study|this study)\b", re.I)
HEADING_OBJ_RE = re.compile(r"(?m)^(?:objectives?|aims?|purpose|study\s+aims?)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\bobjective\s+(?:measurement|value)|aim\s+for|objective\s+function\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(
    r"(?:(?:the\s+objective\s+of\s+this\s+study\s+was\s+to)|(?:we\s+aim(?:ed)?\s+to\s+(?!study\b))|(?:we\s+hypothes(?:is|iz)(?:e|ed)?\s+that))",
    re.I | re.DOTALL
)

# ─────────────────────────────
# Helper
# ─────────────────────────────
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

# ─────────────────────────────
# Finder tiers
# ─────────────────────────────
def find_objective_hypothesis_v1(text: str):
    """Tier 1 – any objective/aim/hypothesis cue."""
    return _collect([OBJ_CUE_RE, HYP_CUE_RE], text)

def find_objective_hypothesis_v2(text: str, window: int = 3):
    """Tier 2 – cue + verb tense OR hypothesis phrase."""
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    verb_re = re.compile(r"\b(?:was|were|is|are|aim(?:ed)?|hypothes(?:is|iz)(?:e|ed)?)\b", re.I)
    verb_idx = {i for i, t in enumerate(tokens) if verb_re.fullmatch(t)}
    out = []
    for m in OBJ_CUE_RE.finditer(text):
        w_s, w_e = _char_to_word((m.start(), m.end()), spans)
        if any(v for v in verb_idx if w_s - window <= v <= w_e + window):
            out.append((w_s, w_e, m.group(0)))
    for m in HYP_CUE_RE.finditer(text):
        w_s, w_e = _char_to_word((m.start(), m.end()), spans)
        out.append((w_s, w_e, m.group(0)))
    return out

def find_objective_hypothesis_v3(text: str, block_chars: int = 300):
    """Tier 3 – inside Objectives/Aims heading block."""
    spans = _token_spans(text)
    blocks = []
    for h in HEADING_OBJ_RE.finditer(text):
        s = h.end(); e = min(len(text), s + block_chars)
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for patt in (OBJ_CUE_RE, HYP_CUE_RE):
        for m in patt.finditer(text):
            if inside(m.start()):
                w_s, w_e = _char_to_word((m.start(), m.end()), spans)
                out.append((w_s, w_e, m.group(0)))
    return out

def find_objective_hypothesis_v4(text: str, window: int = 4):
    """Tier 4 – v2 + explicit study token near cue."""
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    study_idx = {i for i, t in enumerate(tokens) if STUDY_TOKEN_RE.search(t)}
    matches = find_objective_hypothesis_v2(text, window=window)
    out = []
    for w_s, w_e, snip in matches:
        if any(s for s in study_idx if w_s - window <= s <= w_e + window):
            out.append((w_s, w_e, snip))
    return out

def find_objective_hypothesis_v5(text: str):
    """Tier 5 – tight template."""
    return _collect([TIGHT_TEMPLATE_RE], text)

# ─────────────────────────────
# Mapping & exports
# ─────────────────────────────
OBJECTIVE_HYPOTHESIS_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_objective_hypothesis_v1,
    "v2": find_objective_hypothesis_v2,
    "v3": find_objective_hypothesis_v3,
    "v4": find_objective_hypothesis_v4,
    "v5": find_objective_hypothesis_v5,
}

__all__ = [
    "find_objective_hypothesis_v1", "find_objective_hypothesis_v2", "find_objective_hypothesis_v3", "find_objective_hypothesis_v4", "find_objective_hypothesis_v5", "OBJECTIVE_HYPOTHESIS_FINDERS",
]

find_objective_hypothesis_high_recall = find_objective_hypothesis_v1
find_objective_hypothesis_high_precision = find_objective_hypothesis_v5
