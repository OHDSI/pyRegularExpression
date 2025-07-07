"""statistical_analysis_additional_method_finder.py – precision/recall ladder for *statistical methods of additional analyses* (secondary, subgroup, exploratory).
Five variants (v1–v5):
    • v1 – high recall: any clause mentioning secondary/subgroup/post‑hoc/exploratory analysis + analysis verb (analysed, evaluated, modelled).
    • v2 – v1 **and** explicit statistical test/model keyword (logistic regression, Cox, ANOVA, etc.) within ±4 tokens.
    • v3 – only inside a *Statistical Analysis* or *Secondary/Subgroup Analysis* heading block (first ~500 characters).
    • v4 – v2 plus subgroup term or post‑hoc/exploratory keyword in same sentence.
    • v5 – tight template: “Secondary outcomes analysed with logistic regression; age subgroups examined.”
Each finder returns tuples: (start_word_idx, end_word_idx, snippet).
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

TOKEN_RE = re.compile(r"\\S+")

def _token_spans(text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_to_word(span: Tuple[int, int], spans: Sequence[Tuple[int, int]]):
    s, e = span
    w_s = next(i for i, (a, b) in enumerate(spans) if a <= s < b)
    w_e = next(i for i, (a, b) in reversed(list(enumerate(spans))) if a < e <= b)
    return w_s, w_e

SECONDARY_RE = re.compile(r"\\b(?:secondary|exploratory|post[- ]hoc|subgroup|additional)\\b", re.I)
ANALYSIS_VERB_RE = re.compile(r"\\b(?:analys(?:ed|is)|model(?:ed|ling)?|evaluat(?:ed|ion)|assess(?:ed|ment)?|examined|tested)\\b", re.I)
STAT_TEST_RE = re.compile(r"\\b(?:cox|kaplan[- ]meier|log[- ]rank|mixed[- ]effects?|gee|logistic\\s+regression|linear\\s+regression|poisson|negative\\s+binomial|anova|t[- ]test|chi[- ]square|fisher|wilcoxon|mann[- ]whitney)\\b", re.I)
HEAD_SEC_RE = re.compile(r"(?m)^(?:statistical\\s+analysis|secondary\\s+analysis|subgroup\\s+analysis|exploratory\\s+analysis)\\s*[:\\-]?\\s*$", re.I)
TRAP_RE = re.compile(r"\\bp\\s*<\\s*0\\.\\d+|significant|confidence\\s+interval\\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"secondary\\s+outcomes?\\s+analys(?:ed|is)\\s+with\\s+logistic\\s+regression[\\.\\;]\\s+[^\\.\\n]{0,60}?subgroups?\\s+examined", re.I)
SUBGROUP_TERM_RE = re.compile(r"\\b(?:subgroup|age\\s+group|sex|gender|baseline\\s+characteristic|interaction)\\b", re.I)

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

def find_statistical_analysis_additional_method_v1(text: str):
    patterns = [re.compile(rf"{SECONDARY_RE.pattern}[^\\.\\n]{{0,10}}{ANALYSIS_VERB_RE.pattern}", re.I)]
    return _collect(patterns, text)

def find_statistical_analysis_additional_method_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    test_idx = {i for i, t in enumerate(tokens) if STAT_TEST_RE.fullmatch(t)}
    sec_idx = {i for i, t in enumerate(tokens) if SECONDARY_RE.fullmatch(t)}
    out = []
    for s_i in sec_idx:
        if any(abs(t - s_i) <= window for t in test_idx):
            w_s, w_e = _char_to_word(spans[s_i], spans)
            out.append((w_s, w_e, tokens[s_i]))
    return out

def find_statistical_analysis_additional_method_v3(text: str, block_chars: int = 500):
    spans = _token_spans(text)
    blocks = []
    for h in HEAD_SEC_RE.finditer(text):
        s = h.end(); e = min(len(text), s + block_chars)
        blocks.append((s, e))
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in STAT_TEST_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_statistical_analysis_additional_method_v4(text: str, window: int = 6):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    sub_idx = {i for i, t in enumerate(tokens) if SUBGROUP_TERM_RE.fullmatch(t) or re.fullmatch(SECONDARY_RE, t)}
    matches = find_statistical_analysis_additional_method_v2(text, window=window)
    out = []
    for w_s, w_e, snip in matches:
        if any(w_s - window <= s <= w_e + window for s in sub_idx):
            out.append((w_s, w_e, snip))
    return out

def find_statistical_analysis_additional_method_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

STATISTICAL_ANALYSIS_ADDITIONAL_METHOD_FINDERS: Dict[str, Callable[[str], List[Tuple[int,int,str]]]] = {
    "v1": find_statistical_analysis_additional_method_v1,
    "v2": find_statistical_analysis_additional_method_v2,
    "v3": find_statistical_analysis_additional_method_v3,
    "v4": find_statistical_analysis_additional_method_v4,
    "v5": find_statistical_analysis_additional_method_v5,
}

__all__ = ["find_statistical_analysis_additional_method_v1","find_statistical_analysis_additional_method_v2","find_statistical_analysis_additional_method_v3","find_statistical_analysis_additional_method_v4","find_statistical_analysis_additional_method_v5","STATISTICAL_ANALYSIS_ADDITIONAL_METHOD_FINDERS"]

find_statistical_analysis_additional_method_high_recall = find_statistical_analysis_additional_method_v1
find_statistical_analysis_additional_method_high_precision = find_statistical_analysis_additional_method_v5
