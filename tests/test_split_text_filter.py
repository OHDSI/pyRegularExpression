"""Unit tests for pyregularexpression.split_text_filter (enhanced version).

Run with::

    pytest -q test_split_text_filter.py
"""
from __future__ import annotations

import importlib
from typing import List

import pytest
from nltk.tokenize import sent_tokenize  # ensures sentence boundaries match helper

import nltk
nltk.download('punkt')
nltk.download('punkt_tab') 

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
        "Sentence A. The algorithm validation was performed using cross‑validation. "
        "Patients with ICD‑10 code I60 were included. "
        "Sentence B unrelated. "
        "Lost to follow‑up was recorded in 5% of cases."
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
    # Should retain keywords from each finder
    assert "I60" in out.matched
    assert "algorithm validation" in out.matched
    assert "Lost to follow‑up" in out.matched
    # Ensure removed region truly lacks matched keywords
    assert "I60" not in out.notmatched


# ──────────────────────────────────────────────────────────
# Context window logic
# ──────────────────────────────────────────────────────────

def test_window_back_includes_previous_sentence(sample_text):
    out = _run(sample_text, back=1)
    assert "Sentence A." in out.matched, "Previous sentence not included by window_back=1"


def test_no_sentence_duplication(sample_text):
    out = _run(sample_text, back=1, fwd=1)
    matched_sents: List[str] = sent_tokenize(out.matched)
    notmatched_sents: List[str] = sent_tokenize(out.notmatched)
    overlap = set(matched_sents).intersection(notmatched_sents)
    assert not overlap, f"Sentences duplicated across splits: {overlap}"
