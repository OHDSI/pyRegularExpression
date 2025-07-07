
"""sensitivity_analysis_finder.py – precision/recall ladder for *sensitivity analysis* statements.
Five variants (v1–v5):
    • v1 – high recall: any occurrence of “sensitivity analysis/analyses”.
    • v2 – sensitivity phrase + analysis verb (performed/conducted/repeated) within ±window tokens.
    • v3 – only inside a *Sensitivity analysis* heading block.
    • v4 – v2 plus scenario/assumption tokens (excluding, removing, alternative, varying) to exclude generic mentions.
    • v5 – tight template: “Excluding switchers in sensitivity analysis…”, “Sensitivity analyses repeated with alternative cut‑offs…”, etc.
Each finder returns a list of tuples: (start_token_idx, end_token_idx, matched_snippet)
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
SENS_PHRASE_RE = re.compile(r"\bsensitivity\s+analyse?s\b", re.I)

ANALYSIS_VERB_RE = re.compile(r"\b(?:performed|conducted|repeated|ran|undertook|carried\s+out)\b", re.I)

SCENARIO_TOKEN_RE = re.compile(r"\b(?:excluding|removing|restricting|alternative|varying|assumption|switchers|per[- ]?protocol|as[- ]?treated)\b", re.I)

HEADING_SENS_RE = re.compile(r"(?m)^(?:sensitivity\s+analysis(?:es)?)\s*[:\-]?\s*$", re.I)

TRAP_RE = re.compile(r"\bassay\s+sensitivity\b|\bsensitivity\s+\d{1,3}\s*%", re.I)

TIGHT_TEMPLATE_RE = re.compile(
    r"(?:sensitivity\s+analyse?s\s+(?:were\s+)?(?:performed|conducted|repeated)|excluding\s+[^\.\n]{0,60}\s+in\s+sensitivity\s+analyse?s)",
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
            if TRAP_RE.search(text[max(0, m.start()-20): m.end()+20]):
                continue
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

# ─────────────────────────────
# 3.  Finder tiers
# ─────────────────────────────
def find_sensitivity_analysis_v1(text: str) -> List[Tuple[int, int, str]]:
    """Tier 1 – any sensitivity analysis phrase."""
    return _collect([SENS_PHRASE_RE], text)

def find_sensitivity_analysis_v2(text: str, window: int = 4) -> List[Tuple[int, int, str]]:
    """Tier 2 – sensitivity phrase + analysis verb within ±window tokens."""
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    verb_idx = {i for i, t in enumerate(tokens) if ANALYSIS_VERB_RE.fullmatch(t)}
    out: List[Tuple[int, int, str]] = []
    for m in SENS_PHRASE_RE.finditer(text):
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        if any(v for v in verb_idx if w_s - window <= v <= w_e + window):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_sensitivity_analysis_v3(text: str, block_chars: int = 300) -> List[Tuple[int, int, str]]:
    """Tier 3 – within Sensitivity analysis heading blocks."""
    token_spans = _token_spans(text)
    blocks: List[Tuple[int, int]] = []
    for h in HEADING_SENS_RE.finditer(text):
        s = h.end()
        nxt = text.find("\n\n", s)
        e = nxt if 0 <= nxt - s <= block_chars else s + block_chars
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out: List[Tuple[int, int, str]] = []
    for m in SENS_PHRASE_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_sensitivity_analysis_v4(text: str, window: int = 6) -> List[Tuple[int, int, str]]:
    """Tier 4 – v2 + scenario/assumption token near phrase."""
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    scen_idx = {i for i, t in enumerate(tokens) if SCENARIO_TOKEN_RE.fullmatch(t)}
    matches = find_sensitivity_analysis_v2(text, window=window)
    out: List[Tuple[int, int, str]] = []
    for w_s, w_e, snip in matches:
        if any(scn for scn in scen_idx if w_s - window <= scn <= w_e + window):
            out.append((w_s, w_e, snip))
    return out

def find_sensitivity_analysis_v5(text: str) -> List[Tuple[int, int, str]]:
    """Tier 5 – tight template."""
    return _collect([TIGHT_TEMPLATE_RE], text)

# ─────────────────────────────
# 4.  Mapping & exports
# ─────────────────────────────
SENSITIVITY_ANALYSIS_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_sensitivity_analysis_v1,
    "v2": find_sensitivity_analysis_v2,
    "v3": find_sensitivity_analysis_v3,
    "v4": find_sensitivity_analysis_v4,
    "v5": find_sensitivity_analysis_v5,
}

__all__ = [
    "find_sensitivity_analysis_v1",
    "find_sensitivity_analysis_v2",
    "find_sensitivity_analysis_v3",
    "find_sensitivity_analysis_v4",
    "find_sensitivity_analysis_v5",
    "SENSITIVITY_ANALYSIS_FINDERS",
]

find_sensitivity_analysis_high_recall = find_sensitivity_analysis_v1
find_sensitivity_analysis_high_precision = find_sensitivity_analysis_v5
