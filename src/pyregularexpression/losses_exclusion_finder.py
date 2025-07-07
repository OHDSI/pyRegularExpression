"""losses_exclusion_finder.py – precision/recall ladder for *losses and exclusions after allocation*.
Five variants (v1–v5):
    • v1 – high recall: any dropout/loss cue (lost to follow-up, withdrew consent, dropped out, excluded from analysis) plus a number.
    • v2 – v1 **and** follow‑up/analysis stage keyword within ±4 tokens.
    • v3 – only inside a *Participant Flow / Losses* heading block (first ~500 characters).
    • v4 – v2 plus explicit reason phrase (due to, because of, adverse event, side effects) in same sentence.
    • v5 – tight template: “5 lost to follow-up, 2 withdrew due to side effects.”
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
    w_s = next(i for i,(a,b) in enumerate(spans) if a<=s<b)
    w_e = next(i for i,(a,b) in reversed(list(enumerate(spans))) if a<e<=b)
    return w_s,w_e

NUM_RE = r"\d{1,4}"
NUM_TOKEN_RE = re.compile(r"^\d{1,4}$")
LOSS_CUE_RE = re.compile(r"\b(?:lost\s+to\s+follow[- ]up|withdrew|withdrawn|dropped?\s+out|drop[- ]outs?|excluded\s+from\s+analysis|missing\s+data)\b", re.I)
STAGE_RE = re.compile(r"\b(?:follow[- ]up|analysis|study\s+period|treatment|intervention)\b", re.I)
REASON_RE = re.compile(r"\b(?:due\s+to|because\s+of|adverse\s+event|side\s+effects?|pregnancy)\b", re.I)
HEAD_LOSS_RE = re.compile(r"(?m)^(?:losses?\s+and\s+exclusions?|drop[- ]?outs?|participant\s+flow)\s*[:\-]?.*$", re.I)
TIGHT_TEMPLATE_RE = re.compile(rf"{NUM_RE}\s+lost\s+to\s+follow[- ]up,?\s+{NUM_RE}\s+withdrew\s+(?:due\s+to|because\s+of)\s+[^\.\n]+", re.I)
TRAP_RE = re.compile(r"\bexcluded\s+during\s+screening|lost\s+samples?|specimens\b", re.I)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans=_token_spans(text)
    out: List[Tuple[int,int,str]]=[]
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0,m.start()-25):m.end()+25]):
                continue
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_losses_exclusion_v1(text: str):
    pattern = re.compile(rf"{NUM_RE}[^\n]{{0,15}}{LOSS_CUE_RE.pattern}", re.I)
    return _collect([pattern], text)

def find_losses_exclusion_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    tokens = [text[s:e] for s,e in spans]
    out = []
    for m in LOSS_CUE_RE.finditer(text):
        cue_start, cue_end = m.start(), m.end()
        w_s_cue, w_e_cue = _char_to_word((cue_start, cue_end), spans)
        start_idx = max(0, w_s_cue - window)
        end_idx = min(len(tokens), w_e_cue + window + 1)
        snippet = " ".join(tokens[start_idx:end_idx])
        if re.search(NUM_RE, snippet) and STAGE_RE.search(snippet):
            out.append((start_idx, end_idx-1, snippet))
    return out

def find_losses_exclusion_v3(text: str, block_chars: int = 500):
    spans = _token_spans(text)
    blocks = []
    for h in HEAD_LOSS_RE.finditer(text):
        s = h.start()  # include heading itself
        e = min(len(text), s + block_chars)
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in LOSS_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_losses_exclusion_v4(text: str, window: int = 6):
    spans = _token_spans(text)
    tokens = [text[s:e] for s,e in spans]
    out = []
    for m in LOSS_CUE_RE.finditer(text):
        cue_start, cue_end = m.start(), m.end()
        w_s_cue, w_e_cue = _char_to_word((cue_start, cue_end), spans)
        start_idx = max(0, w_s_cue - window)
        end_idx = min(len(tokens), w_e_cue + window + 1)
        snippet = " ".join(tokens[start_idx:end_idx])
        if re.search(NUM_RE, snippet) and REASON_RE.search(snippet):
            out.append((start_idx, end_idx-1, snippet))
    return out

def find_losses_exclusion_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

LOSSES_EXCLUSION_FINDERS: Dict[str, Callable[[str], List[Tuple[int,int,str]]]] = {
    "v1": find_losses_exclusion_v1,
    "v2": find_losses_exclusion_v2,
    "v3": find_losses_exclusion_v3,
    "v4": find_losses_exclusion_v4,
    "v5": find_losses_exclusion_v5,
}

__all__ = ["find_losses_exclusion_v1","find_losses_exclusion_v2","find_losses_exclusion_v3","find_losses_exclusion_v4","find_losses_exclusion_v5","LOSSES_EXCLUSION_FINDERS"]

find_losses_exclusion_high_recall = find_losses_exclusion_v1
find_losses_exclusion_high_precision = find_losses_exclusion_v5
