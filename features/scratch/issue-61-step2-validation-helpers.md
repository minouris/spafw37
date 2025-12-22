# Step 2: Validation Helpers Implementation

## Overview

Extract the three validation helpers that check command definition properties. These are the simplest extractions with clear boundaries.

**Methods created:**
- `_validate_command_name()` - Validates command has non-empty name
  - `test_validate_command_name_empty_string_raises_error()`
  - `test_validate_command_name_none_raises_error()`
- `_validate_command_action()` - Validates command has action function
  - `test_validate_command_action_missing_raises_error()`
  - `test_validate_command_action_none_raises_error()`
- `_validate_command_references()` - Validates no self-references or conflicts
  - `test_validate_command_references_self_reference_raises_error()`
  - `test_validate_command_references_conflicting_constraints_raises_error()`

## Module-level imports

See `issue-61-step1-imports.md` for all required imports.

## Implementation

### Test 2.1.1: Name validation - empty string

```gherkin
Scenario: Empty command name raises ValueError
  Given a command definition with empty string name
  When _validate_command_name() is called
  Then ValueError is raised with "Command name cannot be empty"
  
  # Tests: Name validation enforcement
  # Validates: Helper catches empty command names
```

### Code 2.1.1: Test for _validate_command_name() with empty string

```python
# Block 2.1.1: Add to tests/test_command.py

def test_validate_command_name_empty_string_raises_error():
    """Test that _validate_command_name() raises ValueError for empty string.
    
    This test verifies that the validation helper correctly rejects command
    definitions with empty string names. Empty names would cause registry
    lookup failures and must be caught early.
    """
    setup_function()
    
    empty_name_command = {COMMAND_NAME: ''}
    with pytest.raises(ValueError, match="Command name cannot be empty"):
        command._validate_command_name(empty_name_command)
```

### Test 2.1.2: Name validation - None value

```gherkin
Scenario: None command name raises ValueError
  Given a command definition with None as name value
  When _validate_command_name() is called
  Then ValueError is raised with "Command name cannot be empty"
  
  # Tests: Name validation enforcement
  # Validates: Helper catches None command names
```

### Code 2.1.2: Test for _validate_command_name() with None

```python
# Block 2.1.2: Add to tests/test_command.py

def test_validate_command_name_none_raises_error():
    """Test that _validate_command_name() raises ValueError for None name.
    
    This test verifies that the validation helper correctly rejects command
    definitions with None as the name value. None names would cause registry
    lookup failures and must be caught early.
    """
    setup_function()
    
    none_name_command = {COMMAND_NAME: None}
    with pytest.raises(ValueError, match="Command name cannot be empty"):
        command._validate_command_name(none_name_command)
```

### Code 2.1.3: Implement _validate_command_name() helper

```python
# Block 2.1.3: Add to src/spafw37/command.py before add_command()

def _validate_command_name(cmd):
    """Validate that command has a non-empty name.
    
    Args:
        cmd: Command definition dict
        
    Raises:
        ValueError: If command name is empty or None
    """
    # Block 2.1.3.1: Get command name
    name = cmd.get(COMMAND_NAME)
    
    # Block 2.1.3.2: Validate non-empty
    if not name:
        raise ValueError("Command name cannot be empty")
```

### Test 2.2.1: Action validation - missing key

```gherkin
Scenario: Missing command action raises ValueError
  Given a command definition without COMMAND_ACTION key
  When _validate_command_action() is called
  Then ValueError is raised with "Command action is required"
  
  # Tests: Action validation enforcement
  # Validates: Helper catches missing action key
```

### Code 2.2.1: Test for _validate_command_action() with missing action

```python
# Block 2.2.1: Add to tests/test_command.py

def test_validate_command_action_missing_raises_error():
    """Test that _validate_command_action() raises ValueError for missing action.
    
    This test verifies that the validation helper correctly rejects command
    definitions without the COMMAND_ACTION key. Commands without actions cannot
    be executed and must be caught during registration.
    """
    setup_function()
    
    no_action_command = {COMMAND_NAME: 'test-cmd'}
    with pytest.raises(ValueError, match="Command action is required"):
        command._validate_command_action(no_action_command)
```

### Test 2.2.2: Action validation - None value

```gherkin
Scenario: None command action raises ValueError
  Given a command definition with None as action value
  When _validate_command_action() is called
  Then ValueError is raised with "Command action is required"
  
  # Tests: Action validation enforcement
  # Validates: Helper catches None action value
```

### Code 2.2.2: Test for _validate_command_action() with None action

```python
# Block 2.2.2: Add to tests/test_command.py

def test_validate_command_action_none_raises_error():
    """Test that _validate_command_action() raises ValueError for None action.
    
    This test verifies that the validation helper correctly rejects command
    definitions with None as the action value. Commands with None actions cannot
    be executed and must be caught during registration.
    """
    setup_function()
    
    none_action_command = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_ACTION: None
    }
    with pytest.raises(ValueError, match="Command action is required"):
        command._validate_command_action(none_action_command)
```

### Code 2.2.3: Implement _validate_command_action() helper

```python
# Block 2.2.3: Add to src/spafw37/command.py after _validate_command_name()

def _validate_command_action(cmd):
    """Validate that command has an action function.
    
    Args:
        cmd: Command definition dict
        
    Raises:
        ValueError: If command action is missing or None
    """
    # Block 2.2.3.1: Validate action exists
    if not cmd.get(COMMAND_ACTION):
        raise ValueError("Command action is required")
```

### Test 2.3.1: Reference validation - self-reference

```gherkin
Scenario: Self-referencing command raises ValueError
  Given a command definition with its own name in COMMAND_GOES_AFTER
  When _validate_command_references() is called
  Then ValueError is raised with "cannot reference itself"
  
  # Tests: Self-reference detection
  # Validates: Helper catches circular dependency at definition time
```

### Code 2.3.1: Test for _validate_command_references() with self-reference

```python
# Block 2.3.1: Add to tests/test_command.py

def test_validate_command_references_self_reference_raises_error():
    """Test that _validate_command_references() raises ValueError for self-references.
    
    This test verifies that the validation helper correctly detects and rejects
    commands that reference themselves in dependency fields. Self-references would
    create immediate circular dependencies that cannot be resolved.
    """
    setup_function()
    
    self_ref_command = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_GOES_AFTER: ['test-cmd']
    }
    with pytest.raises(ValueError, match="cannot reference itself"):
        command._validate_command_references(self_ref_command)
```

### Test 2.3.2: Reference validation - conflicting constraints

```gherkin
Scenario: Conflicting sequencing constraints raise ValueError
  Given a command definition with same command in GOES_BEFORE and GOES_AFTER
  When _validate_command_references() is called
  Then ValueError is raised with "conflicting constraints"
  
  # Tests: Constraint conflict detection
  # Validates: Helper catches impossible sequencing requirements
```

### Code 2.3.2: Test for _validate_command_references() with conflicting constraints

```python
# Block 2.3.2: Add to tests/test_command.py

def test_validate_command_references_conflicting_constraints_raises_error():
    """Test that _validate_command_references() raises ValueError for conflicts.
    
    This test verifies that the validation helper correctly detects impossible
    sequencing constraints where the same command appears in both GOES_BEFORE
    and GOES_AFTER lists. These conflicting requirements cannot be satisfied.
    """
    setup_function()
    
    conflicting_command = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_GOES_BEFORE: ['other-cmd'],
        COMMAND_GOES_AFTER: ['other-cmd']
    }
    with pytest.raises(ValueError, match="conflicting constraints"):
        command._validate_command_references(conflicting_command)
```

### Code 2.3.3: Implement _validate_command_references() helper

```python
# Block 2.3.3: Add to src/spafw37/command.py after _validate_command_action()

def _validate_command_references(cmd):
    """Validate command dependency references.
    
    Checks for self-references and conflicting sequencing constraints.
    
    Args:
        cmd: Command definition dict
        
    Raises:
        ValueError: If command references itself or has conflicting constraints
    """
    # Block 2.3.3.1: Get command name
    name = cmd.get(COMMAND_NAME)
    
    # Block 2.3.3.2: Check for self-references in all fields
    reference_fields = [
        COMMAND_GOES_AFTER,
        COMMAND_GOES_BEFORE,
        COMMAND_NEXT_COMMANDS,
        COMMAND_REQUIRE_BEFORE
    ]
    for field in reference_fields:
        references = cmd.get(field, []) or []
        if name in references:
            raise ValueError(f"Command '{name}' cannot reference itself")
    
    # Block 2.3.3.3: Get GOES_BEFORE and GOES_AFTER sets
    goes_before = set(cmd.get(COMMAND_GOES_BEFORE, []) or [])
    goes_after = set(cmd.get(COMMAND_GOES_AFTER, []) or [])
    
    # Block 2.3.3.4: Check for conflicting constraints
    conflicting_commands = goes_before & goes_after
    if conflicting_commands:
        raise ValueError(
            f"Command '{name}' has conflicting constraints with: "
            f"{list(conflicting_commands)}"
        )
```

## Verification

After implementing Step 1:
- Run `pytest tests/test_command.py::test_validate_command_name_empty_string_raises_error -v`
- Run `pytest tests/test_command.py::test_validate_command_name_none_raises_error -v`
- Run `pytest tests/test_command.py::test_validate_command_action_missing_raises_error -v`
- Run `pytest tests/test_command.py::test_validate_command_action_none_raises_error -v`
- Run `pytest tests/test_command.py::test_validate_command_references_self_reference_raises_error -v`
- Run `pytest tests/test_command.py::test_validate_command_references_conflicting_constraints_raises_error -v`
- Run full test suite: `pytest tests/test_command.py -v`

All existing tests should continue to pass.
