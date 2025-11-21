"""Tests for parameter alias detection helpers in param.py.

Covers is_short_alias and is_long_alias_with_value functions.
"""
from spafw37 import param

def setup_function():
    param._param_aliases.clear()
    param._params.clear()
    param._preparse_args.clear()
    try:
        param._xor_list.clear()
    except Exception:
        pass

def test_is_short_alias_true():
    """Test is_short_alias returns True for short aliases.
    Short aliases match the pattern -x where x is a single character.
    """
    setup_function()
    assert param.is_short_alias('-v') is True
    assert param.is_short_alias('-x') is True

def test_is_short_alias_false():
    """Test is_short_alias returns False for non-short aliases.
    Long aliases and regular strings should not match short alias pattern.
    """
    setup_function()
    assert param.is_short_alias('--verbose') is False
    assert param.is_short_alias('value') is False

def test_is_long_alias_with_value_true():
    """Test is_long_alias_with_value for --param=value format.
    Should return True when alias has embedded value.
    """
    setup_function()
    assert param.is_long_alias_with_value('--param=value') is True
    assert param.is_long_alias_with_value('--count=42') is True

def test_is_long_alias_with_value_false():
    """Test is_long_alias_with_value for other formats.
    Should return False when no embedded value.
    """
    setup_function()
    assert param.is_long_alias_with_value('--param') is False
    assert param.is_long_alias_with_value('value') is False
