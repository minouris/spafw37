"""Basic Configuration Example - Runtime config access.

This example shows:
- Getting config values with get_param()
- Setting config values with set_param()
- Runtime configuration state
- Runtime-only parameters for temporary state
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_TOGGLE,
    PARAM_RUNTIME_ONLY,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)

# Define runtime-only parameters for this demo
params = [
    {
        PARAM_NAME: 'app-name',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True,
    },
    {
        PARAM_NAME: 'version',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True,
    },
    {
        PARAM_NAME: 'debug',
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_RUNTIME_ONLY: True,
    },
    {
        PARAM_NAME: 'max-connections',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_RUNTIME_ONLY: True,
    },
]

def show_config():
    """Display current configuration."""
    spafw37.output("Configuration Demo")
    spafw37.output("=" * 40)
    
    # Set some config values
    spafw37.set_param(param_name='app-name', value='MyApp')
    spafw37.set_param(param_name='version', value='1.0.0')
    spafw37.set_param(param_name='debug', value=True)
    
    # Get config values
    app_name = spafw37.get_param('app-name')
    version = spafw37.get_param('version')
    debug = spafw37.get_param('debug')
    
    spafw37.output(f"Application: {app_name}")
    spafw37.output(f"Version: {version}")
    spafw37.output(f"Debug mode: {debug}")

def modify_config():
    """Modify configuration values."""
    spafw37.output("\nModifying configuration...")
    
    spafw37.set_param(param_name='debug', value=False)
    spafw37.set_param(param_name='max-connections', value=100)
    
    debug = spafw37.get_param('debug')
    max_conn = spafw37.get_param('max-connections')
    
    spafw37.output(f"Debug mode: {debug}")
    spafw37.output(f"Max connections: {max_conn}")

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

# Register parameters and commands
spafw37.add_params(params)
spafw37.add_commands(commands)
spafw37.set_app_name('config-basic-demo')

if __name__ == '__main__':
    spafw37.run_cli()
