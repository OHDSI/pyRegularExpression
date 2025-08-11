"""Tests for random_sequence_generation_finder."""
import pytest
from pyregularexpression.random_sequence_generation_finder import (
    find_random_sequence_generation_v1,
    find_random_sequence_generation_v2,
    find_random_sequence_generation_v3,
    find_random_sequence_generation_v4,
    find_random_sequence_generation_v5,
    RANDOM_SEQUENCE_GENERATION_FINDERS,
)

# Positive examples
HIT_BLOCK = "The allocation sequence was computer-generated using block randomization with block size = 4."
HIT_COIN = "Participants were assigned by a coin toss sequence."
HIT_ENVELOPES = "Allocation was carried out by shuffling sealed opaque envelopes."
HIT_PERMUTED_BLOCK = "We used a permuted block design for the allocation sequence."
HIT_STRATIFIED = "The study employed stratified randomization based on clinical site."

# Negative examples (should not match)
MISS_RANDOMLY = "Participants were randomly selected from the registry."
MISS_RANDOM_EFFECTS = "We fitted a random-effects model to the data."
MISS_RANDOM_SAMPLING = "The study used a random sampling technique."

@pytest.mark.parametrize(
    "text, expected_fns",
    [
        (HIT_BLOCK, ["v1", "v2", "v4", "v5"]),
        (HIT_COIN, ["v1", "v2"]),
        (HIT_ENVELOPES, ["v1", "v2"]),
        (HIT_PERMUTED_BLOCK, ["v1", "v2", "v4"]),
        (HIT_STRATIFIED, ["v1", "v2", "v4"]),
    ],
)
def test_positive_hits(text, expected_fns):
    """Test that the finder functions find matches in positive examples."""
    for name, fn in RANDOM_SEQUENCE_GENERATION_FINDERS.items():
        if name in expected_fns:
            assert fn(text), f"{name} failed to find a match in: {text}"
        else:
            assert not fn(text), f"{name} unexpectedly found a match in: {text}"


@pytest.mark.parametrize(
    "text", [MISS_RANDOMLY, MISS_RANDOM_EFFECTS, MISS_RANDOM_SAMPLING]
)
def test_negative_misses(text):
    """Test that the finder functions do not find matches in negative examples."""
    for name, fn in RANDOM_SEQUENCE_GENERATION_FINDERS.items():
        assert not fn(text), f"{name} found a match in negative example: {text}"


# A more complex case for v3
HEADING_EXAMPLE = """
Randomisation
The allocation sequence was computer-generated.
"""

def test_v3_with_heading():
    """v3 should find a match when a heading is present."""
    assert find_random_sequence_generation_v3(HEADING_EXAMPLE)
