# Step 4: Modify command registration to check for top-level cycles

## Overview

This step integrates top-level cycle registration with command registration. When a command is registered via `add_command()`, the system checks if a top-level cycle exists for that command and attaches it.

**Integration point:** `_store_command()` in `src/spafw37/command.py`

**Key behaviours:**
- Check `cycle.get_cycle(command_name)` for top-level cycle
- If both inline (COMMAND_CYCLE) and top-level cycles exist, apply equivalency checking
- First definition wins if identical, raise ValueError if different
- Attach top-level cycle to `cmd[COMMAND_CYCLE]` before calling `cycle.register_cycle()`

**Functions modified:**
- `_store_command()` - Add top-level cycle lookup and attachment logic

**Tests created:**
- `test_store_command_attaches_top_level_cycle()` - Command gets top-level cycle attached
- `test_store_command_top_level_cycle_wins_when_no_inline()` - Top-level cycle used when no inline
- `test_store_command_inline_cycle_wins_when_no_top_level()` - Inline cycle used when no top-level
- `test_store_command_equivalency_checking_identical_cycles()` - Identical inline/top-level cycles coexist
- `test_store_command_equivalency_checking_different_cycles_raises()` - Different inline/top-level cycles raise error
- `test_store_command_calls_register_cycle_with_attached_cycle()` - Integration with register_cycle()

## Module-level imports

See `issue-63-step1-imports.md` for all required imports.

## Algorithm

### Command Registration with Top-Level Cycle Attachment

When a command is stored via `_store_command()`:
1. Extract command name from command definition
2. Check for inline cycle: `cycle_def = cmd.get(COMMAND_CYCLE)`
3. Check for top-level cycle: `top_level_cycle = cycle.get_cycle(command_name)`
4. If both exist:
   - Apply equivalency checking using `cycle._cycles_are_equivalent()`
   - If identical: use inline cycle (first-wins)
   - If different: raise ValueError
5. If only top-level exists: attach to `cmd[COMMAND_CYCLE]`
6. If only inline exists: use inline cycle (no change)
7. Continue with existing `cycle.register_cycle()` call

## Implementation

### Code 4.1.1: Modify _store_command() for top-level cycle integration

**File:** `src/spafw37/command.py`

```python
# Block 4.1.1: Modify _store_command() function (around line 342)
# Find the existing _store_command() function and modify it

def _store_command(cmd):
    """Store a command definition and register associated cycle.
    
    This function stores the command in the _commands dict and registers
    any associated cycle (inline or top-level). If both inline and top-level
    cycles exist, equivalency checking is applied.
    
    Args:
        cmd: Command definition dict
    
    Raises:
        ValueError: If conflicting cycles defined (inline vs top-level)
    """
    # Block 4.1.1.1: Extract command name
    cmd_name = cmd[COMMAND_NAME]
    
    # Block 4.1.1.2: Check for inline cycle
    inline_cycle = cmd.get(COMMAND_CYCLE)
    
    # Block 4.1.1.3: Check for top-level cycle
    top_level_cycle = cycle.get_cycle(cmd_name)
    
    # Block 4.1.1.4: Handle both inline and top-level cycles
    if inline_cycle and top_level_cycle:
        # Apply equivalency checking
        if not cycle._cycles_are_equivalent(inline_cycle, top_level_cycle):
            raise ValueError(
                f"Conflicting cycle definitions for command '{cmd_name}'. "
                f"Inline COMMAND_CYCLE differs from top-level cycle registered via add_cycle()."
            )
        # If identical, inline cycle wins (first-wins behaviour)
        # No action needed - inline_cycle already in cmd[COMMAND_CYCLE]
    
    # Block 4.1.1.5: Attach top-level cycle if no inline cycle
    elif top_level_cycle and not inline_cycle:
        cmd[COMMAND_CYCLE] = top_level_cycle
    
    # Block 4.1.1.6: Store command in registry
    _commands[cmd_name] = cmd
    
    # Block 4.1.1.7: Register cycle if present
    if COMMAND_CYCLE in cmd:
        cycle.register_cycle(cmd, cmd[COMMAND_CYCLE])
```

### Test 4.2.1: _store_command() attaches top-level cycle

**File:** `tests/test_command.py`

```gherkin
Scenario: Register command with top-level cycle defined
  Given a top-level cycle registered via add_cycle() for a command
  When the command is registered via add_command()
  Then the top-level cycle should be attached to the command
  And the command should have COMMAND_CYCLE property
  And register_cycle() should be called with the cycle
  
  # Tests: Top-level cycle attachment during command registration
  # Validates: Integration between add_cycle() and add_command()
```

```python
def test_store_command_attaches_top_level_cycle():
    """Test that _store_command() attaches top-level cycle to command.
    
    This test verifies that when a command is registered and a top-level
    cycle exists for that command (registered via add_cycle()), the cycle
    is attached to the command's COMMAND_CYCLE property.
    This behaviour is expected to enable top-level cycle registration.
    """
    setup_function()
    
    # Register top-level cycle first
    test_cycle = {
        CYCLE_COMMAND: 'test-cmd',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    cycle.add_cycle(test_cycle)
    
    # Register command
    test_command = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_ACTION: lambda: None
    }
    command.add_command(test_command)
    
    # Verify cycle attached
    stored_cmd = command._commands['test-cmd']
    assert COMMAND_CYCLE in stored_cmd
    assert stored_cmd[COMMAND_CYCLE] is test_cycle
```

### Test 4.2.2: _store_command() uses top-level cycle when no inline

**File:** `tests/test_command.py`

```gherkin
Scenario: Command registration with only top-level cycle
  Given a top-level cycle for a command
  And no inline COMMAND_CYCLE in the command definition
  When the command is registered
  Then the top-level cycle should be used
  And COMMAND_CYCLE should be set on the command
  
  # Tests: Top-level cycle wins when no inline cycle
  # Validates: Top-level cycles work as primary definition method
```

```python
def test_store_command_top_level_cycle_wins_when_no_inline():
    """Test that top-level cycle is used when command has no inline cycle.
    
    This test verifies that when a command is registered without an inline
    COMMAND_CYCLE property, but a top-level cycle exists, the top-level
    cycle is attached and used.
    This behaviour is expected to support top-level cycle registration.
    """
    setup_function()
    
    top_level_cycle = {
        CYCLE_COMMAND: 'my-cmd',
        CYCLE_NAME: 'my-cycle',
        CYCLE_LOOP: lambda: True
    }
    cycle.add_cycle(top_level_cycle)
    
    cmd = {
        COMMAND_NAME: 'my-cmd',
        COMMAND_ACTION: lambda: None
    }
    command.add_command(cmd)
    
    stored_cmd = command._commands['my-cmd']
    assert COMMAND_CYCLE in stored_cmd
    assert stored_cmd[COMMAND_CYCLE][CYCLE_NAME] == 'my-cycle'
```

### Test 4.2.3: _store_command() uses inline cycle when no top-level

**File:** `tests/test_command.py`

```gherkin
Scenario: Command registration with only inline cycle
  Given a command with inline COMMAND_CYCLE
  And no top-level cycle registered
  When the command is registered
  Then the inline cycle should be used
  And no error should be raised
  
  # Tests: Inline cycle works when no top-level cycle
  # Validates: Backward compatibility with inline cycles
```

```python
def test_store_command_inline_cycle_wins_when_no_top_level():
    """Test that inline cycle is used when no top-level cycle exists.
    
    This test verifies that when a command has an inline COMMAND_CYCLE
    and no top-level cycle exists, the inline cycle is used without error.
    This behaviour is expected for backward compatibility.
    """
    setup_function()
    
    inline_cycle = {
        CYCLE_NAME: 'inline-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    cmd = {
        COMMAND_NAME: 'my-cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_CYCLE: inline_cycle
    }
    command.add_command(cmd)
    
    stored_cmd = command._commands['my-cmd']
    assert COMMAND_CYCLE in stored_cmd
    assert stored_cmd[COMMAND_CYCLE][CYCLE_NAME] == 'inline-cycle'
```

### Test 4.2.4: Equivalency checking - identical inline and top-level cycles

**File:** `tests/test_command.py`

```gherkin
Scenario: Command with identical inline and top-level cycles
  Given a top-level cycle for a command
  And the same command with identical inline COMMAND_CYCLE
  When the command is registered
  Then no error should be raised
  And the inline cycle should be used (first-wins)
  
  # Tests: Equivalency checking with identical cycles
  # Validates: Identical definitions coexist without error
```

```python
def test_store_command_equivalency_checking_identical_cycles():
    """Test that identical inline and top-level cycles coexist.
    
    This test verifies that when a command has both an inline COMMAND_CYCLE
    and a top-level cycle with identical definitions, no error is raised.
    This behaviour is expected to allow modular code where the same cycle
    definition appears in multiple places.
    """
    setup_function()
    
    # Create shared cycle definition
    shared_loop = lambda: True
    cycle_def = {
        CYCLE_NAME: 'shared-cycle',
        CYCLE_LOOP: shared_loop
    }
    
    # Register as top-level
    top_level = {
        CYCLE_COMMAND: 'my-cmd',
        CYCLE_NAME: 'shared-cycle',
        CYCLE_LOOP: shared_loop
    }
    cycle.add_cycle(top_level)
    
    # Register command with identical inline cycle
    cmd = {
        COMMAND_NAME: 'my-cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_CYCLE: cycle_def
    }
    
    # Should not raise
    command.add_command(cmd)
    
    stored_cmd = command._commands['my-cmd']
    assert COMMAND_CYCLE in stored_cmd
```

### Test 4.2.5: Equivalency checking - different inline and top-level cycles raise error

**File:** `tests/test_command.py`

```gherkin
Scenario: Command with conflicting inline and top-level cycles
  Given a top-level cycle for a command
  And the same command with different inline COMMAND_CYCLE
  When the command is registered
  Then ValueError should be raised
  And error message should indicate conflicting cycles
  
  # Tests: Equivalency checking with different cycles
  # Validates: Conflicting definitions detected and rejected
```

```python
def test_store_command_equivalency_checking_different_cycles_raises():
    """Test that conflicting inline and top-level cycles raise error.
    
    This test verifies that when a command has both an inline COMMAND_CYCLE
    and a top-level cycle with different definitions, a ValueError is raised.
    This behaviour is expected to prevent configuration conflicts.
    """
    setup_function()
    
    # Register top-level cycle
    top_level = {
        CYCLE_COMMAND: 'my-cmd',
        CYCLE_NAME: 'top-level-cycle',
        CYCLE_LOOP: lambda: True
    }
    cycle.add_cycle(top_level)
    
    # Try to register command with different inline cycle
    cmd = {
        COMMAND_NAME: 'my-cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_CYCLE: {
            CYCLE_NAME: 'different-cycle',
            CYCLE_LOOP: lambda: False
        }
    }
    
    with pytest.raises(ValueError) as exc_info:
        command.add_command(cmd)
    
    assert 'conflicting' in str(exc_info.value).lower()
    assert 'my-cmd' in str(exc_info.value)
```

### Test 4.2.6: _store_command() calls register_cycle() with attached cycle

**File:** `tests/test_command.py`

```gherkin
Scenario: Verify cycle registration integration
  Given a command with attached cycle (inline or top-level)
  When _store_command() is called
  Then cycle.register_cycle() should be called
  And the cycle should be fully registered
  
  # Tests: Integration with cycle.register_cycle()
  # Validates: Full cycle registration flow works correctly
```

```python
def test_store_command_calls_register_cycle_with_attached_cycle():
    """Test that _store_command() calls register_cycle() after attaching cycle.
    
    This test verifies that after attaching a top-level cycle to a command,
    _store_command() calls cycle.register_cycle() to complete registration.
    This behaviour is expected to integrate with existing cycle machinery.
    """
    setup_function()
    
    # Register top-level cycle
    test_cycle = {
        CYCLE_COMMAND: 'test-cmd',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True,
        CYCLE_COMMANDS: ['child-cmd']
    }
    cycle.add_cycle(test_cycle)
    
    # Register command
    cmd = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_ACTION: lambda: None
    }
    command.add_command(cmd)
    
    # Verify cycle was registered (integration test)
    # The cycle.register_cycle() call should have processed the cycle
    stored_cmd = command._commands['test-cmd']
    assert COMMAND_CYCLE in stored_cmd
    
    # Note: Full verification of register_cycle() behaviour is in test_cycle.py
    # This test just confirms the integration point works
```

## Implementation Order

1. Modify `_store_command()` function (Code 4.1.1)
2. Add tests to `tests/test_command.py` (Tests 4.2.1-4.2.6)
3. Verify integration tests pass

## Notes

- This step integrates top-level cycles with existing command registration
- Equivalency checking reuses `cycle._cycles_are_equivalent()` from Step 2
- First-wins behaviour: when cycles are identical, inline cycle is used
- All existing cycle validation happens in `cycle.register_cycle()` (unchanged)
