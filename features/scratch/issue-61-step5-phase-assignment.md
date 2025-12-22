# Step 5: Phase Assignment

This file contains the TDD implementation for extracting phase assignment from `add_command()`.

## Overview

Extract helper: `_assign_command_phase()` - Sets default phase if not specified

**Methods created:**
- `_assign_command_phase()` - Assigns default phase when missing
  - `test_assign_command_phase_missing_phase()`
  - `test_assign_command_phase_existing_phase()`

## Module-level imports

See `issue-61-step1-imports.md` for all required imports.

## Implementation

### Test 5.1.1: Assign default phase when not specified

```gherkin
Scenario: Default phase is assigned when COMMAND_PHASE is missing
  Given a command without COMMAND_PHASE
  When _assign_command_phase() is called
  Then COMMAND_PHASE is set to config.get_default_phase()
  
  # Tests: Default phase assignment
  # Validates: Helper delegates to config module for default value
```

### Code 5.1.1: Test for _assign_command_phase() with missing phase

```python
# Block 5.1.1: Add to tests/test_command.py

def test_assign_command_phase_missing_phase():
    """Test that _assign_command_phase() assigns default when phase missing.
    
    This test verifies that commands without COMMAND_PHASE are assigned the
    default phase from config.get_default_phase(). This ensures all commands
    have a phase assigned before registration.
    """
    setup_function()
    
    cmd = {COMMAND_NAME: 'test-cmd'}
    
    command._assign_command_phase(cmd)
    
    # Phase should be assigned
    assert COMMAND_PHASE in cmd
    assert cmd[COMMAND_PHASE] == config.get_default_phase()
```

### Test 5.1.2: Preserve existing phase

```gherkin
Scenario: Existing COMMAND_PHASE is preserved
  Given a command with COMMAND_PHASE already set
  When _assign_command_phase() is called
  Then COMMAND_PHASE remains unchanged
  
  # Tests: Phase preservation
  # Validates: Helper doesn't override explicit phase values
```

### Code 5.1.2: Test for _assign_command_phase() with existing phase

```python
# Block 5.1.2: Add to tests/test_command.py

def test_assign_command_phase_existing_phase():
    """Test that _assign_command_phase() preserves existing phase.
    
    This test verifies that commands with COMMAND_PHASE already set are not
    modified. The helper should only assign defaults for missing phases and
    respect explicit phase assignments.
    """
    setup_function()
    
    cmd = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_PHASE: 'custom-phase'
    }
    
    command._assign_command_phase(cmd)
    
    # Phase should be unchanged
    assert cmd[COMMAND_PHASE] == 'custom-phase'
```

### Code 5.1.3: Implement _assign_command_phase() helper

```python
# Block 5.1.3: Add to src/spafw37/command.py after _process_inline_commands()

def _assign_command_phase(cmd):
    """Assign default phase if not specified in command.
    
    Sets COMMAND_PHASE to config.get_default_phase() if not already present.
    
    Args:
        cmd: Command definition dict (modified in place)
    """
    # Block 5.1.3.1: Check if phase is missing or empty
    if not cmd.get(COMMAND_PHASE):
        # Block 5.1.3.2: Assign default phase from config
        cmd[COMMAND_PHASE] = config.get_default_phase()
```

## Verification

After implementing Step 4:
- Run `pytest tests/test_command.py::test_assign_command_phase_missing_phase -v`
- Run `pytest tests/test_command.py::test_assign_command_phase_existing_phase -v`
- Run full test suite: `pytest tests/test_command.py -v`

All existing tests should continue to pass.
