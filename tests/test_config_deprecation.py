"""
Tests for deprecated config API functions.

These tests verify that the old config API functions continue to work correctly
despite being deprecated, ensuring backward compatibility.
"""

import pytest
from spafw37 import config, param
from spafw37.constants.param import PARAM_TYPE_TEXT, PARAM_TYPE_NUMBER, PARAM_TYPE_TOGGLE, PARAM_TYPE_LIST, PARAM_TYPE_DICT


def setup_function():
    """
    Reset state before each test to ensure isolation.
    
    Clears all internal data structures to prevent test interference, ensuring
    each test starts with a clean slate for reproducible results.
    """
    param._params.clear()
    param._param_aliases.clear()
    param._xor_list.clear()
    config._config.clear()
    config._deprecated_warnings_shown.clear()


class TestDeprecatedFunctionsStillWork:
    """
    Tests that deprecated functions still work correctly.
    
    Deprecation should not break functionality - the functions should continue
    to work as before, ensuring backward compatibility for existing code.
    """

    def test_deprecated_get_config_value_works(self):
        """
        Tests that get_config_value() still functions correctly.
        
        Despite being deprecated, the function should return correct values
        because backward compatibility must be maintained.
        """
        config._config['test_key'] = 'test_value'
        
        result = config.get_config_value('test_key')
        
        assert result == 'test_value'

    def test_deprecated_get_config_int_works(self):
        """
        Tests that get_config_int() still functions correctly.
        
        Despite being deprecated, the function should return correct integer values
        because backward compatibility must be maintained.
        """
        config._config['count'] = 42
        
        result = config.get_config_int('count')
        
        assert result == 42
        assert isinstance(result, int)

    def test_deprecated_get_config_str_works(self):
        """
        Tests that get_config_str() still functions correctly.
        
        Despite being deprecated, the function should return correct string values
        because backward compatibility must be maintained.
        """
        config._config['message'] = 'hello'
        
        result = config.get_config_str('message')
        
        assert result == 'hello'
        assert isinstance(result, str)

    def test_deprecated_get_config_bool_works(self):
        """
        Tests that get_config_bool() still functions correctly.
        
        Despite being deprecated, the function should return correct boolean values
        because backward compatibility must be maintained.
        """
        config._config['enabled'] = True
        
        result = config.get_config_bool('enabled')
        
        assert result is True
        assert isinstance(result, bool)

    def test_deprecated_get_config_float_works(self):
        """
        Tests that get_config_float() still functions correctly.
        
        Despite being deprecated, the function should return correct float values
        because backward compatibility must be maintained.
        """
        config._config['ratio'] = 3.14
        
        result = config.get_config_float('ratio')
        
        assert result == 3.14
        assert isinstance(result, float)

    def test_deprecated_get_config_list_works(self):
        """
        Tests that get_config_list() still functions correctly.
        
        Despite being deprecated, the function should return correct list values
        because backward compatibility must be maintained.
        """
        config._config['items'] = ['a', 'b', 'c']
        
        result = config.get_config_list('items')
        
        assert result == ['a', 'b', 'c']
        assert isinstance(result, list)

    def test_deprecated_get_config_dict_works(self):
        """
        Tests that get_config_dict() still functions correctly.
        
        Despite being deprecated, the function should return correct dict values
        because backward compatibility must be maintained.
        """
        config._config['settings'] = {'key': 'value'}
        
        result = config.get_config_dict('settings')
        
        assert result == {'key': 'value'}
        assert isinstance(result, dict)

    def test_deprecated_set_config_value_works(self):
        """
        Tests that set_config_value() still functions correctly.
        
        Despite being deprecated, the function should set values correctly
        because backward compatibility must be maintained.
        """
        config.set_config_value('new_key', 'new_value')
        
        assert config._config['new_key'] == 'new_value'

    def test_deprecated_set_config_list_value_works(self):
        """
        Tests that set_config_list_value() still functions correctly.
        
        Despite being deprecated, the function should append values correctly
        because backward compatibility must be maintained.
        """
        config.set_config_list_value('item1', 'list_key')
        config.set_config_list_value('item2', 'list_key')
        
        assert config._config['list_key'] == ['item1', 'item2']

    def test_deprecated_set_config_list_value_extends_lists(self):
        """
        Tests that set_config_list_value() extends when given a list.
        
        When provided with a list value, it should extend the existing list
        because this is the expected behavior from the original implementation.
        """
        config.set_config_list_value('item1', 'other_list_key')
        config.set_config_list_value(['item2', 'item3'], 'other_list_key')
        
        assert config._config['other_list_key'] == ['item1', 'item2', 'item3']


class TestDeprecatedFunctionsWithDefaults:
    """
    Tests that deprecated getter functions handle defaults correctly.
    
    The deprecated functions should return default values when keys don't exist,
    maintaining the original API behavior.
    """

    def test_get_config_int_returns_default(self):
        """
        Tests that get_config_int() returns default when key not found.
        
        When a key doesn't exist, the default value should be returned
        because this is the expected behavior from the original API.
        """
        result = config.get_config_int('nonexistent', default=99)
        
        assert result == 99

    def test_get_config_str_returns_default(self):
        """
        Tests that get_config_str() returns default when key not found.
        
        When a key doesn't exist, the default value should be returned
        because this is the expected behavior from the original API.
        """
        result = config.get_config_str('nonexistent', default='fallback')
        
        assert result == 'fallback'

    def test_get_config_bool_returns_default(self):
        """
        Tests that get_config_bool() returns default when key not found.
        
        When a key doesn't exist, the default value should be returned
        because this is the expected behavior from the original API.
        """
        result = config.get_config_bool('nonexistent', default=True)
        
        assert result is True

    def test_get_config_float_returns_default(self):
        """
        Tests that get_config_float() returns default when key not found.
        
        When a key doesn't exist, the default value should be returned
        because this is the expected behavior from the original API.
        """
        result = config.get_config_float('nonexistent', default=2.71)
        
        assert result == 2.71

    def test_get_config_list_returns_default(self):
        """
        Tests that get_config_list() returns default when key not found.
        
        When a key doesn't exist, the default value should be returned
        because this is the expected behavior from the original API.
        """
        result = config.get_config_list('nonexistent', default=['x', 'y'])
        
        assert result == ['x', 'y']

    def test_get_config_dict_returns_default(self):
        """
        Tests that get_config_dict() returns default when key not found.
        
        When a key doesn't exist, the default value should be returned
        because this is the expected behavior from the original API.
        """
        result = config.get_config_dict('nonexistent', default={'key': 'val'})
        
        assert result == {'key': 'val'}


class TestDeprecationDecorator:
    """
    Tests for the @_deprecated decorator mechanism.
    
    Verifies that the decorator tracks which functions have shown warnings
    to avoid repeated warnings for the same function.
    """

    def test_deprecation_tracking_set_exists(self):
        """
        Tests that deprecation tracking set exists.
        
        The _deprecated_warnings_shown set should exist and be accessible
        because it's used to track which functions have already shown warnings.
        """
        assert hasattr(config, '_deprecated_warnings_shown')
        assert isinstance(config._deprecated_warnings_shown, set)

    def test_can_clear_deprecation_tracking(self):
        """
        Tests that deprecation tracking can be cleared.
        
        The tracking set should be clearable, which is useful for testing
        because it allows each test to start with a clean state.
        """
        config._deprecated_warnings_shown.add('test_function')
        assert 'test_function' in config._deprecated_warnings_shown
        
        config._deprecated_warnings_shown.clear()
        
        assert len(config._deprecated_warnings_shown) == 0

