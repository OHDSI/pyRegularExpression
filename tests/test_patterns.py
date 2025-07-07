"""Basic sanity tests for shipped patterns."""

from pyregularexpression import patterns
import pytest

@pytest.mark.parametrize(
    "address",
    [
        "user@example.com",
        "info@sub.example.co.uk",
    ],
)
def test_email_valid(address):
    assert patterns.EMAIL.fullmatch(address)

@pytest.mark.parametrize(
    "address",
    [
        "user@example",
        "user@.com",
        "@example.com",
    ],
)
def test_email_invalid(address):
    assert patterns.EMAIL.fullmatch(address) is None
