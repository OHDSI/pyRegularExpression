"""eligibility_criteria_finder.py – precision/recall ladder for *inclusion / exclusion eligibility criteria* statements.
Five variants (v1–v5):
    • v1 – high recall: any eligibility cue (eligible patients were, inclusion criteria included, we excluded participants who, exclusion criteria, criteria for enrollment, eligible if).
    • v2 – explicit inclusion OR exclusion cue + condition within ±4 tokens (numeric/age/diagnosis etc.).
    • v3 – only inside an *Eligibility / Inclusion and Exclusion Criteria* heading block (first ~500 characters).
    • v4 – v2 plus both an inclusion and an exclusion cue in the same sentence/nearby to maximise precision.
    • v5 – tight template: paired statement listing age/diagnosis eligibility and exclusion of specific conditions (e.g., “Adults 18–65 with diabetes were eligible; prior insulin use was an exclusion”).
Each finder returns tuples: (start_word_idx, end_word_idx, snippet).
"""

from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

# ─────────────────────────────
# 0. Shared utilities
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
# 1. Regex assets
# ─────────────────────────────
INCL_CUE_RE = re.compile(
    r'\b(eligible\s+(patients|participants|individuals)|inclusion\s+criteria(?:\s+included)?|patients\s+were\s+eligible)\b',
    re.I
)

EXCL_CUE_RE = re.compile(
    r"\b(?:were\s+excluded|we\s+excluded|exclusion\s+criteria(?:\s+included)?|not\s+eligible\s+if|excluded\s+if|were\s+not\s+eligible(?:\s+if)?)\b",
    re.I,
)

QUALIFIER_RE = re.compile(
    r'\b(aged\s+\d{1,3}(?:\s*(?:–|-|to|\u2013|\u2014|\u2212)\s*)\d{1,3}|diagnosed\s+\w+|with\s+(?:a\s+)?\w+|history\s+of\s+\w+|had\s+\w+|those\s+with\s+\w+|patients\s+with\s+\w+)\b',
    re.I,
)

ELIG_CUE_RE = re.compile(
    r"\b(?:inclusion\s+criteria|exclusion\s+criteria|eligibility\s+criteria|enrollment\s+criteria|eligible)\b",
    re.I,
)

HEADING_ELIG_RE = re.compile(
    r"(?m)^\s*(?:eligibility\s+criteria|inclusion\s+and\s+exclusion\s+criteria|study\s+population|participants?)\s*[:\-]?\s*$",
    re.I
)

TRAP_RE = re.compile(
    r"\b(?:diagnostic\s+criteria|classification\s+criteria|performance\s+criteria)\b",
    re.I,
)

TIGHT_TEMPLATE_RE = re.compile(
    r"\b(?:(?:adults?|children|patients|participants)\s+\d{1,3}(?:\s*(?:–|-|to)\s*)\d{1,3}"
    r"|eligible\s+(?:patients|participants|individuals)[^\.\n]{0,100}?(?:aged\s+\d{1,3}(?:\s*(?:–|-|to)\s*)\d{1,3}))"
    r"(?:[^\.\n]{0,100}?(?:inclusion\s+criteria|were\s+eligible))?"
    r"(?:[^\.\n]{0,100}?(?:exclusion\s+criteria|were\s+excluded|not\s+eligible|excluded\s+if))?",
    re.I
)

# ─────────────────────────────
# 2. Helper
# ─────────────────────────────
def _collect(patterns: Sequence[re.Pattern[str]], text: str) -> List[Tuple[int, int, str]]:
    token_spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0, m.start()-25):m.end()+25]):
                continue
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

# ─────────────────────────────
# 3. Finder variants
# ─────────────────────────────
def find_eligibility_criteria_v1(text: str) -> List[Tuple[int, int, str]]:
    """Tier 1 – any inclusion/exclusion cue or tight template."""
    return _collect([INCL_CUE_RE, EXCL_CUE_RE, ELIG_CUE_RE, TIGHT_TEMPLATE_RE], text)

def find_eligibility_criteria_v2(text: str, window: int = 10) -> List[Tuple[int, int, str]]:
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    out = []
    cue_spans = _collect([INCL_CUE_RE, EXCL_CUE_RE], text)
    for cue_start, cue_end, _ in cue_spans:
        for j in range(max(0, cue_start - window), min(len(tokens), cue_end + window)):
            for k in range(1, 5): 
                if j + k <= len(tokens):
                    phrase = " ".join(tokens[j:j + k])
                    if QUALIFIER_RE.search(phrase):
                        w_s = min(cue_start, j)
                        w_e = max(cue_end, j + k)
                        snippet = text[token_spans[w_s][0]:token_spans[w_e - 1][1]]
                        out.append((w_s, w_e, snippet))
                        break  
            else:
                continue
            break
    return out

def find_eligibility_criteria_v3(text: str, block_chars: int = 500) -> List[Tuple[int, int, str]]:
    """Tier 3 – only inside ‘Eligibility’ heading blocks."""    
    token_spans = _token_spans(text)
    blocks: List[Tuple[int, int]] = []
    for h in HEADING_ELIG_RE.finditer(text):
        s = h.end()
        e = min(len(text), s + block_chars)
        blocks.append((s, e))
    def _inside(pos: int): return any(s <= pos < e for s, e in blocks)
    out: List[Tuple[int, int, str]] = []
    for patt in [INCL_CUE_RE, EXCL_CUE_RE]:
        for m in patt.finditer(text):
            if _inside(m.start()):
                w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
                out.append((w_s, w_e, m.group(0)))
    return out

def find_eligibility_criteria_v4(text: str) -> List[Tuple[int, int, str]]:
    """
    v4 – fires if the text contains a valid inclusion cue *before* a valid exclusion cue.
    Returns a single span from the start of the first inclusion match to the end
    of the first exclusion match.
    """
    token_spans = _token_spans(text)

    # 1) collect all inclusion matches, filtering out any inside a negation trap
    raw_inc = list(INCL_CUE_RE.finditer(text))
    inc_matches = []
    for m in raw_inc:
        window_start = max(0, m.start() - 30)
        window_end   = m.end() + 30
        if TRAP_RE.search(text[window_start:window_end]):
            continue
        inc_matches.append(m)

    # 2) if no valid inclusion, bail out
    if not inc_matches:
        return []

    # 3) pick the first valid inclusion
    inc_m = inc_matches[0]

    # 4) find the first exclusion cue
    ex_m = EXCL_CUE_RE.search(text)
    # require exclusion exists and inclusion precedes it
    if not ex_m or inc_m.start() > ex_m.start():
        return []

    # 5) build span from inclusion start to exclusion end
    start_char = inc_m.start()
    end_char   = ex_m.end()

    w_s, w_e = _char_span_to_word_span((start_char, end_char), token_spans)
    snippet  = text[start_char:end_char]
    return [(w_s, w_e, snippet)]


def find_eligibility_criteria_v5(text: str) -> List[Tuple[int, int, str]]:
    """Tier 5 – very tight template-based match for age range + eligibility + exclusion."""
    token_spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for m in TIGHT_TEMPLATE_RE.finditer(text):
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        out.append((w_s, w_e, m.group(0)))
    return out

# ─────────────────────────────
# 4. Public mapping & exports
# ─────────────────────────────
ELIGIBILITY_CRITERIA_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_eligibility_criteria_v1,
    "v2": find_eligibility_criteria_v2,
    "v3": find_eligibility_criteria_v3,
    "v4": find_eligibility_criteria_v4,
    "v5": find_eligibility_criteria_v5,
}

__all__ = [
    "find_eligibility_criteria_v1",
    "find_eligibility_criteria_v2",
    "find_eligibility_criteria_v3",
    "find_eligibility_criteria_v4",
    "find_eligibility_criteria_v5",
    "ELIGIBILITY_CRITERIA_FINDERS",
]

# handy aliases
find_eligibility_criteria_high_recall = find_eligibility_criteria_v1
find_eligibility_criteria_high_precision = find_eligibility_criteria_v5
