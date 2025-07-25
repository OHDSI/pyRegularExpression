"""exclusion_rule_finder.py – precision/recall ladder for *exclusion‑rule* statements.
Five variants (v1–v5):
    • v1 – high recall: any exclusion/‘not eligible’ cue
    • v2 – cue + gating words like ‘if’, ‘only’, or ':' within context window
    • v3 – only inside an *Exclusion criteria* heading block
    • v4 – v2 plus explicit conditional verbs (must NOT have), excludes follow‑up / dropout traps
    • v5 – tight template: “Exclusion criteria: …” or “Patients were excluded if …”
All functions return a list of tuples: (start_token_idx, end_token_idx, matched_snippet)
"""
from __future__ import annotations
import re
from typing import List, Tuple, Sequence, Dict, Callable

# ─────────────────────────────
# 0.  Shared utilities
# ─────────────────────────────
TOKEN_RE = re.compile(r"\S+")

def _token_spans(text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in TOKEN_RE.finditer(text)]

def _char_span_to_word_span(span: Tuple[int, int], token_spans: Sequence[Tuple[int, int]]) -> Tuple[int, int]:
    s_char, e_char = span
    w_start = next(i for i, (s, e) in enumerate(token_spans) if s <= s_char < e)
    w_end = next(i for i, (s, e) in reversed(list(enumerate(token_spans))) if s < e_char <= e)
    return w_start, w_end

# ─────────────────────────────
# 1.  Regex assets
# ─────────────────────────────

EXCLUSION_RULE_TERM_RE = re.compile(r"\b(?:exclusion\s+criteria|excluded(?:\s+only|\s+if)?|not\s+eligible|must\s+not\s+have|history\s+of|allergy|exclusions\s*[:\n]?)\b", re.I)
HEADING_EXCLUSION_RE = re.compile(r"^(exclusion criteria|exclusions)\s*[:\n]?", re.I | re.M)
GATING_TOKEN_RE = re.compile(r"\b(?:if|only|criteria:|:|not\s+eligible|must\s+not\s+have)\b", re.I)
TRAP_RE = re.compile(r"\b(excluded\s+variables?|excluded\s+the\s+possibility|(?:analysis|study|trial)\s+excluded|withdrew|withdrawn|lost\s+to\s+follow[- ]?up|dropped\s+out|after\s+enrol(?:l|l)ment|during\s+follow[- ]?up|excluded\s+from\s+.*analysis)\b", re.I)
TIGHT_TEMPLATE_RE = re.compile(r"(?:exclusion\s+criteria:\s+[^\.\n]{0,120}|patients?\s+were\s+excluded\s+if\s+[^\.\n]{0,120}|participants?\s+were\s+not\s+eligible\s+if\s+[^\.\n]{0,120})", re.I)
CONDITIONAL_VERB_RE = re.compile(r"\b(?:must\s+not\s+have|were\s+not\s+eligible|had\s+to\s+be\s+free\s+of)\b", re.I)

# ─────────────────────────────
# 2.  Helper
# ─────────────────────────────
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

# ─────────────────────────────
# 3.  Finder variants
# ─────────────────────────────
#def find_exclusion_rule_v1(text: str) -> List[Tuple[int, int, str]]:
    """Tier 1 – any exclusion/‘not eligible’ cue."""
 #   return _collect([EXCLUSION_RULE_TERM_RE], text)

def find_exclusion_rule_v1(text: str) -> List[Tuple[int, int, str]]:
    """Tier 1 – high recall: any exclusion/‘not eligible’ cue, filters nearby traps."""
    token_spans = _token_spans(text)
    out: List[Tuple[int, int, str]] = []

    for m in EXCLUSION_RULE_TERM_RE.finditer(text):
        # Trap-aware: skip if trap found within 30-character context
        if TRAP_RE.search(text[max(0, m.start() - 60): m.end() + 60]):
            continue
        w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
        out.append((w_s, w_e, m.group(0)))

    return out

def find_exclusion_rule_v2(text: str, window: int = 5) -> List[Tuple[int, int, str]]:
    """Tier 2 – cue + gating token (‘if’, ‘only’, ':') nearby."""
    token_spans = _token_spans(text)
    tokens = [text[s:e].lower() for s, e in token_spans]
    out = []
    for m in EXCLUSION_RULE_TERM_RE.finditer(text):
        cue_start, cue_end = m.start(), m.end()
        w_s, w_e = _char_span_to_word_span((cue_start, cue_end), token_spans)
        nearby = tokens[max(0, w_s - window): w_e + window]
        
        # Case 1: "excluded if", "not eligible only", etc.
        if any(g in nearby for g in {"if", "only"}):
            out.append((w_s, w_e, m.group(0)))
            continue

        # Case 2: "cue:" colon pattern — colon must immediately follow
        after_cue = text[cue_end:cue_end + 5].lstrip()
        if after_cue.startswith(":"):
            out.append((w_s, w_e, m.group(0)))
            continue
    return out

def find_exclusion_rule_v3(text: str, block_chars: int = 400) -> List[Tuple[int, int, str]]:
    """Tier 3 – only inside ‘Exclusion criteria’ heading blocks."""
    token_spans = _token_spans(text)
    blocks: List[Tuple[int, int]] = []
    for match in HEADING_EXCLUSION_RE.finditer(text):
        start = match.end()
        next_double_newline = text.find("\n\n", start)

        # Compute block end conservatively
        if 0 <= next_double_newline - start <= block_chars:
            end = next_double_newline
        else:
            end = min(start + block_chars, len(text))

        blocks.append((start, end))

    def _inside(pos: int) -> bool:
        return any(start <= pos < end for start, end in blocks)

    matches: List[Tuple[int, int, str]] = []
    for m in EXCLUSION_RULE_TERM_RE.finditer(text):
        if _inside(m.start()):
            w_s, w_e = _char_span_to_word_span((m.start(), m.end()), token_spans)
            matches.append((w_s, w_e, m.group(0)))

    return matches

def find_exclusion_rule_v3(text: str):
    # Normalize text to handle different casings
    lines = text.lower().splitlines()
    matches = []
    in_exclusion_block = False

    for i, line in enumerate(lines):
        line = line.strip()
        if re.match(r"^(exclusion criteria|exclusions)\s*:", line):
            in_exclusion_block = True
            continue
        if in_exclusion_block:
            if line == "":
                in_exclusion_block = False
                continue
            # Match any reasonable exclusion statement
            if re.search(r"\bmust not have\b|\bnot eligible\b|\bhistory of\b|\ballergy\b", line):
                matches.append((i, i, line))
    return matches

def find_exclusion_rule_v4(text: str) -> List[Tuple[int, int, str]]:
    """Tier 4 – v2 + explicit negative conditional verbs, excludes follow‑up traps."""
    token_spans = _token_spans(text)
    tokens = [text[s:e].lower() for s, e in token_spans]
    out = []

    for i in range(len(tokens) - 2):
        if tokens[i] == "must" and tokens[i + 1] == "not" and tokens[i + 2] in {"have", "be", "meet"}:
            # look ahead for conditional token
            if any(t in {"if", "only", "unless", "provided"} for t in tokens[i + 3:i + 10]):
                w_s, w_e = i, i + 3
                out.append((w_s, w_e, " ".join(tokens[w_s:w_e])))
    return out

def find_exclusion_rule_v5(text: str) -> List[Tuple[int, int, str]]:
    """Tier 5 – tight template (colon list or ‘excluded if’ sentence)."""
    return _collect([TIGHT_TEMPLATE_RE], text)

# ─────────────────────────────
# 4.  Public mapping & exports
# ─────────────────────────────
EXCLUSION_RULE_FINDERS: Dict[str, Callable[[str], List[Tuple[int, int, str]]]] = {
    "v1": find_exclusion_rule_v1,
    "v2": find_exclusion_rule_v2,
    "v3": find_exclusion_rule_v3,
    "v4": find_exclusion_rule_v4,
    "v5": find_exclusion_rule_v5,
}

__all__ = [
    "find_exclusion_rule_v1",
    "find_exclusion_rule_v2",
    "find_exclusion_rule_v3",
    "find_exclusion_rule_v4",
    "find_exclusion_rule_v5",
    "EXCLUSION_RULE_FINDERS",
]

# handy aliases
find_exclusion_rule_high_recall = find_exclusion_rule_v1
find_exclusion_rule_high_precision = find_exclusion_rule_v5

