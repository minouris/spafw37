"""Custom prompt and output handler demonstration.

This example shows:
- Custom prompt handler with set_prompt_handler()
- Custom output handler with set_output_handler()
- Retry limit configuration with set_max_prompt_retries()

Usage:
    python params_prompt_handlers.py process
    # Shows custom formatting and retry handling

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
    PROMPT_ON_START,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)


def custom_prompt_handler(param_config):
    """Custom prompt handler with special formatting."""
    prompt_text = param_config.get(PARAM_PROMPT, 'Enter value: ')
    param_name = param_config.get(PARAM_NAME, 'unknown')
    
    # Add custom formatting
    print(f"\n{'=' * 50}")
    print(f"Parameter: {param_name}")
    print(f"{'=' * 50}")
    
    return input(prompt_text)


def custom_output_handler(message):
    """Custom output handler with prefix."""
    print(f"[PROMPT] {message}")


def process_command():
    """Process command."""
    username = spafw37.get_param('username')
    batch_size = spafw37.get_param('batch-size')
    print(f'\nProcessing with:')
    print(f'  Username: {username}')
    print(f'  Batch Size: {batch_size}')


if __name__ == '__main__':
    # Configure custom handlers
    spafw37.set_prompt_handler(custom_prompt_handler)
    spafw37.set_output_handler(custom_output_handler)
    spafw37.set_max_prompt_retries(5)  # Allow 5 retry attempts
    
    # Define parameters with prompts
    spafw37.add_params([
        {
            PARAM_NAME: 'username',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALIASES: ['--username', '-u'],
            PARAM_DESCRIPTION: 'Username for processing',
            PARAM_PROMPT: 'Enter username: ',
            PARAM_PROMPT_TIMING: PROMPT_ON_START,
        },
        {
            PARAM_NAME: 'batch-size',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_ALIASES: ['--batch-size', '-b'],
            PARAM_DESCRIPTION: 'Batch size for processing',
            PARAM_PROMPT: 'Enter batch size (1-100): ',
            PARAM_PROMPT_TIMING: PROMPT_ON_START,
        },
    ])
    
    # Define command
    spafw37.add_commands([{
        COMMAND_NAME: 'process',
        COMMAND_DESCRIPTION: 'Process data',
        COMMAND_ACTION: process_command,
    }])
    
    # Run CLI
    spafw37.run_cli()
