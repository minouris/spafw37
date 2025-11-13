"""
Parameter Groups Example

Demonstrates organizing parameters into groups for better help display.

Key concepts:
- Using PARAM_GROUP to organize related parameters
- Grouping parameters by functional area
- Improving help output readability
- Organizing large parameter sets

This example models a file processing tool with parameters grouped by:
1. Input/Output Options - File paths and formats
2. Processing Options - Performance and behavior settings
3. Validation Options - Quality control settings
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_TOGGLE,
    PARAM_DEFAULT,
    PARAM_GROUP,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)


def setup():
    """Configure the application with grouped parameters."""
    
    # Define parameters organized into functional groups
    params = [
        # Input/Output Options group
        {
            PARAM_NAME: 'input-file',
            PARAM_DESCRIPTION: 'Path to input file',
            PARAM_ALIASES: ['--input', '-i'],
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_GROUP: 'Input/Output Options',
        },
        {
            PARAM_NAME: 'output-file',
            PARAM_DESCRIPTION: 'Path to output file',
            PARAM_ALIASES: ['--output', '-o'],
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_GROUP: 'Input/Output Options',
        },
        {
            PARAM_NAME: 'format',
            PARAM_DESCRIPTION: 'Output format (json, xml, csv)',
            PARAM_ALIASES: ['--format', '-f'],
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_DEFAULT: 'json',
            PARAM_GROUP: 'Input/Output Options',
        },
        
        # Processing Options group
        {
            PARAM_NAME: 'threads',
            PARAM_DESCRIPTION: 'Number of processing threads',
            PARAM_ALIASES: ['--threads', '-t'],
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_DEFAULT: 1,
            PARAM_GROUP: 'Processing Options',
        },
        {
            PARAM_NAME: 'batch-size',
            PARAM_DESCRIPTION: 'Number of items per batch',
            PARAM_ALIASES: ['--batch-size', '-b'],
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_DEFAULT: 100,
            PARAM_GROUP: 'Processing Options',
        },
        {
            PARAM_NAME: 'parallel',
            PARAM_DESCRIPTION: 'Enable parallel processing',
            PARAM_ALIASES: ['--parallel', '-p'],
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_DEFAULT: False,
            PARAM_GROUP: 'Processing Options',
        },
        
        # Validation Options group
        {
            PARAM_NAME: 'strict',
            PARAM_DESCRIPTION: 'Enable strict validation mode',
            PARAM_ALIASES: ['--strict'],
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_DEFAULT: False,
            PARAM_GROUP: 'Validation Options',
        },
        {
            PARAM_NAME: 'max-errors',
            PARAM_DESCRIPTION: 'Maximum errors before stopping',
            PARAM_ALIASES: ['--max-errors'],
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_DEFAULT: 10,
            PARAM_GROUP: 'Validation Options',
        },
        {
            PARAM_NAME: 'skip-warnings',
            PARAM_DESCRIPTION: 'Skip validation warnings',
            PARAM_ALIASES: ['--skip-warnings'],
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_DEFAULT: False,
            PARAM_GROUP: 'Validation Options',
        },
    ]
    
    # Define command
    def process():
        """Process files with configured parameters."""
        # Get Input/Output parameters
        input_file = spafw37.get_config_str('input-file', default='input.txt')
        output_file = spafw37.get_config_str('output-file', default='output.txt')
        format_type = spafw37.get_config_str('format')
        
        # Get Processing parameters
        threads = spafw37.get_config_int('threads')
        batch_size = spafw37.get_config_int('batch-size')
        parallel = spafw37.get_config_bool('parallel', default=False)
        
        # Get Validation parameters
        strict = spafw37.get_config_bool('strict', default=False)
        max_errors = spafw37.get_config_int('max-errors')
        skip_warnings = spafw37.get_config_bool('skip-warnings', default=False)
        
        # Display configuration
        spafw37.output("Processing Configuration:")
        spafw37.output()
        spafw37.output("Input/Output:")
        spafw37.output(f"  Input:  {input_file}")
        spafw37.output(f"  Output: {output_file}")
        spafw37.output(f"  Format: {format_type}")
        spafw37.output()
        spafw37.output("Processing:")
        spafw37.output(f"  Threads:    {threads}")
        spafw37.output(f"  Batch size: {batch_size}")
        spafw37.output(f"  Parallel:   {parallel}")
        spafw37.output()
        spafw37.output("Validation:")
        spafw37.output(f"  Strict mode:    {strict}")
        spafw37.output(f"  Max errors:     {max_errors}")
        spafw37.output(f"  Skip warnings:  {skip_warnings}")
        spafw37.output()
        spafw37.output("Processing complete!")
    
    commands = [
        {
            COMMAND_NAME: 'process',
            COMMAND_DESCRIPTION: 'Process files with grouped parameters',
            COMMAND_ACTION: process,
        }
    ]
    
    spafw37.add_params(params)
    spafw37.add_commands(commands)


if __name__ == '__main__':
    setup()
    spafw37.output("Parameter Groups Example")
    spafw37.output("Parameters are organized into functional groups in help output\n")
    spafw37.run_cli()
