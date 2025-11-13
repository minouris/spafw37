"""
Custom Phase Order Example

Demonstrates reordering phases with set_phases_order() to control execution flow.

Key concepts:
- Customizing phase execution order with set_phases_order()
- Placing cleanup before setup for special workflows
- Controlling when teardown happens relative to other phases
- Understanding phase order impact on command execution

This example shows a data pipeline that:
1. Cleans old data first (CLEANUP)
2. Sets up fresh environment (SETUP)
3. Processes data (EXECUTION)
4. Tears down resources (TEARDOWN)
5. Reports results (END)
"""

from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_PHASE,
)
from spafw37.constants.phase import (
    PHASE_SETUP,
    PHASE_CLEANUP,
    PHASE_EXECUTION,
    PHASE_TEARDOWN,
    PHASE_END,
)


def setup():
    """Configure the application with custom phase ordering."""
    
    # Define phase-specific actions
    def cleanup_old_data():
        """Clean old data files."""
        spafw37.output("[1. CLEANUP] Removing old data files...")
    
    def setup_environment():
        """Set up fresh environment."""
        spafw37.output("[2. SETUP] Setting up fresh environment...")
    
    def process_data():
        """Process the data."""
        spafw37.output("[3. EXECUTION] Processing data...")
    
    def teardown_resources():
        """Tear down resources."""
        spafw37.output("[4. TEARDOWN] Releasing resources...")
    
    def send_report():
        """Send final report."""
        spafw37.output("[5. END] Sending completion report...")
    
    commands = [
        {
            COMMAND_NAME: 'cleanup',
            COMMAND_DESCRIPTION: 'Clean old data',
            COMMAND_ACTION: cleanup_old_data,
            COMMAND_PHASE: PHASE_CLEANUP,
        },
        {
            COMMAND_NAME: 'setup',
            COMMAND_DESCRIPTION: 'Setup environment',
            COMMAND_ACTION: setup_environment,
            COMMAND_PHASE: PHASE_SETUP,
        },
        {
            COMMAND_NAME: 'process',
            COMMAND_DESCRIPTION: 'Process data',
            COMMAND_ACTION: process_data,
            COMMAND_PHASE: PHASE_EXECUTION,
        },
        {
            COMMAND_NAME: 'teardown',
            COMMAND_DESCRIPTION: 'Teardown resources',
            COMMAND_ACTION: teardown_resources,
            COMMAND_PHASE: PHASE_TEARDOWN,
        },
        {
            COMMAND_NAME: 'report',
            COMMAND_DESCRIPTION: 'Send report',
            COMMAND_ACTION: send_report,
            COMMAND_PHASE: PHASE_END,
        },
    ]
    
    # Set custom phase order: CLEANUP first, then default order
    # Default order: [SETUP, CLEANUP, EXECUTION, TEARDOWN, END]
    # Custom order: [CLEANUP, SETUP, EXECUTION, TEARDOWN, END]
    custom_order = [
        PHASE_CLEANUP,    # Run cleanup FIRST
        PHASE_SETUP,      # Then setup
        PHASE_EXECUTION,  # Then main execution
        PHASE_TEARDOWN,   # Then teardown
        PHASE_END,        # Finally end phase
    ]
    
    spafw37.set_phases_order(custom_order)
    spafw37.add_commands(commands)


if __name__ == '__main__':
    setup()
    spafw37.output("Phase order: CLEANUP → SETUP → EXECUTION → TEARDOWN → END\n")
    spafw37.run_cli()
