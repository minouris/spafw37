"""Prompt repeat behaviour demonstration.

This example shows:
- PROMPT_REPEAT_NEVER (prompt only once, reuse value)
- PROMPT_REPEAT_ALWAYS (prompt every time)
- How repeat behaviour affects multiple command execution

Usage:
    python params_prompt_repeat.py process process process
    # batch-size prompts once (REPEAT_NEVER)
    # continue-flag prompts every time (REPEAT_ALWAYS)

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
    PARAM_PROMPT_REPEAT,
    PROMPT_ON_COMMAND,
    PROMPT_ON_COMMANDS,
    PROMPT_REPEAT_NEVER,
    PROMPT_REPEAT_ALWAYS,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)


iteration_count = [0]


def process_command():
    """Command that demonstrates repeat behaviour."""
    iteration_count[0] += 1
    batch_size = spafw37.get_param('batch-size')
    continue_flag = spafw37.get_param('continue-flag')
    
    print(f'\n--- Iteration {iteration_count[0]} ---')
    print(f'Batch Size: {batch_size}')
    print(f'Continue: {continue_flag}')


if __name__ == '__main__':
    # This param prompts only once (default REPEAT_NEVER behaviour)
    # Value is reused for subsequent command invocations
    spafw37.add_params([{
        PARAM_NAME: 'batch-size',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_ALIASES: ['--batch-size', '-b'],
        PARAM_DESCRIPTION: 'Processing batch size',
        PARAM_PROMPT: 'Enter batch size: ',
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['process'],
        PARAM_PROMPT_REPEAT: PROMPT_REPEAT_NEVER,  # Prompt once, reuse value
    }])
    
    # This param prompts every time (REPEAT_ALWAYS behaviour)
    # User is asked for input before each command execution
    spafw37.add_params([{
        PARAM_NAME: 'continue-flag',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--continue', '-c'],
        PARAM_DESCRIPTION: 'Continue processing flag',
        PARAM_PROMPT: 'Continue processing? (yes/no): ',
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['process'],
        PARAM_PROMPT_REPEAT: PROMPT_REPEAT_ALWAYS,  # Prompt every time
    }])
    
    # Define command
    spafw37.add_commands([{
        COMMAND_NAME: 'process',
        COMMAND_DESCRIPTION: 'Process a batch of data',
        COMMAND_ACTION: process_command,
    }])
    
    # Run CLI - try running the command multiple times
    # Example: python params_prompt_repeat.py process process process
    spafw37.run_cli()
