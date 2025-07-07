"""recruitment_timeline_finder.py – precision/recall ladder for *recruitment period / timeline*.
Five variants (v1–v5):
    • v1 – high recall: any recruitment/enrolment cue (recruited, enrolled, study period, follow‑up) immediately followed by a date or date‑range.
    • v2 – v1 **and** explicit date range separator (to, through, –, —) within the phrase.
    • v3 – only inside a *Recruitment / Study Period / Timeline* heading block (first ~500 characters).
    • v4 – v2 plus follow‑up duration phrase (followed for, follow‑up of X months/years) in the same sentence.
    • v5 – tight template: “Enrolled March 2015–July 2017; each followed 12 months.”
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
    return w_s,w_e

MONTHS = r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?"
YEAR = r"(?:19|20)\d{2}"
DATE_RE = rf"(?:{MONTHS}\s+{YEAR}|{YEAR})"
DATE_RANGE_RE = rf"{DATE_RE}\s*(?:–|-|to|through|until)\s*{DATE_RE}"

ENROL_CUE_RE = re.compile(r"\b(?:recruit(?:ed|ment)|enrol(?:led|ment)|included|study\s+period|data\s+collection|patients?\s+were\s+enrolled)\b", re.I)
FOLLOW_CUE_RE = re.compile(r"\bfollow(?:ed)?\s*(?:up|for)?\b", re.I)
HEAD_RECRUIT_RE = re.compile(r"(?m)^(?:recruitment|enrolment|study\s+period|timeline)\s*[:\-]?\s*$", re.I)
TIGHT_TEMPLATE_RE = re.compile(rf"enrol(?:led|ment)\s+{DATE_RANGE_RE};?\s+[^\.\n]{{0,40}}follow(?:ed|\s+up)\s+\d+\s+(?:months?|years?)", re.I)

TRAP_RE = re.compile(r"\bwas\s+challenging|difficult\s+to\s+recruit\b", re.I)

DATE_TOKEN = re.compile(rf"^(?:{MONTHS}|{YEAR})$", re.I)
RANGE_SEP = re.compile(r"^(?:–|-|to|through|until)$")


def _collect(patterns: Sequence[re.Pattern[str]], text: str):
    spans = _token_spans(text)
    out: List[Tuple[int,int,str]] = []
    for patt in patterns:
        for m in patt.finditer(text):
            if TRAP_RE.search(text[max(0,m.start()-25):m.end()+25]):
                continue
            w_s,w_e = _char_to_word((m.start(), m.end()), spans)
            out.append((w_s, w_e, m.group(0)))
    return out


def find_recruitment_timeline_v1(text: str):
    pattern = re.compile(rf"{ENROL_CUE_RE.pattern}[^\n]{{0,20}}(?:{DATE_RANGE_RE}|{DATE_RE})", re.I)
    return _collect([pattern], text)


def find_recruitment_timeline_v2(text: str, window: int = 6):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    cue_idx={i for i,t in enumerate(tokens) if ENROL_CUE_RE.fullmatch(t)}
    sep_idx={i for i,t in enumerate(tokens) if RANGE_SEP.fullmatch(t)}
    out=[]
    for c in cue_idx:
        if any(abs(s-c)<=window for s in sep_idx):
            w_s,w_e=_char_to_word(spans[c],spans)
            out.append((w_s,w_e,tokens[c]))
    return out


def find_recruitment_timeline_v3(text: str, block_chars: int = 500):
    spans=_token_spans(text)
    blocks=[]
    for h in HEAD_RECRUIT_RE.finditer(text):
        s=h.end(); e=min(len(text),s+block_chars)
        blocks.append((s,e))
    inside=lambda p:any(s<=p<e for s,e in blocks)
    out=[]
    for m in ENROL_CUE_RE.finditer(text):
        if inside(m.start()):
            w_s,w_e=_char_to_word((m.start(),m.end()),spans)
            out.append((w_s,w_e,m.group(0)))
    return out


def find_recruitment_timeline_v4(text: str, window: int = 8):
    spans=_token_spans(text)
    tokens=[text[s:e] for s,e in spans]
    follow_idx={i for i,t in enumerate(tokens) if FOLLOW_CUE_RE.fullmatch(t)}
    matches=find_recruitment_timeline_v2(text, window=window)
    out=[]
    for w_s,w_e,snip in matches:
        if any(w_s-window<=f<=w_e+window for f in follow_idx):
            out.append((w_s,w_e,snip))
    return out


def find_recruitment_timeline_v5(text: str):
    return _collect([TIGHT_TEMPLATE_RE], text)

RECRUITMENT_TIMELINE_FINDERS: Dict[str,Callable[[str],List[Tuple[int,int,str]]]] = {
    "v1":find_recruitment_timeline_v1,
    "v2":find_recruitment_timeline_v2,
    "v3":find_recruitment_timeline_v3,
    "v4":find_recruitment_timeline_v4,
    "v5":find_recruitment_timeline_v5,
}

__all__=["find_recruitment_timeline_v1","find_recruitment_timeline_v2","find_recruitment_timeline_v3","find_recruitment_timeline_v4","find_recruitment_timeline_v5","RECRUITMENT_TIMELINE_FINDERS"]

find_recruitment_timeline_high_recall=find_recruitment_timeline_v1
find_recruitment_timeline_high_precision=find_recruitment_timeline_v5
