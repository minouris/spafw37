"""Cycle Loop End Example - Per-iteration cleanup and state updates.

This example shows:
- CYCLE_LOOP_END - runs at end of each iteration
- Counter increment pattern using CYCLE_LOOP_END
- Symmetry with CYCLE_LOOP_START (prepare/cleanup)
- Accumulating results across iterations
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
    CYCLE_LOOP_START,
    CYCLE_LOOP_END,
    CYCLE_END,
    CYCLE_COMMANDS,
)
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_NUMBER,
    PARAM_TYPE_LIST,
    PARAM_RUNTIME_ONLY,
)

# Runtime parameters for cycle state
params = [
    {
        PARAM_NAME: 'iteration-count',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_RUNTIME_ONLY: True,
    },
    {
        PARAM_NAME: 'max-iterations',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_RUNTIME_ONLY: True,
    },
    {
        PARAM_NAME: 'current-value',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_RUNTIME_ONLY: True,
    },
    {
        PARAM_NAME: 'results',
        PARAM_TYPE: PARAM_TYPE_LIST,
        PARAM_RUNTIME_ONLY: True,
    },
]

# Cycle control functions

def init_cycle():
    """Initialize cycle state."""
    spafw37.set_param(param_name='iteration-count', value=0)
    spafw37.set_param(param_name='max-iterations', value=5)
    spafw37.set_param(param_name='results', value=[])
    spafw37.output("Starting cycle with 5 iterations")
    spafw37.output("=" * 50)

def has_more_iterations():
    """Check if more iterations remain."""
    iteration_count = spafw37.get_param('iteration-count')
    max_iterations = spafw37.get_param('max-iterations')
    return iteration_count < max_iterations

def prepare_iteration():
    """Prepare data for the iteration."""
    iteration_count = spafw37.get_param('iteration-count')
    current_value = iteration_count * 10
    spafw37.set_param(param_name='current-value', value=current_value)
    spafw37.output(f"[Iteration {iteration_count + 1}] Prepared value: {current_value}")

def cleanup_iteration():
    """Cleanup at end of iteration - increments counter and accumulates results."""
    iteration_count = spafw37.get_param('iteration-count')
    current_value = spafw37.get_param('current-value')
    
    # Accumulate results
    results = spafw37.get_param('results')
    results.append(current_value * 2)  # Store processed value
    spafw37.set_param(param_name='results', value=results)
    
    # Increment counter
    iteration_count += 1
    spafw37.set_param(param_name='iteration-count', value=iteration_count)
    
    spafw37.output(f"[Iteration {iteration_count}] Cleanup complete, result: {current_value * 2}")
    spafw37.output("-" * 50)

def finalize_cycle():
    """Finalize cycle and display results."""
    iteration_count = spafw37.get_param('iteration-count')
    results = spafw37.get_param('results')
    total = sum(results)
    
    spafw37.output("=" * 50)
    spafw37.output(f"Cycle complete: {iteration_count} iterations")
    spafw37.output(f"Results: {results}")
    spafw37.output(f"Total: {total}")

# Cycle command actions

def process_data():
    """Process data in the iteration."""
    iteration_count = spafw37.get_param('iteration-count')
    current_value = spafw37.get_param('current-value')
    processed = current_value * 2
    spafw37.output(f"[Iteration {iteration_count + 1}] Processing: {current_value} -> {processed}")

# Define cycle commands
cycle_commands = [
    {
        COMMAND_NAME: 'process',
        COMMAND_DESCRIPTION: 'Process iteration data',
        COMMAND_ACTION: process_data,
    }
]

# Define main command with cycle
commands = [
    {
        COMMAND_NAME: 'run-cycle',
        COMMAND_DESCRIPTION: 'Run demonstration cycle with loop end',
        COMMAND_ACTION: lambda: None,
        COMMAND_CYCLE: {
            CYCLE_NAME: 'demo-cycle',
            CYCLE_INIT: init_cycle,
            CYCLE_LOOP: has_more_iterations,
            CYCLE_LOOP_START: prepare_iteration,
            CYCLE_LOOP_END: cleanup_iteration,  # Cleanup at end of each iteration
            CYCLE_END: finalize_cycle,
            CYCLE_COMMANDS: cycle_commands,
        }
    }
]

if __name__ == '__main__':
    spafw37.add_params(params)
    spafw37.add_commands(commands)
    spafw37.run_cli()
