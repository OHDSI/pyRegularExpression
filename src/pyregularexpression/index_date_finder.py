"""index_date_finder.py – precision/recall ladder for *index‑date definition* statements.
Five variants (v1–v5):
    • v1 – high recall: any ‘index/baseline date’ cue
    • v2 – cue + defining verb within context window
    • v3 – only inside ‘Index date/Baseline date’ definition blocks
    • v4 – v2 plus explicit ‘defined/set/assigned/=”’ syntax, excludes traps
    • v5 – tight template: “Index date = …” or “Index date was defined as …”
Functions return a list of tuples: (start_token_idx, end_token_idx, matched_snippet)
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
INDEX_TERM_RE = re.compile(r"\b(?:index\s+date|baseline\s+date)\b", re.I)

DEFINE_VERB_RE = re.compile(r"\b(?:defined|set|assigned|taken|established|determined|calculated)\b", re.I)

EQUAL_SYNTAX_RE = re.compile(r"=", re.I)

HEADING_INDEX_RE = re.compile(r"(?m)^(?:index\s+date|baseline\s+date|time\s+zero)\s*[:\-]?\s*$", re.I)

TRAP_RE = re.compile(r"\b(?:index\s+(?:case|test|patient|event)|follow(?:ed|ing)?\s+from|data\s+entry)\b", re.I)

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
def find_index_date_v1(text: str):
    """Tier 1 – any index/baseline date mention."""
    return _collect([INDEX_TERM_RE], text)

def find_index_date_v2(text: str, window: int = 5):
    """Tier 2 – INDEX_TERM within ±window tokens of defining verb."""
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    verb_idx = {i for i, t in enumerate(tokens) if DEFINE_VERB_RE.fullmatch(t)}
    out: List[Tuple[int, int, str]] = []
    for m in INDEX_TERM_RE.finditer(text):
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        if any(v for v in verb_idx if w_s - window <= v <= w_e + window):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_index_date_v3(text: str, block_chars: int = 300):
    """Tier 3 – only inside dedicated Index/Baseline headings."""
    token_spans = _token_spans(text)
    blocks: List[Tuple[int, int]] = []
    for h in HEADING_INDEX_RE.finditer(text):
        start = h.end()
        nxt_blank = text.find("\n\n", start)
        end = nxt_blank if 0 <= nxt_blank - start <= block_chars else start + block_chars
        blocks.append((start, end))
    def _inside(pos: int):
        return any(s <= pos < e for s, e in blocks)
    out: List[Tuple[int, int, str]] = []
    for m in INDEX_TERM_RE.finditer(text):
        if _inside(m.start()):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_index_date_v4(text: str, window: int = 5):
    """Tier 4 – v2 + explicit '=' or defining verb in same clause, excludes traps."""
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    matches = find_index_date_v2(text, window=window)
    out: List[Tuple[int, int, str]] = []
    for w_s, w_e, snippet in matches:
        clause_text = " ".join(tokens[max(0, w_s - 3): w_e + 6])
        if EQUAL_SYNTAX_RE.search(clause_text) or DEFINE_VERB_RE.search(clause_text):
            if not TRAP_RE.search(clause_text):
                out.append((w_s, w_e, snippet))
    return out

def find_index_date_v5(text: str):
    """Tier 5 – tight template with '=' or 'was defined as'."""
    TEMPLATE_RE = re.compile(
        r"(?:index\s+date|baseline\s+date)\s*(?:=|was\s+defined\s+as|was\s+set\s+as|was\s+assigned\s+as)\s+[^\.\;\n]{0,50}",
        re.I,
    )
    return _collect([TEMPLATE_RE], text)

# ─────────────────────────────
# 4.  Public mapping & exports
# ─────────────────────────────
INDEX_DATE_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_index_date_v1,
    "v2": find_index_date_v2,
    "v3": find_index_date_v3,
    "v4": find_index_date_v4,
    "v5": find_index_date_v5,
}

__all__ = [
    "find_index_date_v1",
    "find_index_date_v2",
    "find_index_date_v3",
    "find_index_date_v4",
    "find_index_date_v5",
    "INDEX_DATE_FINDERS",
]

# aliases
find_index_date_v1 = find_index_date_v1
find_index_date_v5 = find_index_date_v5
