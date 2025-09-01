import pytest
from pyregularexpression.apply_regex_functions import apply_regex_funcs

def find_a(text):
    return [(0, 1, 'a')] if 'a' in text else []

def find_b(text):
    return [(1, 2, 'b')] if 'b' in text else []

def find_c_with_arg(text, arg=None):
    return [(2, 3, 'c')] if 'c' in text else []

def test_apply_regex_funcs_multiple_matches():
    text = "abc"
    funcs = [find_a, find_b]
    result = apply_regex_funcs(text, funcs)
    assert result['any_match'] is True
    assert 'find_a' in result['matches']
    assert 'find_b' in result['matches']
    assert result['matches']['find_a'] == [(0, 1, 'a')]
    assert result['matches']['find_b'] == [(1, 2, 'b')]

def test_apply_regex_funcs_single_match():
    text = "a"
    funcs = [find_a, find_b]
    result = apply_regex_funcs(text, funcs)
    assert result['any_match'] is True
    assert 'find_a' in result['matches']
    assert 'find_b' in result['matches']
    assert result['matches']['find_a'] == [(0, 1, 'a')]
    assert result['matches']['find_b'] == []

def test_apply_regex_funcs_no_match():
    text = "xyz"
    funcs = [find_a, find_b]
    result = apply_regex_funcs(text, funcs)
    assert result['any_match'] is False
    assert result['matches']['find_a'] == []
    assert result['matches']['find_b'] == []

def test_apply_regex_funcs_empty_text():
    text = ""
    funcs = [find_a, find_b]
    result = apply_regex_funcs(text, funcs)
    assert result['any_match'] is False

def test_apply_regex_funcs_empty_funcs():
    text = "abc"
    funcs = []
    result = apply_regex_funcs(text, funcs)
    assert result['any_match'] is False
    assert result['matches'] == {}

def test_apply_regex_funcs_type_error_handling():
    text = "abc"
    # This function requires an additional argument and will raise a TypeError
    def find_d_requires_arg(text, required_arg):
        return [(3, 4, 'd')] if 'd' in text else []

    funcs = [find_a, find_d_requires_arg]

    # The current implementation has a bug where it catches TypeError and retries
    # the same call, which will fail again. A robust implementation might skip
    # the function or log an error. For now, we test the buggy behavior.
    with pytest.raises(TypeError):
        apply_regex_funcs(text, funcs)
