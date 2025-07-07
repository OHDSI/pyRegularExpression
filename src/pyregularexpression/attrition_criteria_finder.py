
"""attrition_criteria_finder.py – precision/recall ladder for *attrition criteria* (post‑enrolment loss).
Five variants (v1–v5):
    • v1 – high recall: any attrition cue (lost / withdrew / dropped out)
    • v2 – cue + study‑context token within ±window tokens (during follow‑up / during study)
    • v3 – only inside an *Attrition / Loss to follow‑up* heading block
    • v4 – v2 plus numeric evidence (count or %), excludes exit‑criterion and pre‑screen traps
    • v5 – tight template: “N participants were lost to follow‑up”, “withdrew consent during follow‑up”, etc.
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
ATTRITION_CUE_RE = re.compile(
    r"\b(?:lost\s+to\s+follow[- ]?up|lost\s+contact|withdrew\s+consent|withdrawn|dropped\s+out|discontinued\s+participation|lost)\b",
    re.I,
)

STUDY_CONTEXT_RE = re.compile(
    r"""
    \b(
        during\s+(the\s+)?(study|follow[-\s]?up|trial)|(study|trial|follow[-\s]?up)\s+period|in\s+(the\s+)?(study|trial|follow[-\s]?up)
    )\b
    """,
    flags=re.IGNORECASE | re.VERBOSE,
)

NUMERIC_EVIDENCE_RE = re.compile(
    r"""
    (?:(?:\d+|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)\s+(participants?|patients?|subjects?)|\d+\s*%(\s+of\s+(participants?|patients?|subjects?))?|n\s*=\s*\d+
    )
    """,
    re.IGNORECASE | re.VERBOSE
)

HEADING_ATTRITION_RE = re.compile(r"(?m)^(?:attrition|loss\s+to\s+follow[- ]?up|participant\s+flow)\s*[:\-]?\s*$", re.I)

TRAP_RE = re.compile(
    r"\b(?:exclusion\s+criteria|excluded\s+if|exit\s+when|censored|screen\s+failure|pre[- ]?randomi[sz]ation)\b",
    re.I,
)

TIGHT_TEMPLATE_RE = re.compile(
    r"(?:\d+\s*(?:participants?|patients?|subjects?)\s+(?:were\s+)?(?:lost\s+to\s+follow[- ]?up|withdrew\s+consent|dropped\s+out)|"
    r"withdrew\s+consent\s+during\s+(?:follow[- ]?up|the\s+study))",
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
def find_attrition_criteria_v1(text: str) -> List[Tuple[int, int, str]]:
    """Tier 1 – any attrition cue."""    
    return _collect([ATTRITION_CUE_RE], text)

def find_attrition_criteria_v2(text: str, window: int = 5) -> List[Tuple[int, int, str]]:
    """Tier 2 – attrition cue + study‑context token within ±window tokens."""
    token_spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    cue_matches = [(m.start(), m.end(), m.group(0)) for m in ATTRITION_CUE_RE.finditer(text) if not TRAP_RE.search(text[max(0, m.start()-30):m.end()+30])]
    ctx_word_indices = set()
    for m in STUDY_CONTEXT_RE.finditer(text):
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        ctx_word_indices.update(range(w_s, w_e + 1))
    for s_char, e_char, snippet in cue_matches:
        w_s, w_e = _char_span_to_word_span((s_char, e_char), token_spans)
        if any(c for c in ctx_word_indices if w_s - window <= c <= w_e + window):
            out.append((w_s, w_e, snippet))
    return out

def find_attrition_criteria_v3(text: str, block_chars: int = 400) -> List[Tuple[int, int, str]]:
    """Tier 3 – only inside Attrition / Loss heading blocks."""    
    token_spans = _token_spans(text)
    blocks: List[Tuple[int, int]] = []
    for h in HEADING_ATTRITION_RE.finditer(text):
        start = h.end()
        nxt_blank = text.find("\n\n", start)
        end = nxt_blank if 0 <= nxt_blank - start <= block_chars else start + block_chars
        blocks.append((start, end))
    def _inside(p): return any(s <= p < e for s, e in blocks)
    out: List[Tuple[int, int, str]] = []
    for m in ATTRITION_CUE_RE.finditer(text):
        if _inside(m.start()):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_attrition_criteria_v4(text: str, window: int = 6) -> List[Tuple[int, int, str]]:
    """Tier 4 – v2 + numeric evidence of dropout."""    
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    num_idx = set()
    for i in range(len(tokens)):
        for j in range(i+1, min(i+4, len(tokens))+1):
            span_text = " ".join(tokens[i:j])
            if NUMERIC_EVIDENCE_RE.fullmatch(span_text):
                num_idx.update(range(i, j))
    matches = find_attrition_criteria_v2(text, window=window)
    out: List[Tuple[int, int, str]] = []
    for w_s, w_e, snip in matches:
        if any(n for n in num_idx if w_s - window <= n <= w_e + window):
            out.append((w_s, w_e, snip))
    return out

def find_attrition_criteria_v5(text: str) -> List[Tuple[int, int, str]]:
    """Tier 5 – tight template with numeric and cue."""    
    return _collect([TIGHT_TEMPLATE_RE], text)

# ─────────────────────────────
# 4.  Public mapping & exports
# ─────────────────────────────
ATTRITION_CRITERIA_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_attrition_criteria_v1,
    "v2": find_attrition_criteria_v2,
    "v3": find_attrition_criteria_v3,
    "v4": find_attrition_criteria_v4,
    "v5": find_attrition_criteria_v5,
}

__all__ = [
    "find_attrition_criteria_v1",
    "find_attrition_criteria_v2",
    "find_attrition_criteria_v3",
    "find_attrition_criteria_v4",
    "find_attrition_criteria_v5",
    "ATTRITION_CRITERIA_FINDERS",
]

# handy aliases
find_attrition_criteria_high_recall = find_attrition_criteria_v1
find_attrition_criteria_high_precision = find_attrition_criteria_v5
