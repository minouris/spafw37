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
        env = spafw37.get_param('environment')
        project = spafw37.get_param('project')
        region = spafw37.get_param('region', default='us-east-1')
        timeout = spafw37.get_param('timeout', default=30)
        
        spafw37.output(f"Project: {project}")
        spafw37.output(f"Environment: {env}")
        spafw37.output(f"Region: {region}")
        spafw37.output(f"Timeout: {timeout}s")
        spafw37.output()
        spafw37.output("Status: Active")
    
    def deploy():
        """Deploy the project."""
        env = spafw37.get_param('environment')
        project = spafw37.get_param('project')
        region = spafw37.get_param('region', default='us-east-1')
        
        spafw37.output(f"Deploying project '{project}' to {env} ({region})...")
        spafw37.output("Deployment complete!")
    
    def validate():
        """Validate configuration."""
        env = spafw37.get_param('environment')
        project = spafw37.get_param('project')
        
        spafw37.output(f"Validating project '{project}' in {env}...")
        spafw37.output("Configuration valid!")
    
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
    spafw37.output("Required Parameters Example")
    spafw37.output("Demonstrates PARAM_REQUIRED - globally required parameters\n")
    spafw37.run_cli()
