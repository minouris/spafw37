"""
Command Visibility Example

Demonstrates command visibility control using COMMAND_FRAMEWORK and COMMAND_EXCLUDE_HELP.

Commands can be hidden from help displays or marked as framework commands to distinguish
between application functionality and internal utilities.

Key Concepts:
- COMMAND_FRAMEWORK: Marks command as framework-internal (vs application command)
- COMMAND_EXCLUDE_HELP: Hides command from help listing (but still executable)
- Commands remain fully functional even when hidden
- Useful for deprecated, internal, or advanced commands

Usage Examples:
    # Show help - only visible commands listed
    python commands_visibility.py --help
    
    # Run visible commands
    python commands_visibility.py build
    python commands_visibility.py deploy
    
    # Run hidden commands - still works, just not in help
    python commands_visibility.py internal-diagnostics
    python commands_visibility.py legacy-process
    
    # Framework command (hidden)
    python commands_visibility.py framework-init
"""

from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_FRAMEWORK,
    COMMAND_EXCLUDE_HELP,
)


def setup():
    """Configure commands with different visibility levels."""
    
    # Visible application commands
    def build():
        """Build the application."""
        spafw37.output("Building application...")
        spafw37.output("  Compiling sources")
        spafw37.output("  Linking libraries")
        spafw37.output("Build complete!")
        spafw37.output()
    
    def test():
        """Run tests."""
        spafw37.output("Running tests...")
        spafw37.output("  Unit tests: 45 passed")
        spafw37.output("  Integration tests: 12 passed")
        spafw37.output("All tests passed!")
        spafw37.output()
    
    def deploy():
        """Deploy the application."""
        spafw37.output("Deploying application...")
        spafw37.output("  Packaging artifacts")
        spafw37.output("  Uploading to server")
        spafw37.output("Deployment complete!")
        spafw37.output()
    
    # Hidden internal/diagnostic command
    def internal_diagnostics():
        """Run internal diagnostics (hidden from help)."""
        spafw37.output("[INTERNAL] Running diagnostics...")
        spafw37.output("  System health: OK")
        spafw37.output("  Memory usage: 45%")
        spafw37.output("  Disk space: 230GB available")
        spafw37.output("  Network: Connected")
        spafw37.output("Diagnostics complete!")
        spafw37.output()
    
    # Hidden deprecated command
    def legacy_process():
        """Legacy processing command (deprecated, hidden from help)."""
        spafw37.output("[DEPRECATED] Running legacy process...")
        spafw37.output("  This command is deprecated")
        spafw37.output("  Please use 'build' instead")
        spafw37.output("Legacy process complete!")
        spafw37.output()
    
    # Hidden advanced command
    def debug_rebuild():
        """Advanced debug rebuild (hidden from help)."""
        spafw37.output("[ADVANCED] Debug rebuild...")
        spafw37.output("  Building with debug symbols")
        spafw37.output("  Verbose logging enabled")
        spafw37.output("  Source maps generated")
        spafw37.output("Debug rebuild complete!")
        spafw37.output()
    
    # Framework command (internal utility)
    def framework_init():
        """Framework initialization (hidden framework command)."""
        spafw37.output("[FRAMEWORK] Initializing framework...")
        spafw37.output("  Loading core modules")
        spafw37.output("  Registering plugins")
        spafw37.output("  Setting up environment")
        spafw37.output("Framework initialized!")
        spafw37.output()
    
    commands = [
        # Visible application commands (appear in help)
        {
            COMMAND_NAME: 'build',
            COMMAND_DESCRIPTION: 'Build the application',
            COMMAND_ACTION: build,
        },
        {
            COMMAND_NAME: 'test',
            COMMAND_DESCRIPTION: 'Run tests',
            COMMAND_ACTION: test,
        },
        {
            COMMAND_NAME: 'deploy',
            COMMAND_DESCRIPTION: 'Deploy the application',
            COMMAND_ACTION: deploy,
        },
        
        # Hidden from help - internal diagnostic command
        {
            COMMAND_NAME: 'internal-diagnostics',
            COMMAND_DESCRIPTION: 'Run internal diagnostics (hidden)',
            COMMAND_ACTION: internal_diagnostics,
            COMMAND_EXCLUDE_HELP: True,  # Not shown in help
        },
        
        # Hidden from help - deprecated command
        {
            COMMAND_NAME: 'legacy-process',
            COMMAND_DESCRIPTION: 'Legacy processing (deprecated)',
            COMMAND_ACTION: legacy_process,
            COMMAND_EXCLUDE_HELP: True,  # Not shown in help
        },
        
        # Hidden from help - advanced command
        {
            COMMAND_NAME: 'debug-rebuild',
            COMMAND_DESCRIPTION: 'Advanced debug rebuild',
            COMMAND_ACTION: debug_rebuild,
            COMMAND_EXCLUDE_HELP: True,  # Not shown in help
        },
        
        # Framework command (internal utility, not application functionality)
        {
            COMMAND_NAME: 'framework-init',
            COMMAND_DESCRIPTION: 'Framework initialization',
            COMMAND_ACTION: framework_init,
            COMMAND_FRAMEWORK: True,  # Marked as framework command
            COMMAND_EXCLUDE_HELP: True,  # Also hidden from help
        },
    ]
    
    spafw37.add_commands(commands)


if __name__ == '__main__':
    setup()
    spafw37.output("Command Visibility Example")
    spafw37.output("Demonstrates COMMAND_FRAMEWORK and COMMAND_EXCLUDE_HELP\n")
    spafw37.run_cli()
