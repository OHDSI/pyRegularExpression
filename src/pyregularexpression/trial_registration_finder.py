"""trial_registration_finder.py – precision/recall ladder for *prospective trial registration* statements.
Five variants (v1–v5):
    • v1 – high recall: any sentence with a registration cue ("trial registration", registered at ClinicalTrials.gov, NCT########, ISRCTN, EudraCT, ChiCTR).
    • v2 – v1 **and** registration verb (registered, prospectively registered, recorded) within ±4 tokens of the cue or identifier.
    • v3 – only inside a *Trial Registration* or *Registration* heading block (first ≈400 characters).
    • v4 – v2 plus explicit registry identifier pattern (NCT\d{8}, ISRCTN\d+, EudraCT \d{4}-\d{6}-\d{2}, ChiCTR-\w+).
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

REGISTRY_ID_RE = re.compile(r"\b(?:NCT\d{8}|ISRCTN\d{6,8}|EudraCT\s*\d{4}-\d{6}-\d{2}|ChiCTR(?:-\w+)?|ANZCTR\s*\w+|JPRN-\w+|ClinicalTrials\.gov|ISRCTN|EudraCT|ChiCTR)\b", re.I)
REG_CUE_RE = re.compile(r"\b(?:trial\s+registration|study\s+registered|registered\s+(?:at|in|with|on)|recorded\s+as|registration\s+was\s+recorded|prospectively\s+registered|ChiCTR|ClinicalTrials\.gov|EudraCT|ISRCTN)\b", re.I)
VERB_RE = re.compile(r"\b(?:registered|recorded|submitted|prospectively\s+registered)\b", re.I)
HEAD_REG_RE = re.compile(r"(?m)^(?:trial\s+registration|registration)\s*[:\-]?\s*$", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"(?:this\s+)?trial\s+was\s+prospectively\s+registered(?:\s+at\s+\w+)?[^\n]{0,60}?(?:NCT\d{8}|ISRCTN\d{6,8}|EudraCT\s*\d{4}-\d{6}-\d{2}|ChiCTR-\w+)", re.I)
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

    for patt in [REG_CUE_RE, REGISTRY_ID_RE]:
        for m in patt.finditer(text):
            context = text[max(0, m.start() - 40): m.end() + 40]
            if TRAP_RE.search(context):
                continue
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    
    return out

def find_trial_registration_v2(text: str, window: int = 6):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    cue_idx = set()
    verb_idx = set()
    
    for patt in [REG_CUE_RE, REGISTRY_ID_RE]:
        for m in patt.finditer(text):
            w_s, _ = _char_to_word((m.start(), m.end()), spans)
            cue_idx.add(w_s)
            
    for m in VERB_RE.finditer(text):
        w_s, _ = _char_to_word((m.start(), m.end()), spans)
        verb_idx.add(w_s)
    out: List[Tuple[int, int, str]] = []
    for c in cue_idx:
        if any(abs(v - c) <= window for v in verb_idx):
            w_s, w_e = _char_to_word(spans[c], spans)
            out.append((w_s, w_e, tokens[c]))
    return out

def find_trial_registration_v3(text: str, block_chars: int = 400):
    spans = _token_spans(text)
    blocks = [(h.end(), min(len(text), h.end() + block_chars)) for h in HEAD_REG_RE.finditer(text)]
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for patt in [REG_CUE_RE, REGISTRY_ID_RE]:
        for m in patt.finditer(text):
            if inside(m.start()):
                w_s, w_e = _char_to_word((m.start(), m.end()), spans)
                out.append((w_s, w_e, m.group(0)))
    return out

def find_trial_registration_v4(text: str, window: int = 6):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    id_idx = {i for i, t in enumerate(tokens) if REGISTRY_ID_RE.fullmatch(t)}
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
