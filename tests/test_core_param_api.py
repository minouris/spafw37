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
    
    The set_param() function should delegate to param.set_param() and
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
    
    The join_param() function should delegate to param.join_param() and
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


class TestCoreGetParam:
    """
    Tests for core.get_param() function.
    
    The get_param() function should intelligently route to the correct typed getter
    based on the parameter's PARAM_TYPE and return properly coerced values.
    """

    def test_get_param_returns_string_for_text_type(self):
        """
        Tests that get_param() returns string for PARAM_TYPE_TEXT.
        
        When parameter type is TEXT, the value should be returned as string
        because get_param() routes to _get_param_str().
        """
        test_param = {'name': 'name', 'type': PARAM_TYPE_TEXT}
        param.add_params([test_param])
        param.set_param(param_name='name', value='Alice')
        
        result = core.get_param(param_name='name')
        
        assert result == 'Alice'
        assert isinstance(result, str)

    def test_get_param_returns_int_for_number_type(self):
        """
        Tests that get_param() returns int for PARAM_TYPE_NUMBER.
        
        When parameter type is NUMBER, the value should be returned as int
        because get_param() routes to _get_param_int().
        """
        test_param = {'name': 'count', 'type': PARAM_TYPE_NUMBER}
        param.add_params([test_param])
        param.set_param(param_name='count', value=42)
        
        result = core.get_param(param_name='count')
        
        assert result == 42
        assert isinstance(result, int)

    def test_get_param_returns_bool_for_toggle_type(self):
        """
        Tests that get_param() returns bool for PARAM_TYPE_TOGGLE.
        
        When parameter type is TOGGLE, the value should be returned as bool
        because get_param() routes to _get_param_bool().
        """
        test_param = {'name': 'enabled', 'type': PARAM_TYPE_TOGGLE}
        param.add_params([test_param])
        param.set_param(param_name='enabled', value=True)
        
        result = core.get_param(param_name='enabled')
        
        assert result is True
        assert isinstance(result, bool)

    def test_get_param_returns_list_for_list_type(self):
        """
        Tests that get_param() returns list for PARAM_TYPE_LIST.
        
        When parameter type is LIST, the value should be returned as list
        because get_param() routes to _get_param_list().
        """
        test_param = {'name': 'items', 'type': PARAM_TYPE_LIST}
        param.add_params([test_param])
        param.set_param(param_name='items', value=['a', 'b', 'c'])
        
        result = core.get_param(param_name='items')
        
        assert result == ['a', 'b', 'c']
        assert isinstance(result, list)

    def test_get_param_returns_dict_for_dict_type(self):
        """
        Tests that get_param() returns dict for PARAM_TYPE_DICT.
        
        When parameter type is DICT, the value should be returned as dict
        because get_param() routes to _get_param_dict().
        """
        test_param = {'name': 'config', 'type': PARAM_TYPE_DICT}
        param.add_params([test_param])
        param.set_param(param_name='config', value={'key': 'value'})
        
        result = core.get_param(param_name='config')
        
        assert result == {'key': 'value'}
        assert isinstance(result, dict)

    def test_get_param_returns_default_when_missing(self):
        """
        Tests that get_param() returns default when parameter not found.
        
        When parameter doesn't exist, the default should be returned
        because get_param() provides fallback behavior.
        """
        test_param = {'name': 'missing', 'type': PARAM_TYPE_TEXT}
        param.add_params([test_param])
        
        result = core.get_param(param_name='missing', default='fallback')
        
        assert result == 'fallback'

    def test_get_param_by_alias(self):
        """
        Tests that get_param() works with alias resolution.
        
        When called with alias, the parameter should be resolved and value returned
        because get_param() supports flexible resolution.
        """
        test_param = {'name': 'url', 'type': PARAM_TYPE_TEXT, 'aliases': ['--url', '-u']}
        param.add_params([test_param])
        param.set_param(param_name='url', value='https://example.com')
        
        result = core.get_param(alias='--url')
        
        assert result == 'https://example.com'

    def test_get_param_by_bind_name(self):
        """
        Tests that get_param() works with bind_name resolution.
        
        When called with bind_name, the parameter should be resolved and value returned
        because get_param() supports flexible resolution.
        """
        test_param = {'name': 'port', 'type': PARAM_TYPE_NUMBER, 'config-name': 'server_port'}
        param.add_params([test_param])
        param.set_param(param_name='port', value=8080)
        
        result = core.get_param(bind_name='server_port')
        
        assert result == 8080

    def test_get_param_strict_mode_raises_on_missing(self):
        """
        Tests that get_param() raises ValueError in strict mode when parameter missing.
        
        When strict=True and parameter definition not found, ValueError should be raised
        because strict mode enforces that the parameter must exist.
        """
        with pytest.raises(ValueError, match="Parameter definition not found"):
            core.get_param(param_name='nonexistent', strict=True)
