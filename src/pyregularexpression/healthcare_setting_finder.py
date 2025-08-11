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
FACILITY_RE = re.compile(
    r"\b(?:inpatient|outpatient|ambulatory|primary\s+care|secondary\s+care|tertiary\s+care|emergency\s+department|ed|er|icu|intensive\s+care(?:\s+unit)?|clinic|clinics|hospitals?(?:\s+based)?|ward|community\s+pharmacy|settings)\b",  # Corrected backslashes
    re.I,
)

# CONTEXT_RE = re.compile(r"\b(?:setting|clinic|care|unit|hospital|environment|data|patients?)\b", re.I)
# CONTEXT_RE = re.compile(r"\b(?:setting|clinic|care|unit|hospital|environment|data|patients?|ward|healthcare|inpatient|outpatient|facility|medical|hospitalization|treatment)\b", re.I)
CONTEXT_RE = re.compile(r"\b(?:setting|settings|clinic|care|unit|hospital|environment|data|patients?|ward|healthcare|inpatient|outpatient|facility|medical|hospitalization|treatment|caregiver|medical\scare)\b", re.I)


#QUALIFIER_RE = re.compile(r"\b(?:primary|secondary|tertiary|academic|community|teaching|urban|rural)\b", re.I)
QUALIFIER_RE = re.compile(r"\b(?:primary|secondary|tertiary|academic|community|teaching|urban|rural|outpatient|ambulatory|regional|suburban|specialist|private|public|emergency)\b", re.I)

#HEADING_SET_RE = re.compile(r"(?m)^(?:setting|healthcare\s+setting|study\s+setting)\s*[:\-]?\s*$", re.I)
#HEADING_SET_RE = re.compile(r"(?m)^(?:setting|healthcare\s+setting|study\s+setting|study\s+design|research\s+setting|care\s+setting|clinical\s+setting|service\s+setting)\s*[:\-]?\s*$", re.I)
HEADING_SET_RE = re.compile(
    r"(?m)^(?:setting|healthcare\s+setting|study\s+setting|study\s+design|research\s+setting|care\s+setting|clinical\s+setting|service\s+setting)\s*[:\-\.]?\s*",
    re.I
)


GENERIC_TRAP_RE = re.compile(r"real[- ]?world\s+setting|setting\s+of\s+care", re.I)

TIGHT_TEMPLATE_RE = re.compile(
    r"(?:(?:conducted|performed|carried\s+out)\s+in|admitted\s+to|data\s+(?:were\s+extracted\s+)?from|recruited\s+(?:from|in|at))\s+[^\.\\n]{0,80}(?:inpatient|outpatient|primary\s+care|icu|clinic|hospital|emergency\s+department)\b",
    re.I,
)

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
    ctx_idx = {i for i, t in enumerate(tokens) if CONTEXT_RE.search(t)}
    out = []
    for m in FACILITY_RE.finditer(text):
        w_s, w_e = _char_to_word((m.start(), m.end()), tok_spans)
        if any(c for c in ctx_idx if w_s - window <= c <= w_e + window):
            out.append((w_s, w_e, m.group(0)))
    return out


def find_healthcare_setting_v3(text: str, block_chars: int = 250):
    text = normalize_text(text)  # Normalize the text first
    tok_spans = _token_spans(text)
    blocks = []
    for h in HEADING_SET_RE.finditer(text):
        s = h.end()
        nxt = text.find("\n\n", s)
        e = nxt if 0 <= nxt - s <= block_chars else s + block_chars
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in FACILITY_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_to_word((m.start(), m.end()), tok_spans)
            out.append((w_s, w_e, m.group(0)))
    return out



def find_healthcare_setting_v4(text: str, window: int = 4):
    """Tier 4 – v2 + qualifier token near facility term."""
    text = normalize_text(text)  # Normalize the text first
    tok_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in tok_spans]
    
    # Create a set of indices for tokens that are qualifiers
    qual_idx = {i for i, t in enumerate(tokens) if QUALIFIER_RE.search(t)}
    
    # Get matches from v2 (facility term + context)
    matches = find_healthcare_setting_v2(text, window=window)
    
    # Store results
    out = []
    
    # Loop over the matches from v2
    for w_s, w_e, snip in matches:
        # Check if any of the qualifiers are within the window before or after the matched span
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
