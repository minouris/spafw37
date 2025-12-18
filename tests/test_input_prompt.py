"""Tests for input_prompt module - default interactive prompt handler."""

from io import StringIO
import pytest

from spafw37 import input_prompt
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_PROMPT,
    PARAM_DEFAULT,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_TOGGLE,
    PARAM_ALLOWED_VALUES,
    PARAM_SENSITIVE
)


def test_format_prompt_text_with_default():
    """Test that prompt text formatting includes default values using bash convention.
    
    This test verifies that when a parameter has PARAM_DEFAULT set, the formatted prompt
    displays "[default: value]" following standard bash/Unix prompt conventions.
    This behaviour is expected because users need clear indication of what value will be
    used if they press Enter without typing, matching familiar command-line tool patterns."""
    param_def = {
        PARAM_DEFAULT: 'example_default',
        PARAM_PROMPT: 'Enter text'
    }
    formatted_text = input_prompt._format_prompt_text(param_def)
    assert '[default: example_default]' in formatted_text, "Default value not displayed"
    assert formatted_text == 'Enter text [default: example_default]: ', "Format incorrect"


def test_format_prompt_text_sensitive_hides_default():
    """Test that sensitive params do not display default values in prompt text.
    
    This test verifies that when a parameter has PARAM_SENSITIVE=True, the formatted
    prompt does not include "[default: value]" even if PARAM_DEFAULT is set.
    This behaviour is expected because displaying default values for passwords, API keys,
    or other sensitive data in terminal output creates security risks (screen capture,
    terminal history, shoulder surfing). The default will still be used if user presses
    Enter, but it won't be visible."""
    param_def = {
        PARAM_PROMPT: 'API Key',
        PARAM_DEFAULT: 'secret_key_123',
        PARAM_SENSITIVE: True
    }
    formatted_text = input_prompt._format_prompt_text(param_def)
    assert '[default:' not in formatted_text, "Default should not be displayed for sensitive param"
    assert 'secret_key_123' not in formatted_text, "Sensitive value should not appear in prompt"
    assert formatted_text == 'API Key: ', "Format should be prompt text with colon only"


def test_prompt_text_input_returns_string(monkeypatch):
    """Test that the default prompt handler captures plain text input from users.
    
    This test verifies that when stdin is mocked with StringIO containing "test value",
    the prompt_for_value() function returns exactly that string without modification.
    This behaviour is expected because text parameters are the simplest type and should
    return user input verbatim, establishing the foundation for all other input types."""
    param_def = {
        PARAM_NAME: 'test_param',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: 'Enter text'
    }
    mock_stdin = StringIO("test value\n")
    monkeypatch.setattr('sys.stdin', mock_stdin)
    user_value = input_prompt.prompt_for_value(param_def)
    assert user_value == "test value", "Expected 'test value', got '{0}'".format(user_value)


def test_prompt_text_with_default_blank_input(monkeypatch):
    """Test that pressing Enter without typing selects the default value automatically.
    
    This test verifies that when stdin is mocked with just a newline character and
    PARAM_DEFAULT is set, the function returns the default value.
    This behaviour is expected because the bash convention of showing "[default: value]"
    implies that blank input (just pressing Enter) will use that default value."""
    param_def = {
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PROMPT: 'Enter text',
        PARAM_DEFAULT: 'default_value'
    }
    mock_stdin = StringIO("\n")
    monkeypatch.setattr('sys.stdin', mock_stdin)
    user_value = input_prompt.prompt_for_value(param_def)
    assert user_value == 'default_value', "Expected 'default_value', got '{0}'".format(user_value)


def test_prompt_sensitive_param_uses_getpass(monkeypatch):
    """Test that sensitive parameters use getpass.getpass() for non-echoing input.
    
    This test verifies that when PARAM_SENSITIVE is True, the handler calls getpass.getpass()
    instead of input() to prevent keystrokes from being echoed to the terminal.
    This behaviour is expected for security reasons - passwords, API keys, and tokens should not
    be visible on screen or in terminal logs."""
    param_def = {
        PARAM_PROMPT: 'Password',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_SENSITIVE: True
    }
    getpass_called = []
    def mock_getpass(prompt_text):
        getpass_called.append(prompt_text)
        return "secret123"
    monkeypatch.setattr('spafw37.input_prompt.getpass', mock_getpass)
    user_value = input_prompt.prompt_for_value(param_def)
    assert len(getpass_called) == 1, "getpass should have been called once"
    assert user_value == "secret123", "Expected 'secret123', got '{0}'".format(user_value)


def test_prompt_sensitive_param_suppresses_default_display(monkeypatch):
    """Test that sensitive parameters do not display default values in prompt text.
    
    This test verifies that when PARAM_SENSITIVE is True and PARAM_DEFAULT is set,
    the formatted prompt text does NOT include the '[default: value]' suffix.
    This behaviour is expected for security reasons - displaying default passwords or API keys
    in the prompt would leak credentials in terminal logs, screen recordings, or observed screens."""
    param_def = {
        PARAM_PROMPT: 'API Key',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_SENSITIVE: True,
        PARAM_DEFAULT: 'old_secret_key_12345'
    }
    getpass_called = []
    def mock_getpass(prompt_text):
        getpass_called.append(prompt_text)
        return ""
    monkeypatch.setattr('spafw37.input_prompt.getpass', mock_getpass)
    input_prompt.prompt_for_value(param_def)
    prompt_text = getpass_called[0]
    assert '[default:' not in prompt_text, "Sensitive param must not display default value"
    assert 'old_secret_key_12345' not in prompt_text, "Credential leaked in prompt text"
    assert prompt_text == 'API Key: ', "Expected 'API Key: ', got '{0}'".format(prompt_text)


def test_prompt_number_integer_valid(monkeypatch):
    """Test that integer input is correctly converted to int type for numeric parameters.
    
    This test verifies that when a user enters "42" for a PARAM_TYPE_NUMBER parameter,
    the handler converts it to the integer 42 (not string or float).
    This behaviour is expected because integer input (no decimal point) should be
    converted using int() for proper numeric operations, counters, and array indices."""
    param_def = {
        PARAM_PROMPT: 'Enter number',
        PARAM_TYPE: PARAM_TYPE_NUMBER
    }
    mock_stdin = StringIO("42\n")
    monkeypatch.setattr('sys.stdin', mock_stdin)
    result_value = input_prompt.prompt_for_value(param_def)
    assert isinstance(result_value, int), "Expected int type, got {0}".format(type(result_value))
    assert result_value == 42, "Expected 42, got {0}".format(result_value)


def test_prompt_number_float_valid(monkeypatch):
    """Test that floating-point input is correctly converted to float type for numeric parameters.
    
    This test verifies that when a user enters "3.14" for a PARAM_TYPE_NUMBER parameter,
    the handler converts it to the float 3.14 (not string or integer).
    This behaviour is expected because float input (contains decimal point) should be
    converted using float() for precise measurements, percentages, and scientific values."""
    param_def = {
        PARAM_PROMPT: 'Enter number',
        PARAM_TYPE: PARAM_TYPE_NUMBER
    }
    mock_stdin = StringIO("3.14\n")
    monkeypatch.setattr('sys.stdin', mock_stdin)
    result_value = input_prompt.prompt_for_value(param_def)
    assert isinstance(result_value, float), "Expected float type, got {0}".format(type(result_value))
    assert result_value == 3.14, "Expected 3.14, got {0}".format(result_value)


def test_prompt_number_invalid_raises_error(monkeypatch):
    """Test that non-numeric input raises ValueError for numeric parameters.
    
    This test verifies that when a user enters "not_a_number" for a PARAM_TYPE_NUMBER parameter,
    the handler raises ValueError rather than returning invalid data.
    This behaviour is expected because type conversion failures must be caught and reported
    clearly, enabling retry logic at higher levels to prompt the user again."""
    param_def = {
        PARAM_PROMPT: 'Enter number',
        PARAM_TYPE: PARAM_TYPE_NUMBER
    }
    mock_stdin = StringIO("not_a_number\n")
    monkeypatch.setattr('sys.stdin', mock_stdin)
    with pytest.raises(ValueError):
        input_prompt.prompt_for_value(param_def)


def test_prompt_toggle_yes_variations(monkeypatch):
    """Test that toggle parameters accept multiple affirmative formats with case-insensitive matching.
    
    This test verifies that inputs "y", "Y", "yes", "YES", "true", and "True" all return
    the Python boolean True for PARAM_TYPE_TOGGLE parameters.
    This behaviour is expected because providing flexible, user-friendly input options
    improves usability rather than forcing users to remember exact format requirements."""
    param_def = {
        PARAM_PROMPT: 'Confirm?',
        PARAM_TYPE: PARAM_TYPE_TOGGLE
    }
    affirmative_inputs = ['y', 'Y', 'yes', 'YES', 'true', 'True']
    for test_input in affirmative_inputs:
        mock_stdin = StringIO("{0}\n".format(test_input))
        monkeypatch.setattr('sys.stdin', mock_stdin)
        result_value = input_prompt.prompt_for_value(param_def)
        assert result_value is True, "Input '{0}' should return True".format(test_input)


def test_prompt_toggle_no_variations(monkeypatch):
    """Test that toggle parameters accept multiple negative formats with case-insensitive matching.
    
    This test verifies that inputs "n", "N", "no", "NO", "false", and "False" all return
    the Python boolean False for PARAM_TYPE_TOGGLE parameters.
    This behaviour is expected because comprehensive support for common negative variations
    provides a complete and intuitive toggle input experience."""
    param_def = {
        PARAM_PROMPT: 'Confirm?',
        PARAM_TYPE: PARAM_TYPE_TOGGLE
    }
    negative_inputs = ['n', 'N', 'no', 'NO', 'false', 'False']
    for test_input in negative_inputs:
        mock_stdin = StringIO("{0}\n".format(test_input))
        monkeypatch.setattr('sys.stdin', mock_stdin)
        result_value = input_prompt.prompt_for_value(param_def)
        assert result_value is False, "Input '{0}' should return False".format(test_input)


def test_prompt_toggle_invalid_raises_error(monkeypatch):
    """Test that unrecognized input raises ValueError for toggle parameters.
    
    This test verifies that when a user enters "maybe" for a PARAM_TYPE_TOGGLE parameter,
    the handler raises ValueError with a clear message about expected formats.
    This behaviour is expected because ambiguous or invalid input must be rejected,
    enabling retry logic to prompt the user again with guidance on valid options."""
    param_def = {
        PARAM_PROMPT: 'Confirm?',
        PARAM_TYPE: PARAM_TYPE_TOGGLE
    }
    mock_stdin = StringIO("maybe\n")
    monkeypatch.setattr('sys.stdin', mock_stdin)
    with pytest.raises(ValueError, match="Expected y/yes/true or n/no/false"):
        input_prompt.prompt_for_value(param_def)


def test_prompt_eof_raises_error(monkeypatch):
    """Test that EOF condition raises EOFError when stdin closes unexpectedly.
    
    This test verifies that when stdin is empty (EOF condition from Ctrl+D, closed pipe,
    or automated scripts), the handler raises EOFError rather than failing silently.
    This behaviour is expected because EOF must be detected and reported clearly,
    ensuring the application fails predictably in non-interactive environments."""
    param_def = {
        PARAM_PROMPT: 'Enter value',
        PARAM_TYPE: PARAM_TYPE_TEXT
    }
    mock_stdin = StringIO("")
    monkeypatch.setattr('sys.stdin', mock_stdin)
    with pytest.raises(EOFError):
        input_prompt.prompt_for_value(param_def)
