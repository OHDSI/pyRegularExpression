"""exit_criterion_finder.py – precision/recall ladder for *exit-criterion* statements.

Five variants (v1–v5):

    • v1 – high recall: any exit/censoring cue
    • v2 – cue + temporal keyword (‘until’, ‘whichever’, ‘censored at/when’) within context window
    • v3 – only inside an *Exit criteria / Censoring* heading block
    • v4 – v2 plus explicit event/time token (death/transplant/date), excludes attrition traps
    • v5 – tight template: “followed until …”, “censored at …”, “exit when …”

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
EXIT_CRITERION_TERM_RE = re.compile(
    r"\b(?:followed\s+until|until\s+the\s+earlier\s+of|until|exit\s+when|censored\s+(?:at|on|when)|exit\s+at|follow[- ]?up\s+ended)\b",
    re.I,
)

TEMPORAL_KEYWORD_RE = re.compile(r"\b(?:until|whichever|earlier|later|censored|exit)\b", re.I)

EVENT_TOKEN_RE = re.compile(
    r"\b(?:death|transplant|end[-\s]+of[-\s]+study|\d{4}-\d{2}-\d{2}|31\s+dec\s+\d{4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})\b",
    re.I,
)

HEADING_EXIT_RE = re.compile(
    r"(?m)^(?:exit\s+criteria|censoring|follow[- ]?up\s+end|end\s+of\s+follow[- ]?up)\s*[:\-]?\s*$",
    re.I,
)

TRAP_RE = re.compile(
    r"\b(?:study\s+ended|lost\s+to\s+follow[- ]?up|withdrew|withdrawn|dropped\s+out|attrition|analysis)\b",
    re.I,
)

TIGHT_TEMPLATE_RE = re.compile(
    r"(?:followed\s+until\s+[^\.\n]{0,60}|censored\s+(?:at|when)\s+[^\.\n]{0,60}|exit\s+when\s+[^\.\n]{0,60})",
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
def find_exit_criterion_v1(text: str) -> List[Tuple[int, int, str]]:
    """Tier 1 – any exit/censoring cue."""    
    return _collect([EXIT_CRITERION_TERM_RE], text)

def find_exit_criterion_v2(text: str, window: int = 5) -> List[Tuple[int, int, str]]:
    """Tier 2 – exit cue + temporal keyword within ±window tokens."""    
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    temp_idx = {i for i, t in enumerate(tokens) if TEMPORAL_KEYWORD_RE.fullmatch(t)}
    out: List[Tuple[int, int, str]] = []
    for m in EXIT_CRITERION_TERM_RE.finditer(text):
        if TRAP_RE.search(text[max(0, m.start()-30): m.end()+30]):
            continue
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        if any(w_s - window <= t <= w_e + window for t in temp_idx):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_exit_criterion_v3(text: str, block_chars: int = 400) -> List[Tuple[int, int, str]]:
    """Tier 3 – only inside ‘Exit criteria / Censoring’ heading blocks."""    
    token_spans = _token_spans(text)
    blocks: List[Tuple[int, int]] = []
    for h in HEADING_EXIT_RE.finditer(text):
        start = h.end()
        nxt_blank = text.find("\n\n", start)
        end = nxt_blank if 0 <= nxt_blank - start <= block_chars else start + block_chars
        blocks.append((start, end))
    def _inside(pos: int): return any(s <= pos < e for s, e in blocks)
    out: List[Tuple[int, int, str]] = []
    for m in EXIT_CRITERION_TERM_RE.finditer(text):
        if _inside(m.start()):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_exit_criterion_v4(text: str, window: int = 8) -> List[Tuple[int, int, str]]:
    """Tier 4 – v2 + explicit event/time token."""    
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    event_idx = {i for i, t in enumerate(tokens) if EVENT_TOKEN_RE.search(t)}
    matches = find_exit_criterion_v2(text, window=window)
    out: List[Tuple[int, int, str]] = []
    for w_s, w_e, snip in matches:
        if any(w_s - window <= e <= w_e + window for e in event_idx):
            out.append((w_s, w_e, snip))
    return out

def find_exit_criterion_v5(text: str) -> List[Tuple[int, int, str]]:
    """Tier 5 – tight template form."""    
    return _collect([TIGHT_TEMPLATE_RE], text)

# ─────────────────────────────
# 4.  Public mapping & exports
# ─────────────────────────────
EXIT_CRITERION_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_exit_criterion_v1,
    "v2": find_exit_criterion_v2,
    "v3": find_exit_criterion_v3,
    "v4": find_exit_criterion_v4,
    "v5": find_exit_criterion_v5,
}

__all__ = [
    "find_exit_criterion_v1",
    "find_exit_criterion_v2",
    "find_exit_criterion_v3",
    "find_exit_criterion_v4",
    "find_exit_criterion_v5",
    "EXIT_CRITERION_FINDERS",
]

# handy aliases
find_exit_criterion_high_recall = find_exit_criterion_v1
find_exit_criterion_high_precision = find_exit_criterion_v5
