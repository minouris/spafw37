"""Tests for parameter validation helpers in param.py.

Tests the type-specific validation functions (_validate_number, _validate_toggle,
_validate_list, _validate_dict, _validate_text) that coerce and validate parameter
values according to their declared types.
"""
import pytest
from spafw37 import config, param
from spafw37.constants.param import (
    PARAM_ALLOWED_VALUES,
    PARAM_DEFAULT,
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_DICT,
    PARAM_TYPE_LIST,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_TOGGLE,
)


def setup_function():
    """Reset param state before each test to ensure isolation."""
    param._params.clear()
    param._param_aliases.clear()
    param._xor_list.clear()
    config._config.clear()


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
# Tests for _validate_toggle removed as function was deleted
# Toggle validation is now handled inline in set_param_value()

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


def test_validate_allowed_values_text_valid():
    """Test that the _validate_allowed_values helper accepts valid TEXT parameter values.
    
    This test verifies that when a TEXT parameter has PARAM_ALLOWED_VALUES defined,
    values that are members of the allowed list pass validation without raising errors.
    This behaviour is expected because valid values should not be rejected by the whitelist.
    """
    setup_function()
    param_def = {
        PARAM_NAME: 'environment',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALLOWED_VALUES: ['dev', 'staging', 'production']
    }
    # Should not raise
    param._validate_allowed_values(param_def, 'dev')
    param._validate_allowed_values(param_def, 'staging')
    param._validate_allowed_values(param_def, 'production')


def test_validate_allowed_values_text_invalid():
        """Test that the _validate_allowed_values helper rejects invalid TEXT parameter values.
        
        This test verifies that when a TEXT parameter has PARAM_ALLOWED_VALUES defined,
        values that are not in the allowed list are rejected with a clear ValueError.
        This behaviour is expected because invalid values must be rejected to enforce the whitelist constraint.
        """
        setup_function()
        param_def = {
            PARAM_NAME: 'environment',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALLOWED_VALUES: ['dev', 'staging', 'production']
        }
        with pytest.raises(ValueError, match="Value 'test' not allowed for parameter 'environment'"):
            param._validate_allowed_values(param_def, 'test')
    
def test_validate_allowed_values_list_valid():
    """Test that the _validate_allowed_values helper accepts valid LIST parameter elements.
    
    This test verifies that when a LIST parameter has PARAM_ALLOWED_VALUES defined,
    lists where all elements are members of the allowed list pass validation without errors.
    This behaviour is expected because valid list elements should not be rejected by the whitelist.
    """
    setup_function()
    param_def = {
        PARAM_NAME: 'features',
        PARAM_TYPE: PARAM_TYPE_LIST,
        PARAM_ALLOWED_VALUES: ['auth', 'api', 'database', 'cache']
    }
    # Should not raise
    param._validate_allowed_values(param_def, ['auth', 'api'])
    param._validate_allowed_values(param_def, ['database'])
    
def test_validate_allowed_values_list_invalid_element():
    """Test that the _validate_allowed_values helper rejects LIST parameters with invalid elements.
    
    This test verifies that when a LIST parameter has PARAM_ALLOWED_VALUES defined,
    lists containing any element not in the allowed list are rejected with a clear ValueError.
    This behaviour is expected because all elements must be valid to enforce the whitelist constraint.
    """
    setup_function()
    param_def = {
        PARAM_NAME: 'features',
        PARAM_TYPE: PARAM_TYPE_LIST,
        PARAM_ALLOWED_VALUES: ['auth', 'api', 'database', 'cache']
    }
    with pytest.raises(ValueError, match="List element 'invalid' not allowed for parameter 'features'"):
        param._validate_allowed_values(param_def, ['auth', 'invalid'])
    
def test_validate_allowed_values_list_empty():
    """Test that the _validate_allowed_values helper rejects empty LIST parameters.
    
    This test verifies that when a LIST parameter has PARAM_ALLOWED_VALUES defined,
    empty lists are rejected with a clear ValueError indicating at least one valid value must be provided.
    This behaviour is expected because empty lists provide no valid configuration when allowed values are specified.
    """
    setup_function()
    param_def = {
        PARAM_NAME: 'features',
        PARAM_TYPE: PARAM_TYPE_LIST,
        PARAM_ALLOWED_VALUES: ['auth', 'api', 'database', 'cache']
    }
    with pytest.raises(ValueError, match="Empty list not allowed for parameter 'features'"):
        param._validate_allowed_values(param_def, [])
    
def test_validate_allowed_values_number_valid():
    """Test that the _validate_allowed_values helper accepts valid NUMBER parameter values.
    
    This test verifies that when a NUMBER parameter has PARAM_ALLOWED_VALUES defined,
    values that are members of the allowed list pass validation without raising errors.
    This behaviour is expected because valid numeric values should not be rejected by the whitelist.
    """
    setup_function()
    param_def = {
        PARAM_NAME: 'port',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_ALLOWED_VALUES: [80, 443, 8080, 8443]
    }
    # Should not raise
    param._validate_allowed_values(param_def, 80)
    param._validate_allowed_values(param_def, 443)
    
def test_validate_allowed_values_number_invalid():
    """Test that the _validate_allowed_values helper rejects invalid NUMBER parameter values.
    
    This test verifies that when a NUMBER parameter has PARAM_ALLOWED_VALUES defined,
    values that are not in the allowed list are rejected with a clear ValueError.
    This behaviour is expected because invalid numeric values must be rejected to enforce the whitelist constraint.
    """
    setup_function()
    param_def = {
        PARAM_NAME: 'port',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_ALLOWED_VALUES: [80, 443, 8080, 8443]
    }
    with pytest.raises(ValueError, match="Value 3000 not allowed for parameter 'port'"):
        param._validate_allowed_values(param_def, 3000)
    
def test_validate_allowed_values_not_specified():
    """Test that the _validate_allowed_values helper skips validation when PARAM_ALLOWED_VALUES is not specified.
    
    This test verifies that when a parameter does not have PARAM_ALLOWED_VALUES defined,
    any value is accepted without validation or errors being raised.
    This behaviour is expected because the allowed values constraint is optional and should not affect parameters that don't use it.
    """
    setup_function()
    param_def = {
        PARAM_NAME: 'value',
        PARAM_TYPE: PARAM_TYPE_TEXT
    }
    # Should not raise - no allowed values constraint
    param._validate_allowed_values(param_def, 'anything')
    
def test_validate_allowed_values_toggle_ignored():
    """Test that the _validate_allowed_values helper skips validation for TOGGLE parameters.
    
    This test verifies that TOGGLE parameters do not have allowed values validation applied,
    even when PARAM_ALLOWED_VALUES is specified in the parameter definition.
    This behaviour is expected because TOGGLE parameters have implicit allowed values (True/False) and do not require explicit validation.
    """
    setup_function()
    param_def = {
        PARAM_NAME: 'flag',
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_ALLOWED_VALUES: [True]  # This should be ignored
    }
    # Should not raise - toggles skip validation
    param._validate_allowed_values(param_def, False)
    
def test_normalise_allowed_value_text():
    """Test that the _normalise_allowed_value helper normalises TEXT values to canonical case.
    
    This test verifies that TEXT parameter values are normalised to the exact canonical case
    from the PARAM_ALLOWED_VALUES list, regardless of input case.
    This behaviour is expected to provide consistent canonical case storage for TEXT parameters.
    """
    setup_function()
    param_def = {
        PARAM_NAME: 'log_level',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALLOWED_VALUES: ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    }
    assert param._normalise_allowed_value(param_def, 'debug') == 'DEBUG'
    assert param._normalise_allowed_value(param_def, 'INFO') == 'INFO'
    assert param._normalise_allowed_value(param_def, 'WaRnInG') == 'WARNING'
    
def test_normalise_allowed_value_text_mixed_case():
    """Test that the _normalise_allowed_value helper preserves mixed-case canonical values.
    
    This test verifies that when allowed values contain mixed-case strings (e.g., 'Alice'),
    any case variant of the input is normalised to the exact canonical case from the allowed list.
    This behaviour is expected to preserve proper names and other case-sensitive display values.
    """
    setup_function()
    param_def = {
        PARAM_NAME: 'username',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALLOWED_VALUES: ['Alice', 'Bob', 'Charlie', 'Dave']
    }
    assert param._normalise_allowed_value(param_def, 'alice') == 'Alice'
    assert param._normalise_allowed_value(param_def, 'DAVE') == 'Dave'
    assert param._normalise_allowed_value(param_def, 'BoB') == 'Bob'
    
def test_normalise_allowed_value_list():
    """Test that the _normalise_allowed_value helper normalises LIST elements to canonical case.
    
    This test verifies that LIST parameter elements are normalised to the exact canonical case
    from the PARAM_ALLOWED_VALUES list, returning a list with normalised elements.
    This behaviour is expected to provide consistent canonical case storage for LIST elements.
    """
    setup_function()
    param_def = {
        PARAM_NAME: 'features',
        PARAM_TYPE: PARAM_TYPE_LIST,
        PARAM_ALLOWED_VALUES: ['AUTH', 'API', 'DATABASE', 'CACHE']
    }
    result = param._normalise_allowed_value(param_def, ['auth', 'database'])
    assert result == ['AUTH', 'DATABASE']
    
def test_normalise_allowed_value_list_mixed_case():
    """Test that the _normalise_allowed_value helper preserves mixed-case canonical values in lists.
    
    This test verifies that when LIST allowed values contain mixed-case strings,
    list elements are normalised to the exact canonical case from the allowed list.
    This behaviour is expected to preserve proper names and other case-sensitive display values in lists.
    """
    setup_function()
    param_def = {
        PARAM_NAME: 'team_members',
        PARAM_TYPE: PARAM_TYPE_LIST,
        PARAM_ALLOWED_VALUES: ['Alice', 'Bob', 'Charlie', 'Dave']
    }
    result = param._normalise_allowed_value(param_def, ['alice', 'DAVE', 'BoB'])
    assert result == ['Alice', 'Dave', 'Bob']
    
def test_normalise_allowed_value_number():
    """Test that the _normalise_allowed_value helper returns NUMBER values unchanged.
    
    This test verifies that NUMBER parameter values are returned without modification
    since numeric values do not require case normalisation.
    This behaviour is expected because NUMBER values are exact matches and need no transformation.
    """
    setup_function()
    param_def = {
        PARAM_NAME: 'port',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_ALLOWED_VALUES: [80, 443, 8080, 8443]
    }
    assert param._normalise_allowed_value(param_def, 80) == 80
    assert param._normalise_allowed_value(param_def, 443) == 443
    
def test_normalise_allowed_value_not_specified():
    """Test that the _normalise_allowed_value helper returns values unchanged when no allowed values specified.
    
    This test verifies that when PARAM_ALLOWED_VALUES is not defined,
    values are returned without any transformation.
    This behaviour is expected because normalisation only applies when allowed values are specified.
    """
    setup_function()
    param_def = {
        PARAM_NAME: 'value',
        PARAM_TYPE: PARAM_TYPE_TEXT
    }
    assert param._normalise_allowed_value(param_def, 'anything') == 'anything'
    assert param._normalise_allowed_value(param_def, 'AnyCase') == 'AnyCase'
    
def test_set_param_with_allowed_values_valid():
    """Test that set_param successfully sets a parameter when the value is in the allowed values list.
    
    This test verifies that the set_param function accepts and stores valid values when
    a parameter has PARAM_ALLOWED_VALUES defined and the provided value is in that list.
    This behaviour is expected because valid values should pass through the validation pipeline and be stored correctly.
    """
    setup_function()
    param.add_param({
        PARAM_NAME: 'mode',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALLOWED_VALUES: ['fast', 'normal', 'slow'],
        PARAM_DEFAULT: 'normal'
    })
    # Should not raise
    param.set_param(param_name='mode', value='fast')
    assert param.get_param(param_name='mode') == 'fast'
    
def test_set_param_with_allowed_values_case_insensitive():
    """Test that set_param normalises TEXT parameter values to canonical case.
    
    This test verifies that the set_param function performs case-insensitive matching and stores
    values in the canonical case from the allowed values list for TEXT parameters.
    This behaviour is expected because users should not need to match exact case, and canonical case ensures consistency.
    """
    setup_function()
    param.add_param({
        PARAM_NAME: 'log_level',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALLOWED_VALUES: ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    })
    # lowercase input normalised to uppercase canonical case
    param.set_param(param_name='log_level', value='debug')
    assert param.get_param(param_name='log_level') == 'DEBUG'
    
    param.set_param(param_name='log_level', value='WaRnInG')
    assert param.get_param(param_name='log_level') == 'WARNING'
    
def test_set_param_list_with_allowed_values_valid():
    """Test that set_param successfully sets a LIST parameter when all elements are in the allowed values list.
    
    This test verifies that the set_param function validates and normalises LIST parameter elements,
    accepting lists where all elements are members of the allowed values list.
    This behaviour is expected because valid list elements should pass validation and be stored with normalised case.
    """
    setup_function()
    param.add_param({
        PARAM_NAME: 'features',
        PARAM_TYPE: PARAM_TYPE_LIST,
        PARAM_ALLOWED_VALUES: ['AUTH', 'API', 'DATABASE', 'CACHE']
    })
    # lowercase elements normalised to uppercase
    param.set_param(param_name='features', value=['auth', 'database'])
    result = param.get_param(param_name='features')
    assert result == ['AUTH', 'DATABASE']
    
def test_set_param_list_invalid_element():
    """Test that set_param raises a ValueError when a LIST parameter contains an invalid element.
    
    This test verifies that the set_param function rejects lists containing any element not in the allowed values list,
    providing a clear error message indicating which element was invalid.
    This behaviour is expected because all list elements must be valid to enforce the whitelist constraint.
    """
    setup_function()
    param.add_param({
        PARAM_NAME: 'features',
        PARAM_TYPE: PARAM_TYPE_LIST,
        PARAM_ALLOWED_VALUES: ['auth', 'api', 'database', 'cache']
    })
    with pytest.raises(ValueError, match="List element 'invalid' not allowed for parameter 'features'"):
        param.set_param(param_name='features', value=['auth', 'invalid'])
    
def test_set_param_list_empty():
    """Test that set_param raises a ValueError when a LIST parameter is set to an empty list.
    
    This test verifies that the set_param function rejects empty lists with a clear error message
    when a parameter has PARAM_ALLOWED_VALUES defined.
    This behaviour is expected because empty lists provide no valid configuration when allowed values are specified.
    """
    setup_function()
    param.add_param({
        PARAM_NAME: 'features',
        PARAM_TYPE: PARAM_TYPE_LIST,
        PARAM_ALLOWED_VALUES: ['auth', 'api', 'database', 'cache']
    })
    with pytest.raises(ValueError, match="Empty list not allowed for parameter 'features'"):
        param.set_param(param_name='features', value=[])
    
def test_set_param_with_allowed_values_invalid():
    """Test that set_param raises a ValueError when the value is not in the allowed values list.
    
    This test verifies that the set_param function rejects invalid values with a clear error message
    when a parameter has PARAM_ALLOWED_VALUES defined and the provided value is not in that list.
    This behaviour is expected because invalid values must be rejected to enforce the whitelist constraint in the full parameter pipeline.
    """
    setup_function()
    param.add_param({
        PARAM_NAME: 'mode',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALLOWED_VALUES: ['fast', 'normal', 'slow']
    })
    with pytest.raises(ValueError, match="Value 'turbo' not allowed for parameter 'mode'"):
        param.set_param(param_name='mode', value='turbo')
    
def test_add_param_default_in_allowed_values():
    """Test that add_param successfully registers a parameter when PARAM_DEFAULT is in the allowed values list.
    
    This test verifies that parameter registration succeeds when both PARAM_DEFAULT and PARAM_ALLOWED_VALUES
    are specified and the default value is a member of the allowed values list.
    This behaviour is expected because valid default values should not prevent parameter registration.
    """
    setup_function()
    # Should not raise
    param.add_param({
        PARAM_NAME: 'level',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_ALLOWED_VALUES: [1, 2, 3, 4, 5],
        PARAM_DEFAULT: 3
    })
    
def test_add_param_default_normalised():
    """Test that add_param normalises TEXT default values to canonical case.
    
    This test verifies that when registering a parameter with both PARAM_DEFAULT and PARAM_ALLOWED_VALUES,
    the default value is normalised to the canonical case from the allowed values list.
    This behaviour is expected because consistent canonical case should be stored for TEXT defaults.
    """
    setup_function()
    param.add_param({
        PARAM_NAME: 'log_level',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALLOWED_VALUES: ['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        PARAM_DEFAULT: 'info'  # lowercase
    })
    # Should be normalised to uppercase in the param definition
    param_def = param._params['log_level']
    assert param_def[PARAM_DEFAULT] == 'INFO'
    
def test_add_param_list_default_normalised():
    """Test that add_param normalises LIST default element values to canonical case.
    
    This test verifies that when registering a LIST parameter with both PARAM_DEFAULT and PARAM_ALLOWED_VALUES,
    all default list elements are normalised to the canonical case from the allowed values list.
    This behaviour is expected because consistent canonical case should be stored for LIST defaults.
    """
    setup_function()
    param.add_param({
        PARAM_NAME: 'features',
        PARAM_TYPE: PARAM_TYPE_LIST,
        PARAM_ALLOWED_VALUES: ['AUTH', 'API', 'DATABASE', 'CACHE'],
        PARAM_DEFAULT: ['auth', 'database']  # lowercase
    })
    # Should be normalised to uppercase in the param definition
    param_def = param._params['features']
    assert param_def[PARAM_DEFAULT] == ['AUTH', 'DATABASE']
    
def test_add_param_default_not_in_allowed_values():
    """Test that add_param raises a ValueError when PARAM_DEFAULT is not in the allowed values list.
    
    This test verifies that parameter registration fails with a clear error message when both PARAM_DEFAULT
    and PARAM_ALLOWED_VALUES are specified but the default value is not in the allowed list.
    This behaviour is expected because misconfigured defaults should be detected early at registration time to prevent runtime errors.
    """
    setup_function()
    with pytest.raises(ValueError, match="Value 10 not allowed for parameter 'level'"):
        param.add_param({
            PARAM_NAME: 'level',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_ALLOWED_VALUES: [1, 2, 3, 4, 5],
            PARAM_DEFAULT: 10
        })
    
def test_set_param_allowed_values_with_number_coercion():
    """Test that allowed values validation occurs after type coercion for NUMBER parameters.
    
    This test verifies that when setting a NUMBER parameter with a string value, the value is first
    coerced to an integer and then validated against the allowed values list.
    This behaviour is expected because type coercion must occur before validation to ensure string inputs from CLI are properly converted.
    """
    setup_function()
    param.add_param({
        PARAM_NAME: 'count',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_ALLOWED_VALUES: [1, 2, 3]
    })
    # String "2" should be coerced to int 2, then validated
    param.set_param(param_name='count', value='2')
    result = param.get_param(param_name='count')
    assert result == 2
    assert isinstance(result, int)
