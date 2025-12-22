# Step 7: Refactored add_command()

## Overview

Refactor the main `add_command()` function to delegate all responsibilities to the extracted helpers. This creates a clean, high-level orchestrator function.

**Methods modified:**
- `add_command()` - Refactored to use all extracted helpers
  - `test_add_command_integration()` - Integration test verifying backward compatibility

With all helpers extracted and tested (Steps 1-6), this step shows the final clean implementation of `add_command()` that delegates all responsibilities to focused helper methods.

## Module-level imports

See `issue-61-step1-imports.md` for all required imports.

## Implementation

### Test 7.1: Integration test - refactored add_command maintains behaviour

```gherkin
Scenario: Refactored add_command produces identical results
  Given the same command definition
  When add_command() is called with refactored implementation
  Then command is registered identically to original implementation
  And all existing tests continue to pass
  
  # Tests: Backward compatibility
  # Validates: Refactoring doesn't change external behaviour
```

### Code 7.1: Test for refactored add_command() compatibility

```python
# Block 7.1: Add to tests/test_command.py

def test_refactored_add_command_maintains_behaviour():
    """Test that refactored add_command() produces identical results.
    
    This test verifies that the refactored implementation of add_command()
    using extracted helper methods produces the same registry state as the
    original monolithic implementation. This ensures backward compatibility
    and validates that the refactoring is purely structural with no
    functional changes.
    """
    setup_function()
    
    test_action = lambda: None
    cmd = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_ACTION: test_action,
        COMMAND_PHASE: 'test-phase'
    }
    
    command.add_command(cmd)
    
    # Verify command was registered
    assert 'test-cmd' in command._commands
    registered_cmd = command._commands['test-cmd']
    assert registered_cmd[COMMAND_NAME] == 'test-cmd'
    assert registered_cmd[COMMAND_ACTION] == test_action
    assert registered_cmd[COMMAND_PHASE] == 'test-phase'
```

### Code 7.2: Refactored add_command() using all helpers

```python
# Block 7.2: Replace add_command() in src/spafw37/command.py

def add_command(cmd):
    """Register a command for execution.
    
    A command is a dictionary that must contain at minimum:
    - COMMAND_NAME: Unique identifier for the command
    - COMMAND_ACTION: Callable function to execute
    
    Optional fields:
    - COMMAND_PHASE: Execution phase (defaults to get_default_phase())
    - COMMAND_REQUIRED_PARAMS: List of required parameter definitions
    - COMMAND_TRIGGER_PARAM: Parameter that triggers this command
    - COMMAND_GOES_BEFORE: Commands this must execute before
    - COMMAND_GOES_AFTER: Commands this must execute after
    - COMMAND_NEXT_COMMANDS: Commands to run after this one
    - COMMAND_REQUIRE_BEFORE: Commands that must have run before this
    - COMMAND_VISIBLE_IF_PARAM: Parameter controlling visibility
    - COMMAND_CYCLE: Cycle configuration for repeated execution
    
    Args:
        cmd: Command definition dictionary
        
    Raises:
        ValueError: If command name is empty
        ValueError: If command action is missing
        ValueError: If command references itself
        ValueError: If command has conflicting constraints
    """
    # Validation
    _validate_command_name(cmd)
    _validate_command_action(cmd)
    
    # Skip if already registered
    name = cmd[COMMAND_NAME]
    if name in _commands:
        return
    
    # Process inline definitions
    _process_inline_params(cmd)
    _process_inline_commands(cmd)
    
    # Validate references after inline processing
    _validate_command_references(cmd)
    
    # Assign phase and store
    _assign_command_phase(cmd)
    _store_command(cmd)
```

## Verification

After implementing Step 7:
- Run `pytest tests/test_command.py::test_refactored_add_command_maintains_behaviour -v`
- Run full test suite: `pytest tests/test_command.py -v`
- Run full project test suite: `pytest tests/ -v`
- Check coverage: `pytest --cov=spafw37 --cov-report=term-missing`

All existing tests should continue to pass with no change in behaviour.
