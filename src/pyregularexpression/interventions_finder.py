"""interventions_finder.py – precision/recall ladder for *interventions / treatments* delivered to study arms.
Five variants (v1–v5):
    • v1 – high recall: any arm/treatment cue (intervention group received, treated with, control group given, assigned to X, underwent Y, dosage X mg).
    • v2 – arm cue + treatment/action/agent within ±4 tokens (drug, dose, procedure, placebo, program).
    • v3 – only inside an *Intervention(s) / Treatment* heading block (first ~400 chars).
    • v4 – v2 plus explicit control arm or comparator cue in same sentence/nearby (control group, placebo, usual care) to ensure group context.
    • v5 – tight template: paired description of experimental vs control arms.
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

ARM_CUE_RE = re.compile(r"\b(?:intervention|treatment|experimental|control|placebo|comparison|standard\s+care|usual\s+care)\s+(?:arm|group)\b", re.I)
ACTION_RE = re.compile(r"\b(?:received|were\s+given|was\s+given|treated\s+with|administered|assigned\s+to|underwent|received\s+a|underwent\s+a)\b", re.I)
AGENT_RE = re.compile(r"\b(?:placebo|dose|dosage|mg|g|mcg|units?|tablet|capsule|surgery|procedure|program|therapy|exercise|aerobic|drug|medication|vaccine)\b", re.I)
CONTROL_CUE_RE = re.compile(r"\b(?:control\s+group|placebo\s+group|usual\s+care|standard\s+care|sham)\b", re.I)
HEADING_INT_RE = re.compile(r"(?m)^(?:interventions?|treatments?|experimental\s+design|study\s+arms?)\s*[:\-]?\s*(.*)$", re.I)
TRAP_RE = re.compile(r"\bpolicy\s+interventions?|government\s+interventions?|intervention\s+strategies\s+were\s+discussed\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"\bexperimental\s+arm\s+[^\.\n]{0,120}?\breceived\b[^\.\n]{0,120}?(?:control|placebo|usual\s+care)\s+arm\s+[^\.\n]{0,120}?\b(?:received|continued)\b", re.I)

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

def find_interventions_v1(text: str):
    cue_re = re.compile(r"(?:intervention\s+group\s+received|treatment\s+group\s+received|treated\s+with|control\s+group\s+(?:was\s+given|received)|assigned\s+to\s+[A-Za-z])", re.I)
    return _collect([cue_re], text)

def find_interventions_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    out = []
    visited = set() 
    for i, t in enumerate(tokens):
        start = max(0, i - window)
        end = min(len(tokens), i + window + 1)
        snippet_tokens = tokens[start:end]
        snippet_text = " ".join(snippet_tokens)
        if (ARM_CUE_RE.search(snippet_text) and
            (ACTION_RE.search(snippet_text) or AGENT_RE.search(snippet_text))):
            key = (start, end-1)
            if key not in visited:
                visited.add(key)
                out.append((start, end-1, snippet_text))
    return out

def find_interventions_v3(text: str, block_chars: int = 400):
    spans = _token_spans(text)
    blocks = []
    for h in HEADING_INT_RE.finditer(text):
        s = h.start(1)  
        e = min(len(text), s + block_chars)
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in ARM_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_interventions_v4(text: str, window: int = 6):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    matches = find_interventions_v2(text, window=window)
    out = []
    for start, end, snippet in matches:
        context = " ".join(tokens[max(0, start - window): min(len(tokens), end + window + 1)])
        if CONTROL_CUE_RE.search(context):
            out.append((start, end, snippet))
    return out

def find_interventions_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

INTERVENTIONS_FINDERS: Dict[str, Callable[[str], List[Tuple[int,int,str]]]] = {
    "v1": find_interventions_v1,
    "v2": find_interventions_v2,
    "v3": find_interventions_v3,
    "v4": find_interventions_v4,
    "v5": find_interventions_v5,
}

__all__ = ["find_interventions_v1","find_interventions_v2","find_interventions_v3","find_interventions_v4","find_interventions_v5","INTERVENTIONS_FINDERS"]

find_interventions_high_recall = find_interventions_v1
find_interventions_high_precision = find_interventions_v5
