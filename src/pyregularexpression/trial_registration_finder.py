"""trial_registration_finder.py – precision/recall ladder for *prospective trial registration* statements.
Five variants (v1–v5):
    • v1 – high recall: any sentence with a registration cue ("trial registration", registered at ClinicalTrials.gov, NCT########, ISRCTN, EudraCT, ChiCTR).
    • v2 – v1 **and** registration verb (registered, prospectively registered, recorded) within ±4 tokens of the cue or identifier.
    • v3 – only inside a *Trial Registration* or *Registration* heading block (first ≈400 characters).
    • v4 – v2 plus explicit registry identifier pattern (NCT\\d{8}, ISRCTN\\d+, EudraCT \\d{4}-\\d{6}-\\d{2}, ChiCTR-\\w+).
    • v5 – tight template: “This trial was prospectively registered at ClinicalTrials.gov (NCT01234567).”
Each finder returns tuples: (start_word_idx, end_word_idx, snippet).
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

TOKEN_RE = re.compile(r"\S+")

def _token_spans(text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_to_word(span: Tuple[int, int], spans: Sequence[Tuple[int, int]]):
    s, e = span
    w_s = next(i for i,(a,b) in enumerate(spans) if a<=s<b)
    w_e = next(i for i,(a,b) in reversed(list(enumerate(spans))) if a<e<=b)
    return w_s, w_e

REGISTRY_ID_RE = re.compile(r"\b(?:NCT\d{8}|ISRCTN\d{6,8}|EudraCT\s*\d{4}-\d{6}-\d{2}|ChiCTR(?:-[\w\d]+)?|ACTRN\d{14}|JPRN-UMIN\d{9}|ClinicalTrials\.gov|ISRCTN|EudraCT|ChiCTR|ANZCTR|JPRN)\b", re.I)
REG_CUE_PATTERNS = [
    re.compile(r"\b(?:trial\s+registration|registration\s+was\s+recorded)\b", re.I),
    re.compile(r"\bstudy(?:\s+\w+){0,2}?\s+registered\b", re.I),
    re.compile(r"\btrial(?:\s+\w+){0,2}?\s+registered\b", re.I),
    re.compile(r"\bprospectively\s+registered\b", re.I),
    re.compile(r"\bregistered\s+(?:at|in|with|on)\b", re.I),
    re.compile(r"\brecorded\s+as\b", re.I),
]
VERB_RE = re.compile(r"\b(?:registered|recorded|submitted|prospectively\s+registered)\b", re.I)
HEAD_REG_RE = re.compile(r"(?m)^(?:trial\s+registration|registration)\s*[:\-]?\s*$", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"((?:this\s+)?trial\s+was\s+prospectively\s+registered(?:\s+at\s+[\w\.]+)?\s*\(?(?:NCT\d{8}|ISRCTN\d{6,8}|EudraCT\s*\d{4}-\d{6}-\d{2}|ChiCTR(?:-[\w\d]+)?)\)?)", re.I)
TRAP_RE = re.compile(r"\bIRB\s+|ethical\s+approval|registry\s+of\s+deeds\b", re.I)

def _collect(patterns: Sequence[re.Pattern[str]], text: str) -> List[Tuple[int, int, str]]:
    spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            context = text[max(0, m.start() - 40): m.end() + 40]
            if TRAP_RE.search(context):
                continue
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_trial_registration_v1(text: str) -> List[Tuple[int, int, str]]:
    """Tier 1 – high recall: any registration cue or registry ID with trap filtering."""
    spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []

    for patt in [*REG_CUE_PATTERNS, REGISTRY_ID_RE]:
        for m in patt.finditer(text):
            context = text[max(0, m.start() - 40): m.end() + 40]
            if TRAP_RE.search(context):
                continue
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    
    return out

def find_trial_registration_v2(text: str, window: int = 6):
    spans = _token_spans(text)
    
    cues = {} # Using dict to store cue info, with start word as key
    for patt in [*REG_CUE_PATTERNS, REGISTRY_ID_RE]:
        for m in patt.finditer(text):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            # If multiple cues start at the same word, the longest is kept
            if w_s not in cues or len(m.group(0)) > len(cues[w_s][2]):
                cues[w_s] = (w_s, w_e, m.group(0))
            
    verb_idx = set()
    for m in VERB_RE.finditer(text):
        w_s, w_e = _char_to_word((m.start(), m.end()), spans)
        for i in range(w_s, w_e + 1):
            verb_idx.add(i)

    out: List[Tuple[int, int, str]] = []
    for c_start, cue_data in cues.items():
        c_end = cue_data[1]

        verb_is_near = False
        for i in range(c_start, c_end + 1):
            for v_idx in verb_idx:
                if abs(i - v_idx) <= window:
                    verb_is_near = True
                    break
            if verb_is_near:
                break

        if verb_is_near:
            out.append(cue_data)

    return out

def find_trial_registration_v3(text: str, block_chars: int = 400):
    spans = _token_spans(text)
    blocks = [(h.end(), min(len(text), h.end() + block_chars)) for h in HEAD_REG_RE.finditer(text)]
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for patt in [*REG_CUE_PATTERNS, REGISTRY_ID_RE]:
        for m in patt.finditer(text):
            if inside(m.start()):
                w_s, w_e = _char_to_word((m.start(), m.end()), spans)
                out.append((w_s, w_e, m.group(0)))
    return out

def find_trial_registration_v4(text: str, window: int = 6):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    id_idx = {i for i, t in enumerate(tokens) if REGISTRY_ID_RE.fullmatch(t.strip('.,'))}
    matches = find_trial_registration_v2(text, window=window)
    out: List[Tuple[int, int, str]] = []
    for w_s, w_e, snip in matches:
        if any(w_s - window <= k <= w_e + window for k in id_idx):
            out.append((w_s, w_e, snip))
    return out

def find_trial_registration_v5(text: str) -> List[Tuple[int, int, str]]:
    """Tier 5 – tight template: prospectively registered trial with registry ID."""
    return _collect([TIGHT_TEMPLATE_RE], text)

TRIAL_REGISTRATION_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_trial_registration_v1,
    "v2": find_trial_registration_v2,
    "v3": find_trial_registration_v3,
    "v4": find_trial_registration_v4,
    "v5": find_trial_registration_v5,
}

__all__ = [
    "find_trial_registration_v1", "find_trial_registration_v2", "find_trial_registration_v3", "find_trial_registration_v4", "find_trial_registration_v5", "TRIAL_REGISTRATION_FINDERS",
]

find_trial_registration_high_recall = find_trial_registration_v1
find_trial_registration_high_precision = find_trial_registration_v5
