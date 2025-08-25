"""healthcare_setting_finder.py – precision/recall ladder for *health‑care setting* statements.
Five variants (v1–v5):
    • v1 – high recall: any facility/setting term (inpatient, outpatient, ICU, etc.).
    • v2 – facility term within ±3 tokens of a context word (setting, clinic, care, unit, hospital).
    • v3 – only inside a *Setting / Healthcare setting* heading block.
    • v4 – v2 plus qualifier tokens (primary, secondary, tertiary, academic, community) to filter generic mentions.
    • v5 – tight template: “Conducted in five primary‑care clinics”, “Data from an ICU inpatient setting”, etc.
Each function returns tuples: (start_token_idx, end_token_idx, snippet).
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable


import unicodedata

def normalize_text(text: str) -> str:
    """Normalize the text and replace non-breaking hyphens with regular hyphens."""
    # Normalize the text to NFC form, which handles non-breaking hyphens
    text = unicodedata.normalize("NFC", text)
    return text.replace("\u2011", "-")  # Replace non-breaking hyphen with regular hyphen



# ─────────────────────────────
# 0. Utilities
# ─────────────────────────────
TOKEN_RE = re.compile(r"\S+")

def _token_spans(text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_to_word(span: Tuple[int, int], tokens: Sequence[Tuple[int, int]]):
    s, e = span
    w_s = next(i for i, (a, b) in enumerate(tokens) if a <= s < b)
    w_e = next(i for i, (a, b) in reversed(list(enumerate(tokens))) if a < e <= b)
    return w_s, w_e

# ─────────────────────────────
# 1. Regex assets
# ─────────────────────────────
FACILITY_RE = re.compile(r"\b(hospitals?|medical centers?|healthcare centers?|(?:outpatient|primary care|community|specialty)\s+clinics?|ICU(?:s| wards?)?|intensive care units?|ICU wards?|wards?|pharmacies|pharmacy|community pharmacy|inpatients?|outpatients?)\b", re.I)

CONTEXT_RE = re.compile(r"^(?:setting|settings|clinic|care|unit|environment|data|patients?|ward|healthcare|facility|medical|hospitalization|treatment|caregiver)[\.,;:]?$", re.I)

QUALIFIER_RE = re.compile(r"\b(?:primary|secondary|tertiary|academic|community|teaching|urban|rural|outpatient|ambulatory|regional|suburban|specialist|private|public)\b", re.I)

HEADING_SET_RE = re.compile(r"(?m)^(?:setting|healthcare\s+setting|study\s+setting|study\s+design|research\s+setting|care\s+setting|clinical\s+setting|service\s+setting)\s*[:\-]?\s*.*$", re.I)

GENERIC_TRAP_RE = re.compile(r"real[- ]?world\s+setting|setting\s+of\s+care", re.I)

TIGHT_TEMPLATE_RE = re.compile(r"(?:(?:conducted|performed|carried\s+out)\s+in|data\s+from)\s+[^.\n]{0,80}?(?:inpatient\s+setting|outpatient\s+setting|primary[-\s]+care\s+clinics?|icu(?:\s+inpatient\s+setting)?|hospital(?:\s+ward)?)\b", re.I)

# ─────────────────────────────
# 2. Helper
# ─────────────────────────────

def _collect(patterns: Sequence[re.Pattern[str]], text: str) -> List[Tuple[int, int, str]]:
    tok_spans = _token_spans(text)
    out = []
    for patt in patterns:
        for m in patt.finditer(text):
            if GENERIC_TRAP_RE.search(m.group(0)):
                continue
            w_s, w_e = _char_to_word((m.start(), m.end()), tok_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

# ─────────────────────────────
# 3. Finder tiers
# ─────────────────────────────

def find_healthcare_setting_v1(text: str):
    """Tier 1 – any facility term."""
    text = normalize_text(text)  # Normalize the text first
    return _collect([FACILITY_RE], text)

def find_healthcare_setting_v2(text: str, window: int = 3):
    """Tier 2 – facility term + context word within ±window tokens."""
    text = normalize_text(text)  # Normalize the text first
    tok_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in tok_spans]
    ctx_idx = {i for i, t in enumerate(tokens) if CONTEXT_RE.fullmatch(t)}
    out = []
    for m in FACILITY_RE.finditer(text):
        w_s, w_e = _char_to_word((m.start(), m.end()), tok_spans)
        if any(c for c in ctx_idx if w_s - window <= c <= w_e + window):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_healthcare_setting_v3(text: str):
    text_norm = normalize_text(text)
    print("Normalized text:", text_norm)
    blocks = []
    for match in re.finditer(r"(healthcare setting|study setting)\s*:\s*(.*?)(?:\n\s*\n|$)", text_norm, re.I | re.S):
        blocks.append((match.start(), match.end()))
    print("Found blocks:", blocks)
    matches = []
    for start, end in blocks:
        block_text = text_norm[start:end]
        for fac in FACILITY_RE.finditer(block_text):
            matches.append(fac)
    return matches

def find_healthcare_setting_v4(text: str, window: int = 4):
    """Tier 4 – v2 + qualifier token near facility term."""
    text = normalize_text(text)  # Normalize the text first
    tok_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in tok_spans]
    # Create a set of indices for tokens that are qualifiers
    qual_idx = {i for i, t in enumerate(tokens) if QUALIFIER_RE.fullmatch(t)}
    # Get matches from v2 (facility term + context)
    matches = find_healthcare_setting_v2(text, window=window)
    out = []
    for w_s, w_e, snip in matches:
        if any(q for q in qual_idx if w_s - window <= q <= w_e + window):
            out.append((w_s, w_e, snip))
    return out

def find_healthcare_setting_v5(text: str):
    """Tier 5 – tight template."""
    text = normalize_text(text)  # Normalize the text first
    return _collect([TIGHT_TEMPLATE_RE], text)


# ─────────────────────────────
# 4. Mapping & exports
# ─────────────────────────────
HEALTHCARE_SETTING_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_healthcare_setting_v1,
    "v2": find_healthcare_setting_v2,
    "v3": find_healthcare_setting_v3,
    "v4": find_healthcare_setting_v4,
    "v5": find_healthcare_setting_v5,
}

__all__ = [
    "find_healthcare_setting_v1", "find_healthcare_setting_v2", "find_healthcare_setting_v3",
    "find_healthcare_setting_v4", "find_healthcare_setting_v5", "HEALTHCARE_SETTING_FINDERS",
]

find_healthcare_setting_high_recall = find_healthcare_setting_v1
find_healthcare_setting_high_precision = find_healthcare_setting_v5
