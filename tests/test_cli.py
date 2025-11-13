import pytest
from spafw37 import cli, config_func as config, param, command
import spafw37.config
from spafw37.constants.command import (
    COMMAND_ACTION,
    COMMAND_DESCRIPTION,
    COMMAND_NAME,
    COMMAND_REQUIRED_PARAMS,
)
from spafw37.constants.config import (
    CONFIG_INFILE_ALIAS,
    CONFIG_INFILE_PARAM,
    CONFIG_OUTFILE_PARAM,
)
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_PERSISTENCE,
    PARAM_PERSISTENCE_NEVER,
    PARAM_REQUIRED,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_DEFAULT,
    PARAM_CONFIG_NAME,
    PARAM_SWITCH_LIST,
    PARAM_HAS_VALUE,
)
import spafw37.constants.param as param_consts
import spafw37.configure
import re
from unittest.mock import patch, mock_open
import json

from test_command import _reset_command_module

def setup_function():
    # reset module state between tests
    param._param_aliases.clear()
    param._params.clear()
    param._preparse_args.clear()
    try:
        config._non_persisted_config_names.clear()
        spafw37.config._config.clear()
        config._persistent_config.clear()
        param._xor_list.clear()
        cli._pre_parse_actions.clear()
        cli._post_parse_actions.clear()
        _reset_command_module()
    except Exception:
        pass

def test_register_param_alias_valid():
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
    setup_function()
    invalid_alias = 'invalid-alias'  # Missing leading dashes
    _param = {
        param_consts.PARAM_NAME: 'test_param',
        param.PARAM_ALIASES: [invalid_alias]
    }
    with pytest.raises(ValueError, match="Invalid alias format"):
        param.add_param(_param)

def test_is_alias_format():
    setup_function()
    valid_aliases = ['--valid-alias', '-v', '--another-one', '-a', '-Z', '-ab']
    invalid_aliases = ['invalid', '---too-many-dashes', '-abc', 'no-dash']
    for alias in valid_aliases:
        assert param.is_alias(alias) is True, f"Expected {alias} to be valid"
    for alias in invalid_aliases:
        assert param.is_alias(alias) is False, f"Expected {alias} to be invalid"

def test_is_param_alias_true():
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
    setup_function()
    alias = '--my-alias'
    param_name = 'my_param'
    _param = {
        param_consts.PARAM_NAME: param_name,
        param.PARAM_ALIASES: [alias]
    }
    param.add_param(_param)
    # alias does not belong to the param
    assert param.is_param_alias(_param, '--other-alias') is False

def test_add_param_multiple_aliases():
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
    setup_function()
    assert param.get_param_by_alias('--no-such-alias') == {}

def test_get_param_by_alias_known_returns_param():
    setup_function()
    alias = '--known-alias'
    param_name = 'known_param'
    param.add_param({
        param_consts.PARAM_NAME: param_name,
        param.PARAM_ALIASES: [alias]
    })
    _param = param.get_param_by_alias(alias)
    assert _param.get(param_consts.PARAM_NAME) == param_name

def test_set_default_param_values():
    setup_function()
    bind_name = 'test_bind'
    param_name = 'test_param'
    param.add_param({
        param.PARAM_CONFIG_NAME: bind_name,
        param_consts.PARAM_NAME: param_name,
        param.PARAM_DEFAULT: 'default_value'
    })
    cli._set_defaults()
    assert spafw37.config._config[bind_name] == 'default_value'

def test_set_default_param_toggle_with_default_true():
    setup_function()
    bind_name = 'toggle_param'
    param_name = 'toggle_param_name'
    param.add_param({
        param.PARAM_CONFIG_NAME: bind_name,
        param_consts.PARAM_NAME: param_name,
        param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE,
        param.PARAM_DEFAULT: True
    })
    cli._set_defaults()
    assert spafw37.config._config[bind_name] is True

def test_set_default_param_toggle_with_no_default():
    setup_function()
    bind_name = 'toggle_no_default'
    param_name = 'toggle_no_default_name'
    param.add_param({
        param.PARAM_CONFIG_NAME: bind_name,
        param_consts.PARAM_NAME: param_name,
        param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE
    })
    cli._set_defaults()
    assert spafw37.config._config[bind_name] is False

def test_is_toggle_param_true():
    setup_function()
    _param = {
        param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE
    }
    assert param.is_toggle_param(_param) is True

def test_is_toggle_param_false():
    setup_function()
    _param = {
        param.PARAM_TYPE: param.PARAM_TYPE_TEXT
    }
    assert param.is_toggle_param(_param) is False

def test_is_toggle_param_default_false():
    setup_function()
    _param = {
        param_consts.PARAM_NAME: 'some_param'
    }
    assert param.is_toggle_param(_param) is False

def test_set_param_xor_list_full_set():
    """
    Verifies that xor lists are set when all params are specified
    """
    option1 = "option1"
    option2 = "option2"
    option3 = "option3"
    param.add_params([{
        param_consts.PARAM_NAME: option1,
        param.PARAM_SWITCH_LIST: [ option2, option3 ]
    },{
        param_consts.PARAM_NAME: option2,
        param.PARAM_SWITCH_LIST: [ option1, option3 ]
    },{
        param_consts.PARAM_NAME: option3,
        param.PARAM_SWITCH_LIST: [ option1, option2 ]
    }
    ])
    assert param.has_xor_with(option1, option2)
    assert param.has_xor_with(option1, option3)
    assert param.has_xor_with(option2, option1)
    assert param.has_xor_with(option2, option3)
    assert param.has_xor_with(option3, option1)
    assert param.has_xor_with(option3, option2)

def test_set_param_xor_list_partial_set():
    """
    Verifies that xor lists are set when xors are only specified
     for some params.
    """
    option1 = "option1"
    option2 = "option2"
    option3 = "option3"
    param.add_params([{
        param_consts.PARAM_NAME: option1,
        param.PARAM_SWITCH_LIST: [ option2 ]
    },{
        param_consts.PARAM_NAME: option2,
        param.PARAM_SWITCH_LIST: [ option3 ]
    },{
        param_consts.PARAM_NAME: option3,
        param.PARAM_SWITCH_LIST: [ option1 ]
    }
    ])
    assert param.has_xor_with(option1, option2)
    assert param.has_xor_with(option1, option3)
    assert param.has_xor_with(option2, option1)
    assert param.has_xor_with(option2, option3)
    assert param.has_xor_with(option3, option1)
    assert param.has_xor_with(option3, option2)


def test_parse_value_number_int():
    setup_function()
    _param = { param.PARAM_TYPE: param.PARAM_TYPE_NUMBER }
    assert param._parse_value(_param, "42") == 42
    assert param._parse_value(_param, 42) == 42

def test_parse_value_number_float_and_invalid():
    setup_function()
    _param = { param.PARAM_TYPE: param.PARAM_TYPE_NUMBER }
    assert param._parse_value(_param, "3.14") == 3.14
    assert param._parse_value(_param, 3.14) == 3.14
    assert param._parse_value(_param, "not-a-number") == 0

def test_parse_value_toggle_behavior():
    setup_function()
    # explicit default False -> toggle to True
    param_false = { param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE, param.PARAM_DEFAULT: False }
    assert param._parse_value(param_false, None) is True
    # explicit default True -> toggle to False
    param_true = { param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE, param.PARAM_DEFAULT: True }
    assert param._parse_value(param_true, None) is False
    # no default provided -> treated as False -> toggles to True
    param_no_default = { param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE }
    assert param._parse_value(param_no_default, None) is True

def test_parse_value_list_behavior():
    setup_function()
    _param = { param.PARAM_TYPE: param.PARAM_TYPE_LIST }
    # scalar value should be wrapped in a list
    assert param._parse_value(_param, "single") == ["single"]
    # when given a list, implementation should return it unchanged
    assert param._parse_value(_param, ["a", "b"]) == ["a", "b"]

def test_parse_value_default_returns_value():
    setup_function()
    # unspecified type should return the value unchanged
    _param = {}
    assert param._parse_value(_param, "hello") == "hello"

def test_parse_command_line_toggle_param():
    setup_function()
    param.add_params([{
        param_consts.PARAM_NAME: "some_flag",
        param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE,
        param.PARAM_ALIASES: ['--some-flag', '-s']
    },{
        param_consts.PARAM_NAME: "verbose",
        param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE,
        param.PARAM_ALIASES: ['--verbose', '-v']
    }])
    args = ["--some-flag", "-v"]
    cli.handle_cli_args(args)
    assert spafw37.config._config["some_flag"] is True
    assert spafw37.config._config["verbose"] is True

def test_parse_command_line_param_with_text_value():
    setup_function()
    param.add_params([{
        param_consts.PARAM_NAME: "output_file",
        param.PARAM_TYPE: param.PARAM_TYPE_TEXT,
        param.PARAM_ALIASES: ['--output-file', '-o']
    }])
    args = ["--output-file", "result.txt"]
    cli.handle_cli_args(args)
    assert spafw37.config._config["output_file"] == "result.txt"

def test_parse_command_line_param_with_number_value():
    setup_function()
    param.add_params([{
        param_consts.PARAM_NAME: "max_retries",
        param.PARAM_TYPE: param.PARAM_TYPE_NUMBER,
        param.PARAM_ALIASES: ['--max-retries', '-m']
    }])
    args = ["--max-retries", "5"]
    cli.handle_cli_args(args)
    assert spafw37.config._config["max_retries"] == 5

def test_parse_command_line_param_with_list_value():
    setup_function()
    param.add_params([{
        param_consts.PARAM_NAME: "input_files",
        param.PARAM_TYPE: param.PARAM_TYPE_LIST,
        param.PARAM_ALIASES: ['--input-files', '-i']
    }])
    args = ["--input-files", "file1.txt", "file2.txt"]
    cli.handle_cli_args(args)
    assert spafw37.config._config["input_files"] == ["file1.txt", "file2.txt"]

def test_parse_command_line_param_with_list_value_across_multi_params():
    setup_function()
    param.add_params([{
        param_consts.PARAM_NAME: "input_files",
        param.PARAM_TYPE: param.PARAM_TYPE_LIST,
        param.PARAM_ALIASES: ['--input-files', '-i']
    }])
    args = ["--input-files", "file1.txt", "--input-files", "file2.txt"]
    cli.handle_cli_args(args)
    assert spafw37.config._config["input_files"] == ["file1.txt", "file2.txt"]

def test_parse_command_line_param_with_toggle_value():
    setup_function()
    param.add_params([{
        param_consts.PARAM_NAME: "some_flag",
        param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE,
        param.PARAM_ALIASES: ['--some-flag', '-s'],
        param.PARAM_DEFAULT: True
    },{
        param_consts.PARAM_NAME: "verbose",
        param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE,
        param.PARAM_ALIASES: ['--verbose', '-v']
    }])
    args = ["--some-flag", "-v"]
    cli.handle_cli_args(args)
    assert spafw37.config._config["some_flag"] is False
    assert spafw37.config._config["verbose"] is True

def test_parse_command_line_param_with_equals_value():
    setup_function()
    param.add_params([{
        param_consts.PARAM_NAME: "config_path",
        param.PARAM_TYPE: param.PARAM_TYPE_TEXT,
        param.PARAM_ALIASES: ['--config-path', '-c']
    }])
    args = ["--config-path=/etc/config.json"]
    cli.handle_cli_args(args)
    assert spafw37.config._config["config_path"] == "/etc/config.json"

def test_add_pre_parse_actions():
    setup_function()
    action_called = {'called': False}
    def sample_action():
        action_called['called'] = True
    cli.add_pre_parse_actions([sample_action])
    cli._do_pre_parse_actions()
    assert action_called['called'] is True

def test_add_post_parse_actions():
    setup_function()
    action_called = {'called': False}
    def sample_action():
        action_called['called'] = True
    cli.add_post_parse_actions([sample_action])
    cli._do_post_parse_actions()
    assert action_called['called'] is True

def test_xor_clashing_params_raise_error():
    setup_function()
    param.add_params([{
        param_consts.PARAM_NAME: "option1",
        param.PARAM_ALIASES: ["--option1"],
        param.PARAM_SWITCH_LIST: [ "option2" ],
        param.PARAM_DEFAULT: False
    },{
        param_consts.PARAM_NAME: "option2",
        param.PARAM_ALIASES: ["--option2"],
        param.PARAM_SWITCH_LIST: [ "option1" ],
        param.PARAM_DEFAULT: False
    }])
    args = ["--option1", "--option2"]
    try:
        cli.handle_cli_args(args)
        assert False, "Expected ValueError for clashing xor params"
    except ValueError as e:
        assert str(e) == "Conflicting parameters provided: option1 and option2"

def test_xor_with_non_toggle_text_params():
    """Test that switch-list works correctly with TEXT type params."""
    setup_function()
    param.add_params([{
        param_consts.PARAM_NAME: "format",
        param.PARAM_ALIASES: ["--format"],
        param.PARAM_TYPE: param.PARAM_TYPE_TEXT,
        param.PARAM_SWITCH_LIST: ["output-type"]
    },{
        param_consts.PARAM_NAME: "output-type",
        param.PARAM_ALIASES: ["--output-type"],
        param.PARAM_TYPE: param.PARAM_TYPE_TEXT,
        param.PARAM_SWITCH_LIST: ["format"]
    }])
    
    # Test 1: Both params explicitly set should raise error
    args = ["--format", "json", "--output-type", "csv"]
    try:
        cli.handle_cli_args(args)
        assert False, "Expected ValueError for conflicting text params"
    except ValueError as e:
        assert "Conflicting parameters provided" in str(e)
    
    # Reset for next test
    setup_function()
    param.add_params([{
        param_consts.PARAM_NAME: "format",
        param.PARAM_ALIASES: ["--format"],
        param.PARAM_TYPE: param.PARAM_TYPE_TEXT,
        param.PARAM_SWITCH_LIST: ["output-type"]
    },{
        param_consts.PARAM_NAME: "output-type",
        param.PARAM_ALIASES: ["--output-type"],
        param.PARAM_TYPE: param.PARAM_TYPE_TEXT,
        param.PARAM_SWITCH_LIST: ["format"]
    }])
    
    # Test 2: Only one param set should work
    args = ["--format", "json"]
    cli.handle_cli_args(args)
    assert spafw37.config._config.get("format") == "json"
    assert spafw37.config._config.get("output-type") is None

def test_xor_with_non_toggle_number_params():
    """Test that switch-list works correctly with NUMBER type params."""
    setup_function()
    param.add_params([{
        param_consts.PARAM_NAME: "max-count",
        param.PARAM_ALIASES: ["--max-count"],
        param.PARAM_TYPE: param.PARAM_TYPE_NUMBER,
        param.PARAM_SWITCH_LIST: ["limit"]
    },{
        param_consts.PARAM_NAME: "limit",
        param.PARAM_ALIASES: ["--limit"],
        param.PARAM_TYPE: param.PARAM_TYPE_NUMBER,
        param.PARAM_SWITCH_LIST: ["max-count"]
    }])
    
    # Test 1: Both params explicitly set should raise error
    args = ["--max-count", "100", "--limit", "50"]
    try:
        cli.handle_cli_args(args)
        assert False, "Expected ValueError for conflicting number params"
    except ValueError as e:
        assert "Conflicting parameters provided" in str(e)
    
    # Reset for next test
    setup_function()
    param.add_params([{
        param_consts.PARAM_NAME: "max-count",
        param.PARAM_ALIASES: ["--max-count"],
        param.PARAM_TYPE: param.PARAM_TYPE_NUMBER,
        param.PARAM_SWITCH_LIST: ["limit"]
    },{
        param_consts.PARAM_NAME: "limit",
        param.PARAM_ALIASES: ["--limit"],
        param.PARAM_TYPE: param.PARAM_TYPE_NUMBER,
        param.PARAM_SWITCH_LIST: ["max-count"]
    }])
    
    # Test 2: Only one param set should work
    args = ["--max-count", "100"]
    cli.handle_cli_args(args)
    assert spafw37.config._config.get("max-count") == 100
    assert spafw37.config._config.get("limit") is None

def test_xor_with_mixed_param_types():
    """Test that switch-list works with mixed parameter types (TEXT and NUMBER)."""
    setup_function()
    param.add_params([{
        param_consts.PARAM_NAME: "count",
        param.PARAM_ALIASES: ["--count"],
        param.PARAM_TYPE: param.PARAM_TYPE_NUMBER,
        param.PARAM_SWITCH_LIST: ["size"]
    },{
        param_consts.PARAM_NAME: "size",
        param.PARAM_ALIASES: ["--size"],
        param.PARAM_TYPE: param.PARAM_TYPE_TEXT,
        param.PARAM_SWITCH_LIST: ["count"]
    }])
    
    # Both params explicitly set should raise error even with different types
    args = ["--count", "42", "--size", "large"]
    try:
        cli.handle_cli_args(args)
        assert False, "Expected ValueError for conflicting mixed-type params"
    except ValueError as e:
        assert "Conflicting parameters provided" in str(e)

def test_add_command_registers_command():
    setup_function()
    def sample_command_action():
        pass
    _command = {
        COMMAND_NAME: "sample-command",
        COMMAND_REQUIRED_PARAMS: [],
        COMMAND_DESCRIPTION: "A sample command for testing",
        COMMAND_ACTION: sample_command_action
    }
    command.add_command(_command)
    assert command.get_command("sample-command") == _command

def test_handle_command():
    setup_function()
    _command = {
        COMMAND_NAME: "save-user-config",
        COMMAND_REQUIRED_PARAMS: [ CONFIG_OUTFILE_PARAM ],
        COMMAND_DESCRIPTION: "Saves the current user configuration to a file",
        COMMAND_ACTION: config.save_user_config
    }
    command.add_command(_command)
    param.add_param({
        PARAM_NAME: CONFIG_OUTFILE_PARAM,
        PARAM_DESCRIPTION: 'A JSON file to save configuration to',
        PARAM_CONFIG_NAME: CONFIG_OUTFILE_PARAM,
        PARAM_TYPE: 'string',
        PARAM_ALIASES: [CONFIG_INFILE_ALIAS,'-s'],
        PARAM_REQUIRED: False,
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    })
    args = ["save-user-config", CONFIG_INFILE_ALIAS, "config.json"]
    cli.handle_cli_args(args)
    assert command._is_command_finished("save-user-config")

def test_handle_command_missing_required_param_raises():
    setup_function()
    _command = {
        COMMAND_NAME: "save-user-config",
        COMMAND_REQUIRED_PARAMS: [ CONFIG_OUTFILE_PARAM ],
        COMMAND_DESCRIPTION: "Saves the current user configuration to a file",
        COMMAND_ACTION: config.save_user_config
    }
    command.add_command(_command)
    param.add_param({
        PARAM_NAME: CONFIG_OUTFILE_PARAM,
        PARAM_DESCRIPTION: 'A JSON file to save configuration to',
        PARAM_CONFIG_NAME: CONFIG_OUTFILE_PARAM,
        PARAM_TYPE: 'string',
        PARAM_ALIASES: ['--save-config','-s'],
        PARAM_REQUIRED: False,
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    })
    args = ["save-user-config"]
    with pytest.raises(ValueError, match=f"Missing required parameter '{CONFIG_OUTFILE_PARAM}' for command 'save-user-config'"):
        cli.handle_cli_args(args)

def test_handle_command_executes_action():
    setup_function()
    action_executed = {'executed': False}
    def sample_action():
        action_executed['executed'] = True
    _command = {
        COMMAND_NAME: "sample-command",
        COMMAND_REQUIRED_PARAMS: [],
        COMMAND_DESCRIPTION: "A sample command for testing",
        COMMAND_ACTION: sample_action
    }
    command.add_command(_command)
    args = ["sample-command"]
    cli.handle_cli_args(args)
    command.run_command_queue()
    assert action_executed['executed'] is True

def test_capture_param_values_toggle_direct() -> None:
    """Directly exercise capture_param_values for a toggle parameter."""
    setup_function()
    _param = { param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE }
    # For toggle params, capture_param_values should immediately return (1, True)
    result = cli.capture_param_values(['--some-flag'], _param)
    assert result == (1, True)

def test_capture_param_values_two_aliases_breaks_out():
    setup_function()
    # Register two params with distinct aliases
    param.add_params([{
        param_consts.PARAM_NAME: "first",
        param.PARAM_TYPE: param.PARAM_TYPE_LIST,
        param.PARAM_ALIASES: ['--first', '-f']
    },{
        param_consts.PARAM_NAME: "second",
        param.PARAM_TYPE: param.PARAM_TYPE_TEXT,
        param.PARAM_ALIASES: ['--second', '-s']
    }])
    # Capture values for the first param but provide the second param's alias immediately after
    _param = param.get_param_by_alias('--first')
    result = cli.capture_param_values(['--first', '--second'], _param)
    # Expect capture to break out and return offset 1 (only consumed '--first') and an empty list of values
    assert result == (1, [])

def test_capture_param_values_breaks_on_command():
    setup_function()
    # Register a command that should break capture when encountered
    _command = {
        COMMAND_NAME: "break-command",
        COMMAND_REQUIRED_PARAMS: [],
        COMMAND_DESCRIPTION: "Command used to break capture",
        COMMAND_ACTION: lambda: None
    }
    command.add_command(_command)

    # Register a list param with an alias
    param.add_param({
        param_consts.PARAM_NAME: "files",
        param.PARAM_TYPE: param.PARAM_TYPE_LIST,
        param.PARAM_ALIASES: ['--files', '-f']
    })

    _param = param.get_param_by_alias('--files')
    # Simulate args where the command appears right after the alias
    args = ['--files', 'break-command']
    result = cli.capture_param_values(args, _param)
    # Expect capture to break out and return offset 1 (only consumed '--files') and an empty list of values
    assert result == (1, [])

def test_do_pre_parse_actions_swallow_exception():
    setup_function()
    called = {'done': False}
    def raising_action():
        raise RuntimeError("pre-error")
    def succeeding_action():
        called['done'] = True
    cli.add_pre_parse_actions([raising_action, succeeding_action])
    # Should not raise despite the first action throwing
    cli._do_pre_parse_actions()
    assert called['done'] is True

def test_do_post_parse_actions_reraises_exception():
    setup_function()
    def raising_action():
        raise ValueError("post-error")
    cli.add_post_parse_actions([raising_action])
    try:
        cli._do_post_parse_actions()
        assert False, "Expected ValueError from post-parse action"
    except ValueError as e:
        assert str(e) == "post-error"

def test_run_command_queue_reraises_on_action_exception():
    setup_function()
    def raising_action():
        raise ValueError("cmd-error")
    err_cmd_name = 'err-cmd'
    _command = {
        COMMAND_NAME: err_cmd_name,
        COMMAND_REQUIRED_PARAMS: [],
        COMMAND_ACTION: raising_action
    }
    command.add_command(_command)
    command.queue_command(err_cmd_name)
    try:
        command.run_command_queue()
        assert False, "Expected ValueError from queued command action"
    except ValueError as e:
        assert str(e) == "cmd-error"

def test_handle_long_alias_param_unknown_raises():
    setup_function()
    # Ensure no config params so test_switch_xor doesn't try to inspect _param
    try:
        cli._handle_long_alias_param("--no-such=val")
        assert False, "Expected ValueError for unknown long alias"
    except ValueError as e:
        assert str(e) == "Unknown parameter alias: --no-such"

def test_handle_command_unknown_raises():
    setup_function()
    try:
        cli._handle_command("no-such-command")
        assert False, "Expected ValueError for unknown command"
    except ValueError as e:
        assert str(e) == "Unknown command alias: no-such-command"

def test_parse_command_line_unknown_arg_raises():
    setup_function()
    try:
        cli._parse_command_line(["--this-does-not-exist"])
        assert False, "Expected ValueError for unknown argument"
    except ValueError as e:
        assert str(e) == "Unknown parameter alias: --this-does-not-exist"

def test_parse_command_line_unknown_argument_raises():
    setup_function()
    try:
        cli._parse_command_line(["unknown-argument"])
        assert False, "Expected ValueError for unknown argument"
    except ValueError as e:
        assert str(e) == "Unknown argument or command: unknown-argument"

def test_load_user_config_file_not_found():
    setup_function()
    spafw37.config._config[CONFIG_INFILE_PARAM] = "nonexistent.json"
    with patch('builtins.open', side_effect=FileNotFoundError("No such file")):
        with pytest.raises(FileNotFoundError, match="Config file 'nonexistent.json' not found"):
             config.load_user_config()

def test_load_user_config_permission_denied():
    setup_function()
    spafw37.config._config[CONFIG_INFILE_PARAM] = "restricted.json"
    with patch('builtins.open', side_effect=PermissionError("Permission denied")):
        with pytest.raises(PermissionError, match="Permission denied for config file 'restricted.json'"):
             config.load_user_config()

def test_load_user_config_invalid_json():
    setup_function()
    spafw37.config._config[CONFIG_INFILE_PARAM] = "invalid.json"
    invalid_json = "{ invalid json content"
    with patch('builtins.open', mock_open(read_data=invalid_json)):
        with pytest.raises(ValueError, match="Invalid JSON in config file 'invalid.json'"):
             config.load_user_config()

def test_load_persistent_config_file_not_found():
    setup_function()
    spafw37.config._config[CONFIG_INFILE_PARAM] = "nonexistent.json"
    with patch('builtins.open', side_effect=FileNotFoundError("No such file")):
        with pytest.raises(FileNotFoundError, match="Config file 'config.json' not found"):
             config.load_persistent_config()

def test_load_persistent_config_permission_denied():
    setup_function()
    spafw37.config._config[CONFIG_INFILE_PARAM] = "restricted.json"
    with patch('builtins.open', side_effect=PermissionError("Permission denied")):
        try:
            config.load_persistent_config()
            assert False, "Expected PermissionError"
        except PermissionError as e:
            assert "Permission denied" in str(e)

def test_load_persistent_config_invalid_json():
    setup_function()
    spafw37.config._config[CONFIG_INFILE_PARAM] = "invalid.json"
    invalid_json = "{ malformed json"
    with patch('builtins.open', mock_open(read_data=invalid_json)):
        with pytest.raises(ValueError, match="Invalid JSON in config file 'config.json'"):
             config.load_persistent_config()

def test_save_user_config_permission_denied():
    setup_function()
    spafw37.config._config["test_key"] = "test_value"
    spafw37.config._config[CONFIG_OUTFILE_PARAM] = "restricted.json"
    with patch('builtins.open', side_effect=PermissionError("Permission denied")):
        with pytest.raises(IOError, match="Error writing to config file 'restricted.json': Permission denied"):
             config.save_user_config()

def test_save_user_config_invalid_path():
    setup_function()
    spafw37.config._config["test_key"] = "test_value"
    spafw37.config._config[CONFIG_OUTFILE_PARAM] = "/invalid/path/config.json"
    with patch('builtins.open', side_effect=OSError("Invalid path")):
        with pytest.raises(IOError, match="Error writing to config file '/invalid/path/config.json': Invalid path"):
             config.save_user_config()

def test_save_persistent_config_permission_denied():
    setup_function()
    config._persistent_config["persistent_key"] = "persistent_value"
    with patch('builtins.open', side_effect=PermissionError("Permission denied")):
        with pytest.raises(IOError, match="Error writing to config file 'config.json': Permission denied"):
             config.save_persistent_config()

def test_save_persistent_config_disk_full():
    setup_function()
    config._persistent_config["key"] = "value"
    spafw37.config._config[CONFIG_OUTFILE_PARAM] = "config.json"
    with patch('builtins.open', side_effect=OSError("No space left on device")):
        with pytest.raises(IOError, match="Error writing to config file 'config.json': No space left on device"):
             config.save_persistent_config()

def test_load_config_empty_file():
    setup_function()
    spafw37.config._config[CONFIG_INFILE_PARAM] = "empty.json"
    with patch('builtins.open', mock_open(read_data="")):
        with pytest.raises(ValueError, match="Config file 'empty.json' is empty"):
             config.load_user_config()

def test_save_config_json_serialization_error():
    setup_function()
    # Create an object that can't be JSON serialized
    import datetime
    spafw37.config._config["non_serializable"] = datetime.datetime.now()
    spafw37.config._config[CONFIG_OUTFILE_PARAM] = "test.json"
    
    with patch('builtins.open', mock_open()):
        with pytest.raises(TypeError, match="Object of type datetime is not JSON serializable"):
            config.save_user_config()

def test_load_config_unicode_decode_error():
    setup_function()
    spafw37.config._config[CONFIG_INFILE_PARAM] = "bad_encoding.json"
    # Simulate a file with invalid UTF-8 encoding
    with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte')):
        with pytest.raises(UnicodeDecodeError, match="Unicode decode error in config file 'bad_encoding.json': invalid start byte"):
             config.load_user_config()

def test_save_config_write_error_during_operation():
    setup_function()
    spafw37.config._config["test"] = "value"
    spafw37.config._config[CONFIG_OUTFILE_PARAM] = "test.json"
    
    # Mock open to succeed but file.write to fail
    mock_file = mock_open()
    mock_file.return_value.write.side_effect = OSError("Write failed")
    
    with patch('builtins.open', mock_file):
        with pytest.raises(IOError, match="Error writing to config file 'test.json': Write failed"):
             config.save_user_config()

def test_handle_cli_args_sets_defaults():
    setup_function()
    bind_name = 'default_bind'
    param_name = 'default_param'
    param.add_param({
        param.PARAM_CONFIG_NAME: bind_name,
        param_consts.PARAM_NAME: param_name,
        param.PARAM_DEFAULT: 'default_value'
    })
    # calling handle_cli_args with no args should set defaults
    cli.handle_cli_args([])
    assert spafw37.config._config[bind_name] == 'default_value'


def test_handle_cli_args_shows_help_when_no_app_commands(capsys):
    """Test that handle_cli_args displays help when no app commands are queued."""
    setup_function()
    
    # Call with no arguments - should display help since no app commands
    cli.handle_cli_args([])
    
    captured = capsys.readouterr()
    assert "Usage:" in captured.out


def test_handle_cli_args_shows_help_with_only_framework_commands(capsys):
    """Test that help is shown when only framework commands are queued."""
    setup_function()
    from spafw37.constants.command import COMMAND_FRAMEWORK
    
    def framework_action():
        pass
    
    command.add_command({
        COMMAND_NAME: "framework-cmd",
        COMMAND_DESCRIPTION: "Framework command",
        COMMAND_ACTION: framework_action,
        COMMAND_REQUIRED_PARAMS: [],
        COMMAND_FRAMEWORK: True
    })
    
    # Queue only framework command - should display help
    cli.handle_cli_args(["framework-cmd"])
    
    captured = capsys.readouterr()
    assert "Usage:" in captured.out


def test_handle_cli_args_runs_app_commands():
    """Test that app commands are executed when queued."""
    setup_function()
    
    executed = []
    
    def app_action():
        executed.append("app-cmd")
    
    command.add_command({
        COMMAND_NAME: "app-cmd",
        COMMAND_DESCRIPTION: "App command",
        COMMAND_ACTION: app_action,
        COMMAND_REQUIRED_PARAMS: []
    })
    
    # Queue app command - should execute
    cli.handle_cli_args(["app-cmd"])
    
    assert "app-cmd" in executed


def test_add_pre_parse_actions_plural():
    """Test adding multiple pre-parse actions at once.
    
    The add_pre_parse_actions function should add all actions from a list.
    This validates line 24-26 coverage.
    """
    setup_function()
    
    executed = []
    
    def action1():
        executed.append("action1")
    
    def action2():
        executed.append("action2")
    
    cli.add_pre_parse_actions([action1, action2])
    
    # Trigger pre-parse actions
    cli._do_pre_parse_actions()
    
    assert executed == ["action1", "action2"]


def test_add_post_parse_actions_plural():
    """Test adding multiple post-parse actions at once.
    
    The add_post_parse_actions function should add all actions from a list.
    This validates line 30-32 coverage.
    """
    setup_function()
    
    executed = []
    
    def action1():
        executed.append("action1")
    
    def action2():
        executed.append("action2")
    
    cli.add_post_parse_actions([action1, action2])
    
    # Trigger post-parse actions
    cli._do_post_parse_actions()
    
    assert executed == ["action1", "action2"]


def test_do_pre_parse_actions_exception_handling():
    """Test that pre-parse action exceptions are caught and ignored.
    
    Pre-parse actions that raise exceptions should be silently caught,
    allowing subsequent actions to run. This validates line 44-49.
    """
    setup_function()
    
    executed = []
    
    def failing_action():
        raise ValueError("Pre-parse error")
    
    def success_action():
        executed.append("success")
    
    cli.add_pre_parse_actions([failing_action, success_action])
    
    # Should not raise, and success_action should still run
    cli._do_pre_parse_actions()
    
    assert "success" in executed


def test_capture_param_values_file_reference():
    """Test capturing parameter value from file reference (@path).
    
    When a parameter value starts with '@', it should be treated as a
    file reference and the file contents loaded. This validates line 75-78.
    """
    setup_function()
    
    # Create a test file
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("file content")
        temp_file = f.name
    
    try:
        # Create a text param
        text_param = {
            PARAM_NAME: 'text-param',
            PARAM_ALIASES: ['--text'],
            PARAM_TYPE: 'text',
        }
        param.add_param(text_param)
        
        # Test capture with file reference
        args = [f'@{temp_file}']
        offset, value = cli.capture_param_values(args, text_param)
        
        assert offset == 1
        assert value == "file content"
    finally:
        os.unlink(temp_file)


def test_capture_param_values_dict_param_json():
    """Test capturing dict parameter with JSON value.
    
    Dict params should trigger JSON accumulation logic.
    This validates line 99 and the _accumulate_json_for_dict_param function.
    """
    setup_function()
    
    dict_param = {
        PARAM_NAME: 'dict-param',
        PARAM_ALIASES: ['--dict'],
        PARAM_TYPE: 'dict',
    }
    param.add_param(dict_param)
    
    # Test with JSON that spans multiple tokens
    args = ['{', '"key":', '"value"', '}']
    offset, value = cli.capture_param_values(args, dict_param)
    
    # Should accumulate all tokens into valid JSON
    assert '"key"' in value
    assert '"value"' in value


def test_capture_param_values_list_param_whitespace_split():
    """Test that list params split whitespace-containing strings.
    
    When a list param value contains whitespace (from file or elsewhere),
    it should be split into multiple list items. This validates line 108-116.
    """
    setup_function()
    
    list_param = {
        PARAM_NAME: 'list-param',
        PARAM_ALIASES: ['--list'],
        PARAM_TYPE: 'list',
    }
    param.add_param(list_param)
    
    # Simulate a value with spaces (as if from a file)
    args = ["value1 value2 value3"]
    offset, values = cli.capture_param_values(args, list_param)
    
    assert offset == 1
    assert values == ["value1", "value2", "value3"]


def test_capture_param_values_list_param_empty_string():
    """Test that list params skip empty strings.
    
    Empty strings (e.g., from empty files) should be skipped for list params.
    This validates line 114-116.
    """
    setup_function()
    
    list_param = {
        PARAM_NAME: 'list-param',
        PARAM_ALIASES: ['--list'],
        PARAM_TYPE: 'list',
    }
    param.add_param(list_param)
    
    # Test with empty string followed by real value
    args = ["", "value1"]
    offset, values = cli.capture_param_values(args, list_param)
    
    # Empty string should be skipped
    assert values == ["value1"]


def test_handle_long_alias_param_file_reference():
    """Test long alias with embedded file reference (--param=@file).
    
    When the embedded value is a file reference, it should be loaded.
    This validates line 231 coverage.
    """
    setup_function()
    
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("embedded file content")
        temp_file = f.name
    
    try:
        text_param = {
            PARAM_NAME: 'text-param',
            PARAM_ALIASES: ['--text'],
            PARAM_TYPE: 'text',
        }
        param.add_param(text_param)
        
        # Store current args for XOR checking
        cli._current_args = [f'--text=@{temp_file}']
        
        value, param_def = cli._handle_long_alias_param(f'--text=@{temp_file}')
        
        assert value == "embedded file content"
        assert param_def == text_param
    finally:
        os.unlink(temp_file)


def test_accumulate_json_for_dict_param_file_reference():
    """Test JSON accumulation with file reference.
    
    When dict param value starts with '@', it should return the file ref as-is.
    This validates line 475-476 coverage.
    """
    setup_function()
    
    args = ['@data.json']
    offset, value = cli._accumulate_json_for_dict_param(
        args, 0, 1, 1, param, command, cli._is_quoted_token
    )
    
    assert offset == 1
    assert value == '@data.json'


def test_accumulate_json_invalid_json_raises():
    """Test that invalid JSON raises ValueError.
    
    When JSON tokens can't be parsed into valid JSON, a ValueError should
    be raised with a helpful message. This validates line 503-505.
    """
    setup_function()
    
    # Invalid JSON that can't be completed
    args = ['{', '"key"', 'invalid']
    
    with pytest.raises(ValueError, match="Could not parse JSON"):
        cli._accumulate_json_for_dict_param(
            args, 0, 1, 3, param, command, cli._is_quoted_token
        )


def test_accumulate_json_stops_at_command():
    """Test that JSON accumulation stops when encountering a command.
    
    When accumulating JSON tokens, stop if a command is encountered.
    This validates line 486-487 coverage.
    """
    setup_function()
    
    # Register a command
    def cmd_action():
        pass
    
    command.add_command({
        COMMAND_NAME: "test-cmd",
        COMMAND_DESCRIPTION: "Test command",
        COMMAND_ACTION: cmd_action,
        COMMAND_REQUIRED_PARAMS: []
    })
    
    # JSON followed by command
    args = ['{', '"key":', '"value"', '}', 'test-cmd']
    
    # Should stop before the command
    offset, value = cli._accumulate_json_for_dict_param(
        args, 0, 1, 5, param, command, cli._is_quoted_token
    )
    
    # Should have accumulated the complete JSON before the command
    import json
    parsed = json.loads(value)
    assert parsed == {"key": "value"}


def test_accumulate_json_stops_at_alias():
    """Test that JSON accumulation stops when encountering an unquoted alias.
    
    When accumulating JSON tokens, stop if an alias for another param is found.
    This validates line 483-485 coverage.
    """
    setup_function()
    
    # Register a param
    param.add_param({
        PARAM_NAME: 'other-param',
        PARAM_ALIASES: ['--other'],
        PARAM_TYPE: 'text',
    })
    
    # JSON followed by another param alias
    args = ['{', '"key":', '"value"', '}', '--other', 'value']
    
    # Should stop before the alias
    offset, value = cli._accumulate_json_for_dict_param(
        args, 0, 1, 6, param, command, cli._is_quoted_token
    )
    
    # Should have accumulated the complete JSON before the alias
    import json
    parsed = json.loads(value)
    assert parsed == {"key": "value"}


def test_accumulate_json_single_token_not_json():
    """Test dict param with single non-JSON token.
    
    When a dict param value is a single token that's not JSON and not a file ref,
    return it as-is and let the param parser handle it. This validates line 507.
    """
    setup_function()
    
    args = ['not-json-value']
    offset, value = cli._accumulate_json_for_dict_param(
        args, 0, 1, 1, param, command, cli._is_quoted_token
    )
    
    assert offset == 1
    assert value == 'not-json-value'


def test_pre_parse_params_with_long_alias_embedded_value():
    """Test pre-parse handling of long alias with embedded value.
    
    Pre-parse should handle --param=value format correctly.
    This validates lines 402-405 coverage.
    """
    setup_function()
    
    # Add a pre-parse param
    verbose_param = {
        PARAM_NAME: 'verbose',
        PARAM_ALIASES: ['--verbose', '-v'],
        PARAM_TYPE: 'toggle',
        'preparse': True,
    }
    param.add_param(verbose_param)
    param.add_pre_parse_args(['verbose'])
    
    # Pre-parse with long alias format
    cli._pre_parse_params(['--verbose=true'])
    
    # Verify the value was set in config
    assert spafw37.config.get_config_value('verbose') is True


def test_pre_parse_params_skips_commands():
    """Test that pre-parse skips over command arguments.
    
    Commands in the args list should be skipped during pre-parse.
    This validates lines 394-396 coverage.
    """
    setup_function()
    
    def cmd_action():
        pass
    
    command.add_command({
        COMMAND_NAME: "test-cmd",
        COMMAND_DESCRIPTION: "Test command",
        COMMAND_ACTION: cmd_action,
        COMMAND_REQUIRED_PARAMS: []
    })
    
    verbose_param = {
        PARAM_NAME: 'verbose',
        PARAM_ALIASES: ['--verbose'],
        PARAM_TYPE: 'toggle',
        PARAM_HAS_VALUE: False,
        'preparse': True,
    }
    param.add_param(verbose_param)
    param.add_pre_parse_args(['verbose'])
    
    # Pre-parse with command in the middle
    cli._pre_parse_params(['test-cmd', '--verbose'])
    
    # Verbose should still be set despite command being present
    assert spafw37.config.get_config_value('verbose') is True


def test_pre_parse_params_short_alias():
    """Test pre-parse handling of short alias arguments.
    
    Pre-parse should handle short aliases like -v correctly.
    This validates lines 406-409 coverage.
    """
    setup_function()
    
    verbose_param = {
        PARAM_NAME: 'verbose',
        PARAM_ALIASES: ['-v'],
        PARAM_TYPE: 'toggle',
        PARAM_HAS_VALUE: False,
        'preparse': True,
    }
    param.add_param(verbose_param)
    param.add_pre_parse_args(['verbose'])
    
    # Pre-parse with short alias
    cli._pre_parse_params(['-v'])
    
    assert spafw37.config.get_config_value('verbose') is True


def test_handle_cli_args_no_app_commands_shows_help(capsys):
    """Test that help is displayed when no app commands are queued.
    
    If only framework commands run (or no commands), help should be shown.
    This validates lines 448-450 coverage.
    """
    setup_function()
    
    # Add a param so we have something to show help for
    param.add_param({
        PARAM_NAME: 'test-param',
        PARAM_ALIASES: ['--test'],
        PARAM_TYPE: 'text',
        PARAM_DESCRIPTION: 'Test parameter',
    })
    
    # Run with no commands
    cli.handle_cli_args([])
    
    captured = capsys.readouterr()
    # Should display help
    assert "Usage:" in captured.out or "Parameters:" in captured.out


def test_capture_param_values_quoted_alias_treated_as_value():
    """Test that quoted alias-like tokens are treated as values.
    
    When capturing param values, if an argument looks like an alias but is quoted,
    it should be treated as a value. This validates line 89.
    """
    setup_function()
    
    list_param = {
        PARAM_NAME: 'items',
        PARAM_ALIASES: ['--items'],
        PARAM_TYPE: 'list',
    }
    param.add_param(list_param)
    
    # Include a quoted "alias-like" value
    args = ['"--value"', 'actual-value']
    offset, value = cli.capture_param_values(args, list_param)
    
    assert offset == 2
    assert '"--value"' in value
    assert 'actual-value' in value


def test_test_switch_xor_no_conflict_when_param_not_in_args():
    """Test that XOR conflict check is skipped when param not in args.
    
    If the current param is not in the args list, no XOR check should occur.
    This validates line 142.
    """
    setup_function()
    
    verbose = {
        PARAM_NAME: 'verbose',
        PARAM_ALIASES: ['--verbose'],
        PARAM_TYPE: 'toggle',
        PARAM_SWITCH_LIST: ['silent'],
    }
    silent = {
        PARAM_NAME: 'silent',
        PARAM_ALIASES: ['--silent'],
        PARAM_TYPE: 'toggle',
    }
    param.add_param(verbose)
    param.add_param(silent)
    
    # Args don't contain verbose, so no conflict check
    args = ['--silent']
    cli.test_switch_xor(verbose, args)  # Should not raise


def test_parse_long_alias_with_embedded_value_unknown_alias():
    """Test parsing long alias with value when alias is unknown.
    
    When the alias in --alias=value is not registered, should return None.
    This validates lines 290, 294.
    """
    setup_function()
    
    preparse_map = {}
    result = cli._parse_long_alias_with_embedded_value('--unknown=value', preparse_map)
    
    assert result == (None, None)


def test_parse_long_alias_with_embedded_value_not_preparse():
    """Test parsing long alias with value when param is not a pre-parse param.
    
    When the alias is valid but not in the preparse_map, should return None.
    This validates lines 290, 294.
    """
    setup_function()
    
    regular_param = {
        PARAM_NAME: 'regular',
        PARAM_ALIASES: ['--regular'],
        PARAM_TYPE: 'text',
    }
    param.add_param(regular_param)
    
    preparse_map = {}  # Empty, so regular is not pre-parse
    result = cli._parse_long_alias_with_embedded_value('--regular=value', preparse_map)
    
    assert result == (None, None)


def test_extract_param_value_from_next_argument_no_next_arg():
    """Test extracting param value when there's no next argument.
    
    When at the end of args list, should return default value with 0 increment.
    This validates lines 312-321.
    """
    setup_function()
    
    param_def = {
        PARAM_NAME: 'test',
        PARAM_DEFAULT: 'default-value',
    }
    
    args = []
    value, increment = cli._extract_param_value_from_next_argument(param_def, args, 0, 0)
    
    assert value == 'default-value'
    assert increment == 0


def test_extract_param_value_next_is_alias():
    """Test extracting param value when next arg is an alias.
    
    When the next argument is an alias, should return default value.
    This validates lines 312-321.
    """
    setup_function()
    
    param_def = {
        PARAM_NAME: 'count',
        PARAM_DEFAULT: '10',
    }
    
    other_param = {
        PARAM_NAME: 'other',
        PARAM_ALIASES: ['--other'],
        PARAM_TYPE: 'text',
    }
    param.add_param(other_param)
    
    # Next arg is an alias, so should return default
    args = ['--count', '--other', 'value']
    value, increment = cli._extract_param_value_from_next_argument(param_def, args, 0, 3)
    
    # Should get default since next arg is an alias
    assert value == '10'
    assert increment == 0


def test_extract_param_value_next_is_command():
    """Test extracting param value when next arg is a command.
    
    When the next argument is a command, should return default value.
    This validates lines 312-321.
    """
    setup_function()
    
    param_def = {
        PARAM_NAME: 'count',
        PARAM_DEFAULT: '10',
    }
    
    def cmd_action():
        pass
    
    command.add_command({
        COMMAND_NAME: "run",
        COMMAND_DESCRIPTION: "Run command",
        COMMAND_ACTION: cmd_action,
        COMMAND_REQUIRED_PARAMS: []
    })
    
    args = ['run']
    value, increment = cli._extract_param_value_from_next_argument(param_def, args, 0, 1)
    
    assert value == '10'
    assert increment == 0


def test_parse_short_alias_argument_unknown_alias():
    """Test parsing short alias when alias is unknown.
    
    Should return (None, None, 0) when alias is not registered.
    This validates lines 339, 343.
    """
    setup_function()
    
    preparse_map = {}
    result = cli._parse_short_alias_argument('--unknown', [], 0, 0, preparse_map)
    
    assert result == (None, None, 0)


def test_parse_short_alias_argument_not_preparse():
    """Test parsing short alias when param is not a pre-parse param.
    
    Should return (None, None, 0) when param is not in preparse_map.
    This validates lines 339, 343.
    """
    setup_function()
    
    regular_param = {
        PARAM_NAME: 'regular',
        PARAM_ALIASES: ['--regular'],
        PARAM_TYPE: 'text',
    }
    param.add_param(regular_param)
    
    preparse_map = {}
    result = cli._parse_short_alias_argument('--regular', ['value'], 0, 1, preparse_map)
    
    assert result == (None, None, 0)


def test_parse_short_alias_argument_with_value():
    """Test parsing short alias for param that has a value.
    
    Should extract value from next argument.
    This validates lines 348-351.
    """
    setup_function()
    
    param_def = {
        PARAM_NAME: 'count',
        PARAM_ALIASES: ['--count'],
        PARAM_TYPE: 'number',
        PARAM_HAS_VALUE: True,
    }
    param.add_param(param_def)
    
    preparse_map = {'count': param_def}
    args = ['--count', '42']
    result_def, result_value, increment = cli._parse_short_alias_argument('--count', args, 0, 2, preparse_map)
    
    assert result_def == param_def
    assert result_value == 42
    assert increment == 1


@pytest.mark.skip(reason="Line 424 requires 'help' command, not --help flag")
def test_handle_cli_args_with_help_command_returns_early(capsys):
    """Test that handle_cli_args returns early when help command is handled.
    
    When help is displayed, the function should return without further processing.
    This validates line 424.
    """
    setup_function()
    
    # Add a simple param to trigger help display
    param.add_param({
        PARAM_NAME: 'test',
        PARAM_ALIASES: ['--test'],
        PARAM_TYPE: 'text',
    })
    
    # Call with --help should return early (line 424)
    cli.handle_cli_args(['--help'])
    
    captured = capsys.readouterr()
    # Help should have been displayed
    assert "Usage:" in captured.out or "Parameters:" in captured.out


def test_is_quoted_token_double_quotes():
    """Test _is_quoted_token with double-quoted strings.
    
    Should return True for strings enclosed in double quotes.
    This validates line 486.
    """
    setup_function()
    
    assert cli._is_quoted_token('"hello"') is True
    assert cli._is_quoted_token('"--alias"') is True


def test_is_quoted_token_single_quotes():
    """Test _is_quoted_token with single-quoted strings.
    
    Should return True for strings enclosed in single quotes.
    This validates line 488.
    """
    setup_function()
    
    assert cli._is_quoted_token("'hello'") is True
    assert cli._is_quoted_token("'--alias'") is True


def test_is_quoted_token_not_quoted():
    """Test _is_quoted_token with non-quoted strings.
    
    Should return False for strings not enclosed in quotes.
    This validates the return path of _is_quoted_token.
    """
    setup_function()
    
    assert cli._is_quoted_token('hello') is False
    assert cli._is_quoted_token('--alias') is False


