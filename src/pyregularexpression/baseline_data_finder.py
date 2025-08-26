"""baseline_data_finder.py – precision/recall ladder for *baseline participant characteristics*.
Five variants (v1–v5):
    • v1 – high recall: any baseline cue (baseline characteristics, at baseline, Table 1 shows demographics) followed by a numeric value or percentage.
    • v2 – v1 **and** explicit group label/comparison keyword (treatment, placebo, group, vs, compared to) within ±4 tokens.
    • v3 – only inside a *Baseline Characteristics* / *Table 1* heading block (first ~400 characters).
    • v4 – v2 plus at least two different baseline variables (age, sex, BMI, etc.) or multiple numbers/percentages in the same sentence.
    • v5 – tight template: “Mean age 54 vs 55; 60 % female in both groups at baseline.”
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
    return w_s, w_e

NUM_RE = r"\d+(?:\.\d+)?%?"
NUM_TOKEN_RE = re.compile(r"^\d+(?:\.\d+)?%?$" )
BASELINE_CUE_RE = re.compile(
    r"\b(?:baseline(?:\s+(?:characteristics|demographics|data))?|at\s+baseline|table\s+1)\b",
    re.I
)
GROUP_RE = re.compile(r"\b(?:treatment|intervention|placebo|control|group|arm|vs|versus|compared\s+to)\b", re.I)
VAR_RE = re.compile(r"\b(?:age|sex|gender|male|female|bmi|body\s+mass\s+index|weight|height|smokers?|comorbidities?|race|ethnicity)\b", re.I)
HEAD_BASE_RE = re.compile(r"(?m)^(?:baseline\s+characteristics|table\s+1|baseline\s+data)\s*[:\-]?\s*$", re.I)
TRAP_RE = re.compile(r"\bbaseline\s+(tumou?r|lesion|value|measurement)\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(
    r"""
    (?=.*\b(mean|median)?\s*age\s*\d+\s*(?:±\s*\d+)?\s*vs\s*\d+)    
    (?=.*\b\d+\s*%\s*(?:male|female)\b.*?(?:in\s+both\s+groups)?\s*(?:at\s+baseline)?)
    """,
    re.I | re.X
)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans=_token_spans(text)
    out: List[Tuple[int,int,str]]=[]
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0,m.start()-20):m.end()+20]):
                continue
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_baseline_data_v1(text: str):
    pattern=re.compile(rf"{BASELINE_CUE_RE.pattern}[^\n]{{0,30}}{NUM_RE}", re.I)
    return _collect([pattern], text)

def find_baseline_data_v2(text: str, window: int = 8):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    out = []
    sentences = re.split(r"(?<=[\.\n])\s+", text)

    for sent in sentences:
        if BASELINE_CUE_RE.search(sent) and GROUP_RE.search(sent) and re.search(NUM_RE, sent):
            for m in BASELINE_CUE_RE.finditer(sent):
                abs_start = text.find(sent) + m.start()
                abs_end = text.find(sent) + m.end()
                w_s, w_e = _char_to_word((abs_start, abs_end), spans)
                out.append((w_s, w_e, m.group(0)))
    return out

def find_baseline_data_v3(text: str, block_chars: int = 400):
    spans = _token_spans(text)
    blocks = []
    for h in HEAD_BASE_RE.finditer(text):
        s = h.end()
        e = min(len(text), s + block_chars)
        blocks.append((s, e))
    out = []
    for s, e in blocks:
        block_text = text[s:e]
        for m in re.finditer(r"\b(?:age|bmi|sex|weight|height|%|\d+)\b", block_text, re.I):
            abs_start = s + m.start()
            abs_end = s + m.end()
            w_s, w_e = _char_to_word((abs_start, abs_end), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_baseline_data_v4(text: str, window: int = 8):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    matches = find_baseline_data_v2(text, window)
    out = []
    for w_s, w_e, snip in matches:
        context = " ".join(tokens[max(0, w_s - window):min(len(tokens), w_e + window)])
        vars_found = set(VAR_RE.findall(context))
        nums_found = re.findall(NUM_RE, context)
        if len(vars_found) >= 2 or len(nums_found) >= 2:
            out.append((w_s, w_e, snip))
    return out

def find_baseline_data_v5(text: str) -> List[Tuple[int, int, str]]:
    match = TIGHT_TEMPLATE_RE.search(text)
    if match:
        start, end = match.span()
        return [(start, end, text[start:end])]
    return []

BASELINE_DATA_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1": find_baseline_data_v1,
    "v2": find_baseline_data_v2,
    "v3": find_baseline_data_v3,
    "v4": find_baseline_data_v4,
    "v5": find_baseline_data_v5,
}

__all__=["find_baseline_data_v1","find_baseline_data_v2","find_baseline_data_v3","find_baseline_data_v4","find_baseline_data_v5","BASELINE_DATA_FINDERS"]

find_baseline_data_high_recall=find_baseline_data_v1
find_baseline_data_high_precision=find_baseline_data_v5
