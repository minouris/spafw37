# Step 3: Verify inline command support in CYCLE_COMMANDS

## Overview

This step verifies that commands can be defined inline within the **CYCLE_COMMANDS** list of cycle definitions, similar to how params can be defined inline in `COMMAND_REQUIRED_PARAMS`.

**Important distinction:**
- **CYCLE_COMMAND** (singular): The target command the cycle attaches to - inline support was added in Step 2
- **CYCLE_COMMANDS** (plural): The list of commands within the cycle - this step verifies inline support works

Commands in `CYCLE_COMMANDS` can be dicts (inline definitions) or strings (command name references).

**Note:** The existing `register_cycle()` function in `cycle.py` already supports inline command definitions in CYCLE_COMMANDS through the `_mark_cycle_commands_not_invocable()` helper. This step creates integration tests to verify that functionality works correctly with top-level cycles registered via `add_cycle()`.

**Tests created:**
- `test_cycle_with_inline_commands_in_cycle_commands()` - Cycle with inline command in CYCLE_COMMANDS list
- `test_cycle_with_mixed_inline_and_string_in_cycle_commands()` - Mix of dicts and strings in CYCLE_COMMANDS
- `test_cycle_with_inline_command_forward_reference()` - Inline command referencing not-yet-defined param

## Module-level imports

See `issue-63-step1-imports.md` for all required imports.

## Algorithm

### Inline Command Support in CYCLE_COMMANDS

The existing `register_cycle()` function already handles inline command definitions in the CYCLE_COMMANDS list:
1. When a cycle is registered (via `_store_command()` calling `cycle.register_cycle()`)
2. `register_cycle()` processes the cycle and calls `_mark_cycle_commands_not_invocable()`
3. `_mark_cycle_commands_not_invocable()` handles both inline dicts and string references in CYCLE_COMMANDS
4. Inline commands in CYCLE_COMMANDS are added directly to commands_dict (line 225 in cycle.py)

**For top-level cycles:**
- Cycles registered via `add_cycle()` are stored in `_cycles` dict
- When command is registered, cycle is attached and `register_cycle()` is called
- At that point, inline commands in CYCLE_COMMANDS are processed normally

**Key insight:** No new code needed in `cycle.py` for inline command support in CYCLE_COMMANDS. The existing machinery works. We just need integration tests to verify it works with top-level cycles.

## Implementation

### Test 3.2.1: Inline command definition in CYCLE_COMMANDS

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Cycle with inline command in CYCLE_COMMANDS
  Given a cycle with CYCLE_COMMANDS containing command dict
  When the cycle is registered via add_cycle()
  Then the cycle should be stored successfully
  And the inline command definition should be preserved
  And no exceptions should be raised
  
  # Tests: Inline command definition support in CYCLE_COMMANDS
  # Validates: Commands can be defined inline in CYCLE_COMMANDS list
```

```python
def test_cycle_with_inline_commands_in_cycle_commands():
    """Test that cycles can contain inline command definitions in CYCLE_COMMANDS.
    
    This test verifies that when a cycle definition includes inline command
    definitions in CYCLE_COMMANDS (as dicts rather than name strings), the
    cycle is stored successfully with the inline commands preserved.
    This behaviour is expected because inline definitions are processed when
    the cycle is attached to a command during command registration.
    """
    setup_function()
    
    test_cycle = {
        CYCLE_COMMAND: 'parent-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True,
        CYCLE_COMMANDS: [
            {
                COMMAND_NAME: 'inline-command',
                COMMAND_ACTION: lambda: None
            }
        ]
    }
    
    cycle.add_cycle(test_cycle)
    
    retrieved_cycle = cycle.get_cycle('parent-command')
    assert retrieved_cycle is not None
    assert CYCLE_COMMANDS in retrieved_cycle
    assert isinstance(retrieved_cycle[CYCLE_COMMANDS], list)
    assert len(retrieved_cycle[CYCLE_COMMANDS]) == 1
    assert isinstance(retrieved_cycle[CYCLE_COMMANDS][0], dict)
```

### Test 3.2.2: Mixed inline and string command references in CYCLE_COMMANDS

**File:** `tests/test_cycle.py`

```gherkin
Scenario: CYCLE_COMMANDS with both dicts and strings
  Given a cycle with CYCLE_COMMANDS containing mix of dicts and strings
  When the cycle is registered via add_cycle()
  Then the cycle should be stored successfully
  And both inline and referenced commands should be preserved
  And no exceptions should be raised
  
  # Tests: Mixed command definition formats in CYCLE_COMMANDS
  # Validates: Flexibility in specifying commands within cycle
```

```python
def test_cycle_with_mixed_inline_and_string_in_cycle_commands():
    """Test that CYCLE_COMMANDS can contain both inline dicts and string references.
    
    This test verifies that when CYCLE_COMMANDS contains a mix of inline command
    definitions (dicts) and command name references (strings), the cycle is
    stored successfully with both formats preserved.
    This behaviour is expected to provide maximum flexibility.
    """
    setup_function()
    
    test_cycle = {
        CYCLE_COMMAND: 'parent-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True,
        CYCLE_COMMANDS: [
            {
                COMMAND_NAME: 'inline-cmd',
                COMMAND_ACTION: lambda: None
            },
            'string-ref-cmd'
        ]
    }
    
    cycle.add_cycle(test_cycle)
    
    retrieved_cycle = cycle.get_cycle('parent-command')
    assert retrieved_cycle is not None
    assert len(retrieved_cycle[CYCLE_COMMANDS]) == 2
    assert isinstance(retrieved_cycle[CYCLE_COMMANDS][0], dict)
    assert isinstance(retrieved_cycle[CYCLE_COMMANDS][1], str)
```

### Test 3.2.3: Validation deferred for inline commands in CYCLE_COMMANDS

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Inline command with forward reference to param
  Given a cycle with inline command referencing param not yet defined
  When the cycle is registered via add_cycle()
  Then the cycle should be stored successfully
  And no validation error should be raised
  
  # Tests: Deferred validation of inline command definitions
  # Validates: Allows flexible registration order
```

```python
def test_add_cycle_with_inline_command_forward_reference():
    """Test that inline commands can reference not-yet-defined parameters.
    
    This test verifies that when a cycle contains an inline command definition
    that references a parameter not yet registered, add_cycle() does not raise
    a validation error. The command reference is validated later when the cycle
    is attached to a command during command registration.
    This behaviour is expected to allow flexible registration order.
    """
    setup_function()
    
    test_cycle = {
        CYCLE_COMMAND: 'parent-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True,
        CYCLE_COMMANDS: [
            {
                COMMAND_NAME: 'inline-command',
                COMMAND_ACTION: lambda: None,
                COMMAND_REQUIRED_PARAMS: ['future-param']
            }
        ]
    }
    
    # Should not raise - validation deferred until command registration
    cycle.add_cycle(test_cycle)
    
    retrieved_cycle = cycle.get_cycle('parent-command')
    assert retrieved_cycle is not None
```

## Implementation Order

No new implementation code required. Tests verify that existing inline command support works with top-level cycles.

1. Add test for inline command definitions (Test 3.2.1)
2. Add test for mixed inline/string commands (Test 3.2.2)
3. Add test for deferred validation (Test 3.2.3)
