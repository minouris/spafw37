"""Command Sequencing Example - Controlling command execution order.

This example shows:
- COMMAND_GOES_AFTER - specify commands that should run before this one
- Natural ordering of commands
- Sequential execution flow
"""

from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_GOES_AFTER,
)

# Command action functions

def prepare_command():
    """Prepare the environment."""
    spafw37.output("[1] PREPARE: Setting up environment...")
    spafw37.output("    Creating directories...")
    spafw37.output("    Ready!")

def download_command():
    """Download data."""
    spafw37.output("[2] DOWNLOAD: Fetching data...")
    spafw37.output("    Connecting...")
    spafw37.output("    Downloaded!")

def process_command():
    """Process the data."""
    spafw37.output("[3] PROCESS: Processing data...")
    spafw37.output("    Transforming...")
    spafw37.output("    Processed!")

def finalize_command():
    """Finalize and clean up."""
    spafw37.output("[4] FINALIZE: Cleaning up...")
    spafw37.output("    Removing temporary files...")
    spafw37.output("    Done!")

# Define commands with sequencing
commands = [
    {
        COMMAND_NAME: 'prepare',
        COMMAND_DESCRIPTION: 'Prepare environment',
        COMMAND_ACTION: prepare_command,
    },
    {
        COMMAND_NAME: 'download',
        COMMAND_DESCRIPTION: 'Download data',
        COMMAND_ACTION: download_command,
        COMMAND_GOES_AFTER: ['prepare'],  # Runs after prepare
    },
    {
        COMMAND_NAME: 'process',
        COMMAND_DESCRIPTION: 'Process data',
        COMMAND_ACTION: process_command,
        COMMAND_GOES_AFTER: ['download'],  # Runs after download
    },
    {
        COMMAND_NAME: 'finalize',
        COMMAND_DESCRIPTION: 'Finalize and clean up',
        COMMAND_ACTION: finalize_command,
        COMMAND_GOES_AFTER: ['process'],  # Runs after process
    },
]

# Register commands
spafw37.add_commands(commands)
spafw37.set_app_name('commands-sequencing-demo')

if __name__ == '__main__':
    spafw37.run_cli()
