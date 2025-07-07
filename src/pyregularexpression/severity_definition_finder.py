"""severity_definition_finder.py – precision/recall ladder for *severity definition* statements.
Five variants (v1–v5):
    • v1 – high recall: any severity cue (mild/moderate/severe/severity)
    • v2 – cue + defining verb (defined/classified/categorised) within ±window tokens
    • v3 – only inside a *Severity definition / Classification* heading block
    • v4 – v2 plus explicit multi-level listing (mild+moderate+severe) or comparison/threshold token (≥, IV antibiotics, admission)
    • v5 – tight template: “Severity was defined by …”, “Disease classified as mild/moderate/severe based on …”, etc.
Each function returns a list of tuples: (start_token_idx, end_token_idx, matched_snippet)
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

SEVERITY_TERM_RE = re.compile(r"\b(?:severity|mild|moderate|severe)\b(?!\s+weather\b)", re.I)
DEFINE_VERB_RE = re.compile(r"\b(?:defined|classified|categoris(?:ed|ed)|graded|stratified|assessed)\b", re.I)
LISTING_PATTERN_RE = re.compile(r"mild\s*(?:[\/,]| and )\s*moderate\s*(?:[\/,]| and )\s*severe(?:\s+[a-zA-Z ]+)?", re.I)
THRESHOLD_TOKEN_RE = re.compile(r"\b(?:>=|<=|>|<|iv\s+antibiotics|admission|hospitalisation|oxygen|\d+\s*points?)\b", re.I)
HEADING_SEVERITY_RE = re.compile(r"(?m)^(?:severity|classification)\s*(?:definition|grading|was recorded)?\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\b(?:severe|moderate|mild)\b(?![^\.]{0,40}(?:defined|classified))", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"(?:severity\s+(?:was\s+)?defined\s+(?:by|as)\s+[^\.\n]{0,100})|(?:classified\s+as\s+mild[\/ ,]+moderate[\/ ,]+severe(?:\s+based\s+on[^\.\n]{0,100})?)",re.I)

def _collect(patterns: Sequence[re.Pattern[str]], text: str) -> List[Tuple[int, int, str]]:
    token_spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_severity_definition_v1(text: str): return _collect([SEVERITY_TERM_RE], text)

def find_severity_definition_v2(text: str, window: int = 5):
    token_spans=_token_spans(text); tokens=[text[s:e] for s,e in token_spans]
    verb_idx={i for i,t in enumerate(tokens) if DEFINE_VERB_RE.fullmatch(t)}
    out=[]
    for m in SEVERITY_TERM_RE.finditer(text):
        w_s,w_e=_char_span_to_word_span((m.start(),m.end()),token_spans)
        if any(v for v in verb_idx if w_s-window<=v<=w_e+window): out.append((w_s,w_e,m.group(0)))
    return out

def find_severity_definition_v3(text: str, block_chars: int = 400):
    token_spans = _token_spans(text)
    blocks = []
    for h in HEADING_SEVERITY_RE.finditer(text):
        s = h.end()
        nb = text.find("\n\n", s)
        e = nb if nb != -1 else len(text)
        e = min(s + block_chars, e)
        blocks.append((s, e)) 
    inside = lambda p: any(s <= p < e for s, e in blocks)
    return [
        _char_span_to_word_span((m.start(), m.end()), token_spans) + (m.group(0),)
        for m in SEVERITY_TERM_RE.finditer(text)
        if inside(m.start())
    ]

def find_severity_definition_v4(text: str, window: int = 6):
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    out = []
    for m in LISTING_PATTERN_RE.finditer(text):
        try:
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
        except StopIteration:
            continue
    thresh = {i for i, t in enumerate(tokens) if THRESHOLD_TOKEN_RE.fullmatch(t)}
    matches = find_severity_definition_v2(text, window)
    for w_s, w_e, snip in matches:
        if any(i for i in thresh if w_s - window <= i <= w_e + window):
            out.append((w_s, w_e, snip))
    return out

def find_severity_definition_v5(text:str): return _collect([TIGHT_TEMPLATE_RE], text)

SEVERITY_DEFINITION_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]]={"v1":find_severity_definition_v1,"v2":find_severity_definition_v2,"v3":find_severity_definition_v3,"v4":find_severity_definition_v4,"v5":find_severity_definition_v5}
__all__=["find_severity_definition_v1","find_severity_definition_v2","find_severity_definition_v3","find_severity_definition_v4","find_severity_definition_v5","SEVERITY_DEFINITION_FINDERS"]
find_severity_definition_high_recall=find_severity_definition_v1
find_severity_definition_high_precision=find_severity_definition_v5
