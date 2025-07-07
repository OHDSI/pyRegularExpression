
"""exposure_definition_finder.py – precision/recall ladder for *exposure definition* statements.

Five variants (v1–v5):

    • v1 – high recall: any exposure cue
    • v2 – cue + defining verb (defined/considered/operationalized) within ±window tokens
    • v3 – only inside an *Exposure definition / Exposure assessment* heading block
    • v4 – v2 plus explicit criterion token (≥, at least, prescriptions, days, etc.), excludes generic mentions
    • v5 – tight template: “Exposure was defined as ≥2 prescriptions…”, “Exposure = drug X for 30 days”, etc.

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
EXPOSURE_DEF_CUE_RE = re.compile(r"\b(?:exposure|exposed)\b", re.I)

DEFINE_VERB_RE = re.compile(r"\b(?:defined|considered|operationalis(?:ed|ed)|assigned|classified|characteris(?:ed|ed))\b", re.I)

CRITERION_TOKEN_RE = re.compile(r"\b(?:>=|<=|>|<|at\s+least|more\s+than|\d+\s*(?:prescriptions?|doses?|fills?|days?|weeks?|months)|within\s+\d+)\b", re.I)

HEADING_EXPOSURE_RE = re.compile(r"(?m)^(?:exposure\s+(?:definition|assessment|classification))\s*[:\-]?\s*$", re.I)

TRAP_RE = re.compile(r"\b(?:radiation\s+exposure|occupational\s+exposure|environmental\s+exposure|randomi(?:s|z)ed)\b", re.I)

TIGHT_TEMPLATE_RE = re.compile(
    r"(?:exposure\s+was\s+defined\s+as|exposure\s*=)\s+[^\.\n]{0,80}",
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
def find_exposure_definition_v1(text: str) -> List[Tuple[int, int, str]]:
    """Tier 1 – any exposure cue."""    
    return _collect([EXPOSURE_DEF_CUE_RE], text)

def find_exposure_definition_v2(text: str, window: int = 5) -> List[Tuple[int, int, str]]:
    """Tier 2 – cue + defining verb within ±window tokens."""    
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    verb_idx = {i for i, t in enumerate(tokens) if DEFINE_VERB_RE.fullmatch(t)}
    out: List[Tuple[int, int, str]] = []
    for m in EXPOSURE_DEF_CUE_RE.finditer(text):
        if TRAP_RE.search(text[max(0, m.start()-30):m.end()+30]):
            continue
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        if any(v for v in verb_idx if w_s - window <= v <= w_e + window):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_exposure_definition_v3(text: str, block_chars: int = 400) -> List[Tuple[int, int, str]]:
    """Tier 3 – inside Exposure definition heading blocks."""    
    token_spans = _token_spans(text)
    blocks: List[Tuple[int, int]] = []
    for h in HEADING_EXPOSURE_RE.finditer(text):
        start = h.end()
        nxt_blank = text.find("\n\n", start)
        end = nxt_blank if 0 <= nxt_blank - start <= block_chars else start + block_chars
        blocks.append((start, end))
    def _inside(p): return any(s <= p < e for s, e in blocks)
    out: List[Tuple[int, int, str]] = []
    for m in EXPOSURE_DEF_CUE_RE.finditer(text):
        if _inside(m.start()):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_exposure_definition_v4(text: str, window: int = 6) -> List[Tuple[int, int, str]]:
    """Tier 4 – v2 + explicit criterion token."""    
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    crit_idx = {i for i, t in enumerate(tokens) if CRITERION_TOKEN_RE.fullmatch(t)}
    matches = find_exposure_definition_v2(text, window=window)
    out: List[Tuple[int, int, str]] = []
    for w_s, w_e, snip in matches:
        if any(c for c in crit_idx if w_s - window <= c <= w_e + window):
            out.append((w_s, w_e, snip))
    return out

def find_exposure_definition_v5(text: str) -> List[Tuple[int, int, str]]:
    """Tier 5 – tight template form."""    
    return _collect([TIGHT_TEMPLATE_RE], text)

# ─────────────────────────────
# 4.  Public mapping & exports
# ─────────────────────────────
EXPOSURE_DEFINITION_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_exposure_definition_v1,
    "v2": find_exposure_definition_v2,
    "v3": find_exposure_definition_v3,
    "v4": find_exposure_definition_v4,
    "v5": find_exposure_definition_v5,
}

__all__ = [
    "find_exposure_definition_v1",
    "find_exposure_definition_v2",
    "find_exposure_definition_v3",
    "find_exposure_definition_v4",
    "find_exposure_definition_v5",
    "EXPOSURE_DEFINITION_FINDERS",
]

# aliases
find_exposure_definition_high_recall = find_exposure_definition_v1
find_exposure_definition_high_precision = find_exposure_definition_v5
