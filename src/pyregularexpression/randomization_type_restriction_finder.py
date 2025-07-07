"""randomization_type_restriction_finder.py – precision/recall ladder for *randomization type / restrictions* (blocking, stratification, ratio).
Five variants (v1–v5):
    • v1 – high recall: any restriction cue (block randomization, permuted blocks, stratified by, minimization, 1:1 ratio, 2:1 ratio).
    • v2 – restriction cue + randomisation keyword (randomized, allocation, sequence) within ±4 tokens.
    • v3 – only inside a *Randomisation / Allocation* heading block (first ~400 characters).
    • v4 – v2 plus explicit allocation ratio (e.g., 1:1, 2:1) or multiple modifiers (block + stratified) in same sentence.
    • v5 – tight template: “Randomized 2:1 to drug vs placebo using permuted blocks of six, stratified by site.”
Each function returns tuples: (start_word_idx, end_word_idx, snippet).
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

TOKEN_RE = re.compile(r"\S+")

def _token_spans(text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_to_word(span: Tuple[int, int], spans: Sequence[Tuple[int, int]]):
    s, e = span
    w_s = next(i for i, (a, b) in enumerate(spans) if a <= s < b)
    w_e = next(i for i, (a, b) in reversed(list(enumerate(spans))) if a < e <= b)
    return w_s, w_e

# Regex assets
RESTRICT_CUE_RE = re.compile(
    r"\b(?:block\s+randomi[sz]ation|permuted\s+blocks?|minimi[sz]ation|stratified\s*(?:by)?|strata|shuffled\s+envelopes)\b",
    re.I,
)
RATIO_RE = re.compile(r"\b\d+:\d+\b")
RAND_KEY_RE = re.compile(r"\b(?:randomi[sz](?:ed|ation)|allocation|sequence|assigned)\b", re.I)
MODIFIER_RE = re.compile(r"\b(?:block|blocks?|permuted|stratified|minimization|strata|ratio)\b", re.I)
HEADING_RAND_RE = re.compile(r"(?m)^(?:randomi[sz]ation|allocation|sequence\s+generation)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\brandomly\s+assigned|random\s+sampling|random\s+effects?\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(
    r"randomi[sz]ed\s+\d+:\d+\s+[^\.\n]{0,100}permuted\s+blocks?[^\.\n]{0,80}stratified\s+by", re.I
)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0, m.start()-30):m.end()+30]):
                continue
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_randomization_type_restriction_v1(text: str):
    return _collect([RESTRICT_CUE_RE, RATIO_RE], text)

def find_randomization_type_restriction_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    key_idx = {i for i, t in enumerate(tokens) if RAND_KEY_RE.fullmatch(t)}
    rest_idx = {i for i, t in enumerate(tokens) if RESTRICT_CUE_RE.fullmatch(t) or RATIO_RE.fullmatch(t)}
    out = []
    for i in rest_idx:
        if any(k for k in key_idx if abs(k - i) <= window):
            w_s, w_e = _char_to_word(spans[i], spans)
            out.append((w_s, w_e, tokens[i]))
    return out

def find_randomization_type_restriction_v3(text: str, block_chars: int = 400):
    spans = _token_spans(text)
    blocks = []
    for h in HEADING_RAND_RE.finditer(text):
        s = h.end(); e = min(len(text), s + block_chars)
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in RESTRICT_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_randomization_type_restriction_v4(text: str, window: int = 6):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    ratio_idx = {i for i, t in enumerate(tokens) if RATIO_RE.fullmatch(t)}
    mod_idx = {i for i, t in enumerate(tokens) if MODIFIER_RE.fullmatch(t)}
    matches = find_randomization_type_restriction_v2(text, window=window)
    out = []
    for w_s, w_e, snip in matches:
        mods_near = sum(1 for m in mod_idx if w_s - window <= m <= w_e + window)
        ratio_near = any(r for r in ratio_idx if w_s - window <= r <= w_e + window)
        if ratio_near or mods_near >= 2:
            out.append((w_s, w_e, snip))
    return out

def find_randomization_type_restriction_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

RANDOMIZATION_TYPE_RESTRICTION_FINDERS: Dict[str, Callable[[str], List[Tuple[int,int,str]]]] = {
    "v1": find_randomization_type_restriction_v1,
    "v2": find_randomization_type_restriction_v2,
    "v3": find_randomization_type_restriction_v3,
    "v4": find_randomization_type_restriction_v4,
    "v5": find_randomization_type_restriction_v5,
}

__all__ = [
    "find_randomization_type_restriction_v1", "find_randomization_type_restriction_v2",
    "find_randomization_type_restriction_v3", "find_randomization_type_restriction_v4",
    "find_randomization_type_restriction_v5", "RANDOMIZATION_TYPE_RESTRICTION_FINDERS",
]

find_randomization_type_restriction_high_recall = find_randomization_type_restriction_v1
find_randomization_type_restriction_high_precision = find_randomization_type_restriction_v5
