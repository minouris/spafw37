"""Logging module for spafw37.

This module provides logging functionality with custom TRACE level,
file and console handlers, and scope-based logging support.
"""
import logging as stdlib_logging
import os
import sys
from datetime import datetime

from spafw37 import config
from spafw37 import config_func
from spafw37.logging_config import (
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
    LOGGING_PARAMS,
)

# Custom TRACE log level (below DEBUG)
TRACE = 5
stdlib_logging.addLevelName(TRACE, "TRACE")

# Standard log levels
DEBUG = stdlib_logging.DEBUG
INFO = stdlib_logging.INFO
WARNING = stdlib_logging.WARNING
ERROR = stdlib_logging.ERROR
CRITICAL = stdlib_logging.CRITICAL

# Default values
_DEFAULT_LOG_DIR = 'logs/'
_DEFAULT_FILE_LEVEL = DEBUG
_DEFAULT_CONSOLE_LEVEL = INFO

# Module state
_logger = None
_file_handler = None
_console_handler = None
_error_handler = None
_current_scope = None
_log_dir = _DEFAULT_LOG_DIR
_suppress_errors = False
_scope_log_levels = {}


def _get_timestamp():
    """Get current timestamp in the format MM-dd hh:mm:ss.sss."""
    now = datetime.now()
    return now.strftime('%m-%d %H:%M:%S.%f')[:-3]


def _get_log_filename():
    """Generate log filename with pattern log-{yyyy-MM-dd-hh.mm.ss}.log."""
    now = datetime.now()
    return f"log-{now.strftime('%Y-%m-%d-%H.%M.%S')}.log"


def _get_log_filepath():
    """Get full path to log file."""
    return os.path.join(_log_dir, _get_log_filename())


class CustomFormatter(stdlib_logging.Formatter):
    """Custom formatter for log messages.
    
    Format: [{MM-dd hh:mm:ss.sss}][{scope}][{log_level}] {message}
    """
    
    def format(self, record):
        """Format log record."""
        timestamp = _get_timestamp()
        scope = getattr(record, 'scope', _current_scope or config_func.get_app_name())
        level = record.levelname
        message = record.getMessage()
        return f"[{timestamp}][{scope}][{level}] {message}"


def _create_file_handler():
    """Create and configure file handler."""
    os.makedirs(_log_dir, exist_ok=True)
    handler = stdlib_logging.FileHandler(_get_log_filepath())
    handler.setLevel(_DEFAULT_FILE_LEVEL)
    handler.setFormatter(CustomFormatter())
    return handler


def _create_console_handler():
    """Create and configure console handler for stdout."""
    handler = stdlib_logging.StreamHandler(sys.stdout)
    handler.setLevel(_DEFAULT_CONSOLE_LEVEL)
    handler.setFormatter(CustomFormatter())
    return handler


def _create_error_handler():
    """Create and configure error handler for stderr."""
    handler = stdlib_logging.StreamHandler(sys.stderr)
    handler.setLevel(stdlib_logging.ERROR)
    handler.setFormatter(CustomFormatter())
    return handler


def _init_logger():
    """Initialize the logger with handlers."""
    global _logger, _file_handler, _console_handler, _error_handler
    
    if _logger is not None:
        return
    
    _logger = stdlib_logging.getLogger('spafw37')
    _logger.setLevel(TRACE)
    _logger.propagate = False
    
    # Create handlers
    _file_handler = _create_file_handler()
    _console_handler = _create_console_handler()
    _error_handler = _create_error_handler()
    
    # Add handlers
    _logger.addHandler(_file_handler)
    _logger.addHandler(_console_handler)
    _logger.addHandler(_error_handler)


def set_current_scope(scope):
    """Set the current scope for logging."""
    global _current_scope
    _current_scope = scope


def set_log_dir(log_dir):
    """Set the log directory."""
    global _log_dir, _file_handler, _logger
    
    _log_dir = log_dir
    
    # Recreate file handler if logger is initialized
    if _logger is not None and _file_handler is not None:
        _logger.removeHandler(_file_handler)
        _file_handler.close()
        _file_handler = _create_file_handler()
        _logger.addHandler(_file_handler)


def set_file_level(level):
    """Set the file handler log level."""
    if _file_handler is not None:
        _file_handler.setLevel(level)


def set_console_level(level):
    """Set the console handler log level."""
    if _console_handler is not None:
        _console_handler.setLevel(level)


def set_silent_mode(silent):
    """Enable or disable silent mode (errors to stderr only)."""
    if silent and _console_handler is not None:
        _console_handler.setLevel(stdlib_logging.CRITICAL + 1)
    elif _console_handler is not None:
        _console_handler.setLevel(_DEFAULT_CONSOLE_LEVEL)


def set_no_logging_mode(no_logging):
    """Enable or disable no-logging mode (errors to stderr only)."""
    if no_logging:
        if _console_handler is not None:
            _console_handler.setLevel(stdlib_logging.CRITICAL + 1)
        if _file_handler is not None:
            _file_handler.setLevel(stdlib_logging.CRITICAL + 1)
    else:
        if _console_handler is not None:
            _console_handler.setLevel(_DEFAULT_CONSOLE_LEVEL)
        if _file_handler is not None:
            _file_handler.setLevel(_DEFAULT_FILE_LEVEL)


def set_suppress_errors(suppress):
    """Enable or disable error suppression."""
    global _suppress_errors
    _suppress_errors = suppress
    if _error_handler is not None:
        if suppress:
            _error_handler.setLevel(stdlib_logging.CRITICAL + 1)
        else:
            _error_handler.setLevel(stdlib_logging.ERROR)


def set_scope_log_level(scope, level):
    """Set log level for a specific scope."""
    _scope_log_levels[scope] = level


def get_scope_log_level(scope):
    """Get log level for a specific scope."""
    return _scope_log_levels.get(scope)


def _should_log_to_console():
    """Check if console logging should be enabled based on config flags."""
    if config.get_config_bool(LOG_NO_LOGGING_PARAM):
        return False
    if config.get_config_bool(LOG_SILENT_PARAM):
        return False
    return True


def _should_log_to_file():
    """Check if file logging should be enabled based on config flags."""
    if config.get_config_bool(LOG_NO_LOGGING_PARAM):
        return False
    if config.get_config_bool(LOG_NO_FILE_LOGGING_PARAM):
        return False
    return True


def log(_level=INFO, _scope=None, _message=''):
    """Log a message."""
    if _logger is None:
        _init_logger()
    
    # Check scope-specific log level
    effective_scope = _scope or _current_scope or config_func.get_app_name()
    scope_level = get_scope_log_level(effective_scope)
    
    if scope_level is not None and _level < scope_level:
        return
    
    # Guardrail: Check config flags to determine if logging should happen
    should_log_console = _should_log_to_console()
    should_log_file = _should_log_to_file()
    
    # If both are disabled, don't log at all
    if not should_log_console and not should_log_file:
        return
    
    # Temporarily remove handlers based on config
    console_removed = False
    file_removed = False
    
    if _console_handler and not should_log_console:
        _logger.removeHandler(_console_handler) # type: ignore
        console_removed = True
    
    if _file_handler and not should_log_file:
        _logger.removeHandler(_file_handler) # type: ignore
        file_removed = True
    
    try:
        # Create log record with scope information
        extra = {'scope': effective_scope}
        _logger.log(_level, _message, extra=extra) # type: ignore
    finally:
        # Restore handlers
        if console_removed and _console_handler:
            _logger.addHandler(_console_handler) # type: ignore
        if file_removed and _file_handler:
            _logger.addHandler(_file_handler) # type: ignore


def log_trace(_scope=None, _message=''):
    """Log a TRACE level message."""
    log(_level=TRACE, _scope=_scope, _message=_message)


def log_debug(_scope=None, _message=''):
    """Log a DEBUG level message."""
    log(_level=DEBUG, _scope=_scope, _message=_message)


def log_info(_scope=None, _message=''):
    """Log an INFO level message."""
    log(_level=INFO, _scope=_scope, _message=_message)


def log_warning(_scope=None, _message=''):
    """Log a WARNING level message."""
    log(_level=WARNING, _scope=_scope, _message=_message)


def log_error(_scope=None, _message=''):
    """Log an ERROR level message."""
    log(_level=ERROR, _scope=_scope, _message=_message)


def _get_level_from_name(level_name):
    """Convert level name to level number."""
    level_map = {
        'TRACE': TRACE,
        'DEBUG': DEBUG,
        'INFO': INFO,
        'WARNING': WARNING,
        'ERROR': ERROR,
        'CRITICAL': CRITICAL,
    }
    return level_map.get(level_name.upper(), INFO)


def apply_logging_config():
    """Apply logging configuration from config values.
    
    Starts with default handler levels and applies only the enabled flags.
    All log level flags are mutually exclusive.
    """
    # Initialize logger
    _init_logger()
    
    # Start with default levels
    file_level = _DEFAULT_FILE_LEVEL  # DEBUG
    console_level = _DEFAULT_CONSOLE_LEVEL  # INFO
    
    # Apply log level flags (mutually exclusive, only one should be set)
    # Priority: explicit log-level > trace > verbose > silent/no-logging
    
    # Check for explicit log level first (overrides everything)
    log_level = config.get_config_value(LOG_LEVEL_PARAM)
    if log_level:
        level = _get_level_from_name(log_level)
        file_level = level
        console_level = level
    
    # Check for trace (both console and file to TRACE)
    elif config.get_config_value(LOG_TRACE_PARAM):
        file_level = TRACE
        console_level = TRACE
    
    # Check for trace-console (only console to TRACE)
    elif config.get_config_value(LOG_TRACE_CONSOLE_PARAM):
        console_level = TRACE
    
    # Check for verbose (console to DEBUG)
    elif config.get_config_value(LOG_VERBOSE_PARAM):
        console_level = DEBUG
    
    # Check for silent mode (console effectively disabled)
    elif config.get_config_value(LOG_SILENT_PARAM):
        console_level = stdlib_logging.CRITICAL + 1  # Above all levels
    
    # Check for no-logging mode (both handlers disabled)
    elif config.get_config_value(LOG_NO_LOGGING_PARAM):
        console_level = stdlib_logging.CRITICAL + 1
        file_level = stdlib_logging.CRITICAL + 1
    
    # Apply the determined levels to handlers
    set_file_level(file_level)
    set_console_level(console_level)
    
    # Check for no-file-logging mode (takes precedence over log-dir)
    if config.get_config_value(LOG_NO_FILE_LOGGING_PARAM):
        set_file_level(stdlib_logging.CRITICAL + 1)  # Disable file logging
    else:
        # Apply log directory only if file logging is not disabled
        log_dir = config.get_config_value(LOG_DIR_PARAM)
        if log_dir:
            set_log_dir(log_dir)
    
    # Apply suppress errors
    if config.get_config_value(LOG_SUPPRESS_ERRORS_PARAM):
        set_suppress_errors(True)
    
    # Apply scope-specific log levels (phase-log-level param for backward compatibility)
    scope_log_levels = config.get_config_value(LOG_PHASE_LOG_LEVEL_PARAM)
    if scope_log_levels:
        # Format: [scope1, level1, scope2, level2, ...]
        for i in range(0, len(scope_log_levels), 2):
            if i + 1 < len(scope_log_levels):
                scope = scope_log_levels[i]
                level_name = scope_log_levels[i + 1]
                level = _get_level_from_name(level_name)
                set_scope_log_level(scope, level)
