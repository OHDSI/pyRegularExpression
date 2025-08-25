
"""changes_to_outcomes_finder.py – precision/recall ladder for *changes to prespecified outcomes after trial initiation*.
Five variants (v1–v5):
    • v1 – high recall: any modification cue (changed the primary outcome, added a new secondary outcome, amended the outcomes, outcome was revised).
    • v2 – modification cue + outcome keyword within ±4 tokens and temporal phrase (mid-study, after trial started, X months into the trial).
    • v3 – only inside a *Protocol amendments / Outcome changes* heading block (first ~400 chars).
    • v4 – v2 plus explicit reason phrase (due to, because of, owing to) nearby for extra precision.
    • v5 – tight template: “Due to low event rate, the primary outcome was changed from OS to DFS midway.”
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

# regex assets

HEADING_CHG_RE = re.compile(
    r"(?m)^(?:[ \t]*outcome\s+changes?|changes\s+to\s+outcomes?|protocol\s+amendments?)\s*[:\-]?\s*$",
    re.I
)
TRAP_RE = re.compile(r"\bchanges?\s+in\s+outcomes?|significant\s+change\s+in\s+outcome\s+values?\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(
    r"\b(?:due\s+to|because\s+of|owing\s+to)\s+[^\.\n]{0,60}?primary\s+outcome\s+was\s+changed\s+from\s+[^\.\n]{0,40}?\s+to\s+[^\.\n]{0,40}?\s*(?:mid[- ]?(?:study|way)|after\s+\d+\s+events)\b",
    re.I,
)
TEMPORAL_RE = re.compile(
    r"\b("
    r"after|during|mid(?:[-\s])?study|midway|"
    r"\d+\s+(weeks?|months?|years?)\s+into|"
    r"(?:the\s+)?(trial|study)\s+(started|began)|"
    r"(?:after|within)\s+\d+\s+(weeks?|months?|days?|years?)"
    r")\b",
    re.I,
)
MOD_CUE_RE = re.compile(
    r"\b("
    r"(?:changed|added|amended|revised|modified|updated|altered|introduced)\b"
    r"(?:\s+(?:a|the|new|existing|additional)?\s*(?:primary|secondary|tertiary|outcomes?|measures?))*"
    r"|(?:outcomes?\s+(?:were\s+)?(?:changed|amended|revised|modified|updated))"
    r")\b",
    re.I
)
REASON_RE = re.compile(
    r"\b(due\s+to|because\s+of|owing\s+to|as\s+a\s+result\s+of|on\s+account\s+of)\b",
    re.I,
)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            print(f"[DEBUG] Regex matched: '{m.group(0)}' at span {m.start()}–{m.end()}")
            if TRAP_RE.search(text[max(0, m.start()-30):m.end()+30]):  # Trap detection
                print("[DEBUG] Trap detected, skipping match:", m.group(0))
                continue
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            print("[DEBUG] Adding match:", m.group(0))
            out.append((w_s, w_e, m.group(0)))
    return out

# Finder tiers
def find_changes_to_outcomes_v1(text: str):
    return _collect([MOD_CUE_RE], text)

def find_changes_to_outcomes_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    mod_matches = [(m.start(), m.end(), m.group()) for m in MOD_CUE_RE.finditer(text)]
    temp_matches = [(m.start(), m.end(), m.group()) for m in TEMPORAL_RE.finditer(text)]
    out = []
    for m_start, m_end, snippet in mod_matches:
        w_s, w_e = _char_to_word((m_start, m_end), spans)
        for t_start, t_end, _ in temp_matches:
            t_w_s, t_w_e = _char_to_word((t_start, t_end), spans)
            if max(w_s, t_w_s) - min(w_e, t_w_e) <= window:
                out.append((w_s, w_e, snippet))
                break
    return out

def find_changes_to_outcomes_v3(text: str, block_chars: int = 500):
    spans = _token_spans(text)
    blocks = []
    for h in HEADING_CHG_RE.finditer(text):
        s = h.end()
        e = min(len(text), s + block_chars)
        blocks.append((s, e))
    out = []
    for m in MOD_CUE_RE.finditer(text):
        for s, e in blocks:
            if s <= m.start() < e:
                w_s, w_e = _char_to_word((m.start(), m.end()), spans)
                out.append((w_s, w_e, m.group(0)))
                break
    return out

def find_changes_to_outcomes_v4(text: str, window: int = 10):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    matches = find_changes_to_outcomes_v1(text)
    reason_idx = set()
    for m in REASON_RE.finditer(text):
        w_s, w_e = _char_to_word((m.start(), m.end()), spans)
        reason_idx.update(range(w_s, w_e + 1))
    out = []
    for w_s, w_e, snip in matches:
        mod_idx = w_s  # start token index of modification cue
        start_idx = max(0, mod_idx - window)
        end_idx = min(len(tokens), w_e + window + 1)
        if any(r in range(start_idx, end_idx) for r in reason_idx):
            out.append((w_s, w_e, snip))
    return out

def find_changes_to_outcomes_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

# mapping
CHANGES_TO_OUTCOMES_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]]={
    "v1":find_changes_to_outcomes_v1,
    "v2":find_changes_to_outcomes_v2,
    "v3":find_changes_to_outcomes_v3,
    "v4":find_changes_to_outcomes_v4,
    "v5":find_changes_to_outcomes_v5,
}

__all__=["find_changes_to_outcomes_v1","find_changes_to_outcomes_v2","find_changes_to_outcomes_v3",
         "find_changes_to_outcomes_v4","find_changes_to_outcomes_v5","CHANGES_TO_OUTCOMES_FINDERS"]

find_changes_to_outcomes_high_recall = find_changes_to_outcomes_v1
find_changes_to_outcomes_high_precision = find_changes_to_outcomes_v5
