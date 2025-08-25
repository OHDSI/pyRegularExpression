
"""ethics_approval_finder.py – precision/recall ladder for *ethics approval & consent* statements.
Five variants (v1–v5):
    • v1 – high recall: any IRB/ethics/consent keyword (IRB, ethics committee, informed consent).
    • v2 – approval verb (approved, reviewed, waived) within ±4 tokens of an IRB/ethics keyword.
    • v3 – only inside an *Ethics approval / Ethical considerations* heading block.
    • v4 – v2 plus explicit consent phrase or IRB protocol number pattern to avoid generic ethics principles.
    • v5 – tight template: “Protocol approved by XYZ IRB #2021‑45; informed consent obtained.”
Each finder returns (start_word_idx, end_word_idx, snippet) tuples.
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

# ─────────────────────────────
# Utilities
# ─────────────────────────────
TOKEN_RE = re.compile(r"\S+")

def _token_spans(text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_to_word(span: Tuple[int, int], spans: Sequence[Tuple[int, int]]):
    s, e = span
    w_s = next(i for i, (a, b) in enumerate(spans) if a <= s < b)
    w_e = next(i for i, (a, b) in reversed(list(enumerate(spans))) if a < e <= b)
    return w_s, w_e

# ─────────────────────────────
# Regex assets
# ─────────────────────────────
IRB_RE = re.compile(r"\b(?:irb|institutional\s+review\s+board|research\s+ethics\s+board|reb|ethics\s+committee|ethics\s+review\s+board)\b", re.I)
APPROVAL_VERB_RE = re.compile(r"\b(?:approved|reviewed|waived|granted|obtained|cleared)\b", re.I)
CONSENT_RE = re.compile(r"\b(?:informed\s+consent|written\s+consent|verbal\s+consent|parental\s+consent)\b", re.I)
IRB_NUM_RE = re.compile(r"\b(?:protocol|project)?\s?#?\d{2,4}[-_]?[A-Za-z]?\d{0,3}\b")
HEADING_ETHICS_RE = re.compile(r"(?m)^(?:ethics(?:\s+approval)?|ethical\s+considerations|ethics\s+statement|informed\s+consent)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\bethical\s+principles|ethical\s+guidelines|ethically\s+conducted\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(
    r"protocol\s+(?:was\s+)?approved\s+by\s+[^\.\n]{0,60}(?:irb|ethics\s+committee)[^\.\n]{0,80}(?:informed\s+consent\s+(?:was\s+)?(?:obtained|waived))",
    re.I,
)

# ─────────────────────────────
# Helper
# ─────────────────────────────
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

# ─────────────────────────────
# Finder tiers
# ─────────────────────────────
def find_ethics_approval_v1(text: str):
    """Tier 1 – any IRB/ethics/consent keyword."""
    return _collect([IRB_RE, CONSENT_RE], text)

def find_ethics_approval_v2(text: str, window: int = 4):
    """Tier 2 – approval verb near IRB/ethics keyword."""
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    verb_idx = {i for i, t in enumerate(tokens) if APPROVAL_VERB_RE.fullmatch(t)}
    out = []
    for m in IRB_RE.finditer(text):
        w_s, w_e = _char_to_word((m.start(), m.end()), spans)
        if any(v for v in verb_idx if w_s - window <= v <= w_e + window):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_ethics_approval_v3(text: str, block_chars: int = 250):
    """Tier 3 – inside ethics heading blocks."""
    spans = _token_spans(text)
    blocks = []
    for h in HEADING_ETHICS_RE.finditer(text):
        s = h.end()
        nxt = text.find("\n\n", s)
        e = nxt if 0 <= nxt - s <= block_chars else s + block_chars
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in IRB_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_ethics_approval_v4(text: str, window: int = 6):
    """Tier 4 – v2 + consent phrase or protocol number nearby."""
    spans = _token_spans(text)
    matches = find_ethics_approval_v2(text, window=window)
    consent_hits = []
    for patt in (CONSENT_RE, IRB_NUM_RE):
        for m in patt.finditer(text):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            consent_hits.append((w_s, w_e))
    out = []
    for w_s, w_e, snip in matches:
        if any(c_s - window <= w_s <= c_e + window or w_s - window <= c_s <= w_e + window
               for c_s, c_e in consent_hits):
            out.append((w_s, w_e, snip))
    return out

def find_ethics_approval_v5(text: str):
    """Tier 5 – tight template."""
    return _collect([TIGHT_TEMPLATE_RE], text)

# ─────────────────────────────
# Mapping & exports
# ─────────────────────────────
ETHICS_APPROVAL_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_ethics_approval_v1,
    "v2": find_ethics_approval_v2,
    "v3": find_ethics_approval_v3,
    "v4": find_ethics_approval_v4,
    "v5": find_ethics_approval_v5,
}

__all__ = [
    "find_ethics_approval_v1", "find_ethics_approval_v2", "find_ethics_approval_v3",
    "find_ethics_approval_v4", "find_ethics_approval_v5", "ETHICS_APPROVAL_FINDERS",
]

find_ethics_approval_high_recall = find_ethics_approval_v1
find_ethics_approval_high_precision = find_ethics_approval_v5
