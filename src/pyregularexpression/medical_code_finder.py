from __future__ import annotations
import re
from typing import List, Tuple, Sequence

# ─────────────────────────────
# 0.  Shared utilities
# ─────────────────────────────
TOKEN_RE = re.compile(r"\S+")


def _token_spans(text: str) -> List[Tuple[int, int]]:
    """Return character start / end offsets for every non‑whitespace token."""    
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]


def _char_span_to_word_span(char_span: Tuple[int, int], token_spans: Sequence[Tuple[int, int]]) -> Tuple[int, int]:
    """Convert a character slice to the **inclusive** word‑index span that covers it."""    
    s_char, e_char = char_span
    w_start = next(i for i, (s, e) in enumerate(token_spans) if s <= s_char < e)
    w_end = next(i for i, (s, e) in reversed(list(enumerate(token_spans))) if s < e_char <= e)
    return w_start, w_end

# ─────────────────────────────
# 1.  Canonical high‑recall regex (Tier 1)
# ─────────────────────────────
MEDICAL_CODE_RE = re.compile(
    r"""\b(?:
        [A-TV-Z][0-9]{2}[A-Z0-9]?(?:\.[A-Z0-9]{1,4})? |        # ICD‑10‑CM
        [VE]?\d{3}(?:\.\d{1,2})? |                           # ICD‑9‑CM
        [0-9A-Z][A-Z]\d[0-9A-Z](?:\.[A-Z0-9]{2})? |           # ICD‑11 stem
        (?:\d{4,5}-\d{3,4}-\d{1,2}|\d{10,12}) |             # NDC
        \d{1,6}-\d |                                          # LOINC hyphen form
        [A-Z]\d{2}[A-Z][A-Z0-9]{1,4} |                        # ATC
        RXCUI:?\s*\d{7,9} |                                   # RxNorm
        [1-9]\d{5,17} |                                       # SNOMED CT
        OMOP\d{3,15} |                                        # OMOP concept id
        [A-Z0-9]{1,5}\.[A-Z0-9]{1,2} |                        # Read / CTV3
        D?\d{4,5} |                                           # CPT / CDT
        [A-Z]\d{4}(?:-[A-Z0-9]{2})?                           # HCPCS‑II
    )\b""",
    re.VERBOSE | re.IGNORECASE,
)

# ─────────────────────────────
# 2.  Precision helpers & false‑positive fences
# ─────────────────────────────
CODE_TERM = (
    r"(?:icd(?:[- ]?(?:9|10|11))?|icd[- ]?cm|icd[- ]?o|"
    r"international\ classification\ of\ diseases(?:[- ]?(?:9|10|11))?)|"
    r"cpt|current\ procedural\ terminology(?:[- ]?4)?|hcpcs|healthcare\ common\ procedure\ coding\ system|"
    r"snomed(?:[ -]?ct)?|rxnorm|loinc|read\ codes?|icpc|atc(?:\s+codes?)?"
)

CODE_KEYWORD_RE = re.compile(CODE_TERM, re.I)

# short‑numeric guard (≤3 digits not near a keyword)
_CODE_CONTEXT_RE = re.compile(rf"(?i)(?:{CODE_TERM})\W{{0,20}}\d{{1,3}}\b")

# research‑driven helpers
GENERIC_CODE_TRAP_RE = re.compile(r"\b(?:programming|source|survey|genetic|study[- ]?id)\s+codes?\b", re.I)
NEEDS_ACRONYM_RE = re.compile(r"\b(?:icd[- ]?\d{1,2}|cpt|snomed(?:\s+ct)?|rxnorm|loinc|diagnosis|procedure|billing|medical|clinical)\b", re.I)

NEGATIVE_PRE_TOKEN_RE = re.compile(r"^(?:#|mg|kg|mmhg|bpm)$", re.I)
HEADING_RE = re.compile(r"(?m)^(?:diagnosis|procedure|billing|icd-?\d{1,2}?|codes?)\s+codes?:\s*$", re.I)
STRICT_TOKEN_RE = re.compile(r"^[A-Z0-9]{3,7}(?:\.[A-Z0-9]{1,4})?$", re.A)

# ─────────────────────────────
# 3.  Core guard functions
# ─────────────────────────────
def _is_short_numeric_false_positive(match: re.Match[str], text: str, min_len: int = 4) -> bool:
    token = match.group(0)
    if not token.isdigit() or len(token) >= min_len:
        return False
    span_start = max(0, match.start() - 30)
    return not _CODE_CONTEXT_RE.search(text[span_start : match.start()])

# ─────────────────────────────
# 4.  Finder variants (ladder Tiers 1‑5)
# ─────────────────────────────
def find_medical_code_v1(text: str):  # high recall
    token_spans = _token_spans(text)
    out = []
    for m in MEDICAL_CODE_RE.finditer(text):
        if _is_short_numeric_false_positive(m, text):
            continue
        out.append((*_char_span_to_word_span((m.start(), m.end()), token_spans), m.group(0).upper()))
    return out

def find_medical_code_v2(text: str, window: int = 5):  # anchor ±window tokens
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    keywords_pos = {i for i, tok in enumerate(tokens) if CODE_KEYWORD_RE.fullmatch(tok)}
    out = []
    for m in MEDICAL_CODE_RE.finditer(text):
        if _is_short_numeric_false_positive(m, text):
            continue
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        w0 = max(0, w_s - window)
        w1 = w_e + window + 1
        window_tokens = tokens[w0:w1]
        window_lower = [t.lower() for t in window_tokens]
        if any(t in ("code", "codes") for t in window_lower):
            if not any(NEEDS_ACRONYM_RE.search(t) for t in window_tokens):
                continue
        if any(k for k in keywords_pos if w0 <= k <= w1 - 1):
            out.append((w_s, w_e, m.group(0).upper()))
    return out

def find_medical_code_v3(text: str, block_chars: int = 300):  # heading‑anchored
    token_spans = _token_spans(text)
    blocks = []
    for h in HEADING_RE.finditer(text):
        start = h.end()
        nxt_blank = text.find("\n\n", start)
        end = nxt_blank if 0 <= nxt_blank - start <= block_chars else start + block_chars
        blocks.append((start, end))
    def _inside(pos): return any(s <= pos < e for s, e in blocks)
    out = []
    for m in MEDICAL_CODE_RE.finditer(text):
        if _inside(m.start()):
            out.append((*_char_span_to_word_span((m.start(), m.end()), token_spans), m.group(0).upper()))
    return out

def find_medical_code_v4(text: str):  # defensive look‑arounds
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    out = []
    for m in MEDICAL_CODE_RE.finditer(text):
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        if w_s > 0 and NEGATIVE_PRE_TOKEN_RE.match(tokens[w_s - 1]):
            continue
        if _is_short_numeric_false_positive(m, text):
            continue
        ctx_start = max(0, m.start() - 50)
        ctx_end = m.end() + 50
        ctx = text[ctx_start:ctx_end]
        if GENERIC_CODE_TRAP_RE.search(ctx) and not NEEDS_ACRONYM_RE.search(ctx):
            continue
        out.append((w_s, w_e, m.group(0).upper()))
    return out

def find_medical_code_v5(text: str):  # strict stand‑alone
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    return [(idx, idx, tok.upper()) for idx, tok in enumerate(tokens) if STRICT_TOKEN_RE.fullmatch(tok)]

MEDICAL_CODE_FINDERS = {
    "v1": find_medical_code_v1,
    "v2": find_medical_code_v2,
    "v3": find_medical_code_v3,
    "v4": find_medical_code_v4,
    "v5": find_medical_code_v5,
}
