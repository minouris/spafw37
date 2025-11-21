"""Basic Parameters Example - Simple parameter types and aliases.

This example shows:
- Text parameters
- Number parameters
- Parameter aliases (multiple ways to specify the same parameter)
- Default values
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_DEFAULT,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)

# Define basic parameters
params = [
    # Text parameter with aliases
    {
        PARAM_NAME: 'input-file',
        PARAM_DESCRIPTION: 'Input file path',
        PARAM_ALIASES: ['--input', '-i'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
    },
    # Text parameter with default value
    {
        PARAM_NAME: 'output-file',
        PARAM_DESCRIPTION: 'Output file path',
        PARAM_ALIASES: ['--output', '-o'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DEFAULT: 'output.txt',
    },
    # Number parameter
    {
        PARAM_NAME: 'count',
        PARAM_DESCRIPTION: 'Number of items to process',
        PARAM_ALIASES: ['--count', '-c'],
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_DEFAULT: 10,
    },
]

def process_command():
    """Process with basic parameters."""
    # Get parameter values
    input_file = spafw37.get_param('input-file')
    output_file = spafw37.get_param('output-file')
    count = spafw37.get_param('count')
    
    spafw37.output(f"Processing: {input_file}")
    spafw37.output(f"Output to: {output_file}")
    spafw37.output(f"Count: {count}")
    
    for i in range(count):
        spafw37.output(f"  Processing item {i + 1}/{count}")
    
    spafw37.output(f"\nCompleted! Results written to {output_file}")

# Define command
commands = [
    {
        COMMAND_NAME: 'process',
        COMMAND_DESCRIPTION: 'Process files with basic parameters',
        COMMAND_ACTION: process_command,
    }
]

# Register parameters and commands
spafw37.add_params(params)
spafw37.add_commands(commands)
spafw37.set_app_name('params-basic-demo')

if __name__ == '__main__':
    spafw37.run_cli()
