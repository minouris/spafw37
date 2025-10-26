"""Tests for buffered parameter registration and run-level parsing with new structure."""

import pytest
from spafw37 import cli, config, param, command
from spafw37.config_consts import (
    PARAM_NAME, PARAM_ALIASES, PARAM_TYPE, PARAM_DEFAULT, PARAM_DEFERRED,
    PARAM_TYPE_TEXT, PARAM_TYPE_NUMBER, PARAM_TYPE_TOGGLE,
    RUN_LEVEL_NAME, RUN_LEVEL_PARAMS, RUN_LEVEL_COMMANDS, RUN_LEVEL_CONFIG, RUN_LEVEL_ERROR_HANDLER
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


def test_build_params_no_run_level():
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


def test_add_run_level():
    """Test adding a run-level."""
    setup_function()
    
    param.add_run_level({
        RUN_LEVEL_NAME: 'init',
        RUN_LEVEL_PARAMS: ['verbose'],
        RUN_LEVEL_CONFIG: {'verbose': True}
    })
    
    assert len(param._run_levels) == 1
    run_level = param.get_run_level('init')
    assert run_level is not None
    assert run_level[RUN_LEVEL_NAME] == 'init'


def test_run_level_filters_params():
    """Test that run-level only registers params in its param list."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'included',
        PARAM_ALIASES: ['--included'],
        PARAM_DEFAULT: 'value1'
    })
    
    param.add_param({
        PARAM_NAME: 'excluded',
        PARAM_ALIASES: ['--excluded'],
        PARAM_DEFAULT: 'value2'
    })
    
    param.add_run_level({
        RUN_LEVEL_NAME: 'init',
        RUN_LEVEL_PARAMS: ['included'],
        RUN_LEVEL_CONFIG: {}
    })
    
    param.build_params_for_run_level('init')
    
    assert 'included' in param._params
    assert 'excluded' not in param._params


def test_run_level_config_override():
    """Test that run-level config overrides param defaults."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'test',
        PARAM_ALIASES: ['--test'],
        PARAM_DEFAULT: 'base'
    })
    
    param.add_run_level({
        RUN_LEVEL_NAME: 'init',
        RUN_LEVEL_PARAMS: ['test'],
        RUN_LEVEL_CONFIG: {'test': 'override'}
    })
    
    param.build_params_for_run_level('init')
    
    assert param._params['test'][PARAM_DEFAULT] == 'override'


def test_list_run_levels():
    """Test listing run-level names."""
    setup_function()
    
    param.add_run_level({RUN_LEVEL_NAME: 'init', RUN_LEVEL_PARAMS: []})
    param.add_run_level({RUN_LEVEL_NAME: 'main', RUN_LEVEL_PARAMS: []})
    
    names = param.list_run_levels()
    assert names == ['init', 'main']


def test_param_deferred_false_activates_immediately():
    """Test that PARAM_DEFERRED=False causes immediate activation."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'immediate',
        PARAM_ALIASES: ['--immediate'],
        PARAM_DEFERRED: False
    })
    
    assert 'immediate' in param._params
    assert len(param._buffered_params) == 0


def test_param_deferred_true_buffers():
    """Test that PARAM_DEFERRED=True (default) buffers param."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'buffered',
        PARAM_ALIASES: ['--buffered'],
        PARAM_DEFERRED: True
    })
    
    assert 'buffered' not in param._params
    assert len(param._buffered_params) == 1


def test_run_level_error_handler_default():
    """Test default error handler is called on error."""
    setup_function()
    
    param.add_param({
        PARAM_NAME: 'test',
        PARAM_ALIASES: ['--test']
    })
    
    def bad_activation(param_dict):
        raise ValueError("Test error")
    
    original_activate = param._activate_param
    param._activate_param = bad_activation
    
    try:
        with pytest.raises(ValueError, match="Test error"):
            param.build_params_for_run_level('test')
    finally:
        param._activate_param = original_activate


def test_run_level_custom_error_handler():
    """Test custom error handler in run-level definition."""
    setup_function()
    
    errors = []
    
    def custom_handler(run_level_name, error):
        errors.append((run_level_name, error))
    
    param.add_param({
        PARAM_NAME: 'test',
        PARAM_ALIASES: ['--test']
    })
    
    param.add_run_level({
        RUN_LEVEL_NAME: 'custom',
        RUN_LEVEL_PARAMS: ['test'],
        RUN_LEVEL_CONFIG: {},
        RUN_LEVEL_ERROR_HANDLER: custom_handler
    })
    
    def bad_activation(param_dict):
        raise ValueError("Test error")
    
    original_activate = param._activate_param
    param._activate_param = bad_activation
    
    try:
        param.build_params_for_run_level('custom')
        assert len(errors) == 1
        assert errors[0][0] == 'custom'
        assert isinstance(errors[0][1], ValueError)
    finally:
        param._activate_param = original_activate
