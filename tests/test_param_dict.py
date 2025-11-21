import json
import pytest
from spafw37 import cli, param
import spafw37.config
from spafw37 import config_func


def setup_function():
    # Reset module state between tests (similar to other test setup)
    param._param_aliases.clear()
    param._params.clear()
    param._preparse_args.clear()
    try:
        spafw37.config._config.clear()
        config_func._persistent_config.clear()
        param._xor_list.clear()
        cli._pre_parse_actions.clear()
        cli._post_parse_actions.clear()
    except Exception:
        pass


def test_dict_param_inline_json():
    """Test dict param with inline JSON string.
    
    Should parse JSON string and store as dict in config.
    This validates basic dict param functionality.
    """
    setup_function()
    param.add_param({
        'name': 'mydict',
        'aliases': ['--mydict'],
        'type': 'dict'
    })
    args = ['--mydict', '{"a":1,"b":"two"}']
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('mydict') == {"a": 1, "b": "two"}


def test_dict_param_multitoken_json():
    """Test dict param with JSON split across multiple tokens.
    
    Should reassemble tokens and parse as single JSON object.
    This validates multi-token JSON handling for dict params.
    """
    setup_function()
    param.add_param({
        'name': 'mydict',
        'aliases': ['--mydict'],
        'type': 'dict'
    })
    # Simulate JSON split into tokens (e.g. because of shell splitting)
    args = ['--mydict', '{', '"a":1', '}']
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('mydict') == {"a": 1}


def test_dict_param_with_equals_syntax_inline_json():
    """Ensure dict params work with --param=value syntax for inline JSON.

    This tests that the @file loading code path in _handle_long_alias_param
    works correctly for dict params when using the --param=value format.
    """
    setup_function()
    param.add_param({
        'name': 'config',
        'aliases': ['--config'],
        'type': 'dict'
    })
    args = ['--config={"key":"value"}']
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('config') == {"key": "value"}


def test_dict_param_invalid_json_raises_error():
    """Ensure that invalid JSON for dict params raises a clear error.

    When a dict parameter receives invalid JSON that cannot be parsed,
    the system should raise a ValueError with a helpful message.
    """
    setup_function()
    param.add_param({
        'name': 'data',
        'aliases': ['--data'],
        'type': 'dict'
    })
    args = ['--data', '{invalid json}']
    try:
        cli.handle_cli_args(args)
        assert False, "Expected ValueError for invalid JSON"
    except ValueError as e:
        assert 'JSON' in str(e) or 'dict' in str(e)


def test_dict_param_complex_nested_json():
    """Ensure dict params handle complex nested JSON structures.

    This verifies that the dict param type can handle realistic complex
    JSON with nested objects, arrays, and various data types when passed
    as inline JSON via CLI.
    """
    setup_function()
    param.add_param({
        'name': 'schema',
        'aliases': ['--schema'],
        'type': 'dict'
    })
    complex_data = {
        "users": [
            {"name": "Alice", "age": 30, "active": True},
            {"name": "Bob", "age": 25, "active": False}
        ],
        "settings": {
            "theme": "dark",
            "notifications": {
                "email": True,
                "sms": False
            }
        },
        "version": 1.5
    }
    # Pass complex JSON inline (not via file) to test dict param handling
    args = ['--schema', json.dumps(complex_data)]
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('schema') == complex_data


def test_parse_json_text_invalid_json():
    """Test _default_filter_dict raises ValueError for invalid JSON.
    
    Should provide clear error message for malformed JSON.
    This validates JSON parsing error handling for dict params.
    """
    setup_function()
    
    with pytest.raises(ValueError, match="Invalid JSON for dict parameter"):
        param._default_filter_dict('{invalid}')


def test_parse_json_text_not_dict():
    """Test _default_filter_dict raises ValueError when JSON is not an object.
    
    Must be a JSON object for dict parameters.
    This validates type checking for parsed JSON in dict params.
    """
    setup_function()
    
    with pytest.raises(ValueError, match="Dict parameter requires JSON object"):
        param._default_filter_dict('[1, 2, 3]')


def test_dict_param_multiple_inline_json_objects():
    """Test dict param with multiple inline JSON objects merges them.
    
    When multiple JSON objects are provided (space-separated), they should
    be parsed individually and merged into a single dict.
    This validates the edge case: --dict {"a":1} {"b":2}
    """
    setup_function()
    param.add_param({
        'name': 'config',
        'aliases': ['--config'],
        'type': 'dict'
    })
    # Simulate multiple JSON objects as single string value
    args = ['--config', '{"a":1} {"b":2}']
    cli.handle_cli_args(args)
    result = spafw37.config._config.get('config')
    assert result == {"a": 1, "b": 2}


def test_dict_param_multiple_objects_with_key_collision():
    """Test dict param with multiple objects having same keys.
    
    When multiple JSON objects have overlapping keys, later values
    should override earlier ones (recent wins strategy).
    This validates merge conflict resolution.
    """
    setup_function()
    param.add_param({
        'name': 'overrides',
        'aliases': ['--overrides'],
        'type': 'dict'
    })
    
    # Two objects with overlapping key "x"
    args = ['--overrides', '{"x":1,"y":2} {"x":99,"z":3}']
    cli.handle_cli_args(args)
    
    result = spafw37.config._config.get('overrides')
    # x should be 99 (from second object), y from first, z from second
    assert result == {"x": 99, "y": 2, "z": 3}


