"""
data_provenance_finder.py – precision/recall ladder for *data provenance* 
(references to origin, lineage, or traceability of datasets).

Five variants (v1–v5):
    • v1 – high recall: any clause containing `provenance`, `origin`, `lineage`, `source data`, 
      `traceability`, `audit trail`.
    • v2 – v1 **and** paired with verbs like `documented`, `recorded`, `tracked`, `maintained` 
      within ±4 tokens.
    • v3 – only inside a *Methods*, *Data Source*, or *Provenance* heading block (first ~400 characters).
    • v4 – v2 plus explicit mention of dataset/file/source system (e.g. “raw data,” “clinical record,” “CSV”).
    • v5 – tight template: “Data provenance documented in audit trail; lineage maintained across transformations.”

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

# Core regex patterns
PROVENANCE_RE = re.compile(r"\b(?:provenance|lineage|origin|traceability|audit\s+trail|source\s+data)\b", re.I)
VERB_RE = re.compile(r"\b(?:document(?:ed|ation)?|record(?:ed|ing)?|track(?:ed|ing)?|maintain(?:ed|ance)?|capture(?:d)?|log(?:ged|ging)?)\b", re.I)
DATASET_RE = re.compile(r"\b(?:dataset|data\s+set|raw\s+data(?:\s+\w+)*|clinical\s+record(?:s|\s+system)?|CSV|Excel|database|source\s+system|file|files)\b", re.I)
HEAD_SEC_RE = re.compile(r"(?i)(methods|data\s+source|provenance|traceability|audit)\s*[:\-]?", re.M)
TIGHT_TEMPLATE_RE = re.compile(r"(?:data\s+)?provenance\s+(?:was\s+)?(documented|recorded|maintained).*?(audit\s+trail|lineage)", re.I | re.DOTALL)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

# Variant 1 – High recall
def find_data_provenance_v1(text: str):
    return _collect([PROVENANCE_RE], text)

# Variant 2 – Add provenance + verbs within ±4 tokens
def find_data_provenance_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    prov_idx = {i for i, t in enumerate(tokens) if PROVENANCE_RE.search(t)}
    verb_idx = {i for i, t in enumerate(tokens) if VERB_RE.search(t)}
    out = []
    for p_i in prov_idx:
        nearby_verbs = [v for v in verb_idx if abs(v - p_i) <= window]
        if not nearby_verbs:
            nearby_verbs = [v for v in verb_idx if abs(v - p_i) <= window + 1]
        if nearby_verbs:
            w_s = min([p_i] + nearby_verbs)
            w_e = max([p_i] + nearby_verbs)
            snippet = " ".join(tokens[w_s:w_e+1])
            out.append((w_s, w_e, snippet))
    return out

# Variant 3 – Only inside heading blocks
def find_data_provenance_v3(text: str, block_chars: int = 400):
    spans = _token_spans(text)
    blocks = []
    for h in HEAD_SEC_RE.finditer(text):
        s = h.end(); e = min(len(text), s + block_chars)
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in PROVENANCE_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

# Variant 4 – Provenance + dataset/file mention
def find_data_provenance_v4(text: str, window: int = 6):
    base_matches = find_data_provenance_v2(text, window=window)
    spans = _token_spans(text)
    out = []
    dataset_spans = [(m.start(), m.end()) for m in DATASET_RE.finditer(text)]
    for w_s, w_e, snip in base_matches:
        char_s, char_e = spans[w_s][0], spans[w_e][1]
        for d_s, d_e in dataset_spans:
            context = text[max(0, d_s - 10):min(len(text), d_e + 20)].lower()
            if "no dataset" in context or "without dataset" in context:
                continue
            if not (d_e < char_s - 50 or d_s > char_e + 50):
                out.append((w_s, w_e, snip))
                break
    return out

# Variant 5 – Tight template
def find_data_provenance_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

DATA_PROVENANCE_FINDERS: Dict[str, Callable[[str], List[Tuple[int,int,str]]]] = {
    "v1": find_data_provenance_v1,
    "v2": find_data_provenance_v2,
    "v3": find_data_provenance_v3,
    "v4": find_data_provenance_v4,
    "v5": find_data_provenance_v5,
}

__all__ = [
    "find_data_provenance_v1",
    "find_data_provenance_v2",
    "find_data_provenance_v3",
    "find_data_provenance_v4",
    "find_data_provenance_v5",
    "DATA_PROVENANCE_FINDERS",
]

find_data_provenance_high_recall = find_data_provenance_v1
find_data_provenance_high_precision = find_data_provenance_v5
