import json
import os
from spafw37 import cli, param
from spafw37 import file as spafw37_file
import spafw37.config
from spafw37 import config_func as config_func

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


def test_quoted_alias_like_value_is_accepted():
    setup_function()
    param.add_param({
        'name': 'textparam',
        'aliases': ['--textparam'],
        'type': 'text'
    })
    # Simulate a quoted token that looks like an alias in its raw form
    args = ['--textparam', '"-not-a-flag"']
    cli.handle_cli_args(args)
    # Value should be the quoted string (parser does not strip quotes)
    assert spafw37.config._config.get('textparam') == '"-not-a-flag"'


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


def test_file_not_found_raises_error(tmp_path):
    """Ensure that referencing a non-existent file raises a clear error.

    When using @file syntax with a file that doesn't exist, the system
    should raise an error indicating the file was not found.
    """
    setup_function()
    param.add_param({
        'name': 'data',
        'aliases': ['--data'],
        'type': 'text'
    })
    nonexistent = tmp_path / "does_not_exist.txt"
    args = ['--data', f'@{str(nonexistent)}']
    try:
        cli.handle_cli_args(args)
        assert False, "Expected error for non-existent file"
    except (FileNotFoundError, IOError, OSError):
        pass  # Expected


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


def test_is_short_alias_true():
    """Test is_short_alias returns True for short aliases.
    
    Short aliases match the pattern -x where x is a single character.
    This validates line 48.
    """
    setup_function()
    assert param.is_short_alias('-v') is True
    assert param.is_short_alias('-x') is True


def test_is_short_alias_false():
    """Test is_short_alias returns False for non-short aliases.
    
    Long aliases and regular strings should not match short alias pattern.
    This validates line 48.
    """
    setup_function()
    assert param.is_short_alias('--verbose') is False
    assert param.is_short_alias('value') is False


def test_is_long_alias_with_value_true():
    """Test is_long_alias_with_value for --param=value format.
    
    Should return True when alias has embedded value.
    This validates line 42.
    """
    setup_function()
    assert param.is_long_alias_with_value('--param=value') is True
    assert param.is_long_alias_with_value('--count=42') is True


def test_is_long_alias_with_value_false():
    """Test is_long_alias_with_value for other formats.
    
    Should return False when no embedded value.
    This validates line 42.
    """
    setup_function()
    assert param.is_long_alias_with_value('--param') is False
    assert param.is_long_alias_with_value('value') is False


def test_is_runtime_only_param_true():
    """Test is_runtime_only_param when param has runtime-only=True.
    
    Should return True for params marked as runtime-only.
    This validates line 86.
    """
    setup_function()
    runtime_param = {'name': 'test', 'runtime-only': True}
    assert param.is_runtime_only_param(runtime_param) is True


def test_is_runtime_only_param_false_for_none():
    """Test is_runtime_only_param when param is None.
    
    Should return False for None param.
    This validates line 86.
    """
    setup_function()
    assert param.is_runtime_only_param(None) is False


def test_parse_value_list_joined_to_string_for_non_list_param():
    """Test that list values are joined to string for non-list params.
    
    When a list is passed to a text/number/toggle param, join with spaces.
    This validates line 124.
    """
    setup_function()
    text_param = {'name': 'text', 'type': 'text'}
    value = param._parse_value(text_param, ['hello', 'world'])
    assert value == 'hello world'


def test_param_in_args_with_equals_format():
    """Test param_in_args detects --param=value format.
    
    Should return True when param appears as --alias=value in args.
    This validates line 214.
    """
    setup_function()
    test_param = {
        'name': 'count',
        'aliases': ['--count', '-c'],
        'type': 'number',
    }
    param.add_param(test_param)
    
    args = ['--count=42', 'other']
    assert param.param_in_args('count', args) is True


def test_parse_json_text_invalid_json():
    """Test _parse_json_text raises ValueError for invalid JSON.
    
    Should provide clear error message for malformed JSON.
    This validates lines 363-364.
    """
    setup_function()
    import pytest
    
    with pytest.raises(ValueError, match="Invalid JSON for dict parameter"):
        param._parse_json_text('{invalid}')


def test_parse_json_text_not_dict():
    """Test _parse_json_text raises ValueError when JSON is not an object.
    
    Must be a JSON object for dict parameters.
    This validates line 366.
    """
    setup_function()
    import pytest
    
    with pytest.raises(ValueError, match="Provided JSON must be an object"):
        param._parse_json_text('[1, 2, 3]')


def test_normalize_dict_input_not_string():
    """Test _normalize_dict_input raises ValueError for non-string input.
    
    Should validate input type and raise clear error.
    This validates line 384.
    """
    setup_function()
    import pytest
    
    with pytest.raises(ValueError, match="Invalid dict parameter value"):
        param._normalize_dict_input(123)


def test_read_file_raw_file_not_found():
    """Test _read_file_raw raises FileNotFoundError for missing file.
    
    Should provide clear error message with file path.
    This validates lines 400-401.
    """
    setup_function()
    import pytest
    
    with pytest.raises(FileNotFoundError, match="Parameter file not found"):
        spafw37_file._read_file_raw('/nonexistent/file.txt')


def test_read_file_raw_permission_denied(tmp_path):
    """Test _read_file_raw raises PermissionError for unreadable file.
    
    Should provide clear error message for permission issues.
    This validates lines 400-401.
    """
    setup_function()
    import pytest
    import stat
    
    # Create a file with no read permissions
    p = tmp_path / "noperm.txt"
    p.write_text('content')
    p.chmod(stat.S_IWUSR)  # Write only, no read
    
    try:
        with pytest.raises(PermissionError, match="Permission denied"):
            spafw37_file._read_file_raw(str(p))
    finally:
        # Restore permissions
        p.chmod(stat.S_IRUSR | stat.S_IWUSR)


def test_is_number_param_for_dict_type():
    """Test is_number_param returns False for dict params.
    
    Dict params should not be treated as number params.
    This validates line 147 (else branch).
    """
    setup_function()
    dict_param = {'name': 'mydict', 'type': 'dict'}
    assert param._is_number_param(dict_param) is False


def test_is_list_param_for_dict_type():
    """Test is_list_param returns False for dict params.
    
    Dict params should not be treated as list params.
    This validates line 153 (else branch).
    """
    setup_function()
    dict_param = {'name': 'mydict', 'type': 'dict'}
    assert param._is_list_param(dict_param) is False


