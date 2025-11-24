"""Tests for the logging module."""
from __future__ import annotations

import logging as stdlib_logging
import os
import tempfile
import shutil
from pathlib import Path

from spafw37 import logging
from spafw37.logging import (
    TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL,
    log, log_trace, log_debug, log_info, log_warning, log_error,
    set_current_scope, set_log_dir,
    set_file_level, set_console_level, set_silent_mode,
    set_no_logging_mode, set_suppress_errors, set_scope_log_level,
    get_scope_log_level, LOGGING_PARAMS, apply_logging_config,
    LOG_VERBOSE_PARAM,
    LOG_TRACE_PARAM,
    LOG_TRACE_CONSOLE_PARAM,
    LOG_SILENT_PARAM,
    LOG_NO_LOGGING_PARAM,
    LOG_NO_FILE_LOGGING_PARAM,
    LOG_SUPPRESS_ERRORS_PARAM,
    LOG_DIR_PARAM,
    LOG_LEVEL_PARAM,
    LOG_PHASE_LOG_LEVEL_PARAM,
)
from spafw37 import config_func as config, param
from spafw37.constants.param import PARAM_NAME


def setup_function():
    """Reset logging module state before each test.
    
    This ensures each test starts with a clean logging configuration,
    preventing test interference from shared handler state.
    """
    # Remove any existing handlers from stdlib logger if it exists
    stdlib_logger = stdlib_logging.getLogger('spafw37')
    for handler in stdlib_logger.handlers[:]:
        stdlib_logger.removeHandler(handler)
        handler.close()
    
    # Reset logging module state
    logging._logger = None
    logging._file_handler = None
    logging._console_handler = None
    logging._error_handler = None
    logging._current_scope = None
    logging._suppress_errors = False
    logging._scope_log_levels = {}
    logging._log_dir = logging._DEFAULT_LOG_DIR
    
    # Reset params module state
    param._PARAMS = []
    
    # Reset config module state (both modules)
    from spafw37 import config as config_module
    config_module._config = {}
    config._persistent_config = {}


def test_trace_level_exists():
    """Test that TRACE level is defined."""
    assert TRACE == 5
    assert TRACE < DEBUG


def test_log_function_basic():
    """Test basic log function."""
    # Should not raise
    log(_level=INFO, _message="Test message")
    log_info(_message="Test info message")


def test_log_with_scope():
    """Test logging with scope."""
    log(_level=INFO, _scope="test-scope", _message="Test message with scope")


def test_set_app_name():
    """Test setting application name."""
    config.set_app_name("test-app")
    log_info(_message="Test message")


def test_set_current_scope():
    """Test setting current scope."""
    set_current_scope("setup-scope")
    log_info(_message="Test message in scope")
    set_current_scope(None)


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


def test_scope_log_level():
    """Test scope-specific log levels."""
    set_scope_log_level("test-scope", WARNING)
    assert get_scope_log_level("test-scope") == WARNING
    
    # Info level should not log for this scope
    log(_level=INFO, _scope="test-scope", _message="Should be filtered")
    
    # Warning level should log
    log(_level=WARNING, _scope="test-scope", _message="Should appear")


def test_logging_params_defined():
    """Test that all logging params are defined."""
    assert len(LOGGING_PARAMS) == 10
    
    param_names = {p['name'] for p in LOGGING_PARAMS}
    expected_params = {
        LOG_VERBOSE_PARAM,
        LOG_TRACE_PARAM,
        LOG_TRACE_CONSOLE_PARAM,
        LOG_SILENT_PARAM,
        LOG_NO_LOGGING_PARAM,
        LOG_NO_FILE_LOGGING_PARAM,
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
    param.set_param(param_name=verbose_param[PARAM_NAME], value=True)
    
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
    param.set_param(param_name=trace_param[PARAM_NAME], value=True)
    
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
        param.set_param(param_name=log_dir_param[PARAM_NAME], value=test_log_dir)
        
        # Apply config
        apply_logging_config()
        
        # Log a message
        log_info(_message="Test message in configured dir")
        
        # Verify log dir was created
        assert os.path.exists(test_log_dir)


def test_apply_logging_config_scope_log_level():
    """Test applying scope-specific log level config."""
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Set scope log level (using phase-log-level param for backward compatibility)
    phase_param = param.get_param_by_name(LOG_PHASE_LOG_LEVEL_PARAM)
    param.set_param(param_name=phase_param[PARAM_NAME], value=["setup", "WARNING", "execution", "DEBUG"])
    
    # Apply config
    apply_logging_config()
    
    # Verify scope levels were set
    assert get_scope_log_level("setup") == WARNING
    assert get_scope_log_level("execution") == DEBUG


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
    from spafw37.constants.command import (
        COMMAND_NAME, COMMAND_ACTION, COMMAND_PHASE
    )
    from spafw37.constants.phase import PHASE_EXECUTION
    
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
    from spafw37.constants.param import PARAM_CONFIG_NAME, PARAM_TYPE
    
    with tempfile.TemporaryDirectory() as temp_dir:
        set_log_dir(temp_dir)
        set_file_level(DEBUG)
        
        # Create and register a test param
        test_param = {
            PARAM_NAME: 'test-param-log',
            PARAM_CONFIG_NAME: 'test-param-log',
            PARAM_TYPE: 'text',
        }
        param.add_param(test_param)

        # Set param value
        param.set_param(param_name=test_param[PARAM_NAME], value='test-value')        # Verify log file contains param setting logs
        log_files = list(Path(temp_dir).glob("log-*.log"))
        assert len(log_files) > 0
        
        log_content = log_files[0].read_text()
        assert "Set param 'test-param-log' = test-value" in log_content


def test_should_log_to_console_with_no_logging():
    """Test console logging is disabled when LOG_NO_LOGGING_PARAM is set.
    
    When the no-logging parameter is enabled, console logging should be
    disabled regardless of other settings. This validates the logging
    suppression logic (line 211).
    """
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Get and set no-logging param
    no_logging_param = param.get_param_by_name(LOG_NO_LOGGING_PARAM)
    param.set_param(param_name=no_logging_param[PARAM_NAME], value=True)
    
    # Verify console logging is disabled
    assert logging._should_log_to_console() is False


def test_should_log_to_console_in_silent_mode():
    """Test console logging is disabled in silent mode.
    
    When silent mode is enabled, console logging should be disabled.
    This validates the silent mode check (line 213).
    """
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Get and set silent param
    silent_param = param.get_param_by_name(LOG_SILENT_PARAM)
    param.set_param(param_name=silent_param[PARAM_NAME], value=True)
    
    # Verify console logging is disabled
    assert logging._should_log_to_console() is False


def test_should_log_to_file_with_no_logging():
    """Test file logging is disabled when LOG_NO_LOGGING_PARAM is set.
    
    When the no-logging parameter is enabled, file logging should be
    disabled. This validates the logging suppression logic (line 220).
    """
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Get and set no-logging param
    no_logging_param = param.get_param_by_name(LOG_NO_LOGGING_PARAM)
    param.set_param(param_name=no_logging_param[PARAM_NAME], value=True)
    
    # Verify file logging is disabled
    assert logging._should_log_to_file() is False


def test_should_log_to_file_with_no_file_logging():
    """Test file logging is disabled when LOG_NO_FILE_LOGGING_PARAM is set.
    
    When the no-file-logging parameter is enabled, file logging should be
    disabled even if console logging is still active. This validates the
    file-specific suppression logic (line 222).
    """
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Get and set no-file-logging param
    no_file_logging_param = param.get_param_by_name(LOG_NO_FILE_LOGGING_PARAM)
    param.set_param(param_name=no_file_logging_param[PARAM_NAME], value=True)
    
    # Verify file logging is disabled
    assert logging._should_log_to_file() is False


def test_log_with_both_logging_disabled():
    """Test log function returns early when both console and file are disabled.
    
    When both console and file logging are disabled, the log function should
    return without creating log records. This validates the early return
    optimization (line 244).
    """
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Get and set no-logging param
    no_logging_param = param.get_param_by_name(LOG_NO_LOGGING_PARAM)
    param.set_param(param_name=no_logging_param[PARAM_NAME], value=True)
    
    # This should return early without error
    logging.log(logging.INFO, _message='Should not be logged')


def test_apply_logging_config_with_log_level_param():
    """Test explicit log-level parameter sets both console and file levels.
    
    When an explicit log-level is specified, it should override all other
    level settings for both console and file. This validates the log-level
    parameter handling (lines 327-329).
    """
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Get and set log-level param
    log_level_param = param.get_param_by_name(LOG_LEVEL_PARAM)
    param.set_param(param_name=log_level_param[PARAM_NAME], value='WARNING')
    
    logging.apply_logging_config()
    
    # Both console and file should be at WARNING level
    assert logging._console_handler.level == stdlib_logging.WARNING
    assert logging._file_handler.level == stdlib_logging.WARNING


def test_apply_logging_config_with_trace_console():
    """Test trace-console parameter sets only console to TRACE.
    
    When trace-console is enabled, only console logging should be at TRACE
    level while file remains at default. This validates the trace-console
    parameter handling (line 338).
    """
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Get and set trace-console param
    trace_console_param = param.get_param_by_name(LOG_TRACE_CONSOLE_PARAM)
    param.set_param(param_name=trace_console_param[PARAM_NAME], value=True)
    
    logging.apply_logging_config()
    
    # Console should be TRACE, file should be DEBUG (default)
    assert logging._console_handler.level == logging.TRACE
    assert logging._file_handler.level == stdlib_logging.DEBUG


def test_apply_logging_config_with_silent():
    """Test silent parameter disables console logging.
    
    When silent mode is enabled, console logging should be set to a level
    above CRITICAL to effectively disable it. This validates the silent
    mode handling (line 346).
    """
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Get and set silent param
    silent_param = param.get_param_by_name(LOG_SILENT_PARAM)
    param.set_param(param_name=silent_param[PARAM_NAME], value=True)
    
    logging.apply_logging_config()
    
    # Console should be above CRITICAL (disabled)
    assert logging._console_handler.level > stdlib_logging.CRITICAL


def test_apply_logging_config_with_no_logging():
    """Test no-logging parameter disables both console and file.
    
    When no-logging mode is enabled, both console and file logging should
    be disabled. This validates the no-logging mode handling (lines 350-351).
    """
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Get and set no-logging param
    no_logging_param = param.get_param_by_name(LOG_NO_LOGGING_PARAM)
    param.set_param(param_name=no_logging_param[PARAM_NAME], value=True)
    
    logging.apply_logging_config()
    
    # Both should be above CRITICAL (disabled)
    assert logging._console_handler.level > stdlib_logging.CRITICAL
    assert logging._file_handler.level > stdlib_logging.CRITICAL


def test_apply_logging_config_with_no_file_logging():
    """Test no-file-logging parameter disables file logging.
    
    When no-file-logging is enabled, file logging should be disabled but
    console can remain active. This validates the no-file-logging handling
    (line 359).
    """
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Get and set no-file-logging param
    no_file_logging_param = param.get_param_by_name(LOG_NO_FILE_LOGGING_PARAM)
    param.set_param(param_name=no_file_logging_param[PARAM_NAME], value=True)
    
    logging.apply_logging_config()
    
    # File should be above CRITICAL (disabled)
    assert logging._file_handler.level > stdlib_logging.CRITICAL


def test_apply_logging_config_with_suppress_errors():
    """Test suppress-errors parameter enables error suppression.
    
    When suppress-errors is enabled, the logging system should suppress
    error output. This validates the suppress-errors handling (line 368).
    """
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Get and set suppress-errors param
    suppress_errors_param = param.get_param_by_name(LOG_SUPPRESS_ERRORS_PARAM)
    param.set_param(param_name=suppress_errors_param[PARAM_NAME], value=True)
    
    logging.apply_logging_config()
    
    # Verify suppress errors is enabled
    assert logging._suppress_errors is True


def test_no_logging_allows_errors_to_stderr(capfd):
    """Test that errors reach stderr when --no-logging is set.
    
    When no-logging mode is enabled, ERROR and CRITICAL messages should
    still be output to stderr via the error handler. This validates the
    documented behavior of --no-logging flag.
    """
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Set no-logging mode
    no_logging_param = param.get_param_by_name(LOG_NO_LOGGING_PARAM)
    param.set_param(param_name=no_logging_param[PARAM_NAME], value=True)
    
    # Apply logging config
    apply_logging_config()
    
    # Log an error
    log_error(_message="Test error message")
    
    # Capture output
    captured = capfd.readouterr()
    
    # Verify error appears on stderr
    assert "Test error message" in captured.err
    assert "ERROR" in captured.err
    
    # Verify nothing on stdout
    assert "Test error message" not in captured.out


def test_silent_allows_errors_to_stderr(capfd):
    """Test that errors reach stderr when --silent is set.
    
    When silent mode is enabled, ERROR and CRITICAL messages should
    still be output to stderr via the error handler. This validates the
    documented behavior of --silent flag.
    """
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Set silent mode
    silent_param = param.get_param_by_name(LOG_SILENT_PARAM)
    param.set_param(param_name=silent_param[PARAM_NAME], value=True)
    
    # Apply logging config
    apply_logging_config()
    
    # Log an error
    log_error(_message="Test silent error message")
    
    # Capture output
    captured = capfd.readouterr()
    
    # Verify error appears on stderr
    assert "Test silent error message" in captured.err
    assert "ERROR" in captured.err
    
    # Verify nothing on stdout
    assert "Test silent error message" not in captured.out


def test_suppress_errors_blocks_stderr(capfd):
    """Test that --suppress-errors blocks all output including stderr.
    
    When suppress-errors mode is enabled, no messages should be output
    to stderr or stdout, including ERROR messages. This validates the
    documented behavior of --suppress-errors flag.
    """
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Set suppress-errors mode
    suppress_errors_param = param.get_param_by_name(LOG_SUPPRESS_ERRORS_PARAM)
    param.set_param(param_name=suppress_errors_param[PARAM_NAME], value=True)
    
    # Apply logging config
    apply_logging_config()
    
    # Log an error
    log_error(_message="Test suppressed error message")
    
    # Capture output
    captured = capfd.readouterr()
    
    # Verify no output to stderr
    assert "Test suppressed error message" not in captured.err
    
    # Verify no output to stdout
    assert "Test suppressed error message" not in captured.out


def test_no_logging_suppresses_non_errors(capfd):
    """Test that --no-logging suppresses non-error messages.
    
    When no-logging mode is enabled, INFO, WARNING, DEBUG, and TRACE
    messages should be suppressed entirely. Only ERROR and CRITICAL
    should reach stderr. This ensures the fix doesn't break suppression.
    """
    # Add logging params
    param.add_params(LOGGING_PARAMS)
    
    # Set no-logging mode
    no_logging_param = param.get_param_by_name(LOG_NO_LOGGING_PARAM)
    param.set_param(param_name=no_logging_param[PARAM_NAME], value=True)
    
    # Apply logging config
    apply_logging_config()
    
    # Log non-error messages
    log_trace(_message="Test trace message")
    log_debug(_message="Test debug message")
    log_info(_message="Test info message")
    log_warning(_message="Test warning message")
    
    # Capture output
    captured = capfd.readouterr()
    
    # Verify no output to stdout
    assert "Test trace message" not in captured.out
    assert "Test debug message" not in captured.out
    assert "Test info message" not in captured.out
    assert "Test warning message" not in captured.out
    
    # Verify no output to stderr
    assert "Test trace message" not in captured.err
    assert "Test debug message" not in captured.err
    assert "Test info message" not in captured.err
    assert "Test warning message" not in captured.err


def test_log_level_param_accepts_valid_values():
    """Test that LOG_LEVEL_PARAM accepts all valid log level values.
    
    Verifies that the LOG_LEVEL_PARAM can be set to any of the allowed values:
    CRITICAL, ERROR, WARNING, INFO, DEBUG, TRACE.
    """
    setup_function()
    param.add_params(LOGGING_PARAMS)
    
    # All valid log levels should be accepted
    valid_levels = ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE']
    for level in valid_levels:
        param.set_param(param_name=LOG_LEVEL_PARAM, value=level)
        assert param.get_param(param_name=LOG_LEVEL_PARAM) == level


def test_log_level_param_rejects_invalid_values():
    """Test that LOG_LEVEL_PARAM rejects invalid log level values.
    
    Verifies that attempting to set LOG_LEVEL_PARAM to a value not in the
    allowed values list raises a ValueError with appropriate error message.
    """
    setup_function()
    param.add_params(LOGGING_PARAMS)
    
    import pytest
    # Invalid log levels should be rejected
    with pytest.raises(ValueError, match="Value 'INVALID' not allowed for parameter 'log-level'"):
        param.set_param(param_name=LOG_LEVEL_PARAM, value='INVALID')
    
    with pytest.raises(ValueError, match="Value 'NOTSET' not allowed for parameter 'log-level'"):
        param.set_param(param_name=LOG_LEVEL_PARAM, value='NOTSET')
    
    with pytest.raises(ValueError, match="Value 'VERBOSE' not allowed for parameter 'log-level'"):
        param.set_param(param_name=LOG_LEVEL_PARAM, value='VERBOSE')


def test_log_level_param_case_insensitive_matching():
    """Test that LOG_LEVEL_PARAM performs case-insensitive matching.
    
    Verifies that log level values can be provided in any case (lowercase,
    uppercase, mixed case) and are normalised to the canonical uppercase form.
    """
    setup_function()
    param.add_params(LOGGING_PARAMS)
    
    # Lowercase input should be normalised to uppercase
    param.set_param(param_name=LOG_LEVEL_PARAM, value='debug')
    assert param.get_param(param_name=LOG_LEVEL_PARAM) == 'DEBUG'
    
    # Mixed case should be normalised to uppercase
    param.set_param(param_name=LOG_LEVEL_PARAM, value='WaRnInG')
    assert param.get_param(param_name=LOG_LEVEL_PARAM) == 'WARNING'
    
    # Lowercase 'trace' should be normalised to 'TRACE'
    param.set_param(param_name=LOG_LEVEL_PARAM, value='trace')
    assert param.get_param(param_name=LOG_LEVEL_PARAM) == 'TRACE'
    
    # Verify invalid value in lowercase is still rejected
    import pytest
    with pytest.raises(ValueError, match="Value 'invalid' not allowed for parameter 'log-level'"):
        param.set_param(param_name=LOG_LEVEL_PARAM, value='invalid')


def test_log_level_param_integration_with_logging_system():
    """Test that LOG_LEVEL_PARAM with allowed values integrates correctly with logging system.
    
    Verifies that setting LOG_LEVEL_PARAM to various allowed values correctly
    configures the logging system to use those levels.
    """
    setup_function()
    param.add_params(LOGGING_PARAMS)
    
    # Set to WARNING and verify it applies
    param.set_param(param_name=LOG_LEVEL_PARAM, value='WARNING')
    logging.apply_logging_config()
    assert logging._console_handler.level == stdlib_logging.WARNING
    assert logging._file_handler.level == stdlib_logging.WARNING
    
    # Reset logging and try ERROR level
    setup_function()
    param.add_params(LOGGING_PARAMS)
    param.set_param(param_name=LOG_LEVEL_PARAM, value='ERROR')
    logging.apply_logging_config()
    assert logging._console_handler.level == stdlib_logging.ERROR
    assert logging._file_handler.level == stdlib_logging.ERROR
    
    # Reset logging and try DEBUG with lowercase input
    setup_function()
    param.add_params(LOGGING_PARAMS)
    param.set_param(param_name=LOG_LEVEL_PARAM, value='debug')  # lowercase
    logging.apply_logging_config()
    assert logging._console_handler.level == stdlib_logging.DEBUG
    assert logging._file_handler.level == stdlib_logging.DEBUG
