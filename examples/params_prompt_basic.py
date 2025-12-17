"""Basic parameter prompt demonstration.

This example shows:
- Basic prompt usage with PROMPT_ON_START timing
- Text input prompts
- CLI override behaviour (pass --username value to skip prompt)

Usage:
    python params_prompt_basic.py process
    # Will prompt: Enter username:
    
    python params_prompt_basic.py --username alice process
    # Skips prompt, uses CLI value

**Added in v1.1.0**
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_ALIASES,
    PARAM_DESCRIPTION,
    PARAM_PROMPT,
    PARAM_PROMPT_TIMING,
    PROMPT_ON_START,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)


def process_command():
    """Command handler that displays param values."""
    username = spafw37.get_param('username')
    print(f'Processing for user: {username}')


if __name__ == '__main__':
    # Define parameter with prompt
    spafw37.add_params([{
        PARAM_NAME: 'username',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--username', '-u'],
        PARAM_DESCRIPTION: 'Username for processing',
        PARAM_PROMPT: 'Enter username: ',
        PARAM_PROMPT_TIMING: PROMPT_ON_START,
    }])
    
    # Define command
    spafw37.add_commands([{
        COMMAND_NAME: 'process',
        COMMAND_DESCRIPTION: 'Process data for user',
        COMMAND_ACTION: process_command,
    }])
    
    # Run CLI - if no --username provided, will prompt
    spafw37.run_cli()
