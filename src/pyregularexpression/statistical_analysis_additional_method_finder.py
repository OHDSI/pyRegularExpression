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

TOKEN_RE = re.compile(r"\S+")

def _token_spans(text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_to_word(span: Tuple[int, int], spans: Sequence[Tuple[int, int]]):
    s, e = span
    w_s = next(i for i, (a, b) in enumerate(spans) if a <= s < b)
    w_e = next(i for i, (a, b) in reversed(list(enumerate(spans))) if a < e <= b)
    return w_s, w_e

SECONDARY_RE = re.compile(r"\b(?:secondary|exploratory|post[- ]hoc|subgroup|additional)\b", re.I)
ANALYSIS_VERB_RE = re.compile(r"\b(?:analys(?:ed|is)|model(?:ed|ling)?|evaluat(?:ed|ion)|assess(?:ed|ment)?|examined|tested)\b", re.I)
STAT_TEST_RE = re.compile(r"\b(?:cox|kaplan[- ]meier|log[- ]rank|mixed[- ]effects?|gee|logistic\s+regression|linear\s+regression|poisson|negative\s+binomial|anova|t[- ]test|chi[- ]square|fisher|wilcoxon|mann[- ]whitney)\b", re.I)
HEAD_SEC_RE = re.compile(r"(?i)(statistical\s+analysis|secondary\s+analysis|subgroup\s+analysis|exploratory\s+analysis)\s*[:\-]?", re.M)
TRAP_RE = re.compile(r"\bp\s*<\s*0\.\d+|significant|confidence\s+interval\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"secondary\s+outcomes?\s+analys(?:ed|is)\s+with\s+logistic\s+regression[.;]\s+[^.\n]{0,60}?subgroups?\s+examined", re.I)
SUBGROUP_TERM_RE = re.compile(r"\b(?:subgroup|age\s+group|sex|gender|baseline\s+characteristic|interaction)\b", re.I)

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
    pattern = re.compile(r"\b(?:secondary|subgroup|exploratory|post[- ]hoc|additional)\b.*?\b(?:analys(?:ed|is)|model(?:ed|ling)?|evaluat(?:ed|ion)|performed|examined|tested)\b",re.I )
    return _collect([pattern], text)

def find_statistical_analysis_additional_method_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    token_map = {i: (s, e) for i, (s, e) in enumerate(spans)}
    sec_idx = {i for i, t in enumerate(tokens) if SECONDARY_RE.search(t)}
    test_idx = set()
    for match in STAT_TEST_RE.finditer(text):
        start, end = match.start(), match.end()
        w_s = next(i for i, (s, e) in enumerate(spans) if s <= start < e)
        w_e = next(i for i, (s, e) in reversed(list(enumerate(spans))) if s < end <= e)
        test_idx.update(range(w_s, w_e+1))
    out = []
    for s_i in sec_idx:
        nearby_tests = [t for t in test_idx if abs(t - s_i) <= window]
        if nearby_tests:
            w_s = min([s_i] + nearby_tests)
            w_e = max([s_i] + nearby_tests)
            snippet = " ".join(tokens[w_s:w_e+1])
            out.append((w_s, w_e, snippet))
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
    base_matches = find_statistical_analysis_additional_method_v2(text, window=window)
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    sub_idx = {i for i, t in enumerate(tokens) if SUBGROUP_TERM_RE.search(t) or SECONDARY_RE.search(t)}
    out = []
    for w_s, w_e, snip in base_matches:
        if any(max(0, w_s - window) <= s <= w_e + window for s in sub_idx):
            out.append((w_s, w_e, snip))
    return out

def find_statistical_analysis_additional_method_v5(text: str):
    pattern = re.compile(r"(?:secondary\s+outcomes?\s+analys(?:ed|is)|subgroup\s+analyses?\s+performed).*?logistic\s+regression.*?(?:subgroups?\s+examined|baseline\s+characteristics?)?", re.I | re.DOTALL)
    return _collect([pattern], text)

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
