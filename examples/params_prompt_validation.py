"""Prompt validation and retry demonstration.

This example shows:
- Integration with PARAM_INPUT_FILTER for validation
- Automatic retry on validation failure
- Custom error messages from input filters
- Maximum retry configuration

Usage:
    python params_prompt_validation.py process
    # Try entering invalid values to see retry behaviour
    # Age: enter negative number or text
    # Email: enter invalid email format

**Added in v1.1.0**
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_ALIASES,
    PARAM_DESCRIPTION,
    PARAM_PROMPT,
    PARAM_PROMPT_TIMING,
    PARAM_INPUT_FILTER,
    PROMPT_ON_START,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)


def validate_age(value_str):
    """Validate age is positive number."""
    try:
        age = int(value_str)
        if age < 0:
            raise ValueError("Age must be positive")
        if age > 150:
            raise ValueError("Age must be less than 150")
        return str(age)
    except ValueError as error:
        raise ValueError(f"Invalid age: {error}")


def validate_email(value_str):
    """Validate email format."""
    value_str = value_str.strip()
    if not value_str:
        raise ValueError("Email cannot be empty")
    if '@' not in value_str:
        raise ValueError("Email must contain @")
    if '.' not in value_str.split('@')[1]:
        raise ValueError("Email domain must contain .")
    return value_str


def register_command():
    """Registration command."""
    name = spafw37.get_param('name')
    age = spafw37.get_param('age')
    email = spafw37.get_param('email')
    
    print(f'\nRegistration successful:')
    print(f'  Name: {name}')
    print(f'  Age: {age}')
    print(f'  Email: {email}')


if __name__ == '__main__':
    # Set retry limit to 3 attempts
    spafw37.set_max_prompt_retries(3)
    
    # Define parameters with validation
    spafw37.add_params([
        {
            PARAM_NAME: 'name',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALIASES: ['--name', '-n'],
            PARAM_DESCRIPTION: 'User name',
            PARAM_PROMPT: 'Enter your name: ',
            PARAM_PROMPT_TIMING: PROMPT_ON_START,
        },
        {
            PARAM_NAME: 'age',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_ALIASES: ['--age', '-a'],
            PARAM_DESCRIPTION: 'User age',
            PARAM_PROMPT: 'Enter your age (0-150): ',
            PARAM_PROMPT_TIMING: PROMPT_ON_START,
            PARAM_INPUT_FILTER: validate_age,
        },
        {
            PARAM_NAME: 'email',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALIASES: ['--email', '-e'],
            PARAM_DESCRIPTION: 'User email address',
            PARAM_PROMPT: 'Enter your email: ',
            PARAM_PROMPT_TIMING: PROMPT_ON_START,
            PARAM_INPUT_FILTER: validate_email,
        },
    ])
    
    # Define command
    spafw37.add_commands([{
        COMMAND_NAME: 'register',
        COMMAND_DESCRIPTION: 'Register a new user',
        COMMAND_ACTION: register_command,
    }])
    
    # Run CLI
    spafw37.run_cli()
