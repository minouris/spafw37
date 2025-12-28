#!/usr/bin/env python
"""Flexible cycle registration order.

Demonstrates that cycles can be registered before their target commands,
providing flexibility in code organisation.

Run: python examples/cycles_api_flexible_order.py
"""

from spafw37 import core as spafw37
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION
from spafw37.constants.cycle import (
    CYCLE_COMMAND,
    CYCLE_NAME,
    CYCLE_INIT,
    CYCLE_LOOP,
    CYCLE_END,
    CYCLE_COMMANDS
)


cycle_state = {'count': 0, 'max_iterations': 2}


def init_counter():
    """Initialise cycle state."""
    print("  [INIT] Initialising counter")
    cycle_state['count'] = 0


def check_counter():
    """Check if we should continue looping."""
    should_continue = cycle_state['count'] < cycle_state['max_iterations']
    cycle_state['count'] += 1
    print("  [LOOP CHECK] Iteration {}, Continue={}".format(cycle_state['count'], should_continue))
    return should_continue


def end_summary():
    """Print final summary."""
    print("  [END] Cycle complete. Total iterations: {}".format(cycle_state['count']))


def step_action():
    """Execute step action."""
    print("    → Processing step")


print("=== Flexible Registration Order ===\n")

# Register cycle BEFORE command exists
print("Registering cycle...")
cycle_def = {
    CYCLE_COMMAND: 'process-flexible',
    CYCLE_NAME: 'flexible-cycle',
    CYCLE_INIT: init_counter,
    CYCLE_LOOP: check_counter,
    CYCLE_END: end_summary,
    CYCLE_COMMANDS: [
        {COMMAND_NAME: 'flex-step', COMMAND_ACTION: step_action}
    ]
}
spafw37.add_cycle(cycle_def)

# Register command AFTER cycle
print("Registering command...\n")
command_def = {
    COMMAND_NAME: 'process-flexible',
    COMMAND_ACTION: lambda: print("COMMAND: process-flexible")
}
spafw37.add_command(command_def)

print("Running cycle:")
spafw37.run_cli(['process-flexible'])

print("\n=== Complete ===")
