"""CLI argument override behaviour demonstration.

This example shows:
- How CLI arguments override prompts
- Prompt appears only when parameter is not provided via CLI
- Combining CLI arguments with interactive prompts

Usage:
    # All prompts appear (no CLI args):
    python params_prompt_cli_override.py deploy
    
    # Skip environment prompt (CLI arg provided):
    python params_prompt_cli_override.py --environment production deploy
    
    # Skip both prompts (all CLI args provided):
    python params_prompt_cli_override.py --environment production --confirm yes deploy

**Added in v1.1.0**
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_ALIASES,
    PARAM_DESCRIPTION,
    PARAM_PROMPT,
    PARAM_PROMPT_TIMING,
    PARAM_ALLOWED_VALUES,
    PROMPT_ON_START,
    PROMPT_ON_COMMAND,
    PROMPT_ON_COMMANDS,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)


def deploy_command():
    """Deployment command."""
    environment = spafw37.get_param('environment')
    confirmation = spafw37.get_param('confirmation')
    
    print(f'\nDeployment configuration:')
    print(f'  Environment: {environment}')
    print(f'  Confirmed: {confirmation}')
    
    if confirmation.lower() == 'yes':
        print(f'\n✓ Deploying to {environment}...')
    else:
        print('\n✗ Deployment cancelled')


if __name__ == '__main__':
    # Parameter with prompt at start
    # Prompt skipped if --environment provided via CLI
    spafw37.add_params([{
        PARAM_NAME: 'environment',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--environment', '--env', '-e'],
        PARAM_DESCRIPTION: 'Deployment environment',
        PARAM_PROMPT: 'Select environment (development/staging/production): ',
        PARAM_PROMPT_TIMING: PROMPT_ON_START,
        PARAM_ALLOWED_VALUES: ['development', 'staging', 'production'],
    }])
    
    # Parameter with prompt before command
    # Prompt skipped if --confirm provided via CLI
    spafw37.add_params([{
        PARAM_NAME: 'confirmation',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--confirm', '-c'],
        PARAM_DESCRIPTION: 'Deployment confirmation',
        PARAM_PROMPT: 'Proceed with deployment? (yes/no): ',
        PARAM_PROMPT_TIMING: PROMPT_ON_COMMAND,
        PROMPT_ON_COMMANDS: ['deploy'],
    }])
    
    # Define command
    spafw37.add_commands([{
        COMMAND_NAME: 'deploy',
        COMMAND_DESCRIPTION: 'Deploy application to environment',
        COMMAND_ACTION: deploy_command,
    }])
    
    # Run CLI
    # CLI arguments take precedence over prompts
    # Only missing parameters will be prompted for
    spafw37.run_cli()
