"""Tests for the logging module."""
from __future__ import annotations

import os
import tempfile
import shutil
from pathlib import Path

from spafw37 import logging
from spafw37.logging import (
    TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL,
    log, log_trace, log_debug, log_info, log_warning, log_error,
    set_app_name, set_current_phase, set_log_dir,
    set_file_level, set_console_level, set_silent_mode,
    set_no_logging_mode, set_suppress_errors, set_phase_log_level,
    get_phase_log_level, LOGGING_PARAMS, apply_logging_config,
)
from spafw37 import config, param
from spafw37.config_consts import (
    LOG_VERBOSE_PARAM,
    LOG_TRACE_PARAM,
    LOG_TRACE_CONSOLE_PARAM,
    LOG_SILENT_PARAM,
    LOG_NO_LOGGING_PARAM,
    LOG_SUPPRESS_ERRORS_PARAM,
    LOG_DIR_PARAM,
    LOG_LEVEL_PARAM,
    LOG_PHASE_LOG_LEVEL_PARAM,
)


def test_trace_level_exists():
    """Test that TRACE level is defined."""
    assert TRACE == 5
    assert TRACE < DEBUG


def test_log_function_basic():
    """Test basic log function."""
    # Should not raise
    log(_level=INFO, _message="Test message")
    log_info(_message="Test info message")


def test_log_with_phase():
    """Test logging with phase."""
    log(_level=INFO, _phase="test-phase", _message="Test message with phase")


def test_set_app_name():
    """Test setting application name."""
    set_app_name("test-app")
    log_info(_message="Test message")


def test_set_current_phase():
    """Test setting current phase."""
    set_current_phase("setup-phase")
    log_info(_message="Test message in phase")
    set_current_phase(None)


def test_set_log_dir():
    """Test setting log directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_log_dir = os.path.join(temp_dir, "test_logs")
        set_log_dir(test_log_dir)
        log_info(_message="Test message")
        
        # Check that log directory was created
        assert os.path.exists(test_log_dir)
        
        # Check that a log file was created
        log_files = list(Path(test_log_dir).glob("log-*.log"))
        assert len(log_files) > 0


def test_log_levels():
    """Test all log level convenience functions."""
    log_trace(_message="Trace message")
    log_debug(_message="Debug message")
    log_info(_message="Info message")
    log_warning(_message="Warning message")
    log_error(_message="Error message")


def test_set_file_level():
    """Test setting file log level."""
    set_file_level(WARNING)
    log_info(_message="This should not appear in file")


def test_set_console_level():
    """Test setting console log level."""
    set_console_level(ERROR)
    log_info(_message="This should not appear on console")


def test_set_silent_mode():
    """Test silent mode."""
    set_silent_mode(True)
    log_info(_message="This should be silent")
    set_silent_mode(False)


def test_set_no_logging_mode():
    """Test no-logging mode."""
    set_no_logging_mode(True)
    log_info(_message="This should not log anywhere")
    set_no_logging_mode(False)


def test_set_suppress_errors():
    """Test error suppression."""
    set_suppress_errors(True)
    log_error(_message="This error should be suppressed")
    set_suppress_errors(False)


def test_phase_log_level():
    """Test phase-specific log levels."""
    set_phase_log_level("test-phase", WARNING)
    assert get_phase_log_level("test-phase") == WARNING
    
    # Info level should not log for this phase
    log(_level=INFO, _phase="test-phase", _message="Should be filtered")
    
    # Warning level should log
    log(_level=WARNING, _phase="test-phase", _message="Should appear")


def test_logging_params_defined():
    """Test that all logging params are defined."""
    assert len(LOGGING_PARAMS) == 9
    
    param_names = {p['name'] for p in LOGGING_PARAMS}
    expected_params = {
        LOG_VERBOSE_PARAM,
        LOG_TRACE_PARAM,
        LOG_TRACE_CONSOLE_PARAM,
        LOG_SILENT_PARAM,
        LOG_NO_LOGGING_PARAM,
        LOG_SUPPRESS_ERRORS_PARAM,
        LOG_DIR_PARAM,
        LOG_LEVEL_PARAM,
        LOG_PHASE_LOG_LEVEL_PARAM,
    }
    assert param_names == expected_params


def test_apply_logging_config_verbose():
    """Test applying verbose logging config."""
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Set verbose flag
    verbose_param = param.get_param_by_name(LOG_VERBOSE_PARAM)
    config.set_config_value(verbose_param, True)
    
    # Apply config
    apply_logging_config()
    
    # Verify console level is DEBUG
    # (We can't directly check the level, but we can verify it doesn't raise)


def test_apply_logging_config_trace():
    """Test applying trace logging config."""
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Set trace flag
    trace_param = param.get_param_by_name(LOG_TRACE_PARAM)
    config.set_config_value(trace_param, True)
    
    # Apply config
    apply_logging_config()


def test_apply_logging_config_log_dir():
    """Test applying log directory config."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Add logging params
        param.add_params(LOGGING_PARAMS)
        
        # Set log dir
        test_log_dir = os.path.join(temp_dir, "config_logs")
        log_dir_param = param.get_param_by_name(LOG_DIR_PARAM)
        config.set_config_value(log_dir_param, test_log_dir)
        
        # Apply config
        apply_logging_config()
        
        # Log a message
        log_info(_message="Test message in configured dir")
        
        # Verify log dir was created
        assert os.path.exists(test_log_dir)


def test_apply_logging_config_phase_log_level():
    """Test applying phase-specific log level config."""
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Set phase log level
    phase_param = param.get_param_by_name(LOG_PHASE_LOG_LEVEL_PARAM)
    config.set_config_value(phase_param, ["setup", "WARNING", "execution", "DEBUG"])
    
    # Apply config
    apply_logging_config()
    
    # Verify phase levels were set
    assert get_phase_log_level("setup") == WARNING
    assert get_phase_log_level("execution") == DEBUG


def test_log_file_naming_pattern():
    """Test that log files follow the naming pattern log-{yyyy-MM-dd-hh.mm.ss}.log."""
    with tempfile.TemporaryDirectory() as temp_dir:
        set_log_dir(temp_dir)
        log_info(_message="Test message for filename check")
        
        log_files = list(Path(temp_dir).glob("log-*.log"))
        assert len(log_files) > 0
        
        # Check filename pattern (should match log-YYYY-MM-DD-HH.MM.SS.log)
        log_file = log_files[0]
        name = log_file.name
        assert name.startswith("log-")
        assert name.endswith(".log")
        assert len(name.split("-")) >= 4  # log, YYYY, MM, DD-HH.MM.SS.log


def test_logging_params_persistence():
    """Test that logging params have correct persistence settings."""
    # Verbose should not persist
    verbose_param = [p for p in LOGGING_PARAMS if p['name'] == LOG_VERBOSE_PARAM][0]
    assert verbose_param['persistence'] == 'never'
    
    # Log dir should persist
    log_dir_param = [p for p in LOGGING_PARAMS if p['name'] == LOG_DIR_PARAM][0]
    assert log_dir_param['persistence'] == 'always'


def test_switch_list_conflicts():
    """Test that mutually exclusive params are defined in switch lists."""
    silent_param = [p for p in LOGGING_PARAMS if p['name'] == LOG_SILENT_PARAM][0]
    assert LOG_VERBOSE_PARAM in silent_param['switch-list']
    assert LOG_NO_LOGGING_PARAM in silent_param['switch-list']
    
    no_logging_param = [p for p in LOGGING_PARAMS if p['name'] == LOG_NO_LOGGING_PARAM][0]
    assert LOG_SILENT_PARAM in no_logging_param['switch-list']


def test_command_execution_logging():
    """Test that command execution produces INFO level logs."""
    from spafw37 import command
    from spafw37.config_consts import (
        COMMAND_NAME, COMMAND_ACTION, COMMAND_PHASE, PHASE_EXECUTION
    )
    
    # Set up test environment
    with tempfile.TemporaryDirectory() as temp_dir:
        set_log_dir(temp_dir)
        
        # Reset command module state completely
        command._commands = {}
        command._finished_commands = []
        command._phases = {PHASE_EXECUTION: []}
        command._phases_completed = []
        command._command_queue = []
        
        # Create a test command
        test_executed = {'value': False}
        
        def test_action():
            test_executed['value'] = True
        
        test_cmd = {
            COMMAND_NAME: 'test-cmd',
            COMMAND_ACTION: test_action,
            COMMAND_PHASE: PHASE_EXECUTION,
        }
        
        # Register and queue command
        command.add_command(test_cmd)
        command.queue_command('test-cmd')
        
        # Execute command queue
        command.run_command_queue()
        
        # Verify command was executed
        assert test_executed['value'] is True
        
        # Verify log file contains command execution logs
        log_files = list(Path(temp_dir).glob("log-*.log"))
        assert len(log_files) > 0
        
        log_content = log_files[0].read_text()
        assert 'Starting command: test-cmd' in log_content
        assert 'Completed command: test-cmd' in log_content


def test_param_setting_logging():
    """Test that param value setting produces DEBUG level logs."""
    from spafw37.config_consts import PARAM_NAME, PARAM_BIND_TO, PARAM_TYPE
    
    with tempfile.TemporaryDirectory() as temp_dir:
        set_log_dir(temp_dir)
        set_file_level(DEBUG)
        
        # Create a test param
        test_param = {
            PARAM_NAME: 'test-param-log',
            PARAM_BIND_TO: 'test-param-log',
            PARAM_TYPE: 'text',
        }
        
        # Set param value
        config.set_config_value(test_param, 'test-value')
        
        # Verify log file contains param setting logs
        log_files = list(Path(temp_dir).glob("log-*.log"))
        assert len(log_files) > 0
        
        log_content = log_files[0].read_text()
        assert "Set param 'test-param-log' = test-value" in log_content
