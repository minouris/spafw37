"""Tests for core facade module."""

import pytest
import sys
from spafw37 import core
from spafw37 import param, command, config_func
import spafw37.config
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_LIST,
    PARAM_TYPE_DICT,
    PARAM_TYPE_TOGGLE,
    PARAM_DEFAULT,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_ACTION,
    COMMAND_DESCRIPTION,
    COMMAND_REQUIRED_PARAMS,
)
from spafw37.command import CommandParameterError


def setup_function():
    """Reset module state between tests."""
    from spafw37.constants.phase import PHASE_DEFAULT, PHASE_ORDER
    param._param_aliases.clear()
    param._params.clear()
    param._preparse_args.clear()
    try:
        spafw37.config._config.clear()
        spafw37.config._phases_order = list(PHASE_ORDER)
        spafw37.config._default_phase = PHASE_DEFAULT
        config_func._persistent_config.clear()
        param._xor_list.clear()
        command._commands.clear()
        command._command_queue.clear()
        command._finished_commands.clear()
        command._phases.clear()
        command._phases[PHASE_DEFAULT] = []
        command._phase_order.clear()
        command._phase_order.append(PHASE_DEFAULT)
        command._phases_completed.clear()
        command._current_phase = None
    except Exception:
        pass


def test_set_and_get_app_name():
    """Test setting and getting application name."""
    setup_function()
    
    core.set_app_name("TestApp")
    assert core.get_app_name() == "TestApp"


def test_set_config_file():
    """Test setting configuration file path."""
    setup_function()
    
    core.set_config_file("test_config.json")
    assert config_func._config_file == "test_config.json"


def test_add_param():
    """Test adding a single parameter through core facade."""
    setup_function()
    
    test_param = {
        PARAM_NAME: 'test',
        PARAM_ALIASES: ['--test'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
    }
    
    core.add_param(test_param)
    assert param.get_param_by_alias('--test') is not None


def test_add_params():
    """Test adding multiple parameters through core facade."""
    setup_function()
    
    params = [
        {
            PARAM_NAME: 'test1',
            PARAM_ALIASES: ['--test1'],
            PARAM_TYPE: PARAM_TYPE_TEXT,
        },
        {
            PARAM_NAME: 'test2',
            PARAM_ALIASES: ['--test2'],
            PARAM_TYPE: PARAM_TYPE_NUMBER,
        },
    ]
    
    core.add_params(params)
    assert param.get_param_by_alias('--test1') is not None
    assert param.get_param_by_alias('--test2') is not None


def test_add_command():
    """Test adding a single command through core facade."""
    setup_function()
    
    executed = []
    
    def test_action():
        executed.append('test')
    
    test_cmd = {
        COMMAND_NAME: 'test',
        COMMAND_ACTION: test_action,
        COMMAND_DESCRIPTION: 'Test command',
    }
    
    core.add_command(test_cmd)
    assert command.is_command('test')


def test_add_commands():
    """Test adding multiple commands through core facade."""
    setup_function()
    
    def action1():
        pass
    
    def action2():
        pass
    
    commands = [
        {
            COMMAND_NAME: 'cmd1',
            COMMAND_ACTION: action1,
            COMMAND_DESCRIPTION: 'Command 1',
        },
        {
            COMMAND_NAME: 'cmd2',
            COMMAND_ACTION: action2,
            COMMAND_DESCRIPTION: 'Command 2',
        },
    ]
    
    core.add_commands(commands)
    assert command.is_command('cmd1')
    assert command.is_command('cmd2')


def test_set_phases_order():
    """Test setting phase execution order through core facade."""
    setup_function()
    
    custom_order = ['setup', 'execution', 'teardown']
    core.set_phases_order(custom_order)
    assert spafw37.config.get_phases_order() == custom_order


def test_set_default_phase():
    """Test setting default phase through core facade."""
    setup_function()
    
    core.set_default_phase('custom')
    assert spafw37.config.get_default_phase() == 'custom'


def test_set_config_value():
    """Test setting configuration value through core facade."""
    setup_function()
    
    core.set_config_value('test_key', 'test_value')
    assert spafw37.config._config.get('test_key') == 'test_value'


def test_get_config_value():
    """Test that deprecated get_config_value requires registered params.
    
    This test verifies that the deprecated method correctly raises ValueError
    when attempting to access configuration without a registered parameter.
    Users must register parameters to access values through the param API.
    """
    setup_function()
    
    spafw37.config._config['test_key'] = 'test_value'
    # Should raise ValueError because param is not registered
    with pytest.raises(ValueError):
        core.get_config_value('test_key')


def test_get_config_int():
    """Test that deprecated get_config_int requires registered params.
    
    This test verifies that the deprecated method correctly raises ValueError
    when attempting to access configuration without a registered parameter.
    Users must register parameters to access values through the param API.
    """
    setup_function()
    
    spafw37.config._config['count'] = 42
    # Should raise ValueError because param is not registered
    with pytest.raises(ValueError):
        core.get_config_int('count')


def test_get_config_str():
    """Test that deprecated get_config_str requires registered params.
    
    This test verifies that the deprecated method correctly raises ValueError
    when attempting to access configuration without a registered parameter.
    Users must register parameters to access values through the param API.
    """
    setup_function()
    
    spafw37.config._config['name'] = 'test'
    # Should raise ValueError because param is not registered
    with pytest.raises(ValueError):
        core.get_config_str('name')


def test_get_config_bool():
    """Test that deprecated get_config_bool requires registered params.
    
    This test verifies that the deprecated method correctly raises ValueError
    when attempting to access configuration without a registered parameter.
    Users must register parameters to access values through the param API.
    """
    setup_function()
    
    spafw37.config._config['flag'] = True
    # Should raise ValueError because param is not registered
    with pytest.raises(ValueError):
        core.get_config_bool('flag')


def test_get_config_float():
    """Test that deprecated get_config_float requires registered params.
    
    This test verifies that the deprecated method correctly raises ValueError
    when attempting to access configuration without a registered parameter.
    Users must register parameters to access values through the param API.
    """
    setup_function()
    
    spafw37.config._config['value'] = 3.14
    # Should raise ValueError because param is not registered
    with pytest.raises(ValueError):
        core.get_config_float('value')


def test_get_config_list():
    """Test that deprecated get_config_list requires registered params.
    
    This test verifies that the deprecated method correctly raises ValueError
    when attempting to access configuration without a registered parameter.
    Users must register parameters to access values through the param API.
    """
    setup_function()
    
    spafw37.config._config['items'] = ['a', 'b', 'c']
    # Should raise ValueError because param is not registered
    with pytest.raises(ValueError):
        core.get_config_list('items')


def test_get_config_dict():
    """Test that deprecated get_config_dict requires registered params.
    
    This test verifies that the deprecated method correctly raises ValueError
    when attempting to access configuration without a registered parameter.
    Users must register parameters to access values through the param API.
    """
    setup_function()
    
    test_dict = {'key': 'value', 'nested': {'inner': 'data'}}
    spafw37.config._config['data'] = test_dict
    # Should raise ValueError because param is not registered
    with pytest.raises(ValueError):
        core.get_config_dict('data')


def test_is_verbose():
    """Test checking verbose mode through core facade."""
    setup_function()
    
    from spafw37.logging_config import LOG_VERBOSE_PARAM
    
    spafw37.config._config[LOG_VERBOSE_PARAM] = False
    assert core.is_verbose() is False
    
    spafw37.config._config[LOG_VERBOSE_PARAM] = True
    assert core.is_verbose() is True


def test_is_silent():
    """Test checking silent mode through core facade."""
    setup_function()
    
    from spafw37.logging_config import LOG_SILENT_PARAM
    
    spafw37.config._config[LOG_SILENT_PARAM] = False
    assert core.is_silent() is False
    
    spafw37.config._config[LOG_SILENT_PARAM] = True
    assert core.is_silent() is True


def test_output_normal():
    """Test output function in normal mode."""
    setup_function()
    
    from spafw37.logging_config import LOG_VERBOSE_PARAM, LOG_SILENT_PARAM
    spafw37.config._config[LOG_VERBOSE_PARAM] = False
    spafw37.config._config[LOG_SILENT_PARAM] = False
    
    output_calls = []
    
    def custom_handler(msg):
        output_calls.append(msg)
    
    core.set_output_handler(custom_handler)
    core.output("test message")
    
    assert output_calls == ["test message"]


def test_output_silent_mode():
    """Test output function respects silent mode."""
    setup_function()
    
    from spafw37.logging_config import LOG_SILENT_PARAM
    spafw37.config._config[LOG_SILENT_PARAM] = True
    
    output_calls = []
    
    def custom_handler(msg):
        output_calls.append(msg)
    
    core.set_output_handler(custom_handler)
    core.output("test message")
    
    assert output_calls == []


def test_output_verbose_mode():
    """Test output function with verbose flag requires verbose mode."""
    setup_function()
    
    from spafw37.logging_config import LOG_VERBOSE_PARAM, LOG_SILENT_PARAM
    spafw37.config._config[LOG_VERBOSE_PARAM] = False
    spafw37.config._config[LOG_SILENT_PARAM] = False
    
    output_calls = []
    
    def custom_handler(msg):
        output_calls.append(msg)
    
    core.set_output_handler(custom_handler)
    core.output("verbose message", verbose=True)
    
    assert output_calls == []
    
    # Now enable verbose
    spafw37.config._config[LOG_VERBOSE_PARAM] = True
    core.output("verbose message", verbose=True)
    
    assert output_calls == ["verbose message"]


def test_output_with_per_call_handler():
    """Test output function with per-call handler override."""
    setup_function()
    
    from spafw37.logging_config import LOG_VERBOSE_PARAM, LOG_SILENT_PARAM
    spafw37.config._config[LOG_VERBOSE_PARAM] = False
    spafw37.config._config[LOG_SILENT_PARAM] = False
    
    global_calls = []
    per_call_calls = []
    
    def global_handler(msg):
        global_calls.append(msg)
    
    def per_call_handler(msg):
        per_call_calls.append(msg)
    
    core.set_output_handler(global_handler)
    core.output("message1")
    core.output("message2", output_handler=per_call_handler)
    
    assert global_calls == ["message1"]
    assert per_call_calls == ["message2"]


def test_set_output_handler_with_default():
    """Test resetting output handler to default."""
    setup_function()
    
    from spafw37.logging_config import LOG_VERBOSE_PARAM, LOG_SILENT_PARAM
    spafw37.config._config[LOG_VERBOSE_PARAM] = False
    spafw37.config._config[LOG_SILENT_PARAM] = False
    
    # Set custom handler
    custom_calls = []
    
    def custom_handler(msg):
        custom_calls.append(msg)
    
    core.set_output_handler(custom_handler)
    core.output("custom")
    assert custom_calls == ["custom"]
    
    # Reset to default (this will use print, which we can't easily capture)
    core.set_output_handler()
    # Just verify it doesn't crash
    core.output("default")


def test_run_cli_success(monkeypatch):
    """Test run_cli successfully executes a simple command."""
    setup_function()
    
    executed = []
    
    def test_action():
        executed.append('test')
    
    test_cmd = {
        COMMAND_NAME: 'test',
        COMMAND_ACTION: test_action,
        COMMAND_DESCRIPTION: 'Test command',
    }
    
    core.add_command(test_cmd)

    # Mock sys.argv to simulate command line
    monkeypatch.setattr(sys, 'argv', ['prog', 'test'])

    core.run_cli(['test'], _embedded=True)

    assert executed == ['test']
def test_run_cli_command_parameter_error(monkeypatch, capsys):
    """Test run_cli handles CommandParameterError by displaying help and exiting."""
    setup_function()
    
    def failing_action():
        raise CommandParameterError("Missing required param", "failing")
    
    test_cmd = {
        COMMAND_NAME: 'failing',
        COMMAND_ACTION: failing_action,
        COMMAND_DESCRIPTION: 'Failing command',
    }
    
    core.add_command(test_cmd)

    # Mock sys.argv
    monkeypatch.setattr(sys, 'argv', ['prog', 'failing'])

    # Mock sys.exit to capture exit call
    exit_code = []

    def mock_exit(code):
        exit_code.append(code)

    monkeypatch.setattr(sys, 'exit', mock_exit)

    core.run_cli(['failing'], _embedded=False)

    assert exit_code == [1]
    captured = capsys.readouterr()
    assert "Error: Missing required param" in captured.out


def test_run_cli_value_error(monkeypatch, capsys):
    """Test run_cli handles ValueError by displaying error and exiting."""
    setup_function()
    
    # Mock sys.argv with unknown parameter (triggers ValueError in cli.py)
    monkeypatch.setattr(sys, 'argv', ['prog', '--unknown-param', 'value'])
    
    # Mock sys.exit
    exit_code = []
    
    def mock_exit(code):
        exit_code.append(code)
    
    monkeypatch.setattr(sys, 'exit', mock_exit)
    
    core.run_cli()
    
    assert exit_code == [1]
    captured = capsys.readouterr()
    assert "Error:" in captured.out


def test_set_log_dir():
    """Test that set_log_dir facade function calls logging module.
    
    The function should delegate to the logging module's set_log_dir function.
    This validates the facade pattern for logging directory configuration.
    """
    from unittest.mock import patch
    
    with patch('spafw37.logging.set_log_dir') as mock_set_log_dir:
        core.set_log_dir('/test/logs')
        mock_set_log_dir.assert_called_once_with('/test/logs')


def test_log_trace():
    """Test that log_trace facade function calls logging module.
    
    The function should delegate to the logging module's log_trace function
    with scope and message parameters. This validates the logging facade.
    """
    from unittest.mock import patch
    
    with patch('spafw37.logging.log_trace') as mock_log_trace:
        core.log_trace(_scope='test', _message='trace message')
        mock_log_trace.assert_called_once_with(_scope='test', _message='trace message')


def test_log_debug():
    """Test that log_debug facade function calls logging module.
    
    The function should delegate to the logging module's log_debug function
    with scope and message parameters. This validates the logging facade.
    """
    from unittest.mock import patch
    
    with patch('spafw37.logging.log_debug') as mock_log_debug:
        core.log_debug(_scope='test', _message='debug message')
        mock_log_debug.assert_called_once_with(_scope='test', _message='debug message')


def test_log_info():
    """Test that log_info facade function calls logging module.
    
    The function should delegate to the logging module's log_info function
    with scope and message parameters. This validates the logging facade.
    """
    from unittest.mock import patch
    
    with patch('spafw37.logging.log_info') as mock_log_info:
        core.log_info(_scope='test', _message='info message')
        mock_log_info.assert_called_once_with(_scope='test', _message='info message')


def test_log_warning():
    """Test that log_warning facade function calls logging module.
    
    The function should delegate to the logging module's log_warning function
    with scope and message parameters. This validates the logging facade.
    """
    from unittest.mock import patch
    
    with patch('spafw37.logging.log_warning') as mock_log_warning:
        core.log_warning(_scope='test', _message='warning message')
        mock_log_warning.assert_called_once_with(_scope='test', _message='warning message')


def test_log_error():
    """Test that log_error facade function calls logging module.
    
    The function should delegate to the logging module's log_error function
    with scope and message parameters. This validates the logging facade.
    """
    from unittest.mock import patch
    
    with patch('spafw37.logging.log_error') as mock_log_error:
        core.log_error(_scope='test', _message='error message')
        mock_log_error.assert_called_once_with(_scope='test', _message='error message')


def test_set_current_scope():
    """Test that set_current_scope facade function calls logging module.
    
    The function should delegate to the logging module's set_current_scope
    function with the scope parameter. This validates the logging scope facade.
    """
    from unittest.mock import patch
    
    with patch('spafw37.logging.set_current_scope') as mock_set_scope:
        core.set_current_scope('test-scope')
        mock_set_scope.assert_called_once_with('test-scope')

