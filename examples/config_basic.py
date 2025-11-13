"""Basic Configuration Example - Runtime config access.

This example shows:
- Getting config values
- Setting config values
- Runtime configuration state
"""

from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)

def show_config():
    """Display current configuration."""
    print("Configuration Demo")
    print("=" * 40)
    
    # Set some config values
    spafw37.set_config_value('app-name', 'MyApp')
    spafw37.set_config_value('version', '1.0.0')
    spafw37.set_config_value('debug', True)
    
    # Get config values
    app_name = spafw37.get_config_str('app-name')
    version = spafw37.get_config_str('version')
    debug = spafw37.get_config_bool('debug')
    
    print(f"Application: {app_name}")
    print(f"Version: {version}")
    print(f"Debug mode: {debug}")

def modify_config():
    """Modify configuration values."""
    print("\nModifying configuration...")
    
    spafw37.set_config_value('debug', False)
    spafw37.set_config_value('max-connections', 100)
    
    debug = spafw37.get_config_bool('debug')
    max_conn = spafw37.get_config_int('max-connections')
    
    print(f"Debug mode: {debug}")
    print(f"Max connections: {max_conn}")

# Define commands
commands = [
    {
        COMMAND_NAME: 'show',
        COMMAND_DESCRIPTION: 'Show configuration',
        COMMAND_ACTION: show_config,
    },
    {
        COMMAND_NAME: 'modify',
        COMMAND_DESCRIPTION: 'Modify configuration',
        COMMAND_ACTION: modify_config,
    },
]

# Register commands
spafw37.add_commands(commands)
spafw37.set_app_name('config-basic-demo')

if __name__ == '__main__':
    spafw37.run_cli()
