"""Sensitive parameter handling demonstration.

This example shows:
- PARAM_PROMPT_SENSITIVE flag to hide input
- Password/token input without terminal display
- Secure handling of sensitive data

Usage:
    python params_prompt_sensitive.py login
    # Username displays as you type
    # Password is hidden (no echo)

**Added in v1.1.0**
"""

import getpass
from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_ALIASES,
    PARAM_DESCRIPTION,
    PARAM_PROMPT,
    PARAM_PROMPT_TIMING,
    PARAM_PROMPT_SENSITIVE,
    PROMPT_ON_START,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)


def sensitive_prompt_handler(param_config):
    """Custom handler for sensitive input using getpass."""
    prompt_text = param_config.get(PARAM_PROMPT, 'Enter value: ')
    is_sensitive = param_config.get(PARAM_PROMPT_SENSITIVE, False)
    
    if is_sensitive:
        # Use getpass for hidden input
        return getpass.getpass(prompt_text)
    else:
        # Use regular input
        return input(prompt_text)


def login_command():
    """Login command using credentials."""
    username = spafw37.get_param('username')
    password = spafw37.get_param('password')
    api_token = spafw37.get_param('api-token')
    
    print(f'\nLogin attempt for user: {username}')
    print(f'Password length: {len(password)} characters')
    print(f'API Token length: {len(api_token)} characters')
    print('(Sensitive values not displayed for security)')


if __name__ == '__main__':
    # Configure custom handler that supports sensitive input
    spafw37.set_prompt_handler(sensitive_prompt_handler)
    
    # Define parameters (normal and sensitive)
    spafw37.add_params([
        {
            PARAM_NAME: 'username',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALIASES: ['--username', '-u'],
            PARAM_DESCRIPTION: 'Username for authentication',
            PARAM_PROMPT: 'Enter username: ',
            PARAM_PROMPT_TIMING: PROMPT_ON_START,
        },
        {
            PARAM_NAME: 'password',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALIASES: ['--password', '-p'],
            PARAM_DESCRIPTION: 'Password (hidden input)',
            PARAM_PROMPT: 'Enter password: ',
            PARAM_PROMPT_TIMING: PROMPT_ON_START,
            PARAM_PROMPT_SENSITIVE: True,  # Hide input
        },
        {
            PARAM_NAME: 'api-token',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALIASES: ['--api-token', '-t'],
            PARAM_DESCRIPTION: 'API authentication token (hidden input)',
            PARAM_PROMPT: 'Enter API token: ',
            PARAM_PROMPT_TIMING: PROMPT_ON_START,
            PARAM_PROMPT_SENSITIVE: True,  # Hide input
        },
    ])
    
    # Define command
    spafw37.add_commands([{
        COMMAND_NAME: 'login',
        COMMAND_DESCRIPTION: 'Authenticate with credentials',
        COMMAND_ACTION: login_command,
    }])
    
    # Run CLI
    spafw37.run_cli()
