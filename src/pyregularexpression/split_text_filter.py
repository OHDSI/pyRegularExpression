from __future__ import annotations
from dataclasses import dataclass       # stdlib ≥3.7 :contentReference[oaicite:1]{index=1}
from typing import Callable, Iterable, List, Tuple, Dict
import bisect, functools, re

import nltk                             # relies on PunktSentenceTokenizer :contentReference[oaicite:2]{index=2}
from nltk.tokenize import PunktSentenceTokenizer

# -------------------------------------------------------------------
@dataclass(slots=True)
class SplitResult:
    """Richer return value for `split_text_by_filter`."""
    matched: str                 # concatenated context window (LLM payload)
    notmatched: str              # everything that was dropped
    sentences: List[str]         # full article, in order
    mask: List[bool]             # True → kept, False → dropped
    matched_ix: List[int]        # indices of kept sentences
    hits: List[Tuple[int, str, str]]  # (sent_idx, finder_name, hit)

    # convenience iterators
    def kept_sentences(self):
        return (s for s, keep in zip(self.sentences, self.mask) if keep)

    def dropped_sentences(self):
        return (s for s, keep in zip(self.sentences, self.mask) if not keep)


_TOKEN_RE = re.compile(r"\S+")

@functools.lru_cache(maxsize=1)
def _tokenizer() -> PunktSentenceTokenizer:
    return PunktSentenceTokenizer()

def _token_spans(text: str) -> List[Tuple[int, int]]:
    return [(m.start(), m.end()) for m in _TOKEN_RE.finditer(text)]

def _sentence_data(text: str):
    tok = _tokenizer()
    spans = list(tok.span_tokenize(text))
    sents = [text[s:e] for s, e in spans]
    starts = [s for s, _ in spans]
    return sents, starts

# -------------------------------------------------------------------
def split_text_by_filter(
    text: str,
    finder_funcs: Iterable[Callable[[str], List[Tuple[int, int, str]]]],
    window_back: int = 0,
    window_fwd: int = 0,
) -> SplitResult:
    """Return a dataclass with matched & not-matched info (see SplitResult)."""
    if not text.strip():
        return SplitResult("", "", [], [], [], [])

    sentences, sent_start_chars = _sentence_data(text)
    token_spans = _token_spans(text)

    matched_idx: set[int] = set()
    hits: List[Tuple[int, str, str]] = []

    for finder in finder_funcs:
        for w_start, _w_end, hit in finder(text):
            if w_start >= len(token_spans):
                continue
            char_pos = token_spans[w_start][0]
            sent_idx = bisect.bisect_right(sent_start_chars, char_pos) - 1
            if 0 <= sent_idx < len(sentences):
                lo = max(0, sent_idx - window_back)
                hi = min(len(sentences), sent_idx + window_fwd + 1)
                matched_idx.update(range(lo, hi))
                hits.append((sent_idx, finder.__name__, hit))

    mask = [i in matched_idx for i in range(len(sentences))]
    matched_ix = sorted(matched_idx)
    matched_sents = [sentences[i] for i in matched_ix]
    notmatched_sents = [s for i, s in enumerate(sentences) if i not in matched_idx]

    return SplitResult(
        matched=" ".join(matched_sents).strip(),
        notmatched=" ".join(notmatched_sents).strip(),
        sentences=sentences,
        mask=mask,
        matched_ix=matched_ix,
        hits=hits,
    )
