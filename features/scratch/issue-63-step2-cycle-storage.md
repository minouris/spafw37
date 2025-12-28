### Step 2: Add cycle storage and registration functions to cycle.py

#### Overview

This step adds the foundational infrastructure for registering cycles via top-level API, including support for inline command definitions in the CYCLE_COMMAND field.

**Module-level constants and storage:**
- `_cycles` dict - Stores registered cycles indexed by command name

**Public functions created:**
- `add_cycle(cycle_def)` - Register single cycle definition
  - Supports inline CYCLE_COMMAND definitions (dict) in addition to string references
  - `test_add_cycle_module_level_storage_initialised()`
  - `test_add_cycle_registers_single_cycle()`
  - `test_add_cycle_with_inline_cycle_command_definition()`
  - `test_add_cycle_with_inline_cycle_command_extracts_name()`
  - `test_add_cycle_validates_required_cycle_command_field()`
  - `test_add_cycle_validates_required_cycle_name_field()`
  - `test_add_cycle_validates_required_cycle_loop_field()`
- `add_cycles(cycle_defs)` - Register multiple cycle definitions
  - `test_add_cycles_registers_multiple_cycles()`
  - `test_add_cycles_with_mixed_inline_and_string_cycle_commands()`
- `get_cycle(command_name)` - Retrieve registered cycle by command name
  - `test_get_cycle_retrieves_registered_cycle()`
  - `test_get_cycle_returns_none_for_unregistered_command()`

**Private helper functions created:**
- `_validate_cycle_required_fields(cycle_def)` - Validate required fields exist
  - `test_validate_cycle_required_fields_accepts_valid_cycle()`
  - `test_validate_cycle_required_fields_rejects_missing_cycle_command()`
  - `test_validate_cycle_required_fields_rejects_missing_cycle_name()`
  - `test_validate_cycle_required_fields_rejects_missing_cycle_loop()`
- `_cycles_are_equivalent(cycle1, cycle2)` - Deep equality check for cycles
  - `test_cycles_are_equivalent_returns_true_for_identical_cycles()`
  - `test_cycles_are_equivalent_returns_false_for_different_required_fields()`
  - `test_cycles_are_equivalent_returns_false_for_different_optional_fields()`
  - `test_cycles_are_equivalent_compares_function_references()`
- `_extract_command_name(command_ref)` - Extract command name from string or dict
  - `test_extract_command_name_from_string()`
  - `test_extract_command_name_from_dict()`
  - `test_extract_command_name_validates_dict_has_command_name()`

#### Module-level imports

See `issue-63-step1-imports.md` for all required imports.

**Additional imports needed for inline CYCLE_COMMAND support:**
```python
from spafw37 import command  # For command._register_inline_command()
from spafw37.constants.command import COMMAND_NAME
```

#### Algorithm

##### Cycle Registration Flow

1. **Inline command handling**: If CYCLE_COMMAND is a dict (inline definition):
   - Register the command using `command._register_inline_command()`
   - Extract command name from the inline definition
2. **Validation**: Check required fields (CYCLE_COMMAND, CYCLE_NAME, CYCLE_LOOP)
3. **Command name extraction**: Extract command name from CYCLE_COMMAND (string or dict)
4. **Duplicate check**: If cycle already registered for command:
   - Compare for deep equality using `_cycles_are_equivalent()`
   - If identical: silently skip (first-wins)
   - If different: raise ValueError
5. **Storage**: Store cycle in `_cycles` dict indexed by command name

##### Equivalency Checking Algorithm

Deep comparison of two cycle definitions:
1. Compare all keys (both required and optional fields)
2. For each key:
   - Compare primitive values (strings, numbers) with `==`
   - Compare function references with `is` (object identity)
   - Compare lists/dicts recursively
3. Return True only if ALL fields match

#### Implementation

##### Code 2.1: Module-level storage

**File:** `src/spafw37/cycle.py`

```python
### Block 2.1.1: Module-level cycle storage dictionary
### Add after existing module state declarations (around line 45)

_cycles = {}  # Stores cycles indexed by command name
```

##### Test 2.2.1: Module-level cycles storage initialised

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Module-level _cycles dict exists
  Given the cycle module is imported
  When the module is loaded
  Then _cycles dict should exist at module level
  And _cycles dict should be empty initially
  
  # Tests: Module-level storage initialization
  # Validates: Infrastructure for storing registered cycles
```

```python
def test_add_cycle_module_level_storage_initialised():
    """Test that module-level _cycles storage is initialised.
    
    This test verifies that the _cycles dictionary exists at module level
    and is initially empty when the module is first imported.
    This behaviour is expected because cycles are registered dynamically at runtime.
    """
    setup_function()
    assert hasattr(cycle, '_cycles')
    assert isinstance(cycle._cycles, dict)
    assert len(cycle._cycles) == 0
```

##### Code 2.3.1: add_cycle() - Main registration function

**File:** `src/spafw37/cycle.py`

```python
### Block 2.3.1: Add cycle registration function
### Add after _get_cycle_from_command() function (around line 105)

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
    """
    # Block 2.3.1.1: Validate required fields
    _validate_cycle_required_fields(cycle_def)
    
    # Block 2.3.1.2: Handle inline CYCLE_COMMAND definition
    command_ref = cycle_def[CYCLE_COMMAND]
    if isinstance(command_ref, dict):
        command._register_inline_command(command_ref)
    
    # Block 2.3.1.3: Extract command name
    command_name = _extract_command_name(command_ref)
    
    # Block 2.3.1.4: Check for existing cycle and apply equivalency checking
    if command_name in _cycles:
        existing_cycle = _cycles[command_name]
        if _cycles_are_equivalent(existing_cycle, cycle_def):
            return
        raise ValueError(
            f"Conflicting cycle definition for command '{command_name}'. "
            f"A different cycle is already registered for this command."
        )
    
    # Block 2.3.1.5: Store cycle indexed by command name
    _cycles[command_name] = cycle_def
```

##### Test 2.3.2: add_cycle() registers single cycle definition

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Register single cycle via add_cycle()
  Given a valid cycle definition with CYCLE_COMMAND and CYCLE_NAME
  When add_cycle() is called with the cycle dict
  Then the cycle should be stored in _cycles indexed by command name
  And no exceptions should be raised
  
  # Tests: Single cycle registration via add_cycle()
  # Validates: Basic cycle storage mechanism works correctly
```

```python
def test_add_cycle_registers_single_cycle():
    """Test that add_cycle() registers a single cycle definition.
    
    This test verifies that when a valid cycle definition is passed to add_cycle(),
    it is stored in the _cycles dictionary indexed by the command name.
    This behaviour is expected because cycles must be associated with specific commands.
    """
    setup_function()
    
    test_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    cycle.add_cycle(test_cycle)
    
    assert 'test-command' in cycle._cycles
    assert cycle._cycles['test-command'] == test_cycle
```

##### Test 2.3.7: add_cycle() with inline CYCLE_COMMAND definition

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Register cycle with inline CYCLE_COMMAND
  Given a cycle with CYCLE_COMMAND as inline command dict
  When add_cycle() is called
  Then the inline command should be registered
  And the cycle should be stored indexed by the command name from the inline definition
  And no exceptions should be raised
  
  # Tests: Inline CYCLE_COMMAND definition support
  # Validates: CYCLE_COMMAND can be dict (inline) or string (reference)
```

```python
def test_add_cycle_with_inline_cycle_command_definition():
    """Test that add_cycle() handles inline CYCLE_COMMAND definitions.
    
    This test verifies that when CYCLE_COMMAND is provided as a dict
    (inline command definition) rather than a string, the command is
    registered and the cycle is stored correctly.
    This behaviour is expected to allow defining commands and cycles together.
    """
    setup_function()
    
    test_cycle = {
        CYCLE_COMMAND: {
            COMMAND_NAME: 'inline-parent',
            COMMAND_ACTION: lambda: None
        },
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    cycle.add_cycle(test_cycle)
    
    # Cycle should be stored indexed by extracted command name
    assert 'inline-parent' in cycle._cycles
    assert cycle._cycles['inline-parent'] == test_cycle
    
    # Command should be registered
    assert 'inline-parent' in command._commands
```

##### Test 2.3.6: add_cycle() extracts name from inline CYCLE_COMMAND

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Extract command name from inline CYCLE_COMMAND
  Given a cycle with CYCLE_COMMAND as dict containing COMMAND_NAME
  When add_cycle() is called
  Then the command name should be extracted from the inline definition
  And the cycle should be indexed by that name
  
  # Tests: Command name extraction from inline definitions
  # Validates: Proper indexing of cycles with inline commands
```

```python
def test_add_cycle_with_inline_cycle_command_extracts_name():
    """Test that add_cycle() extracts command name from inline CYCLE_COMMAND.
    
    This test verifies that when CYCLE_COMMAND is an inline definition (dict),
    the command name is correctly extracted from the COMMAND_NAME field
    and used to index the cycle in storage.
    This behaviour is expected for proper cycle-command association.
    """
    setup_function()
    
    inline_command_def = {
        COMMAND_NAME: 'extracted-name',
        COMMAND_ACTION: lambda: None
    }
    
    test_cycle = {
        CYCLE_COMMAND: inline_command_def,
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    cycle.add_cycle(test_cycle)
    
    # Should be indexed by extracted name, not inline dict object
    assert 'extracted-name' in cycle._cycles
    stored_cycle = cycle._cycles['extracted-name']
    assert stored_cycle[CYCLE_COMMAND] is inline_command_def
```

##### Test 2.3.7: add_cycle() validates required CYCLE_COMMAND field

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Missing CYCLE_COMMAND field
  Given a cycle definition without CYCLE_COMMAND field
  When add_cycle() is called
  Then ValueError should be raised
  And error message should indicate missing CYCLE_COMMAND
  
  # Tests: Required field validation
  # Validates: Cannot register cycle without a target command
```

```python
def test_add_cycle_validates_required_cycle_command_field():
    """Test that add_cycle() validates CYCLE_COMMAND field is present.
    
    This test verifies that when a cycle definition is missing the required
    CYCLE_COMMAND field, a ValueError is raised with an appropriate error message.
    This behaviour is expected because cycles must be associated with a command.
    """
    setup_function()
    
    invalid_cycle = {
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    with pytest.raises(ValueError) as exc_info:
        cycle.add_cycle(invalid_cycle)
    
    assert 'CYCLE_COMMAND' in str(exc_info.value)
```

##### Test 2.3.6: add_cycle() validates required CYCLE_NAME field

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Missing CYCLE_NAME field
  Given a cycle definition without CYCLE_NAME field
  When add_cycle() is called
  Then ValueError should be raised
  And error message should indicate missing CYCLE_NAME
  
  # Tests: Required field validation for cycle identifier
  # Validates: Cycles must have independent identifiers
```

```python
def test_add_cycle_validates_required_cycle_name_field():
    """Test that add_cycle() validates CYCLE_NAME field is present.
    
    This test verifies that when a cycle definition is missing the required
    CYCLE_NAME field, a ValueError is raised with an appropriate error message.
    This behaviour is expected because cycles need independent identifiers.
    """
    setup_function()
    
    invalid_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_LOOP: lambda: True
    }
    
    with pytest.raises(ValueError) as exc_info:
        cycle.add_cycle(invalid_cycle)
    
    assert 'CYCLE_NAME' in str(exc_info.value)
```

##### Test 2.3.7: add_cycle() validates required CYCLE_LOOP field

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Missing CYCLE_LOOP field
  Given a cycle definition without CYCLE_LOOP field
  When add_cycle() is called
  Then ValueError should be raised
  And error message should indicate missing CYCLE_LOOP
  
  # Tests: Required field validation for loop function
  # Validates: Cycles must define loop behaviour
```

```python
def test_add_cycle_validates_required_cycle_loop_field():
    """Test that add_cycle() validates CYCLE_LOOP field is present.
    
    This test verifies that when a cycle definition is missing the required
    CYCLE_LOOP field, a ValueError is raised with an appropriate error message.
    This behaviour is expected because cycles must define loop behaviour.
    """
    setup_function()
    
    invalid_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle'
    }
    
    with pytest.raises(ValueError) as exc_info:
        cycle.add_cycle(invalid_cycle)
    
    assert 'CYCLE_LOOP' in str(exc_info.value)
```

##### Test 2.3.6: Equivalency checking - identical cycles silently skip

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Register identical cycle definition twice
  Given a cycle definition registered for a command
  When add_cycle() is called again with identical definition
  Then the second registration should be silently skipped
  And no exception should be raised
  And the original cycle should remain in _cycles
  
  # Tests: Equivalency checking with first-wins behaviour
  # Validates: Identical definitions don't cause errors (useful for modular code)
```

```python
def test_add_cycle_equivalency_checking_identical_cycles_skip():
    """Test that registering an identical cycle definition is silently skipped.
    
    This test verifies that when add_cycle() is called twice with the exact same
    cycle definition for a command, the second registration is silently skipped.
    This behaviour is expected to allow modular code where the same cycle definition
    might appear in multiple places without causing errors.
    """
    setup_function()
    
    test_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True,
        CYCLE_INIT: lambda: None
    }
    
    cycle.add_cycle(test_cycle)
    original_cycle = cycle._cycles['test-command']
    
    # Register same cycle again
    cycle.add_cycle(test_cycle)
    
    # Verify original cycle unchanged
    assert cycle._cycles['test-command'] is original_cycle
```

##### Test 2.3.7: Equivalency checking - different cycles raise error

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Register different cycle for same command
  Given a cycle definition registered for a command
  When add_cycle() is called with different definition for same command
  Then ValueError should be raised
  And error message should indicate conflicting cycle definitions
  And the original cycle should remain in _cycles
  
  # Tests: Conflict detection for different definitions
  # Validates: Prevents conflicting cycle configurations
```

```python
def test_add_cycle_equivalency_checking_different_cycles_raise_error():
    """Test that registering a different cycle definition raises ValueError.
    
    This test verifies that when add_cycle() is called with a different cycle
    definition for a command that already has a cycle, a ValueError is raised.
    This behaviour is expected to prevent conflicting cycle configurations.
    """
    setup_function()
    
    first_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'first-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    second_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'second-cycle',
        CYCLE_LOOP: lambda: False
    }
    
    cycle.add_cycle(first_cycle)
    
    with pytest.raises(ValueError) as exc_info:
        cycle.add_cycle(second_cycle)
    
    assert 'conflicting' in str(exc_info.value).lower()
    assert 'test-command' in str(exc_info.value)
    
    # Verify original cycle unchanged
    assert cycle._cycles['test-command'] == first_cycle
```

##### Code 2.4.1: add_cycles() - Bulk registration function

**File:** `src/spafw37/cycle.py`

```python
### Block 2.4.1: Add bulk cycle registration function
### Add after add_cycle() function

def add_cycles(cycle_defs):
    """Register multiple cycle definitions.
    
    Convenience function for registering multiple cycles at once.
    Each cycle is registered individually using add_cycle().
    
    Args:
        cycle_defs: List of cycle definition dicts
    
    Raises:
        ValueError: If any cycle validation fails
    """
    for cycle_def in cycle_defs:
        add_cycle(cycle_def)
```

##### Test 2.4.2: add_cycles() registers multiple cycle definitions

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Register multiple cycles via add_cycles()
  Given a list of valid cycle definitions for different commands
  When add_cycles() is called with the list
  Then all cycles should be stored in _cycles indexed by command names
  And no exceptions should be raised
  
  # Tests: Bulk cycle registration via add_cycles()
  # Validates: Plural function follows param/command patterns
```

```python
def test_add_cycles_registers_multiple_cycles():
    """Test that add_cycles() registers multiple cycle definitions.
    
    This test verifies that when a list of cycle definitions is passed to
    add_cycles(), all cycles are registered and stored in the _cycles dictionary.
    This behaviour is expected to provide consistent bulk registration API.
    """
    setup_function()
    
    cycles_list = [
        {
            CYCLE_COMMAND: 'command-one',
            CYCLE_NAME: 'cycle-one',
            CYCLE_LOOP: lambda: True
        },
        {
            CYCLE_COMMAND: 'command-two',
            CYCLE_NAME: 'cycle-two',
            CYCLE_LOOP: lambda: False
        }
    ]
    
    cycle.add_cycles(cycles_list)
    
    assert 'command-one' in cycle._cycles
    assert 'command-two' in cycle._cycles
    assert cycle._cycles['command-one'][CYCLE_NAME] == 'cycle-one'
    assert cycle._cycles['command-two'][CYCLE_NAME] == 'cycle-two'
```

##### Test 2.4.3: add_cycles() with mixed inline and string CYCLE_COMMAND

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Register cycles with mixed inline and string CYCLE_COMMAND
  Given a list with some cycles having inline CYCLE_COMMAND and others with strings
  When add_cycles() is called
  Then all cycles should be registered correctly
  And inline commands should be registered
  And all cycles should be indexed by their command names
  
  # Tests: Mixed inline/string CYCLE_COMMAND in bulk registration
  # Validates: Flexibility in specifying CYCLE_COMMAND format
```

```python
def test_add_cycles_with_mixed_inline_and_string_cycle_commands():
    """Test that add_cycles() handles mixed inline and string CYCLE_COMMAND.
    
    This test verifies that when a list contains some cycles with inline
    CYCLE_COMMAND definitions (dicts) and others with string references,
    all cycles are registered correctly.
    This behaviour is expected to provide maximum flexibility.
    """
    setup_function()
    
    cycles_list = [
        {
            CYCLE_COMMAND: {
                COMMAND_NAME: 'inline-cmd',
                COMMAND_ACTION: lambda: None
            },
            CYCLE_NAME: 'inline-cycle',
            CYCLE_LOOP: lambda: True
        },
        {
            CYCLE_COMMAND: 'string-ref-cmd',
            CYCLE_NAME: 'string-cycle',
            CYCLE_LOOP: lambda: False
        }
    ]
    
    cycle.add_cycles(cycles_list)
    
    # Both should be registered
    assert 'inline-cmd' in cycle._cycles
    assert 'string-ref-cmd' in cycle._cycles
    
    # Inline command should be registered
    assert 'inline-cmd' in command._commands
```

##### Code 2.5.1: get_cycle() - Retrieval function

**File:** `src/spafw37/cycle.py`

```python
### Block 2.5.1: Add cycle retrieval function
### Add after add_cycles() function

def get_cycle(command_name):
    """Retrieve registered cycle by command name.
    
    Args:
        command_name: Name of command to get cycle for
    
    Returns:
        Cycle definition dict if registered, None otherwise
    """
    return _cycles.get(command_name)
```

##### Test 2.5.2: get_cycle() retrieves registered cycle

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Retrieve cycle by command name
  Given a cycle registered for command "my-command"
  When get_cycle("my-command") is called
  Then the cycle definition should be returned
  And the dict should contain all registered properties
  
  # Tests: Cycle retrieval by command name
  # Validates: Public API for accessing registered cycles
```

```python
def test_get_cycle_retrieves_registered_cycle():
    """Test that get_cycle() retrieves a registered cycle by command name.
    
    This test verifies that after registering a cycle, it can be retrieved
    using get_cycle() with the command name as the key.
    This behaviour is expected to provide public API access to registered cycles.
    """
    setup_function()
    
    test_cycle = {
        CYCLE_COMMAND: 'my-command',
        CYCLE_NAME: 'my-cycle',
        CYCLE_LOOP: lambda: True,
        CYCLE_INIT: lambda: None
    }
    
    cycle.add_cycle(test_cycle)
    retrieved_cycle = cycle.get_cycle('my-command')
    
    assert retrieved_cycle is not None
    assert retrieved_cycle == test_cycle
    assert retrieved_cycle[CYCLE_NAME] == 'my-cycle'
```

##### Test 2.5.3: get_cycle() returns None for unregistered command

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Request cycle for command with no cycle
  Given no cycle registered for command "unknown-command"
  When get_cycle("unknown-command") is called
  Then None should be returned
  And no exception should be raised
  
  # Tests: Graceful handling of missing cycles
  # Validates: Allows checking if cycle exists without errors
```

```python
def test_get_cycle_returns_none_for_unregistered_command():
    """Test that get_cycle() returns None for an unregistered command.
    
    This test verifies that when get_cycle() is called with a command name
    that has no registered cycle, None is returned without raising an exception.
    This behaviour is expected to allow safe checking for cycle existence.
    """
    setup_function()
    
    result = cycle.get_cycle('unknown-command')
    
    assert result is None
```

##### Code 2.6.1: _validate_cycle_required_fields() helper

**File:** `src/spafw37/cycle.py`

```python
### Block 2.6.1: Add cycle validation helper
### Add before add_cycle() function (helpers come before functions that use them)

def _validate_cycle_required_fields(cycle_def):
    """Validate that cycle definition contains all required fields.
    
    Required fields:
    - CYCLE_COMMAND: Target command name
    - CYCLE_NAME: Cycle identifier
    - CYCLE_LOOP: Loop condition function
    
    Args:
        cycle_def: Cycle definition dict to validate
    
    Raises:
        ValueError: If any required field is missing
    """
    # Block 2.6.1.1: Check CYCLE_COMMAND field
    if CYCLE_COMMAND not in cycle_def:
        raise ValueError("Cycle definition missing required field: CYCLE_COMMAND")
    
    # Block 2.6.1.2: Check CYCLE_NAME field
    if CYCLE_NAME not in cycle_def:
        raise ValueError("Cycle definition missing required field: CYCLE_NAME")
    
    # Block 2.6.1.3: Check CYCLE_LOOP field
    if CYCLE_LOOP not in cycle_def:
        raise ValueError("Cycle definition missing required field: CYCLE_LOOP")
```

##### Test 2.6.2: _validate_cycle_required_fields() accepts valid cycle

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Valid cycle passes validation
  Given a cycle definition with all required fields
  When _validate_cycle_required_fields is called
  Then no exception should be raised
  
  # Tests: Validation accepts valid cycles
  # Validates: Required field checking works correctly
```

```python
def test_validate_cycle_required_fields_accepts_valid_cycle():
    """Test that _validate_cycle_required_fields accepts a valid cycle.
    
    This test verifies that when a cycle definition contains all required fields,
    the validation function does not raise any exceptions.
    This behaviour is expected because valid cycles should pass validation.
    """
    setup_function()
    
    valid_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    # Should not raise
    cycle._validate_cycle_required_fields(valid_cycle)
```

##### Test 2.6.3: _validate_cycle_required_fields() rejects missing CYCLE_COMMAND

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Missing CYCLE_COMMAND field rejected
  Given a cycle definition without CYCLE_COMMAND
  When _validate_cycle_required_fields is called
  Then ValueError should be raised
  And error message should mention CYCLE_COMMAND
  
  # Tests: Validation rejects missing required field
  # Validates: CYCLE_COMMAND is required
```

```python
def test_validate_cycle_required_fields_rejects_missing_cycle_command():
    """Test that _validate_cycle_required_fields rejects missing CYCLE_COMMAND.
    
    This test verifies that when a cycle definition is missing the CYCLE_COMMAND
    field, the validation function raises a ValueError with an appropriate message.
    This behaviour is expected because CYCLE_COMMAND is a required field.
    """
    setup_function()
    
    invalid_cycle = {
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    with pytest.raises(ValueError) as exc_info:
        cycle._validate_cycle_required_fields(invalid_cycle)
    
    assert 'CYCLE_COMMAND' in str(exc_info.value)
```

##### Test 2.6.4: _validate_cycle_required_fields() rejects missing CYCLE_NAME

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Missing CYCLE_NAME field rejected
  Given a cycle definition without CYCLE_NAME
  When _validate_cycle_required_fields is called
  Then ValueError should be raised
  And error message should mention CYCLE_NAME
  
  # Tests: Validation rejects missing required field
  # Validates: CYCLE_NAME is required
```

```python
def test_validate_cycle_required_fields_rejects_missing_cycle_name():
    """Test that _validate_cycle_required_fields rejects missing CYCLE_NAME.
    
    This test verifies that when a cycle definition is missing the CYCLE_NAME
    field, the validation function raises a ValueError with an appropriate message.
    This behaviour is expected because CYCLE_NAME is a required field.
    """
    setup_function()
    
    invalid_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_LOOP: lambda: True
    }
    
    with pytest.raises(ValueError) as exc_info:
        cycle._validate_cycle_required_fields(invalid_cycle)
    
    assert 'CYCLE_NAME' in str(exc_info.value)
```

##### Test 2.6.5: _validate_cycle_required_fields() rejects missing CYCLE_LOOP

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Missing CYCLE_LOOP field rejected
  Given a cycle definition without CYCLE_LOOP
  When _validate_cycle_required_fields is called
  Then ValueError should be raised
  And error message should mention CYCLE_LOOP
  
  # Tests: Validation rejects missing required field
  # Validates: CYCLE_LOOP is required
```

```python
def test_validate_cycle_required_fields_rejects_missing_cycle_loop():
    """Test that _validate_cycle_required_fields rejects missing CYCLE_LOOP.
    
    This test verifies that when a cycle definition is missing the CYCLE_LOOP
    field, the validation function raises a ValueError with an appropriate message.
    This behaviour is expected because CYCLE_LOOP is a required field.
    """
    setup_function()
    
    invalid_cycle = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle'
    }
    
    with pytest.raises(ValueError) as exc_info:
        cycle._validate_cycle_required_fields(invalid_cycle)
    
    assert 'CYCLE_LOOP' in str(exc_info.value)
```

##### Code 2.7.1: _cycles_are_equivalent() helper

**File:** `src/spafw37/cycle.py`

```python
### Block 2.7.1: Add equivalency checking helper
### Add before add_cycle() function

def _cycles_are_equivalent(cycle1, cycle2):
    """Check if two cycle definitions are equivalent.
    
    Performs deep equality comparison including:
    - All keys (required and optional fields)
    - Primitive values (strings, numbers, bools)
    - Function references (using object identity)
    - Nested structures (lists, dicts)
    
    Args:
        cycle1: First cycle definition dict
        cycle2: Second cycle definition dict
    
    Returns:
        True if cycles are equivalent, False otherwise
    """
    # Block 2.7.1.1: Check if key sets match
    if set(cycle1.keys()) != set(cycle2.keys()):
        return False
    
    # Block 2.7.1.2: Compare values for each key
    for key in cycle1:
        value1 = cycle1[key]
        value2 = cycle2[key]
        
        if callable(value1) and callable(value2):
            if value1 is not value2:
                return False
        elif value1 != value2:
            return False
    
    return True
```

##### Test 2.7.2: _cycles_are_equivalent() returns True for identical cycles

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Identical cycles are equivalent
  Given two cycle definitions with identical properties
  When _cycles_are_equivalent is called
  Then it should return True
  
  # Tests: Equivalency checking for identical cycles
  # Validates: Same properties recognised as equivalent
```

```python
def test_cycles_are_equivalent_returns_true_for_identical_cycles():
    """Test that _cycles_are_equivalent returns True for identical cycles.
    
    This test verifies that when two cycle definitions have exactly the same
    properties and values, the equivalency function returns True.
    This behaviour is expected for detecting duplicate registrations.
    """
    setup_function()
    
    loop_func = lambda: True
    init_func = lambda: None
    
    cycle1 = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_func,
        CYCLE_INIT: init_func
    }
    
    cycle2 = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_func,
        CYCLE_INIT: init_func
    }
    
    assert cycle._cycles_are_equivalent(cycle1, cycle2) is True
```

##### Test 2.7.3: _cycles_are_equivalent() returns False for different required fields

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Cycles with different required fields are not equivalent
  Given two cycle definitions with different CYCLE_NAME
  When _cycles_are_equivalent is called
  Then it should return False
  
  # Tests: Equivalency checking for different required fields
  # Validates: Differences in required fields detected
```

```python
def test_cycles_are_equivalent_returns_false_for_different_required_fields():
    """Test that _cycles_are_equivalent returns False for different required fields.
    
    This test verifies that when two cycle definitions differ in a required field
    like CYCLE_NAME, the equivalency function returns False.
    This behaviour is expected to detect conflicting cycle definitions.
    """
    setup_function()
    
    cycle1 = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'cycle-one',
        CYCLE_LOOP: lambda: True
    }
    
    cycle2 = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'cycle-two',
        CYCLE_LOOP: lambda: True
    }
    
    assert cycle._cycles_are_equivalent(cycle1, cycle2) is False
```

##### Test 2.7.4: _cycles_are_equivalent() returns False for different optional fields

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Cycles with different optional fields are not equivalent
  Given two cycles, one with CYCLE_INIT and one without
  When _cycles_are_equivalent is called
  Then it should return False
  
  # Tests: Equivalency checking for different optional fields
  # Validates: Presence/absence of optional fields detected
```

```python
def test_cycles_are_equivalent_returns_false_for_different_optional_fields():
    """Test that _cycles_are_equivalent returns False for different optional fields.
    
    This test verifies that when two cycle definitions differ in optional fields,
    the equivalency function returns False.
    This behaviour is expected because all properties must match for equivalency.
    """
    setup_function()
    
    cycle1 = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True,
        CYCLE_INIT: lambda: None
    }
    
    cycle2 = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    assert cycle._cycles_are_equivalent(cycle1, cycle2) is False
```

##### Test 2.7.5: _cycles_are_equivalent() compares function references

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Cycles with different function objects are not equivalent
  Given two cycles with different CYCLE_LOOP function objects
  When _cycles_are_equivalent is called
  Then it should return False
  
  # Tests: Function object identity comparison
  # Validates: Different function objects not treated as equivalent
```

```python
def test_cycles_are_equivalent_compares_function_references():
    """Test that _cycles_are_equivalent compares function object identity.
    
    This test verifies that when two cycle definitions have different function
    objects (even if they do the same thing), equivalency returns False.
    This behaviour is expected because function identity matters for cycles.
    """
    setup_function()
    
    cycle1 = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    cycle2 = {
        CYCLE_COMMAND: 'test-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: lambda: True
    }
    
    assert cycle._cycles_are_equivalent(cycle1, cycle2) is False
```

##### Code 2.8.1: _extract_command_name() helper

**File:** `src/spafw37/cycle.py`

```python
### Block 2.8.1: Add command name extraction helper
### Add after _cycles_are_equivalent() function

def _extract_command_name(command_ref):
    """Extract command name from string reference or inline definition dict.
    
    Args:
        command_ref: Either a string (command name) or dict (inline definition)
    
    Returns:
        Command name as string
        
    Raises:
        ValueError: If dict missing COMMAND_NAME field
    """
    # Block 2.8.1.1: Handle string reference
    if isinstance(command_ref, str):
        return command_ref
    
    # Block 2.8.1.2: Handle dict (inline definition)
    if isinstance(command_ref, dict):
        if COMMAND_NAME not in command_ref:
            raise ValueError("Inline command definition missing COMMAND_NAME field")
        return command_ref[COMMAND_NAME]
    
    # Block 2.8.1.3: Invalid type
    raise ValueError(
        f"CYCLE_COMMAND must be string or dict, got {type(command_ref).__name__}"
    )
```

##### Test 2.8.2: _extract_command_name() extracts from string

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Extract command name from string
  Given a command name as string
  When _extract_command_name is called
  Then it should return the string unchanged
  
  # Tests: String command name extraction
  # Validates: String references passed through unchanged
```

```python
def test_extract_command_name_from_string():
    """Test that _extract_command_name returns string unchanged.
    
    This test verifies that when a command name is provided as a string,
    the function returns it unchanged.
    This behaviour is expected for command name references.
    """
    setup_function()
    
    result = cycle._extract_command_name('my-command')
    
    assert result == 'my-command'
```

##### Test 2.8.3: _extract_command_name() extracts from dict

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Extract command name from inline definition
  Given an inline command definition dict with COMMAND_NAME
  When _extract_command_name is called
  Then it should return the COMMAND_NAME value
  
  # Tests: Inline command name extraction
  # Validates: Name extracted from inline definition
```

```python
def test_extract_command_name_from_dict():
    """Test that _extract_command_name extracts name from inline definition.
    
    This test verifies that when an inline command definition (dict) is provided,
    the function extracts and returns the COMMAND_NAME field.
    This behaviour is expected for inline command definitions.
    """
    setup_function()
    
    inline_command = {
        COMMAND_NAME: 'inline-cmd',
        COMMAND_ACTION: lambda: None
    }
    
    result = cycle._extract_command_name(inline_command)
    
    assert result == 'inline-cmd'
```

##### Test 2.8.4: _extract_command_name() validates dict has COMMAND_NAME

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Inline definition missing COMMAND_NAME
  Given an inline command definition dict without COMMAND_NAME
  When _extract_command_name is called
  Then ValueError should be raised
  And error message should indicate missing COMMAND_NAME
  
  # Tests: Validation of inline command definitions
  # Validates: Inline commands must have name field
```

```python
def test_extract_command_name_validates_dict_has_command_name():
    """Test that _extract_command_name validates COMMAND_NAME in dict.
    
    This test verifies that when an inline command definition (dict) is missing
    the required COMMAND_NAME field, a ValueError is raised.
    This behaviour is expected to catch malformed inline definitions.
    """
    setup_function()
    
    invalid_inline_command = {
        COMMAND_ACTION: lambda: None
    }
    
    with pytest.raises(ValueError) as exc_info:
        cycle._extract_command_name(invalid_inline_command)
    
    assert 'COMMAND_NAME' in str(exc_info.value)
```

#### Implementation Order

1. Add module-level `_cycles` dict (Code 2.1)
2. Add `_validate_cycle_required_fields()` helper (Code 2.6.1)
3. Add `_cycles_are_equivalent()` helper (Code 2.7.1)
4. Add `_extract_command_name()` helper (Code 2.8.1)
5. Add `add_cycle()` main function (Code 2.3.1)
6. Add `add_cycles()` bulk function (Code 2.4.1)
7. Add `get_cycle()` retrieval function (Code 2.5.1)
