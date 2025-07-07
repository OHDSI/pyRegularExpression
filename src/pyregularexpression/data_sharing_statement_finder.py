"""data_sharing_statement_finder.py – precision/recall ladder for *data‑sharing statements*.
Five variants (v1–v5):
    • v1 – high recall: any sentence with a sharing cue ("data will be shared upon request", "data are available", repository names like Dryad, Figshare, Zenodo, OSF, Github, "data sharing statement").
    • v2 – v1 **and** verb indicating availability (available, shared, provided, deposited, released) within ±4 tokens of the cue.
    • v3 – only inside a *Data Availability / Data Sharing / Availability Statement* heading block (first ≈400 characters).
    • v4 – v2 plus explicit access mechanism – repository name **or** phrase “upon request” / “contact the author”.
    • v5 – tight template: “Individual participant data will be available in Dryad after publication.”
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

DATA_CUE_RE = re.compile(r"\b(?:data\s+sharing\s+statement|data\s+(?:will\s+be\s+)?shared|data\s+are\s+available|data\s+available|dataset\s+available|datasets?\s+deposited|data\s+availability)\b", re.I)
VERB_RE = re.compile(r"\b(?:shared|available|provided|deposited|released|accessible)\b", re.I)
REPO_RE = re.compile(r"\b(?:Dryad|Figshare|Zenodo|OSF|Open\s+Science\s+Framework|GitHub|Dataverse|ClinicalStudyDataRequest|Yoda)\b", re.I)
REQUEST_RE = re.compile(r"\bupon\s+request|by\s+request|contact\s+the\s+author|reasonable\s+request\b", re.I)
HEAD_DS_RE = re.compile(r"(?m)^(?:data\s+availability|availability\s+statement|data\s+sharing)\s*[:\-]?.*", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"data\s+will\s+be\s+available[^\.\n]{0,60}(?:Dryad|Figshare|Zenodo|upon\s+request)", re.I)
TRAP_RE = re.compile(r"\bopen\s+access\s+census\s+data|publicly\s+available\s+datasets?\s+were\s+used\b", re.I)

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

def find_data_sharing_statement_v1(text: str):
    return _collect([DATA_CUE_RE, REPO_RE], text)

def find_data_sharing_statement_v2(text: str, window: int = 4):
    spans = _token_spans(text)
    tokens = [text[s:e] for s, e in spans]
    out = []
    # search DATA_CUE_RE matches
    for m in DATA_CUE_RE.finditer(text):
        start, end = m.start(), m.end()
        w_s, w_e = _char_to_word((start, end), spans)
        token_window = range(max(0, w_s - window), min(len(tokens), w_e + window + 1))
        if any(VERB_RE.fullmatch(tokens[i]) for i in token_window):
            out.append((w_s, w_e, m.group(0)))
    # search REPO_RE matches with nearby verb
    for m in REPO_RE.finditer(text):
        start, end = m.start(), m.end()
        w_s, w_e = _char_to_word((start, end), spans)
        token_window = range(max(0, w_s - window), min(len(tokens), w_e + window + 1))
        if any(VERB_RE.fullmatch(tokens[i]) for i in token_window):
            out.append((w_s, w_e, m.group(0)))
    return out

def find_data_sharing_statement_v3(text: str, block_chars: int = 400):
    spans = _token_spans(text)
    blocks = [(h.start(), min(len(text), h.start() + block_chars)) for h in HEAD_DS_RE.finditer(text)]
    inside = lambda p: any(s <= p < e for s, e in blocks)
    out = []
    for m in DATA_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s, w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_data_sharing_statement_v4(text: str, window: int = 6):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    mech_idx={i for i,t in enumerate(tokens) if REPO_RE.search(t) or REQUEST_RE.search(t)}
    matches=find_data_sharing_statement_v2(text, window=window)
    out=[]
    for w_s,w_e,snip in matches:
        if any(w_s-window<=k<=w_e+window for k in mech_idx):
            out.append((w_s,w_e,snip))
    return out

def find_data_sharing_statement_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

DATA_SHARING_STATEMENT_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1": find_data_sharing_statement_v1,
    "v2": find_data_sharing_statement_v2,
    "v3": find_data_sharing_statement_v3,
    "v4": find_data_sharing_statement_v4,
    "v5": find_data_sharing_statement_v5,
}

__all__=[
    "find_data_sharing_statement_v1","find_data_sharing_statement_v2","find_data_sharing_statement_v3",
    "find_data_sharing_statement_v4","find_data_sharing_statement_v5","DATA_SHARING_STATEMENT_FINDERS"
]

find_data_sharing_statement_high_recall=find_data_sharing_statement_v1
find_data_sharing_statement_high_precision=find_data_sharing_statement_v5
