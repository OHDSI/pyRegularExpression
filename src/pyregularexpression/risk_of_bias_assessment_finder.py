"""risk_of_bias_assessment_finder.py – precision/recall ladder for *risk‑of‑bias assessments* in systematic reviews.
Five variants (v1–v5):
    • v1 – high recall: any sentence with a bias‑assessment cue ("risk of bias", ROBINS‑I, ROB 2, Cochrane tool, Newcastle–Ottawa Scale, NOS, quality assessment).
    • v2 – v1 **and** assessment verb (assessed, evaluated, rated, scored, used, applied) within ±4 tokens of the cue.
    • v3 – only inside a *Risk of Bias / Quality Assessment* heading block (first ≈400 characters).
    • v4 – v2 plus explicit rating keyword (low, high, moderate, unclear) **or** tool name in the same sentence.
    • v5 – tight template: “Risk of bias was assessed with the ROBINS‑I tool.”
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

TOOL_RE = re.compile(r"\b(?:ROBINS[- ]?I|ROB[- ]?2|Cochrane\s+risk\s+of\s+bias\s+tool|Newcastle[-–]Ottawa\s+Scale|NOS)\b", re.I)
BIAS_CUE_RE = re.compile(r"\brisk\s+of\s+bias|quality\s+assessment\b", re.I)
VERB_RE = re.compile(r"\b(?:assessed|evaluated|rated|scored|used|applied|performed)\b", re.I)
RATING_RE = re.compile(r"\b(?:low|high|moderate|unclear)\b", re.I)
HEAD_ROB_RE = re.compile(r"(?m)^(?:risk\s+of\s+bias|quality\s+assessment|study\s+quality)\s*[:\-]?\s*$", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"risk\s+of\s+bias\s+was\s+assessed[^\.\n]{0,60}(?:ROBINS[- ]?I|ROB[- ]?2|Newcastle)", re.I)
TRAP_RE = re.compile(r"\bbias\s+may\s+affect|selection\s+bias\b", re.I)

def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans=_token_spans(text)
    out: List[Tuple[int,int,str]]=[]
    for patt in patterns:
        for m in patt.finditer(text):
            context=text[max(0,m.start()-40):m.end()+40]
            if TRAP_RE.search(context):
                continue
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_risk_of_bias_assessment_v1(text: str):
    return _collect([BIAS_CUE_RE, TOOL_RE], text)

def find_risk_of_bias_assessment_v2(text: str, window: int = 4):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    cue_idx={i for i,t in enumerate(tokens) if BIAS_CUE_RE.fullmatch(t) or TOOL_RE.fullmatch(t)}
    verb_idx={i for i,t in enumerate(tokens) if VERB_RE.fullmatch(t)}
    out=[]
    for c in cue_idx:
        if any(abs(v-c)<=window for v in verb_idx):
            w_s,w_e=_char_to_word(spans[c],spans)
            out.append((w_s,w_e,tokens[c]))
    return out

def find_risk_of_bias_assessment_v3(text: str, block_chars: int = 400):
    spans=_token_spans(text)
    blocks=[(h.end(),min(len(text),h.end()+block_chars)) for h in HEAD_ROB_RE.finditer(text)]
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in BIAS_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_risk_of_bias_assessment_v4(text: str, window: int = 6):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    extra_idx={i for i,t in enumerate(tokens) if TOOL_RE.fullmatch(t) or RATING_RE.fullmatch(t)}
    matches=find_risk_of_bias_assessment_v2(text, window=window)
    out=[]
    for w_s,w_e,snip in matches:
        if any(w_s-window<=k<=w_e+window for k in extra_idx):
            out.append((w_s,w_e,snip))
    return out

def find_risk_of_bias_assessment_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

RISK_OF_BIAS_ASSESSMENT_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1": find_risk_of_bias_assessment_v1,
    "v2": find_risk_of_bias_assessment_v2,
    "v3": find_risk_of_bias_assessment_v3,
    "v4": find_risk_of_bias_assessment_v4,
    "v5": find_risk_of_bias_assessment_v5,
}

__all__=[
    "find_risk_of_bias_assessment_v1","find_risk_of_bias_assessment_v2","find_risk_of_bias_assessment_v3",
    "find_risk_of_bias_assessment_v4","find_risk_of_bias_assessment_v5","RISK_OF_BIAS_ASSESSMENT_FINDERS"
]

find_risk_of_bias_assessment_high_recall=find_risk_of_bias_assessment_v1
find_risk_of_bias_assessment_high_precision=find_risk_of_bias_assessment_v5
