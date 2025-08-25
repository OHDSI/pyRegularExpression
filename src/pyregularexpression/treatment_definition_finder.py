"""treatment_definition_finder.py – precision/recall ladder for *treatment definition* statements.
Five variants (v1–v5):
    • v1 – high recall: any treatment/intervention cue
    • v2 – cue + defining verb (received/administered/consisted of) within ±window tokens
    • v3 – only inside a *Treatment regimen / Intervention* heading block
    • v4 – v2 plus explicit regimen/dose/frequency token (mg, daily, × weeks, etc.), excludes vague ‘if needed’ mentions
    • v5 – tight template: “Drug X 10 mg daily × 12 weeks”, “Intervention consisted of 3 IU/kg every week”, etc.
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

TREATMENT_CUE_RE = re.compile(r"\b(?:treatment|treated|intervention|therapy|regimen)\b", re.I)
DEFINE_VERB_RE = re.compile(r"\b(?:received|administered|given|consisted|of|comprised|initiated|delivered)\b", re.I)
HEADING_TREATMENT_RE = re.compile(r"(?im)^(?:treatment\s+(?:definition|regimen)|intervention|drug\s+therapy)\s*[:\-]?", re.I)
REGIMEN_TOKEN_RE = re.compile(
    r"\b(?:\d+\s*(?:mg|ml|iu|mcg|g)|(?:iu(?:/kg)?|mg|ml|mcg|g)|daily|weekly|monthly|once\s+daily|twice\s+daily|x\s*\d+\s*(?:weeks?|months?)|for\s+\d+\s*(?:weeks?|months?))\b",
    re.I,
)
TRAP_RE = re.compile(r"\b(?:as\s+needed|prn|if\s+needed|according\s+to\s+need|outcome)\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"(?:treatment\s+group\s+received|intervention\s+consisted\s+of|drug\s+\w+\s*=?)\s+[A-Za-z0-9\s×x/\.\-]{5,80}", re.I)

def _collect(patterns: Sequence[re.Pattern[str]], text: str) -> List[Tuple[int, int, str]]:
    token_spans = _token_spans(text)
    out = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(m.group(0)):
                continue
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_treatment_definition_v1(text: str): return _collect([TREATMENT_CUE_RE], text)

def find_treatment_definition_v2(text: str, window: int = 5):
    token_spans = _token_spans(text); tokens=[text[s:e] for s,e in token_spans]
    verbs={i for i,t in enumerate(tokens) if DEFINE_VERB_RE.fullmatch(t)}
    out=[]
    for m in TREATMENT_CUE_RE.finditer(text):
        if TRAP_RE.search(text[max(0,m.start()-30):m.end()+30]): continue
        w_s,w_e=_char_span_to_word_span((m.start(),m.end()),token_spans)
        if any(v for v in verbs if w_s-window<=v<=w_e+window): out.append((w_s,w_e,m.group(0)))
    return out

def find_treatment_definition_v3(text: str, block_chars:int=400):
    token_spans=_token_spans(text); blocks=[]
    for h in HEADING_TREATMENT_RE.finditer(text):
        s=h.start(); nb=text.find("\n\n",h.end()); e=nb if 0<=nb-h.end()<=block_chars else h.end()+block_chars; blocks.append((s,e))
    inside=lambda p:any(s<=p<e for s,e in blocks)
    return [_char_span_to_word_span((m.start(),m.end()),token_spans)+ (m.group(0),) for m in TREATMENT_CUE_RE.finditer(text) if inside(m.start())]

def find_treatment_definition_v4(text: str, window:int=6):
    token_spans=_token_spans(text); tokens=[text[s:e] for s,e in token_spans]
    reg={i for i,t in enumerate(tokens) if REGIMEN_TOKEN_RE.fullmatch(t)}
    matches=find_treatment_definition_v2(text,window)
    return [t for t in matches if any(r for r in reg if t[0]-window<=r<=t[1]+window)]

def find_treatment_definition_v5(text:str): return _collect([TIGHT_TEMPLATE_RE], text)

TREATMENT_DEFINITION_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]]={"v1":find_treatment_definition_v1,"v2":find_treatment_definition_v2,"v3":find_treatment_definition_v3,"v4":find_treatment_definition_v4,"v5":find_treatment_definition_v5}
__all__=["find_treatment_definition_v1","find_treatment_definition_v2","find_treatment_definition_v3","find_treatment_definition_v4","find_treatment_definition_v5","TREATMENT_DEFINITION_FINDERS"]
find_treatment_definition_high_recall=find_treatment_definition_v1
find_treatment_definition_high_precision=find_treatment_definition_v5
