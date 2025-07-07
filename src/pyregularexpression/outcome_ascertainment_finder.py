"""outcome_ascertainment_finder.py – precision/recall ladder for *outcome ascertainment* statements.
Five variants (v1–v5):
    • v1 – high recall: any ascertainment verb cue (ascertained/identified/confirmed/etc.)
    • v2 – cue + source/preposition (via/through/from/using) within ±window tokens
    • v3 – only inside an *Outcome ascertainment / Event verification* heading block
    • v4 – v2 plus explicit outcome/event keyword (stroke, death, MI, cancer, etc.) or imaging/chart review term, excludes bias-only mentions
    • v5 – tight template: “Stroke events verified via imaging”, “Outcomes were confirmed by medical record review”, etc.
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

ASCERTAIN_VERB_RE = re.compile(
    r"\b(?:ascertained|identified|confirmed|verified|captured|obtained|detected)\b",
    re.I,
)

SOURCE_PREP_RE = re.compile(r"\b(?:via|through|from|using|with|based\s+on|by)\b", re.I)

OUTCOME_KEYWORD_RE = re.compile(
    r"\b(?:stroke|death|mortality|myocardial\s+infarction|mi|cancer|hospitalisation|event|outcome|endpoint)\b",
    re.I,
)

DATASET_TERM_RE = re.compile(r"\b(?:medical\s+records?|chart\s+review|claims?|imaging|registry|database|ehr|electronic\s+health\s+records?)\b", re.I)

HEADING_ASCERT_RE = re.compile(r"(?m)^(?:outcome\s+ascertainment|event\s+ascertainment|event\s+verification|event\s+adjudication)\s*[:\-]?\s*$", re.I)

TRAP_RE = re.compile(r"\bascertainment\s+bias\b", re.I)

TIGHT_TEMPLATE_RE = re.compile(
    r"(?:events?|outcomes?)\s+(?:were\s+)?(?:ascertained|confirmed|verified|identified)\s+(?:via|through|from|using|by)\s+[^\.\n]{0,80}",
    re.I,
)

def _collect(patterns: Sequence[re.Pattern[str]], text: str) -> List[Tuple[int, int, str]]:
    token_spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(m.group(0)):
                continue
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            out.append((w_s, w_e, m.group(0)))
    return out

def find_outcome_ascertainment_v1(text: str):
    return _collect([ASCERTAIN_VERB_RE], text)

def find_outcome_ascertainment_v2(text: str, window: int = 5):
    token_spans=_token_spans(text); tokens=[text[s:e] for s,e in token_spans]
    prep_idx={i for i,t in enumerate(tokens) if SOURCE_PREP_RE.fullmatch(t)}
    out=[]
    for m in ASCERTAIN_VERB_RE.finditer(text):
        if TRAP_RE.search(text[max(0,m.start()-30):m.end()+30]): continue
        w_s,w_e=_char_span_to_word_span((m.start(),m.end()),token_spans)
        if any(p for p in prep_idx if w_s-window<=p<=w_e+window):
            out.append((w_s,w_e,m.group(0)))
    return out

def find_outcome_ascertainment_v3(text: str, block_chars: int = 400):
    token_spans=_token_spans(text); blocks=[]
    for h in HEADING_ASCERT_RE.finditer(text):
        s=h.end(); nb=text.find("\n\n",s); e=nb if 0<=nb-s<=block_chars else s+block_chars; blocks.append((s,e))
    inside=lambda p:any(s<=p<e for s,e in blocks)
    return [_char_span_to_word_span((m.start(),m.end()),token_spans)+(m.group(0),) for m in ASCERTAIN_VERB_RE.finditer(text) if inside(m.start())]

def find_outcome_ascertainment_v4(text: str, window: int = 6):
    token_spans = _token_spans(text)
    tokens = [text[s:e] for s, e in token_spans]
    matches = find_outcome_ascertainment_v2(text, window)
    out = []
    for w_s, w_e, snippet in matches:
        start = max(0, w_s - window)
        end = min(len(tokens) - 1, w_e + window)
        window_text = " ".join(tokens[start:end+1])
        if OUTCOME_KEYWORD_RE.search(window_text) or DATASET_TERM_RE.search(window_text):
            out.append((w_s, w_e, snippet))
    return out

def find_outcome_ascertainment_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

OUTCOME_ASCERTAINMENT_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]]={"v1":find_outcome_ascertainment_v1,"v2":find_outcome_ascertainment_v2,"v3":find_outcome_ascertainment_v3,"v4":find_outcome_ascertainment_v4,"v5":find_outcome_ascertainment_v5}
__all__=["find_outcome_ascertainment_v1","find_outcome_ascertainment_v2","find_outcome_ascertainment_v3","find_outcome_ascertainment_v4","find_outcome_ascertainment_v5","OUTCOME_ASCERTAINMENT_FINDERS"]
find_outcome_ascertainment_high_recall=find_outcome_ascertainment_v1
find_outcome_ascertainment_high_precision=find_outcome_ascertainment_v5
