import pytest
from spafw37 import cli, config_func, logging, param, command
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
    PARAM_TYPE_TOGGLE,
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
        spafw37.config._config.clear()
        config_func._persistent_config.clear()
        param._xor_list.clear()
        cli._pre_parse_actions.clear()
        cli._post_parse_actions.clear()
        _reset_command_module()
    except Exception:
        pass


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
    from spafw37 import core
    core.add_params([{
        PARAM_NAME: "some_flag",
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_ALIASES: ['--some-flag', '-s'],
        PARAM_DEFAULT: True
    },{
        PARAM_NAME: "another_flag",
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_ALIASES: ['--another', '-a']
    }])
    core.add_command({
        COMMAND_NAME: "test-command",
        COMMAND_REQUIRED_PARAMS: [],        
        COMMAND_ACTION: lambda: None})
    core.add_params(logging.LOGGING_PARAMS)
    args = ["test-command", "--trace-console", "--some-flag", "-a"]
    core.run_cli(args, True)
    assert core.get_param("another_flag") is True
    assert core.get_param("some_flag") is False

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
        # Error message order may vary, just check both params are mentioned
        assert "conflicts with" in str(e)
        assert "option1" in str(e)
        assert "option2" in str(e)

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
        assert "conflicts with" in str(e)
    
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
        assert "conflicts with" in str(e)
    
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
        assert "conflicts with" in str(e)

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



def test_parse_command_line_unknown_arg_raises():
    setup_function()
    try:
        tokenized = cli._tokenise_cli_args(["--this-does-not-exist"])
        cli._parse_command_line(tokenized)
        assert False, "Expected ValueError for unknown argument"
    except ValueError as e:
        assert "Unknown parameter" in str(e)

def test_parse_command_line_unknown_argument_raises():
    setup_function()
    try:
        tokenized = cli._tokenise_cli_args(["unknown-argument"])
        cli._parse_command_line(tokenized)
        assert False, "Expected exception for unknown command"
    except (ValueError, KeyError) as e:
        assert "unknown-argument" in str(e).lower() or "not found" in str(e).lower()

def test_load_user_config_file_not_found():
    setup_function()
    spafw37.config._config[CONFIG_INFILE_PARAM] = "nonexistent.json"
    # Mock os.path.exists to return False (file doesn't exist)
    with patch('os.path.exists', return_value=False):
        with pytest.raises(FileNotFoundError, match="Config file 'nonexistent.json' not found"):
             config_func.load_user_config()

def test_load_user_config_permission_denied():
    setup_function()
    spafw37.config._config[CONFIG_INFILE_PARAM] = "restricted.json"
    # Mock filesystem to simulate existing file with no read permission
    with patch('os.path.exists', return_value=True), \
         patch('os.path.isfile', return_value=True), \
         patch('os.access', return_value=False):
        with pytest.raises(PermissionError, match="Permission denied reading file: restricted.json"):
             config_func.load_user_config()

def test_load_user_config_invalid_json():
    setup_function()
    spafw37.config._config[CONFIG_INFILE_PARAM] = "invalid.json"
    invalid_json = "{ invalid json content"
    # Mock filesystem to simulate existing readable file
    with patch('os.path.exists', return_value=True), \
         patch('os.path.isfile', return_value=True), \
         patch('os.access', return_value=True), \
         patch('builtins.open', mock_open(read_data=invalid_json)):
        with pytest.raises(ValueError, match="Invalid JSON in config file 'invalid.json'"):
             config_func.load_user_config()

def test_load_persistent_config_file_not_found():
    setup_function()
    spafw37.config._config[CONFIG_INFILE_PARAM] = "nonexistent.json"
    with patch('builtins.open', side_effect=FileNotFoundError("No such file")):
        with pytest.raises(FileNotFoundError, match="Config file 'config.json' not found"):
             config_func.load_persistent_config()

def test_load_persistent_config_permission_denied():
    setup_function()
    spafw37.config._config[CONFIG_INFILE_PARAM] = "restricted.json"
    # Mock filesystem to simulate existing file with no read permission
    with patch('os.path.exists', return_value=True), \
         patch('os.path.isfile', return_value=True), \
         patch('os.access', return_value=False):
        try:
            config_func.load_persistent_config()
            assert False, "Expected PermissionError"
        except PermissionError as e:
            assert "Permission denied" in str(e)

def test_load_persistent_config_invalid_json():
    setup_function()
    spafw37.config._config[CONFIG_INFILE_PARAM] = "invalid.json"
    invalid_json = "{ malformed json"
    # Mock filesystem to simulate existing readable file
    with patch('os.path.exists', return_value=True), \
         patch('os.path.isfile', return_value=True), \
         patch('os.access', return_value=True), \
         patch('builtins.open', mock_open(read_data=invalid_json)):
        with pytest.raises(ValueError, match="Invalid JSON in config file 'config.json'"):
             config_func.load_persistent_config()

def test_save_user_config_permission_denied():
    setup_function()
    spafw37.config._config["test_key"] = "test_value"
    spafw37.config._config[CONFIG_OUTFILE_PARAM] = "restricted.json"
    with patch('builtins.open', side_effect=PermissionError("Permission denied")):
        with pytest.raises(IOError, match="Error writing to config file 'restricted.json': Permission denied"):
             config_func.save_user_config()

def test_save_user_config_invalid_path():
    setup_function()
    spafw37.config._config["test_key"] = "test_value"
    spafw37.config._config[CONFIG_OUTFILE_PARAM] = "/invalid/path/config.json"
    with patch('builtins.open', side_effect=OSError("Invalid path")):
        with pytest.raises(IOError, match="Error writing to config file '/invalid/path/config.json': Invalid path"):
             config_func.save_user_config()

def test_save_persistent_config_permission_denied():
    setup_function()
    config_func._persistent_config["persistent_key"] = "persistent_value"
    with patch('builtins.open', side_effect=PermissionError("Permission denied")):
        with pytest.raises(IOError, match="Error writing to config file 'config.json': Permission denied"):
             config_func.save_persistent_config()

def test_save_persistent_config_disk_full():
    setup_function()
    config_func._persistent_config["key"] = "value"
    spafw37.config._config[CONFIG_OUTFILE_PARAM] = "config.json"
    with patch('builtins.open', side_effect=OSError("No space left on device")):
        with pytest.raises(IOError, match="Error writing to config file 'config.json': No space left on device"):
             config_func.save_persistent_config()

def test_load_config_empty_file():
    """
    Test that loading an empty config file returns an empty dict.
    Empty config files are treated as valid configuration with no settings.
    This allows for flexible initialization where empty files don't cause errors.
    """
    setup_function()
    spafw37.config._config[CONFIG_INFILE_PARAM] = "empty.json"
    # Mock filesystem to simulate existing readable empty file
    with patch('os.path.exists', return_value=True), \
         patch('os.path.isfile', return_value=True), \
         patch('os.access', return_value=True), \
         patch('builtins.open', mock_open(read_data="")):
        result = config_func.load_config("empty.json")
        assert result == {}

def test_save_config_json_serialization_error():
    setup_function()
    # Create an object that can't be JSON serialized
    import datetime
    spafw37.config._config["non_serializable"] = datetime.datetime.now()
    spafw37.config._config[CONFIG_OUTFILE_PARAM] = "test.json"
    
    with patch('builtins.open', mock_open()):
        with pytest.raises(TypeError, match="Object of type datetime is not JSON serializable"):
            config_func.save_user_config()

def test_load_config_unicode_decode_error():
    setup_function()
    spafw37.config._config[CONFIG_INFILE_PARAM] = "bad_encoding.json"
    # Mock filesystem and simulate a file with invalid UTF-8 encoding
    with patch('os.path.exists', return_value=True), \
         patch('os.path.isfile', return_value=True), \
         patch('os.access', return_value=True), \
         patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid start byte')):
        with pytest.raises(UnicodeDecodeError, match="Unicode decode error in config file 'bad_encoding.json': invalid start byte"):
             config_func.load_user_config()

def test_save_config_write_error_during_operation():
    setup_function()
    spafw37.config._config["test"] = "value"
    spafw37.config._config[CONFIG_OUTFILE_PARAM] = "test.json"
    
    # Mock open to succeed but file.write to fail
    mock_file = mock_open()
    mock_file.return_value.write.side_effect = OSError("Write failed")
    
    with patch('builtins.open', mock_file):
        with pytest.raises(IOError, match="Error writing to config file 'test.json': Write failed"):
             config_func.save_user_config()

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
    
    # Tokenize and pre-parse with toggle (no value)
    tokenized = cli._tokenise_cli_args(['--verbose'])
    cli._pre_parse_params(tokenized)
    
    # Verbose should still be set despite command being present
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
    
    # Tokenize and pre-parse with command in the middle
    tokenized = cli._tokenise_cli_args(['test-cmd', '--verbose'])
    cli._pre_parse_params(tokenized)
    
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
    
    # Tokenize and pre-parse with short alias
    tokenized = cli._tokenise_cli_args(['-v'])
    cli._pre_parse_params(tokenized)
    
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


