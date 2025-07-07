"""
settings_locations_finder.py – precision/recall ladder for *study settings / locations* 
(where the research was conducted, e.g., hospital, clinic, city, country).

Five variants (v1–v5):
    • v1 – high recall: any clause containing 'setting(s)' or 'conducted/performed/carried out' + location terms.
    • v2 – v1 **and** explicit facility or geographic term (hospital, clinic, university, school, community, country, city, region).
    • v3 – only inside a *Study Setting*, *Methods*, or *Participants* heading block (first ~400 characters).
    • v4 – v2 plus geopolitical or institutional entity (country names, cities, WHO regions, universities) in same sentence.
    • v5 – tight template: “The study was conducted at [facility] in [city], [country].”

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

# --- Regex patterns ---
SETTING_RE = re.compile(r"\bsettings?\b", re.I)
CONDUCT_RE = re.compile(r"\b(?:conducted|performed|carried\s+out|undertaken)\b", re.I)

FACILITY_RE = re.compile(
    r"\b(?:hospital(?:s)?|clinic(?:s)?|centre(?:s)?|center(?:s)?|university(?:ies)?|school(?:s)?|practice(?:s)?|"
    r"ward(?:s)?|laborator(?:y|ies)|community|communities)\b",
    re.I
)

GEO_RE = re.compile(
    r"\b(?:USA|United\s+States|UK|United\s+Kingdom|India|China|Canada|Australia|Europe|Asia|Africa|"
    r"France|Germany|Italy|Spain|Brazil|Mexico|Japan|Korea|Russia|Nigeria|South\s+Africa|"
    r"city|country|region)\b\.?",
    re.I
)

HEAD_SEC_RE = re.compile(r"(?i)(study\s+setting|methods?|participants?)\s*[:\-]?", re.M)

TIGHT_TEMPLATE_RE = re.compile(
    r"(?:the\s+study\s+was\s+(?:conducted|performed|carried\s+out)\s+at\s+.+?\s+(?:hospital|clinic|university|school)\s+in\s+[A-Z][a-z]+(?:,\s*[A-Z][a-z]+)*)",
    re.I
)

CUE_RE = re.compile(
    r"\b(?:conducted|performed|carried\s+out|undertaken|recruited|obtained|collected)\b",
    re.I
)

# --- Helper to collect matches ---
def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

# Variant 1 – High recall: mentions of "settings" or "conducted" phrases
def find_settings_location_v1(text: str):
    pattern = re.compile(
        r"(?:study\s+settings?|research\s+setting|study\s+was\s+(?:conducted|performed|carried\s+out|undertaken))",
        re.I
    )
    matches = _collect([pattern], text)
    filtered = []
    for w_s, w_e, snippet in matches:
        span_text = text.lower()
        start_char = snippet.lower()
        before = " ".join(text.split()[:w_s][-5:]).lower()
        if ("without reference to" in before or 
            before.endswith("no") or 
            before.endswith("without")):
            continue
        filtered.append((w_s, w_e, snippet))
    return filtered

# Variant 2 – Add facility term requirement
def find_settings_location_v2(text: str, window: int = 5):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    loc_idx = {i for i, t in enumerate(tokens) if CUE_RE.search(t)}
    fac_idx = {i for i, t in enumerate(tokens) if FACILITY_RE.search(t)}
    out = []
    for li in loc_idx:
        if any(abs(fi - li) <= window for fi in fac_idx):
            w_s = max(0, li - window)
            w_e = min(len(tokens)-1, li + window)
            snippet = " ".join(tokens[w_s:w_e+1])
            out.append((w_s, w_e, snippet))
    return out

# Variant 3 – Restrict to Study Setting/Methods/Participants blocks
def find_settings_location_v3(text: str, block_chars: int = 400):
    spans = _token_spans(text)
    blocks = []
    for h in HEAD_SEC_RE.finditer(text):
        s = h.end(); e = min(len(text), s + block_chars)
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in FACILITY_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

# Variant 4 – Facility + geopolitical/geographic terms
def find_settings_location_v4(text: str, window: int = 8):
    base_matches = find_settings_location_v2(text, window=window)
    if not base_matches:
        return []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    out = []
    for w_s, w_e, snip in base_matches:
        for sent in sentences:
            if snip in sent:
                if GEO_RE.search(sent):
                    out.append((w_s, w_e, snip))
                break
    return out

# Variant 5 – Tight template form
def find_settings_location_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

# --- Registry ---
SETTINGS_LOCATION_FINDERS: Dict[str, Callable[[str], List[Tuple[int,int,str]]]] = {
    "v1": find_settings_location_v1,
    "v2": find_settings_location_v2,
    "v3": find_settings_location_v3,
    "v4": find_settings_location_v4,
    "v5": find_settings_location_v5,
}

__all__ = [
    "find_settings_location_v1",
    "find_settings_location_v2",
    "find_settings_location_v3",
    "find_settings_location_v4",
    "find_settings_location_v5",
    "SETTINGS_LOCATION_FINDERS",
]

find_settings_location_high_recall = find_settings_location_v1
find_settings_location_high_precision = find_settings_location_v5
