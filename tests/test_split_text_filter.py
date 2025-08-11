"""Unit tests for pyregularexpression.split_text_filter (enhanced version).

Run with::

    pytest -q test_split_text_filter.py
"""
from __future__ import annotations

import importlib
from typing import List, Tuple

import pytest
from nltk.tokenize import sent_tokenize

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
        "The study protocol was approved by the institutional review board. "
        "The algorithm validation was performed using cross-validation. "
        "Patients with ICD-10 code G47.33 were included. "
        "Sentence B unrelated. "
        "Those lost to follow-up were recorded in 5% of cases."
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
    assert "G47.33" in out.matched
    assert "algorithm validation" in out.matched
    assert "lost to follow-up" in out.matched.lower()
    assert "G47.33" not in out.notmatched

    # The sentences are:
    # 0: "The study protocol was approved by the institutional review board."
    # 1: "The algorithm validation was performed using cross-validation."
    # 2: "Patients with ICD-10 code G47.33 were included."
    # 3: "Sentence B unrelated."
    # 4: "Those lost to follow-up were recorded in 5% of cases."
    # Hits should be in sentences 1, 2, and 4.
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
    assert "The study protocol was approved by the institutional review board." in out.matched, "Previous sentence not included by window_back=1"


def test_window_fwd_includes_next_sentence(sample_text):
    out = _run(sample_text, fwd=1)
    # Match "I60" is in sentence 2: "Patients with ICD-10 code I60 were included."
    # The next sentence is "Sentence B unrelated."
    assert "Sentence B unrelated." in out.matched


def test_no_sentence_duplication(sample_text):
    out = _run(sample_text, back=1, fwd=1)
    matched_sents = list(out.kept_sentences())
    notmatched_sents = list(out.dropped_sentences())
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


# ──────────────────────────────────────────────────────────
# Additional robustness tests
# ──────────────────────────────────────────────────────────

def test_empty_text():
    out = split_text_by_filter("", [find_medical_code_v1])
    assert out.matched == ""
    assert out.notmatched == ""
    assert out.sentences == []
    assert out.mask == []
    assert out.matched_ix == []
    assert out.hits == []


def test_no_finders(sample_text):
    out = split_text_by_filter(sample_text, [])
    assert out.matched == ""
    # The original text is returned in notmatched, with sentences joined by space
    assert out.notmatched.strip() == " ".join(sent_tokenize(sample_text))
    assert len(out.sentences) > 0
    assert not any(out.mask)
    assert out.matched_ix == []
    assert out.hits == []


def test_finder_returns_empty_list(sample_text):
    def no_op_finder(text: str):
        return []
    out = split_text_by_filter(sample_text, [no_op_finder])
    assert out.matched == ""
    assert out.notmatched.strip() == " ".join(sent_tokenize(sample_text))
    assert len(out.sentences) > 0
    assert not any(out.mask)
    assert out.matched_ix == []
    assert out.hits == []


def test_overlapping_matches():
    text = "Another sentence. Sentence B with ICD-10 G47.33. Sentence C."
    def find_b_with(text: str) -> List[Tuple[int, int, str]]:
        if "B with" in text:
            # tokens are: 'Another', 'sentence.', 'Sentence', 'B', 'with', 'ICD-10', 'G47.33.', 'Sentence', 'C.'
            # "B with" corresponds to tokens 3 and 4
            return [(4, 5, "B with")]
        return []

    # `find_medical_code_v1` will also match on "G47.33" in the same sentence.
    # The sentence should only be included once.
    out = split_text_by_filter(text, [find_medical_code_v1, find_b_with])
    assert out.matched_ix == [1]
    assert "Sentence B with ICD-10 G47.33." in out.matched
    assert "Another sentence." not in out.matched
    assert "Sentence C." not in out.matched


def test_match_at_beginning_of_text():
    text = "G47.33 is a code. Sentence B."
    out = split_text_by_filter(text, [find_medical_code_v1])
    assert out.matched_ix == [0]
    assert "G47.33 is a code." in out.matched
    assert "Sentence B." not in out.matched


def test_match_at_end_of_text():
    text = "Another sentence. The code is G47.33."
    out = split_text_by_filter(text, [find_medical_code_v1])
    assert out.matched_ix == [1]
    assert "The code is G47.33." in out.matched
    assert "Another sentence." not in out.matched


def test_windowing_at_edges():
    text = "Sentence 1. Sentence 2. Sentence 3. Sentence 4. Sentence 5."
    def find_s3(text: str) -> List[Tuple[int, int, str]]:
        if "Sentence 3" in text:
            # tokens: 'Sentence', '1.', 'Sentence', '2.', 'Sentence', '3.', ...
            # "Sentence 3" is at token 4 and 5
            return [(4, 5, "Sentence 3")]
        return []

    # Window back larger than available sentences
    out = split_text_by_filter(text, [find_s3], window_back=10)
    assert out.matched_ix == [0, 1, 2] # Sentences 1, 2, 3

    # Window forward larger than available sentences
    out = split_text_by_filter(text, [find_s3], window_fwd=10)
    assert out.matched_ix == [2, 3, 4] # Sentences 3, 4, 5

    # Window both directions
    out = split_text_by_filter(text, [find_s3], window_back=1, window_fwd=1)
    assert out.matched_ix == [1, 2, 3] # Sentences 2, 3, 4


def test_finder_with_invalid_span():
    text = "A sentence."
    def find_invalid(text: str) -> List[Tuple[int, int, str]]:
        # w_start > w_end, w_start out of bounds, w_start < 0
        return [(2, 1, "invalid"), (100, 101, "invalid"), (-1, 0, "invalid")]

    out = split_text_by_filter(text, [find_invalid])
    assert out.matched == ""
    assert out.notmatched == "A sentence."
