"""data_safety_monitoring_finder.py – precision/recall ladder for *Data‑Safety Monitoring* descriptions.
Five variants (v1–v5):
    • v1 – high recall: any sentence with DSMB/DMC cues ("Data Safety Monitoring Board", "Data Monitoring Committee", DSMB, DMC, periodic safety review).
    • v2 – v1 **and** safety verb (reviewed, monitored, met, evaluated) within ±4 tokens of the cue.
    • v3 – only inside a *Data Safety Monitoring / DSMB / DMC* heading block (first ≈400 characters).
    • v4 – v2 plus explicit independence/frequency term (independent, external, quarterly, periodic) or phrase “safety data”.
    • v5 – tight template: “An independent DSMB met quarterly to review adverse events.”
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
    w_s = next(i for i,(a,b) in enumerate(spans) if a<=s<b)
    w_e = next(i for i,(a,b) in reversed(list(enumerate(spans))) if a<e<=b)
    return w_s, w_e

DSMB_RE = re.compile(r"\\b(?:data\\s+(?:and\\s+)?safety\\s+monitoring\\s+(?:board|committee)|data\\s+monitoring\\s+committee|DSMB|DMC)\\b", re.I)
VERB_RE = re.compile(r"\\b(?:reviewed|monitored|met|evaluated|assessed)\\b", re.I)
SAFETY_RE = re.compile(r"\\b(?:safety\\s+data|adverse\\s+events?|AE[s]?)\\b", re.I)
FREQ_RE = re.compile(r"\\b(?:quarterly|monthly|periodic(?:ally)?|annual(?:ly)?)\\b", re.I)
HEAD_DSMB_RE = re.compile(r"(?m)^(?:data\\s+safety\\s+monitoring|DSMB|DMC)\\s*[:\\-]?\\s*$", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"independent\\s+DSMB\\s+met\\s+\\w+\\s+to\\s+review\\s+safety\\s+data", re.I)

TRAP_RE = re.compile(r"\\bmonitoring\\s+of\\s+data\\s+quality|data\\s+safety\\s+sheet\\b", re.I)

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

def find_data_safety_monitoring_v1(text: str):
    return _collect([DSMB_RE], text)

def find_data_safety_monitoring_v2(text: str, window: int = 4):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    cue_idx={i for i,t in enumerate(tokens) if DSMB_RE.fullmatch(t)}
    verb_idx={i for i,t in enumerate(tokens) if VERB_RE.fullmatch(t)}
    out=[]
    for c in cue_idx:
        if any(abs(v-c)<=window for v in verb_idx):
            w_s,w_e=_char_to_word(spans[c],spans)
            out.append((w_s,w_e,tokens[c]))
    return out

def find_data_safety_monitoring_v3(text: str, block_chars: int = 400):
    spans=_token_spans(text)
    blocks=[(h.end(),min(len(text),h.end()+block_chars)) for h in HEAD_DSMB_RE.finditer(text)]
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in DSMB_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_data_safety_monitoring_v4(text: str, window: int = 6):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    extra_idx={i for i,t in enumerate(tokens) if SAFETY_RE.fullmatch(t) or FREQ_RE.fullmatch(t)}
    matches=find_data_safety_monitoring_v2(text, window=window)
    out=[]
    for w_s,w_e,snip in matches:
        if any(w_s-window<=k<=w_e+window for k in extra_idx):
            out.append((w_s,w_e,snip))
    return out

def find_data_safety_monitoring_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

DATA_SAFETY_MONITORING_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1": find_data_safety_monitoring_v1,
    "v2": find_data_safety_monitoring_v2,
    "v3": find_data_safety_monitoring_v3,
    "v4": find_data_safety_monitoring_v4,
    "v5": find_data_safety_monitoring_v5,
}

__all__=[
    "find_data_safety_monitoring_v1","find_data_safety_monitoring_v2","find_data_safety_monitoring_v3",
    "find_data_safety_monitoring_v4","find_data_safety_monitoring_v5","DATA_SAFETY_MONITORING_FINDERS"
]

find_data_safety_monitoring_high_recall=find_data_safety_monitoring_v1
find_data_safety_monitoring_high_precision=find_data_safety_monitoring_v5
