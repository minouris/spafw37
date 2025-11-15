"""Basic Cycles Example - Simple repeating command sequences.

This example shows:
- CYCLE_INIT - initialise before loop starts
- CYCLE_LOOP - check if iteration should continue
- CYCLE_END - finalise after loop completes
- Basic iteration pattern
"""

from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_CYCLE,
)
from spafw37.constants.cycle import (
    CYCLE_NAME,
    CYCLE_INIT,
    CYCLE_LOOP,
    CYCLE_END,
    CYCLE_COMMANDS,
)
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_NUMBER,
    PARAM_RUNTIME_ONLY,
)

# Runtime parameters for cycle state
params = [
    {
        PARAM_NAME: 'counter',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_RUNTIME_ONLY: True,
    },
    {
        PARAM_NAME: 'max-iterations',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_RUNTIME_ONLY: True,
    },
]

# Cycle control functions

def init_counter():
    """Initialise the counter."""
    spafw37.set_config_value('counter', 0)
    spafw37.set_config_value('max-iterations', 5)
    spafw37.output("Initialized counter cycle (5 iterations)")
    spafw37.output("=" * 40)

def has_more_iterations():
    """Check if more iterations remain."""
    counter = spafw37.get_config_int('counter')
    max_iterations = spafw37.get_config_int('max-iterations')
    return counter < max_iterations

def finalize_counter():
    """Finalise the counter."""
    counter = spafw37.get_config_int('counter')
    spafw37.output("=" * 40)
    spafw37.output(f"Completed {counter} iterations")

# Cycle command actions

def process_iteration():
    """Process one iteration."""
    counter = spafw37.get_config_int('counter')
    counter += 1
    spafw37.set_config_value('counter', counter)
    
    max_iterations = spafw37.get_config_int('max-iterations')
    spafw37.output(f"[Iteration {counter}/{max_iterations}] Processing...")

# Define cycle commands
cycle_commands = [
    {
        COMMAND_NAME: 'process-iteration',
        COMMAND_DESCRIPTION: 'Process one iteration',
        COMMAND_ACTION: process_iteration,
    }
]

# Define main command with cycle
commands = [
    {
        COMMAND_NAME: 'run-cycle',
        COMMAND_DESCRIPTION: 'Run the counter cycle',
        COMMAND_ACTION: lambda: None,
        COMMAND_CYCLE: {
            CYCLE_NAME: 'counter-cycle',
            CYCLE_INIT: init_counter,
            CYCLE_LOOP: has_more_iterations,
            CYCLE_END: finalize_counter,
            CYCLE_COMMANDS: cycle_commands,
        }
    }
]

# Register parameters and commands
spafw37.add_params(params)
spafw37.add_commands(commands)
spafw37.set_app_name('cycles-basic-demo')

if __name__ == '__main__':
    spafw37.run_cli()
