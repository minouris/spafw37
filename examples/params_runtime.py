"""Runtime-Only Parameters Example - Internal state parameters.

This example shows:
- Runtime-only parameters (PARAM_RUNTIME_ONLY)
- Shared state between commands
- Parameters not exposed to CLI
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_TEXT,
    PARAM_RUNTIME_ONLY,
    PARAM_DEFAULT,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_NEXT_COMMANDS,
)

# Define runtime-only parameters for internal state
params = [
    # Runtime-only parameters - not accessible from command line
    {
        PARAM_NAME: 'session-id',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True,
    },
    {
        PARAM_NAME: 'items-processed',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_RUNTIME_ONLY: True,
        PARAM_DEFAULT: 0,
    },
    {
        PARAM_NAME: 'total-size',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_RUNTIME_ONLY: True,
        PARAM_DEFAULT: 0,
    },
]

def init_command():
    """Initialize session with runtime state."""
    import uuid
    
    # Set runtime-only parameter values
    session_id = str(uuid.uuid4())
    spafw37.set_config_value('session-id', session_id)
    spafw37.set_config_value('items-processed', 0)
    spafw37.set_config_value('total-size', 0)
    
    print(f"Session initialized: {session_id}")
    print("Ready to process items")

def process_item_command():
    """Process an item and update runtime state."""
    import random
    
    # Read current state
    session_id = spafw37.get_config_str('session-id')
    items_processed = spafw37.get_config_int('items-processed')
    total_size = spafw37.get_config_int('total-size')
    
    # Simulate processing
    item_size = random.randint(100, 1000)
    items_processed += 1
    total_size += item_size
    
    # Update state
    spafw37.set_config_value('items-processed', items_processed)
    spafw37.set_config_value('total-size', total_size)
    
    print(f"[Session: {session_id}] Processed item {items_processed} ({item_size} bytes)")

def summary_command():
    """Display summary using runtime state."""
    session_id = spafw37.get_config_str('session-id')
    items_processed = spafw37.get_config_int('items-processed')
    total_size = spafw37.get_config_int('total-size')
    
    print()
    print("=" * 50)
    print(f"Session: {session_id}")
    print(f"Items processed: {items_processed}")
    print(f"Total size: {total_size} bytes")
    print("=" * 50)

# Define commands that share runtime state
commands = [
    {
        COMMAND_NAME: 'init',
        COMMAND_DESCRIPTION: 'Initialize processing session',
        COMMAND_ACTION: init_command,
    },
    {
        COMMAND_NAME: 'process-item',
        COMMAND_DESCRIPTION: 'Process an item (can be run multiple times)',
        COMMAND_ACTION: process_item_command,
    },
    {
        COMMAND_NAME: 'summary',
        COMMAND_DESCRIPTION: 'Show processing summary',
        COMMAND_ACTION: summary_command,
    },
]

# Register parameters and commands
spafw37.add_params(params)
spafw37.add_commands(commands)
spafw37.set_app_name('params-runtime-demo')

if __name__ == '__main__':
    spafw37.run_cli()
