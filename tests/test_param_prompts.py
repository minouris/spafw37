"""Tests for param module prompt support."""

import pytest

from spafw37 import param, logging
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_PROMPT,
    PARAM_PROMPT_HANDLER,
    PARAM_PROMPT_TIMING,
    PARAM_PROMPT_REPEAT,
    PARAM_PROMPT_RETRIES,
    PARAM_REQUIRED,
    PARAM_SENSITIVE,
    PARAM_ALLOWED_VALUES,
    PROMPT_ON_START,
    PROMPT_ON_COMMAND,
    PROMPT_ON_COMMANDS,
    PROMPT_REPEAT_ALWAYS,
    PROMPT_REPEAT_IF_BLANK,
    PROMPT_REPEAT_NEVER
)


def test_module_level_prompt_state_initialised():
    """Test that module-level prompt state variables are initialised correctly.
    
    This test verifies _global_prompt_handler starts as None (no custom handler),
    _prompted_params starts as empty set (no prompts executed yet), and the
    _PROMPT_AUTO_POPULATE flag constant is defined for marking params during registration.
    This behaviour is expected because clean initial state ensures no leftover configuration
    from previous test runs or imports affects prompt behaviour."""
    assert param._global_prompt_handler is None, "Global handler should start as None"
    assert isinstance(param._prompted_params, set), "Prompted params must be a set"
    assert len(param._prompted_params) == 0, "Prompted params should start empty"
    assert hasattr(param, '_PROMPT_AUTO_POPULATE'), "Auto-populate flag constant missing"
    assert isinstance(param._PROMPT_AUTO_POPULATE, str), "Flag must be string key"


def test_validate_prompt_timing_with_on_start():
    """Test that PROMPT_ON_START constant passes timing validation successfully.
    
    This test verifies _validate_prompt_timing() accepts the PROMPT_ON_START constant
    without raising exceptions, as this is one of the two valid timing modes.
    This behaviour is expected because PROMPT_ON_START indicates prompts should run
    immediately after CLI parsing, before command execution, which is a core timing option."""
    try:
        param._validate_prompt_timing(PROMPT_ON_START)
        validation_passed = True
    except ValueError:
        validation_passed = False
    assert validation_passed, "PROMPT_ON_START should pass validation"


def test_validate_prompt_timing_with_on_command():
    """Test that PROMPT_ON_COMMAND constant passes timing validation successfully.
    
    This test verifies _validate_prompt_timing() accepts the PROMPT_ON_COMMAND constant
    without raising exceptions, as this indicates prompts should run before specific commands.
    This behaviour is expected because PROMPT_ON_COMMAND tells the framework to check the
    PROMPT_ON_COMMANDS property for the list of commands to prompt before."""
    try:
        param._validate_prompt_timing(PROMPT_ON_COMMAND)
        validation_passed = True
    except ValueError:
        validation_passed = False
    assert validation_passed, "PROMPT_ON_COMMAND should pass validation"


def test_validate_prompt_timing_rejects_invalid_value():
    """Test that invalid timing values raise ValueError during validation.
    
    This test verifies _validate_prompt_timing() rejects values that are neither
    PROMPT_ON_START constant nor lists, such as arbitrary strings like "invalid".
    This behaviour is expected because accepting invalid timing values would cause
    subtle runtime errors when the framework tries to determine when to prompt."""
    with pytest.raises(ValueError, match="PARAM_PROMPT_TIMING must be"):
        param._validate_prompt_timing("invalid_constant")


def test_validate_prompt_repeat_with_valid_constants():
    """Test that all PROMPT_REPEAT_* constants pass repeat validation successfully.
    
    This test verifies _validate_prompt_repeat() accepts PROMPT_REPEAT_ALWAYS,
    PROMPT_REPEAT_IF_BLANK, and PROMPT_REPEAT_NEVER without raising exceptions.
    This behaviour is expected because these three constants represent the complete
    set of valid repeat behaviours for prompts in cycle and multi-command scenarios."""
    valid_constants = [PROMPT_REPEAT_ALWAYS, PROMPT_REPEAT_IF_BLANK, PROMPT_REPEAT_NEVER]
    for repeat_constant in valid_constants:
        try:
            param._validate_prompt_repeat(repeat_constant)
            validation_passed = True
        except ValueError:
            validation_passed = False
        assert validation_passed, "Constant {0} should pass validation".format(repeat_constant)


def test_validate_prompt_repeat_rejects_invalid_value():
    """Test that invalid repeat values raise ValueError during validation.
    
    This test verifies _validate_prompt_repeat() rejects arbitrary values that are
    not one of the three valid PROMPT_REPEAT_* constants.
    This behaviour is expected because accepting invalid repeat values would cause
    undefined behaviour in cycle logic where the framework checks repeat mode."""
    with pytest.raises(ValueError, match="PARAM_PROMPT_REPEAT must be one of"):
        param._validate_prompt_repeat("invalid_repeat")


def test_param_with_valid_prompt_properties_registers():
    """Test that params with valid prompt properties register successfully without errors.
    
    This test verifies add_param() accepts parameters with PARAM_PROMPT and valid
    PARAM_PROMPT_TIMING (PROMPT_ON_START), storing all properties correctly.
    This behaviour is expected because properly configured prompt params are valid
    and should integrate seamlessly with the registration system."""
    param._params = {}
    test_param = {
        PARAM_NAME: 'test_prompt_param',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: 'Enter value:',
        PARAM_PROMPT_TIMING: PROMPT_ON_START
    }
    param.add_param(test_param)
    registered_param = param.get_param_by_name('test_prompt_param')
    assert registered_param is not None, "Param should be registered"
    assert registered_param[PARAM_PROMPT] == 'Enter value:', "PARAM_PROMPT not preserved"
    assert registered_param[PARAM_PROMPT_TIMING] == PROMPT_ON_START, "Timing not preserved"


def test_param_with_prompt_but_no_timing_gets_auto_populate_flag():
    """Test that params with PARAM_PROMPT but no explicit timing are marked for auto-population.
    
    This test verifies that when PARAM_PROMPT_TIMING is not specified, the internal
    _PROMPT_AUTO_POPULATE flag is set on the param definition during registration.
    This behaviour is expected because params without explicit timing need to be
    processed later when commands are registered to establish timing from COMMAND_REQUIRED_PARAMS."""
    param._params = {}
    test_param = {
        PARAM_NAME: 'auto_populate_param',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: 'Enter value:'
    }
    param.add_param(test_param)
    registered_param = param.get_param_by_name('auto_populate_param')
    assert param._PROMPT_AUTO_POPULATE in registered_param, "Auto-populate flag should be set"
    assert registered_param[param._PROMPT_AUTO_POPULATE] is True, "Flag should be True"


def test_prompt_param_with_empty_string_raises_error():
    """Test that params with empty or whitespace-only PARAM_PROMPT are rejected.
    
    This test verifies add_param() raises ValueError when PARAM_PROMPT is an empty string
    or contains only whitespace, as prompts need meaningful text to display to users.
    This behaviour is expected because empty prompts would confuse users with no
    indication of what input is expected."""
    param._params = {}
    empty_param = {
        PARAM_NAME: 'empty_prompt',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: ''
    }
    with pytest.raises(ValueError, match="PARAM_PROMPT must be a non-empty string"):
        param.add_param(empty_param)
    param._params = {}
    whitespace_param = {
        PARAM_NAME: 'whitespace_prompt',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: '   '
    }
    with pytest.raises(ValueError, match="PARAM_PROMPT must be a non-empty string"):
        param.add_param(whitespace_param)


def test_prompt_param_without_type_raises_error():
    """Test that prompt-enabled params without PARAM_TYPE are rejected during registration.
    
    This test verifies add_param() raises ValueError when a parameter has PARAM_PROMPT
    but doesn't specify PARAM_TYPE, which is needed to determine input handling.
    This behaviour is expected because the framework needs PARAM_TYPE to know how to
    parse and validate user input (text, number, toggle, etc.)."""
    param._params = {}
    no_type_param = {
        PARAM_NAME: 'no_type_prompt',
        PARAM_PROMPT: 'Enter value:'
    }
    with pytest.raises(ValueError, match="PARAM_TYPE is required for prompt-enabled param"):
        param.add_param(no_type_param)


def test_set_prompt_handler_stores_custom_handler():
    """Test that set_prompt_handler() correctly stores custom handler reference globally.
    
    This test verifies set_prompt_handler() updates the module-level _global_prompt_handler
    variable with the provided custom handler function reference.
    This behaviour is expected because the global handler provides extensibility,
    allowing applications to replace the default input() handler with GUI prompts,
    API-based input, or other custom input mechanisms."""
    def custom_handler(param_def):
        return "custom_value"
    param.set_prompt_handler(custom_handler)
    assert param._global_prompt_handler is custom_handler, "Custom handler not stored"
    param.set_prompt_handler(None)
    assert param._global_prompt_handler is None, "Handler should be cleared"


def test_set_allowed_values_updates_param_definition():
    """Test that set_allowed_values() dynamically updates parameter allowed values list.
    
    This test verifies set_allowed_values() modifies the PARAM_ALLOWED_VALUES property
    of a registered parameter, enabling runtime population of multiple choice options.
    This behaviour is expected because commands need to populate choice lists dynamically
    (e.g., from database queries, API calls, or file system scans) without creating
    bidirectional dependencies between params and commands."""
    param._params = {}
    test_param = {
        PARAM_NAME: 'dynamic_choice',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: 'Select option'
    }
    param.add_param(test_param)
    new_values = ['option1', 'option2', 'option3']
    param.set_allowed_values('dynamic_choice', new_values)
    registered_param = param.get_param_by_name('dynamic_choice')
    assert PARAM_ALLOWED_VALUES in registered_param, "PARAM_ALLOWED_VALUES should be set"
    assert registered_param[PARAM_ALLOWED_VALUES] == new_values, "Values not updated correctly"


def test_set_allowed_values_raises_error_for_unregistered_param():
    """Test that set_allowed_values() raises KeyError for unregistered parameter names.
    
    This test verifies set_allowed_values() fails clearly when attempting to update
    a parameter that hasn't been registered, preventing silent failures.
    This behaviour is expected because typos or incorrect param names should be
    caught immediately rather than silently ignored."""
    param._params = {}
    with pytest.raises(KeyError, match="Parameter 'nonexistent' is not registered"):
        param.set_allowed_values('nonexistent', ['a', 'b'])


def test_set_allowed_values_raises_error_for_non_list_values():
    """Test that set_allowed_values() raises ValueError when values is not a list.
    
    This test verifies type checking for the values parameter, ensuring only list
    types are accepted for allowed values (not strings, tuples, or other iterables).
    This behaviour is expected because PARAM_ALLOWED_VALUES is defined as a list
    property and type consistency prevents subtle bugs."""
    param._params = {}
    test_param = {
        PARAM_NAME: 'choice_param',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: 'Select'
    }
    param.add_param(test_param)
    with pytest.raises(ValueError, match="Allowed values must be a list"):
        param.set_allowed_values('choice_param', 'not_a_list')


def test_default_handler_without_overrides():
    """Test that _get_prompt_handler() returns default handler when no overrides configured.
    
    This regression test verifies that when neither param-level nor global handlers are set,
    the framework returns the built-in input_prompt.prompt_for_value function.
    This behaviour is expected because the framework must provide default terminal-based
    prompting without requiring configuration."""
    param._global_prompt_handler = None
    param_def = {PARAM_NAME: 'test_param', PARAM_PROMPT: 'Enter value:'}
    handler = param._get_prompt_handler(param_def)
    from spafw37 import input_prompt
    assert handler == input_prompt.prompt_for_value


def test_param_level_handler_override():
    """Test that _get_prompt_handler() returns param-level handler when configured.
    
    This test verifies that when a param has PARAM_PROMPT_HANDLER property set,
    that custom handler is returned instead of the default.
    This behaviour is expected because params may need specialised input methods
    (e.g., file picker dialogue, password masking)."""
    param._global_prompt_handler = None
    def custom_handler(param_def):
        return 'custom_value'
    param_def = {
        PARAM_NAME: 'test_param',
        PARAM_PROMPT: 'Enter value:',
        PARAM_PROMPT_HANDLER: custom_handler
    }
    handler = param._get_prompt_handler(param_def)
    assert handler == custom_handler


def test_global_handler_override():
    """Test that _get_prompt_handler() returns global handler when configured.
    
    This test verifies that when set_prompt_handler() has been called with a custom handler,
    that global handler is returned for params without param-level handlers.
    This behaviour is expected because global handlers provide application-wide customisation."""
    def global_handler(param_def):
        return 'global_value'
    param.set_prompt_handler(global_handler)
    param_def = {PARAM_NAME: 'test_param', PARAM_PROMPT: 'Enter value:'}
    handler = param._get_prompt_handler(param_def)
    assert handler == global_handler
    param.set_prompt_handler(None)


def test_param_level_handler_overrides_global():
    """Test that param-level handler takes precedence over global handler.
    
    This test verifies the handler resolution precedence: param-level → global → default.
    This behaviour is expected because param-specific handlers must override global settings
    for fine-grained control."""
    def global_handler(param_def):
        return 'global_value'
    def param_handler(param_def):
        return 'param_value'
    param.set_prompt_handler(global_handler)
    param_def = {
        PARAM_NAME: 'test_param',
        PARAM_PROMPT: 'Enter value:',
        PARAM_PROMPT_HANDLER: param_handler
    }
    handler = param._get_prompt_handler(param_def)
    assert handler == param_handler
    param.set_prompt_handler(None)


def test_param_value_is_set_returns_true_for_valid_value():
    """Test that _param_value_is_set() returns True when param has a non-empty value.
    
    This test verifies the helper correctly identifies params with values (CLI override detection).
    This behaviour is expected because params set via CLI should skip prompting."""
    from spafw37 import config
    param._params = {}
    config._config = {}
    param.add_param({PARAM_NAME: 'test_param', PARAM_TYPE: PARAM_TYPE_TEXT})
    param.set_param(param_name='test_param', value='some_value')
    assert param._param_value_is_set('test_param') is True


def test_param_value_is_set_returns_false_for_none():
    """Test that _param_value_is_set() returns False when param value is None.
    
    This test verifies the helper correctly identifies params without values.
    This behaviour is expected because None indicates no value was provided."""
    from spafw37 import config
    param._params = {}
    config._config = {}
    param.add_param({PARAM_NAME: 'test_param', PARAM_TYPE: PARAM_TYPE_TEXT})
    param.set_param(param_name='test_param', value=None)
    assert param._param_value_is_set('test_param') is False


def test_param_value_is_set_returns_false_for_empty_string():
    """Test that _param_value_is_set() returns False when param value is empty string.
    
    This test verifies the helper treats empty strings as unset values.
    This behaviour is expected because empty string indicates no meaningful value."""
    from spafw37 import config
    param._params = {}
    config._config = {}
    param.add_param({PARAM_NAME: 'test_param', PARAM_TYPE: PARAM_TYPE_TEXT})
    param.set_param(param_name='test_param', value='')
    assert param._param_value_is_set('test_param') is False


def test_timing_matches_context_start_with_none():
    """Test that _timing_matches_context() returns True for PROMPT_ON_START with None context.
    
    This test verifies PROMPT_ON_START timing matches the start-of-execution context.
    This behaviour ensures start-timing prompts appear at application startup."""
    param_def = {PARAM_PROMPT_TIMING: PROMPT_ON_START}
    assert param._timing_matches_context(param_def, None) is True


def test_timing_matches_context_start_with_command():
    """Test that _timing_matches_context() returns False for PROMPT_ON_START with command context.
    
    This test verifies PROMPT_ON_START timing does not match command execution context.
    This behaviour ensures start-timing prompts don't appear during command execution."""
    param_def = {PARAM_PROMPT_TIMING: PROMPT_ON_START}
    assert param._timing_matches_context(param_def, 'some_cmd') is False


def test_timing_matches_context_command_with_none():
    """Test that _timing_matches_context() returns False for PROMPT_ON_COMMAND with None context.
    
    This test verifies PROMPT_ON_COMMAND timing does not match start-of-execution context.
    This behaviour ensures command-timing prompts don't appear at application startup."""
    param_def = {
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['cmd1', 'cmd2']
    }
    assert param._timing_matches_context(param_def, None) is False


def test_timing_matches_context_command_with_matching():
    """Test that _timing_matches_context() returns True for PROMPT_ON_COMMAND with matching command.
    
    This test verifies PROMPT_ON_COMMAND timing matches when command is in PROMPT_ON_COMMANDS list.
    This behaviour ensures command-timing prompts appear before configured commands."""
    param_def = {
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['cmd1', 'cmd2']
    }
    assert param._timing_matches_context(param_def, 'cmd1') is True
    assert param._timing_matches_context(param_def, 'cmd2') is True


def test_timing_matches_context_command_with_nonmatching():
    """Test that _timing_matches_context() returns False for PROMPT_ON_COMMAND with non-matching command.
    
    This test verifies PROMPT_ON_COMMAND timing does not match unlisted commands.
    This behaviour ensures command-timing prompts only appear before configured commands."""
    param_def = {
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['cmd1', 'cmd2']
    }
    assert param._timing_matches_context(param_def, 'cmd3') is False


def test_should_repeat_prompt_always():
    """Test that _should_repeat_prompt() returns True for PROMPT_REPEAT_ALWAYS.
    
    This test verifies PROMPT_REPEAT_ALWAYS mode always allows prompt repetition.
    This behaviour enables prompts to repeat every time for cycle scenarios."""
    param_def = {PARAM_PROMPT_REPEAT: PROMPT_REPEAT_ALWAYS}
    assert param._should_repeat_prompt(param_def, 'test_param') is True


def test_should_repeat_prompt_if_blank_with_value():
    """Test that _should_repeat_prompt() returns False for PROMPT_REPEAT_IF_BLANK when value set.
    
    This test verifies PROMPT_REPEAT_IF_BLANK mode prevents repetition when param has value.
    This behaviour allows prompts to skip when user has already provided a value."""
    param._params = {}
    param.add_param({PARAM_NAME: 'test_param', PARAM_TYPE: PARAM_TYPE_TEXT})
    param.set_param(param_name='test_param', value='value')
    param_def = {PARAM_PROMPT_REPEAT: PROMPT_REPEAT_IF_BLANK}
    assert param._should_repeat_prompt(param_def, 'test_param') is False


def test_should_repeat_prompt_if_blank_without_value():
    """Test that _should_repeat_prompt() returns True for PROMPT_REPEAT_IF_BLANK when value blank.
    
    This test verifies PROMPT_REPEAT_IF_BLANK mode allows repetition when param has no value.
    This behaviour enables prompts to repeat until user provides a value."""
    param._params = {}
    param.add_param({PARAM_NAME: 'test_param', PARAM_TYPE: PARAM_TYPE_TEXT})
    param.set_param(param_name='test_param', value=None)
    param_def = {PARAM_PROMPT_REPEAT: PROMPT_REPEAT_IF_BLANK}
    assert param._should_repeat_prompt(param_def, 'test_param') is True


def test_should_repeat_prompt_never_first_time():
    """Test that _should_repeat_prompt() returns True for PROMPT_REPEAT_NEVER on first call.
    
    This test verifies PROMPT_REPEAT_NEVER mode allows the first prompt.
    This behaviour enables one-time prompts that don't repeat."""
    param._prompted_params = set()
    param_def = {PARAM_PROMPT_REPEAT: PROMPT_REPEAT_NEVER}
    assert param._should_repeat_prompt(param_def, 'test_param') is True


def test_should_repeat_prompt_never_after_prompt():
    """Test that _should_repeat_prompt() returns False for PROMPT_REPEAT_NEVER after prompting.
    
    This test verifies PROMPT_REPEAT_NEVER mode prevents repetition after first prompt.
    This behaviour ensures prompts never repeat once executed."""
    param._prompted_params = set()
    param._prompted_params.add('test_param')
    param_def = {PARAM_PROMPT_REPEAT: PROMPT_REPEAT_NEVER}
    assert param._should_repeat_prompt(param_def, 'test_param') is False


def test_cli_override_prevents_prompt():
    """Test that _should_prompt_param() returns False when param value already set.
    
    This integration test verifies that CLI-provided values prevent prompting,
    regardless of timing or repeat configuration.
    This behaviour is expected because command-line arguments must take precedence
    over interactive prompts."""
    param._params = {}
    param.add_param({
        PARAM_NAME: 'username',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: 'Username:'
    })
    param.set_param(param_name='username', value='cli_user')
    param_def = param._params['username']
    assert param._should_prompt_param(param_def, None) is False


def test_prompt_on_start_timing():
    """Test that _should_prompt_param() enforces PROMPT_ON_START timing.
    
    This integration test verifies params with PROMPT_ON_START timing prompt when
    called from start context (command_name=None) but not from command context.
    This behaviour ensures prompts appear at the correct execution phase."""
    param._params = {}
    param.add_param({
        PARAM_NAME: 'api_key',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: 'API Key:',
        PARAM_PROMPT_TIMING: PROMPT_ON_START
    })
    param_def = param._params['api_key']
    assert param._should_prompt_param(param_def, None, check_value=False) is True
    assert param._should_prompt_param(param_def, 'deploy', check_value=False) is False


def test_prompt_on_command_timing():
    """Test that _should_prompt_param() enforces PROMPT_ON_COMMAND timing.
    
    This integration test verifies params with PROMPT_ON_COMMAND timing prompt only
    before commands listed in PROMPT_ON_COMMANDS.
    This behaviour ensures prompts appear before the correct commands."""
    param._params = {}
    param.add_param({
        PARAM_NAME: 'password',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: 'Password:',
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['login', 'secure_op']
    })
    param_def = param._params['password']
    assert param._should_prompt_param(param_def, None, check_value=False) is False
    assert param._should_prompt_param(param_def, 'login', check_value=False) is True
    assert param._should_prompt_param(param_def, 'secure_op', check_value=False) is True
    assert param._should_prompt_param(param_def, 'other_cmd', check_value=False) is False


def test_set_output_handler():
    """Test that set_output_handler() configures output handler."""
    def custom_handler(message):
        pass
    param.set_output_handler(custom_handler)
    assert param._output_handler == custom_handler
    param.set_output_handler(None)


def test_set_max_prompt_retries():
    """Test that set_max_prompt_retries() updates global retry limit."""
    original = param._max_prompt_retries
    param.set_max_prompt_retries(5)
    assert param._max_prompt_retries == 5
    param.set_max_prompt_retries(original)


def test_log_param_sanitizes_sensitive(monkeypatch):
    """Test log_param() redacts error details for sensitive params."""
    calls = []
    def mock_log(_level, _message):
        calls.append((_level, _message))
    monkeypatch.setattr('spafw37.logging.log', mock_log)
    param_def = {PARAM_NAME: 'api_key', PARAM_SENSITIVE: True}
    message = "Invalid value for 'api_key': secret123 is not valid"
    param.log_param(logging.ERROR, message, param_def)
    assert len(calls) == 1
    assert calls[0][0] == logging.ERROR
    assert calls[0][1] == "Invalid value for sensitive param 'api_key'"


def test_log_param_preserves_nonsensitive(monkeypatch):
    """Test log_param() preserves full message for non-sensitive params."""
    calls = []
    def mock_log(_level, _message):
        calls.append((_level, _message))
    monkeypatch.setattr('spafw37.logging.log', mock_log)
    param_def = {PARAM_NAME: 'count', PARAM_SENSITIVE: False}
    message = "Invalid value for 'count': 'abc' is not a number"
    param.log_param(logging.ERROR, message, param_def)
    assert len(calls) == 1
    assert calls[0][0] == logging.ERROR
    assert calls[0][1] == message


def test_raise_param_error_sanitizes_sensitive():
    """Test raise_param_error() sanitizes exception for sensitive params."""
    param_def = {PARAM_NAME: 'password', PARAM_SENSITIVE: True}
    error = ValueError("'secret123' is too short")
    with pytest.raises(ValueError) as exc_info:
        param.raise_param_error(error, param_def)
    error_message = str(exc_info.value)
    assert "sensitive param 'password'" in error_message
    assert "secret123" not in error_message


def test_raise_param_error_preserves_nonsensitive():
    """Test raise_param_error() raises original error for non-sensitive params."""
    param_def = {PARAM_NAME: 'count', PARAM_SENSITIVE: False}
    error = ValueError("'abc' is not a number")
    with pytest.raises(ValueError) as exc_info:
        param.raise_param_error(error, param_def)
    assert str(exc_info.value) == "'abc' is not a number"


def test_raise_param_error_preserves_type():
    """Test raise_param_error() preserves exception type."""
    param_def = {PARAM_NAME: 'api_key', PARAM_SENSITIVE: True}
    error = TypeError("expected str, got int")
    with pytest.raises(TypeError) as exc_info:
        param.raise_param_error(error, param_def)
    error_message = str(exc_info.value)
    assert "sensitive param 'api_key'" in error_message
    assert "int" not in error_message


def test_retry_decision_infinite():
    """Test _should_continue_after_prompt_error() with infinite retries."""
    should_continue, count = param._should_continue_after_prompt_error(-1, 100)
    assert should_continue is True
    assert count == 100


def test_retry_decision_zero():
    """Test _should_continue_after_prompt_error() with zero retries."""
    should_continue, count = param._should_continue_after_prompt_error(0, 0)
    assert should_continue is False
    assert count == 0


def test_retry_decision_finite_continues():
    """Test _should_continue_after_prompt_error() continues when under limit."""
    should_continue, count = param._should_continue_after_prompt_error(3, 0)
    assert should_continue is True
    assert count == 1


def test_retry_decision_finite_stops():
    """Test _should_continue_after_prompt_error() stops when at limit."""
    should_continue, count = param._should_continue_after_prompt_error(3, 2)
    assert should_continue is False
    assert count == 3


def test_display_validation_error_with_handler(monkeypatch):
    """Test _display_prompt_validation_error() uses log_param and output handler."""
    log_calls = []
    def mock_log_param(level, message, param_def):
        log_calls.append((level, message, param_def))
    monkeypatch.setattr('spafw37.param.log_param', mock_log_param)
    output_calls = []
    def mock_output(message):
        output_calls.append(message)
    param._output_handler = mock_output
    param_def = {PARAM_NAME: 'test_param', PARAM_SENSITIVE: False}
    error = ValueError("must be positive")
    param._display_prompt_validation_error(param_def, error)
    assert len(log_calls) == 1
    assert 'test_param' in log_calls[0][1]
    assert 'must be positive' in log_calls[0][1]
    assert len(output_calls) == 1
    assert 'must be positive' in output_calls[0]
    param._output_handler = None


def test_display_validation_error_defaults_to_print(monkeypatch):
    """Test _display_prompt_validation_error() defaults to print() without handler."""
    log_calls = []
    def mock_log_param(level, message, param_def):
        log_calls.append((level, message, param_def))
    monkeypatch.setattr('spafw37.param.log_param', mock_log_param)
    print_calls = []
    def mock_print(message):
        print_calls.append(message)
    monkeypatch.setattr('builtins.print', mock_print)
    param._output_handler = None
    param_def = {PARAM_NAME: 'test_param', PARAM_SENSITIVE: False}
    error = ValueError("invalid")
    param._display_prompt_validation_error(param_def, error)
    assert len(log_calls) == 1
    assert len(print_calls) == 1
    assert 'invalid' in print_calls[0]


def test_handle_stop_required_nonsensitive_raises():
    """Test _handle_prompt_error_stop() raises original error for non-sensitive params."""
    param_def = {PARAM_NAME: 'count', PARAM_REQUIRED: True, PARAM_SENSITIVE: False}
    error = ValueError("'abc' is not a number")
    with pytest.raises(ValueError) as exc_info:
        param._handle_prompt_error_stop(param_def, error)
    assert "'abc' is not a number" in str(exc_info.value)


def test_handle_stop_required_sensitive_sanitizes():
    """Test _handle_prompt_error_stop() sanitizes error for sensitive params."""
    param_def = {PARAM_NAME: 'api_key', PARAM_REQUIRED: True, PARAM_SENSITIVE: True}
    error = ValueError("'secret123' is not valid")
    with pytest.raises(ValueError) as exc_info:
        param._handle_prompt_error_stop(param_def, error)
    error_message = str(exc_info.value)
    assert "sensitive param 'api_key'" in error_message
    assert "secret123" not in error_message


def test_handle_stop_optional_returns():
    """Test _handle_prompt_error_stop() returns silently for optional params."""
    param_def = {PARAM_NAME: 'optional_param'}
    error = ValueError("invalid")
    result = param._handle_prompt_error_stop(param_def, error)
    assert result is None


def test_execute_prompt_success():
    """Test _execute_prompt() sets value on successful prompt."""
    param._params = {}
    param.add_param({PARAM_NAME: 'test_param', PARAM_TYPE: PARAM_TYPE_TEXT})
    def mock_handler(param_def):
        return 'valid_value'
    param_def = param._params['test_param']
    param._execute_prompt(param_def, mock_handler)
    assert param.get_param(param_name='test_param') == 'valid_value'


def test_execute_prompt_retry_succeeds():
    """Test _execute_prompt() retries after validation failure."""
    param._params = {}
    param.add_param({
        PARAM_NAME: 'test_param',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALLOWED_VALUES: ['valid', 'other']
    })
    call_count = 0
    def mock_handler(param_def):
        nonlocal call_count
        call_count += 1
        return 'invalid' if call_count == 1 else 'valid'
    param_def = param._params['test_param']
    param._execute_prompt(param_def, mock_handler)
    assert call_count == 2
    assert param.get_param(param_name='test_param') == 'valid'


def test_execute_prompt_max_retries_required():
    """Test _execute_prompt() raises ValueError for required param after max retries."""
    param._params = {}
    param.add_param({
        PARAM_NAME: 'required_param',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_REQUIRED: True,
        PARAM_ALLOWED_VALUES: ['valid'],
        PARAM_PROMPT_RETRIES: 2
    })
    def mock_handler(param_def):
        return 'always_invalid'
    param_def = param._params['required_param']
    with pytest.raises(ValueError):
        param._execute_prompt(param_def, mock_handler)


def test_execute_prompt_max_retries_required_sanitizes():
    """Test _execute_prompt() sanitizes error for required sensitive param after max retries."""
    param._params = {}
    param.add_param({
        PARAM_NAME: 'api_key',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_REQUIRED: True,
        PARAM_SENSITIVE: True,
        PARAM_ALLOWED_VALUES: ['valid_key'],
        PARAM_PROMPT_RETRIES: 1
    })
    def mock_handler(param_def):
        return 'secret123'
    param_def = param._params['api_key']
    with pytest.raises(ValueError) as exc_info:
        param._execute_prompt(param_def, mock_handler)
    error_message = str(exc_info.value)
    assert "sensitive param 'api_key'" in error_message
    assert "secret123" not in error_message


def test_execute_prompt_max_retries_optional():
    """Test _execute_prompt() returns silently for optional param after max retries."""
    param._params = {}
    param.add_param({
        PARAM_NAME: 'optional_param',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALLOWED_VALUES: ['valid'],
        PARAM_PROMPT_RETRIES: 2
    })
    def mock_handler(param_def):
        return 'always_invalid'
    param_def = param._params['optional_param']
    param._execute_prompt(param_def, mock_handler)
    assert param.get_param(param_name='optional_param') is None


def test_get_params_to_prompt_filters_timing():
    """Test _get_params_to_prompt() filters params by timing."""
    param._params = {}
    param.add_param({
        PARAM_NAME: 'start1',
        PARAM_PROMPT: 'Enter start1:',
        PARAM_PROMPT_TIMING: PROMPT_ON_START,
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    param.add_param({
        PARAM_NAME: 'start2',
        PARAM_PROMPT: 'Enter start2:',
        PARAM_PROMPT_TIMING: PROMPT_ON_START,
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    param.add_param({
        PARAM_NAME: 'command1',
        PARAM_PROMPT: 'Enter command1:',
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    results = param._get_params_to_prompt(PROMPT_ON_START)
    param_names = [name for name, _, _ in results]
    assert 'start1' in param_names
    assert 'start2' in param_names
    assert 'command1' not in param_names
    assert len(param_names) == 2


def test_get_params_to_prompt_resolves_handlers():
    """Test _get_params_to_prompt() resolves handlers."""
    def custom_handler(param_def):
        return "custom"
    param._params = {}
    param._prompted_params = set()
    param.add_param({
        PARAM_NAME: 'resolves_handler_param',
        PARAM_PROMPT: 'Enter value:',
        PARAM_PROMPT_TIMING: PROMPT_ON_START,
        PARAM_PROMPT_HANDLER: custom_handler,
        PARAM_PROMPT_REPEAT: PROMPT_REPEAT_ALWAYS,
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    results = param._get_params_to_prompt(PROMPT_ON_START)
    assert len(results) == 1
    name, param_def_result, handler = results[0]
    assert name == 'resolves_handler_param'
    assert handler == custom_handler


def test_get_params_for_command_uses_list():
    """Test _get_params_for_command() uses COMMAND_PROMPT_PARAMS list."""
    from spafw37.constants.command import COMMAND_NAME, COMMAND_PROMPT_PARAMS
    from spafw37.constants.param import PROMPT_ON_COMMANDS
    param._params = {}
    param._prompted_params = set()
    param.add_param({
        PARAM_NAME: 'param1',
        PARAM_PROMPT: 'Enter param1:',
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['test_command'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    param.add_param({
        PARAM_NAME: 'param2',
        PARAM_PROMPT: 'Enter param2:',
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['test_command'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    command_def = {
        COMMAND_NAME: 'test_command',
        COMMAND_PROMPT_PARAMS: ['param1', 'param2']
    }
    results = param._get_params_for_command(command_def)
    param_names = [name for name, _, _ in results]
    assert 'param1' in param_names
    assert 'param2' in param_names
    assert len(param_names) == 2


def test_get_params_for_command_filters_by_should_prompt():
    """Test _get_params_for_command() filters using _should_prompt_param()."""
    from spafw37.constants.command import COMMAND_NAME, COMMAND_PROMPT_PARAMS
    from spafw37.constants.param import PROMPT_ON_COMMANDS
    param._params = {}
    param._prompted_params = set()
    param.add_param({
        PARAM_NAME: 'already_set',
        PARAM_PROMPT: 'Enter:',
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['test_command'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    param.add_param({
        PARAM_NAME: 'needs_prompt',
        PARAM_PROMPT: 'Enter:',
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['test_command'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    param.set_param(param_name='already_set', value='value')
    command_def = {
        COMMAND_NAME: 'test_command',
        COMMAND_PROMPT_PARAMS: ['already_set', 'needs_prompt']
    }
    results = param._get_params_for_command(command_def)
    param_names = [name for name, _, _ in results]
    assert 'needs_prompt' in param_names
    assert 'already_set' not in param_names
    assert len(param_names) == 1


def test_execute_prompts_tracks_success():
    """Test _execute_prompts() tracks successful prompts."""
    param._params = {}
    param._prompted_params = set()
    param.add_param({PARAM_NAME: 'param1', PARAM_TYPE: PARAM_TYPE_TEXT})
    param.add_param({PARAM_NAME: 'param2', PARAM_TYPE: PARAM_TYPE_TEXT})
    param.add_param({PARAM_NAME: 'param3', PARAM_TYPE: PARAM_TYPE_TEXT})
    def mock_handler(param_def):
        return 'value'
    params_list = [
        ('param1', param._params['param1'], mock_handler),
        ('param2', param._params['param2'], mock_handler),
        ('param3', param._params['param3'], mock_handler)
    ]
    param._execute_prompts(params_list)
    assert 'param1' in param._prompted_params
    assert 'param2' in param._prompted_params
    assert 'param3' in param._prompted_params


def test_execute_prompts_propagates_errors():
    """Test _execute_prompts() propagates errors from required params."""
    param._params = {}
    param.add_param({
        PARAM_NAME: 'required_param',
        PARAM_REQUIRED: True,
        PARAM_ALLOWED_VALUES: ['valid'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT_RETRIES: 1
    })
    def mock_handler(param_def):
        return 'invalid'
    params_list = [
        ('required_param', param._params['required_param'], mock_handler)
    ]
    with pytest.raises(ValueError):
        param._execute_prompts(params_list)


def test_prompt_params_for_start_orchestration():
    """Test prompt_params_for_start() orchestrates identification and execution."""
    param._params = {}
    param._prompted_params = set()
    param.add_param({
        PARAM_NAME: 'start_param',
        PARAM_PROMPT: 'Enter value:',
        PARAM_PROMPT_TIMING: PROMPT_ON_START,
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    def mock_handler(param_def):
        return 'value'
    param._global_prompt_handler = mock_handler
    param.prompt_params_for_start()
    assert param.get_param(param_name='start_param') == 'value'
    assert 'start_param' in param._prompted_params


def test_prompt_params_for_start_no_params():
    """Test prompt_params_for_start() returns early with no params."""
    param._params = {}
    param._prompted_params = set()
    param.prompt_params_for_start()
    assert len(param._prompted_params) == 0


def test_prompt_params_for_command_orchestration():
    """Test prompt_params_for_command() orchestrates identification and execution."""
    from spafw37.constants.command import COMMAND_NAME, COMMAND_PROMPT_PARAMS
    from spafw37.constants.param import PROMPT_ON_COMMANDS
    param._params = {}
    param._prompted_params = set()
    param.add_param({
        PARAM_NAME: 'command_param',
        PARAM_PROMPT: 'Enter value:',
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['test_command'],
        PARAM_TYPE: PARAM_TYPE_TEXT
    })
    command_def = {
        COMMAND_NAME: 'test_command',
        COMMAND_PROMPT_PARAMS: ['command_param']
    }
    def mock_handler(param_def):
        return 'value'
    param._global_prompt_handler = mock_handler
    param.prompt_params_for_command(command_def)
    assert param.get_param(param_name='command_param') == 'value'
    assert 'command_param' in param._prompted_params


def test_prompt_params_for_command_no_params():
    """Test prompt_params_for_command() returns early with no COMMAND_PROMPT_PARAMS."""
    from spafw37.constants.command import COMMAND_NAME
    param._params = {}
    param._prompted_params = set()
    command_def = {COMMAND_NAME: 'test_command'}
    param.prompt_params_for_command(command_def)
    assert len(param._prompted_params) == 0
