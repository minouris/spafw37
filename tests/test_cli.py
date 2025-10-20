from spafw37 import cli, config, param
import spafw37.param
from spafw37.param import PARAM_NAME, PARAM_ALIASES, PARAM_TYPE, PARAM_DEFAULT, PARAM_BIND_TO, PARAM_SWITCH_LIST
import re

def setup_function():
    # reset module state between tests
    param._param_aliases.clear()
    param._params.clear()
    try:
        config._non_persisted_config_names.clear()
        config._config.clear()
        config._persistent_config.clear()
        param._xor_list.clear()
    except Exception:
        pass

def test_register_param_alias_valid():
    setup_function()
    alias1 = '--test-alias'
    alias2 = '-t'
    param_name = 'test_param'
    param.add_param({
        param.PARAM_NAME: param_name,
        param.PARAM_ALIASES: [alias1, alias2]
    })
    assert param._param_aliases[alias1] == param_name
    assert param._param_aliases[alias2] == param_name

def test_register_param_alias_invalid_raises():
    setup_function()
    invalid_alias = 'invalid-alias'  # Missing leading dashes
    _param = {
        param.PARAM_NAME: 'test_param',
        param.PARAM_ALIASES: [invalid_alias]
    }
    try:
        param.add_param(_param)
        assert False, "Expected ValueError for invalid alias format"
    except ValueError as e:
        assert str(e) == f"Invalid alias format: {invalid_alias}"

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
        param.PARAM_NAME: param_name,
        param.PARAM_ALIASES: [alias]
    }
    param.add_param(_param)
    assert param.is_param_alias(_param, alias) is True

def test_is_param_alias_false():
    setup_function()
    alias = '--my-alias'
    param_name = 'my_param'
    _param = {
        param.PARAM_NAME: param_name,
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
        param.PARAM_NAME: param_name,
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
        param.PARAM_NAME: param_name,
        param.PARAM_ALIASES: [alias]
    })
    _param = param.get_param_by_alias(alias)
    assert _param.get(param.PARAM_NAME) == param_name

def test_set_default_param_values():
    setup_function()
    bind_name = 'test_bind'
    param_name = 'test_param'
    param.add_param({
        param.PARAM_BIND_TO: bind_name,
        param.PARAM_NAME: param_name,
        param.PARAM_DEFAULT: 'default_value'
    })
    cli._set_defaults()
    assert config._config[bind_name] == 'default_value'

def test_set_default_param_toggle_with_default_true():
    setup_function()
    bind_name = 'toggle_param'
    param_name = 'toggle_param_name'
    param.add_param({
        param.PARAM_BIND_TO: bind_name,
        param.PARAM_NAME: param_name,
        param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE,
        param.PARAM_DEFAULT: True
    })
    cli._set_defaults()
    assert config._config[bind_name] is True

def test_set_default_param_toggle_with_no_default():
    setup_function()
    bind_name = 'toggle_no_default'
    param_name = 'toggle_no_default_name'
    param.add_param({
        param.PARAM_BIND_TO: bind_name,
        param.PARAM_NAME: param_name,
        param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE
    })
    cli._set_defaults()
    assert config._config[bind_name] is False

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
        param.PARAM_NAME: 'some_param'
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
        param.PARAM_NAME: option1,
        param.PARAM_SWITCH_LIST: [ option2, option3 ]
    },{
        param.PARAM_NAME: option2,
        param.PARAM_SWITCH_LIST: [ option1, option3 ]
    },{
        param.PARAM_NAME: option3,
        param.PARAM_SWITCH_LIST: [ option1, option2 ]
    }
    ])
    assert param._has_xor_with(option1, option2)
    assert param._has_xor_with(option1, option3)
    assert param._has_xor_with(option2, option1)
    assert param._has_xor_with(option2, option3)
    assert param._has_xor_with(option3, option1)
    assert param._has_xor_with(option3, option2)

def test_set_param_xor_list_partial_set():
    """
    Verifies that xor lists are set when xors are only specified
     for some params.
    """
    option1 = "option1"
    option2 = "option2"
    option3 = "option3"
    param.add_params([{
        param.PARAM_NAME: option1,
        param.PARAM_SWITCH_LIST: [ option2 ]
    },{
        param.PARAM_NAME: option2,
        param.PARAM_SWITCH_LIST: [ option3 ]
    },{
        param.PARAM_NAME: option3,
        param.PARAM_SWITCH_LIST: [ option1 ]
    }
    ])
    assert param._has_xor_with(option1, option2)
    assert param._has_xor_with(option1, option3)
    assert param._has_xor_with(option2, option1)
    assert param._has_xor_with(option2, option3)
    assert param._has_xor_with(option3, option1)
    assert param._has_xor_with(option3, option2)


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
        param.PARAM_NAME: "some_flag",
        param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE,
        param.PARAM_ALIASES: ['--some-flag', '-s']
    },{
        param.PARAM_NAME: "verbose",
        param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE,
        param.PARAM_ALIASES: ['--verbose', '-v']
    }])
    args = ["--some-flag", "-v"]
    cli.handle_cli_args(args)
    assert config._config["some_flag"] is True
    assert config._config["verbose"] is True

def test_parse_command_line_param_with_text_value():
    setup_function()
    param.add_params([{
        param.PARAM_NAME: "output_file",
        param.PARAM_TYPE: param.PARAM_TYPE_TEXT,
        param.PARAM_ALIASES: ['--output-file', '-o']
    }])
    args = ["--output-file", "result.txt"]
    cli.handle_cli_args(args)
    assert config._config["output_file"] == "result.txt"

def test_parse_command_line_param_with_number_value():
    setup_function()
    param.add_params([{
        param.PARAM_NAME: "max_retries",
        param.PARAM_TYPE: param.PARAM_TYPE_NUMBER,
        param.PARAM_ALIASES: ['--max-retries', '-m']
    }])
    args = ["--max-retries", "5"]
    cli.handle_cli_args(args)
    assert config._config["max_retries"] == 5

def test_parse_command_line_param_with_list_value():
    setup_function()
    param.add_params([{
        param.PARAM_NAME: "input_files",
        param.PARAM_TYPE: param.PARAM_TYPE_LIST,
        param.PARAM_ALIASES: ['--input-files', '-i']
    }])
    args = ["--input-files", "file1.txt", "file2.txt"]
    cli.handle_cli_args(args)
    assert config._config["input_files"] == ["file1.txt", "file2.txt"]

def test_parse_command_line_param_with_list_value_across_multi_params():
    setup_function()
    param.add_params([{
        param.PARAM_NAME: "input_files",
        param.PARAM_TYPE: param.PARAM_TYPE_LIST,
        param.PARAM_ALIASES: ['--input-files', '-i']
    }])
    args = ["--input-files", "file1.txt", "--input-files", "file2.txt"]
    cli.handle_cli_args(args)
    assert config._config["input_files"] == ["file1.txt", "file2.txt"]

def test_parse_command_line_param_with_toggle_value():
    setup_function()
    param.add_params([{
        param.PARAM_NAME: "some_flag",
        param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE,
        param.PARAM_ALIASES: ['--some-flag', '-s'],
        param.PARAM_DEFAULT: True
    },{
        param.PARAM_NAME: "verbose",
        param.PARAM_TYPE: param.PARAM_TYPE_TOGGLE,
        param.PARAM_ALIASES: ['--verbose', '-v']
    }])
    args = ["--some-flag", "-v"]
    cli.handle_cli_args(args)
    assert config._config["some_flag"] is False
    assert config._config["verbose"] is True

def test_parse_command_line_param_with_equals_value():
    setup_function()
    param.add_params([{
        param.PARAM_NAME: "config_path",
        param.PARAM_TYPE: param.PARAM_TYPE_TEXT,
        param.PARAM_ALIASES: ['--config-path', '-c']
    }])
    args = ["--config-path=/etc/config.json"]
    cli.handle_cli_args(args)
    assert config._config["config_path"] == "/etc/config.json"

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
        param.PARAM_NAME: "option1",
        param.PARAM_ALIASES: ["--option1"],
        param.PARAM_SWITCH_LIST: [ "option2" ],
        param.PARAM_DEFAULT: False
    },{
        param.PARAM_NAME: "option2",
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