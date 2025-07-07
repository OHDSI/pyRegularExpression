"""covariate_adjustment_finder.py – precision/recall ladder for *covariate adjustment* statements.
Five variants (v1–v5):
    • v1 – high recall: any adjustment/control cue or multivariable model mention.
    • v2 – adjustment cue + linking token (“for”, “with”) within ±window tokens.
    • v3 – only inside a *Statistical analysis / Covariate adjustment* heading block.
    • v4 – v2 plus explicit covariate keyword (age, sex, BMI, smoking, etc.), excluding dose‑adjustment traps.
    • v5 – tight template: “HRs adjusted for age, BMI, smoking”, “Multivariable model controlling for age and sex”, etc.
Each function returns a list of tuples: (start_token_idx, end_token_idx, matched_snippet)
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
ADJUST_VERB_RE = re.compile(r"\b(?:adjusted|adjusting|controlling|controlled|accounted)\b", re.I)

LINK_TOKEN_RE = re.compile(r"\b(?:for|with|including)\b", re.I)

COVARIATE_KEY_RE = re.compile(
    r"\b(?:age|sex|gender|bmi|body\s+mass\s+index|smok(?:e|ing)|race|ethnicity|comorbidit(?:y|ies)|diabetes|hypertension|bp|cholesterol|income|education|baseline)\b",
    re.I,
)

MULTIVAR_RE = re.compile(r"\bmultivaria(?:ble|te).*model\b", re.I)

HEADING_ADJ_RE = re.compile(r"(?m)^(?:statistical\s+analysis|covariate\s+adjustment|analytical\s+approach)\s*[:\-]?\s*$", re.I)

TRAP_RE = re.compile(
    r"\b(?:dose|doses|drug|drugs|treatment|treatments|therapy|therapies|regimen|regimens)\b.{0,40}\badjust(?:ment|ed)\b",
    re.I
)


TIGHT_TEMPLATE_RE = re.compile(
    r"(?:adjusted|controlling|controlled)\s+for\s+[A-Za-z0-9,\s]+(?:age|sex|bmi|smok)\w*[^\.\n]{0,40}|multivaria(?:ble|te)\s+model\s+(?:including|adjusted)\s+[^\.\n]{0,60}",
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

def find_covariate_adjustment_v1(text: str) -> List[Tuple[int, int, str]]:
    """Tier 1 – any adjustment cue or multivariable model."""
    return _collect([ADJUST_VERB_RE, MULTIVAR_RE], text)

def find_covariate_adjustment_v2(text: str, window: int = 4) -> List[Tuple[int, int, str]]:
    """Tier 2 – adjustment cue + link token within ±window tokens, excluding traps."""
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    link_idx = {i for i, t in enumerate(tokens) if LINK_TOKEN_RE.fullmatch(t)}
    out: List[Tuple[int, int, str]] = []
    for m in ADJUST_VERB_RE.finditer(text):
        if TRAP_RE.search(text[max(0, m.start()-40): m.end()+40]):
            continue
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        if any(l for l in link_idx if w_s - window <= l <= w_e + window):
            out.append((w_s, w_e, m.group(0)))
    return out


def find_covariate_adjustment_v3(text: str, block_chars: int = 300) -> List[Tuple[int, int, str]]:
    """Tier 3 – within Covariate adjustment heading blocks."""
    token_spans = _token_spans(text)
    blocks: List[Tuple[int, int]] = []
    for h in HEADING_ADJ_RE.finditer(text):
        s = h.end(); nxt = text.find("\n\n", s); e = nxt if 0 <= nxt - s <= block_chars else s + block_chars
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out: List[Tuple[int, int, str]] = []
    for m in ADJUST_VERB_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_covariate_adjustment_v4(text: str, window: int = 6) -> List[Tuple[int, int, str]]:
    """Tier 4 – v2 + explicit covariate keyword near cue."""
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    cov_idx = {i for i, t in enumerate(tokens) if COVARIATE_KEY_RE.search(t.strip(",.;:"))}
    matches = find_covariate_adjustment_v2(text, window=window)
    out: List[Tuple[int, int, str]] = []
    for w_s, w_e, snip in matches:
        if any(c for c in cov_idx if w_s - window <= c <= w_e + window):
            out.append((w_s, w_e, snip))
    return out

def find_covariate_adjustment_v5(text: str) -> List[Tuple[int, int, str]]:
    """Tier 5 – tight template."""
    return _collect([TIGHT_TEMPLATE_RE], text)

# ─────────────────────────────
# 4.  Mapping & exports
# ─────────────────────────────
COVARIATE_ADJUSTMENT_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_covariate_adjustment_v1,
    "v2": find_covariate_adjustment_v2,
    "v3": find_covariate_adjustment_v3,
    "v4": find_covariate_adjustment_v4,
    "v5": find_covariate_adjustment_v5,
}

__all__ = [
    "find_covariate_adjustment_v1", "find_covariate_adjustment_v2", "find_covariate_adjustment_v3", "find_covariate_adjustment_v4", "find_covariate_adjustment_v5", "COVARIATE_ADJUSTMENT_FINDERS",
]

find_covariate_adjustment_high_recall = find_covariate_adjustment_v1
find_covariate_adjustment_high_precision = find_covariate_adjustment_v5
