"""trial_design_finder.py – precision/recall ladder for *clinical/epidemiological trial or study design* statements.
Five variants (v1–v5):
    • v1 – high recall: any solitary design keyword (randomized trial, cohort study, cross‑sectional, case‑control, phase II, etc.) together with “trial/study”.
    • v2 – design keyword plus ≥1 qualifier (randomized, double‑blind, placebo‑controlled, prospective, retrospective, multicenter) within ±4 tokens, or two distinct design keywords close together.
    • v3 – only inside a *Study/Trial Design* heading block (first ~400 characters).
    • v4 – v2 plus explicit design type term (trial, cohort, case‑control, cross‑sectional) to filter contextual uses.
    • v5 – tight template: “double‑blind, placebo‑controlled randomized trial…”, “prospective multicenter cohort study…”, etc.
Each finder returns ``(start_word_idx, end_word_idx, snippet)`` tuples.
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

# ─────────────────────────────
# 0. Token utilities
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
# 1. Regex assets
# ─────────────────────────────
DESIGN_TERM_RE = re.compile(
    r"\b(?:randomi(?:s|z)ed\s+controlled\s+trial|randomi(?:s|z)ed\s+trial|double\s*[- ]?blind\s+trial|placebo[- ]?controlled\s+trial|open[- ]?label(?:\s+phase\s+[iIvVxX]+)?|phase\s+[iIvVxX]+\s+trial|prospective\s+cohort\s+study|retrospective\s+cohort\s+study|cohort\s+study|case[- ]?control\s+study|cross[- ]?sectional\s+(?:study|design)|multicenter\s+trial|parallel[- ]?group\s+design|pragmatic\s+trial|quasi[- ]?experimental\s+study)\b",
    re.I,
)

QUALIFIER_RE = re.compile(r"\b(?:randomi(?:s|z)ed|double[- ]?blind|placebo[- ]?controlled|open[- ]?label|prospective|retrospective|multicenter|parallel[- ]?group|phase\s+[iIvVxX]+|pragmatic)\b", re.I)

TYPE_TOKEN_RE = re.compile(r"\b(?:trial|study|design)\b", re.I)

HEADING_DESIGN_RE = re.compile(r"(?m)^(?:study|trial)\s+design\s*[:\-]?\s*$", re.I)

TRAP_RE = re.compile(r"\b(?:trial\s+was\s+designed|study\s+was\s+designed|design\s+to\s+minimi[sz]e)\b", re.I)

TIGHT_TEMPLATE_RE = re.compile(
    r"(?:double[- ]?blind|placebo[- ]?controlled|multicenter|randomi(?:s|z)ed).*?(?:trial)"  # multiple qualifiers then 'trial'
    r"|prospective\s+multicenter\s+cohort\s+study"
    r"|phase\s+[iIvVxX]+\s+(?:open[- ]?label\s+)?trial",
    re.I,
)

# ─────────────────────────────
# 2. Helper
# ─────────────────────────────
def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0, m.start()-25):m.end()+25]):
                continue
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

# ─────────────────────────────
# 3. Finder tiers
# ─────────────────────────────
def find_trial_design_v1(text: str):
    """Tier 1 – any design term with trial/study."""
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    type_idx = {i for i, t in enumerate(tokens) if TYPE_TOKEN_RE.fullmatch(t)}
    out = []
    for m in DESIGN_TERM_RE.finditer(text):
        w_s, w_e = _char_to_word((m.start(), m.end()), spans)
        if any(t for t in type_idx if w_s - 4 <= t <= w_e + 4):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_trial_design_v2(text: str, window: int = 4):
    """Tier 2 – design term + qualifier within ±window OR two design terms close."""
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    qual_idx = {i for i, t in enumerate(tokens) if QUALIFIER_RE.fullmatch(t)}
    design_idx = {i for i, t in enumerate(tokens) if DESIGN_TERM_RE.fullmatch(t)}
    out = []
    for i in design_idx:
        if any(q for q in qual_idx if abs(q - i) <= window):
            w_s, w_e = _char_to_word(spans[i], spans)
            out.append((w_s, w_e, tokens[i]))
            continue
        if any(j for j in design_idx if j != i and abs(j - i) <= window):
            w_s, w_e = _char_to_word(spans[i], spans)
            out.append((w_s, w_e, tokens[i]))
    return out

def find_trial_design_v3(text: str, block_chars: int = 400):
    """Tier 3 – within Study/Trial design heading block."""
    spans = _token_spans(text)
    blocks = []
    for h in HEADING_DESIGN_RE.finditer(text):
        s = h.end(); e = min(len(text), s + block_chars)
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in DESIGN_TERM_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_trial_design_v4(text: str, window: int = 4):
    """Tier 4 – v2 + explicit design type token nearby."""
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    type_idx = {i for i, t in enumerate(tokens) if TYPE_TOKEN_RE.fullmatch(t)}
    matches = find_trial_design_v2(text, window=window)
    out = []
    for w_s, w_e, snip in matches:
        if any(t for t in type_idx if w_s - window <= t <= w_e + window):
            out.append((w_s, w_e, snip))
    return out

def find_trial_design_v5(text: str):
    """Tier 5 – tight template match."""
    return _collect([TIGHT_TEMPLATE_RE], text)

# ─────────────────────────────
# 4. Mapping & exports
# ─────────────────────────────
TRIAL_DESIGN_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_trial_design_v1,
    "v2": find_trial_design_v2,
    "v3": find_trial_design_v3,
    "v4": find_trial_design_v4,
    "v5": find_trial_design_v5,
}

__all__ = [
    "find_trial_design_v1", "find_trial_design_v2", "find_trial_design_v3",
    "find_trial_design_v4", "find_trial_design_v5", "TRIAL_DESIGN_FINDERS",
]

find_trial_design_high_recall = find_trial_design_v1
find_trial_design_high_precision = find_trial_design_v5
