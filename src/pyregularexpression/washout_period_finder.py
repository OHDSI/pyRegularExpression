"""
washout_period_finder.py – precision/recall ladder for *washout period* definitions.
Five variants (v1‑v5):
    • v1 – high recall: any washout/run‑in/drug‑free cue
    • v2 – cue + explicit duration (months / weeks / years) or “drug‑free / treatment‑free” within ±window tokens
    • v3 – only inside a *Washout period / Clearance period / Run‑in* heading block
    • v4 – v2 plus temporal anchor before index/baseline (before / prior to / preceding), excludes side‑effect stoppage traps
    • v5 – tight template: “12‑month washout with no antihypertensives”, “patients were drug‑free for 6 months before index”, etc.
Each function returns a list of tuples: (start_token_idx, end_token_idx, matched_snippet)
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

# ─────────────────────────────
# 0.  Shared utilities
# ─────────────────────────────
# allow normal *or* non‑breaking hyphens
HYPHEN = r"[-\u2011]"

SEP = rf"(?:{HYPHEN}|\s+)"

NUMBER_WORD = r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"

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
WASHOUT_CUE_RE = re.compile(
    rf"""\b(
        washout(?:{SEP}period)?        |   # "washout", "washout period", "washout‑period"
        run{SEP}in                      |   # "run in", "run‑in"
        clearance(?:{SEP}period)?      |   # "clearance", "clearance period", "clearance‑period"
        treatment{SEP}free              |   # "treatment free", "treatment‑free"
        drug{SEP}free                   |   # "drug free", "drug‑free"
        no\ therapy                     |   # "no therapy"
        no\ medications                 |   # "no medications"
        no\ drugs                       |
        no\ antihypertensives          # catch "No antihypertensives were used."
    )\b""",
    re.IGNORECASE | re.VERBOSE
)

DURATION_RE = re.compile(
    rf"\b(?:(\d+{HYPHEN}?|{NUMBER_WORD})\s*(?:day|week|month|year)s?)\b",
    re.I
)

BEFORE_ANCHOR_RE = re.compile(r"\b(?:before|prior\s+to|preceding|pre[- ]?index|pre[- ]?baseline)\b", re.I)

HEADING_WASHOUT_RE = re.compile(
    rf"(?im)^ *(?:" 
       rf"washout(?:{SEP}period)|"
       rf"run{SEP}in|"
       rf"clearance(?:{SEP}period)"
    r")\s*[:\-]"
)

TRAP_RE = re.compile(r"\b(?:stopped|discontinued|due\s+to\s+side[- ]?effects|adverse\s+events?)\b", re.I)

TIGHT_TEMPLATE_RE = re.compile(
    r"(?:\d+\s*(?:month|week|year)s?\s+washout\s+(?:period\s+)?with\s+no\s+[A-Za-z\s]{1,40}|drug[- ]?free\s+for\s+\d+\s*(?:month|week|year)s?\s+before\s+index)",
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

def _char_to_token_index_map(text: str, token_spans: List[Tuple[int,int]]) -> Dict[int,int]:
    """Map each character position to its token index."""
    char2tok = {}
    for tok_i, (s,e) in enumerate(token_spans):
        for pos in range(s, e):
            char2tok[pos] = tok_i
    return char2tok

# ─────────────────────────────
# 3.  Finder variants
# ─────────────────────────────
def find_washout_period_v1(text: str) -> List[Tuple[int, int, str]]:
    """Tier 1 – any washout/run‑in cue."""    
    return _collect([WASHOUT_CUE_RE], text)

def find_washout_period_v2(text: str, window: int = 8) -> List[Tuple[int, int, str]]:
    """Tier 2 – cue + duration within ±window characters."""
    out = []
    token_spans = _token_spans(text)
    char2tok = _char_to_token_index_map(text, token_spans)

    for cue_match in WASHOUT_CUE_RE.finditer(text):
        cue_tok = char2tok.get(cue_match.start())
        if cue_tok is None:
            continue
        for dur_match in DURATION_RE.finditer(text):
            dur_tok = char2tok.get(dur_match.start())
            if dur_tok is None or abs(cue_tok - dur_tok) > window:
                continue
            # now check trap
            if TRAP_RE.search(text[cue_match.start(): dur_match.end()]):
                continue
            # good: build span
            span = (
                min(cue_match.start(), dur_match.start()),
                max(cue_match.end(),   dur_match.end())
            )
            w_s, w_e = _char_span_to_word_span(span, token_spans)
            out.append((w_s, w_e, text[span[0]:span[1]]))
            break
    return out

def find_washout_period_v3(text: str, block_chars: int = 400) -> List[Tuple[int, int, str]]:
    """Tier 3 – inside Washout / Run‑in heading blocks."""    
    token_spans = _token_spans(text)
    blocks: List[Tuple[int, int]] = []
    for h in HEADING_WASHOUT_RE.finditer(text):
        start = h.end()
        nxt_blank = text.find("\n\n", start)
        end = nxt_blank if 0 <= nxt_blank - start <= block_chars else start + block_chars
        blocks.append((start, end))
    def _inside(p): return any(s <= p < e for s, e in blocks)
    out: List[Tuple[int, int, str]] = []
    for m in WASHOUT_CUE_RE.finditer(text):
        if _inside(m.start()):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_washout_period_v4(text: str, window: int = 8) -> List[Tuple[int, int, str]]:
    """Tier 4 – cue + duration + anchor (e.g., before/prior to)."""
    token_spans = _token_spans(text)
    out = []
    char2tok = _char_to_token_index_map(text, token_spans)

    for cue_match in WASHOUT_CUE_RE.finditer(text):
        cue_tok = char2tok.get(cue_match.start())
        if cue_tok is None:
            continue
        for dur_match in DURATION_RE.finditer(text):
            dur_tok = char2tok.get(dur_match.start())
            if dur_tok is None or abs(cue_tok - dur_tok) > window:
                continue
            # check anchor + trap in the 40‑char snippet
            snippet = text[
                min(cue_match.start(), dur_match.start()):
                max(cue_match.end(), dur_match.end()) + 40
            ]
            if BEFORE_ANCHOR_RE.search(snippet) and not TRAP_RE.search(snippet):
                span = (
                    min(cue_match.start(), dur_match.start()),
                    max(cue_match.end(),   dur_match.end())
                )
                w_s, w_e = _char_span_to_word_span(span, token_spans)
                out.append((w_s, w_e, text[span[0]:span[1]]))
                break
    return out

def find_washout_period_v5(text: str) -> List[Tuple[int, int, str]]:
    """Tier 5 – tight template with duration and drug‑free cue."""    
    return _collect([TIGHT_TEMPLATE_RE], text)

# ─────────────────────────────
# 4.  Public mapping & exports
# ─────────────────────────────
WASHOUT_PERIOD_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_washout_period_v1,
    "v2": find_washout_period_v2,
    "v3": find_washout_period_v3,
    "v4": find_washout_period_v4,
    "v5": find_washout_period_v5,
}

__all__ = [
    "find_washout_period_v1",
    "find_washout_period_v2",
    "find_washout_period_v3",
    "find_washout_period_v4",
    "find_washout_period_v5",
    "WASHOUT_PERIOD_FINDERS",
]

# handy aliases
find_washout_period_high_recall = find_washout_period_v1
find_washout_period_high_precision = find_washout_period_v5
