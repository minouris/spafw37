"""Logging module for spafw37.

This module provides logging functionality with custom TRACE level,
file and console handlers, and phase-based logging support.
"""
from __future__ import annotations

import logging as stdlib_logging
import os
import sys
from datetime import datetime
from typing import Optional

from .config_consts import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_BIND_TO,
    PARAM_TYPE,
    PARAM_ALIASES,
    PARAM_PERSISTENCE,
    PARAM_PERSISTENCE_ALWAYS,
    PARAM_PERSISTENCE_NEVER,
    PARAM_TYPE_TOGGLE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_LIST,
    PARAM_SWITCH_LIST,
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
_logger: Optional[stdlib_logging.Logger] = None
_file_handler: Optional[stdlib_logging.FileHandler] = None
_console_handler: Optional[stdlib_logging.StreamHandler] = None
_error_handler: Optional[stdlib_logging.StreamHandler] = None
_app_name: str = 'spafw37'
_current_phase: Optional[str] = None
_log_dir: str = _DEFAULT_LOG_DIR
_suppress_errors: bool = False
_phase_log_levels: dict = {}


def _get_timestamp() -> str:
    """Get current timestamp in the format MM-dd hh:mm:ss.sss.
    
    Returns:
        Formatted timestamp string.
    """
    now = datetime.now()
    return now.strftime('%m-%d %H:%M:%S.%f')[:-3]


def _get_log_filename() -> str:
    """Generate log filename with pattern log-{yyyy-MM-dd-hh.mm.ss}.log.
    
    Returns:
        Log filename with timestamp.
    """
    now = datetime.now()
    return f"log-{now.strftime('%Y-%m-%d-%H.%M.%S')}.log"


def _get_log_filepath() -> str:
    """Get full path to log file.
    
    Returns:
        Full path to log file.
    """
    return os.path.join(_log_dir, _get_log_filename())


class CustomFormatter(stdlib_logging.Formatter):
    """Custom formatter for log messages.
    
    Format: [{MM-dd hh:mm:ss.sss}][{phase}][{log_level}] {message}
    """
    
    def format(self, record: stdlib_logging.LogRecord) -> str:
        """Format log record.
        
        Args:
            record: Log record to format.
            
        Returns:
            Formatted log message.
        """
        timestamp = _get_timestamp()
        phase = getattr(record, 'phase', _current_phase or _app_name)
        level = record.levelname
        message = record.getMessage()
        return f"[{timestamp}][{phase}][{level}] {message}"


def _create_file_handler() -> stdlib_logging.FileHandler:
    """Create and configure file handler.
    
    Returns:
        Configured file handler.
    """
    os.makedirs(_log_dir, exist_ok=True)
    handler = stdlib_logging.FileHandler(_get_log_filepath())
    handler.setLevel(_DEFAULT_FILE_LEVEL)
    handler.setFormatter(CustomFormatter())
    return handler


def _create_console_handler() -> stdlib_logging.StreamHandler:
    """Create and configure console handler for stdout.
    
    Returns:
        Configured console handler.
    """
    handler = stdlib_logging.StreamHandler(sys.stdout)
    handler.setLevel(_DEFAULT_CONSOLE_LEVEL)
    handler.setFormatter(CustomFormatter())
    return handler


def _create_error_handler() -> stdlib_logging.StreamHandler:
    """Create and configure error handler for stderr.
    
    Returns:
        Configured error handler.
    """
    handler = stdlib_logging.StreamHandler(sys.stderr)
    handler.setLevel(ERROR)
    handler.setFormatter(CustomFormatter())
    return handler


def _init_logger() -> None:
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


def set_app_name(name: str) -> None:
    """Set the application name for out-of-phase logging.
    
    Args:
        name: Application name.
    """
    global _app_name
    _app_name = name


def set_current_phase(phase: Optional[str]) -> None:
    """Set the current phase for logging.
    
    Args:
        phase: Phase name or None to use app_name.
    """
    global _current_phase
    _current_phase = phase


def set_log_dir(log_dir: str) -> None:
    """Set the log directory.
    
    Args:
        log_dir: Path to log directory.
    """
    global _log_dir, _file_handler, _logger
    
    _log_dir = log_dir
    
    # Recreate file handler if logger is initialized
    if _logger is not None and _file_handler is not None:
        _logger.removeHandler(_file_handler)
        _file_handler.close()
        _file_handler = _create_file_handler()
        _logger.addHandler(_file_handler)


def set_file_level(level: int) -> None:
    """Set the file handler log level.
    
    Args:
        level: Log level (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    if _file_handler is not None:
        _file_handler.setLevel(level)


def set_console_level(level: int) -> None:
    """Set the console handler log level.
    
    Args:
        level: Log level (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    if _console_handler is not None:
        _console_handler.setLevel(level)


def set_silent_mode(silent: bool) -> None:
    """Enable or disable silent mode (errors to stderr only).
    
    Args:
        silent: True to enable silent mode.
    """
    if silent and _console_handler is not None:
        _console_handler.setLevel(stdlib_logging.CRITICAL + 1)
    elif _console_handler is not None:
        _console_handler.setLevel(_DEFAULT_CONSOLE_LEVEL)


def set_no_logging_mode(no_logging: bool) -> None:
    """Enable or disable no-logging mode (errors to stderr only).
    
    Args:
        no_logging: True to disable all logging except errors to stderr.
    """
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


def set_suppress_errors(suppress: bool) -> None:
    """Enable or disable error suppression.
    
    Args:
        suppress: True to suppress error logging.
    """
    global _suppress_errors
    _suppress_errors = suppress
    if _error_handler is not None:
        if suppress:
            _error_handler.setLevel(stdlib_logging.CRITICAL + 1)
        else:
            _error_handler.setLevel(ERROR)


def set_phase_log_level(phase: str, level: int) -> None:
    """Set log level for a specific phase.
    
    Args:
        phase: Phase name.
        level: Log level.
    """
    _phase_log_levels[phase] = level


def get_phase_log_level(phase: str) -> Optional[int]:
    """Get log level for a specific phase.
    
    Args:
        phase: Phase name.
        
    Returns:
        Log level for the phase or None if not set.
    """
    return _phase_log_levels.get(phase)


def log(_level: int = INFO, _phase: Optional[str] = None, _message: str = '') -> None:
    """Log a message.
    
    Args:
        _level: Log level (default: INFO).
        _phase: Phase name (default: current phase or app_name).
        _message: Message to log.
    """
    if _logger is None:
        _init_logger()
    
    # Check phase-specific log level
    effective_phase = _phase or _current_phase or _app_name
    phase_level = get_phase_log_level(effective_phase)
    
    if phase_level is not None and _level < phase_level:
        return
    
    # Create log record with phase information
    extra = {'phase': effective_phase}
    _logger.log(_level, _message, extra=extra)


def log_trace(_phase: Optional[str] = None, _message: str = '') -> None:
    """Log a TRACE level message.
    
    Args:
        _phase: Phase name (default: current phase or app_name).
        _message: Message to log.
    """
    log(_level=TRACE, _phase=_phase, _message=_message)


def log_debug(_phase: Optional[str] = None, _message: str = '') -> None:
    """Log a DEBUG level message.
    
    Args:
        _phase: Phase name (default: current phase or app_name).
        _message: Message to log.
    """
    log(_level=DEBUG, _phase=_phase, _message=_message)


def log_info(_phase: Optional[str] = None, _message: str = '') -> None:
    """Log an INFO level message.
    
    Args:
        _phase: Phase name (default: current phase or app_name).
        _message: Message to log.
    """
    log(_level=INFO, _phase=_phase, _message=_message)


def log_warning(_phase: Optional[str] = None, _message: str = '') -> None:
    """Log a WARNING level message.
    
    Args:
        _phase: Phase name (default: current phase or app_name).
        _message: Message to log.
    """
    log(_level=WARNING, _phase=_phase, _message=_message)


def log_error(_phase: Optional[str] = None, _message: str = '') -> None:
    """Log an ERROR level message.
    
    Args:
        _phase: Phase name (default: current phase or app_name).
        _message: Message to log.
    """
    log(_level=ERROR, _phase=_phase, _message=_message)


# Define logging parameters
LOGGING_PARAMS = [
    {
        PARAM_NAME: LOG_VERBOSE_PARAM,
        PARAM_DESCRIPTION: 'Enable verbose logging (console to DEBUG)',
        PARAM_BIND_TO: LOG_VERBOSE_PARAM,
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_ALIASES: ['--verbose', '-v'],
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER,
    },
    {
        PARAM_NAME: LOG_TRACE_PARAM,
        PARAM_DESCRIPTION: 'Set file log level to TRACE',
        PARAM_BIND_TO: LOG_TRACE_PARAM,
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_ALIASES: ['--trace'],
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER,
    },
    {
        PARAM_NAME: LOG_TRACE_CONSOLE_PARAM,
        PARAM_DESCRIPTION: 'Set console log level to TRACE',
        PARAM_BIND_TO: LOG_TRACE_CONSOLE_PARAM,
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_ALIASES: ['--trace-console'],
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER,
    },
    {
        PARAM_NAME: LOG_SILENT_PARAM,
        PARAM_DESCRIPTION: 'Suppress all console logging (errors to stderr only)',
        PARAM_BIND_TO: LOG_SILENT_PARAM,
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_ALIASES: ['--silent'],
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER,
        PARAM_SWITCH_LIST: [LOG_VERBOSE_PARAM, LOG_TRACE_CONSOLE_PARAM, LOG_NO_LOGGING_PARAM],
    },
    {
        PARAM_NAME: LOG_NO_LOGGING_PARAM,
        PARAM_DESCRIPTION: 'Suppress all logging to console and file (errors to stderr only)',
        PARAM_BIND_TO: LOG_NO_LOGGING_PARAM,
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_ALIASES: ['--no-logging'],
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER,
        PARAM_SWITCH_LIST: [LOG_VERBOSE_PARAM, LOG_TRACE_PARAM, LOG_TRACE_CONSOLE_PARAM, LOG_SILENT_PARAM],
    },
    {
        PARAM_NAME: LOG_SUPPRESS_ERRORS_PARAM,
        PARAM_DESCRIPTION: 'Disable error logging',
        PARAM_BIND_TO: LOG_SUPPRESS_ERRORS_PARAM,
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_ALIASES: ['--suppress-errors'],
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER,
    },
    {
        PARAM_NAME: LOG_DIR_PARAM,
        PARAM_DESCRIPTION: 'Set directory for log files',
        PARAM_BIND_TO: LOG_DIR_PARAM,
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--log-dir'],
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS,
    },
    {
        PARAM_NAME: LOG_LEVEL_PARAM,
        PARAM_DESCRIPTION: 'Set overall log level',
        PARAM_BIND_TO: LOG_LEVEL_PARAM,
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--log-level'],
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER,
    },
    {
        PARAM_NAME: LOG_PHASE_LOG_LEVEL_PARAM,
        PARAM_DESCRIPTION: 'Set log level for a specific phase',
        PARAM_BIND_TO: LOG_PHASE_LOG_LEVEL_PARAM,
        PARAM_TYPE: PARAM_TYPE_LIST,
        PARAM_ALIASES: ['--phase-log-level'],
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER,
    },
]


def _get_level_from_name(level_name: str) -> int:
    """Convert level name to level number.
    
    Args:
        level_name: Level name (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL).
        
    Returns:
        Level number.
    """
    level_map = {
        'TRACE': TRACE,
        'DEBUG': DEBUG,
        'INFO': INFO,
        'WARNING': WARNING,
        'ERROR': ERROR,
        'CRITICAL': CRITICAL,
    }
    return level_map.get(level_name.upper(), INFO)


def apply_logging_config() -> None:
    """Apply logging configuration from config values."""
    from . import config
    
    # Initialize logger
    _init_logger()
    
    # Apply verbose flag
    if config.get_config_value(LOG_VERBOSE_PARAM):
        set_console_level(DEBUG)
    
    # Apply trace flags
    if config.get_config_value(LOG_TRACE_PARAM):
        set_file_level(TRACE)
    
    if config.get_config_value(LOG_TRACE_CONSOLE_PARAM):
        set_console_level(TRACE)
    
    # Apply silent mode
    if config.get_config_value(LOG_SILENT_PARAM):
        set_silent_mode(True)
    
    # Apply no-logging mode
    if config.get_config_value(LOG_NO_LOGGING_PARAM):
        set_no_logging_mode(True)
    
    # Apply suppress errors
    if config.get_config_value(LOG_SUPPRESS_ERRORS_PARAM):
        set_suppress_errors(True)
    
    # Apply log directory
    log_dir = config.get_config_value(LOG_DIR_PARAM)
    if log_dir:
        set_log_dir(log_dir)
    
    # Apply log level
    log_level = config.get_config_value(LOG_LEVEL_PARAM)
    if log_level:
        level = _get_level_from_name(log_level)
        set_file_level(level)
        set_console_level(level)
    
    # Apply phase-specific log levels
    phase_log_levels = config.get_config_value(LOG_PHASE_LOG_LEVEL_PARAM)
    if phase_log_levels:
        # Format: [phase1, level1, phase2, level2, ...]
        for i in range(0, len(phase_log_levels), 2):
            if i + 1 < len(phase_log_levels):
                phase = phase_log_levels[i]
                level_name = phase_log_levels[i + 1]
                level = _get_level_from_name(level_name)
                set_phase_log_level(phase, level)
