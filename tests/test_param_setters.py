"""
Tests for parameter setter functions in param.py.

These tests verify the behavior of set_param_value() which sets parameter values
with flexible resolution, type validation, and XOR conflict checking.
"""

import pytest
from spafw37 import param, config
from spafw37.constants.param import (
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_TOGGLE,
    PARAM_TYPE_LIST,
    PARAM_TYPE_DICT,
)


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


class TestSetParamValueResolution:
    """
    Tests for set_param_value() flexible resolution modes.
    
    This function should resolve parameters using param_name, bind_name, or alias
    with failover logic and properly store values in configuration.
    """

    def test_set_param_value_by_param_name_stores_value(self):
        """
        Tests that set_param_value() sets value using param_name.
        
        When called with param_name, the value should be stored using the bind_name
        as the config key because bind_name is the internal storage identifier.
        """
        test_param = {'name': 'database', 'type': PARAM_TYPE_TEXT, 'config-name': 'db'}
        param.add_params([test_param])
        
        param.set_param_value(param_name='database', value='production')
        
        result = config.get_config_value('db')
        assert result == 'production'

    def test_set_param_value_by_bind_name_stores_value(self):
        """
        Tests that set_param_value() sets value using bind_name.
        
        When called with bind_name directly, the value should be stored using that
        bind_name as the config key because bind_name is the storage key.
        """
        test_param = {'name': 'database', 'type': PARAM_TYPE_TEXT, 'config-name': 'db'}
        param.add_params([test_param])
        
        param.set_param_value(bind_name='db', value='staging')
        
        result = config.get_config_value('db')
        assert result == 'staging'

    def test_set_param_value_by_alias_stores_value(self):
        """
        Tests that set_param_value() sets value using alias.
        
        When called with alias, the parameter should be resolved and value stored
        using the resolved bind_name because aliases map to parameters.
        """
        test_param = {'name': 'verbose', 'type': PARAM_TYPE_TOGGLE, 'aliases': ['--verbose', '-v']}
        param.add_params([test_param])
        
        param.set_param_value(alias='--verbose', value=True)
        
        result = config.get_config_value('verbose')
        assert result is True

    def test_set_param_value_failover_resolution_stores_value(self):
        """
        Tests that set_param_value() uses failover resolution.
        
        When called with only param_name and not found by that name, failover should
        check bind_name and alias spaces to resolve the parameter definition.
        """
        test_param = {'name': 'max_connections', 'type': PARAM_TYPE_NUMBER, 'config-name': 'max_conn'}
        param.add_params([test_param])
        
        # Call with what looks like bind_name but using param_name argument
        param.set_param_value(param_name='max_conn', value=100)
        
        result = config.get_config_value('max_conn')
        assert result == 100

    def test_set_param_value_unknown_param_raises_error(self):
        """
        Tests that set_param_value() raises ValueError for unknown parameter.
        
        When parameter cannot be resolved, ValueError should be raised because
        attempting to set an unknown parameter is a programming error.
        """
        with pytest.raises(ValueError, match="Unknown parameter"):
            param.set_param_value(param_name='nonexistent', value='test')


class TestSetParamValueValidation:
    """
    Tests for set_param_value() type validation behavior.
    
    This function should validate values against parameter types and either
    coerce/accept valid values or raise errors for invalid values.
    """

    def test_set_param_value_validates_number_type(self):
        """
        Tests that set_param_value() validates and coerces number parameters.
        
        When setting a number parameter with string value, the value should be
        validated and coerced to number because number params expect numeric types.
        """
        test_param = {'name': 'port', 'type': PARAM_TYPE_NUMBER}
        param.add_params([test_param])
        
        param.set_param_value(param_name='port', value='8080')
        
        result = config.get_config_value('port')
        assert result == 8080
        assert isinstance(result, (int, float))

    def test_set_param_value_validates_toggle_type(self):
        """
        Tests that set_param_value() handles toggle parameters.
        
        When setting a toggle parameter, the value should be validated as boolean
        because toggles represent on/off states.
        """
        test_param = {'name': 'debug', 'type': PARAM_TYPE_TOGGLE}
        param.add_params([test_param])
        
        param.set_param_value(param_name='debug', value=True)
        
        result = config.get_config_value('debug')
        assert result is True

    def test_set_param_value_validates_list_type(self):
        """
        Tests that set_param_value() validates list parameters.
        
        When setting a list parameter with non-list value, it should be wrapped
        in a list because list params expect list types.
        """
        test_param = {'name': 'tags', 'type': PARAM_TYPE_LIST}
        param.add_params([test_param])
        
        param.set_param_value(param_name='tags', value='single')
        
        result = config.get_config_value('tags')
        assert result == ['single']

    def test_set_param_value_validates_dict_type_json_string(self):
        """
        Tests that set_param_value() validates dict parameters from JSON string.
        
        When setting a dict parameter with JSON string, it should be parsed to dict
        because dict params expect dictionary objects.
        """
        test_param = {'name': 'config', 'type': PARAM_TYPE_DICT}
        param.add_params([test_param])
        
        param.set_param_value(param_name='config', value='{"key": "value"}')
        
        result = config.get_config_value('config')
        assert result == {'key': 'value'}

    def test_set_param_value_validates_dict_type_dict_object(self):
        """
        Tests that set_param_value() accepts dict objects for dict parameters.
        
        When setting a dict parameter with dict object, it should be stored as-is
        because the type already matches the parameter type.
        """
        test_param = {'name': 'settings', 'type': PARAM_TYPE_DICT}
        param.add_params([test_param])
        
        param.set_param_value(param_name='settings', value={'enabled': True})
        
        result = config.get_config_value('settings')
        assert result == {'enabled': True}

    def test_set_param_value_invalid_number_strict_raises_error(self):
        """
        Tests that set_param_value() raises error for invalid number in strict mode.
        
        When strict=True and value cannot be coerced to number, ValueError should
        be raised because strict mode enforces type correctness.
        """
        test_param = {'name': 'count', 'type': PARAM_TYPE_NUMBER}
        param.add_params([test_param])
        
        with pytest.raises(ValueError, match="Cannot coerce value to number"):
            param.set_param_value(param_name='count', value='not_a_number', strict=True)

    def test_set_param_value_invalid_dict_json_raises_error(self):
        """
        Tests that set_param_value() raises error for invalid JSON in dict parameter.
        
        When setting dict parameter with invalid JSON string, ValueError should be
        raised because dict params require valid JSON or dict objects.
        """
        test_param = {'name': 'data', 'type': PARAM_TYPE_DICT}
        param.add_params([test_param])
        
        with pytest.raises(ValueError, match="Invalid JSON"):
            param.set_param_value(param_name='data', value='{invalid json}')


class TestSetParamValueXorConflicts:
    """
    Tests for set_param_value() XOR conflict checking for toggle parameters.
    
    This function should check for mutually exclusive toggle parameters and
    raise errors when attempting to set conflicting toggles.
    """

    def test_set_param_value_xor_no_conflict_succeeds(self):
        """
        Tests that set_param_value() succeeds when no XOR conflict exists.
        
        When setting a toggle that doesn't conflict with any currently set toggle,
        the operation should succeed because there is no mutual exclusion violation.
        """
        test_params = [
            {'name': 'verbose', 'type': PARAM_TYPE_TOGGLE, 'switch-list': ['verbose', 'silent']},
            {'name': 'silent', 'type': PARAM_TYPE_TOGGLE, 'switch-list': ['verbose', 'silent']},
        ]
        param.add_params(test_params)
        
        param.set_param_value(param_name='verbose', value=True)
        
        result = config.get_config_value('verbose')
        assert result is True

    def test_set_param_value_xor_conflict_raises_error(self):
        """
        Tests that set_param_value() raises error when XOR conflict detected.
        
        When attempting to set a toggle that conflicts with an already-set toggle,
        ValueError should be raised because toggles are mutually exclusive.
        """
        test_params = [
            {'name': 'verbose', 'type': PARAM_TYPE_TOGGLE, 'switch-list': ['verbose', 'silent']},
            {'name': 'silent', 'type': PARAM_TYPE_TOGGLE, 'switch-list': ['verbose', 'silent']},
        ]
        param.add_params(test_params)
        
        param.set_param_value(param_name='verbose', value=True)
        
        with pytest.raises(ValueError, match="conflicts with"):
            param.set_param_value(param_name='silent', value=True)

    def test_set_param_value_xor_setting_false_no_conflict(self):
        """
        Tests that set_param_value() allows setting toggle to False without XOR check.
        
        When setting a toggle to False, no conflict should occur because setting to
        False is disabling, not enabling a mutually exclusive option.
        """
        test_params = [
            {'name': 'verbose', 'type': PARAM_TYPE_TOGGLE, 'switch-list': ['verbose', 'silent']},
            {'name': 'silent', 'type': PARAM_TYPE_TOGGLE, 'switch-list': ['verbose', 'silent']},
        ]
        param.add_params(test_params)
        
        param.set_param_value(param_name='verbose', value=True)
        param.set_param_value(param_name='silent', value=False)  # Should not raise
        
        assert config.get_config_value('verbose') is True
        assert config.get_config_value('silent') is False


class TestSetParamValueReplacement:
    """
    Tests for set_param_value() value replacement behavior.
    
    This function should replace existing values, not append or accumulate them,
    because set operation is intended to overwrite previous values.
    """

    def test_set_param_value_replaces_existing_value(self):
        """
        Tests that set_param_value() replaces existing value.
        
        When called multiple times with same parameter, the latest value should
        replace the previous value because set operation overwrites.
        """
        test_param = {'name': 'status', 'type': PARAM_TYPE_TEXT}
        param.add_params([test_param])
        
        param.set_param_value(param_name='status', value='initial')
        param.set_param_value(param_name='status', value='updated')
        
        result = config.get_config_value('status')
        assert result == 'updated'

    def test_set_param_value_list_replaces_not_appends(self):
        """
        Tests that set_param_value() replaces list values, not appends.
        
        When setting a list parameter multiple times, each call should replace the
        entire list because set operation is replacement, not accumulation.
        """
        test_param = {'name': 'items', 'type': PARAM_TYPE_LIST}
        param.add_params([test_param])
        
        param.set_param_value(param_name='items', value=['a', 'b'])
        param.set_param_value(param_name='items', value=['c', 'd'])
        
        result = config.get_config_value('items')
        assert result == ['c', 'd']

    def test_set_param_value_dict_replaces_not_merges(self):
        """
        Tests that set_param_value() replaces dict values, not merges.
        
        When setting a dict parameter multiple times, each call should replace the
        entire dict because set operation is replacement, not merging.
        """
        test_param = {'name': 'config', 'type': PARAM_TYPE_DICT}
        param.add_params([test_param])
        
        param.set_param_value(param_name='config', value={'key1': 'value1'})
        param.set_param_value(param_name='config', value={'key2': 'value2'})
        
        result = config.get_config_value('config')
        assert result == {'key2': 'value2'}
        assert 'key1' not in result


class TestSetParamValueStrictMode:
    """
    Tests for set_param_value() strict mode behavior.
    
    In strict mode, the function should enforce stricter validation and raise
    errors for invalid values rather than attempting coercion.
    """

    def test_set_param_value_strict_mode_default_true(self):
        """
        Tests that set_param_value() defaults to strict=True.
        
        When strict parameter is not provided, strict validation should be enabled
        by default because programmatic setting should enforce correctness.
        """
        test_param = {'name': 'port', 'type': PARAM_TYPE_NUMBER}
        param.add_params([test_param])
        
        with pytest.raises(ValueError):
            param.set_param_value(param_name='port', value='invalid')

    def test_set_param_value_strict_false_coerces_value(self):
        """
        Tests that set_param_value() with strict=False attempts coercion.
        
        When strict=False, the function should attempt to coerce values to the
        expected type because non-strict mode prioritizes flexibility.
        """
        test_param = {'name': 'enabled', 'type': PARAM_TYPE_TOGGLE}
        param.add_params([test_param])
        
        param.set_param_value(param_name='enabled', value='yes', strict=False)
        
        result = config.get_config_value('enabled')
        # Non-empty string is truthy
        assert result is True
