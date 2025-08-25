"""algorithm_validation_finder.py – precision/recall ladder for *algorithm validation* statements.
Five variants (v1–v5):
    • v1 – high recall: any phrase “algorithm validation/validated/evaluated” or performance metric keywords.
    • v2 – algorithm keyword + validation verb (validated/evaluated/assessed) within ±window tokens.
    • v3 – only inside an *Algorithm validation / Performance evaluation* heading block.
    • v4 – v2 plus metric tokens (PPV, NPV, sensitivity, specificity, accuracy, F1, AUC) to exclude algorithm-use-only context.
    • v5 – tight template: “Algorithm validated against chart review; PPV 92 %”, “Accuracy 0.89 (95 % CI) in external validation”, etc.
Each finder returns a list of tuples: (start_token_idx, end_token_idx, matched_snippet)
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

TOKEN_RE = re.compile(r"\S+")

def _token_spans(text: str) -> List[Tuple[int,int]]:
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_span_to_word_span(span: Tuple[int,int], token_spans: Sequence[Tuple[int,int]]) -> Tuple[int,int]:
    s_char, e_char = span
    w_start = next(i for i,(s,e) in enumerate(token_spans) if s<=s_char<e)
    w_end = next(i for i,(s,e) in reversed(list(enumerate(token_spans))) if s<e_char<=e)
    return w_start, w_end

ALGO_TERM_RE = re.compile(r"\balgorithm\b", re.I)
VALIDATE_VERB_RE = re.compile(r"\b(?:validated|validation|evaluated|assessed|tested|performance)\b", re.I)
METRIC_TOKEN_RE = re.compile(r"\b(?:ppv|npv|positive\s+predictive\s+value|negative\s+predictive\s+value|sensitivity|specificity|accuracy|f1|auc|area\s+under\s+the\s+curve|kappa)\b", re.I)
HEADING_VALID_RE = re.compile(r"(?m)^(?:algorithm\s+validation|validation\s+study|performance\s+evaluation)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\b(?:validated\s+questionnaire|assay\s+validation|method\s+validation)\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"algorithm\s+(?:was\s+)?(?:validated|evaluated|assessed)[^\.\n]{0,80}(?:ppv|accuracy|sensitivity|specificity|auc|f1)\b", re.I)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    token_spans=_token_spans(text)
    out=[]
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0,m.start()-30):m.end()+30]): continue
            w_s,w_e=_char_span_to_word_span((m.start(),m.end()),token_spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_algorithm_validation_v1(text:str):
    return _collect([re.compile(r"algorithm\s+validation",re.I), VALIDATE_VERB_RE, METRIC_TOKEN_RE], text)

def find_algorithm_validation_v2(text:str, window:int=4):
    token_spans=_token_spans(text); tokens=[text[s:e] for s,e in token_spans]
    val_idx={i for i,t in enumerate(tokens) if VALIDATE_VERB_RE.fullmatch(t)}
    out=[]
    for m in ALGO_TERM_RE.finditer(text):
        w_s,w_e=_char_span_to_word_span((m.start(),m.end()),token_spans)
        if any(v for v in val_idx if w_s-window<=v<=w_e+window):
            out.append((w_s,w_e,m.group(0)))
    return out

def find_algorithm_validation_v3(text:str, block_chars:int=300):
    token_spans=_token_spans(text); blocks=[]
    for h in HEADING_VALID_RE.finditer(text):
        s=h.end(); nxt=text.find("\n\n",s); e=nxt if 0<=nxt-s<=block_chars else s+block_chars
        blocks.append((s,e))
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in ALGO_TERM_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_span_to_word_span((m.start(),m.end()),token_spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_algorithm_validation_v4(text:str, window:int=6):
    token_spans=_token_spans(text); tokens=[text[s:e] for s,e in token_spans]
    met_idx={i for i,t in enumerate(tokens) if METRIC_TOKEN_RE.fullmatch(t)}
    matches=find_algorithm_validation_v2(text,window)
    out=[]
    for w_s,w_e,snip in matches:
        if any(m for m in met_idx if w_s-window<=m<=w_e+window):
            out.append((w_s,w_e,snip))
    return out

def find_algorithm_validation_v5(text:str):
    return _collect([TIGHT_TEMPLATE_RE], text)

ALGORITHM_VALIDATION_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1": find_algorithm_validation_v1,
    "v2": find_algorithm_validation_v2,
    "v3": find_algorithm_validation_v3,
    "v4": find_algorithm_validation_v4,
    "v5": find_algorithm_validation_v5,
}

__all__=["find_algorithm_validation_v1","find_algorithm_validation_v2","find_algorithm_validation_v3","find_algorithm_validation_v4","find_algorithm_validation_v5","ALGORITHM_VALIDATION_FINDERS"]
find_algorithm_validation_high_recall=find_algorithm_validation_v1
find_algorithm_validation_high_precision=find_algorithm_validation_v5
