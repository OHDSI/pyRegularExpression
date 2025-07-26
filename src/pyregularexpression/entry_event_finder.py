"""entry_event_finder.py – precision/recall ladder for *entry‑event* statements.
Five variants (v1–v5):
    • v1 – high recall (any entry‑event cue)
    • v2 – cue + inclusion verb within context window
    • v3 – only inside Cohort‑entry/Qualifying‑event‑style blocks
    • v4 – v2 plus *first/initial* qualifier and trap guards
    • v5 – tight template ("Entry event was first …")
Returns list of tuples (start_token_idx, end_token_idx, snippet)
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

TOKEN_RE = re.compile(r"\S+")

def _token_spans(text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_span_to_word_span(char_span: Tuple[int, int], token_spans: Sequence[Tuple[int, int]]) -> Tuple[int, int]:
    s_char, e_char = char_span
    w_start = next(i for i, (s, e) in enumerate(token_spans) if s <= s_char < e)
    w_end = next(i for i, (s, e) in reversed(list(enumerate(token_spans))) if s < e_char <= e)
    return w_start, w_end

# Regex assets -------------------------------------------------------------
ENTRY_EVENT_TERM_RE = re.compile(
    r"(?:\bfirst\b|\binitial\b|\bindex\b|\bqualifying\b|\bcohort\s+entry\b|\bentry\s+event\b|\beligible\s+upon\b|\bincluded\s+upon\b|\bincluded\s+after\b|\bhospitali[sz]ation\b|\bhospitali[sz]ed\b|\badmission\b|\bdiagnosis\b|\bencounter\b|\bvisit\b|\bmyocardial\s+infarctions?\b)",
    re.I,
)

INCLUSION_VERB_RE = re.compile(
    r"\b("
    r"eligible\s+(?:upon|after|if)|"
    r"included\s+(?:upon|after|if|based\s+on)|"
    r"selection\s+was\s+based\s+on|"
    r"entry\s+based\s+on|"
    r"qualified|"
    r"must\s+have|"
    r"enrolled\s+(?:upon|after|if)|"
    r"cohort\s+entry\s+defined\s+by|"
    r"entered\s+the\s+cohort|"
    r"qualifying\s+event"
    r")\b", re.I
)


FIRST_INITIAL_RE = re.compile(
    r"\b(?:first|initial)\s+(?:hospitali[sz]ation|admission|diagnos(?:is|es)|visit|index\s+event)\b",
    re.I
)

HEADING_ENTRY_RE = re.compile(r"\b(cohort\s+entry|entry\s+event|qualifying\s+event|index\s+event)\b\s*[:\-]?", re.I)

TRAP_RE = re.compile(
    r"(?:data\s+entry"
    r"|entered\s+data"
    r"|used\s+only\s+for\s+follow[- ]?up"
    r"|follow[- ]?up\s+confirmation"
    r"|post[- ]?discharge"
    r"|monitoring"
    r"|screening"
    r")",
    re.I
)

# Helper -------------------------------------------------------------------
def _collect(patterns: Sequence[re.Pattern[str]], text: str) -> List[Tuple[int, int, str]]:
    token_spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(m.group(0)):
                continue
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

# Finder variants ----------------------------------------------------------
def find_entry_event_v1(text: str):
    token_spans = _token_spans(text)
    out = []
    for m in ENTRY_EVENT_TERM_RE.finditer(text):
        context = text[max(0, m.start() - 50):m.end() + 50]
        if TRAP_RE.search(context):
            continue
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        out.append((w_s, w_e, m.group(0)))
    return out

def find_entry_event_v2(text: str, window: int = 6):
    token_spans = _token_spans(text)
    inc_matches = [
        _char_span_to_word_span((m.start(), m.end()), token_spans)
        for m in INCLUSION_VERB_RE.finditer(text)
    ]
    out = []
    for m in ENTRY_EVENT_TERM_RE.finditer(text):
        context = text[max(0, m.start() - 50):m.end() + 50]
        if TRAP_RE.search(context):
            continue
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        if any(inc_w_s - window <= w_s <= inc_w_e + window or
               inc_w_s - window <= w_e <= inc_w_e + window
               for inc_w_s, inc_w_e in inc_matches):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_entry_event_v3(text: str):
    token_spans = _token_spans(text)
    blocks = []

    # 1. Inline headings with content on the same line
    INLINE_HEADING_RE = re.compile(
        r"(?i)\b(cohort\s+entry|entry\s+event|qualifying\s+event|index\s+event)\b[ \t]*[:\-\u2013][ \t]*(\S.+)"
    )
    for m in INLINE_HEADING_RE.finditer(text):
    # Cover full line
        line_start = text.rfind('\n', 0, m.start(2)) + 1
        line_end = text.find('\n', m.start(2))
        if line_end == -1:
            line_end = len(text)
        blocks.append((line_start, line_end))

    # 2. Block headings with content below (allow 0 or 1 blank lines)
    BLOCK_HEADING_RE = re.compile(
##        r"(?im)^(cohort\s+entry|entry\s+event|qualifying\s+event|index\s+event)\s*[:\-]?\s*$"
        r"(?im)^(cohort\s+entry|entry\s+event|qualifying\s+event|index\s+event)\s*[:\-\u2013]?\s*$"
    )
    for h in BLOCK_HEADING_RE.finditer(text):
        heading_end = h.end()
        after = text[heading_end:]
        if after.startswith("\n\n\n"):
            continue
        match = re.match(r"([\s\n]*)(\S.*)", after, re.DOTALL)
        if not match:
            continue
        gap, content = match.groups()
        if gap.count("\n") > 1:
            continue
    
        content_line = content.split("\n", 1)[0]
        start = heading_end + len(gap)
        end = start + len(content_line)
        blocks.append((start, end))

    def _inside(p):
        return any(start <= p < end for start, end in blocks)

    return [
        (*_char_span_to_word_span((m.start(), m.end()), token_spans), m.group())
        for m in ENTRY_EVENT_TERM_RE.finditer(text)
        if _inside(m.start()) and not TRAP_RE.search(text[max(0, m.start() - 50):m.end() + 50])
    ]


def find_entry_event_v4(text: str, window: int = 6):
    matches = find_entry_event_v2(text, window)
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    qual_idx = {i for i, t in enumerate(tokens) if FIRST_INITIAL_RE.fullmatch(t)}
    return [
        (w_s, w_e, snip)
        for w_s, w_e, snip in matches
        if any(q for q in qual_idx if w_s - window <= q <= w_e + window)
    ]

def find_entry_event_v5(text: str):
    TEMPLATE_RE = re.compile(
        r"entry\s+event\s+was\s+(?:the\s+)?first\s+[A-Za-z\s]+?\b(?:diagnosis|hospitali[sz]ation|admission|event)\b",
        re.I,
    )
    return _collect([TEMPLATE_RE], text)

# Mapping ------------------------------------------------------------------
ENTRY_EVENT_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_entry_event_v1,
    "v2": find_entry_event_v2,
    "v3": find_entry_event_v3,
    "v4": find_entry_event_v4,
    "v5": find_entry_event_v5,
}

__all__ = [
    "find_entry_event_v1", "find_entry_event_v2", "find_entry_event_v3", "find_entry_event_v4", "find_entry_event_v5", "ENTRY_EVENT_FINDERS",
]
