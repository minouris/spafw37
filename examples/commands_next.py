"""Command Next Queuing Example - Dynamic command chaining.

This example shows:
- COMMAND_NEXT_COMMANDS - automatically queue follow-up commands
- Dynamic command flow
- Command chaining
"""

from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_NEXT_COMMANDS,
)

# Command action functions

def start_command():
    """Start the workflow."""
    spafw37.output("[START] Workflow initiated")
    spafw37.output("        Proceeding to authentication...")

def authenticate_command():
    """Authenticate user."""
    spafw37.output("[AUTH] Authenticating...")
    spafw37.output("       Authentication successful!")
    spafw37.output("       Proceeding to data fetch...")

def fetch_data_command():
    """Fetch data from source."""
    spafw37.output("[FETCH] Fetching data...")
    spafw37.output("        Data retrieved!")
    spafw37.output("        Proceeding to processing...")

def process_data_command():
    """Process the fetched data."""
    spafw37.output("[PROCESS] Processing data...")
    spafw37.output("          Processing complete!")
    spafw37.output("          Proceeding to save...")

def save_results_command():
    """Save processed results."""
    spafw37.output("[SAVE] Saving results...")
    spafw37.output("       Results saved!")
    spafw37.output("       Proceeding to notification...")

def notify_command():
    """Send notification."""
    spafw37.output("[NOTIFY] Sending notification...")
    spafw37.output("         Notification sent!")
    spafw37.output("         Workflow complete!")

# Define commands with next-command chaining
commands = [
    {
        COMMAND_NAME: 'start',
        COMMAND_DESCRIPTION: 'Start workflow',
        COMMAND_ACTION: start_command,
        COMMAND_NEXT_COMMANDS: ['authenticate'],  # Auto-queue authenticate
    },
    {
        COMMAND_NAME: 'authenticate',
        COMMAND_DESCRIPTION: 'Authenticate user',
        COMMAND_ACTION: authenticate_command,
        COMMAND_NEXT_COMMANDS: ['fetch-data'],  # Auto-queue fetch-data
    },
    {
        COMMAND_NAME: 'fetch-data',
        COMMAND_DESCRIPTION: 'Fetch data',
        COMMAND_ACTION: fetch_data_command,
        COMMAND_NEXT_COMMANDS: ['process-data'],  # Auto-queue process-data
    },
    {
        COMMAND_NAME: 'process-data',
        COMMAND_DESCRIPTION: 'Process data',
        COMMAND_ACTION: process_data_command,
        COMMAND_NEXT_COMMANDS: ['save-results'],  # Auto-queue save-results
    },
    {
        COMMAND_NAME: 'save-results',
        COMMAND_DESCRIPTION: 'Save results',
        COMMAND_ACTION: save_results_command,
        COMMAND_NEXT_COMMANDS: ['notify'],  # Auto-queue notify
    },
    {
        COMMAND_NAME: 'notify',
        COMMAND_DESCRIPTION: 'Send notification',
        COMMAND_ACTION: notify_command,
    },
]

# Register commands
spafw37.add_commands(commands)
spafw37.set_app_name('commands-next-demo')

if __name__ == '__main__':
    spafw37.run_cli()
