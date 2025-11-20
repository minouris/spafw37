"""Tests for parameter resolution helpers.

Tests the _resolve_param_definition() and _get_param_definition_by_bind_name()
functions that resolve parameter definitions by name, bind name, or alias.
"""
import pytest
from spafw37 import param
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_CONFIG_NAME,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_TOGGLE,
    PARAM_TYPE_LIST,
    PARAM_TYPE_DICT,
    PARAM_DEFAULT,
)


def setup_function():
    """Reset param state before each test to ensure isolation."""
    param._params.clear()
    param._param_aliases.clear()
    param._xor_list.clear()


# Tests for _get_param_definition_by_bind_name()
def test_get_param_definition_by_bind_name_found():
    """Test _get_param_definition_by_bind_name finds param by bind name.
    
    Should return the parameter definition when bind name matches.
    This validates that bind name lookup works correctly.
    """
    setup_function()
    test_param = {
        PARAM_NAME: 'test-param',
        PARAM_CONFIG_NAME: 'test_bind_name',
        PARAM_TYPE: PARAM_TYPE_TEXT
    }
    param.add_param(test_param)
    
    result = param._get_param_definition_by_bind_name('test_bind_name')
    
    assert result is not None
    assert result[PARAM_NAME] == 'test-param'


def test_get_param_definition_by_bind_name_uses_param_name_fallback():
    """Test _get_param_definition_by_bind_name uses param name when no config name set.
    
    Should find param by param name when PARAM_CONFIG_NAME not specified.
    This validates that the bind name defaults to param name.
    """
    setup_function()
    test_param = {
        PARAM_NAME: 'default-name',
        PARAM_TYPE: PARAM_TYPE_TEXT
    }
    param.add_param(test_param)
    
    result = param._get_param_definition_by_bind_name('default-name')
    
    assert result is not None
    assert result[PARAM_NAME] == 'default-name'


def test_get_param_definition_by_bind_name_not_found():
    """Test _get_param_definition_by_bind_name returns None when not found.
    
    Should return None when no parameter has the specified bind name.
    This validates that the function handles missing parameters gracefully.
    """
    setup_function()
    
    result = param._get_param_definition_by_bind_name('nonexistent')
    
    assert result is None


# Tests for _resolve_param_definition()
def test_resolve_param_definition_by_param_name():
    """Test _resolve_param_definition finds param by parameter name.
    
    Should resolve parameter when param_name argument matches.
    This validates that named param_name lookup works.
    """
    setup_function()
    test_param = {
        PARAM_NAME: 'my-param',
        PARAM_CONFIG_NAME: 'my_param_bind',
        PARAM_ALIASES: ['--my-param', '-m'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    }
    param.add_param(test_param)
    
    result = param._resolve_param_definition(param_name='my-param')
    
    assert result is not None
    assert result[PARAM_NAME] == 'my-param'


def test_resolve_param_definition_by_bind_name():
    """Test _resolve_param_definition finds param by bind name.
    
    Should resolve parameter when bind_name argument matches.
    This validates that named bind_name lookup works.
    """
    setup_function()
    test_param = {
        PARAM_NAME: 'my-param',
        PARAM_CONFIG_NAME: 'my_param_bind',
        PARAM_ALIASES: ['--my-param', '-m'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    }
    param.add_param(test_param)
    
    result = param._resolve_param_definition(bind_name='my_param_bind')
    
    assert result is not None
    assert result[PARAM_NAME] == 'my-param'


def test_resolve_param_definition_by_alias():
    """Test _resolve_param_definition finds param by alias.
    
    Should resolve parameter when alias argument matches.
    This validates that named alias lookup works.
    """
    setup_function()
    test_param = {
        PARAM_NAME: 'my-param',
        PARAM_CONFIG_NAME: 'my_param_bind',
        PARAM_ALIASES: ['--my-param', '-m'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    }
    param.add_param(test_param)
    
    result = param._resolve_param_definition(alias='--my-param')
    
    assert result is not None
    assert result[PARAM_NAME] == 'my-param'


def test_resolve_param_definition_positional_finds_param_name():
    """Test _resolve_param_definition positional arg finds param by name first.
    
    Should resolve by param name when positional arg matches param name.
    This validates the failover pattern starts with param name.
    """
    setup_function()
    test_param = {
        PARAM_NAME: 'my-param',
        PARAM_CONFIG_NAME: 'my_param_bind',
        PARAM_ALIASES: ['--my-param', '-m'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    }
    param.add_param(test_param)
    
    result = param._resolve_param_definition('my-param')
    
    assert result is not None
    assert result[PARAM_NAME] == 'my-param'


def test_resolve_param_definition_positional_failover_to_bind_name():
    """Test _resolve_param_definition positional arg fails over to bind name.
    
    Should try bind name when positional arg doesn't match param name.
    This validates the failover pattern includes bind name.
    """
    setup_function()
    test_param = {
        PARAM_NAME: 'my-param',
        PARAM_CONFIG_NAME: 'my_param_bind',
        PARAM_ALIASES: ['--my-param', '-m'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    }
    param.add_param(test_param)
    
    result = param._resolve_param_definition('my_param_bind')
    
    assert result is not None
    assert result[PARAM_NAME] == 'my-param'


def test_resolve_param_definition_positional_failover_to_alias():
    """Test _resolve_param_definition positional arg fails over to alias.
    
    Should try alias when positional arg doesn't match param name or bind name.
    This validates the complete failover pattern.
    """
    setup_function()
    test_param = {
        PARAM_NAME: 'my-param',
        PARAM_CONFIG_NAME: 'my_param_bind',
        PARAM_ALIASES: ['--my-param', '-m'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    }
    param.add_param(test_param)
    
    result = param._resolve_param_definition('-m')
    
    assert result is not None
    assert result[PARAM_NAME] == 'my-param'


def test_resolve_param_definition_named_param_name_no_failover():
    """Test _resolve_param_definition named param_name with failover when other args None.
    
    Should try failover when param_name is specified but bind_name and alias are None.
    This validates that failover happens when only param_name is provided (even as named arg).
    Python 3.7 limitation means we can't distinguish positional from named argument.
    """
    setup_function()
    test_param = {
        PARAM_NAME: 'my-param',
        PARAM_CONFIG_NAME: 'my_param_bind',
        PARAM_ALIASES: ['--my-param', '-m'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    }
    param.add_param(test_param)
    
    # Using bind name value with param_name argument WILL find it via failover
    # because bind_name and alias are None (only param_name specified)
    result = param._resolve_param_definition(param_name='my_param_bind')
    
    assert result is not None
    assert result[PARAM_NAME] == 'my-param'


def test_resolve_param_definition_bind_name_specific_no_failover():
    """Test _resolve_param_definition bind_name is specific, no failover.
    
    Should return None when bind_name doesn't match, without trying other spaces.
    This validates that explicitly using bind_name argument is specific.
    """
    setup_function()
    test_param = {
        PARAM_NAME: 'my-param',
        PARAM_CONFIG_NAME: 'my_param_bind',
        PARAM_ALIASES: ['--my-param', '-m'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    }
    param.add_param(test_param)
    
    # Using param name value with bind_name argument should NOT find it
    result = param._resolve_param_definition(bind_name='my-param')
    
    assert result is None


def test_resolve_param_definition_not_found():
    """Test _resolve_param_definition returns None when param not found.
    
    Should return None when parameter doesn't exist in any address space.
    This validates that the function handles missing parameters gracefully.
    """
    setup_function()
    
    result = param._resolve_param_definition('nonexistent')
    
    assert result is None
