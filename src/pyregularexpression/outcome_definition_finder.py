
"""outcome_definition_finder.py – precision/recall ladder for *outcome definition* statements.

Five variants (v1–v5):

    • v1 – high recall: any outcome/endpoint cue
    • v2 – cue + defining verb within ±window tokens (defined/was/considered)
    • v3 – only inside an *Outcome definition / Endpoint* heading block
    • v4 – v2 plus explicit criterion token (within X days, composite of, readmission, etc.), excludes vague listings
    • v5 – tight template: “Primary outcome: readmission within 30 days”, “Outcome was defined as death from any cause”, etc.

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
    w_start = next((i for i, (s, e) in enumerate(token_spans) if e > s_char), 0)
    w_end   = next((i for i, (s, e) in reversed(list(enumerate(token_spans))) if s < e_char), len(token_spans)-1)
    return w_start, w_end

OUTCOME_CUE_RE = re.compile(r"\b(?:outcomes?|endpoints?)\b", re.I)
DEFINE_VERB_RE = re.compile(r"\b(?:defined|was|were|considered|designated|chosen|specified)\b", re.I)
CRITERION_TOKEN_RE = re.compile(r"\b(?:within\s+\d+\s*(?:day|week|month|year)s?|\d+\s*(?:day|week|month|year)s?|readmission|hospitalisation|death|mi|stroke|composite|incidence|duration|rate)\b", re.I)
HEADING_OUTCOME_RE = re.compile(r"(?m)^(?:outcome\s+definition|endpoint\s+definition|primary\s+outcome|outcomes?)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\b(?:outcomes?\s+were|overall\s+outcome|secondary\s+analysis|result|positive\s+outcome)\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"(?:primary\s+)?(?:outcome|endpoint)\s*(?:was\s+defined\s+as|:)\s+[^\.\n]{0,100}", re.I)

def _collect(patterns, text):
    token_spans = _token_spans(text)
    out = []
    tokens = [text[s:e] for s,e in token_spans]
    for patt in patterns:
        for m in patt.finditer(text):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            snippet = " ".join(tokens[w_s:w_e+1])
            if TRAP_RE.search(snippet):
                continue
            out.append((w_s, w_e, snippet))
    return out

def find_outcome_definition_v1(text: str):
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    out = []
    for m in OUTCOME_CUE_RE.finditer(text):
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        snippet = " ".join(tokens[w_s:w_e+1])
        context_start = max(0, m.start()-50)
        context_end = min(len(text), m.end()+50)
        context = text[context_start:context_end]
        if not TRAP_RE.search(context):
            out.append((w_s, w_e, snippet))
    return out

def find_outcome_definition_v2(text: str, window: int = 5):
    token_spans=_token_spans(text); tokens=[text[s:e] for s,e in token_spans]
    verbs={i for i,t in enumerate(tokens) if DEFINE_VERB_RE.fullmatch(t)}
    out=[]
    for m in OUTCOME_CUE_RE.finditer(text):
        if TRAP_RE.search(text[max(0,m.start()-30):m.end()+30]): continue
        w_s,w_e=_char_span_to_word_span((m.start(),m.end()),token_spans)
        if any(v for v in verbs if w_s-window<=v<=w_e+window): out.append((w_s,w_e,m.group(0)))
    return out

def find_outcome_definition_v3(text: str, block_chars: int = 400):
    token_spans = _token_spans(text)
    matches = []
    for h in HEADING_OUTCOME_RE.finditer(text):
        start = h.end()
        nb = text.find("\n\n", start)
        end = nb if 0 <= nb - start <= block_chars else min(len(text), start + block_chars)
        block_text = text[start:end].strip()
        if block_text and not TRAP_RE.search(block_text) and not re.fullmatch(r"(not specified\.?|\(no outcome reported\))", block_text, re.I):
            w_start, w_end = _char_span_to_word_span((start, end), token_spans)
            matches.append((w_start, w_end, block_text))
    return matches

def find_outcome_definition_v4(text: str, window: int = 6):
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    matches = find_outcome_definition_v1(text) 
    out = []
    for w_s, w_e, snippet in matches:
        start = max(0, w_s - window)
        end = min(len(tokens) - 1, w_e + window)
        window_text = " ".join(tokens[start:end+1])
        if CRITERION_TOKEN_RE.search(window_text) and not re.search(r"\bvague\b", window_text, re.I):
            out.append((w_s, w_e, snippet))
    return out

def find_outcome_definition_v5(text:str): return _collect([TIGHT_TEMPLATE_RE], text)

OUTCOME_DEFINITION_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]]={"v1":find_outcome_definition_v1,"v2":find_outcome_definition_v2,"v3":find_outcome_definition_v3,"v4":find_outcome_definition_v4,"v5":find_outcome_definition_v5}
__all__=["find_outcome_definition_v1","find_outcome_definition_v2","find_outcome_definition_v3","find_outcome_definition_v4","find_outcome_definition_v5","OUTCOME_DEFINITION_FINDERS"]
find_outcome_definition_high_recall=find_outcome_definition_v1
find_outcome_definition_high_precision=find_outcome_definition_v5
