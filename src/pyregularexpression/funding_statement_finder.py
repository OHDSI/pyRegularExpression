"""funding_statement_finder.py – precision/recall ladder for *study funding statements*.
Five variants (v1–v5):
    • v1 – high recall: any funding cue ("funded by", "supported by", "sponsored by", funding source, grant number, NIH, Wellcome Trust).
    • v2 – v1 **and** a funding verb (funded, supported, sponsored, provided by) within ±4 tokens of the cue.
    • v3 – only inside a *Funding* or *Financial Support* heading block (first ≈400 characters).
    • v4 – v2 plus explicit grant/organisation identifier (e.g., R01‑HL123456, grant number XXXXX, corporate name) in same sentence.
    • v5 – tight template: “Supported by NIH grant R01‑HL123456.”
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

FUND_CUE_RE = re.compile(r"\\b(?:funded|funding|supported|financially\\s+supported|sponsored|funding\\s+source|grant(?:\\s+number)?|grants?)\\b", re.I)
VERB_RE = re.compile(r"\\b(?:funded|supported|sponsored|provided|awarded)\\b", re.I)
GRANT_ID_RE = re.compile(r"\\b(?:R\\d{2}[A-Z]{0,2}\\d{6}|[A-Z]{2,}-?\\d{4,}|grant\\s+\\d{5,}|\\d{6,})\\b", re.I)
ORG_RE = re.compile(r"\\b(?:NIH|National\\s+Institutes\\s+of\\s+Health|NSF|Wellcome\\s+Trust|Gates\\s+Foundation|Pfizer|Novartis|Merck|Roche)\\b", re.I)
HEAD_FUND_RE = re.compile(r"(?m)^(?:funding|financial\\s+support|sources?\\s+of\\s+funding|acknowledg(?:e)?ments?)\\s*[:\\-]?\\s*$", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"supported\\s+by\\s+[A-Z]{2,}.*grant\\s+\\w+", re.I)
TRAP_RE = re.compile(r"\\bno\\s+personal\\s+fees|conflicts?\\s+of\\s+interest|employed\\s+by\\b", re.I)

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

def find_funding_statement_v1(text: str):
    return _collect([FUND_CUE_RE, ORG_RE, GRANT_ID_RE], text)

def find_funding_statement_v2(text: str, window: int = 4):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    cue_idx={i for i,t in enumerate(tokens) if FUND_CUE_RE.fullmatch(t) or ORG_RE.fullmatch(t) or GRANT_ID_RE.fullmatch(t)}
    verb_idx={i for i,t in enumerate(tokens) if VERB_RE.fullmatch(t)}
    out=[]
    for c in cue_idx:
        if any(abs(v-c)<=window for v in verb_idx):
            w_s,w_e=_char_to_word(spans[c],spans)
            out.append((w_s,w_e,tokens[c]))
    return out

def find_funding_statement_v3(text: str, block_chars: int = 400):
    spans=_token_spans(text)
    blocks=[(h.end(),min(len(text),h.end()+block_chars)) for h in HEAD_FUND_RE.finditer(text)]
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in FUND_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out

def find_funding_statement_v4(text: str, window: int = 6):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    id_idx={i for i,t in enumerate(tokens) if GRANT_ID_RE.fullmatch(t) or ORG_RE.fullmatch(t)}
    matches=find_funding_statement_v2(text, window=window)
    out=[]
    for w_s,w_e,snip in matches:
        if any(w_s-window<=k<=w_e+window for k in id_idx):
            out.append((w_s,w_e,snip))
    return out

def find_funding_statement_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

FUNDING_STATEMENT_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1": find_funding_statement_v1,
    "v2": find_funding_statement_v2,
    "v3": find_funding_statement_v3,
    "v4": find_funding_statement_v4,
    "v5": find_funding_statement_v5,
}

__all__=["find_funding_statement_v1","find_funding_statement_v2","find_funding_statement_v3","find_funding_statement_v4","find_funding_statement_v5","FUNDING_STATEMENT_FINDERS"]

find_funding_statement_high_recall=find_funding_statement_v1
find_funding_statement_high_precision=find_funding_statement_v5
