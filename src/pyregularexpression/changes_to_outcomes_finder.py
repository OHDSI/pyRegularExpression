
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
MOD_CUE_RE = re.compile(r"\b(?:changed|amended|revised|modified|added)\s+(?:the\s+)?(?:primary|secondary)?\s*outcomes?\b", re.I)
TEMPORAL_RE = re.compile(r"\b(?:after\s+(?:trial|study)\s+(?:start|began)|during\s+(?:the\s+)?trial|mid[- ]?study|\d+\s+(?:weeks?|months?|years?)\s+into\s+(?:the\s+)?trial)\b", re.I)
REASON_RE = re.compile(r"\b(?:due\s+to|because\s+of|owing\s+to)\b", re.I)
HEADING_CHG_RE = re.compile(r"(?m)^(?:outcome\s+changes?|changes\s+to\s+outcomes?|protocol\s+amendments?)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\bchanges?\s+in\s+outcomes?|significant\s+change\s+in\s+outcome\s+values?\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(
    r"\b(?:due\s+to|because\s+of|owing\s+to)\s+[^\.\n]{0,60}?primary\s+outcome\s+was\s+changed\s+from\s+[^\.\n]{0,40}?\s+to\s+[^\.\n]{0,40}?(?:mid[- ]?study|after\s+\d+\s+events)\b",
    re.I,
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

# Finder tiers
def find_changes_to_outcomes_v1(text: str):
    return _collect([MOD_CUE_RE], text)

def find_changes_to_outcomes_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    temp_idx = {i for i,t in enumerate(tokens) if TEMPORAL_RE.fullmatch(t)}
    mod_idx = {i for i,t in enumerate(tokens) if MOD_CUE_RE.fullmatch(t)}
    out=[]
    for i in mod_idx:
        if any(t for t in temp_idx if abs(t-i)<=window):
            w_s,w_e=_char_to_word(spans[i],spans)
            out.append((w_s,w_e,tokens[i]))
    return out

def find_changes_to_outcomes_v3(text: str, block_chars: int = 400):
    spans=_token_spans(text)
    blocks=[]
    for h in HEADING_CHG_RE.finditer(text):
        s=h.end(); e=min(len(text),s+block_chars)
        blocks.append((s,e))
    inside=lambda p: any(s<=p<e for s,e in blocks)
    out=[]
    for m in MOD_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_changes_to_outcomes_v4(text: str, window: int = 6):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    reason_idx={i for i,t in enumerate(tokens) if REASON_RE.fullmatch(t)}
    matches=find_changes_to_outcomes_v2(text,window=window)
    out=[]
    for w_s,w_e,snip in matches:
        if any(r for r in reason_idx if w_s-window<=r<=w_e+window):
            out.append((w_s,w_e,snip))
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
