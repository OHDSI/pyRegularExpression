"""Unit tests for pyregularexpression.split_text_filter (enhanced version).

Run with::

    pytest -q test_split_text_filter.py
"""
from __future__ import annotations

import importlib
from typing import List

import pytest
from nltk.tokenize import sent_tokenize  # ensures sentence boundaries match helper

# Runtime import because the library lives in the editable src tree during CI
split_mod = importlib.import_module("pyregularexpression.split_text_filter")

split_text_by_filter = split_mod.split_text_by_filter

from pyregularexpression.medical_code_finder import find_medical_code_v1  # type: ignore
from pyregularexpression.algorithm_validation_finder import find_algorithm_validation_v1  # type: ignore
from pyregularexpression.attrition_criteria_finder import find_attrition_criteria_v1  # type: ignore

FINDERS = [
    find_medical_code_v1,
    find_algorithm_validation_v1,
    find_attrition_criteria_finder := find_attrition_criteria_v1,
]


@pytest.fixture(scope="module")
def sample_text() -> str:
    """Synthetic mini‑article covering all three finder categories."""
    return (
        "First sentence. The algorithm validation was performed using cross-validation. "
        "Patients with ICD-10 code I60 were included. "
        "Sentence B unrelated. "
        "Lost to follow-up was recorded in 5% of cases."
    )


def _run(text: str, back: int = 0, fwd: int = 0):
    return split_text_by_filter(text, FINDERS, window_back=back, window_fwd=fwd)


# ──────────────────────────────────────────────────────────
# Positive / negative basic behaviour
# ──────────────────────────────────────────────────────────

def test_no_match_returns_all_unmatched():
    out = split_text_by_filter("Nothing special here.", [find_medical_code_v1])
    assert out.matched == ""
    assert out.notmatched == "Nothing special here."


def test_basic_matches(sample_text):
    out = _run(sample_text)
    # Basic keyword checks
    assert "I60" in out.matched
    assert "algorithm validation" in out.matched
    assert "Lost to follow-up" in out.matched
    assert "I60" not in out.notmatched
    # The sentences are: 0='Sentence A.', 1='The algorithm...', 2='Patients with...',
    # 3='Sentence B...', 4='Lost to follow-up...'.
    # With correct sentence tokenization, hits should be in sentences 1, 2, and 4.
    # Note: find_medical_code_v1 may find "A." as a code, so we accept sentence 0 as well.
    # After further review, "A." is not a valid medical code, so sentence 0 should not be matched.
    assert out.matched_ix == [1, 2, 4]
    assert out.mask == [False, True, True, False, True]
    # There are 3 finders, but find_algorithm_validation_v1 finds multiple things.
    # Let's check the finder names in the hits.
    finder_names = {h[1] for h in out.hits}
    assert finder_names == {
        "find_algorithm_validation_v1",
        "find_medical_code_v1",
        "find_attrition_criteria_v1",
    }


# ──────────────────────────────────────────────────────────
# Context window logic
# ──────────────────────────────────────────────────────────

def test_window_back_includes_previous_sentence(sample_text):
    out = _run(sample_text, back=1)
    assert "First sentence." in out.matched, "Previous sentence not included by window_back=1"


def test_window_fwd_includes_next_sentence(sample_text):
    out = _run(sample_text, fwd=1)
    # Match "I60" is in sentence 2: "Patients with ICD-10 code I60 were included."
    # The next sentence is "Sentence B unrelated."
    assert "Sentence B unrelated." in out.matched


def test_no_sentence_duplication(sample_text):
    out = _run(sample_text, back=1, fwd=1)
    matched_sents: List[str] = sent_tokenize(out.matched)
    notmatched_sents: List[str] = sent_tokenize(out.notmatched)
    overlap = set(matched_sents).intersection(notmatched_sents)
    assert not overlap, f"Sentences duplicated across splits: {overlap}"


def test_match_spanning_sentences():
    text = "Sentence one. A phrase that spans. More of the phrase. Sentence three."
    # Tokens (`\S+`):
    # 0=Sentence, 1=one., 2=A, 3=phrase, 4=that, 5=spans.,
    # 6=More, 7=of, 8=the, 9=phrase., 10=Sentence, 11=three.
    # Sentences:
    # "Sentence one."
    # "A phrase that spans."
    # "More of the phrase."
    # "Sentence three."

    def find_spanning_match(text: str) -> List[Tuple[int, int, str]]:
        if "spans. More" in text:
            # Corresponds to tokens 5 ("spans.") and 6 ("More").
            # The end index from finders is inclusive.
            return [(5, 6, "spans. More")]
        return []

    out = split_text_by_filter(text, [find_spanning_match])
    assert "A phrase that spans." in out.matched
    assert "More of the phrase." in out.matched
    assert "Sentence one." not in out.matched
    assert "Sentence three." not in out.matched
