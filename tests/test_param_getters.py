"""
Tests for parameter getter functions in param.py.

These tests verify the behavior of typed parameter getter functions that retrieve
values from the configuration with type coercion, flexible resolution, and strict mode support.
"""

import pytest
from spafw37 import param, config
def setup_function():
    """
    Reset parameter and configuration state before each test to ensure isolation.
    
    Clears all internal data structures to prevent test interference, ensuring
    each test starts with a clean slate for reproducible results.
    """
    param._params.clear()
    param._param_aliases.clear()
    param._xor_list.clear()
    config._config.clear()
class TestGetParamValue:
    """
    Tests for get_param_value() function that retrieves raw parameter values.
    
    This function provides the foundation for all typed getters and should support
    flexible resolution (param_name, bind_name, alias) with failover logic.
    """

    def test_get_param_value_by_param_name_returns_stored_value(self):
        """
        Tests that get_param_value() retrieves a value using param_name.
        
        When a parameter is set and retrieved by its param_name, the stored value
        should be returned exactly as stored because param_name is the primary identifier.
        """
        
        test_param = {'name': 'database', 'type': 'str', 'config-name': 'db'}
        param.add_params([test_param])
        config.set_config_value('db', 'production')  # Store using bind_name (config-name)
        
        result = param.get_param_value(param_name='database')
        assert result == 'production'

    def test_get_param_value_by_bind_name_returns_stored_value(self):
        """
        Tests that get_param_value() retrieves a value using bind_name.
        
        When a parameter is set using param_name and retrieved by bind_name, the value
        should be found because bind_name resolution should map to the same internal config key.
        """
        
        test_param = {'name': 'database', 'type': 'str', 'config-name': 'db'}
        param.add_params([test_param])
        config.set_config_value('db', 'staging')  # Store using bind_name (config-name)
        
        result = param.get_param_value(bind_name='db')
        assert result == 'staging'

    def test_get_param_value_by_alias_returns_stored_value(self):
        """
        Tests that get_param_value() retrieves a value using alias.
        
        When a parameter is set using param_name and retrieved by alias, the value should
        be found because alias resolution should map to the same internal config key.
        """
        
        test_param = {'name': 'verbose', 'type': 'toggle', 'aliases': ['--verbose']}
        param.add_params([test_param])
        config.set_config_value('verbose', True)
        
        result = param.get_param_value(alias='--verbose')
        assert result is True

    def test_get_param_value_failover_resolution_returns_value(self):
        """
        Tests that get_param_value() uses failover resolution with single argument.
        
        When called with only param_name and the parameter is not found by that name,
        failover should check bind_name and alias spaces to find the parameter definition.
        """
        
        test_param = {'name': 'max_connections', 'type': 'int', 'config-name': 'max_conn'}
        param.add_params([test_param])
        config.set_config_value('max_conn', 100)  # Store using bind_name (config-name)
        
        # Call with what looks like bind_name but using param_name argument
        result = param.get_param_value(param_name='max_conn')
        assert result == 100

    def test_get_param_value_missing_returns_default(self):
        """
        Tests that get_param_value() returns default when parameter not found.
        
        When a parameter doesn't exist and default is provided, the default value should
        be returned without raising an error because this is the expected fallback behavior.
        """
        
        result = param.get_param_value(param_name='nonexistent', default='fallback')
        assert result == 'fallback'

    def test_get_param_value_missing_strict_raises_error(self):
        """
        Tests that get_param_value() raises ValueError in strict mode when parameter missing.
        
        When strict=True and parameter is not found, a ValueError should be raised to alert
        the caller because strict mode enforces that the parameter must exist.
        """
        
        with pytest.raises(ValueError, match="Parameter .* not found"):
            param.get_param_value(param_name='nonexistent', strict=True)
class TestGetParamStr:
    """
    Tests for __get_param_str() function that retrieves string parameter values.
    
    This function coerces any value to string using str() and should handle
    various input types with proper string conversion.
    """

    def test_get_param_str_returns_string_value(self):
        """
        Tests that __get_param_str() returns a string value directly.
        
        When a parameter is already stored as a string, it should be returned
        as-is because no coercion is needed.
        """
        
        test_param = {'name': 'name', 'type': 'str'}
        param.add_params([test_param])
        config.set_config_value('name', 'John')
        
        result = param._get_param_str(param_name='name')
        assert result == 'John'
        assert isinstance(result, str)

    def test_get_param_str_coerces_int_to_string(self):
        """
        Tests that __get_param_str() coerces integer to string.
        
        When a parameter is stored as an integer, __get_param_str() should convert it
        to string using str() because the caller expects string output.
        """
        
        test_param = {'name': 'count', 'type': 'int'}
        param.add_params([test_param])
        config.set_config_value('count', 123)
        
        result = param._get_param_str(param_name='count')
        assert result == '123'
        assert isinstance(result, str)

    def test_get_param_str_coerces_float_to_string(self):
        """
        Tests that _get_param_str() coerces float to string.
        
        When a parameter is stored as a float, _get_param_str() should convert it
        to string preserving the decimal representation because precision matters.
        """
        
        test_param = {'name': 'pi', 'type': 'float'}
        param.add_params([test_param])
        config.set_config_value('pi', 3.14)
        
        result = param._get_param_str(param_name='pi')
        assert result == '3.14'
        assert isinstance(result, str)

    def test_get_param_str_coerces_list_to_string_representation(self):
        """
        Tests that __get_param_str() coerces list to its string representation.
        
        When a parameter is stored as a list, __get_param_str() should convert it
        to string using str() which produces Python's list representation format.
        """
        
        test_param = {'name': 'tags', 'type': 'list'}
        param.add_params([test_param])
        config.set_config_value('tags', ['a', 'b', 'c'])
        
        result = param._get_param_str(param_name='tags')
        assert result == "['a', 'b', 'c']"
        assert isinstance(result, str)

    def test_get_param_str_missing_returns_default(self):
        """
        Tests that __get_param_str() returns default when parameter not found.
        
        When a parameter doesn't exist and default is provided, the default should
        be returned because __get_param_str() inherits fallback behavior from get_param_value().
        """
        
        result = param._get_param_str(param_name='missing', default='default_value')
        assert result == 'default_value'

    def test_get_param_str_missing_strict_raises_error(self):
        """
        Tests that __get_param_str() raises ValueError in strict mode when parameter missing.
        
        When strict=True and parameter is not found, ValueError should be raised
        because strict mode requires the parameter to exist.
        """
        
        with pytest.raises(ValueError, match="Parameter .* not found"):
            param._get_param_str(param_name='missing', strict=True)
class TestGetParamInt:
    """
    Tests for __get_param_int() function that retrieves integer parameter values.
    
    This function coerces values to int via int(float(value)) for truncation behavior
    and should handle string and float inputs with proper conversion.
    """

    def test_get_param_int_returns_int_value(self):
        """
        Tests that _get_param_int() returns an integer value directly.
        
        When a parameter is already stored as an integer, it should be returned
        as-is because no coercion is needed.
        """
        
        test_param = {'name': 'count', 'type': 'int'}
        param.add_params([test_param])
        config.set_config_value('count', 42)
        
        result = param._get_param_int(param_name='count')
        assert result == 42
        assert isinstance(result, int)

    def test_get_param_int_coerces_string_to_int(self):
        """
        Tests that _get_param_int() coerces string representation of integer.
        
        When a parameter is stored as a string containing an integer, _get_param_int()
        should parse it to int because users may provide numeric strings via CLI.
        """
        
        test_param = {'name': 'port', 'type': 'str'}
        param.add_params([test_param])
        config.set_config_value('port', '8080')
        
        result = param._get_param_int(param_name='port')
        assert result == 8080
        assert isinstance(result, int)

    def test_get_param_int_truncates_float_value(self):
        """
        Tests that _get_param_int() truncates float to integer.
        
        When a parameter is stored as a float, _get_param_int() should truncate (not round)
        to integer because int(float()) behavior drops the decimal part.
        """
        
        test_param = {'name': 'ratio', 'type': 'float'}
        param.add_params([test_param])
        config.set_config_value('ratio', 3.99)
        
        result = param._get_param_int(param_name='ratio')
        assert result == 3
        assert isinstance(result, int)

    def test_get_param_int_truncates_string_float(self):
        """
        Tests that _get_param_int() truncates string representation of float.
        
        When a parameter is stored as a string containing a float, _get_param_int()
        should parse and truncate to int because the coercion path is str -> float -> int.
        """
        
        test_param = {'name': 'value', 'type': 'str'}
        param.add_params([test_param])
        config.set_config_value('value', '3.14')
        
        result = param._get_param_int(param_name='value')
        assert result == 3
        assert isinstance(result, int)

    def test_get_param_int_invalid_string_strict_raises_error(self):
        """
        Tests that _get_param_int() raises ValueError on invalid string in strict mode.
        
        When strict=True and value cannot be coerced to int, ValueError should be raised
        because strict mode enforces type safety and conversion must succeed.
        """
        
        test_param = {'name': 'bad', 'type': 'str'}
        param.add_params([test_param])
        config.set_config_value('bad', 'not_a_number')
        
        with pytest.raises(ValueError, match="Cannot convert .* to int"):
            param._get_param_int(param_name='bad', strict=True)

    def test_get_param_int_invalid_string_non_strict_returns_default(self):
        """
        Tests that _get_param_int() returns default on invalid string in non-strict mode.
        
        When strict=False and value cannot be coerced to int, default should be returned
        because non-strict mode prioritizes fault tolerance over strict validation.
        """
        
        test_param = {'name': 'bad', 'type': 'str'}
        param.add_params([test_param])
        config.set_config_value('bad', 'invalid')
        
        result = param._get_param_int(param_name='bad', default=999)
        assert result == 999

    def test_get_param_int_missing_returns_default(self):
        """
        Tests that _get_param_int() returns default when parameter not found.
        
        When a parameter doesn't exist and default is provided, the default should
        be returned because _get_param_int() inherits fallback behavior from get_param_value().
        """
        
        result = param._get_param_int(param_name='missing', default=100)
        assert result == 100
class TestGetParamBool:
    """
    Tests for __get_param_bool() function that retrieves boolean parameter values.
    
    This function coerces values using Python's bool() for truthy/falsy evaluation
    and should handle various input types with standard truthiness rules.
    """

    def test_get_param_bool_returns_true_value(self):
        """
        Tests that _get_param_bool() returns True for boolean True.
        
        When a parameter is stored as boolean True, it should be returned
        as-is because no coercion is needed.
        """
        
        test_param = {'name': 'enabled', 'type': 'toggle'}
        param.add_params([test_param])
        config.set_config_value('enabled', True)
        
        result = param._get_param_bool(param_name='enabled')
        assert result is True

    def test_get_param_bool_returns_false_value(self):
        """
        Tests that _get_param_bool() returns False for boolean False.
        
        When a parameter is stored as boolean False, it should be returned
        as-is because no coercion is needed.
        """
        
        test_param = {'name': 'disabled', 'type': 'toggle'}
        param.add_params([test_param])
        config.set_config_value('disabled', False)
        
        result = param._get_param_bool(param_name='disabled')
        assert result is False

    def test_get_param_bool_coerces_non_empty_string_to_true(self):
        """
        Tests that _get_param_bool() coerces non-empty string to True.
        
        When a parameter is stored as a non-empty string, bool() evaluation should
        return True because non-empty strings are truthy in Python.
        """
        
        test_param = {'name': 'flag', 'type': 'str'}
        param.add_params([test_param])
        config.set_config_value('flag', 'yes')
        
        result = param._get_param_bool(param_name='flag')
        assert result is True

    def test_get_param_bool_coerces_empty_string_to_false(self):
        """
        Tests that _get_param_bool() coerces empty string to False.
        
        When a parameter is stored as an empty string, bool() evaluation should
        return False because empty strings are falsy in Python.
        """
        
        test_param = {'name': 'flag', 'type': 'str'}
        param.add_params([test_param])
        config.set_config_value('flag', '')
        
        result = param._get_param_bool(param_name='flag')
        assert result is False

    def test_get_param_bool_coerces_positive_int_to_true(self):
        """
        Tests that _get_param_bool() coerces positive integer to True.
        
        When a parameter is stored as a positive integer, bool() evaluation should
        return True because non-zero integers are truthy in Python.
        """
        
        test_param = {'name': 'count', 'type': 'int'}
        param.add_params([test_param])
        config.set_config_value('count', 1)
        
        result = param._get_param_bool(param_name='count')
        assert result is True

    def test_get_param_bool_coerces_zero_to_false(self):
        """
        Tests that _get_param_bool() coerces zero to False.
        
        When a parameter is stored as zero, bool() evaluation should return False
        because zero is falsy in Python.
        """
        
        test_param = {'name': 'count', 'type': 'int'}
        param.add_params([test_param])
        config.set_config_value('count', 0)
        
        result = param._get_param_bool(param_name='count')
        assert result is False

    def test_get_param_bool_coerces_empty_list_to_false(self):
        """
        Tests that _get_param_bool() coerces empty list to False.
        
        When a parameter is stored as an empty list, bool() evaluation should
        return False because empty lists are falsy in Python.
        """
        
        test_param = {'name': 'items', 'type': 'list'}
        param.add_params([test_param])
        config.set_config_value('items', [])
        
        result = param._get_param_bool(param_name='items')
        assert result is False

    def test_get_param_bool_missing_returns_default(self):
        """
        Tests that _get_param_bool() returns default when parameter not found.
        
        When a parameter doesn't exist and default is provided, the default should
        be returned because _get_param_bool() inherits fallback behavior from get_param_value().
        """
        
        result = param._get_param_bool(param_name='missing', default=True)
        assert result is True
class TestGetParamFloat:
    """
    Tests for __get_param_float() function that retrieves float parameter values.
    
    This function coerces values to float using float() and should handle
    string and integer inputs with proper conversion.
    """

    def test_get_param_float_returns_float_value(self):
        """
        Tests that _get_param_float() returns a float value directly.
        
        When a parameter is already stored as a float, it should be returned
        as-is because no coercion is needed.
        """
        
        test_param = {'name': 'ratio', 'type': 'float'}
        param.add_params([test_param])
        config.set_config_value('ratio', 3.14)
        
        result = param._get_param_float(param_name='ratio')
        assert result == 3.14
        assert isinstance(result, float)

    def test_get_param_float_coerces_int_to_float(self):
        """
        Tests that _get_param_float() coerces integer to float.
        
        When a parameter is stored as an integer, _get_param_float() should convert it
        to float because the caller expects float output.
        """
        
        test_param = {'name': 'count', 'type': 'int'}
        param.add_params([test_param])
        config.set_config_value('count', 123)
        
        result = param._get_param_float(param_name='count')
        assert result == 123.0
        assert isinstance(result, float)

    def test_get_param_float_coerces_string_int_to_float(self):
        """
        Tests that _get_param_float() coerces string integer to float.
        
        When a parameter is stored as a string containing an integer, _get_param_float()
        should parse it to float because users may provide numeric strings via CLI.
        """
        
        test_param = {'name': 'value', 'type': 'str'}
        param.add_params([test_param])
        config.set_config_value('value', '42')
        
        result = param._get_param_float(param_name='value')
        assert result == 42.0
        assert isinstance(result, float)

    def test_get_param_float_coerces_string_float_to_float(self):
        """
        Tests that _get_param_float() coerces string float to float.
        
        When a parameter is stored as a string containing a float, _get_param_float()
        should parse it to float preserving decimal precision.
        """
        
        test_param = {'name': 'pi', 'type': 'str'}
        param.add_params([test_param])
        config.set_config_value('pi', '3.14159')
        
        result = param._get_param_float(param_name='pi')
        assert result == 3.14159
        assert isinstance(result, float)

    def test_get_param_float_invalid_string_strict_raises_error(self):
        """
        Tests that _get_param_float() raises ValueError on invalid string in strict mode.
        
        When strict=True and value cannot be coerced to float, ValueError should be raised
        because strict mode enforces type safety and conversion must succeed.
        """
        
        test_param = {'name': 'bad', 'type': 'str'}
        param.add_params([test_param])
        config.set_config_value('bad', 'not_a_number')
        
        with pytest.raises(ValueError, match="Cannot convert .* to float"):
            param._get_param_float(param_name='bad', strict=True)

    def test_get_param_float_invalid_string_non_strict_returns_default(self):
        """
        Tests that _get_param_float() returns default on invalid string in non-strict mode.
        
        When strict=False and value cannot be coerced to float, default should be returned
        because non-strict mode prioritizes fault tolerance over strict validation.
        """
        
        test_param = {'name': 'bad', 'type': 'str'}
        param.add_params([test_param])
        config.set_config_value('bad', 'invalid')
        
        result = param._get_param_float(param_name='bad', default=99.9)
        assert result == 99.9

    def test_get_param_float_missing_returns_default(self):
        """
        Tests that _get_param_float() returns default when parameter not found.
        
        When a parameter doesn't exist and default is provided, the default should
        be returned because _get_param_float() inherits fallback behavior from get_param_value().
        """
        
        result = param._get_param_float(param_name='missing', default=1.5)
        assert result == 1.5
class TestGetParamList:
    """
    Tests for __get_param_list() function that retrieves list parameter values.
    
    This function returns list values as-is without coercion and defaults to
    empty list when not found, matching typical list parameter usage patterns.
    """

    def test_get_param_list_returns_list_value(self):
        """
        Tests that _get_param_list() returns a list value directly.
        
        When a parameter is stored as a list, it should be returned as-is
        because no coercion is needed for list type parameters.
        """
        
        test_param = {'name': 'tags', 'type': 'list'}
        param.add_params([test_param])
        config.set_config_value('tags', ['a', 'b', 'c'])
        
        result = param._get_param_list(param_name='tags')
        assert result == ['a', 'b', 'c']
        assert isinstance(result, list)

    def test_get_param_list_returns_empty_list_by_default(self):
        """
        Tests that _get_param_list() returns empty list when parameter not found.
        
        When a parameter doesn't exist and no default is provided, an empty list should
        be returned because this matches typical list parameter usage patterns.
        """
        
        result = param._get_param_list(param_name='missing')
        assert result == []
        assert isinstance(result, list)

    def test_get_param_list_respects_custom_default(self):
        """
        Tests that _get_param_list() respects custom default value.
        
        When a parameter doesn't exist and custom default is provided, that default
        should be returned because explicit defaults override the empty list default.
        """
        
        result = param._get_param_list(param_name='missing', default=['default'])
        assert result == ['default']

    def test_get_param_list_no_coercion_from_string(self):
        """
        Tests that _get_param_list() returns string value without coercion.
        
        When a parameter is stored as a string, _get_param_list() should return it as-is
        because _get_param_list() does not perform type coercion (caller must ensure correct type).
        """
        
        test_param = {'name': 'value', 'type': 'str'}
        param.add_params([test_param])
        config.set_config_value('value', 'not_a_list')
        
        result = param._get_param_list(param_name='value')
        assert result == 'not_a_list'
        assert isinstance(result, str)
class TestGetParamDict:
    """
    Tests for __get_param_dict() function that retrieves dict parameter values.
    
    This function returns dict values as-is without coercion and defaults to
    empty dict when not found, matching typical dict parameter usage patterns.
    """

    def test_get_param_dict_returns_dict_value(self):
        """
        Tests that _get_param_dict() returns a dict value directly.
        
        When a parameter is stored as a dict, it should be returned as-is
        because no coercion is needed for dict type parameters.
        """
        
        test_param = {'name': 'config', 'type': 'dict'}
        param.add_params([test_param])
        config.set_config_value('config', {'key': 'value'})
        
        result = param._get_param_dict(param_name='config')
        assert result == {'key': 'value'}
        assert isinstance(result, dict)

    def test_get_param_dict_returns_empty_dict_by_default(self):
        """
        Tests that _get_param_dict() returns empty dict when parameter not found.
        
        When a parameter doesn't exist and no default is provided, an empty dict should
        be returned because this matches typical dict parameter usage patterns.
        """
        
        result = param._get_param_dict(param_name='missing')
        assert result == {}
        assert isinstance(result, dict)

    def test_get_param_dict_respects_custom_default(self):
        """
        Tests that _get_param_dict() respects custom default value.
        
        When a parameter doesn't exist and custom default is provided, that default
        should be returned because explicit defaults override the empty dict default.
        """
        
        result = param._get_param_dict(param_name='missing', default={'default': 'value'})
        assert result == {'default': 'value'}

    def test_get_param_dict_no_coercion_from_string(self):
        """
        Tests that _get_param_dict() returns string value without coercion.
        
        When a parameter is stored as a string, _get_param_dict() should return it as-is
        because _get_param_dict() does not perform type coercion (caller must ensure correct type).
        """
        
        test_param = {'name': 'value', 'type': 'str'}
        param.add_params([test_param])
        config.set_config_value('value', 'not_a_dict')
        
        result = param._get_param_dict(param_name='value')
        assert result == 'not_a_dict'
        assert isinstance(result, str)
