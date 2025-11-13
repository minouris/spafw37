"""
Required Parameters Example

Demonstrates globally required parameters using PARAM_REQUIRED.

Key concepts:
- PARAM_REQUIRED: Parameters that must always be set
- Framework validation before any command execution
- Clear error messages for missing parameters
- Required parameters vs. optional parameters

This example models an application where certain parameters must always
be provided regardless of which command is executed.
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_REQUIRED,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)


def setup():
    """Configure the application with globally required parameters."""
    
    # Define parameters with different requirement levels
    params = [
        # Globally required parameter - must always be set
        {
            PARAM_NAME: 'environment',
            PARAM_DESCRIPTION: 'Target environment (dev, staging, production)',
            PARAM_ALIASES: ['--env', '-e'],
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_REQUIRED: True,  # Must be provided for any command
        },
        
        # Another globally required parameter
        {
            PARAM_NAME: 'project',
            PARAM_DESCRIPTION: 'Project name',
            PARAM_ALIASES: ['--project', '-p'],
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_REQUIRED: True,  # Must always be set
        },
        
        # Optional parameters - not required
        {
            PARAM_NAME: 'region',
            PARAM_DESCRIPTION: 'Target region',
            PARAM_ALIASES: ['--region', '-r'],
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_REQUIRED: False,  # Optional
        },
        
        {
            PARAM_NAME: 'timeout',
            PARAM_DESCRIPTION: 'Operation timeout in seconds',
            PARAM_ALIASES: ['--timeout'],
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_REQUIRED: False,  # Optional with default
        },
    ]
    
    # Define commands that all need the globally required parameters
    def status():
        """Show project status."""
        env = spafw37.get_config_str('environment')
        project = spafw37.get_config_str('project')
        region = spafw37.get_config_str('region', default='us-east-1')
        timeout = spafw37.get_config_int('timeout', default=30)
        
        print(f"Project: {project}")
        print(f"Environment: {env}")
        print(f"Region: {region}")
        print(f"Timeout: {timeout}s")
        print()
        print("Status: Active")
    
    def deploy():
        """Deploy the project."""
        env = spafw37.get_config_str('environment')
        project = spafw37.get_config_str('project')
        region = spafw37.get_config_str('region', default='us-east-1')
        
        print(f"Deploying project '{project}' to {env} ({region})...")
        print("Deployment complete!")
    
    def validate():
        """Validate configuration."""
        env = spafw37.get_config_str('environment')
        project = spafw37.get_config_str('project')
        
        print(f"Validating project '{project}' in {env}...")
        print("Configuration valid!")
    
    commands = [
        {
            COMMAND_NAME: 'status',
            COMMAND_DESCRIPTION: 'Show project status',
            COMMAND_ACTION: status,
        },
        {
            COMMAND_NAME: 'deploy',
            COMMAND_DESCRIPTION: 'Deploy the project',
            COMMAND_ACTION: deploy,
        },
        {
            COMMAND_NAME: 'validate',
            COMMAND_DESCRIPTION: 'Validate configuration',
            COMMAND_ACTION: validate,
        },
    ]
    
    spafw37.add_params(params)
    spafw37.add_commands(commands)


if __name__ == '__main__':
    setup()
    print("Required Parameters Example")
    print("Demonstrates PARAM_REQUIRED - globally required parameters\n")
    spafw37.run_cli()
