"""Tests for parameter helper functions in param.py.

Tests utility functions for alias management, param type checking, XOR relationships,
and value parsing.
"""
import pytest
from spafw37 import param, cli
from spafw37.constants import param as param_consts
import spafw37.config


def setup_function():
    """Reset param state before each test to ensure isolation."""
    param._params.clear()
    param._param_aliases.clear()
    param._xor_list.clear()
    param._preparse_args.clear()
    try:
        spafw37.config._config.clear()
        cli._pre_parse_actions.clear()
        cli._post_parse_actions.clear()
    except Exception:
        pass


# Alias registration and validation tests
def test_register_param_alias_valid():
    """Test add_param registers aliases correctly.
    
    Should store alias-to-param-name mappings in _param_aliases dict.
    This validates that alias registration works for valid alias formats.
    """
    setup_function()
    alias1 = '--test-alias'
    alias2 = '-t'
    param_name = 'test_param'
    param.add_param({
        param_consts.PARAM_NAME: param_name,
        param.PARAM_ALIASES: [alias1, alias2]
    })
    assert param._param_aliases[alias1] == param_name
    assert param._param_aliases[alias2] == param_name


def test_register_param_alias_invalid_raises():
    """Test add_param raises ValueError for invalid alias format.
    
    Should reject aliases that don't start with dashes.
    This validates that alias format validation works.
    """
    setup_function()
    invalid_alias = 'invalid-alias'  # Missing leading dashes
    _param = {
        param_consts.PARAM_NAME: 'test_param',
        param.PARAM_ALIASES: [invalid_alias]
    }
    with pytest.raises(ValueError, match="Invalid alias format"):
        param.add_param(_param)


def test_is_alias_format():
    """Test is_alias validates alias format correctly.
    
    Should return True for valid --long and -short formats.
    Should return False for invalid formats.
    """
    setup_function()
    valid_aliases = ['--valid-alias', '-v', '--another-one', '-a', '-Z', '-ab']
    invalid_aliases = ['invalid', '---too-many-dashes', '-abc', 'no-dash']
    for alias in valid_aliases:
        assert param.is_alias(alias) is True, f"Expected {alias} to be valid"
    for alias in invalid_aliases:
        assert param.is_alias(alias) is False, f"Expected {alias} to be invalid"


def test_is_param_alias_true():
    """Test is_param_alias returns True when alias belongs to param.
    
    Should return True when the specified alias is in the param's alias list.
    This validates alias membership checking.
    """
    setup_function()
    alias = '--my-alias'
    param_name = 'my_param'
    _param = {
        param_consts.PARAM_NAME: param_name,
        param.PARAM_ALIASES: [alias]
    }
    param.add_param(_param)
    assert param.is_param_alias(_param, alias) is True


def test_is_param_alias_false():
    """Test is_param_alias returns False when alias doesn't belong to param.
    
    Should return False when the specified alias is not in the param's alias list.
    This validates alias membership checking for negative cases.
    """
    setup_function()
    alias = '--my-alias'
    param_name = 'my_param'
    _param = {
        param_consts.PARAM_NAME: param_name,
        param.PARAM_ALIASES: [alias]
    }
    param.add_param(_param)
    assert param.is_param_alias(_param, '--other-alias') is False


def test_add_param_multiple_aliases():
    """Test add_param handles multiple aliases correctly.
    
    Should register all aliases for a single parameter.
    This validates that multiple aliases map to the same param.
    """
    setup_function()
    alias1 = '--alias'
    alias2 = '-t'
    param_name = 'test_alias_param'
    aliases = [alias1, alias2]
    param.add_param({
        param_consts.PARAM_NAME: param_name,
        param.PARAM_ALIASES: aliases
    })
    assert param._param_aliases[alias1] == param_name
    assert param._param_aliases[alias2] == param_name


def test_get_param_by_alias_unknown_returns_empty():
    """Test get_param_by_alias returns empty dict for unknown alias.
    
    Should return empty dict when alias is not registered.
    This validates graceful handling of missing aliases.
    """
    setup_function()
    assert param.get_param_by_alias('--no-such-alias') == {}


def test_get_param_by_alias_known_returns_param():
    """Test get_param_by_alias returns param definition for known alias.
    
    Should return the full param definition when alias is registered.
    This validates alias-to-param lookup.
    """
    setup_function()
    alias = '--known-alias'
    param_name = 'known_param'
    param.add_param({
        param_consts.PARAM_NAME: param_name,
        param.PARAM_ALIASES: [alias]
    })
    _param = param.get_param_by_alias(alias)
    assert _param.get(param_consts.PARAM_NAME) == param_name


# Type checking tests
def test_is_toggle_param_true():
    """Test _is_toggle_param returns True for toggle type params.
    
    Should identify params with PARAM_TYPE_TOGGLE.
    This validates toggle param detection.
    """
    setup_function()
    _param = {
        param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE
    }
    assert param._is_toggle_param(_param) is True


def test_is_toggle_param_false():
    """Test _is_toggle_param returns False for non-toggle params.
    
    Should return False for other param types.
    This validates toggle param detection for negative cases.
    """
    setup_function()
    _param = {
        param.PARAM_TYPE: param.PARAM_TYPE_TEXT
    }
    assert param._is_toggle_param(_param) is False


def test_is_toggle_param_default_false():
    """Test _is_toggle_param returns False when type is not specified.
    
    Should return False when param has no type specified.
    This validates default behavior for params without explicit type.
    """
    setup_function()
    _param = {
        param_consts.PARAM_NAME: 'some_param'
    }
    assert param._is_toggle_param(_param) is False


# XOR relationship tests
def test_set_param_xor_list_full_set():
    """Test XOR lists are set correctly when all params specify relationships.
    
    Should create bidirectional XOR relationships between all specified params.
    This validates that mutual exclusivity is properly registered.
    """
    option1 = "option1"
    option2 = "option2"
    option3 = "option3"
    param.add_params([{
        param_consts.PARAM_NAME: option1,
        param.PARAM_SWITCH_LIST: [option2, option3]
    }, {
        param_consts.PARAM_NAME: option2,
        param.PARAM_SWITCH_LIST: [option1, option3]
    }, {
        param_consts.PARAM_NAME: option3,
        param.PARAM_SWITCH_LIST: [option1, option2]
    }])
    assert param.has_xor_with(option1, option2)
    assert param.has_xor_with(option1, option3)
    assert param.has_xor_with(option2, option1)
    assert param.has_xor_with(option2, option3)
    assert param.has_xor_with(option3, option1)
    assert param.has_xor_with(option3, option2)


def test_set_param_xor_list_partial_set():
    """Test XOR lists are set correctly when only some params specify relationships.
    
    Should create transitive XOR relationships even when not all params specify all relationships.
    This validates that the framework infers bidirectional relationships.
    """
    option1 = "option1"
    option2 = "option2"
    option3 = "option3"
    param.add_params([{
        param_consts.PARAM_NAME: option1,
        param.PARAM_SWITCH_LIST: [option2]
    }, {
        param_consts.PARAM_NAME: option2,
        param.PARAM_SWITCH_LIST: [option3]
    }, {
        param_consts.PARAM_NAME: option3,
        param.PARAM_SWITCH_LIST: [option1]
    }])
    assert param.has_xor_with(option1, option2)
    assert param.has_xor_with(option1, option3)
    assert param.has_xor_with(option2, option1)
    assert param.has_xor_with(option2, option3)
    assert param.has_xor_with(option3, option1)
    assert param.has_xor_with(option3, option2)


# Value parsing tests
def test_parse_value_number_int():
    """Test _parse_value converts strings to integers for number params.
    
    Should parse integer strings and return int values unchanged.
    This validates number parsing for integers.
    """
    setup_function()
    _param = {param.PARAM_TYPE: param.PARAM_TYPE_NUMBER}
    assert param._parse_value(_param, "42") == 42
    assert param._parse_value(_param, 42) == 42


def test_parse_value_number_float_and_invalid():
    """Test _parse_value converts strings to floats and raises ValueError for invalid numbers.
    
    Should parse float strings correctly.
    Should raise ValueError for invalid number strings.
    """
    setup_function()
    _param = {param.PARAM_TYPE: param.PARAM_TYPE_NUMBER}
    assert param._parse_value(_param, "3.14") == 3.14
    assert param._parse_value(_param, 3.14) == 3.14
    try:
        param._parse_value(_param, "not-a-number")
        assert False, "Should have raised ValueError for invalid number"
    except ValueError:
        pass  # Expected


def test_parse_value_toggle_behavior():
    """Test _parse_value flips toggle param values correctly.
    
    Should toggle False to True, True to False.
    Should treat missing default as False and toggle to True.
    """
    setup_function()
    # explicit default False -> toggle to True
    param_false = {param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE, param.PARAM_DEFAULT: False}
    assert param._parse_value(param_false, None) is True
    # explicit default True -> toggle to False
    param_true = {param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE, param.PARAM_DEFAULT: True}
    assert param._parse_value(param_true, None) is False
    # no default provided -> treated as False -> toggles to True
    param_no_default = {param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE}
    assert param._parse_value(param_no_default, None) is True


def test_parse_value_list_behavior():
    """Test _parse_value handles list param values correctly.
    
    Should wrap scalar values in a list.
    Should return list values unchanged.
    """
    setup_function()
    _param = {param.PARAM_TYPE: param.PARAM_TYPE_LIST}
    # scalar value should be wrapped in a list
    assert param._parse_value(_param, "single") == ["single"]
    # when given a list, implementation should return it unchanged
    assert param._parse_value(_param, ["a", "b"]) == ["a", "b"]


def test_parse_value_default_returns_value():
    """Test _parse_value returns value unchanged for unspecified type.
    
    Should return the value as-is when param type is not specified.
    This validates default text behavior.
    """
    setup_function()
    _param = {}
    assert param._parse_value(_param, "hello") == "hello"


def test_is_runtime_only_param_true():
    """Test is_runtime_only_param when param has runtime-only=True.
    
    Should return True for params marked as runtime-only.
    This validates the runtime-only parameter detection.
    """
    setup_function()
    runtime_param = {'name': 'test', 'runtime-only': True}
    assert param.is_runtime_only_param(runtime_param) is True


def test_is_runtime_only_param_false_for_none():
    """Test is_runtime_only_param when param is None.
    
    Should return False for None param.
    This validates null-safety of runtime-only detection.
    """
    setup_function()
    assert param.is_runtime_only_param(None) is False


def test_parse_value_list_joined_to_string_for_non_list_param():
    """Test that list values are joined to string for non-list params.
    
    When a list is passed to a text/number/toggle param, join with spaces.
    This validates multi-token value handling for scalar params.
    """
    setup_function()
    text_param = {'name': 'text', 'type': 'text'}
    value = param._parse_value(text_param, ['hello', 'world'])
    assert value == 'hello world'


def test_is_number_param_for_dict_type():
    """Test is_number_param returns False for dict params.
    
    Dict params should not be treated as number params.
    This validates type checking logic for dict parameters.
    """
    setup_function()
    dict_param = {'name': 'mydict', 'type': 'dict'}
    assert param._is_param_type(dict_param, 'number') is False


def test_is_list_param_for_dict_type():
    """Test is_list_param returns False for dict params.
    
    Dict params should not be treated as list params.
    This validates type checking logic for dict parameters.
    """
    setup_function()
    dict_param = {'name': 'mydict', 'type': 'dict'}
    assert param._is_param_type(dict_param, 'list') is False
