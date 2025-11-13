"""
Custom Phases Example (Advanced)

Demonstrates creating completely custom phases, replacing all defaults.

**WARNING:** This is an advanced pattern. Completely replacing default phases
can break framework features. Framework commands (help, load-config, save-config)
expect PHASE_EXECUTION to exist. When using completely custom phases, you must
set a new default phase or these commands won't work.

**RECOMMENDED:** Use phases_extended.py example instead, which shows how to
extend default phases with custom ones while preserving framework functionality.

Key concepts:
- Creating custom phase names beyond the defaults
- Using set_phases_order() with only custom phases
- Setting a new default phase with set_default_phase()
- Organizing commands into application-specific lifecycle stages
- IMPORTANT: When using completely custom phases, set a default phase
  or all commands must explicitly specify COMMAND_PHASE

This example models a build pipeline with custom phases:
1. VALIDATE - Validate source code and dependencies
2. BUILD - Compile and package
3. TEST - Run test suites
4. DEPLOY - Deploy to target environment
5. VERIFY - Post-deployment verification

Note: Framework commands will run in PHASE_BUILD (the custom default) instead
of PHASE_EXECUTION, which may not be semantically appropriate for operations
like displaying help or saving configuration.
"""

from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_PHASE,
)

# Define custom phase names
PHASE_VALIDATE = "phase-validate"
PHASE_BUILD = "phase-build"
PHASE_TEST = "phase-test"
PHASE_DEPLOY = "phase-deploy"
PHASE_VERIFY = "phase-verify"


def setup():
    """Configure the application with custom phases."""
    
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
    
    def implicit_build():
        """
        This command has no COMMAND_PHASE specified.
        
        It will be assigned to PHASE_BUILD because we called
        set_default_phase(PHASE_BUILD). Without that call,
        it would be assigned to PHASE_EXECUTION, which doesn't
        exist in our custom phase order, so it would never run.
        """
        print("[BUILD] Running implicit build step (uses default phase)...")
    
    # Test phase actions
    def unit_tests():
        """Run unit tests."""
        print("[TEST] Running unit tests...")
    
    def integration_tests():
        """Run integration tests."""
        print("[TEST] Running integration tests...")
    
    # Deploy phase actions
    def deploy_staging():
        """Deploy to staging."""
        print("[DEPLOY] Deploying to staging environment...")
    
    def deploy_prod():
        """Deploy to production."""
        print("[DEPLOY] Deploying to production environment...")
    
    # Verify phase actions
    def health_check():
        """Run health checks."""
        print("[VERIFY] Running health checks...")
    
    def smoke_tests():
        """Run smoke tests."""
        print("[VERIFY] Running smoke tests...")
    
    commands = [
        # Validation phase
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
        # Build phase
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
        {
            COMMAND_NAME: 'implicit-build',
            COMMAND_DESCRIPTION: 'Build step without explicit phase (uses default)',
            COMMAND_ACTION: implicit_build,
            # NOTE: No COMMAND_PHASE specified - will use default phase (PHASE_BUILD)
        },
        # Test phase
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
        # Deploy phase
        {
            COMMAND_NAME: 'deploy-staging',
            COMMAND_DESCRIPTION: 'Deploy to staging',
            COMMAND_ACTION: deploy_staging,
            COMMAND_PHASE: PHASE_DEPLOY,
        },
        {
            COMMAND_NAME: 'deploy-prod',
            COMMAND_DESCRIPTION: 'Deploy to production',
            COMMAND_ACTION: deploy_prod,
            COMMAND_PHASE: PHASE_DEPLOY,
        },
        # Verify phase
        {
            COMMAND_NAME: 'health-check',
            COMMAND_DESCRIPTION: 'Run health checks',
            COMMAND_ACTION: health_check,
            COMMAND_PHASE: PHASE_VERIFY,
        },
        {
            COMMAND_NAME: 'smoke-tests',
            COMMAND_DESCRIPTION: 'Run smoke tests',
            COMMAND_ACTION: smoke_tests,
            COMMAND_PHASE: PHASE_VERIFY,
        },
    ]
    
    # Set custom phase order BEFORE adding commands
    custom_phases = [
        PHASE_VALIDATE,   # Validate first
        PHASE_BUILD,      # Then build
        PHASE_TEST,       # Then test
        PHASE_DEPLOY,     # Then deploy
        PHASE_VERIFY,     # Finally verify deployment
    ]
    
    spafw37.set_phases_order(custom_phases)
    
    # IMPORTANT: When using completely custom phases (no default phases included),
    # you must set a new default phase. Otherwise, commands without an explicit
    # COMMAND_PHASE will be assigned to PHASE_EXECUTION (the normal default),
    # which doesn't exist in our custom phase order and will never run.
    # This must be called BEFORE add_commands() so the new default is used.
    spafw37.set_default_phase(PHASE_BUILD)
    
    # Add commands AFTER setting phase order and default phase
    spafw37.add_commands(commands)


if __name__ == '__main__':
    setup()
    print("Custom pipeline phases: VALIDATE → BUILD → TEST → DEPLOY → VERIFY\n")
    spafw37.run_cli()
