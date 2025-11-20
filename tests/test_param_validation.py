"""Tests for parameter validation helpers in param.py.

Tests the type-specific validation functions (_validate_number, _validate_toggle,
_validate_list, _validate_dict, _validate_text) that coerce and validate parameter
values according to their declared types.
"""
import pytest
from spafw37 import param
from spafw37.constants.param import PARAM_DEFAULT


def setup_function():
    """Reset param state before each test to ensure isolation."""
    param._params.clear()
    param._param_aliases.clear()
    param._xor_list.clear()


# Tests for _validate_number()
def test_validate_number_int_string():
    """Test _validate_number coerces integer string to int.
    
    Should convert string '42' to integer 42.
    This validates that integer string coercion works.
    """
    result = param._validate_number('42')
    assert result == 42
    assert isinstance(result, int)


def test_validate_number_float_string():
    """Test _validate_number coerces float string to float.
    
    Should convert string '3.14' to float 3.14.
    This validates that float string coercion works.
    """
    result = param._validate_number('3.14')
    assert result == 3.14
    assert isinstance(result, float)


def test_validate_number_int_value():
    """Test _validate_number accepts int value as-is.
    
    Should return integer value unchanged.
    This validates that numeric types pass through.
    """
    result = param._validate_number(10)
    assert result == 10
    assert isinstance(result, int)


def test_validate_number_float_value():
    """Test _validate_number accepts float value as-is.
    
    Should return float value unchanged.
    This validates that numeric types pass through.
    """
    result = param._validate_number(2.5)
    assert result == 2.5
    assert isinstance(result, float)


def test_validate_number_invalid_string_raises():
    """Test _validate_number raises ValueError for non-numeric string.
    
    Should raise ValueError when string cannot be coerced to number.
    This validates that invalid input is rejected with clear error.
    """
    with pytest.raises(ValueError, match="Cannot coerce value to number"):
        param._validate_number('not-a-number')


def test_validate_number_empty_string_raises():
    """Test _validate_number raises ValueError for empty string.
    
    Should raise ValueError when string is empty.
    This validates that edge case inputs are handled.
    """
    with pytest.raises(ValueError, match="Cannot coerce value to number"):
        param._validate_number('')


# Tests for _validate_toggle()
def test_validate_toggle_default_false():
    """Test _validate_toggle flips False default to True.
    
    Should return True when default is False.
    This validates that toggle flips the default value.
    """
    param_def = {PARAM_DEFAULT: False}
    result = param._validate_toggle(param_def)
    assert result is True


def test_validate_toggle_default_true():
    """Test _validate_toggle flips True default to False.
    
    Should return False when default is True.
    This validates that toggle flips the default value.
    """
    param_def = {PARAM_DEFAULT: True}
    result = param._validate_toggle(param_def)
    assert result is False


def test_validate_toggle_no_default():
    """Test _validate_toggle returns True when no default specified.
    
    Should return True (flipped from implicit False default).
    This validates that missing default is treated as False.
    """
    param_def = {}
    result = param._validate_toggle(param_def)
    assert result is True


# Tests for _validate_list()
def test_validate_list_list_value():
    """Test _validate_list returns list value unchanged.
    
    Should return list as-is when value is already a list.
    This validates that list values pass through.
    """
    result = param._validate_list(['a', 'b', 'c'])
    assert result == ['a', 'b', 'c']


def test_validate_list_string_value():
    """Test _validate_list wraps string in list.
    
    Should return single-item list containing the string.
    This validates that non-list values are wrapped.
    """
    result = param._validate_list('single-value')
    assert result == ['single-value']


def test_validate_list_int_value():
    """Test _validate_list wraps int in list.
    
    Should return single-item list containing the int.
    This validates that non-list values are wrapped.
    """
    result = param._validate_list(42)
    assert result == [42]


def test_validate_list_empty_list():
    """Test _validate_list returns empty list unchanged.
    
    Should return empty list as-is.
    This validates that edge case inputs are handled.
    """
    result = param._validate_list([])
    assert result == []


# Tests for _validate_dict()
def test_validate_dict_dict_value():
    """Test _validate_dict returns dict value unchanged.
    
    Should return dict as-is when value is already a dict.
    This validates that dict values pass through.
    """
    test_dict = {'key': 'value', 'number': 42}
    result = param._validate_dict(test_dict)
    assert result == test_dict


def test_validate_dict_json_string():
    """Test _validate_dict parses JSON string.
    
    Should parse JSON object string into dict.
    This validates that JSON string parsing works.
    """
    result = param._validate_dict('{"key": "value", "number": 42}')
    assert result == {'key': 'value', 'number': 42}


def test_validate_dict_json_string_with_whitespace():
    """Test _validate_dict parses JSON string with whitespace.
    
    Should parse JSON object string with extra whitespace.
    This validates that JSON parsing handles formatting variations.
    """
    result = param._validate_dict('  {"key": "value"}  ')
    assert result == {'key': 'value'}


def test_validate_dict_invalid_json_raises():
    """Test _validate_dict raises ValueError for invalid JSON.
    
    Should raise ValueError when JSON string is malformed.
    This validates that invalid JSON is rejected with clear error.
    """
    with pytest.raises(ValueError, match="Invalid JSON"):
        param._validate_dict('{"key": invalid}')


def test_validate_dict_non_dict_string_raises():
    """Test _validate_dict raises ValueError for non-dict string.

    Should raise ValueError when string is invalid JSON.
    This validates that non-JSON strings are rejected.
    """
    with pytest.raises(ValueError, match="Invalid JSON"):
        param._validate_dict('not-json')


def test_validate_dict_empty_string_raises():
    """Test _validate_dict raises ValueError for empty string.

    Should raise ValueError when string is empty.
    This validates that edge case inputs are handled.
    """
    with pytest.raises(ValueError, match="Invalid JSON"):
        param._validate_dict('')


def test_validate_dict_array_json_raises():
    """Test _validate_dict raises ValueError for array JSON.

    Should raise ValueError when JSON is valid but not an object.
    This validates that non-dict JSON types are rejected.
    """
    with pytest.raises(ValueError, match="requires JSON object"):
        param._validate_dict('[1, 2, 3]')


# Tests for _validate_text()
def test_validate_text_string_value():
    """Test _validate_text returns string value unchanged.
    
    Should return string as-is when value is already a string.
    This validates that string values pass through.
    """
    result = param._validate_text('hello world')
    assert result == 'hello world'


def test_validate_text_int_value():
    """Test _validate_text converts int to string.
    
    Should convert integer to string representation.
    This validates that non-string values are coerced.
    """
    result = param._validate_text(123)
    assert result == '123'
    assert isinstance(result, str)


def test_validate_text_float_value():
    """Test _validate_text converts float to string.
    
    Should convert float to string representation.
    This validates that non-string values are coerced.
    """
    result = param._validate_text(3.14)
    assert result == '3.14'
    assert isinstance(result, str)


def test_validate_text_empty_string():
    """Test _validate_text returns empty string unchanged.
    
    Should return empty string as-is.
    This validates that edge case inputs are handled.
    """
    result = param._validate_text('')
    assert result == ''
