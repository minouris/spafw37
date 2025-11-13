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
)
import spafw37.constants.param as param_consts
import spafw37.configure
import re
from unittest.mock import patch, mock_open
import json

from tests.test_command import _reset_command_module

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

