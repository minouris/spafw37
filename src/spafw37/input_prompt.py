"""Default interactive prompt handler using Python's built-in input() function.

This module provides the default implementation for soliciting user input
at runtime for params configured with PARAM_PROMPT. The handler supports
text, number, toggle, and multiple choice inputs with proper type conversion
and default value handling.
"""

from getpass import getpass

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


def _format_prompt_text(param_def):
    """Format prompt text with default value in bash convention.
    
    Sensitive params (PARAM_SENSITIVE=True) do not display default values
    to prevent credential leakage in terminal history or screen capture.
    
    Args:
        param_def: Parameter definition dictionary.
        
    Returns:
        Formatted prompt string with [default: value] if default exists and not sensitive.
    """
    prompt_text = param_def.get(PARAM_PROMPT, 'Enter value')
    is_sensitive = param_def.get(PARAM_SENSITIVE, False)
    default_value = param_def.get(PARAM_DEFAULT)
    if default_value is not None and not is_sensitive:
        prompt_text = "{0} [default: {1}]".format(prompt_text, default_value)
    return "{0}: ".format(prompt_text)


def _handle_text_input(param_def, user_input):
    """Handle text input type with sensitive data support.
    
    Uses getpass.getpass() for sensitive params (no echo) and regular user_input for non-sensitive.
    
    Args:
        param_def: Parameter definition dictionary.
        user_input: Raw user input string (ignored for sensitive params, as getpass gets input directly).
        
    Returns:
        User input string or default value if blank.
    """
    if user_input.strip():
        return user_input.strip()
    return param_def.get(PARAM_DEFAULT)


def _handle_number_input(param_def, user_input):
    """Handle number input with int/float conversion.
    
    Args:
        param_def: Parameter definition dictionary.
        user_input: Raw user input string.
        
    Returns:
        Converted number (int or float) or default value if blank.
        
    Raises:
        ValueError: If input cannot be converted to number.
    """
    if not user_input.strip():
        return param_def.get(PARAM_DEFAULT)
    try:
        return int(user_input)
    except ValueError:
        pass
    return float(user_input)


def _handle_toggle_input(param_def, user_input):
    """Handle toggle (boolean) input with multiple accepted formats.
    
    Accepts: y/yes/true (case-insensitive) for True
             n/no/false (case-insensitive) for False
    
    Args:
        param_def: Parameter definition dictionary.
        user_input: Raw user input string.
        
    Returns:
        Boolean value or default value if blank.
        
    Raises:
        ValueError: If input is not a recognized boolean format.
    """
    if not user_input.strip():
        return param_def.get(PARAM_DEFAULT)
    normalized_input = user_input.strip().lower()
    if normalized_input in ('y', 'yes', 'true'):
        return True
    if normalized_input in ('n', 'no', 'false'):
        return False
    raise ValueError("Expected y/yes/true or n/no/false")


def _handle_multiple_choice_input(param_def, user_input, allowed_values):
    """Handle multiple choice input with numeric or text selection.
    
    Args:
        param_def: Parameter definition dictionary.
        user_input: Raw user input string.
        allowed_values: List of allowed string values.
        
    Returns:
        Selected value from allowed_values or default if blank.
        
    Raises:
        ValueError: If input is not valid selection (number or text).
    """
    if not user_input.strip():
        return param_def.get(PARAM_DEFAULT)
    try:
        selection_index = int(user_input) - 1
        if 0 <= selection_index < len(allowed_values):
            return allowed_values[selection_index]
    except ValueError:
        pass
    user_input_stripped = user_input.strip()
    if user_input_stripped in allowed_values:
        return user_input_stripped
    raise ValueError("Invalid selection. Enter number or exact text value")


def _display_multiple_choice_options(allowed_values):
    """Display numbered list of multiple choice options.
    
    Args:
        allowed_values: List of allowed string values to display.
    """
    for option_index, option_value in enumerate(allowed_values, start=1):
        print("{0}. {1}".format(option_index, option_value))


def prompt_for_value(param_def):
    """Main prompt handler using Python's built-in input() function.
    
    Prompts user for input based on param type and configuration.
    Handles text, number, toggle, and multiple choice inputs.
    
    Args:
        param_def: Parameter definition dictionary containing:
            - PARAM_PROMPT: Prompt text to display
            - PARAM_TYPE: Type of input (text/number/toggle)
            - PARAM_DEFAULT: Optional default value
            - PARAM_ALLOWED_VALUES: Optional list for multiple choice
            - PARAM_SENSITIVE: Optional bool for non-echoing input
    
    Returns:
        User input value converted to appropriate type.
        
    Raises:
        EOFError: If stdin reaches EOF (non-interactive environment).
        ValueError: If input cannot be converted to required type.
    """
    allowed_values = param_def.get(PARAM_ALLOWED_VALUES)
    if allowed_values:
        _display_multiple_choice_options(allowed_values)
    prompt_text = _format_prompt_text(param_def)
    is_sensitive = param_def.get(PARAM_SENSITIVE, False)
    if is_sensitive:
        user_input = getpass(prompt_text)
    else:
        user_input = input(prompt_text)
    if allowed_values:
        return _handle_multiple_choice_input(param_def, user_input, allowed_values)
    param_type = param_def.get(PARAM_TYPE, PARAM_TYPE_TEXT)
    if param_type == PARAM_TYPE_NUMBER:
        return _handle_number_input(param_def, user_input)
    elif param_type == PARAM_TYPE_TOGGLE:
        return _handle_toggle_input(param_def, user_input)
    else:
        return _handle_text_input(param_def, user_input)
