# Step 6: Command Storage

This file contains the TDD implementation for extracting command storage from `add_command()`.

## Overview

Extract helper: `_store_command()` - Registry storage and cycle registration

## Module-level imports

See `issue-61-step1-imports.md` for all required imports.

## Implementation

### Test 6.1.1: Store command in registry

```gherkin
Scenario: Command is stored in registry
  Given a command definition
  When _store_command() is called
  Then command is added to _commands dict with name as key
  
  # Tests: Registry storage
  # Validates: Helper stores command in module-level registry
```

### Code 6.1.1: Test for _store_command() registry storage

```python
# Block 6.1.1: Add to tests/test_command.py

def test_store_command_registry_storage():
    """Test that _store_command() stores command in registry.
    
    This test verifies that commands are stored in the module-level _commands
    dictionary with the command name as the key. This is the primary storage
    mechanism for command registration.
    """
    setup_function()
    
    cmd = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_PHASE: 'test-phase'
    }
    
    command._store_command(cmd)
    
    # Command should be in registry
    assert 'test-cmd' in command._commands
    assert command._commands['test-cmd'] == cmd
```

### Test 6.1.2: Register cycle if present

```gherkin
Scenario: Command with cycle triggers cycle registration
  Given a command definition with COMMAND_CYCLE
  When _store_command() is called
  Then cycle.register_cycle() is called with command and registry
  
  # Tests: Cycle registration delegation
  # Validates: Helper delegates cycle registration to cycle module
```

### Code 6.1.2: Test for _store_command() with cycle registration

```python
# Block 6.1.2: Add to tests/test_command.py

def test_store_command_cycle_registration():
    """Test that _store_command() registers cycles when present.
    
    This test verifies that commands with COMMAND_CYCLE trigger cycle
    registration by calling cycle.register_cycle(). This ensures cycle
    functionality is properly initialised during command registration.
    """
    setup_function()
    
    cmd = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_ACTION: lambda: None,
        COMMAND_PHASE: 'test-phase',
        COMMAND_CYCLE: {
            'start': 1,
            'end': 10
        }
    }
    
    command._store_command(cmd)
    
    # Command should be in registry
    assert 'test-cmd' in command._commands
    # Note: cycle.register_cycle() is called internally
    # Full cycle behaviour is tested in cycle module tests
```

### Code 6.1.3: Implement _store_command() helper

```python
# Block 6.1.3: Add to src/spafw37/command.py after _assign_command_phase()

def _store_command(cmd):
    """Store command in registry and register cycle if present.
    
    Adds command to _commands dict and calls cycle.register_cycle() if needed.
    
    Args:
        cmd: Command definition dict
    """
    name = cmd[COMMAND_NAME]
    _commands[name] = cmd
    
    # Register cycle if present
    cycle.register_cycle(cmd, _commands)
```

## Verification

After implementing Step 5:
- Run `pytest tests/test_command.py::test_store_command_registry_storage -v`
- Run `pytest tests/test_command.py::test_store_command_cycle_registration -v`
- Run full test suite: `pytest tests/test_command.py -v`

All existing tests should continue to pass.
