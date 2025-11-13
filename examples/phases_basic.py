"""
Basic Phases Example

Demonstrates using the default phase system for organizing command execution.

Key concepts:
- Default phase order: SETUP → CLEANUP → EXECUTION → TEARDOWN → END
- Assigning commands to phases with COMMAND_PHASE
- Automatic phase-based execution ordering
- Dependencies within phases

Default phases:
- PHASE_SETUP: Initialize resources (database, config, etc.)
- PHASE_CLEANUP: Prepare environment (clean temp files, etc.)
- PHASE_EXECUTION: Main application logic (default for commands)
- PHASE_TEARDOWN: Release resources (close connections, etc.)
- PHASE_END: Final reporting (notifications, summaries, etc.)
"""

from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_PHASE,
    COMMAND_REQUIRE_BEFORE,
)
from spafw37.constants.phase import (
    PHASE_SETUP,
    PHASE_CLEANUP,
    PHASE_EXECUTION,
    PHASE_TEARDOWN,
    PHASE_END,
)


def setup():
    """Configure the application with phase-organized commands."""
    
    # PHASE_SETUP: Resource initialization
    def connect_db():
        """Connect to database."""
        spafw37.output("[SETUP] Connecting to database...")
    
    def load_config():
        """Load configuration."""
        spafw37.output("[SETUP] Loading configuration...")
    
    def verify_setup():
        """Verify setup completed."""
        spafw37.output("[SETUP] Verifying setup complete")
    
    # PHASE_CLEANUP: Environment preparation
    def clean_temp():
        """Clean temporary files."""
        spafw37.output("[CLEANUP] Cleaning temporary files...")
    
    # PHASE_EXECUTION: Main logic
    def process():
        """Process data."""
        spafw37.output("[EXECUTION] Processing data...")
    
    def save():
        """Save results."""
        spafw37.output("[EXECUTION] Saving results...")
    
    # PHASE_TEARDOWN: Resource cleanup
    def close_db():
        """Close database."""
        spafw37.output("[TEARDOWN] Closing database connection...")
    
    # PHASE_END: Final reporting
    def summary():
        """Generate summary."""
        spafw37.output("[END] Execution complete!")
    
    commands = [
        # Setup phase
        {
            COMMAND_NAME: 'connect-db',
            COMMAND_DESCRIPTION: 'Connect to database',
            COMMAND_ACTION: connect_db,
            COMMAND_PHASE: PHASE_SETUP,
        },
        {
            COMMAND_NAME: 'load-config',
            COMMAND_DESCRIPTION: 'Load configuration',
            COMMAND_ACTION: load_config,
            COMMAND_PHASE: PHASE_SETUP,
        },
        {
            COMMAND_NAME: 'verify',
            COMMAND_DESCRIPTION: 'Verify setup',
            COMMAND_ACTION: verify_setup,
            COMMAND_PHASE: PHASE_SETUP,
            COMMAND_REQUIRE_BEFORE: ['connect-db', 'load-config'],
        },
        # Cleanup phase
        {
            COMMAND_NAME: 'clean',
            COMMAND_DESCRIPTION: 'Clean temporary files',
            COMMAND_ACTION: clean_temp,
            COMMAND_PHASE: PHASE_CLEANUP,
        },
        # Execution phase (main logic)
        {
            COMMAND_NAME: 'process',
            COMMAND_DESCRIPTION: 'Process data',
            COMMAND_ACTION: process,
            COMMAND_PHASE: PHASE_EXECUTION,
        },
        {
            COMMAND_NAME: 'save',
            COMMAND_DESCRIPTION: 'Save results',
            COMMAND_ACTION: save,
            COMMAND_PHASE: PHASE_EXECUTION,
            COMMAND_REQUIRE_BEFORE: ['process'],
        },
        # Teardown phase
        {
            COMMAND_NAME: 'close-db',
            COMMAND_DESCRIPTION: 'Close database',
            COMMAND_ACTION: close_db,
            COMMAND_PHASE: PHASE_TEARDOWN,
        },
        # End phase
        {
            COMMAND_NAME: 'summary',
            COMMAND_DESCRIPTION: 'Show summary',
            COMMAND_ACTION: summary,
            COMMAND_PHASE: PHASE_END,
        },
    ]
    
    spafw37.add_commands(commands)


if __name__ == '__main__':
    setup()
    # Commands execute in phase order automatically:
    # SETUP → CLEANUP → EXECUTION → TEARDOWN → END
    spafw37.run_cli()
