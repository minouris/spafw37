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


def test_param_prompt_constants_exist():
    """Test that all PARAM_PROMPT* and PARAM_SENSITIVE constants required for prompt configuration are defined.
    
    This test verifies that PARAM_PROMPT, PARAM_PROMPT_HANDLER, PARAM_PROMPT_TIMING,
    PARAM_PROMPT_REPEAT, and PARAM_SENSITIVE constants exist as strings with unique values.
    This behaviour is expected because these constants form the core vocabulary for
    configuring interactive prompts on parameters and must be available for param definitions."""
    from spafw37.constants import param
    
    assert hasattr(param, 'PARAM_PROMPT'), "PARAM_PROMPT constant missing"
    assert hasattr(param, 'PARAM_PROMPT_HANDLER'), "PARAM_PROMPT_HANDLER constant missing"
    assert hasattr(param, 'PARAM_PROMPT_TIMING'), "PARAM_PROMPT_TIMING constant missing"
    assert hasattr(param, 'PARAM_PROMPT_REPEAT'), "PARAM_PROMPT_REPEAT constant missing"
    assert hasattr(param, 'PARAM_SENSITIVE'), "PARAM_SENSITIVE constant missing"
    
    assert isinstance(param.PARAM_PROMPT, str), "PARAM_PROMPT must be string"
    assert isinstance(param.PARAM_PROMPT_HANDLER, str), "PARAM_PROMPT_HANDLER must be string"
    assert isinstance(param.PARAM_PROMPT_TIMING, str), "PARAM_PROMPT_TIMING must be string"
    assert isinstance(param.PARAM_PROMPT_REPEAT, str), "PARAM_PROMPT_REPEAT must be string"
    assert isinstance(param.PARAM_SENSITIVE, str), "PARAM_SENSITIVE must be string"
    
    constant_values = [
        param.PARAM_PROMPT,
        param.PARAM_PROMPT_HANDLER,
        param.PARAM_PROMPT_TIMING,
        param.PARAM_PROMPT_REPEAT,
        param.PARAM_SENSITIVE
    ]
    assert len(constant_values) == len(set(constant_values)), "Constant values must be unique"


def test_prompt_timing_constants_defined():
    """Test that PROMPT_ON_START and PROMPT_ON_COMMAND timing constants are defined correctly.
    
    This test verifies both timing control constants exist as strings for use in
    PARAM_PROMPT_TIMING property to control when prompts appear (at start or before commands).
    This behaviour is expected because these two constants represent the complete set of
    timing options for prompt execution in the framework."""
    from spafw37.constants.param import PROMPT_ON_START, PROMPT_ON_COMMAND
    
    assert isinstance(PROMPT_ON_START, str), "PROMPT_ON_START must be string"
    assert isinstance(PROMPT_ON_COMMAND, str), "PROMPT_ON_COMMAND must be string"
    assert PROMPT_ON_START != PROMPT_ON_COMMAND, "Timing constants must be unique"


def test_prompt_repeat_constants_defined():
    """Test that all three PROMPT_REPEAT_* behaviour constants are defined correctly.
    
    This test verifies PROMPT_REPEAT_NEVER, PROMPT_REPEAT_IF_BLANK, and PROMPT_REPEAT_ALWAYS
    constants exist as strings for controlling repeat behaviour in cycles and multi-command scenarios.
    This behaviour is expected because these three constants represent the complete set of
    valid repeat behaviours for prompts."""
    from spafw37.constants.param import (
        PROMPT_REPEAT_NEVER,
        PROMPT_REPEAT_IF_BLANK,
        PROMPT_REPEAT_ALWAYS
    )
    
    assert isinstance(PROMPT_REPEAT_NEVER, str), "PROMPT_REPEAT_NEVER must be string"
    assert isinstance(PROMPT_REPEAT_IF_BLANK, str), "PROMPT_REPEAT_IF_BLANK must be string"
    assert isinstance(PROMPT_REPEAT_ALWAYS, str), "PROMPT_REPEAT_ALWAYS must be string"
    
    repeat_values = [PROMPT_REPEAT_NEVER, PROMPT_REPEAT_IF_BLANK, PROMPT_REPEAT_ALWAYS]
    assert len(repeat_values) == len(set(repeat_values)), "Repeat constants must be unique"


def test_prompt_on_commands_constant():
    """Test that PROMPT_ON_COMMANDS constant is defined correctly.
    
    This test verifies the constant exists as a string for use in param definitions
    to specify which commands should trigger prompts when PARAM_PROMPT_TIMING is PROMPT_ON_COMMAND.
    This behaviour is expected because params need to store lists of command names that
    should trigger prompts, enabling per-command prompt control."""
    from spafw37.constants.param import PROMPT_ON_COMMANDS
    
    assert isinstance(PROMPT_ON_COMMANDS, str), "PROMPT_ON_COMMANDS must be string"
    assert PROMPT_ON_COMMANDS == 'prompt-on-commands'


def test_param_prompt_retries_constant():
    """Test that PARAM_PROMPT_RETRIES constant is defined correctly.
    
    This test verifies the constant exists as a string for use in param definitions.
    This behaviour is expected because params need to override global retry configuration
    on a per-param basis for sensitive or critical parameters."""
    from spafw37.constants.param import PARAM_PROMPT_RETRIES
    
    assert PARAM_PROMPT_RETRIES == 'prompt-retries'


def test_command_prompt_params_constant_exists():
    """Test that COMMAND_PROMPT_PARAMS constant is defined in the command constants module.
    
    This test verifies the constant exists as a string key suitable for use as a dictionary
    property on command definitions.
    This behaviour is expected because commands need to store lists of parameter names that
    should prompt before execution, enabling O(1) lookup during command execution."""
    from spafw37.constants import command
    
    assert hasattr(command, 'COMMAND_PROMPT_PARAMS'), "COMMAND_PROMPT_PARAMS constant missing"
    assert isinstance(command.COMMAND_PROMPT_PARAMS, str), "COMMAND_PROMPT_PARAMS must be string"
