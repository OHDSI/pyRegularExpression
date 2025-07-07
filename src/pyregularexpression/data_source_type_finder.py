
"""data_source_type_finder.py – precision/recall ladder for *data‑source type* declarations.
Five variants (v1–v5):
    • v1 – high recall: any explicit data‑type keyword (EHR, claims, registry, survey, etc.).
    • v2 – data‑type keyword within ±2 tokens of “data/records/dataset”.
    • v3 – only inside a *Data source / Data type* heading block.
    • v4 – v2 plus qualifier tokens (nationwide, administrative, insurance, population‑based) to avoid generic “database” mentions.
    • v5 – tight template: “We used nationwide insurance claims data…”, “EHR‑derived database from 2005‑20”, etc.
Each finder returns a list of tuples: (start_token_idx, end_token_idx, matched_snippet)
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

TOKEN_RE = re.compile(r"\S+")

def _token_spans(text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_span_to_word_span(span: Tuple[int, int], token_spans: Sequence[Tuple[int, int]]) -> Tuple[int, int]:
    s_char, e_char = span
    w_start = next(i for i, (s, e) in enumerate(token_spans) if s <= s_char < e)
    w_end = next(i for i, (s, e) in reversed(list(enumerate(token_spans))) if s < e_char <= e)
    return w_start, w_end

TYPE_KEYWORD_RE = re.compile(
    r"\b(?:ehr|electronic\s+health\s+records?|insurance\s+claims?|claims?\s+data|administrative\s+claims?|registry\s+data|registries|survey\s+data|population[- ]?based\s+registry|national\s+inpatient\s+sample|hospital\s+discharge\s+data)\b",
    re.I,
)

DATA_TOKEN_RE = re.compile(r"\b(?:data|records?|dataset)\b", re.I)
QUALIFIER_RE = re.compile(r"\b(?:nationwide|national|administrative|insurance|population[- ]?based|multi[- ]?center|statewide)\b", re.I)

HEADING_SRC_RE = re.compile(r"(?m)^(?:data\s+source|data\s+type|data\s+sources?)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\b(?:datatable|database\s+software|sql\s+database)\b", re.I)

TIGHT_TEMPLATE_RE = re.compile(r"(?:nationwide|insurance|administrative|ehr|registry|survey)\s+(?:claims?|records?|data)[^\.\n]{0,60}", re.I)

def _collect(patterns: Sequence[re.Pattern[str]], text: str) -> List[Tuple[int, int, str]]:
    token_spans = _token_spans(text)
    out = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(m.group(0)):
                continue
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_data_source_type_v1(text: str):
    return _collect([TYPE_KEYWORD_RE], text)

def find_data_source_type_v2(text: str, window: int = 2):
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    data_idx = {i for i, t in enumerate(tokens) if DATA_TOKEN_RE.fullmatch(t)}
    out = []
    for m in TYPE_KEYWORD_RE.finditer(text):
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        if any(d for d in data_idx if w_s - window <= d <= w_e + window):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_data_source_type_v3(text: str, block_chars: int = 250):
    token_spans = _token_spans(text)
    blocks = []
    for h in HEADING_SRC_RE.finditer(text):
        s = h.end()
        nxt = text.find("\n\n", s)
        e = nxt if 0 <= nxt - s <= block_chars else s + block_chars
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in TYPE_KEYWORD_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_data_source_type_v4(text: str, window: int = 3):
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    qual_idx = {i for i, t in enumerate(tokens) if QUALIFIER_RE.fullmatch(t)}
    matches = find_data_source_type_v2(text, window=window)
    out = []
    for w_s, w_e, snip in matches:
        if any(q for q in qual_idx if w_s - window <= q <= w_e + window):
            out.append((w_s, w_e, snip))
    return out

def find_data_source_type_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

DATA_SOURCE_TYPE_FINDERS: Dict[str, Callable[[str], List[Tuple[int,int,str]]]] = {
    "v1": find_data_source_type_v1,
    "v2": find_data_source_type_v2,
    "v3": find_data_source_type_v3,
    "v4": find_data_source_type_v4,
    "v5": find_data_source_type_v5,
}

__all__ = ["find_data_source_type_v1","find_data_source_type_v2","find_data_source_type_v3","find_data_source_type_v4","find_data_source_type_v5","DATA_SOURCE_TYPE_FINDERS"]

find_data_source_type_high_recall = find_data_source_type_v1
find_data_source_type_high_precision = find_data_source_type_v5
