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
    if not spans:
        return []

    # Find all restriction and randomization keywords as character spans
    restriction_spans = [(m.start(), m.end()) for m in RESTRICT_CUE_RE.finditer(text)]
    ratio_spans = [(m.start(), m.end()) for m in RATIO_RE.finditer(text)]
    all_restriction_spans = restriction_spans + ratio_spans

    rand_key_spans = [(m.start(), m.end()) for m in RAND_KEY_RE.finditer(text)]

    if not all_restriction_spans or not rand_key_spans:
        return []

    # Convert character spans to word indices
    restriction_word_indices = [_char_to_word(s, spans) for s in all_restriction_spans]
    rand_key_word_indices = [_char_to_word(s, spans) for s in rand_key_spans]

    out = []
    for r_ws, r_we in restriction_word_indices:
        is_near_rand_key = False
        for k_ws, k_we in rand_key_word_indices:
            # Check for overlap or proximity within the window.
            # Proximity is defined as the number of tokens between the spans.
            is_overlapping = max(k_ws, r_ws) <= min(k_we, r_we)

            if is_overlapping:
                is_near_rand_key = True
                break

            # Check distance if not overlapping
            # Distance is the number of tokens between the end of one span and the start of the other.
            if r_ws > k_we: # restriction is after keyword
                distance = r_ws - k_we - 1
            else: # keyword is after restriction
                distance = k_ws - r_we - 1

            if distance <= window:
                is_near_rand_key = True
                break

        if is_near_rand_key:
            # Extract the original text snippet for the match
            start_char = spans[r_ws][0]
            end_char = spans[r_we][1]
            snippet = text[start_char:end_char]

            # Avoid traps
            if TRAP_RE.search(text[max(0, start_char-30):end_char+30]):
                continue

            out.append((r_ws, r_we, snippet))

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
    if not spans:
        return []

    matches_v2 = find_randomization_type_restriction_v2(text, window=window)
    if not matches_v2:
        return []

    # Find all ratio and modifier matches as word spans
    ratio_spans = [_char_to_word(m.span(), spans) for m in RATIO_RE.finditer(text)]
    mod_spans = [_char_to_word(m.span(), spans) for m in MODIFIER_RE.finditer(text)]

    out = []
    for w_s, w_e, snip in matches_v2:
        # Check for a ratio "near" the match from v2
        # We define "near" as being in the same sentence, which we approximate with a large window
        sentence_window = 15
        ratio_near = any(
            max(r_ws, w_s) <= min(r_we, w_e) or  # Overlap
            (w_s > r_we and w_s - r_we - 1 <= sentence_window) or  # Match is after ratio
            (r_ws > w_e and r_ws - w_e - 1 <= sentence_window)  # Ratio is after match
            for r_ws, r_we in ratio_spans
        )

        # For modifier counting, we need to be stricter to avoid partial matches inside tokens like '(blocks'
        MODIFIER_RE_STRICT = re.compile(r"^(?:block|blocks?|permuted|stratified|minimization|strata|ratio)$", re.I)
        tokens = [text[s:e] for s, e in spans]

        mods_near = 0
        for i, token in enumerate(tokens):
            # Check if the token is within the sentence window of the match
            is_in_window = (max(i, w_s) <= min(i, w_e) or
                            (w_s > i and w_s - i - 1 <= sentence_window) or
                            (i > w_e and i - w_e - 1 <= sentence_window))

            if is_in_window and MODIFIER_RE_STRICT.fullmatch(token):
                mods_near += 1

        if ratio_near or mods_near >= 2:
            out.append((w_s, w_e, snip))

    # Deduplicate the results, as multiple v2 matches might qualify
    return sorted(list(set(out)))

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
