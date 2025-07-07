"""statistical_analysis_primary_analysis_finder.py – precision/recall ladder for *statistical methods of the primary analysis*.
Five variants (v1–v5):
    • v1 – high recall: lines/clauses containing *primary outcome/endpoint* plus an analysis verb (analysed, assessed, modelled, evaluated) **or** an ITT/per‑protocol phrase.
    • v2 – v1 **and** explicit statistical test/model keyword (Cox model, mixed‑effects, logistic regression, Kaplan–Meier, t‑test, chi‑square, etc.) within ±4 tokens.
    • v3 – only inside a *Statistical Analysis* or *Primary Analysis* heading block (first ~500 characters).
    • v4 – v2 plus adjustment phrase (adjusting for, covariates, baseline) or modelling details (random effects, fixed effects, repeated measures) in the same sentence.
    • v5 – tight template: “Primary endpoint analysed with mixed‑effects linear model adjusting for baseline covariates.”
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
    w_s = next(i for i, (a, b) in enumerate(spans) if a <= s < b)
    w_e = next(i for i, (a, b) in reversed(list(enumerate(spans))) if a < e <= b)
    return w_s, w_e

PRIMARY_KEY_RE = re.compile(r"\bprimary\s+(?:endpoint|outcome)\b", re.I)
ANALYSIS_VERB_RE = re.compile(r"\b(?:analys(?:ed|is)|model(?:ed|ling)?|assess(?:ed|ment)?|evaluat(?:ed|ion)|tested)\b", re.I)
ITT_RE = re.compile(r"\b(?:intention[- ]to[- ]treat|per[- ]protocol|modified\s+itt|mITT)\b", re.I)
STAT_TEST_RE = re.compile(r"\b(?:cox(?:\s+proportional\s+hazards)?|kaplan[- ]meier|log[- ]rank|mixed[- ]effects?|generalised\s+estimating\s+equations|gee|linear\s+mixed|logistic\s+regression|poisson\s+regression|negative\s+binomial|anova|t[- ]test|chi[- ]square|fisher'?s\s+exact|wilcoxon|mann[- ]whitney|hazard\s+ratio|rate\s+ratio)\b", re.I)
ADJUST_RE = re.compile(r"\b(?:adjust(?:ed|ing)?\s+for|covariate|baseline|stratified\s+by|random\s+effects|fixed\s+effects|repeated\s+measures)\b", re.I)
HEAD_STAT_RE = re.compile(r"(?m)^(?:statistical\s+analysis(?:es)?|analysis|primary\s+analysis)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\bp\s*<\s*0\.\d+|significant|confidence\s+interval\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"primary\s+(?:endpoint|outcome)\s+analysed\s+with\s+mixed[- ]effects?\s+[^\".\n]{0,40}?adjust(?:ed|ing)\s+for\b", re.I)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0, m.start()-20):m.end()+20]):
                continue
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_statistical_analysis_primary_analysis_v1(text: str):
    patterns = [re.compile(rf"{PRIMARY_KEY_RE.pattern}[^\.\n]{{0,10}}{ANALYSIS_VERB_RE.pattern}", re.I), ITT_RE]
    return _collect(patterns, text)

def find_statistical_analysis_primary_analysis_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    tokens = [text[s:e].strip('.,') for s, e in spans]
    prim_idx = []
    for m in PRIMARY_KEY_RE.finditer(text):
        start_char = m.start()
        idx = next(i for i, (s, e) in enumerate(spans) if s <= start_char < e)
        prim_idx.append(idx)
    test_idx = []
    for m in STAT_TEST_RE.finditer(text):
        start_char = m.start()
        idx = next(i for i, (s, e) in enumerate(spans) if s <= start_char < e)
        test_idx.append(idx)
    out = []
    for p in prim_idx:
        if any(abs(p - t) <= window for t in test_idx):
            snippet_tokens = []
            for m in PRIMARY_KEY_RE.finditer(text):
                if m.start() == spans[p][0]:
                    snippet_tokens = text[m.start():m.end()].split()
                    break
            out.append((p, p + len(snippet_tokens) - 1, ' '.join(snippet_tokens)))

    return out

def find_statistical_analysis_primary_analysis_v3(text:str, block_chars:int=500):
    spans=_token_spans(text)
    blocks=[]
    for h in HEAD_STAT_RE.finditer(text):
        s=h.end(); e=min(len(text),s+block_chars)
        blocks.append((s,e))
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in STAT_TEST_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_statistical_analysis_primary_analysis_v4(text: str, window: int = 6):
    spans = _token_spans(text)
    tokens = [text[s:e].strip('.,') for s, e in spans]
    adj_idx = []
    for m in ADJUST_RE.finditer(text):
        start_char = m.start()
        token_pos = next(i for i, (s, e) in enumerate(spans) if s <= start_char < e)
        adj_idx.append(token_pos)
    matches = find_statistical_analysis_primary_analysis_v2(text, window)
    out = []
    for token_start, token_end, snippet in matches:
        if any(token_start - window <= a <= token_end + window for a in adj_idx):
            out.append((token_start, token_end, snippet))
    return out

def find_statistical_analysis_primary_analysis_v5(text:str):
    return _collect([TIGHT_TEMPLATE_RE], text)

STATISTICAL_ANALYSIS_PRIMARY_ANALYSIS_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]]={
    "v1":find_statistical_analysis_primary_analysis_v1,
    "v2":find_statistical_analysis_primary_analysis_v2,
    "v3":find_statistical_analysis_primary_analysis_v3,
    "v4":find_statistical_analysis_primary_analysis_v4,
    "v5":find_statistical_analysis_primary_analysis_v5,
}

__all__=["find_statistical_analysis_primary_analysis_v1","find_statistical_analysis_primary_analysis_v2","find_statistical_analysis_primary_analysis_v3","find_statistical_analysis_primary_analysis_v4","find_statistical_analysis_primary_analysis_v5","STATISTICAL_ANALYSIS_PRIMARY_ANALYSIS_FINDERS"]

find_statistical_analysis_primary_analysis_high_recall=find_statistical_analysis_primary_analysis_v1
find_statistical_analysis_primary_analysis_high_precision=find_statistical_analysis_primary_analysis_v5
