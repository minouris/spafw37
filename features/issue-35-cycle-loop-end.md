# Issue #35: Add CYCLE_LOOP_END to Cycles

## Overview

Add the ability to run a callable at the end of each loop iteration of a cycle. This completes the cycle iteration lifecycle by providing a hook that runs after all cycle commands have executed but before checking the loop condition for the next iteration.

Currently, cycles support `CYCLE_INIT` (before loop starts), `CYCLE_LOOP` (condition check before each iteration), `CYCLE_LOOP_START` (preparation at start of each iteration), and `CYCLE_END` (after loop completes). The missing piece is `CYCLE_LOOP_END`, which would run after all cycle commands execute in each iteration, enabling cleanup, state updates, or logging at the end of each iteration.

This provides symmetry with `CYCLE_LOOP_START` and enables common patterns like incrementing counters, accumulating results, or cleaning up per-iteration resources without requiring this logic to be embedded in the last cycle command.

**Key architectural decisions:**

- **Part of cycle lifecycle:** Extends existing cycle system with per-iteration cleanup hook
- **Consistent naming:** Follows `CYCLE_LOOP_START` pattern with `CYCLE_LOOP_END` for symmetry
- **Execution order:** Runs after all cycle commands complete, before next `CYCLE_LOOP` check
- **Optional hook:** Not required in cycle definitions, same as `CYCLE_LOOP_START`
- **Backward compatibility:** New functionality, no breaking changes to existing cycles

## Table of Contents

- [Overview](#overview)
- [Implementation Steps](#implementation-steps)
  - [1. Add CYCLE_LOOP_END constant](#1-add-cycle_loop_end-constant)
  - [2. Update cycle execution to call CYCLE_LOOP_END](#2-update-cycle-execution-to-call-cycle_loop_end)
  - [3. Update cycle validation](#3-update-cycle-validation)
  - [4. Add tests](#4-add-tests)
  - [5. Create example](#5-create-example)
  - [6. Update documentation](#6-update-documentation)
- [Further Considerations](#further-considerations)
  - [1. Execution order with nested cycles](#1-execution-order-with-nested-cycles)
  - [2. Error handling in CYCLE_LOOP_END](#2-error-handling-in-cycle_loop_end)
  - [3. State management patterns](#3-state-management-patterns)
- [Success Criteria](#success-criteria)
- [CHANGES for v1.1.0 Release](#changes-for-v110-release)

## Implementation Steps

### 1. Add CYCLE_LOOP_END constant

**File:** `src/spafw37/constants/cycle.py`

Add new constant to cycle constants:

```python
CYCLE_LOOP_END = "cycle-loop-end-function"  # Function to run at end of each iteration - runs after all cycle commands complete
```

**Location:** Add after `CYCLE_LOOP_START` constant and before `CYCLE_END` constant to maintain logical order (start → end within iteration lifecycle).

**Documentation comment:** Should explain that this runs after all cycle commands execute in each iteration, before the next `CYCLE_LOOP` condition check.

**Tests:** No tests needed - this is just a constant definition.

[↑ Back to top](#table-of-contents)

### 2. Update cycle execution to call CYCLE_LOOP_END

**File:** `src/spafw37/cycle.py`

Modify the cycle execution function to call `CYCLE_LOOP_END` after cycle commands execute.

**Implementation order:**

1. Locate the cycle execution loop in `execute_cycle()` or similar function
2. Identify where cycle commands are executed within the loop
3. Add call to `CYCLE_LOOP_END` function after command execution
4. Add error handling for `CYCLE_LOOP_END` execution
5. Add logging for `CYCLE_LOOP_END` execution

**Current execution flow:**

```python
# Simplified current flow
CYCLE_INIT()
while CYCLE_LOOP():
    CYCLE_LOOP_START()  # if defined
    execute_cycle_commands()
    # Missing: CYCLE_LOOP_END() call here
CYCLE_END()
```

**Updated execution flow:**

```python
# Updated flow with CYCLE_LOOP_END
CYCLE_INIT()
while CYCLE_LOOP():
    CYCLE_LOOP_START()  # if defined
    execute_cycle_commands()
    CYCLE_LOOP_END()  # NEW: call at end of iteration
CYCLE_END()
```

**Implementation details:**

- Extract `CYCLE_LOOP_END` function from cycle definition using `cycle_def.get(CYCLE_LOOP_END)`
- Only call if defined (optional, like `CYCLE_LOOP_START`)
- Call after all cycle commands have executed successfully
- Log at TRACE level before calling: `"Calling cycle loop end function for cycle: {cycle_name}"`
- Wrap in try-except to catch and re-raise with context
- Error message format: `"Error in cycle loop end function for cycle '{cycle_name}': {error}"`

**Helper function extraction:**

Create `_call_cycle_loop_end()` helper if cycle execution doesn't already use helpers for lifecycle functions:

```python
def _call_cycle_loop_end(cycle_def):
    """
    Call the cycle loop end function if defined.
    
    Runs at the end of each iteration after all cycle commands complete.
    
    Args:
        cycle_def: Cycle definition dict
        
    Raises:
        CycleExecutionError: If loop end function raises an exception
    """
    loop_end_fn = cycle_def.get(CYCLE_LOOP_END)
    if not loop_end_fn:
        return
    
    cycle_name = cycle_def.get(CYCLE_NAME, 'unknown')
    logging.log_trace('cycle', 'Calling cycle loop end function for cycle: {}'.format(cycle_name))
    
    try:
        loop_end_fn()
    except Exception as error:
        raise CycleExecutionError(
            "Error in cycle loop end function for cycle '{}': {}".format(cycle_name, error)
        )
```

**Tests:** Test coverage added in Step 4.

[↑ Back to top](#table-of-contents)

### 3. Update cycle validation

**File:** `src/spafw37/cycle.py`

Update cycle validation functions to check `CYCLE_LOOP_END` if validation is performed on lifecycle functions.

**Implementation order:**

1. Review existing validation functions for cycle lifecycle functions
2. Identify if `CYCLE_LOOP_START` is validated
3. Add equivalent validation for `CYCLE_LOOP_END` if validation exists
4. Ensure consistent error messages

**Validation checks (if applicable):**

- If cycle validates that lifecycle functions are callable, add check for `CYCLE_LOOP_END`
- Error message format: `"CYCLE_LOOP_END must be callable, got: {type}"`
- Same validation pattern as `CYCLE_LOOP_START`

**Note:** If existing code does not validate lifecycle functions (relies on runtime errors), this step may be minimal or skipped.

**Tests:** Test coverage added in Step 4.

[↑ Back to top](#table-of-contents)

### 4. Add tests

**File:** `tests/test_cycle.py`

Add comprehensive tests for `CYCLE_LOOP_END` functionality.

**Tests to add:**

- `test_cycle_loop_end_called()` - Verify `CYCLE_LOOP_END` function is called at end of each iteration
- `test_cycle_loop_end_multiple_iterations()` - Verify `CYCLE_LOOP_END` called once per iteration across multiple iterations
- `test_cycle_loop_end_optional()` - Verify cycles work without `CYCLE_LOOP_END` defined (backward compatibility)
- `test_cycle_loop_end_execution_order()` - Verify execution order: commands execute, then `CYCLE_LOOP_END`, then `CYCLE_LOOP` check
- `test_cycle_loop_end_access_to_state()` - Verify `CYCLE_LOOP_END` can read state set by cycle commands
- `test_cycle_loop_end_modify_state()` - Verify `CYCLE_LOOP_END` can modify state (e.g., increment counter)
- `test_cycle_loop_end_error_handling()` - Verify error in `CYCLE_LOOP_END` raises `CycleExecutionError` with context
- `test_cycle_loop_end_not_called_after_last_iteration()` - Verify `CYCLE_LOOP_END` not called after loop exits (only `CYCLE_END` runs)
- `test_cycle_loop_end_with_nested_cycles()` - Verify nested cycles each call their own `CYCLE_LOOP_END`

**Test implementation pattern:**

```python
def test_cycle_loop_end_called():
    """
    Test that CYCLE_LOOP_END function is called at end of each iteration.
    The function should run after all cycle commands execute.
    This validates the basic functionality of the new lifecycle hook.
    """
    call_log = []
    
    def loop_end():
        call_log.append('loop_end')
    
    def cycle_command():
        call_log.append('command')
    
    # Define cycle with CYCLE_LOOP_END
    # Execute cycle
    # Assert call_log shows correct order and count
```

**Tests:** These tests provide the coverage for Steps 2 and 3.

[↑ Back to top](#table-of-contents)

### 5. Create example

**File:** `examples/cycles_loop_end.py` (new)

Create example demonstrating `CYCLE_LOOP_END` usage patterns.

**Example should demonstrate:**

- Basic `CYCLE_LOOP_END` usage for counter increment
- State cleanup at end of iteration
- Result accumulation pattern
- Comparison with doing same logic in last cycle command vs. `CYCLE_LOOP_END`
- Symmetry with `CYCLE_LOOP_START` (prepare at start, cleanup at end)

**Example structure:**

```python
"""Cycle Loop End Example - Per-iteration cleanup and state updates.

This example shows:
- CYCLE_LOOP_END - runs at end of each iteration
- Counter increment pattern using CYCLE_LOOP_END
- Symmetry with CYCLE_LOOP_START (prepare/cleanup)
- Accumulating results across iterations
"""

from spafw37 import core as spafw37
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION, COMMAND_CYCLE
from spafw37.constants.cycle import (
    CYCLE_NAME,
    CYCLE_INIT,
    CYCLE_LOOP,
    CYCLE_LOOP_START,
    CYCLE_LOOP_END,
    CYCLE_END,
    CYCLE_COMMANDS,
)
from spafw37.constants.param import PARAM_NAME, PARAM_TYPE, PARAM_TYPE_NUMBER, PARAM_RUNTIME_ONLY

# Runtime parameters
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
]

def init_cycle():
    spafw37.set_param(param_name='iteration-count', value=0)
    spafw37.set_param(param_name='max-iterations', value=3)
    spafw37.output("Starting cycle with 3 iterations")

def has_more_iterations():
    iteration_count = spafw37.get_param('iteration-count')
    max_iterations = spafw37.get_param('max-iterations')
    return iteration_count < max_iterations

def prepare_iteration():
    iteration_count = spafw37.get_param('iteration-count')
    spafw37.output(f"[Iteration {iteration_count + 1}] Starting...")

def process_data():
    iteration_count = spafw37.get_param('iteration-count')
    spafw37.output(f"[Iteration {iteration_count + 1}] Processing data...")

def cleanup_iteration():
    """Runs at end of each iteration - increments counter."""
    iteration_count = spafw37.get_param('iteration-count')
    iteration_count += 1
    spafw37.set_param(param_name='iteration-count', value=iteration_count)
    spafw37.output(f"[Iteration {iteration_count}] Complete")

def finalize_cycle():
    iteration_count = spafw37.get_param('iteration-count')
    spafw37.output(f"Cycle finished: {iteration_count} iterations completed")

# Define cycle
commands = [
    {
        COMMAND_NAME: 'run-cycle',
        COMMAND_ACTION: lambda: None,
        COMMAND_CYCLE: {
            CYCLE_NAME: 'demo-cycle',
            CYCLE_INIT: init_cycle,
            CYCLE_LOOP: has_more_iterations,
            CYCLE_LOOP_START: prepare_iteration,
            CYCLE_LOOP_END: cleanup_iteration,  # NEW: cleanup at end of iteration
            CYCLE_END: finalize_cycle,
            CYCLE_COMMANDS: [
                {
                    COMMAND_NAME: 'process',
                    COMMAND_ACTION: process_data,
                }
            ],
        }
    }
]

if __name__ == '__main__':
    spafw37.add_params(params)
    spafw37.add_commands(commands)
    spafw37.run_cli()
```

**Update `examples/README.md`:**

Add entry for `cycles_loop_end.py` in the Cycles section.

**Tests:** Manual verification - run example and verify output shows correct execution order.

[↑ Back to top](#table-of-contents)

### 6. Update documentation

**Files:** `doc/cycles.md`, `doc/api-reference.md`

Update documentation to include `CYCLE_LOOP_END` in cycle lifecycle descriptions.

**`doc/cycles.md` updates:**

- Update Overview section to mention `CYCLE_LOOP_END` in lifecycle description
- Add `CYCLE_LOOP_END` to Cycle Constants table with description
- Add section for Loop End Function with code example
- Update Cycle Lifecycle section to show complete flow including `CYCLE_LOOP_END`
- Update execution order diagrams or flow descriptions
- Add to Best Practices section: when to use `CYCLE_LOOP_END` vs. embedding logic in commands

**Cycle Constants table addition:**

| Constant | Description |
|----------|-------------|
| `CYCLE_LOOP_END` | Function to run at end of each iteration (runs after all cycle commands complete) |

**Loop End Function section:**

```markdown
### Loop End Function

Runs at the end of each iteration after all cycle commands complete:

```python
def cleanup_iteration():
    iteration_count = spafw37.get_param('iteration-count')
    iteration_count += 1
    spafw37.set_param(param_name='iteration-count', value=iteration_count)
    spafw37.output(f"Iteration {iteration_count} complete")
```

Common use cases:
- Incrementing iteration counters
- Accumulating results from iteration
- Cleaning up per-iteration resources
- Logging iteration completion
```

**Cycle Lifecycle section update:**

```markdown
### Complete Cycle Execution Order

1. `CYCLE_INIT` - Initialize resources before loop starts
2. `CYCLE_LOOP` - Check if iteration should continue (returns True/False)
3. `CYCLE_LOOP_START` - Prepare data for iteration (optional)
4. Execute all cycle commands in order
5. `CYCLE_LOOP_END` - Cleanup or state updates for iteration (optional)
6. Return to step 2 for next iteration
7. `CYCLE_END` - Finalize resources after loop completes
```

**`doc/api-reference.md` updates:**

- Add `CYCLE_LOOP_END` to Cycle Constants section
- Update cycle lifecycle description

**Tests:** Manual review - verify documentation is accurate and consistent.

[↑ Back to top](#table-of-contents)

## Further Considerations

### 1. Execution order with nested cycles

**Question:** How does `CYCLE_LOOP_END` interact with nested cycles?

**Answer:** Each cycle calls its own `CYCLE_LOOP_END` at the end of its iteration, maintaining proper nesting.

**Rationale:**
- Nested cycles are independent and maintain their own lifecycle
- Each cycle should cleanup its own iteration state
- Parent cycle's `CYCLE_LOOP_END` runs after all nested cycle activity completes
- This maintains separation of concerns and predictable execution order

**Implementation:**
- No special handling needed for nested cycles
- Existing nesting logic handles lifecycle function calls correctly
- Each cycle's `CYCLE_LOOP_END` called in its own iteration context

**Execution order example with nested cycles:**

```
Parent CYCLE_INIT
Parent CYCLE_LOOP (true)
  Parent CYCLE_LOOP_START
  Parent command 1
  Nested CYCLE_INIT
  Nested CYCLE_LOOP (true)
    Nested CYCLE_LOOP_START
    Nested commands
    Nested CYCLE_LOOP_END
  Nested CYCLE_LOOP (false)
  Nested CYCLE_END
  Parent command 2
  Parent CYCLE_LOOP_END
Parent CYCLE_LOOP (false)
Parent CYCLE_END
```

[↑ Back to top](#table-of-contents)

### 2. Error handling in CYCLE_LOOP_END

**Question:** What happens if `CYCLE_LOOP_END` raises an exception?

**Answer:** Raise `CycleExecutionError` with context and halt cycle execution.

**Rationale:**
- Consistent with error handling for other lifecycle functions
- Errors in cleanup should stop execution (indicates invalid state)
- Provides clear error message with cycle name and original error
- Prevents continuing with potentially corrupted state

**Implementation:**
- Wrap `CYCLE_LOOP_END` call in try-except block
- Catch any exception and re-raise as `CycleExecutionError`
- Include cycle name and original error message in exception
- Error propagates up and halts command execution

**Alternative considered:** Continue execution and log error.
- Pro: More forgiving, allows cycle to continue
- Con: Continuing with failed cleanup risks corrupted state
- Con: Makes debugging harder (error logged but execution continues)

**Rejected because:** Failing fast with clear error is safer and easier to debug than continuing with potentially invalid state.

[↑ Back to top](#table-of-contents)

### 3. State management patterns

**Question:** Should `CYCLE_LOOP_END` be used for counter increments or should that happen in `CYCLE_LOOP_START`?

**Answer:** Counter increments typically belong in `CYCLE_LOOP_END` as they reflect completed iterations.

**Rationale:**
- `CYCLE_LOOP_START` prepares for upcoming iteration (iteration N about to start)
- `CYCLE_LOOP_END` reflects completed iteration (iteration N just finished)
- Counter semantics usually mean "iterations completed" not "iterations started"
- Placing increment at end prevents off-by-one errors if iteration fails partway through

**Implementation:**
- Document this pattern in examples and best practices
- Show counter increment in `CYCLE_LOOP_END` in example code
- Explain in documentation why end-of-iteration is preferred for completion tracking

**Pattern comparison:**

```python
# Preferred: counter reflects completed iterations
def cleanup_iteration():
    count = spafw37.get_param('count')
    spafw37.set_param(param_name='count', value=count + 1)

# Alternative: counter reflects started iterations
def prepare_iteration():
    count = spafw37.get_param('count')
    spafw37.set_param(param_name='count', value=count + 1)
```

The first pattern is clearer because the counter accurately represents completed work, not started work that might fail.

[↑ Back to top](#table-of-contents)

## Success Criteria

- [ ] `CYCLE_LOOP_END` constant added to `src/spafw37/constants/cycle.py`
- [ ] Cycle execution updated to call `CYCLE_LOOP_END` after cycle commands execute
- [ ] `_call_cycle_loop_end()` helper implemented with error handling and logging
- [ ] Validation updated to check `CYCLE_LOOP_END` if lifecycle functions are validated
- [ ] 9 new tests added to `tests/test_cycle.py` covering all `CYCLE_LOOP_END` scenarios
- [ ] `CYCLE_LOOP_END` optional (cycles work without it, maintaining backward compatibility)
- [ ] Error handling raises `CycleExecutionError` with cycle name and original error
- [ ] Execution order correct: commands → `CYCLE_LOOP_END` → `CYCLE_LOOP` check
- [ ] Nested cycles each call their own `CYCLE_LOOP_END` correctly
- [ ] Example file `examples/cycles_loop_end.py` created demonstrating usage patterns
- [ ] `examples/README.md` updated with new example entry
- [ ] `doc/cycles.md` updated with `CYCLE_LOOP_END` in all relevant sections
- [ ] `doc/cycles.md` Cycle Constants table includes `CYCLE_LOOP_END`
- [ ] `doc/cycles.md` Cycle Lifecycle section shows complete execution order
- [ ] `doc/api-reference.md` updated with `CYCLE_LOOP_END` constant
- [ ] All existing tests still passing
- [ ] Overall test coverage remains above 90%
- [ ] Issue #35 closed with reference to implementation

[↑ Back to top](#table-of-contents)

## CHANGES for v1.1.0 Release

Issue #35: Add CYCLE_LOOP_END to Cycles

### Issues Closed

- #35: Add CYCLE_LOOP_END to Cycles

### Additions

- `CYCLE_LOOP_END` constant for defining function to run at end of each cycle iteration. Function runs after all cycle commands execute but before next loop condition check. Optional, same as `CYCLE_LOOP_START`.

### Removals

None.

### Changes

- Cycle execution now calls `CYCLE_LOOP_END` function at end of each iteration if defined in cycle definition.

### Migration

No migration required. New functionality only. Existing cycles continue to work without defining `CYCLE_LOOP_END`.

### Documentation

- `doc/cycles.md` added `CYCLE_LOOP_END` to Cycle Constants table
- `doc/cycles.md` added Loop End Function section with examples
- `doc/cycles.md` updated Cycle Lifecycle section showing complete execution order
- `doc/cycles.md` added best practices for when to use `CYCLE_LOOP_END`
- `doc/api-reference.md` added `CYCLE_LOOP_END` constant documentation
- `examples/cycles_loop_end.py` demonstrates per-iteration cleanup and counter patterns
- `examples/README.md` updated with new example entry

### Testing

- 9 new tests in `test_cycle.py`
- All tests pass
- Test coverage remains above 90%

---

Full changelog: https://github.com/minouris/spafw37/compare/v1.1.0...v1.2.0  
Issue: https://github.com/minouris/spafw37/issues/35

[↑ Back to top](#table-of-contents)
