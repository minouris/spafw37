"""
Extended Phases Example

Demonstrates extending default phases with custom phases.

Key concepts:
- Adding custom phases to the default phase order
- Preserving framework functionality by keeping PHASE_EXECUTION
- Organizing commands into mixed default and custom phases
- Best practice: extend rather than replace

This example models a deployment pipeline that extends default phases:
1. PHASE_SETUP - Default: initialization, framework config loading
2. PHASE_VALIDATE - Custom: validate source code and dependencies
3. PHASE_BUILD - Custom: compile and package
4. PHASE_TEST - Custom: run test suites
5. PHASE_EXECUTION - Default: main operations, framework commands
6. PHASE_TEARDOWN - Default: cleanup
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
    PHASE_EXECUTION,
    PHASE_TEARDOWN,
)

# Alias framework phases to custom names for your application
# IMPORTANT: These aliases resolve to the same string values that framework
# commands use, so help/load-config/save-config will work correctly
PHASE_START = PHASE_SETUP          # "phase-setup" - framework needs this value
PHASE_RUN = PHASE_EXECUTION        # "phase-execution" - default for user commands  
PHASE_FINISH = PHASE_TEARDOWN      # "phase-teardown" - framework needs this value

# Define additional custom phase names
PHASE_VALIDATE = "phase-validate"
PHASE_BUILD = "phase-build"
PHASE_TEST = "phase-test"


def setup():
    """Configure the application with extended phases."""
    
    # Setup phase actions
    def init_workspace():
        """Initialize workspace."""
        print("[SETUP] Initializing workspace...")
    
    # Validation phase actions
    def check_syntax():
        """Check code syntax."""
        print("[VALIDATE] Checking syntax...")
    
    def check_deps():
        """Check dependencies."""
        print("[VALIDATE] Checking dependencies...")
    
    # Build phase actions
    def compile_code():
        """Compile source code."""
        print("[BUILD] Compiling source code...")
    
    def package():
        """Package artifacts."""
        print("[BUILD] Packaging artifacts...")
    
    # Test phase actions
    def unit_tests():
        """Run unit tests."""
        print("[TEST] Running unit tests...")
    
    def integration_tests():
        """Run integration tests."""
        print("[TEST] Running integration tests...")
    
    # Execution phase actions
    def deploy():
        """Deploy application (main execution)."""
        print("[EXECUTION] Deploying application...")
    
    def verify():
        """Verify deployment (main execution)."""
        print("[EXECUTION] Verifying deployment...")
    
    # Teardown phase actions
    def cleanup():
        """Clean up resources."""
        print("[TEARDOWN] Cleaning up resources...")
    
    # Define commands
    commands = [
        # Setup phase (aliased as PHASE_START)
        {
            COMMAND_NAME: 'init-workspace',
            COMMAND_DESCRIPTION: 'Initialize workspace',
            COMMAND_ACTION: init_workspace,
            COMMAND_PHASE: PHASE_START,  # Actually "phase-setup"
        },
        # Validate phase (custom)
        {
            COMMAND_NAME: 'check-syntax',
            COMMAND_DESCRIPTION: 'Check code syntax',
            COMMAND_ACTION: check_syntax,
            COMMAND_PHASE: PHASE_VALIDATE,
        },
        {
            COMMAND_NAME: 'check-deps',
            COMMAND_DESCRIPTION: 'Check dependencies',
            COMMAND_ACTION: check_deps,
            COMMAND_PHASE: PHASE_VALIDATE,
        },
        # Build phase (custom)
        {
            COMMAND_NAME: 'compile',
            COMMAND_DESCRIPTION: 'Compile code',
            COMMAND_ACTION: compile_code,
            COMMAND_PHASE: PHASE_BUILD,
        },
        {
            COMMAND_NAME: 'package',
            COMMAND_DESCRIPTION: 'Package artifacts',
            COMMAND_ACTION: package,
            COMMAND_PHASE: PHASE_BUILD,
        },
        # Test phase (custom)
        {
            COMMAND_NAME: 'unit-tests',
            COMMAND_DESCRIPTION: 'Run unit tests',
            COMMAND_ACTION: unit_tests,
            COMMAND_PHASE: PHASE_TEST,
        },
        {
            COMMAND_NAME: 'integration-tests',
            COMMAND_DESCRIPTION: 'Run integration tests',
            COMMAND_ACTION: integration_tests,
            COMMAND_PHASE: PHASE_TEST,
        },
        # Execution phase (aliased as PHASE_RUN)
        {
            COMMAND_NAME: 'deploy',
            COMMAND_DESCRIPTION: 'Deploy application',
            COMMAND_ACTION: deploy,
            COMMAND_PHASE: PHASE_RUN,  # Actually "phase-execution"
        },
        {
            COMMAND_NAME: 'verify',
            COMMAND_DESCRIPTION: 'Verify deployment',
            COMMAND_ACTION: verify,
            COMMAND_PHASE: PHASE_RUN,  # Actually "phase-execution"
        },
        # Teardown phase (aliased as PHASE_FINISH)
        {
            COMMAND_NAME: 'cleanup',
            COMMAND_DESCRIPTION: 'Clean up resources',
            COMMAND_ACTION: cleanup,
            COMMAND_PHASE: PHASE_FINISH,  # Actually "phase-teardown"
        },
    ]
    
    # BEST PRACTICE: Use aliased framework constants with custom phases
    # This ensures framework commands (help, load-config, save-config) work
    # because the string values match what they expect
    extended_phases = [
        PHASE_START,      # "phase-setup" - framework: help, load-config
        PHASE_VALIDATE,   # "phase-validate" - custom validation
        PHASE_BUILD,      # "phase-build" - custom build
        PHASE_TEST,       # "phase-test" - custom testing
        PHASE_RUN,        # "phase-execution" - main execution, default phase
        PHASE_FINISH,     # "phase-teardown" - framework: save-config
    ]
    
    # Set extended phase order BEFORE adding commands
    spafw37.set_phases_order(extended_phases)
    
    # No need to call set_default_phase() because PHASE_RUN is aliased to
    # PHASE_EXECUTION, which is the default. Framework commands will work
    # automatically because PHASE_START and PHASE_FINISH resolve to the
    # string values "phase-setup" and "phase-teardown" that they expect.
    
    # Add commands AFTER setting phase order
    spafw37.add_commands(commands)


if __name__ == '__main__':
    setup()
    print("Extended phases: START → VALIDATE → BUILD → TEST → RUN → FINISH")
    print("(Aliased to: SETUP → VALIDATE → BUILD → TEST → EXECUTION → TEARDOWN)\n")
    spafw37.run_cli()
