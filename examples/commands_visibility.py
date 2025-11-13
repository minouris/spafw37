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
        print("Building application...")
        print("  Compiling sources")
        print("  Linking libraries")
        print("Build complete!")
        print()
    
    def test():
        """Run tests."""
        print("Running tests...")
        print("  Unit tests: 45 passed")
        print("  Integration tests: 12 passed")
        print("All tests passed!")
        print()
    
    def deploy():
        """Deploy the application."""
        print("Deploying application...")
        print("  Packaging artifacts")
        print("  Uploading to server")
        print("Deployment complete!")
        print()
    
    # Hidden internal/diagnostic command
    def internal_diagnostics():
        """Run internal diagnostics (hidden from help)."""
        print("[INTERNAL] Running diagnostics...")
        print("  System health: OK")
        print("  Memory usage: 45%")
        print("  Disk space: 230GB available")
        print("  Network: Connected")
        print("Diagnostics complete!")
        print()
    
    # Hidden deprecated command
    def legacy_process():
        """Legacy processing command (deprecated, hidden from help)."""
        print("[DEPRECATED] Running legacy process...")
        print("  This command is deprecated")
        print("  Please use 'build' instead")
        print("Legacy process complete!")
        print()
    
    # Hidden advanced command
    def debug_rebuild():
        """Advanced debug rebuild (hidden from help)."""
        print("[ADVANCED] Debug rebuild...")
        print("  Building with debug symbols")
        print("  Verbose logging enabled")
        print("  Source maps generated")
        print("Debug rebuild complete!")
        print()
    
    # Framework command (internal utility)
    def framework_init():
        """Framework initialization (hidden framework command)."""
        print("[FRAMEWORK] Initializing framework...")
        print("  Loading core modules")
        print("  Registering plugins")
        print("  Setting up environment")
        print("Framework initialized!")
        print()
    
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
    print("Command Visibility Example")
    print("Demonstrates COMMAND_FRAMEWORK and COMMAND_EXCLUDE_HELP\n")
    spafw37.run_cli()
