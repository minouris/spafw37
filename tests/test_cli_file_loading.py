"""Tests for CLI @file loading mechanism.

These tests verify that the CLI module correctly handles @file syntax for loading
parameter values from files. This is a CLI-level feature, not a param module feature.
"""
import json
import pytest
import stat
from spafw37 import cli, param, file as spafw37_file
import spafw37.config
from spafw37 import config_func as config_func


def setup_function():
    """Reset module state between tests."""
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


def test_dict_param_file_input(tmp_path):
    """Test that dict params can load JSON from files using @file syntax.
    
    The CLI should recognize @file syntax and load the file contents,
    then parse the JSON before passing to the param module.
    """
    setup_function()
    param.add_param({
        'name': 'mydict',
        'aliases': ['--mydict'],
        'type': 'dict'
    })
    data = {"x": 10, "y": "yes"}
    file_path = tmp_path / "data.json"
    file_path.write_text(json.dumps(data))
    args = ['--mydict', f"@{str(file_path)}"]
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('mydict') == data


def test_text_param_file_input_reads_file(tmp_path):
    """Test that text params can read content from files using @file syntax.
    
    The CLI should load the file contents as a string for text parameters.
    """
    setup_function()
    param.add_param({
        'name': 'longtext',
        'aliases': ['--longtext'],
        'type': 'text'
    })
    file_path = tmp_path / "text.txt"
    file_path.write_text('hello world')
    args = ['--longtext', f"@{str(file_path)}"]
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('longtext') == 'hello world'


def test_list_param_file_input_splits_whitespace(tmp_path):
    """Test that list params split file content on whitespace using @file syntax.

    The CLI should load the file, split on whitespace, and pass the list
    to the param module. Order is preserved, whitespace is collapsed.
    """
    setup_function()
    param.add_param({
        'name': 'items',
        'aliases': ['--items'],
        'type': 'list'
    })
    file_path = tmp_path / "items.txt"
    file_path.write_text('one two   three\nfour')
    args = ['--items', f"@{str(file_path)}"]
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('items') == ['one', 'two', 'three', 'four']
def test_list_param_file_input_preserves_quoted_items(tmp_path):
    """Test that list params preserve quoted substrings when reading from files.

    When a file contains quoted strings with spaces (e.g., 'one "two three" four'),
    the CLI parser should treat "two three" as a single item in the resulting list.
    """
    setup_function()
    param.add_param({
        'name': 'items',
        'aliases': ['--items'],
        'type': 'list'
    })
    file_path = tmp_path / "quoted_items.txt"
    file_path.write_text('one "two three" four')
    args = ['--items', f"@{str(file_path)}"]
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('items') == ['one', 'two three', 'four']


def test_number_param_file_input(tmp_path):
    """Test that number params can load values from files using @file syntax.

    The CLI @file mechanism should work for all scalar param types,
    not just text and dict types.
    """
    setup_function()
    param.add_param({
        'name': 'count',
        'aliases': ['--count'],
        'type': 'number'
    })
    file_path = tmp_path / "number.txt"
    file_path.write_text('42')
    args = ['--count', f"@{str(file_path)}"]
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('count') == 42


def test_dict_param_with_equals_syntax_file(tmp_path):
    """Test that dict params work with --param=@file syntax.

    The CLI should support file loading in the --param=value code path,
    not just the separate-token code path.
    """
    setup_function()
    param.add_param({
        'name': 'config',
        'aliases': ['--config'],
        'type': 'dict'
    })
    data = {"nested": {"key": "value"}}
    file_path = tmp_path / "config.json"
    file_path.write_text(json.dumps(data))
    args = [f'--config=@{str(file_path)}']
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('config') == data


def test_text_param_with_equals_syntax_file(tmp_path):
    """Test that text params work with --param=@file syntax.

    The CLI @file mechanism should work in the equals-syntax code path
    for text parameters.
    """
    setup_function()
    param.add_param({
        'name': 'message',
        'aliases': ['--message'],
        'type': 'text'
    })
    file_path = tmp_path / "message.txt"
    file_path.write_text('Hello from file')
    args = [f'--message=@{str(file_path)}']
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('message') == 'Hello from file'


def test_list_param_mixed_quoted_unquoted_items(tmp_path):
    """Test that list params handle files with mixed quoted and unquoted items.

    When a file contains both quoted items with spaces and regular unquoted
    items, the CLI parser should correctly preserve quotes where needed and split
    unquoted items on whitespace.
    """
    setup_function()
    param.add_param({
        'name': 'items',
        'aliases': ['--items'],
        'type': 'list'
    })
    file_path = tmp_path / "mixed.txt"
    file_path.write_text('simple "quoted item" another "second quoted"')
    args = ['--items', f'@{str(file_path)}']
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('items') == ['simple', 'quoted item', 'another', 'second quoted']


def test_text_param_empty_file(tmp_path):
    """Test that loading an empty file for a text param returns empty string.

    When a text parameter loads from an empty file via CLI @file syntax,
    it should receive an empty string as the value, not None or raise an error.
    """
    setup_function()
    param.add_param({
        'name': 'content',
        'aliases': ['--content'],
        'type': 'text'
    })
    file_path = tmp_path / "empty.txt"
    file_path.write_text('')
    args = ['--content', f'@{str(file_path)}']
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('content') == ''


def test_list_param_empty_file(tmp_path):
    """Test that loading an empty file for a list param returns empty list.

    When a list parameter loads from an empty file via CLI @file syntax,
    it should receive an empty list as the value.
    """
    setup_function()
    param.add_param({
        'name': 'items',
        'aliases': ['--items'],
        'type': 'list'
    })
    file_path = tmp_path / "empty.txt"
    file_path.write_text('')
    args = ['--items', f'@{str(file_path)}']
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('items') == []


def test_file_not_found_raises_error(tmp_path):
    """Test that referencing a non-existent file raises a clear error.

    When using CLI @file syntax with a file that doesn't exist, the system
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


def test_dict_file_permission_denied(tmp_path):
    """Test that CLI raises PermissionError for unreadable dict param files.

    When a dict parameter references a file via @file syntax and the file
    is not readable, the CLI should raise a clear permission error.
    """
    setup_function()
    import pytest
    import stat
    
    param.add_param({
        'name': 'config',
        'aliases': ['--config'],
        'type': 'dict'
    })
    
    # Create a file with no read permissions
    file_path = tmp_path / "noperm.json"
    file_path.write_text('{"test": "data"}')
    file_path.chmod(stat.S_IWUSR)  # Write only, no read
    
    try:
        args = ['--config', f'@{str(file_path)}']
        with pytest.raises(PermissionError, match="Permission denied"):
            cli.handle_cli_args(args)
    finally:
        # Restore permissions so cleanup works
        file_path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def test_dict_file_invalid_json(tmp_path):
    """Test that CLI raises ValueError when dict param file contains invalid JSON.

    When loading a dict parameter from a file via @file syntax, the CLI
    should validate that the file contains valid JSON.
    """
    setup_function()
    import pytest
    
    param.add_param({
        'name': 'config',
        'aliases': ['--config'],
        'type': 'dict'
    })
    
    file_path = tmp_path / "invalid.json"
    file_path.write_text('{invalid json}')
    
    args = ['--config', f'@{str(file_path)}']
    with pytest.raises(ValueError, match="Invalid JSON"):
        cli.handle_cli_args(args)


def test_dict_file_not_dict(tmp_path):
    """Test that CLI raises ValueError when dict param file contains non-object JSON.

    Dict params must contain JSON objects, not arrays or primitives.
    When the file contains valid JSON but not an object, it should be rejected.
    """
    setup_function()
    import pytest
    
    param.add_param({
        'name': 'config',
        'aliases': ['--config'],
        'type': 'dict'
    })
    
    file_path = tmp_path / "array.json"
    file_path.write_text('[1, 2, 3]')
    
    args = ['--config', f'@{str(file_path)}']
    with pytest.raises(ValueError, match="JSON object"):
        cli.handle_cli_args(args)


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


def test_quoted_alias_like_value_is_accepted():
    """Test that quoted values that look like aliases are accepted.
    
    When a text param receives a quoted value that looks like a flag,
    it should be accepted as a literal value string.
    """
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


def test_read_file_raw_file_not_found():
    """Test _read_file_raw raises FileNotFoundError for missing file.
    
    Should provide clear error message with file path.
    This validates file-not-found error handling.
    """
    setup_function()
    
    with pytest.raises(FileNotFoundError, match="Parameter file not found"):
        spafw37_file._read_file_raw('/nonexistent/file.txt')


def test_read_file_raw_permission_denied(tmp_path):
    """Test _read_file_raw raises PermissionError for unreadable file.
    
    Should provide clear error message for permission issues.
    This validates permission error handling.
    """
    setup_function()
    
    # Create a file with no read permissions
    file_path = tmp_path / "noperm.txt"
    file_path.write_text('content')
    file_path.chmod(stat.S_IWUSR)  # Write only, no read
    
    try:
        with pytest.raises(PermissionError, match="Permission denied"):
            spafw37_file._read_file_raw(str(file_path))
    finally:
        # Restore permissions
        file_path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def test_parse_file_value_single_file(tmp_path):
    """Test _parse_file_value replaces single @file reference with contents.
    
    Should load the file and return its contents in place of the @file token.
    This validates basic file replacement functionality.
    """
    setup_function()
    
    file_path = tmp_path / "data.txt"
    file_path.write_text('file contents')
    
    result = cli._parse_file_value(f'@{str(file_path)}')
    assert result == 'file contents'


def test_parse_file_value_multiple_files(tmp_path):
    """Test _parse_file_value replaces multiple @file references.
    
    When value contains multiple @file tokens, all should be replaced
    with their respective file contents.
    This validates handling of multiple file references in one value.
    """
    setup_function()
    
    file1 = tmp_path / "first.txt"
    file1.write_text('{"a":1}')
    
    file2 = tmp_path / "second.txt"
    file2.write_text('{"b":2}')
    
    result = cli._parse_file_value(f'@{str(file1)} @{str(file2)}')
    assert result == '{"a":1} {"b":2}'


def test_parse_file_value_no_files():
    """Test _parse_file_value returns value unchanged when no @file references.
    
    When value doesn't contain @file tokens, it should be returned as-is.
    This validates no-op behavior for non-file values.
    """
    setup_function()
    
    result = cli._parse_file_value('{"inline":"json"}')
    assert result == '{"inline":"json"}'


def test_parse_file_value_mixed_inline_and_file(tmp_path):
    """Test _parse_file_value handles mix of inline content and @file references.
    
    Should preserve inline content while replacing only the @file tokens.
    This validates selective replacement in mixed-content values.
    """
    setup_function()
    
    file_path = tmp_path / "data.txt"
    file_path.write_text('{"from_file":true}')
    
    result = cli._parse_file_value(f'{{"inline":123}} @{str(file_path)}')
    assert result == '{"inline":123} {"from_file":true}'


def test_parse_file_value_file_not_found(tmp_path):
    """Test _parse_file_value raises FileNotFoundError for missing file.
    
    Should raise clear error when referenced file doesn't exist.
    This validates error handling for non-existent files.
    """
    setup_function()
    
    nonexistent = tmp_path / "missing.txt"
    with pytest.raises(FileNotFoundError):
        cli._parse_file_value(f'@{str(nonexistent)}')


def test_parse_file_value_file_permission_denied(tmp_path):
    """Test _parse_file_value raises PermissionError for unreadable file.
    
    Should raise clear error when file cannot be read.
    This validates error handling for permission issues.
    """
    setup_function()
    
    file_path = tmp_path / "noperm.txt"
    file_path.write_text('content')
    file_path.chmod(stat.S_IWUSR)  # Write only, no read
    
    try:
        with pytest.raises(PermissionError):
            cli._parse_file_value(f'@{str(file_path)}')
    finally:
        # Restore permissions
        file_path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def test_parse_file_value_ignores_email_addresses():
    """Test _parse_file_value doesn't treat @ in email addresses as file references.
    
    When value contains email addresses, the @ symbol should not trigger
    file loading. Only standalone @filepath patterns should be replaced.
    This validates handling of @ in non-file contexts.
    """
    setup_function()
    
    # Email addresses should pass through unchanged
    result = cli._parse_file_value('user@example.com')
    assert result == 'user@example.com'
    
    result = cli._parse_file_value('Contact: admin@domain.org for help')
    assert result == 'Contact: admin@domain.org for help'


def test_parse_file_value_inside_json_structure(tmp_path):
    """Test _parse_file_value handles @file references inside JSON structures.
    
    Should replace @file tokens even when they appear inside JSON objects,
    stopping at structural characters like } or ].
    This validates file references embedded in JSON syntax.
    """
    setup_function()
    
    file_path = tmp_path / "data.json"
    file_path.write_text('{"nested": "value"}')
    
    # Test inside JSON object
    result = cli._parse_file_value(f"{{'key': @{str(file_path)}}}")
    assert result == "{'key': {\"nested\": \"value\"}}"
    
    # Test inside JSON array
    result = cli._parse_file_value(f"[@{str(file_path)}]")
    assert result == '[{"nested": "value"}]'
    
    # Test with comma separator
    result = cli._parse_file_value(f"[@{str(file_path)}, 'other']")
    assert result == '[{"nested": "value"}, \'other\']'


def test_parse_file_value_with_parentheses(tmp_path):
    """Test _parse_file_value stops at closing parenthesis.
    
    When @file reference appears in contexts with parentheses,
    the file path should stop at the closing paren.
    This validates delimiter handling in function-like syntax.
    """
    setup_function()
    
    file_path = tmp_path / "value.txt"
    file_path.write_text('42')
    
    result = cli._parse_file_value(f"process(@{str(file_path)})")
    assert result == "process(42)"

