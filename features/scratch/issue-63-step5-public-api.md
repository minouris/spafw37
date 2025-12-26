# Step 5: Expose new functions through core.py facade

## Overview

This step exposes the new cycle registration functions through the core.py public API facade, following the same delegation pattern used for params and commands.

**Public API functions added to core.py:**
- `add_cycle(cycle_def)` - Delegates to `cycle.add_cycle()`
- `add_cycles(cycle_defs)` - Delegates to `cycle.add_cycles()`

**Tests created:**
- `test_core_add_cycle_delegates_to_cycle_module()` - Verify add_cycle() delegation
- `test_core_add_cycles_delegates_to_cycle_module()` - Verify add_cycles() delegation
- `test_core_api_consistency_with_add_command_pattern()` - Verify API pattern consistency

## Module-level imports

See `issue-63-step1-imports.md` for all required imports.

## Algorithm

### Public API Delegation Pattern

The core.py module serves as a facade, providing simple delegation functions:
1. Import the cycle module
2. Create wrapper functions that call cycle module functions directly
3. Preserve docstrings and function signatures for consistency
4. No additional logic - pure delegation

## Implementation

### Code 5.1.1: Add add_cycle() to core.py

**File:** `src/spafw37/core.py`

```python
# Block 5.1.1: Add add_cycle() delegation function
# Add after existing add_command() function (around line 150)

def add_cycle(cycle_def):
    """Register a cycle definition for a command.
    
    Cycles define repeated command sequences with init, loop, and end functions.
    This function validates the cycle structure and stores it for later attachment
    to commands when they are registered.
    
    The CYCLE_COMMAND field can be:
    - String: Name of an existing or future command (command reference)
    - Dict: Inline command definition (will be registered immediately)
    
    Duplicate handling: If a cycle is already registered for the command:
    - Identical definition (deep equality): silently skip, first registration wins
    - Different definition: raise ValueError to prevent conflicting configurations
    
    Args:
        cycle_def: Cycle definition dict containing:
            - CYCLE_COMMAND: Command name (string) or inline definition (dict) (required)
            - CYCLE_NAME: Identifier for the cycle (required)
            - CYCLE_LOOP: Loop condition function (required)
            - CYCLE_INIT: Init function (optional)
            - CYCLE_LOOP_START: Loop start function (optional)
            - CYCLE_LOOP_END: Loop end function (optional)
            - CYCLE_END: End function (optional)
            - CYCLE_COMMANDS: List of commands in cycle (optional)
    
    Raises:
        ValueError: If required fields missing or conflicting cycle registered
    
    Example:
        >>> from spafw37 import core as spafw37
        >>> cycle = {
        ...     CYCLE_COMMAND: 'my-command',
        ...     CYCLE_NAME: 'my-cycle',
        ...     CYCLE_LOOP: lambda: True
        ... }
        >>> spafw37.add_cycle(cycle)
    """
    cycle.add_cycle(cycle_def)
```

### Code 5.1.2: Add add_cycles() to core.py

**File:** `src/spafw37/core.py`

```python
# Block 5.1.2: Add add_cycles() delegation function
# Add after add_cycle() function

def add_cycles(cycle_defs):
    """Register multiple cycle definitions.
    
    Convenience function for registering multiple cycles at once.
    Each cycle is registered individually using add_cycle().
    
    Args:
        cycle_defs: List of cycle definition dicts
    
    Raises:
        ValueError: If any cycle validation fails
    
    Example:
        >>> from spafw37 import core as spafw37
        >>> cycles = [
        ...     {CYCLE_COMMAND: 'cmd1', CYCLE_NAME: 'cycle1', CYCLE_LOOP: loop_fn1},
        ...     {CYCLE_COMMAND: 'cmd2', CYCLE_NAME: 'cycle2', CYCLE_LOOP: loop_fn2}
        ... ]
        >>> spafw37.add_cycles(cycles)
    """
    cycle.add_cycles(cycle_defs)
```

### Test 5.2.1: core.add_cycle() delegates to cycle.add_cycle()

**File:** `tests/test_core.py`

```gherkin
Scenario: Call core.add_cycle() with cycle definition
  Given a valid cycle definition dict
  When core.add_cycle() is called with the cycle
  Then cycle.add_cycle() should be called
  And the cycle should be stored in cycle._cycles
  And no exceptions should be raised
  
  # Tests: Public API delegation for single cycle
  # Validates: core.py facade provides add_cycle() access
```

```python
def test_core_add_cycle_delegates_to_cycle_module():
    """Test that core.add_cycle() delegates to cycle.add_cycle().
    
    This test verifies that the public API function core.add_cycle()
    correctly delegates to the cycle module's add_cycle() function.
    This behaviour is expected to provide consistent public API.
    """
    setup_function()
    
    test_cycle = {
        CYCLE_COMMAND: 'test-cmd',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    core.add_cycle(test_cycle)
    
    # Verify cycle was registered in cycle module
    assert 'test-cmd' in cycle._cycles
    assert cycle._cycles['test-cmd'] == test_cycle
```

### Test 5.2.2: core.add_cycles() delegates to cycle.add_cycles()

**File:** `tests/test_core.py`

```gherkin
Scenario: Call core.add_cycles() with list of cycle definitions
  Given a list of valid cycle definition dicts
  When core.add_cycles() is called with the list
  Then cycle.add_cycles() should be called
  And all cycles should be stored in cycle._cycles
  And no exceptions should be raised
  
  # Tests: Public API delegation for multiple cycles
  # Validates: core.py facade provides add_cycles() access
```

```python
def test_core_add_cycles_delegates_to_cycle_module():
    """Test that core.add_cycles() delegates to cycle.add_cycles().
    
    This test verifies that the public API function core.add_cycles()
    correctly delegates to the cycle module's add_cycles() function.
    This behaviour is expected to provide consistent bulk registration API.
    """
    setup_function()
    
    cycles_list = [
        {
            CYCLE_COMMAND: 'cmd1',
            CYCLE_NAME: 'cycle1',
            CYCLE_LOOP: lambda: True
        },
        {
            CYCLE_COMMAND: 'cmd2',
            CYCLE_NAME: 'cycle2',
            CYCLE_LOOP: lambda: False
        }
    ]
    
    core.add_cycles(cycles_list)
    
    # Verify all cycles registered
    assert 'cmd1' in cycle._cycles
    assert 'cmd2' in cycle._cycles
    assert cycle._cycles['cmd1'][CYCLE_NAME] == 'cycle1'
    assert cycle._cycles['cmd2'][CYCLE_NAME] == 'cycle2'
```

### Test 5.2.3: API consistency with add_command/add_param patterns

**File:** `tests/test_core.py`

```gherkin
Scenario: Compare add_cycle() signature with add_command()
  Given function signatures for add_cycle() and add_command()
  When comparing parameter names and types
  Then add_cycle() should follow same pattern
  And function documentation should be consistent
  And return types should match pattern
  
  # Tests: API consistency across registration functions
  # Validates: Consistent developer experience
```

```python
def test_core_api_consistency_with_add_command_pattern():
    """Test that add_cycle() follows add_command() API pattern.
    
    This test verifies that the add_cycle() and add_cycles() functions
    follow the same API patterns as add_command() and add_commands().
    This behaviour is expected to provide consistent developer experience.
    """
    setup_function()
    
    # Check function signatures match pattern
    import inspect
    
    # add_cycle() and add_command() both take single definition
    add_cycle_sig = inspect.signature(core.add_cycle)
    add_command_sig = inspect.signature(core.add_command)
    
    assert len(add_cycle_sig.parameters) == 1
    assert len(add_command_sig.parameters) == 1
    
    # add_cycles() and add_commands() both take list
    add_cycles_sig = inspect.signature(core.add_cycles)
    add_commands_sig = inspect.signature(core.add_commands)
    
    assert len(add_cycles_sig.parameters) == 1
    assert len(add_commands_sig.parameters) == 1
    
    # Verify both have docstrings
    assert core.add_cycle.__doc__ is not None
    assert core.add_cycles.__doc__ is not None
    assert len(core.add_cycle.__doc__) > 50
    assert len(core.add_cycles.__doc__) > 50
```

## Implementation Order

1. Add `add_cycle()` function to core.py (Code 5.1.1)
2. Add `add_cycles()` function to core.py (Code 5.1.2)
3. Add tests to `tests/test_core.py` (Tests 5.2.1-5.2.3)
4. Verify all tests pass

## Notes

- Pure delegation - no additional logic in core.py
- Docstrings preserved for API documentation
- Follows exact pattern of add_param/add_command functions
- Return values not needed (consistent with add_param/add_command)
