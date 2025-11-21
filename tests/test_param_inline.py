"""Tests for inline parameter registration in param.py."""

import pytest
from spafw37 import param as spafw37_param
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_ALIASES,
    PARAM_SWITCH_LIST,
    PARAM_TYPE,
    PARAM_TYPE_TOGGLE,
)


def test_register_inline_param_with_string_reference():
    """Test that string parameter references are passed through.
    
    When _register_inline_param receives a string instead of a dict,
    it should return the string unchanged without registering anything.
    """
    result = spafw37_param._register_inline_param('existing_param')
    assert result == 'existing_param'


def test_register_inline_param_with_dict_and_switch_list():
    """Test inline parameter registration with nested switch list.
    
    When an inline parameter definition includes a PARAM_SWITCH_LIST,
    the function should recursively register nested parameters and
    normalize the switch list to contain parameter names.
    """
    # Clear existing params
    spafw37_param._params.clear()
    spafw37_param._param_aliases.clear()
    spafw37_param._xor_list.clear()
    
    # Create inline param with nested switch definitions
    inline_param = {
        PARAM_NAME: 'output_format',
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_ALIASES: ['--format'],
        PARAM_SWITCH_LIST: [
            {
                PARAM_NAME: 'format_json',
                PARAM_ALIASES: ['--json'],
            },
            {
                PARAM_NAME: 'format_xml',
                PARAM_ALIASES: ['--xml'],
            },
            'format_csv',  # String reference
        ]
    }
    
    result = spafw37_param._register_inline_param(inline_param)
    
    # Should return the param name
    assert result == 'output_format'
    
    # Main param should be registered
    assert 'output_format' in spafw37_param._params
    
    # Nested params should be registered
    assert 'format_json' in spafw37_param._params
    assert 'format_xml' in spafw37_param._params
    
    # Aliases should be registered
    assert spafw37_param._param_aliases['--format'] == 'output_format'
    assert spafw37_param._param_aliases['--json'] == 'format_json'
    assert spafw37_param._param_aliases['--xml'] == 'format_xml'
    
    # Switch list should be normalized to names
    registered_param = spafw37_param._params['output_format']
    assert registered_param[PARAM_SWITCH_LIST] == ['format_json', 'format_xml', 'format_csv']


def test_register_inline_param_already_registered():
    """Test that already-registered parameters are not re-registered.
    
    When an inline parameter with the same name already exists in the
    registry, the function should return the name without modifying
    the registry.
    """
    # Clear and register a param
    spafw37_param._params.clear()
    spafw37_param._param_aliases.clear()
    
    original_param = {
        PARAM_NAME: 'test_param',
        PARAM_ALIASES: ['--test'],
    }
    spafw37_param._params['test_param'] = original_param
    spafw37_param._param_aliases['--test'] = 'test_param'
    
    # Try to register with same name but different aliases
    duplicate_param = {
        PARAM_NAME: 'test_param',
        PARAM_ALIASES: ['--different'],
    }
    
    result = spafw37_param._register_inline_param(duplicate_param)
    
    # Should return the name
    assert result == 'test_param'
    
    # Original should still be there unchanged
    assert spafw37_param._params['test_param'] is original_param
    
    # New alias should NOT be registered (param was already there)
    assert '--different' not in spafw37_param._param_aliases


def test_get_param_name_with_string():
    """Test _get_param_name with string input.
    
    When given a string, the function should return it unchanged.
    """
    result = spafw37_param._get_param_name('param_name')
    assert result == 'param_name'


def test_get_param_name_with_dict():
    """Test _get_param_name with dict input.
    
    When given a parameter definition dict, the function should extract
    and return the PARAM_NAME value.
    """
    param_def = {PARAM_NAME: 'test_param', 'other': 'data'}
    result = spafw37_param._get_param_name(param_def)
    assert result == 'test_param'


def test_get_param_name_with_dict_no_name():
    """Test _get_param_name with dict missing PARAM_NAME.
    
    When given a dict without PARAM_NAME, the function should return
    empty string.
    """
    param_def = {'other': 'data'}
    result = spafw37_param._get_param_name(param_def)
    assert result == ''
