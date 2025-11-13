import json
import os
from spafw37 import cli, param
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


def test_dict_param_file_input(tmp_path):
    setup_function()
    param.add_param({
        'name': 'mydict',
        'aliases': ['--mydict'],
        'type': 'dict'
    })
    data = {"x": 10, "y": "yes"}
    p = tmp_path / "data.json"
    p.write_text(json.dumps(data))
    args = ['--mydict', f"@{str(p)}"]
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('mydict') == data


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


def test_text_param_file_input_reads_file(tmp_path):
    setup_function()
    param.add_param({
        'name': 'longtext',
        'aliases': ['--longtext'],
        'type': 'text'
    })
    p = tmp_path / "text.txt"
    p.write_text('hello world')
    args = ['--longtext', f"@{str(p)}"]
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('longtext') == 'hello world'


def test_list_param_file_input_splits_whitespace(tmp_path):
    setup_function()
    param.add_param({
        'name': 'items',
        'aliases': ['--items'],
        'type': 'list'
    })
    p = tmp_path / "items.txt"
    p.write_text('one two   three\nfour')
    args = ['--items', f"@{str(p)}"]
    cli.handle_cli_args(args)
    # Order preserved, whitespace collapsed by split()
    assert spafw37.config._config.get('items') == ['one', 'two', 'three', 'four']


def test_list_param_file_input_preserves_quoted_items(tmp_path):
    """Ensure that list params reading from files preserve quoted substrings.

    When a file is used as input for a list parameter and the file contains
    quoted strings with spaces (for example: 'one "two three" four'), the
    parser should treat "two three" as a single item in the resulting list.
    """
    setup_function()
    param.add_param({
        'name': 'items',
        'aliases': ['--items'],
        'type': 'list'
    })
    p = tmp_path / "quoted_items.txt"
    # Include quoted item containing a space
    p.write_text('one "two three" four')
    args = ['--items', f"@{str(p)}"]
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('items') == ['one', 'two three', 'four']


def test_number_param_file_input(tmp_path):
    """Ensure that number params can load values from files using @file syntax.

    This verifies that the @file mechanism works for all scalar param types,
    not just text and dict types.
    """
    setup_function()
    param.add_param({
        'name': 'count',
        'aliases': ['--count'],
        'type': 'number'
    })
    p = tmp_path / "number.txt"
    p.write_text('42')
    args = ['--count', f"@{str(p)}"]
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('count') == 42


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


def test_dict_param_with_equals_syntax_file(tmp_path):
    """Ensure dict params work with --param=@file syntax.

    This verifies that file loading works in the --param=value code path,
    not just the separate-token code path.
    """
    setup_function()
    param.add_param({
        'name': 'config',
        'aliases': ['--config'],
        'type': 'dict'
    })
    data = {"nested": {"key": "value"}}
    p = tmp_path / "config.json"
    p.write_text(json.dumps(data))
    args = [f'--config=@{str(p)}']
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('config') == data


def test_text_param_with_equals_syntax_file(tmp_path):
    """Ensure text params work with --param=@file syntax.

    This verifies the @file mechanism in the equals-syntax code path
    for text parameters.
    """
    setup_function()
    param.add_param({
        'name': 'message',
        'aliases': ['--message'],
        'type': 'text'
    })
    p = tmp_path / "message.txt"
    p.write_text('Hello from file')
    args = [f'--message=@{str(p)}']
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('message') == 'Hello from file'


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


def test_list_param_mixed_quoted_unquoted_items(tmp_path):
    """Ensure list params correctly handle files with mixed quoted and unquoted items.

    When a file contains both quoted items with spaces and regular unquoted
    items, the parser should correctly preserve quotes where needed and split
    unquoted items on whitespace.
    """
    setup_function()
    param.add_param({
        'name': 'items',
        'aliases': ['--items'],
        'type': 'list'
    })
    p = tmp_path / "mixed.txt"
    p.write_text('simple "quoted item" another "second quoted"')
    args = ['--items', f'@{str(p)}']
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('items') == ['simple', 'quoted item', 'another', 'second quoted']


def test_text_param_empty_file(tmp_path):
    """Ensure that loading an empty file for a text param returns empty string.

    When a text parameter loads from an empty file, it should receive an
    empty string as the value, not None or raise an error.
    """
    setup_function()
    param.add_param({
        'name': 'content',
        'aliases': ['--content'],
        'type': 'text'
    })
    p = tmp_path / "empty.txt"
    p.write_text('')
    args = ['--content', f'@{str(p)}']
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('content') == ''


def test_list_param_empty_file(tmp_path):
    """Ensure that loading an empty file for a list param returns empty list.

    When a list parameter loads from an empty file, it should receive an
    empty list as the value.
    """
    setup_function()
    param.add_param({
        'name': 'items',
        'aliases': ['--items'],
        'type': 'list'
    })
    p = tmp_path / "empty.txt"
    p.write_text('')
    args = ['--items', f'@{str(p)}']
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('items') == []


def test_dict_param_complex_nested_json(tmp_path):
    """Ensure dict params handle complex nested JSON structures.

    This verifies that the dict param type can handle realistic complex
    JSON with nested objects, arrays, and various data types.
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
    p = tmp_path / "schema.json"
    p.write_text(json.dumps(complex_data))
    args = ['--schema', f'@{str(p)}']
    cli.handle_cli_args(args)
    assert spafw37.config._config.get('schema') == complex_data

