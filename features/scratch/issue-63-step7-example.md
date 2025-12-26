# Step 7: Create example demonstrating new API

## Overview

This step creates a new example file showing how to use the `add_cycle()` and `add_cycles()` functions to define cycles separately from commands, demonstrating cleaner code organisation.

**File created:**
- `examples/cycles_toplevel_api.py`

**Tests created:**
- Manual execution test (Test 7.2.1)

## Module-level imports

No imports needed - this is the example file itself.

## Algorithm

### Example Design

The example should demonstrate:
1. Importing core API with alias: `from spafw37 import core as spafw37`
2. Defining cycles with `add_cycle()` (singular)
3. Defining multiple cycles with `add_cycles()` (plural)
4. Inline CYCLE_COMMAND definitions (dict format)
5. String CYCLE_COMMAND references
6. Commands registered separately from cycles
7. Full cycle execution with all phases (init, loop, end)
8. Clear output showing execution flow

## Implementation

### Code 7.1.1: Create cycles_toplevel_api.py example

**File:** `examples/cycles_toplevel_api.py`

```python
#!/usr/bin/env python
"""Demonstrate top-level cycle registration using add_cycle() and add_cycles().

This example shows how to define cycles as top-level objects separate from
commands, providing cleaner code organisation and consistent API patterns.

Run: python examples/cycles_toplevel_api.py
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


# Shared state for cycle demonstration
cycle_state = {'count': 0, 'max_iterations': 3}


def init_counter():
    """Initialise cycle state."""
    print("  [INIT] Initialising counter")
    cycle_state['count'] = 0


def check_counter():
    """Check if we should continue looping."""
    should_continue = cycle_state['count'] < cycle_state['max_iterations']
    print(f"  [LOOP CHECK] Count={cycle_state['count']}, Continue={should_continue}")
    return should_continue


def loop_start_message():
    """Print message at start of each iteration."""
    print(f"  [LOOP START] Starting iteration {cycle_state['count'] + 1}")


def loop_end_increment():
    """Increment counter at end of each iteration."""
    cycle_state['count'] += 1
    print(f"  [LOOP END] Completed iteration {cycle_state['count']}")


def end_summary():
    """Print final summary."""
    print(f"  [END] Cycle complete. Total iterations: {cycle_state['count']}")


def step_one_action():
    """Execute step one of the cycle."""
    print("    → Step 1: Processing")


def step_two_action():
    """Execute step two of the cycle."""
    print("    → Step 2: Processing")


# Example 1: Register single cycle with add_cycle()
# Demonstrates inline CYCLE_COMMAND definition (dict)
print("\n=== Example 1: Single cycle with inline command ===")

single_cycle = {
    CYCLE_COMMAND: {
        COMMAND_NAME: 'process-single',
        COMMAND_ACTION: lambda: print("COMMAND: process-single")
    },
    CYCLE_NAME: 'single-cycle',
    CYCLE_INIT: init_counter,
    CYCLE_LOOP: check_counter,
    CYCLE_LOOP_START: loop_start_message,
    CYCLE_LOOP_END: loop_end_increment,
    CYCLE_END: end_summary,
    CYCLE_COMMANDS: [
        {COMMAND_NAME: 'single-step1', COMMAND_ACTION: step_one_action},
        {COMMAND_NAME: 'single-step2', COMMAND_ACTION: step_two_action}
    ]
}

spafw37.add_cycle(single_cycle)
spafw37.run_cli(['process-single'])


# Example 2: Register multiple cycles with add_cycles()
# Demonstrates string CYCLE_COMMAND references (commands defined separately)
print("\n=== Example 2: Multiple cycles with command references ===")

# Define commands first
commands = [
    {
        COMMAND_NAME: 'process-batch-a',
        COMMAND_ACTION: lambda: print("COMMAND: process-batch-a")
    },
    {
        COMMAND_NAME: 'process-batch-b',
        COMMAND_ACTION: lambda: print("COMMAND: process-batch-b")
    }
]
spafw37.add_commands(commands)

# Define cycles referencing commands by name
cycles = [
    {
        CYCLE_COMMAND: 'process-batch-a',
        CYCLE_NAME: 'batch-a-cycle',
        CYCLE_INIT: init_counter,
        CYCLE_LOOP: check_counter,
        CYCLE_LOOP_START: loop_start_message,
        CYCLE_LOOP_END: loop_end_increment,
        CYCLE_END: end_summary,
        CYCLE_COMMANDS: [
            {COMMAND_NAME: 'batch-a-step1', COMMAND_ACTION: step_one_action}
        ]
    },
    {
        CYCLE_COMMAND: 'process-batch-b',
        CYCLE_NAME: 'batch-b-cycle',
        CYCLE_INIT: init_counter,
        CYCLE_LOOP: check_counter,
        CYCLE_LOOP_START: loop_start_message,
        CYCLE_LOOP_END: loop_end_increment,
        CYCLE_END: end_summary,
        CYCLE_COMMANDS: [
            {COMMAND_NAME: 'batch-b-step1', COMMAND_ACTION: step_one_action},
            {COMMAND_NAME: 'batch-b-step2', COMMAND_ACTION: step_two_action}
        ]
    }
]

spafw37.add_cycles(cycles)
spafw37.run_cli(['process-batch-a'])
spafw37.run_cli(['process-batch-b'])


# Example 3: Flexible registration order
# Demonstrates cycles can be registered before or after commands
print("\n=== Example 3: Flexible registration order ===")

# Register cycle BEFORE command exists
flexible_cycle = {
    CYCLE_COMMAND: 'process-flexible',
    CYCLE_NAME: 'flexible-cycle',
    CYCLE_INIT: init_counter,
    CYCLE_LOOP: check_counter,
    CYCLE_END: end_summary,
    CYCLE_COMMANDS: [
        {COMMAND_NAME: 'flex-step', COMMAND_ACTION: step_one_action}
    ]
}
spafw37.add_cycle(flexible_cycle)

# Register command AFTER cycle
flexible_command = {
    COMMAND_NAME: 'process-flexible',
    COMMAND_ACTION: lambda: print("COMMAND: process-flexible")
}
spafw37.add_command(flexible_command)

spafw37.run_cli(['process-flexible'])

print("\n=== All examples complete ===")
```

### Test 7.2.1: Example executes without errors

**File:** Manual test

```gherkin
Scenario: Run cycles_toplevel_api.py example
  Given the example file with add_cycle() and add_cycles() usage
  When the example is executed from command line
  Then it should complete successfully without exceptions
  And it should demonstrate cycle execution
  And output should show cycle functions being called
  
  # Tests: Example code functionality
  # Validates: Top-level API works in real usage scenario
```

**Manual test procedure:**
1. Navigate to workspace root: `cd /workspaces/spafw37`
2. Run example: `python examples/cycles_toplevel_api.py`
3. Verify output shows:
   - Three separate example sections
   - INIT, LOOP CHECK, LOOP START, LOOP END, END messages
   - Three iterations per cycle (count 0, 1, 2)
   - No Python exceptions or errors
4. Verify example file in README.md examples list

## Implementation Order

1. Create `examples/cycles_toplevel_api.py` (Code 7.1.1)
2. Test example execution manually (Test 7.2.1)
3. Add example to README.md examples list

## Notes

- Example uses `from spafw37 import core as spafw37` alias (standard pattern)
- Demonstrates both inline CYCLE_COMMAND (dict) and string references
- Shows flexible registration order (cycles before/after commands)
- Clear output with section headers for readability
- Inline commands in CYCLE_COMMANDS list (similar to inline params)
- Example should be executable as-is without modification
