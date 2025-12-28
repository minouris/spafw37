#!/usr/bin/env python
"""Basic cycle registration with add_cycle().

Demonstrates single cycle registration using inline CYCLE_COMMAND definition.

Run: python examples/cycles_api_basic.py
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


cycle_state = {'count': 0, 'max_iterations': 3}


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


def step_one_action():
    """Execute step one of the cycle."""
    print("    → Step 1: Processing")


def step_two_action():
    """Execute step two of the cycle."""
    print("    → Step 2: Processing")


print("=== Basic Cycle Registration ===\n")

cycle_def = {
    CYCLE_COMMAND: {
        COMMAND_NAME: 'process-data',
        COMMAND_ACTION: lambda: print("COMMAND: process-data")
    },
    CYCLE_NAME: 'data-processor',
    CYCLE_INIT: init_counter,
    CYCLE_LOOP: check_counter,
    CYCLE_LOOP_START: loop_start_message,
    CYCLE_LOOP_END: loop_end_increment,
    CYCLE_END: end_summary,
    CYCLE_COMMANDS: [
        {COMMAND_NAME: 'load-data', COMMAND_ACTION: step_one_action},
        {COMMAND_NAME: 'transform-data', COMMAND_ACTION: step_two_action}
    ]
}

spafw37.add_cycle(cycle_def)
spafw37.run_cli(['process-data'])

print("\n=== Complete ===")
