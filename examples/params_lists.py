"""List Parameters Example - Parameters that accept multiple values.

This example shows:
- List parameters
- Collecting multiple values
- Processing list parameter values
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_LIST,
    PARAM_DEFAULT,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)

# Define parameters with lists
params = [
    {
        PARAM_NAME: 'output-dir',
        PARAM_DESCRIPTION: 'Output directory',
        PARAM_ALIASES: ['--output', '-o'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DEFAULT: './output',
    },
    # List parameter - can be specified multiple times
    {
        PARAM_NAME: 'files',
        PARAM_DESCRIPTION: 'Files to process (can be specified multiple times)',
        PARAM_ALIASES: ['--file', '-f'],
        PARAM_TYPE: PARAM_TYPE_LIST,
        PARAM_DEFAULT: [],
    },
    # List parameter - tags
    {
        PARAM_NAME: 'tags',
        PARAM_DESCRIPTION: 'Tags to apply',
        PARAM_ALIASES: ['--tag', '-t'],
        PARAM_TYPE: PARAM_TYPE_LIST,
        PARAM_DEFAULT: [],
    },
]

def process_command():
    """Process with list parameters."""
    output_dir = spafw37.get_config_str('output-dir')
    files = spafw37.get_config_list('files')
    tags = spafw37.get_config_list('tags')
    
    spafw37.output(f"Output directory: {output_dir}")
    spafw37.output()
    
    if not files:
        spafw37.output("No files specified. Use --file or -f to specify files.")
        return
    
    spafw37.output(f"Processing {len(files)} file(s):")
    for file in files:
        spafw37.output(f"  - {file}")
    
    if tags:
        spafw37.output(f"\nApplying tags: {', '.join(tags)}")
    
    spafw37.output()
    for i, file in enumerate(files, 1):
        spafw37.output(f"[{i}/{len(files)}] Processing {file}...")
        spafw37.output(f"         Writing to {output_dir}/")
        if tags:
            spafw37.output(f"         Tags: {', '.join(tags)}")
    
    spafw37.output(f"\nCompleted! Processed {len(files)} files to {output_dir}")

# Define command
commands = [
    {
        COMMAND_NAME: 'process',
        COMMAND_DESCRIPTION: 'Process multiple files with list parameters',
        COMMAND_ACTION: process_command,
    }
]

# Register parameters and commands
spafw37.add_params(params)
spafw37.add_commands(commands)
spafw37.set_app_name('params-lists-demo')

if __name__ == '__main__':
    spafw37.run_cli()
