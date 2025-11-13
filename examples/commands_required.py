"""
Command Required Parameters Example

Demonstrates COMMAND_REQUIRED_PARAMS - parameters required by specific commands.

COMMAND_REQUIRED_PARAMS is a list on a command definition specifying parameters
that must be set when that specific command runs. Different commands can have
different parameter requirements.

This is different from PARAM_REQUIRED which applies globally to all commands.

Key Concepts:
- COMMAND_REQUIRED_PARAMS is a list of parameter names
- Each command can have different requirements
- Framework validates requirements before running the command
- Parameters not in COMMAND_REQUIRED_PARAMS are optional for that command

Usage Examples:
    # Show help
    python commands_required.py --help
    
    # status command has no additional requirements
    python commands_required.py status
    
    # deploy command requires api-key and instance-count
    python commands_required.py deploy --api-key abc123 --instance-count 3
    
    # backup command requires backup-path
    python commands_required.py backup --backup-path /backups/app
    
    # Missing required params causes validation error
    python commands_required.py deploy  # Error: missing api-key and instance-count
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_DEFAULT,
    PARAM_TYPE,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_REQUIRED_PARAMS,
)


def setup():
    """Configure parameters and commands."""
    
    # Define parameters - none are globally required
    params = [
        {
            PARAM_NAME: 'environment',
            PARAM_DESCRIPTION: 'Target environment (dev, staging, production)',
            PARAM_ALIASES: ['--env', '-e'],
            PARAM_DEFAULT: 'dev',
        },
        {
            PARAM_NAME: 'api-key',
            PARAM_DESCRIPTION: 'API key for authentication',
            PARAM_ALIASES: ['--key', '-k'],
        },
        {
            PARAM_NAME: 'instance-count',
            PARAM_DESCRIPTION: 'Number of instances to deploy',
            PARAM_ALIASES: ['--count', '-c'],
            PARAM_TYPE: int,
        },
        {
            PARAM_NAME: 'backup-path',
            PARAM_DESCRIPTION: 'Path where backup should be stored',
            PARAM_ALIASES: ['--backup', '-b'],
        },
        {
            PARAM_NAME: 'region',
            PARAM_DESCRIPTION: 'Target region',
            PARAM_ALIASES: ['-r'],
            PARAM_DEFAULT: 'us-east-1',
        },
    ]
    
    # Define commands with varying parameter requirements
    def status():
        """Show deployment status - no special requirements."""
        env = spafw37.get_config_str('environment')
        region = spafw37.get_config_str('region')
        
        spafw37.output(f"Status for {env} ({region}):")
        spafw37.output("  Services: Running")
        spafw37.output("  Health: OK")
    
    def deploy():
        """Deploy application - requires api-key and instance-count."""
        env = spafw37.get_config_str('environment')
        api_key = spafw37.get_config_str('api-key')
        instances = spafw37.get_config_int('instance-count')
        region = spafw37.get_config_str('region')
        
        spafw37.output(f"Deploying to {env} ({region})...")
        spafw37.output(f"API Key: {api_key[:8]}...")
        spafw37.output(f"Instance count: {instances}")
        spafw37.output("Deployment complete!")
    
    def backup():
        """Backup current deployment - requires backup-path."""
        env = spafw37.get_config_str('environment')
        backup_path = spafw37.get_config_str('backup-path')
        region = spafw37.get_config_str('region')
        
        spafw37.output(f"Backing up {env} ({region})...")
        spafw37.output(f"Backup location: {backup_path}")
        spafw37.output("Backup complete!")
    
    commands = [
        # status has no additional requirements
        {
            COMMAND_NAME: 'status',
            COMMAND_DESCRIPTION: 'Show deployment status',
            COMMAND_ACTION: status,
            # No COMMAND_REQUIRED_PARAMS - all params optional
        },
        
        # deploy requires api-key and instance-count
        {
            COMMAND_NAME: 'deploy',
            COMMAND_DESCRIPTION: 'Deploy application',
            COMMAND_ACTION: deploy,
            COMMAND_REQUIRED_PARAMS: ['api-key', 'instance-count'],
        },
        
        # backup requires backup-path
        {
            COMMAND_NAME: 'backup',
            COMMAND_DESCRIPTION: 'Backup current deployment',
            COMMAND_ACTION: backup,
            COMMAND_REQUIRED_PARAMS: ['backup-path'],
        },
    ]
    
    spafw37.add_params(params)
    spafw37.add_commands(commands)


if __name__ == '__main__':
    setup()
    spafw37.output("Command Required Parameters Example")
    spafw37.output("Demonstrates COMMAND_REQUIRED_PARAMS - command-specific requirements\n")
    spafw37.run_cli()
