
"""trial_design_changes_finder.py – precision/recall ladder for *changes to trial design/protocol* after initiation.
Five variants (v1–v5):
    • v1 – high recall: any modification cue (protocol was amended, changes to the study design, modified the trial protocol, revised inclusion criteria, unplanned adjustment).
    • v2 – modification cue + temporal phrase (after enrolment began, during the trial, mid‑study, X months into the trial) within ±4 tokens.
    • v3 – only inside an *Amendments / Protocol changes* heading block (first ~400 characters).
    • v4 – v2 plus explicit keyword “protocol amendment” or “amended protocol” to exclude pre‑trial changes.
    • v5 – tight template: dated/temporal clause + protocol amendment reason (e.g., “Three months into the trial, the protocol was amended … due to safety concerns”).
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
    w_s = next(i for i, (a, b) in enumerate(spans) if a <= s < b)
    w_e = next(i for i, (a, b) in reversed(list(enumerate(spans))) if a < e <= b)
    return w_s, w_e

CHANGE_CUE_RE = re.compile(r"\b(?:protocol\s+was\s+amended|protocol\s+amendment|amended\s+the\s+protocol|the\s+amended\s+protocol|amended\s+protocol|changes?\s+to\s+(?:the\s+)?(?:study|trial)\s+(?:design|protocol)|modified\s+(?:the\s+)?(?:trial|study)\s+protocol|unplanned\s+adjustments?|revised\s+inclusion\s+criteria|updated\s+study\s+design)\b", re.I)

AMEND_KEY_RE = re.compile(r"\bprotocol\s+amendment|amended\s+protocol|the\s+amended\s+protocol\b", re.I)

HEADING_AMD_RE = re.compile(r"(?m)^(?:protocol\s+amendments?|amendments?|changes\s+to\s+(?:protocol|design))\s*[:\-]?\s*$", re.I)

TRAP_RE = re.compile(r"\b(before\s+(?:enrolment|enrollment|recruitment|trial\s+start)|design\s+changes?\s+planned)\b", re.I)

NUMBER_WORDS = "one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty"

TEMPORAL_RE = re.compile(rf"\b(?:after\s+(?:the\s+)?(?:trial|study)\s+(?:began|started|initiation)|during\s+(?:the\s+)?(?:trial|study)|mid[- ]?study|(?:\d+|{NUMBER_WORDS})\s+(?:weeks?|months?|years?)\s+into\s+(?:the\s+)?(?:trial|study))\b", re.I)

TIGHT_TEMPLATE_RE = re.compile(rf"\b(?:\d+|{NUMBER_WORDS})\s+(?:weeks?|months?|years?)\s+into\s+the\s+(?:trial|study),?\s+the\s+protocol\s+was\s+amended[^\.\n]{{0,120}}", re.I)

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

def find_trial_design_changes_v1(text: str):
    return _collect([CHANGE_CUE_RE], text)

def find_trial_design_changes_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    temporal_hits = [ _char_to_word((m.start(), m.end()), spans) for m in TEMPORAL_RE.finditer(text) ]
    out = []
    for m in CHANGE_CUE_RE.finditer(text):
        w_s, w_e = _char_to_word((m.start(), m.end()), spans)
        if any(ts <= w_e + window and te >= w_s - window for ts, te in temporal_hits):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_trial_design_changes_v3(text: str, block_chars: int = 400):
    spans = _token_spans(text)
    blocks = []
    for h in HEADING_AMD_RE.finditer(text):
        s = h.end(); e = min(len(text), s + block_chars)
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in CHANGE_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_trial_design_changes_v4(text: str, window: int = 4):
    spans = _token_spans(text)
    amend_hits = [ _char_to_word((m.start(), m.end()), spans) for m in AMEND_KEY_RE.finditer(text) ]
    matches = find_trial_design_changes_v2(text, window=window)
    out = []
    for w_s, w_e, snip in matches:
        if any(as_ <= w_e + window and ae >= w_s - window for as_, ae in amend_hits):
            out.append((w_s, w_e, snip))
    return out

def find_trial_design_changes_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

TRIAL_DESIGN_CHANGES_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_trial_design_changes_v1,
    "v2": find_trial_design_changes_v2,
    "v3": find_trial_design_changes_v3,
    "v4": find_trial_design_changes_v4,
    "v5": find_trial_design_changes_v5,
}

__all__ = [
    "find_trial_design_changes_v1", "find_trial_design_changes_v2", "find_trial_design_changes_v3",
    "find_trial_design_changes_v4", "find_trial_design_changes_v5", "TRIAL_DESIGN_CHANGES_FINDERS",
]

find_trial_design_changes_high_recall = find_trial_design_changes_v1
find_trial_design_changes_high_precision = find_trial_design_changes_v5
