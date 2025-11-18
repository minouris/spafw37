"""
Tests for the new parameter API in core.py.

These tests verify that the public param API wrapper functions in core.py
correctly delegate to the underlying param module functions.
"""

import pytest
from spafw37 import core, param, config
from spafw37.constants.param import PARAM_TYPE_TEXT, PARAM_TYPE_NUMBER, PARAM_TYPE_TOGGLE, PARAM_TYPE_LIST, PARAM_TYPE_DICT


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


class TestCoreSetParam:
    """
    Tests for core.set_param() function.
    
    The set_param() function should delegate to param.set_param_value() and
    support flexible resolution via param_name, bind_name, or alias.
    """

    def test_set_param_by_name(self):
        """
        Tests that set_param() works with param_name.
        
        When called with param_name, the parameter should be resolved and value set
        because param_name is the primary identifier for parameters.
        """
        test_param = {'name': 'hostname', 'type': PARAM_TYPE_TEXT}
        param.add_params([test_param])
        
        core.set_param(param_name='hostname', value='localhost')
        
        result = config.get_config_value('hostname')
        assert result == 'localhost'

    def test_set_param_by_bind_name(self):
        """
        Tests that set_param() works with bind_name.
        
        When called with bind_name, the parameter should be resolved via config-name
        because bind_name provides an alternative configuration key.
        """
        test_param = {'name': 'port', 'type': PARAM_TYPE_NUMBER, 'config-name': 'server_port'}
        param.add_params([test_param])
        
        core.set_param(bind_name='server_port', value=8080)
        
        result = config.get_config_value('server_port')
        assert result == 8080

    def test_set_param_by_alias(self):
        """
        Tests that set_param() works with alias.
        
        When called with alias, the parameter should be resolved via aliases list
        because aliases provide command-line style parameter references.
        """
        test_param = {'name': 'verbose', 'type': PARAM_TYPE_TOGGLE, 'aliases': ['--verbose', '-v']}
        param.add_params([test_param])
        
        core.set_param(alias='--verbose', value=True)
        
        result = config.get_config_value('verbose')
        assert result is True

    def test_set_param_replaces_existing_value(self):
        """
        Tests that set_param() replaces existing value instead of accumulating.
        
        When called multiple times, the last value should win because set_param()
        is designed to replace rather than accumulate values.
        """
        test_param = {'name': 'message', 'type': PARAM_TYPE_TEXT}
        param.add_params([test_param])
        
        core.set_param(param_name='message', value='first')
        core.set_param(param_name='message', value='second')
        
        result = config.get_config_value('message')
        assert result == 'second'


class TestCoreJoinParam:
    """
    Tests for core.join_param() function.
    
    The join_param() function should delegate to param.join_param_value() and
    support type-specific accumulation logic.
    """

    def test_join_param_string_accumulation(self):
        """
        Tests that join_param() accumulates string values.
        
        When called multiple times with strings, values should concatenate with space
        because string joining uses separator-based concatenation.
        """
        test_param = {'name': 'keywords', 'type': PARAM_TYPE_TEXT}
        param.add_params([test_param])
        
        core.join_param(param_name='keywords', value='python')
        core.join_param(param_name='keywords', value='testing')
        
        result = config.get_config_value('keywords')
        assert result == 'python testing'

    def test_join_param_list_accumulation(self):
        """
        Tests that join_param() accumulates list values.
        
        When called multiple times with single values, they should be appended
        because list joining accumulates items into a list.
        """
        test_param = {'name': 'filenames', 'type': PARAM_TYPE_LIST}
        param.add_params([test_param])
        
        core.join_param(param_name='filenames', value='file1.txt')
        core.join_param(param_name='filenames', value='file2.txt')
        
        result = config.get_config_value('filenames')
        assert result == ['file1.txt', 'file2.txt']

    def test_join_param_dict_merge(self):
        """
        Tests that join_param() merges dict values.
        
        When called multiple times with dicts, they should be merged
        because dict joining performs shallow/deep merge based on config.
        """
        test_param = {'name': 'app_config', 'type': PARAM_TYPE_DICT}
        param.add_params([test_param])
        
        core.join_param(param_name='app_config', value={'host': 'localhost'})
        core.join_param(param_name='app_config', value={'port': 8080})
        
        result = config.get_config_value('app_config')
        assert result == {'host': 'localhost', 'port': 8080}

    def test_join_param_by_bind_name(self):
        """
        Tests that join_param() works with bind_name resolution.
        
        When called with bind_name, the parameter should be resolved and values
        accumulated because bind_name is a valid identifier.
        """
        test_param = {'name': 'tags', 'type': PARAM_TYPE_LIST, 'config-name': 'tag_list'}
        param.add_params([test_param])
        
        core.join_param(bind_name='tag_list', value='tag1')
        core.join_param(bind_name='tag_list', value='tag2')
        
        result = config.get_config_value('tag_list')
        assert result == ['tag1', 'tag2']


class TestCoreGetParamStr:
    """
    Tests for core.get_param_str() function.
    
    The get_param_str() function should delegate to param.get_param_str() and
    return string values with proper defaults.
    """

    def test_get_param_str_returns_value(self):
        """
        Tests that get_param_str() returns existing string value.
        
        When parameter has a value, that value should be returned as string
        because get_param_str() retrieves and type-casts the value.
        """
        test_param = {'name': 'name', 'type': PARAM_TYPE_TEXT}
        param.add_params([test_param])
        param.set_param_value(param_name='name', value='Alice')
        
        result = core.get_param_str(param_name='name')
        
        assert result == 'Alice'

    def test_get_param_str_returns_default(self):
        """
        Tests that get_param_str() returns default when param not set.
        
        When parameter has no value, the default should be returned
        because get_param_str() provides default fallback behavior.
        """
        test_param = {'name': 'missing', 'type': PARAM_TYPE_TEXT}
        param.add_params([test_param])
        
        result = core.get_param_str(param_name='missing', default='fallback')
        
        assert result == 'fallback'

    def test_get_param_str_by_alias(self):
        """
        Tests that get_param_str() works with alias resolution.
        
        When called with alias, the parameter should be resolved and value returned
        because get_param_str() supports flexible resolution.
        """
        test_param = {'name': 'url', 'type': PARAM_TYPE_TEXT, 'aliases': ['--url', '-u']}
        param.add_params([test_param])
        param.set_param_value(param_name='url', value='https://example.com')
        
        result = core.get_param_str(alias='--url')
        
        assert result == 'https://example.com'


class TestCoreGetParamInt:
    """
    Tests for core.get_param_int() function.
    
    The get_param_int() function should delegate to param.get_param_int() and
    return integer values with proper defaults.
    """

    def test_get_param_int_returns_value(self):
        """
        Tests that get_param_int() returns existing integer value.
        
        When parameter has a numeric value, that value should be returned as integer
        because get_param_int() retrieves and type-casts the value.
        """
        test_param = {'name': 'count', 'type': PARAM_TYPE_NUMBER}
        param.add_params([test_param])
        param.set_param_value(param_name='count', value=42)
        
        result = core.get_param_int(param_name='count')
        
        assert result == 42

    def test_get_param_int_returns_default(self):
        """
        Tests that get_param_int() returns default when param not set.
        
        When parameter has no value, the default should be returned
        because get_param_int() provides default fallback behavior.
        """
        test_param = {'name': 'missing', 'type': PARAM_TYPE_NUMBER}
        param.add_params([test_param])
        
        result = core.get_param_int(param_name='missing', default=99)
        
        assert result == 99


class TestCoreGetParamBool:
    """
    Tests for core.get_param_bool() function.
    
    The get_param_bool() function should delegate to param.get_param_bool() and
    return boolean values with proper defaults.
    """

    def test_get_param_bool_returns_value(self):
        """
        Tests that get_param_bool() returns existing boolean value.
        
        When parameter has a boolean value, that value should be returned
        because get_param_bool() retrieves the toggle value.
        """
        test_param = {'name': 'enabled', 'type': PARAM_TYPE_TOGGLE}
        param.add_params([test_param])
        param.set_param_value(param_name='enabled', value=True)
        
        result = core.get_param_bool(param_name='enabled')
        
        assert result is True

    def test_get_param_bool_returns_default(self):
        """
        Tests that get_param_bool() returns default when param not set.
        
        When parameter has no value, the default should be returned
        because get_param_bool() provides default fallback behavior.
        """
        test_param = {'name': 'missing', 'type': PARAM_TYPE_TOGGLE}
        param.add_params([test_param])
        
        result = core.get_param_bool(param_name='missing', default=False)
        
        assert result is False


class TestCoreGetParamFloat:
    """
    Tests for core.get_param_float() function.
    
    The get_param_float() function should delegate to param.get_param_float() and
    return float values with proper defaults.
    """

    def test_get_param_float_returns_value(self):
        """
        Tests that get_param_float() returns existing float value.
        
        When parameter has a numeric value, that value should be returned as float
        because get_param_float() retrieves and type-casts the value.
        """
        test_param = {'name': 'threshold', 'type': PARAM_TYPE_NUMBER}
        param.add_params([test_param])
        param.set_param_value(param_name='threshold', value=3.14)
        
        result = core.get_param_float(param_name='threshold')
        
        assert result == 3.14

    def test_get_param_float_returns_default(self):
        """
        Tests that get_param_float() returns default when param not set.
        
        When parameter has no value, the default should be returned
        because get_param_float() provides default fallback behavior.
        """
        test_param = {'name': 'missing', 'type': PARAM_TYPE_NUMBER}
        param.add_params([test_param])
        
        result = core.get_param_float(param_name='missing', default=2.71)
        
        assert result == 2.71


class TestCoreGetParamList:
    """
    Tests for core.get_param_list() function.
    
    The get_param_list() function should delegate to param.get_param_list() and
    return list values with proper defaults.
    """

    def test_get_param_list_returns_value(self):
        """
        Tests that get_param_list() returns existing list value.
        
        When parameter has a list value, that value should be returned
        because get_param_list() retrieves the list.
        """
        test_param = {'name': 'items', 'type': PARAM_TYPE_LIST}
        param.add_params([test_param])
        param.set_param_value(param_name='items', value=['a', 'b', 'c'])
        
        result = core.get_param_list(param_name='items')
        
        assert result == ['a', 'b', 'c']

    def test_get_param_list_returns_default(self):
        """
        Tests that get_param_list() returns default when param not set.
        
        When parameter has no value, the default should be returned
        because get_param_list() provides default fallback behavior.
        """
        test_param = {'name': 'missing', 'type': PARAM_TYPE_LIST}
        param.add_params([test_param])
        
        result = core.get_param_list(param_name='missing', default=['x', 'y'])
        
        assert result == ['x', 'y']


class TestCoreGetParamDict:
    """
    Tests for core.get_param_dict() function.
    
    The get_param_dict() function should delegate to param.get_param_dict() and
    return dict values with proper defaults.
    """

    def test_get_param_dict_returns_value(self):
        """
        Tests that get_param_dict() returns existing dict value.
        
        When parameter has a dict value, that value should be returned
        because get_param_dict() retrieves the dictionary.
        """
        test_param = {'name': 'config', 'type': PARAM_TYPE_DICT}
        param.add_params([test_param])
        param.set_param_value(param_name='config', value={'key': 'value'})
        
        result = core.get_param_dict(param_name='config')
        
        assert result == {'key': 'value'}

    def test_get_param_dict_returns_default(self):
        """
        Tests that get_param_dict() returns default when param not set.
        
        When parameter has no value, the default should be returned
        because get_param_dict() provides default fallback behavior.
        """
        test_param = {'name': 'missing', 'type': PARAM_TYPE_DICT}
        param.add_params([test_param])
        
        result = core.get_param_dict(param_name='missing', default={'fallback': 'data'})
        
        assert result == {'fallback': 'data'}
