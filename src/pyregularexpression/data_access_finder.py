
"""data_access_finder.py – precision/recall ladder for *data‑access / availability* statements.

Five variants (v1–v5):

    • v1 – high recall: any availability/permission keyword (available, accessible, request, agreement, repository, embargo, restricted).
    • v2 – keyword within ±3 tokens of the word “data” or “dataset”.
    • v3 – only inside a *Data access / Availability* heading block (or acknowledgements / data‑sharing section).
    • v4 – v2 plus formal permission cue (approval, agreement, Committee, IRB) or repository reference (Zenodo, Dryad, dbGaP).
    • v5 – tight template: “Dataset available upon reasonable request with institutional approval”, “Data are deposited in the Zenodo repository under accession …”, etc.

Each function returns a list of tuples: (start_token_idx, end_token_idx, matched_snippet).
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

# ---------- regex assets ----------
AVAIL_RE = re.compile(r"\b(?:available|accessible|access|accession|request|upon\s+request|on\s+request|repository|deposited|released|shared|restricted|embargo)\b", re.I)
DATA_TOKEN_RE = re.compile(r"\b(?:data(?:set)?|datasets|database)\b", re.I)
PERMISSION_RE = re.compile(r"\b(?:approval|agreement|committee|irb|dua|data\s+use\s+agreement|ethics|governance)\b", re.I)
REPO_RE = re.compile(r"\b(?:zenodo|dryad|figshare|dbgap|eurostat|dataverse|icpsr|ukbiobank|nda)\b", re.I)
HEADING_ACC_RE = re.compile(r"(?m)^(?:data\s+(?:access|availability|sharing)|availability\s+of\s+data|data\s+statement)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\baccess\s+to\s+care|open\s+access\s+journal|internet\s+access\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(
    r"data(?:set)?\s+(?:are|is|were)\s+(?:available|accessible|deposited)[^\.\n]{0,120}(?:request|zenodo|dryad|dbgap|agreement|approval)\b",
    re.I,
)

# ---------- helper ----------
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

# ---------- finder tiers ----------
def find_data_access_v1(text: str):
    """Tier 1 – any availability/permission keyword."""
    return _collect([AVAIL_RE], text)

def find_data_access_v2(text: str, window: int = 3):
    """Tier 2 – keyword within ±window tokens of “data/dataset”."""
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    data_idx = {i for i, t in enumerate(tokens) if DATA_TOKEN_RE.fullmatch(t)}
    out = []
    for m in AVAIL_RE.finditer(text):
        w_s, w_e = _char_to_word((m.start(), m.end()), spans)
        if any(d for d in data_idx if w_s - window <= d <= w_e + window):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_data_access_v3(text: str, block_chars: int = 300):
    """Tier 3 – inside Data access/availability heading blocks."""
    spans = _token_spans(text)
    blocks: List[Tuple[int, int]] = []
    for h in HEADING_ACC_RE.finditer(text):
        s = h.end()
        nxt = text.find("\n\n", s)
        e = nxt if 0 <= nxt - s <= block_chars else s + block_chars
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in AVAIL_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_data_access_v4(text: str, window: int = 5):
    """Tier 4 – v2 + permission/repository token near phrase."""
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    perm_idx = {i for i, t in enumerate(tokens) if PERMISSION_RE.fullmatch(t) or REPO_RE.fullmatch(t)}
    matches = find_data_access_v2(text, window=window)
    out = []
    for w_s, w_e, snip in matches:
        if any(p for p in perm_idx if w_s - window <= p <= w_e + window):
            out.append((w_s, w_e, snip))
    return out

def find_data_access_v5(text: str):
    """Tier 5 – tight template match."""
    return _collect([TIGHT_TEMPLATE_RE], text)

# ---------- exports ----------
DATA_ACCESS_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_data_access_v1,
    "v2": find_data_access_v2,
    "v3": find_data_access_v3,
    "v4": find_data_access_v4,
    "v5": find_data_access_v5,
}

__all__ = [
    "find_data_access_v1", "find_data_access_v2", "find_data_access_v3",
    "find_data_access_v4", "find_data_access_v5", "DATA_ACCESS_FINDERS",
]

find_data_access_high_recall = find_data_access_v1
find_data_access_high_precision = find_data_access_v5
