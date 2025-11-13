"""Command Dependencies Example - Required prerequisite commands.

This example shows:
- COMMAND_REQUIRE_BEFORE - ensure dependencies run first
- Enforcing prerequisites
- Complex dependency chains
"""

from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_REQUIRE_BEFORE,
)

# Command action functions

def setup_command():
    """Set up the environment."""
    spafw37.output("[SETUP] Initializing environment...")
    spafw37.output("        Creating config files...")
    spafw37.output("        Setup complete!")

def validate_command():
    """Validate configuration."""
    spafw37.output("[VALIDATE] Checking prerequisites...")
    spafw37.output("           Verifying dependencies...")
    spafw37.output("           Validation passed!")

def build_command():
    """Build the project."""
    spafw37.output("[BUILD] Compiling sources...")
    spafw37.output("        Linking libraries...")
    spafw37.output("        Build successful!")

def test_command():
    """Run tests."""
    spafw37.output("[TEST] Running test suite...")
    spafw37.output("       All tests passed!")

def deploy_command():
    """Deploy the application."""
    spafw37.output("[DEPLOY] Deploying application...")
    spafw37.output("         Deployment complete!")

# Define commands with dependencies
commands = [
    {
        COMMAND_NAME: 'setup',
        COMMAND_DESCRIPTION: 'Set up environment',
        COMMAND_ACTION: setup_command,
    },
    {
        COMMAND_NAME: 'validate',
        COMMAND_DESCRIPTION: 'Validate configuration',
        COMMAND_ACTION: validate_command,
        COMMAND_REQUIRE_BEFORE: ['setup'],  # Requires setup to run first
    },
    {
        COMMAND_NAME: 'build',
        COMMAND_DESCRIPTION: 'Build the project',
        COMMAND_ACTION: build_command,
        COMMAND_REQUIRE_BEFORE: ['validate'],  # Requires validation first
    },
    {
        COMMAND_NAME: 'test',
        COMMAND_DESCRIPTION: 'Run tests',
        COMMAND_ACTION: test_command,
        COMMAND_REQUIRE_BEFORE: ['build'],  # Requires build first
    },
    {
        COMMAND_NAME: 'deploy',
        COMMAND_DESCRIPTION: 'Deploy application',
        COMMAND_ACTION: deploy_command,
        COMMAND_REQUIRE_BEFORE: ['test'],  # Requires tests to pass first
    },
]

# Register commands
spafw37.add_commands(commands)
spafw37.set_app_name('commands-dependencies-demo')

if __name__ == '__main__':
    spafw37.run_cli()
