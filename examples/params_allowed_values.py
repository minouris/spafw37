"""Allowed Values Example - Restricting parameter values.

This example demonstrates PARAM_ALLOWED_VALUES for constraining
parameter values to a predefined set. Useful for:
- Environment names (dev, staging, production)
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Enumerated options (small, medium, large)
- Port selections (80, 443, 8080)

Run this example:
    python examples/params_allowed_values.py deploy --env production
    python examples/params_allowed_values.py deploy --env invalid  # Error!
    python examples/params_allowed_values.py start --port 8080
    python examples/params_allowed_values.py start --port 9999  # Error!
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
    PARAM_ALLOWED_VALUES,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)


def deploy_action():
    """Deploy to specified environment."""
    env = spafw37.get_param('environment')
    region = spafw37.get_param('region')
    
    spafw37.output(f"Deploying to environment: {env}")
    spafw37.output(f"Region: {region}")


def start_action():
    """Start server on specified port."""
    port = spafw37.get_param('port')
    size = spafw37.get_param('size')
    
    spafw37.output(f"Starting server on port {port}")
    spafw37.output(f"Instance size: {size}")


def setup():
    """Configure parameters and commands."""
    
    # Define parameters with allowed values
    params = [
        {
            PARAM_NAME: 'environment',
            PARAM_DESCRIPTION: 'Target environment',
            PARAM_ALIASES: ['--env', '-e'],
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALLOWED_VALUES: ['dev', 'staging', 'production'],
            PARAM_DEFAULT: 'dev',
        },
        {
            PARAM_NAME: 'region',
            PARAM_DESCRIPTION: 'Target region',
            PARAM_ALIASES: ['--region', '-r'],
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALLOWED_VALUES: ['north', 'south', 'east', 'west'],
            PARAM_DEFAULT: 'north',
        },
        {
            PARAM_NAME: 'port',
            PARAM_DESCRIPTION: 'Server port',
            PARAM_ALIASES: ['--port', '-p'],
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_ALLOWED_VALUES: [80, 443, 8080, 8443],
            PARAM_DEFAULT: 8080,
        },
        {
            PARAM_NAME: 'size',
            PARAM_DESCRIPTION: 'Instance size',
            PARAM_ALIASES: ['--size', '-s'],
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALLOWED_VALUES: ['small', 'medium', 'large', 'xlarge'],
            PARAM_DEFAULT: 'medium',
        },
    ]
    
    # Define commands
    commands = [
        {
            COMMAND_NAME: 'deploy',
            COMMAND_DESCRIPTION: 'Deploy application',
            COMMAND_ACTION: deploy_action,
        },
        {
            COMMAND_NAME: 'start',
            COMMAND_DESCRIPTION: 'Start server',
            COMMAND_ACTION: start_action,
        },
    ]
    
    spafw37.add_params(params)
    spafw37.add_commands(commands)


if __name__ == '__main__':
    setup()
    spafw37.run_cli()
