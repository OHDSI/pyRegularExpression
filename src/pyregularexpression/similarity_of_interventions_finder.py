"""similarity_of_interventions_finder.py – precision/recall ladder for *similarity of interventions*.
Five variants (v1–v5):
    • v1 – high recall: any similarity cue (identical placebo, matched placebo, indistinguishable, sham procedure, double‑dummy).
    • v2 – similarity cue + intervention form word (placebo, capsule, injection, device, procedure) within ±4 tokens.
    • v3 – only inside a *Similarity of Interventions* heading block.
    • v4 – v2 plus explicit qualifier (identical, matched, indistinguishable) and form word in same context.
    • v5 – tight template: “Control arm received placebo injection identical in appearance to active drug.”
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

SIM_CUE_RE = re.compile(
    r"\b(?:identical|matched|matching|indistinguishable|double[- ]dummy|dummy|sham)\b"
    r"(?:[^\.\n]{0,20}?\b(?:placebo|capsule|tablet|injection|procedure|device|patch|solution|syringe))?",
    re.I,
)

FORM_RE = re.compile(r"\b(?:placebo|capsule|tablet|injection|solution|suspension|device|procedure|patch|syringe)\b", re.I)
QUAL_RE = re.compile(r"\b(?:identical|matched|indistinguishable)\b", re.I)
HEAD_SIM_RE = re.compile(r"(?m)^(?:similarity\s+of\s+interventions?|blinding\s+materials?|manufacturing\s+matching)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\bsimilar\s+in\s+(?:duration|effect|class)\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(
    r"placebo\s+(?:capsule|tablet|injection|solution)\s+identical\s+in\s+appearance\s+to\s+(?:active|study)\s+drug",
    re.I,
)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0, m.start()-25):m.end()+25]):
                continue
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_similarity_of_interventions_v1(text: str):
    return _collect([SIM_CUE_RE], text)

def find_similarity_of_interventions_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    form_idx = {i for i, t in enumerate(tokens) if FORM_RE.fullmatch(t)}
    sim_idx = {i for i, t in enumerate(tokens) if SIM_CUE_RE.fullmatch(t)}
    out = []
    for s_i in sim_idx:
        if any(f for f in form_idx if abs(f - s_i) <= window):
            w_s, w_e = _char_to_word(spans[s_i], spans)
            out.append((w_s, w_e, tokens[s_i]))
    return out

def find_similarity_of_interventions_v3(text: str, block_chars: int = 400):
    spans = _token_spans(text)
    blocks = []
    for h in HEAD_SIM_RE.finditer(text):
        s = h.end(); e = min(len(text), s + block_chars)
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in SIM_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_similarity_of_interventions_v4(text: str, window: int = 6):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    matches = find_similarity_of_interventions_v2(text, window=window)
    out = []
    for w_s, w_e, snip in matches:
        qual_near = any(QUAL_RE.fullmatch(tokens[i]) for i in range(max(0, w_s-window), min(len(tokens), w_e+window)))
        form_near = any(FORM_RE.fullmatch(tokens[i]) for i in range(max(0, w_s-window), min(len(tokens), w_e+window)))
        if qual_near and form_near:
            out.append((w_s, w_e, snip))
    return out

def find_similarity_of_interventions_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

SIMILARITY_OF_INTERVENTIONS_FINDERS: Dict[str, Callable[[str], List[Tuple[int,int,str]]]] = {
    "v1": find_similarity_of_interventions_v1,
    "v2": find_similarity_of_interventions_v2,
    "v3": find_similarity_of_interventions_v3,
    "v4": find_similarity_of_interventions_v4,
    "v5": find_similarity_of_interventions_v5,
}

__all__ = ["find_similarity_of_interventions_v1","find_similarity_of_interventions_v2","find_similarity_of_interventions_v3","find_similarity_of_interventions_v4","find_similarity_of_interventions_v5","SIMILARITY_OF_INTERVENTIONS_FINDERS"]

find_similarity_of_interventions_high_recall = find_similarity_of_interventions_v1
find_similarity_of_interventions_high_precision = find_similarity_of_interventions_v5
