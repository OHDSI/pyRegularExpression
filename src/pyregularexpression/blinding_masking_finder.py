"""blinding_masking_finder.py – precision/recall ladder for *blinding / masking* status.
Five variants (v1–v5):
    • v1 – high recall: any blinding cue (double‑blind, single‑blind, masked,
           open‑label, unblinded, assessor‑blinded).
    • v2 – blinding cue + role keyword (participants, investigators, assessors,
           clinicians, data collectors) within ±4 tokens.
    • v3 – only inside a *Blinding / Masking* heading block (first ~400 characters).
    • v4 – v2 plus evidence of at least two distinct roles or explicit phrase
           double/triple/quadruple‑blind in same sentence.
    • v5 – tight template: “Double‑blind study: participants and assessors were
           unaware of assignments.”
Each finder returns tuples: (start_word_idx, end_word_idx, snippet).
"""
from __future__ import annotations

import re
from collections.abc import Callable, Sequence

TOKEN_RE = re.compile(r"\S+")


def _token_spans(text: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]


def _char_to_word(span: tuple[int, int], spans: Sequence[tuple[int, int]]):
    s, e = span
    w_s = next(i for i, (a, b) in enumerate(spans) if a <= s < b)
    w_e = next(i for i, (a, b) in reversed(list(enumerate(spans))) if a < e <= b)
    return w_s, w_e


# Regex assets
BLIND_CUE_RE = re.compile(
    r"\b(?:double|single|triple|quadruple)\s*-?\s*blind\b|blinded?\b|unblinded\b"
    r"|masked\b|blinding\b|open[- ]label\b",
    re.I,
)
ROLE_RE = re.compile(
    r"\b(?:participants?|patients?|subjects?|investigators?|clinicians?|physicians?"
    r"|assessors?|outcome\s+assessors?|data\s+collectors?|care\s+providers?)\b",
    re.I,
)
HEADING_BLIND_RE = re.compile(r"(?m)^(?:blinding|masking)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\bblinded\s+review|blind\s+analysis|blind\s+assessment\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(
    r"double[- ]blind\s+study[:\-]?\s+participants?\s+and\s+assessors?\s+"
    r"(?:were|remained)\s+(?:unaware|masked)\b",
    re.I,
)
LEVEL_RE = re.compile(r"\b(?:double|triple|quadruple)\s*-?\s*blind\b", re.I)


def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans = _token_spans(text)
    out: list[tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0, m.start() - 25) : m.end() + 25]):
                continue
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out


def find_blinding_masking_v1(text: str):
    return _collect([BLIND_CUE_RE], text)


def find_blinding_masking_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    role_idx = {i for i, t in enumerate(tokens) if ROLE_RE.search(t)}
    cue_idx = {i for i, t in enumerate(tokens) if BLIND_CUE_RE.search(t)}
    out = []
    for c in cue_idx:
        if any(r for r in role_idx if abs(r - c) <= window):
            w_s, w_e = _char_to_word(spans[c], spans)
            out.append((w_s, w_e, tokens[c]))
    return out


def find_blinding_masking_v3(text: str, block_chars: int = 400):
    spans = _token_spans(text)
    blocks = []
    for h in HEADING_BLIND_RE.finditer(text):
        s = h.end()
        e = min(len(text), s + block_chars)
        blocks.append((s, e))

    def inside(p):
        return any(s <= p < e for s, e in blocks)

    out = []
    for m in BLIND_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out


def find_blinding_masking_v4(text: str, window: int = 6):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    matches = find_blinding_masking_v2(text, window=window)
    out = []
    for w_s, w_e, snip in matches:
        start_idx = max(0, w_s - window)
        end_idx = min(len(tokens), w_e + window)
        roles = {
            tokens[i].lower()
            for i in range(start_idx, end_idx)
            if ROLE_RE.search(tokens[i])
        }
        level_present = any(
            LEVEL_RE.search(tokens[i]) for i in range(start_idx, end_idx)
        )
        if len(roles) >= 2 or level_present:
            out.append((w_s, w_e, snip))
    return out


def find_blinding_masking_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)


BLINDING_MASKING_FINDERS: dict[str, Callable[[str], list[tuple[int, int, str]]]] = {
    "v1": find_blinding_masking_v1,
    "v2": find_blinding_masking_v2,
    "v3": find_blinding_masking_v3,
    "v4": find_blinding_masking_v4,
    "v5": find_blinding_masking_v5,
}

__all__ = [
    "find_blinding_masking_v1",
    "find_blinding_masking_v2",
    "find_blinding_masking_v3",
    "find_blinding_masking_v4",
    "find_blinding_masking_v5",
    "BLINDING_MASKING_FINDERS",
]

find_blinding_masking_high_recall = find_blinding_masking_v1
find_blinding_masking_high_precision = find_blinding_masking_v5
