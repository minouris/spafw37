#!/usr/bin/env python
"""Multiple cycle registration with add_cycles().

Demonstrates registering multiple cycles at once using string references
to commands defined separately.

Run: python examples/cycles_api_multiple.py
"""

from spafw37 import core as spafw37
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION
from spafw37.constants.cycle import (
    CYCLE_COMMAND,
    CYCLE_NAME,
    CYCLE_INIT,
    CYCLE_LOOP,
    CYCLE_LOOP_START,
    CYCLE_LOOP_END,
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
    print("  [LOOP CHECK] Count={}, Continue={}".format(cycle_state['count'], should_continue))
    return should_continue


def loop_start_message():
    """Print message at start of each iteration."""
    print("  [LOOP START] Starting iteration {}".format(cycle_state['count'] + 1))


def loop_end_increment():
    """Increment counter at end of each iteration."""
    cycle_state['count'] += 1
    print("  [LOOP END] Completed iteration {}".format(cycle_state['count']))


def end_summary():
    """Print final summary."""
    print("  [END] Cycle complete. Total iterations: {}".format(cycle_state['count']))


def step_action():
    """Execute step action."""
    print("    → Processing step")


print("=== Multiple Cycle Registration ===\n")

# Define commands first
commands = [
    {
        COMMAND_NAME: 'process-alpha',
        COMMAND_ACTION: lambda: print("COMMAND: process-alpha")
    },
    {
        COMMAND_NAME: 'process-beta',
        COMMAND_ACTION: lambda: print("COMMAND: process-beta")
    }
]
spafw37.add_commands(commands)

# Define cycles referencing commands by name
cycles = [
    {
        CYCLE_COMMAND: 'process-alpha',
        CYCLE_NAME: 'alpha-cycle',
        CYCLE_INIT: init_counter,
        CYCLE_LOOP: check_counter,
        CYCLE_LOOP_START: loop_start_message,
        CYCLE_LOOP_END: loop_end_increment,
        CYCLE_END: end_summary,
        CYCLE_COMMANDS: [
            {COMMAND_NAME: 'alpha-step', COMMAND_ACTION: step_action}
        ]
    },
    {
        CYCLE_COMMAND: 'process-beta',
        CYCLE_NAME: 'beta-cycle',
        CYCLE_INIT: init_counter,
        CYCLE_LOOP: check_counter,
        CYCLE_LOOP_START: loop_start_message,
        CYCLE_LOOP_END: loop_end_increment,
        CYCLE_END: end_summary,
        CYCLE_COMMANDS: [
            {COMMAND_NAME: 'beta-step', COMMAND_ACTION: step_action}
        ]
    }
]

spafw37.add_cycles(cycles)

print("Running alpha cycle:")
spafw37.run_cli(['process-alpha'])

print("\nRunning beta cycle:")
spafw37.run_cli(['process-beta'])

print("\n=== Complete ===")
