
"""inclusion_rule_finder.py – precision/recall ladder for *inclusion‑rule* statements.
Five variants (v1–v5):
    • v1 – high recall: any inclusion/eligibility cue
    • v2 – cue + gating words like ‘if’, ‘only’, or ':' within context window
    • v3 – only inside an *Inclusion criteria / Eligibility* heading block
    • v4 – v2 plus explicit conditional verbs (must have / required to have), excludes traps
    • v5 – tight template: “Inclusion criteria: …” or “Patients were eligible if …”
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
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_span_to_word_span(span: Tuple[int, int], token_spans: Sequence[Tuple[int, int]]) -> Tuple[int, int]:
    s_char, e_char = span
    w_start = next(i for i, (s, e) in enumerate(token_spans) if s <= s_char < e)
    w_end = next(i for i, (s, e) in reversed(list(enumerate(token_spans))) if s < e_char <= e)
    return w_start, w_end

# ─────────────────────────────
# 1.  Regex assets
# ─────────────────────────────
INCL_TERM_RE = re.compile(
    r"\b(?:inclusion\s+criteria|included|eligible|must\s+have|required\s+to\s+have|included\s+only|included\s+if)\b",
    re.I,
)

GATING_TOKEN_RE = re.compile(r"\b(?:if|only|criteria:|:|must\s+have)", re.I)

HEADING_INCL_RE = re.compile(r"(?m)^(?:inclusion\s+criteria|eligibility\s+criteria|inclusion)\s*[:\-]?[ \t]*$", re.I)

TRAP_RE = re.compile(r"\b(?:study\s+included|analysis\s+included|included\s+patients|patients\s+included)\b", re.I)

TIGHT_TEMPLATE_RE = re.compile(
    r"(?:inclusion\s+criteria:\s+[^\.\n]{0,120}|patients?\s+were\s+eligible\s+if\s+[^\.\n]{0,120})",
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
def find_inclusion_rule_v1(text: str):
    """Tier 1 – any inclusion/eligibility cue."""
    token_spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []

def find_inclusion_rule_v2(text: str, window: int = 5):
    """Tier 2 – inclusion cue + gating token (‘if’, ‘only’, ':') nearby."""    
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    gate_idx = {i for i, t in enumerate(tokens) if GATING_TOKEN_RE.fullmatch(t)}
    out: List[Tuple[int, int, str]] = []
    for m in INCL_TERM_RE.finditer(text):
        if TRAP_RE.search(text[max(0, m.start()-20):m.end()+20]):
            continue
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        if any(g for g in gate_idx if w_s - window <= g <= w_e + window):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_inclusion_rule_v3(text: str, block_chars: int = 400):
    """Tier 3 – only inside ‘Inclusion criteria’ heading blocks."""    
    token_spans = _token_spans(text)
    blocks: List[Tuple[int, int]] = []
    for h in HEADING_INCL_RE.finditer(text):
        start = h.end()
        nxt_blank = text.find("\n\n", start)
        end = nxt_blank if 0 <= nxt_blank - start <= block_chars else start + block_chars
        blocks.append((start, end))
    def _inside(pos): return any(s <= pos < e for s, e in blocks)
    out: List[Tuple[int, int, str]] = []
    for m in INCL_TERM_RE.finditer(text):
        if _inside(m.start()):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_inclusion_rule_v4(text: str, window: int = 6):
    """Tier 4 – v2 + explicit conditional verbs, excludes traps."""    
    CONDITIONAL_VERB_RE = re.compile(r"\b(?:must\s+have|required\s+to\s+have|had\s+to\s+have|must\s+possess)\b", re.I)
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    cond_idx = {i for i, t in enumerate(tokens) if CONDITIONAL_VERB_RE.fullmatch(t)}
    matches = find_inclusion_rule_v2(text, window=window)
    out: List[Tuple[int, int, str]] = []
    for w_s, w_e, snip in matches:
        if any(c for c in cond_idx if w_s - window <= c <= w_e + window):
            out.append((w_s, w_e, snip))
    return out

def find_inclusion_rule_v5(text: str):
    """Tier 5 – tight template (colon list or ‘eligible if’ sentence)."""    
    return _collect([TIGHT_TEMPLATE_RE], text)

# ─────────────────────────────
# 4.  Public mapping & exports
# ─────────────────────────────
INCLUSION_RULE_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_inclusion_rule_v1,
    "v2": find_inclusion_rule_v2,
    "v3": find_inclusion_rule_v3,
    "v4": find_inclusion_rule_v4,
    "v5": find_inclusion_rule_v5,
}

__all__ = [
    "find_inclusion_rule_v1", "find_inclusion_rule_v2", "find_inclusion_rule_v3", "find_inclusion_rule_v4", "find_inclusion_rule_v5", "INCLUSION_RULE_FINDERS",
]

# aliases
find_inclusion_v1 = find_inclusion_rule_v1
find_inclusion_v5 = find_inclusion_rule_v5
