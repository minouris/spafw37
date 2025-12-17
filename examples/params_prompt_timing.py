"""Prompt timing control demonstration.

This example shows:
- PROMPT_ON_START timing (prompt at application start)
- PROMPT_ON_COMMAND timing (prompt before specific commands)
- PROMPT_ON_COMMANDS property (specify which commands trigger prompts)

Usage:
    python params_prompt_timing.py init delete
    # api_key prompts at start (before any commands)
    # confirmation prompts before delete command only

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
    PROMPT_ON_COMMAND,
    PROMPT_ON_COMMANDS,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)


def init_command():
    """Initialisation command."""
    api_key = spafw37.get_param('api-key')
    print(f'Initialised with API key: {api_key[:10]}...')


def delete_command():
    """Deletion command requiring confirmation."""
    confirmation = spafw37.get_param('confirmation')
    if confirmation.lower() == 'yes':
        print('Deletion confirmed and executed')
    else:
        print('Deletion cancelled')


if __name__ == '__main__':
    # This param prompts at application start (before any commands run)
    spafw37.add_params([{
        PARAM_NAME: 'api-key',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--api-key', '-k'],
        PARAM_DESCRIPTION: 'API authentication key',
        PARAM_PROMPT: 'Enter API key: ',
        PARAM_PROMPT_TIMING: PROMPT_ON_START,
    }])
    
    # This param prompts only before delete command (per-command timing)
    spafw37.add_params([{
        PARAM_NAME: 'confirmation',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--confirm', '-c'],
        PARAM_DESCRIPTION: 'Deletion confirmation',
        PARAM_PROMPT: 'Proceed with deletion? (yes/no): ',
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['delete'],
    }])
    
    # Define commands
    spafw37.add_commands([
        {
            COMMAND_NAME: 'init',
            COMMAND_DESCRIPTION: 'Initialise the system',
            COMMAND_ACTION: init_command,
        },
        {
            COMMAND_NAME: 'delete',
            COMMAND_DESCRIPTION: 'Delete data (requires confirmation)',
            COMMAND_ACTION: delete_command,
        },
    ])
    
    # Run CLI
    spafw37.run_cli()
