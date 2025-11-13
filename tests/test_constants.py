"""Tests for constants modules.

These tests primarily exist to ensure constants are importable and achieve
test coverage for constants modules.
"""


def test_logging_constants_importable():
    """Test that all logging constants can be imported.
    
    Importing the constants validates that they are defined correctly and also
    provides test coverage for the constants/logging.py module which is otherwise
    at 0% coverage.
    """
    from spafw37.constants.logging import (
        LOG_VERBOSE_PARAM,
        LOG_TRACE_PARAM,
        LOG_TRACE_CONSOLE_PARAM,
        LOG_SILENT_PARAM,
        LOG_NO_LOGGING_PARAM,
        LOG_SUPPRESS_ERRORS_PARAM,
        LOG_DIR_PARAM,
        LOG_LEVEL_PARAM,
        LOG_PHASE_LOG_LEVEL_PARAM,
        LOGGING_HELP_GROUP,
    )
    
    # Verify constants are strings
    assert isinstance(LOG_VERBOSE_PARAM, str)
    assert isinstance(LOG_TRACE_PARAM, str)
    assert isinstance(LOG_TRACE_CONSOLE_PARAM, str)
    assert isinstance(LOG_SILENT_PARAM, str)
    assert isinstance(LOG_NO_LOGGING_PARAM, str)
    assert isinstance(LOG_SUPPRESS_ERRORS_PARAM, str)
    assert isinstance(LOG_DIR_PARAM, str)
    assert isinstance(LOG_LEVEL_PARAM, str)
    assert isinstance(LOG_PHASE_LOG_LEVEL_PARAM, str)
    assert isinstance(LOGGING_HELP_GROUP, str)
    
    # Verify expected values
    assert LOG_VERBOSE_PARAM == 'log-verbose'
    assert LOGGING_HELP_GROUP == 'Logging Options'
