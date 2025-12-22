# Step 4: Inline Command Processing

This file contains the TDD implementation for extracting inline command processing from `add_command()`.

## Overview

Extract helper: `_process_inline_commands()` - Handles inline command definitions in dependency/sequencing fields

**Methods created:**
- `_normalise_command_list()` - Converts list of command defs to command names
  - `test_normalise_command_list()`
- `_process_inline_commands()` - Processes inline command definitions in all dependency fields
  - `test_process_inline_commands_goes_after()`
  - `test_process_inline_commands_multiple_fields()`
  - `test_process_inline_commands_no_inline_commands()`

## Module-level imports

See `issue-61-step1-imports.md` for all required imports.

## Implementation

### Test 4.1.1: Process dependency fields with inline command definitions

```gherkin
Scenario: Inline command definitions in dependency fields are processed
  Given a command with inline cmd defs in COMMAND_GOES_AFTER
  When _process_inline_commands() is called
  Then each inline cmd is registered via _register_inline_command()
  And COMMAND_GOES_AFTER is updated with command names
  
  # Tests: Inline command processing for dependency fields
  # Validates: Helper delegates to registration and normalises lists
```

### Code 4.1.1: Test for _process_inline_commands() with COMMAND_GOES_AFTER

```python
# Block 4.1.1: Add to tests/test_command.py

def test_process_inline_commands_goes_after():
    """Test that _process_inline_commands() handles COMMAND_GOES_AFTER.
    
    This test verifies that inline command definitions in COMMAND_GOES_AFTER
    are registered and the list is normalised to command names. This allows
    commands to define dependencies inline without pre-registration.
    """
    setup_function()
    
    inline_cmd = {
        COMMAND_NAME: 'inline-cmd',
        COMMAND_ACTION: lambda: None
    }
    cmd = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_GOES_AFTER: [inline_cmd]
    }
    
    command._process_inline_commands(cmd)
    
    # Inline command should be registered
    assert 'inline-cmd' in command._commands
    # List should be normalised to names
    assert cmd[COMMAND_GOES_AFTER] == ['inline-cmd']
```

### Test 4.1.2: Process all dependency fields

```gherkin
Scenario: All dependency fields with inline commands are processed
  Given a command with inline cmds in multiple dependency fields
  When _process_inline_commands() is called
  Then all inline cmds are registered
  And all fields are normalised to command names
  
  # Tests: Comprehensive inline command processing
  # Validates: Helper processes all dependency field types
```

### Code 4.1.2: Test for _process_inline_commands() with multiple fields

```python
# Block 4.1.2: Add to tests/test_command.py

def test_process_inline_commands_multiple_fields():
    """Test that _process_inline_commands() handles all dependency fields.
    
    This test verifies that inline command definitions in all dependency
    fields (GOES_BEFORE, GOES_AFTER, NEXT_COMMANDS, REQUIRE_BEFORE) are
    processed correctly. This ensures comprehensive inline command support.
    """
    setup_function()
    
    inline_cmd_1 = {
        COMMAND_NAME: 'inline-1',
        COMMAND_ACTION: lambda: None
    }
    inline_cmd_2 = {
        COMMAND_NAME: 'inline-2',
        COMMAND_ACTION: lambda: None
    }
    inline_cmd_3 = {
        COMMAND_NAME: 'inline-3',
        COMMAND_ACTION: lambda: None
    }
    inline_cmd_4 = {
        COMMAND_NAME: 'inline-4',
        COMMAND_ACTION: lambda: None
    }
    
    cmd = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_GOES_BEFORE: [inline_cmd_1],
        COMMAND_GOES_AFTER: [inline_cmd_2],
        COMMAND_NEXT_COMMANDS: [inline_cmd_3],
        COMMAND_REQUIRE_BEFORE: [inline_cmd_4]
    }
    
    command._process_inline_commands(cmd)
    
    # All inline commands should be registered
    assert 'inline-1' in command._commands
    assert 'inline-2' in command._commands
    assert 'inline-3' in command._commands
    assert 'inline-4' in command._commands
    # All fields should be normalised
    assert cmd[COMMAND_GOES_BEFORE] == ['inline-1']
    assert cmd[COMMAND_GOES_AFTER] == ['inline-2']
    assert cmd[COMMAND_NEXT_COMMANDS] == ['inline-3']
    assert cmd[COMMAND_REQUIRE_BEFORE] == ['inline-4']
```

### Test 4.1.3: Process command with no inline commands

```gherkin
Scenario: Command with no inline commands is unchanged
  Given a command with no dependency fields
  When _process_inline_commands() is called
  Then command dict is unchanged
  
  # Tests: No-op behaviour for commands without inline commands
  # Validates: Helper safely handles missing fields
```

### Code 4.1.3: Test for _process_inline_commands() with no inline commands

```python
# Block 4.1.3: Add to tests/test_command.py

def test_process_inline_commands_no_inline_commands():
    """Test that _process_inline_commands() handles commands with no inline cmds.
    
    This test verifies that commands without dependency fields are processed
    without errors. The helper should safely handle missing fields without
    side effects.
    """
    setup_function()
    
    cmd = {COMMAND_NAME: 'test-cmd'}
    original_cmd = cmd.copy()
    
    command._process_inline_commands(cmd)
    
    # Command should be unchanged
    assert cmd == original_cmd
```

### Test 4.1.4: Helper - normalise command list

```gherkin
Scenario: List of inline command definitions is normalised to command names
  Given a list of inline command definitions
  When _normalise_command_list() is called
  Then each command is registered via _register_inline_command()
  And a list of command names is returned
  
  # Tests: Command list normalisation helper
  # Validates: Helper extracts loop logic to avoid nesting violation
```

### Code 4.1.4: Test for _normalise_command_list() helper

```python
# Block 4.1.4: Add to tests/test_command.py

def test_normalise_command_list():
    """Test that _normalise_command_list() converts command defs to names.
    
    This test verifies that a list of inline command definitions is
    normalised to a list of command names by registering each command
    and collecting the names. This helper avoids nesting violations.
    """
    setup_function()
    
    cmd_list = [
        {COMMAND_NAME: 'cmd1', COMMAND_ACTION: lambda: None},
        {COMMAND_NAME: 'cmd2', COMMAND_ACTION: lambda: None}
    ]
    
    result = command._normalise_command_list(cmd_list)
    
    assert result == ['cmd1', 'cmd2']
    assert 'cmd1' in command._commands
    assert 'cmd2' in command._commands
```

### Code 4.1.5: Implement _normalise_command_list() helper

```python
# Block 4.1.5: Add to src/spafw37/command.py after _normalise_param_list()

def _normalise_command_list(cmd_list):
    """Normalise list of command definitions to command names.
    
    Args:
        cmd_list: List of command definition dicts
        
    Returns:
        List of command names (strings)
    """
    # Block 4.1.5.1: Initialize result list
    normalised_cmds = []
    
    # Block 4.1.5.2: Loop through command definitions
    for cmd_def in cmd_list:
        # Block 4.1.5.2.1: Register command via _register_inline_command()
        cmd_name = _register_inline_command(cmd_def)
        # Block 4.1.5.2.2: Append name to result list
        normalised_cmds.append(cmd_name)
    
    # Block 4.1.5.3: Return normalised list
    return normalised_cmds
```

### Code 4.1.6: Implement _process_inline_commands() using helper

```python
# Block 4.1.6: Add to src/spafw37/command.py after _normalise_command_list()

def _process_inline_commands(cmd):
    """Process inline command definitions in dependency/sequencing fields.
    
    Handles COMMAND_GOES_BEFORE, COMMAND_GOES_AFTER, COMMAND_NEXT_COMMANDS,
    and COMMAND_REQUIRE_BEFORE. Registers inline command definitions and
    normalises fields to command names.
    
    Args:
        cmd: Command definition dict (modified in place)
    """
    # Block 4.1.6.1: Define dependency field list
    dependency_fields = [
        COMMAND_GOES_BEFORE,
        COMMAND_GOES_AFTER,
        COMMAND_NEXT_COMMANDS,
        COMMAND_REQUIRE_BEFORE,
    ]
    # Block 4.1.6.2: Loop through each field type
    for field in dependency_fields:
        # Block 4.1.6.2.1: Get field value from command
        cmd_list = cmd.get(field, [])
        
        # Block 4.1.6.2.2: If field has values, normalise and update
        if cmd_list:
            # Block 4.1.6.2.2.1: Call _normalise_command_list() helper
            normalised_cmds = _normalise_command_list(cmd_list)
            # Block 4.1.6.2.2.2: Update cmd with normalised list
            cmd[field] = normalised_cmds
```

## Verification

After implementing Step 3:
- Run `pytest tests/test_command.py::test_process_inline_commands_goes_after -v`
- Run `pytest tests/test_command.py::test_process_inline_commands_multiple_fields -v`
- Run `pytest tests/test_command.py::test_process_inline_commands_no_inline_commands -v`
- Run full test suite: `pytest tests/test_command.py -v`

All existing tests should continue to pass.
