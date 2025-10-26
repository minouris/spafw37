"""Tests for buffered parameter registration and run-level parsing."""

import pytest
from spafw37 import cli, config, param, command
from spafw37.config_consts import (
    PARAM_NAME, PARAM_ALIASES, PARAM_TYPE, PARAM_DEFAULT, PARAM_BIND_TO,
    PARAM_TYPE_TEXT, PARAM_TYPE_NUMBER, PARAM_TYPE_TOGGLE, PARAM_DEFERRED
)


def setup_function():
    """Reset module state between tests."""
    param._param_aliases.clear()
    param._params.clear()
    param._buffered_params.clear()
    param._run_levels.clear()
    param._xor_list.clear()
    config._non_persisted_config_names.clear()
    config._config.clear()
    config._persistent_config.clear()
    cli._pre_parse_actions.clear()
    cli._post_parse_actions.clear()
    command._commands.clear()
    command._finished_commands.clear()
    command._command_queue.clear()
    command._phases = {command.PHASE_DEFAULT: []}
    command._phases_completed.clear()


def test_add_buffered_param():
    """Test adding a parameter to the buffer."""
    setup_function()
    
    param_dict = {
        PARAM_NAME: 'test',
        PARAM_ALIASES: ['--test'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DEFAULT: 'value'
    }
    
    param.add_param(param_dict)
    
    assert len(param._buffered_params) == 1
    assert param._buffered_params[0][PARAM_NAME] == 'test'
    assert len(param._params) == 0


def test_build_params_for_run_level_no_level():
    """Test building params without a run-level."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'test',
        PARAM_ALIASES: ['--test'],
        PARAM_DEFAULT: 'base_value'
    })
    
    param.build_params_for_run_level()
    
    assert 'test' in param._params
    assert param._params['test'][PARAM_DEFAULT] == 'base_value'
    assert len(param._buffered_params) == 0


def test_register_run_level():
    """Test registering a run-level."""
    setup_function()
    
    param.register_run_level('dev', {
        'test': 'dev_value',
        'other': 'dev_other'
    })
    
    assert 'dev' in param._run_levels
    assert param._run_levels['dev']['test'] == 'dev_value'


def test_build_params_with_run_level():
    """Test building params with a run-level applied."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'test',
        PARAM_ALIASES: ['--test'],
        PARAM_DEFAULT: 'base_value'
    })
    
    param.register_run_level('dev', {'test': 'dev_value'})
    
    param.build_params_for_run_level('dev')
    
    assert 'test' in param._params
    assert param._params['test'][PARAM_DEFAULT] == 'dev_value'


def test_multiple_run_levels_override():
    """Test that later run-levels override earlier ones."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'test',
        PARAM_ALIASES: ['--test'],
        PARAM_DEFAULT: 'base_value'
    })
    
    param.register_run_level('dev', {'test': 'dev_value'})
    param.register_run_level('prod', {'test': 'prod_value'})
    
    param.build_params_for_run_level('dev')
    
    assert param._params['test'][PARAM_DEFAULT] == 'dev_value'
    
    param._params.clear()
    param._param_aliases.clear()
    param.add_param({
        PARAM_NAME: 'test',
        PARAM_ALIASES: ['--test'],
        PARAM_DEFAULT: 'base_value'
    })
    
    param.build_params_for_run_level('prod')
    
    assert param._params['test'][PARAM_DEFAULT] == 'prod_value'


def test_extract_run_levels_single():
    """Test extracting a single run-level from args."""
    setup_function()
    
    args = ['-R', 'dev', '--test', 'value']
    levels = cli._extract_run_levels(args)
    
    assert levels == ['dev']


def test_extract_run_levels_comma_separated():
    """Test extracting comma-separated run-levels."""
    setup_function()
    
    args = ['-R', 'dev,staging,prod', '--test', 'value']
    levels = cli._extract_run_levels(args)
    
    assert levels == ['dev', 'staging', 'prod']


def test_extract_run_levels_multiple_flags():
    """Test extracting run-levels from multiple flags."""
    setup_function()
    
    args = ['-R', 'dev', '--test', 'value', '-R', 'prod']
    levels = cli._extract_run_levels(args)
    
    assert levels == ['dev', 'prod']


def test_extract_run_levels_long_form():
    """Test extracting run-levels with long form alias."""
    setup_function()
    
    args = ['--run-levels', 'dev', '--test', 'value']
    levels = cli._extract_run_levels(args)
    
    assert levels == ['dev']


def test_filter_run_level_args():
    """Test filtering run-level arguments from args list."""
    setup_function()
    
    args = ['-R', 'dev', '--test', 'value', '-R', 'prod', 'command']
    filtered = cli._filter_run_level_args(args)
    
    assert filtered == ['--test', 'value', 'command']


def test_handle_cli_args_with_run_level():
    """Test full CLI handling with run-level."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'test',
        PARAM_ALIASES: ['--test'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DEFAULT: 'base_value'
    })
    
    param.register_run_level('dev', {'test': 'dev_value'})
    
    cli.handle_cli_args(['-R', 'dev', '--test', 'cli_value'])
    
    assert config.get_config_value('test') == 'cli_value'


def test_handle_cli_args_run_level_default_used():
    """Test that run-level default is used when no CLI override."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'test',
        PARAM_ALIASES: ['--test'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DEFAULT: 'base_value'
    })
    
    param.register_run_level('dev', {'test': 'dev_value'})
    
    cli.handle_cli_args(['-R', 'dev'])
    
    assert config.get_config_value('test') == 'dev_value'


def test_list_run_levels():
    """Test listing registered run-levels."""
    setup_function()
    
    param.register_run_level('dev', {})
    param.register_run_level('prod', {})
    param.register_run_level('staging', {})
    
    levels = param.list_run_levels()
    
    assert set(levels) == {'dev', 'prod', 'staging'}


def test_get_run_level():
    """Test getting a specific run-level."""
    setup_function()
    
    param.register_run_level('dev', {'test': 'value'})
    
    level = param.get_run_level('dev')
    
    assert level == {'test': 'value'}
    assert param.get_run_level('nonexistent') is None


def test_get_buffered_params():
    """Test getting buffered parameters."""
    setup_function()
    
    param.add_param({PARAM_NAME: 'p1'})
    param.add_param({PARAM_NAME: 'p2'})
    
    buffered = param.get_buffered_params()
    
    assert len(buffered) == 2
    assert buffered[0][PARAM_NAME] == 'p1'
    assert buffered[1][PARAM_NAME] == 'p2'


def test_backward_compatibility_add_param():
    """Test that add_param now buffers parameters."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'test',
        PARAM_ALIASES: ['--test'],
        PARAM_DEFAULT: 'value'
    })
    
    # Should be in buffer, not yet in _params
    assert len(param._buffered_params) == 1
    assert 'test' not in param._params
    
    # After building, should be in _params
    param.build_params_for_run_level()
    assert 'test' in param._params
    assert '--test' in param._param_aliases


def test_cli_override_always_wins():
    """Test that CLI arguments always override run-level defaults."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'value',
        PARAM_ALIASES: ['--value'],
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_DEFAULT: 10
    })
    
    param.register_run_level('dev', {'value': 20})
    param.register_run_level('prod', {'value': 30})
    
    cli.handle_cli_args(['-R', 'dev,prod', '--value', '50'])
    
    assert config.get_config_value('value') == 50


def test_multiple_params_with_run_level():
    """Test multiple parameters with run-level."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'host',
        PARAM_ALIASES: ['--host'],
        PARAM_DEFAULT: 'localhost'
    })
    
    param.add_param({
        PARAM_NAME: 'port',
        PARAM_ALIASES: ['--port'],
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_DEFAULT: 8000
    })
    
    param.register_run_level('prod', {
        'host': 'prod.example.com',
        'port': 443
    })
    
    cli.handle_cli_args(['-R', 'prod'])
    
    assert config.get_config_value('host') == 'prod.example.com'
    assert config.get_config_value('port') == 443


def test_param_deferred_false_activates_immediately():
    """Test that params with PARAM_DEFERRED=False are activated immediately."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'immediate',
        PARAM_ALIASES: ['--immediate'],
        PARAM_DEFAULT: 'immediate_value',
        PARAM_DEFERRED: False
    })
    
    # Should be immediately in _params, not in buffer
    assert 'immediate' in param._params
    assert len(param._buffered_params) == 0
    assert param._params['immediate'][PARAM_DEFAULT] == 'immediate_value'


def test_param_deferred_true_buffers():
    """Test that params with PARAM_DEFERRED=True (or default) are buffered."""
    setup_function()
    
    # Explicit True
    param.add_param({
        PARAM_NAME: 'deferred1',
        PARAM_ALIASES: ['--deferred1'],
        PARAM_DEFERRED: True
    })
    
    # Default (not specified, should default to True)
    param.add_param({
        PARAM_NAME: 'deferred2',
        PARAM_ALIASES: ['--deferred2']
    })
    
    # Both should be in buffer, not in _params
    assert 'deferred1' not in param._params
    assert 'deferred2' not in param._params
    assert len(param._buffered_params) == 2


def test_mixed_deferred_and_immediate_params():
    """Test mixing immediate and deferred params."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'immediate',
        PARAM_ALIASES: ['--immediate'],
        PARAM_DEFERRED: False
    })
    
    param.add_param({
        PARAM_NAME: 'deferred',
        PARAM_ALIASES: ['--deferred']
    })
    
    # immediate should be in _params
    assert 'immediate' in param._params
    # deferred should be in buffer
    assert len(param._buffered_params) == 1
    assert param._buffered_params[0][PARAM_NAME] == 'deferred'


def test_run_level_error_handler_default():
    """Test default error handler logs and re-raises."""
    setup_function()
    
    # Add a param that will cause an error during activation
    param.add_param({
        PARAM_NAME: 'test',
        PARAM_ALIASES: ['invalid-alias']  # Invalid alias format
    })
    
    param.register_run_level('bad', {'test': 'value'})
    
    # Should raise ValueError through default error handler
    try:
        param.build_params_for_run_level('bad')
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert 'Invalid alias format' in str(e)


def test_run_level_error_handler_custom():
    """Test custom error handler."""
    setup_function()
    
    errors_caught = []
    
    def custom_handler(run_level, error):
        errors_caught.append((run_level, str(error)))
        # Don't re-raise, just log
    
    param.set_run_level_error_handler(custom_handler)
    
    # Add a param that will cause an error
    param.add_param({
        PARAM_NAME: 'test',
        PARAM_ALIASES: ['invalid-alias']
    })
    
    param.register_run_level('bad', {'test': 'value'})
    
    # Should NOT raise because custom handler doesn't re-raise
    param.build_params_for_run_level('bad')
    
    assert len(errors_caught) == 1
    assert errors_caught[0][0] == 'bad'
    assert 'Invalid alias format' in errors_caught[0][1]
    
    # Reset to default
    param.set_run_level_error_handler(param._default_run_level_error_handler)


def test_run_level_get_error_handler():
    """Test getting the current error handler."""
    setup_function()
    
    # Should return default handler
    handler = param.get_run_level_error_handler()
    assert handler == param._default_run_level_error_handler
    
    # Set custom and verify
    def custom_handler(run_level, error):
        pass
    
    param.set_run_level_error_handler(custom_handler)
    assert param.get_run_level_error_handler() == custom_handler
    
    # Reset
    param.set_run_level_error_handler(param._default_run_level_error_handler)
