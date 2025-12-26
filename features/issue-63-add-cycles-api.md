# Issue #63: Add top-level add_cycles() API for cycle definitions

**GitHub Issue:** https://github.com/minouris/spafw37/issues/63

## Overview

Currently, cycles can only be defined inline with commands using the `COMMAND_CYCLE` property. This works but is not consistent with how other framework objects (params, commands) are registered using top-level `add_params()` and `add_commands()` functions.

### Proposed Feature

Add `add_cycles()` and `add_cycle()` functions to the core API to allow cycles to be defined as top-level objects, similar to how params and commands are registered.

#### Current API (inline only):
```python
from spafw37 import core as spafw37
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION, COMMAND_CYCLE
from spafw37.constants.cycle import (
    CYCLE_NAME, CYCLE_INIT, CYCLE_LOOP, CYCLE_LOOP_START,
    CYCLE_LOOP_END, CYCLE_END, CYCLE_COMMANDS
)

commands = [{
    COMMAND_NAME: 'my-command',
    COMMAND_ACTION: my_action,
    COMMAND_CYCLE: {
        CYCLE_NAME: 'my-cycle',
        CYCLE_INIT: init_fn,
        CYCLE_LOOP: loop_fn,
        CYCLE_LOOP_START: loop_start_fn,
        CYCLE_LOOP_END: loop_end_fn,
        CYCLE_END: end_fn,
        CYCLE_COMMANDS: cycle_commands,
    }
}]
spafw37.add_commands(commands)
```

#### Proposed API (top-level - plural):
```python
from spafw37 import core as spafw37
from spafw37.constants.cycle import (
    CYCLE_COMMAND, CYCLE_NAME, CYCLE_INIT, CYCLE_LOOP,
    CYCLE_LOOP_START, CYCLE_LOOP_END, CYCLE_END, CYCLE_COMMANDS
)

cycles = [{
    CYCLE_COMMAND: 'my-command',
    CYCLE_NAME: 'my-cycle',
    CYCLE_INIT: init_fn,
    CYCLE_LOOP: loop_fn,
    CYCLE_LOOP_START: loop_start_fn,
    CYCLE_LOOP_END: loop_end_fn,
    CYCLE_END: end_fn,
    CYCLE_COMMANDS: cycle_commands,
}]
spafw37.add_cycles(cycles)
```

#### Proposed API (top-level - singular):
```python
from spafw37 import core as spafw37
from spafw37.constants.cycle import (
    CYCLE_COMMAND, CYCLE_NAME, CYCLE_INIT, CYCLE_LOOP,
    CYCLE_LOOP_START, CYCLE_LOOP_END, CYCLE_END, CYCLE_COMMANDS
)

cycle = {
    CYCLE_COMMAND: 'my-command',
    CYCLE_NAME: 'my-cycle',
    CYCLE_INIT: init_fn,
    CYCLE_LOOP: loop_fn,
    CYCLE_LOOP_START: loop_start_fn,
    CYCLE_LOOP_END: loop_end_fn,
    CYCLE_END: end_fn,
    CYCLE_COMMANDS: cycle_commands,
}
spafw37.add_cycle(cycle)
```

### Requirements

- Implement `add_cycles()` - accepts a list of cycle definitions
- Implement `add_cycle()` - accepts a single cycle definition
- Both functions should be exposed through `core.py` (public API)
- Follow existing patterns from `add_param()`/`add_params()` and `add_command()`/`add_commands()`

### Benefits

- Consistency with `add_params()` and `add_commands()` API design
- Separation of concerns (cycles defined separately from commands)
- Cleaner code organisation for complex workflows
- Easier testing with top-level cycle definitions
- Flexibility to add single cycles or multiple cycles at once

### Context

This feature was identified during implementation of Issue #15 (User Input Params) when writing integration tests. The tests assumed `add_cycles()` existed but it does not.

**Key architectural decisions:**

- **API consistency:** New `add_cycle()` and `add_cycles()` functions mirror existing `add_param()`/`add_params()` and `add_command()`/`add_commands()` patterns for consistent developer experience
- **Cycle storage:** Cycles will be stored in a module-level registry (`_cycles` dict) in `cycle.py`, with command name as key to support cycle lookup
- **Integration approach:** Cycles registered via top-level API will be associated with commands during command registration phase (in `add_command()`)
- **Backward compatibility:** Existing inline `COMMAND_CYCLE` definition method continues to work unchanged; new API provides alternative registration approach
- **Equivalency checking:** Duplicate cycle registrations use deep equality comparison - identical definitions silently skip (no error), different definitions raise `ValueError`
- **Validation timing:** Cycle structure validated immediately on registration, command reference validated when command is registered (flexible order)
- **Immutability:** Cycles are immutable once registered - no editing capability (prevents scattered definitions across codebase)
- **CYCLE_NAME property:** Cycles have independent identifiers separate from command names for identification and logging (multi-command attachment is potential future enhancement, not in scope for this issue)
- **Inline command definitions:** Commands can be defined inline within `CYCLE_COMMANDS` list (similar to how params can be defined inline in `COMMAND_REQUIRED_PARAMS`)

## Table of Contents

- [Overview](#overview)
- [Implementation Steps](#implementation-steps)
  - [1. Add cycle storage and registration functions to cycle.py](#1-add-cycle-storage-and-registration-functions-to-cyclepy)
  - [2. Add support for inline command definitions in cycles](#2-add-support-for-inline-command-definitions-in-cycles)
  - [3. Modify command registration to check for top-level cycles](#3-modify-command-registration-to-check-for-top-level-cycles)
  - [4. Expose new functions through core.py facade](#4-expose-new-functions-through-corepy-facade)
  - [5. Update constants file with CYCLE_NAME property](#5-update-constants-file-with-cycle_name-property)
  - [6. Create example demonstrating new API](#6-create-example-demonstrating-new-api)
  - [7. Update documentation](#7-update-documentation)
- [Further Considerations](#further-considerations)
  - [1. Error handling for duplicate cycle definitions](#1-error-handling-for-duplicate-cycle-definitions---resolved)
  - [2. Validation of CYCLE_COMMAND field](#2-validation-of-cycle_command-field---resolved)
  - [3. Priority when both inline and top-level cycles exist](#3-priority-when-both-inline-and-top-level-cycles-exist---resolved)
  - [4. Related Issue: Commands and params validation](#4-related-issue-commands-and-params-validation)
- [Success Criteria](#success-criteria)
- [Planning Checklist](#planning-checklist)
- [Implementation Log](#implementation-log)
- [Implementation Checklist](#implementation-checklist)
- [CHANGES for v1.1.0 Release](#changes-for-v110-release)

## Implementation Steps
### Step 1: Module-level Imports

This file consolidates ALL imports required for implementing Issue #63. Other step files reference this rather than duplicating imports.

#### Module-level imports for src/spafw37/cycle.py

```python
### Standard library imports
from copy import deepcopy

### Internal imports
from spafw37 import command
from spafw37.constants.command import COMMAND_NAME
from spafw37.constants.cycle import (
    CYCLE_COMMAND,
    CYCLE_NAME,
    CYCLE_LOOP
)
```

#### Module-level imports for src/spafw37/command.py

```python
### Note: command.py already has imports - these are ADDITIONS only

from spafw37 import cycle
```

#### Module-level imports for src/spafw37/core.py

```python
### Note: core.py already has imports - these are ADDITIONS only

from spafw37 import cycle
```

#### Module-level imports for tests/test_cycle.py

```python
### Standard library imports
import pytest

### Internal imports
from spafw37 import command, cycle
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION
from spafw37.constants.cycle import (
    CYCLE_COMMAND,
    CYCLE_NAME,
    CYCLE_INIT,
    CYCLE_LOOP,
    CYCLE_LOOP_START,
    CYCLE_LOOP_END,
    CYCLE_END,
    CYCLE_COMMANDS
)
```

#### Module-level imports for tests/test_command.py

```python
### Note: test_command.py already has imports - these are ADDITIONS only

from spafw37 import cycle
from spafw37.constants.cycle import (
    CYCLE_COMMAND,
    CYCLE_NAME,
    CYCLE_LOOP
)
```

#### Module-level imports for tests/test_core.py

```python
### Note: test_core.py already has imports - these are ADDITIONS only

from spafw37.constants.cycle import (
    CYCLE_COMMAND,
    CYCLE_NAME,
    CYCLE_LOOP
)
```
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
### Step 3: Verify inline command support in CYCLE_COMMANDS

#### Overview

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

#### Module-level imports

See `issue-63-step1-imports.md` for all required imports.

#### Algorithm

##### Inline Command Support in CYCLE_COMMANDS

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

#### Implementation

##### Test 3.2.1: Inline command definition in CYCLE_COMMANDS

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

##### Test 3.2.2: Mixed inline and string command references in CYCLE_COMMANDS

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

##### Test 3.2.3: Validation deferred for inline commands in CYCLE_COMMANDS

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

#### Implementation Order

No new implementation code required. Tests verify that existing inline command support works with top-level cycles.

1. Add test for inline command definitions (Test 3.2.1)
2. Add test for mixed inline/string commands (Test 3.2.2)
3. Add test for deferred validation (Test 3.2.3)
### Step 4: Modify command registration to check for top-level cycles

#### Overview

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

#### Module-level imports

See `issue-63-step1-imports.md` for all required imports.

#### Algorithm

##### Command Registration with Top-Level Cycle Attachment

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

#### Implementation

##### Code 4.1.1: Modify _store_command() for top-level cycle integration

**File:** `src/spafw37/command.py`

```python
### Block 4.1.1: Modify _store_command() function (around line 342)
### Find the existing _store_command() function and modify it

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

##### Test 4.2.1: _store_command() attaches top-level cycle

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

##### Test 4.2.2: _store_command() uses top-level cycle when no inline

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

##### Test 4.2.3: _store_command() uses inline cycle when no top-level

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

##### Test 4.2.4: Equivalency checking - identical inline and top-level cycles

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

##### Test 4.2.5: Equivalency checking - different inline and top-level cycles raise error

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

##### Test 4.2.6: _store_command() calls register_cycle() with attached cycle

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

#### Implementation Order

1. Modify `_store_command()` function (Code 4.1.1)
2. Add tests to `tests/test_command.py` (Tests 4.2.1-4.2.6)
3. Verify integration tests pass

#### Notes

- This step integrates top-level cycles with existing command registration
- Equivalency checking reuses `cycle._cycles_are_equivalent()` from Step 2
- First-wins behaviour: when cycles are identical, inline cycle is used
- All existing cycle validation happens in `cycle.register_cycle()` (unchanged)
### Step 5: Expose new functions through core.py facade

#### Overview

This step exposes the new cycle registration functions through the core.py public API facade, following the same delegation pattern used for params and commands.

**Public API functions added to core.py:**
- `add_cycle(cycle_def)` - Delegates to `cycle.add_cycle()`
- `add_cycles(cycle_defs)` - Delegates to `cycle.add_cycles()`

**Tests created:**
- `test_core_add_cycle_delegates_to_cycle_module()` - Verify add_cycle() delegation
- `test_core_add_cycles_delegates_to_cycle_module()` - Verify add_cycles() delegation
- `test_core_api_consistency_with_add_command_pattern()` - Verify API pattern consistency

#### Module-level imports

See `issue-63-step1-imports.md` for all required imports.

#### Algorithm

##### Public API Delegation Pattern

The core.py module serves as a facade, providing simple delegation functions:
1. Import the cycle module
2. Create wrapper functions that call cycle module functions directly
3. Preserve docstrings and function signatures for consistency
4. No additional logic - pure delegation

#### Implementation

##### Code 5.1.1: Add add_cycle() to core.py

**File:** `src/spafw37/core.py`

```python
### Block 5.1.1: Add add_cycle() delegation function
### Add after existing add_command() function (around line 150)

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

##### Code 5.1.2: Add add_cycles() to core.py

**File:** `src/spafw37/core.py`

```python
### Block 5.1.2: Add add_cycles() delegation function
### Add after add_cycle() function

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

##### Test 5.2.1: core.add_cycle() delegates to cycle.add_cycle()

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

##### Test 5.2.2: core.add_cycles() delegates to cycle.add_cycles()

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

##### Test 5.2.3: API consistency with add_command/add_param patterns

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

#### Implementation Order

1. Add `add_cycle()` function to core.py (Code 5.1.1)
2. Add `add_cycles()` function to core.py (Code 5.1.2)
3. Add tests to `tests/test_core.py` (Tests 5.2.1-5.2.3)
4. Verify all tests pass

#### Notes

- Pure delegation - no additional logic in core.py
- Docstrings preserved for API documentation
- Follows exact pattern of add_param/add_command functions
- Return values not needed (consistent with add_param/add_command)
### Step 6: Update constants file with CYCLE_COMMAND property

#### Overview

This step ensures the CYCLE_COMMAND constant is properly defined and exported from the constants module, and that CYCLE_NAME documentation clarifies cycle identifiers are separate from command names.

**File modified:**
- `src/spafw37/constants/cycle.py`

**Tests created:**
- `test_cycle_command_constant_defined_and_exported()` - Verify CYCLE_COMMAND exists
- `test_cycle_name_constant_defined_and_documented()` - Verify CYCLE_NAME exists

#### Module-level imports

No additional imports needed - constants file only defines string constants.

#### Algorithm

##### Constants Validation

1. Verify CYCLE_COMMAND constant is defined
2. Verify CYCLE_COMMAND is exported in module's public API
3. Verify CYCLE_NAME constant is defined
4. Add or update docstring comments explaining usage

#### Implementation

##### Code 6.1.1: Ensure CYCLE_COMMAND constant defined

**File:** `src/spafw37/constants/cycle.py`

```python
### Block 6.1.1: Add CYCLE_COMMAND constant if not present
### Add to constants section (check if already exists first)

### Target command for cycle attachment
### Used in top-level cycle definitions via add_cycle()
### Can be a string (command name) or dict (inline command definition)
CYCLE_COMMAND = 'cycle-command'
```

##### Code 6.1.2: Update CYCLE_NAME documentation

**File:** `src/spafw37/constants/cycle.py`

```python
### Block 6.1.2: Update CYCLE_NAME constant documentation
### Modify existing CYCLE_NAME constant comment

### Cycle identifier (independent of command names)
### Used to identify cycles in logging and error messages
### Multiple commands could potentially share a cycle (future enhancement)
CYCLE_NAME = 'cycle-name'
```

##### Test 6.2.1: CYCLE_COMMAND constant defined and exported

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Import CYCLE_COMMAND from constants.cycle
  Given the constants.cycle module
  When CYCLE_COMMAND is imported
  Then the constant should be a string
  And the constant should be properly exported
  And no exceptions should be raised
  
  # Tests: CYCLE_COMMAND constant availability
  # Validates: New constant properly defined for top-level API
```

```python
def test_cycle_command_constant_defined_and_exported():
    """Test that CYCLE_COMMAND constant is defined and exported.
    
    This test verifies that the CYCLE_COMMAND constant is properly defined
    in the constants.cycle module and can be imported.
    This behaviour is expected to support top-level cycle registration.
    """
    # Import already done at module level
    assert isinstance(CYCLE_COMMAND, str)
    assert len(CYCLE_COMMAND) > 0
    assert CYCLE_COMMAND == 'cycle-command'
```

##### Test 6.2.2: CYCLE_NAME constant defined and documented

**File:** `tests/test_cycle.py`

```gherkin
Scenario: Import CYCLE_NAME from constants.cycle
  Given the constants.cycle module
  When CYCLE_NAME is imported
  Then the constant should be a string
  And the constant should be properly exported
  And documentation should clarify cycle identifier purpose
  
  # Tests: CYCLE_NAME constant availability and documentation
  # Validates: Cycle identifiers separate from command names
```

```python
def test_cycle_name_constant_defined_and_documented():
    """Test that CYCLE_NAME constant is defined and documented.
    
    This test verifies that the CYCLE_NAME constant is properly defined
    in the constants.cycle module with clear documentation.
    This behaviour is expected to support cycle identification.
    """
    # Import already done at module level
    assert isinstance(CYCLE_NAME, str)
    assert len(CYCLE_NAME) > 0
    assert CYCLE_NAME == 'cycle-name'
```

##### Manual Review 6.3.1: Verify constant documentation

**Action:** Manual review of `src/spafw37/constants/cycle.py`

**Checklist:**
- [ ] CYCLE_COMMAND constant defined with value 'cycle-command'
- [ ] CYCLE_COMMAND has comment explaining it's for top-level cycle registration
- [ ] Comment clarifies CYCLE_COMMAND can be string or inline dict
- [ ] CYCLE_NAME constant defined with value 'cycle-name'
- [ ] CYCLE_NAME has comment explaining cycle identifiers are independent of command names
- [ ] All constants follow existing formatting and style conventions
- [ ] No duplicate constant definitions

#### Implementation Order

1. Check if CYCLE_COMMAND already exists in constants/cycle.py
2. Add CYCLE_COMMAND if missing (Code 6.1.1)
3. Update CYCLE_NAME documentation (Code 6.1.2)
4. Add tests to `tests/test_cycle.py` (Tests 6.2.1-6.2.2)
5. Manual review of constants file (Review 6.3.1)

#### Notes

- Check existing constants file first - CYCLE_COMMAND may already exist
- CYCLE_NAME likely already exists - just needs documentation update
- Constants are simple strings - minimal implementation needed
- Documentation comments are key for developer understanding
### Step 7: Create example demonstrating new API

#### Overview

This step creates a new example file showing how to use the `add_cycle()` and `add_cycles()` functions to define cycles separately from commands, demonstrating cleaner code organisation.

**File created:**
- `examples/cycles_toplevel_api.py`

**Tests created:**
- Manual execution test (Test 7.2.1)

#### Module-level imports

No imports needed - this is the example file itself.

#### Algorithm

##### Example Design

The example should demonstrate:
1. Importing core API with alias: `from spafw37 import core as spafw37`
2. Defining cycles with `add_cycle()` (singular)
3. Defining multiple cycles with `add_cycles()` (plural)
4. Inline CYCLE_COMMAND definitions (dict format)
5. String CYCLE_COMMAND references
6. Commands registered separately from cycles
7. Full cycle execution with all phases (init, loop, end)
8. Clear output showing execution flow

#### Implementation

##### Code 7.1.1: Create cycles_toplevel_api.py example

**File:** `examples/cycles_toplevel_api.py`

```python
#!/usr/bin/env python
"""Demonstrate top-level cycle registration using add_cycle() and add_cycles().

This example shows how to define cycles as top-level objects separate from
commands, providing cleaner code organisation and consistent API patterns.

Run: python examples/cycles_toplevel_api.py
"""

from spafw37 import core as spafw37
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION
from spafw37.constants.cycle import (
    CYCLE_COMMAND,
    CYCLE_NAME,
    CYCLE_INIT,
    CYCLE_LOOP,
    CYCLE_LOOP_START,
    CYCLE_LOOP_END,
    CYCLE_END,
    CYCLE_COMMANDS
)


### Shared state for cycle demonstration
cycle_state = {'count': 0, 'max_iterations': 3}


def init_counter():
    """Initialise cycle state."""
    print("  [INIT] Initialising counter")
    cycle_state['count'] = 0


def check_counter():
    """Check if we should continue looping."""
    should_continue = cycle_state['count'] < cycle_state['max_iterations']
    print(f"  [LOOP CHECK] Count={cycle_state['count']}, Continue={should_continue}")
    return should_continue


def loop_start_message():
    """Print message at start of each iteration."""
    print(f"  [LOOP START] Starting iteration {cycle_state['count'] + 1}")


def loop_end_increment():
    """Increment counter at end of each iteration."""
    cycle_state['count'] += 1
    print(f"  [LOOP END] Completed iteration {cycle_state['count']}")


def end_summary():
    """Print final summary."""
    print(f"  [END] Cycle complete. Total iterations: {cycle_state['count']}")


def step_one_action():
    """Execute step one of the cycle."""
    print("    → Step 1: Processing")


def step_two_action():
    """Execute step two of the cycle."""
    print("    → Step 2: Processing")


### Example 1: Register single cycle with add_cycle()
### Demonstrates inline CYCLE_COMMAND definition (dict)
print("\n=== Example 1: Single cycle with inline command ===")

single_cycle = {
    CYCLE_COMMAND: {
        COMMAND_NAME: 'process-single',
        COMMAND_ACTION: lambda: print("COMMAND: process-single")
    },
    CYCLE_NAME: 'single-cycle',
    CYCLE_INIT: init_counter,
    CYCLE_LOOP: check_counter,
    CYCLE_LOOP_START: loop_start_message,
    CYCLE_LOOP_END: loop_end_increment,
    CYCLE_END: end_summary,
    CYCLE_COMMANDS: [
        {COMMAND_NAME: 'single-step1', COMMAND_ACTION: step_one_action},
        {COMMAND_NAME: 'single-step2', COMMAND_ACTION: step_two_action}
    ]
}

spafw37.add_cycle(single_cycle)
spafw37.run_cli(['process-single'])


### Example 2: Register multiple cycles with add_cycles()
### Demonstrates string CYCLE_COMMAND references (commands defined separately)
print("\n=== Example 2: Multiple cycles with command references ===")

### Define commands first
commands = [
    {
        COMMAND_NAME: 'process-batch-a',
        COMMAND_ACTION: lambda: print("COMMAND: process-batch-a")
    },
    {
        COMMAND_NAME: 'process-batch-b',
        COMMAND_ACTION: lambda: print("COMMAND: process-batch-b")
    }
]
spafw37.add_commands(commands)

### Define cycles referencing commands by name
cycles = [
    {
        CYCLE_COMMAND: 'process-batch-a',
        CYCLE_NAME: 'batch-a-cycle',
        CYCLE_INIT: init_counter,
        CYCLE_LOOP: check_counter,
        CYCLE_LOOP_START: loop_start_message,
        CYCLE_LOOP_END: loop_end_increment,
        CYCLE_END: end_summary,
        CYCLE_COMMANDS: [
            {COMMAND_NAME: 'batch-a-step1', COMMAND_ACTION: step_one_action}
        ]
    },
    {
        CYCLE_COMMAND: 'process-batch-b',
        CYCLE_NAME: 'batch-b-cycle',
        CYCLE_INIT: init_counter,
        CYCLE_LOOP: check_counter,
        CYCLE_LOOP_START: loop_start_message,
        CYCLE_LOOP_END: loop_end_increment,
        CYCLE_END: end_summary,
        CYCLE_COMMANDS: [
            {COMMAND_NAME: 'batch-b-step1', COMMAND_ACTION: step_one_action},
            {COMMAND_NAME: 'batch-b-step2', COMMAND_ACTION: step_two_action}
        ]
    }
]

spafw37.add_cycles(cycles)
spafw37.run_cli(['process-batch-a'])
spafw37.run_cli(['process-batch-b'])


### Example 3: Flexible registration order
### Demonstrates cycles can be registered before or after commands
print("\n=== Example 3: Flexible registration order ===")

### Register cycle BEFORE command exists
flexible_cycle = {
    CYCLE_COMMAND: 'process-flexible',
    CYCLE_NAME: 'flexible-cycle',
    CYCLE_INIT: init_counter,
    CYCLE_LOOP: check_counter,
    CYCLE_END: end_summary,
    CYCLE_COMMANDS: [
        {COMMAND_NAME: 'flex-step', COMMAND_ACTION: step_one_action}
    ]
}
spafw37.add_cycle(flexible_cycle)

### Register command AFTER cycle
flexible_command = {
    COMMAND_NAME: 'process-flexible',
    COMMAND_ACTION: lambda: print("COMMAND: process-flexible")
}
spafw37.add_command(flexible_command)

spafw37.run_cli(['process-flexible'])

print("\n=== All examples complete ===")
```

##### Test 7.2.1: Example executes without errors

**File:** Manual test

```gherkin
Scenario: Run cycles_toplevel_api.py example
  Given the example file with add_cycle() and add_cycles() usage
  When the example is executed from command line
  Then it should complete successfully without exceptions
  And it should demonstrate cycle execution
  And output should show cycle functions being called
  
  # Tests: Example code functionality
  # Validates: Top-level API works in real usage scenario
```

**Manual test procedure:**
1. Navigate to workspace root: `cd /workspaces/spafw37`
2. Run example: `python examples/cycles_toplevel_api.py`
3. Verify output shows:
   - Three separate example sections
   - INIT, LOOP CHECK, LOOP START, LOOP END, END messages
   - Three iterations per cycle (count 0, 1, 2)
   - No Python exceptions or errors
4. Verify example file in README.md examples list

#### Implementation Order

1. Create `examples/cycles_toplevel_api.py` (Code 7.1.1)
2. Test example execution manually (Test 7.2.1)
3. Add example to README.md examples list

#### Notes

- Example uses `from spafw37 import core as spafw37` alias (standard pattern)
- Demonstrates both inline CYCLE_COMMAND (dict) and string references
- Shows flexible registration order (cycles before/after commands)
- Clear output with section headers for readability
- Inline commands in CYCLE_COMMANDS list (similar to inline params)
- Example should be executable as-is without modification
### Step 8: Update documentation

#### Overview

This step updates all relevant documentation to reflect the new top-level cycle registration API.

**Files to update:**
- `doc/cycles.md` - Add section on top-level cycle registration
- `doc/api-reference.md` - Add add_cycle() and add_cycles() function signatures
- `README.md` - Update features list and add "What's New" section

**Tests created:**
- Manual review tests (Tests 8.2.1-8.2.3)

#### Module-level imports

No imports needed - documentation files only.

#### Algorithm

##### Documentation Updates

1. **cycles.md**: Add new section explaining top-level API
2. **api-reference.md**: Document new public functions
3. **README.md**: Update features list and add version notice

#### Implementation

##### Code 8.1.1: Update doc/cycles.md

**File:** `doc/cycles.md`

**Action:** Add new section after existing cycle documentation

````markdown
#### Top-Level Cycle Registration

**Added in v1.1.0**

Cycles can be registered as top-level objects using `add_cycle()` and `add_cycles()`, providing an alternative to inline `COMMAND_CYCLE` definitions.

##### API Functions

**`add_cycle(cycle_def)`**

Register a single cycle definition:

```python
from spafw37 import core as spafw37
from spafw37.constants.cycle import CYCLE_COMMAND, CYCLE_NAME, CYCLE_LOOP

cycle = {
    CYCLE_COMMAND: 'my-command',
    CYCLE_NAME: 'my-cycle',
    CYCLE_LOOP: lambda: True
}
spafw37.add_cycle(cycle)
```

**`add_cycles(cycle_defs)`**

Register multiple cycle definitions:

```python
cycles = [
    {CYCLE_COMMAND: 'cmd1', CYCLE_NAME: 'cycle1', CYCLE_LOOP: loop1},
    {CYCLE_COMMAND: 'cmd2', CYCLE_NAME: 'cycle2', CYCLE_LOOP: loop2}
]
spafw37.add_cycles(cycles)
```

##### CYCLE_COMMAND Field

The `CYCLE_COMMAND` field identifies which command the cycle attaches to. It can be:

- **String**: Command name reference (command may exist or be registered later)
- **Dict**: Inline command definition (command registered immediately)

```python
### String reference
cycle = {
    CYCLE_COMMAND: 'existing-command',
    CYCLE_NAME: 'my-cycle',
    CYCLE_LOOP: loop_fn
}

### Inline definition
cycle = {
    CYCLE_COMMAND: {
        COMMAND_NAME: 'new-command',
        COMMAND_ACTION: action_fn
    },
    CYCLE_NAME: 'my-cycle',
    CYCLE_LOOP: loop_fn
}
```

##### Registration Order

Cycles can be registered before or after their target commands:

```python
### Cycle before command
spafw37.add_cycle({CYCLE_COMMAND: 'future-cmd', ...})
spafw37.add_command({COMMAND_NAME: 'future-cmd', ...})

### Command before cycle
spafw37.add_command({COMMAND_NAME: 'existing-cmd', ...})
spafw37.add_cycle({CYCLE_COMMAND: 'existing-cmd', ...})
```

##### Duplicate Handling

When a cycle is registered for a command that already has a cycle (via multiple `add_cycle()` calls or both inline and top-level):

- **Identical definitions**: First registration wins, subsequent identical registrations are silently skipped
- **Different definitions**: `ValueError` is raised to prevent conflicting configurations

This allows the same cycle definition to appear in multiple modules (useful for testing and modular code) while catching actual conflicts.

##### Benefits

- **API Consistency**: Matches `add_param()`/`add_params()` and `add_command()`/`add_commands()` patterns
- **Separation of Concerns**: Cycles defined separately from commands
- **Cleaner Organisation**: Related cycles grouped together
- **Flexible Order**: Register cycles and commands in any order
- **Inline Commands**: Commands can be defined inline in `CYCLE_COMMAND` field

See `examples/cycles_toplevel_api.py` for complete usage examples.
````

##### Code 8.1.2: Update doc/api-reference.md

**File:** `doc/api-reference.md`

**Action:** Add new section in core API functions area

````markdown
##### add_cycle(cycle_def)

Register a cycle definition for a command.

**Added in v1.1.0**

**Parameters:**
- `cycle_def` (dict): Cycle definition containing:
  - `CYCLE_COMMAND` (str or dict): Target command name or inline definition (required)
  - `CYCLE_NAME` (str): Cycle identifier (required)
  - `CYCLE_LOOP` (callable): Loop condition function (required)
  - `CYCLE_INIT` (callable): Initialisation function (optional)
  - `CYCLE_LOOP_START` (callable): Loop start function (optional)
  - `CYCLE_LOOP_END` (callable): Loop end function (optional)
  - `CYCLE_END` (callable): Cleanup function (optional)
  - `CYCLE_COMMANDS` (list): Commands in cycle (optional)

**Returns:** None

**Raises:**
- `ValueError`: If required fields missing or conflicting cycle registered

**Example:**
```python
from spafw37 import core as spafw37
cycle = {
    CYCLE_COMMAND: 'process',
    CYCLE_NAME: 'process-cycle',
    CYCLE_LOOP: lambda: True
}
spafw37.add_cycle(cycle)
```

---

##### add_cycles(cycle_defs)

Register multiple cycle definitions.

**Added in v1.1.0**

**Parameters:**
- `cycle_defs` (list): List of cycle definition dicts

**Returns:** None

**Raises:**
- `ValueError`: If any cycle validation fails

**Example:**
```python
from spafw37 import core as spafw37
cycles = [
    {CYCLE_COMMAND: 'cmd1', CYCLE_NAME: 'cycle1', CYCLE_LOOP: loop1},
    {CYCLE_COMMAND: 'cmd2', CYCLE_NAME: 'cycle2', CYCLE_LOOP: loop2}
]
spafw37.add_cycles(cycles)
```
````

##### Code 8.1.3: Update README.md features list

**File:** `README.md`

**Action:** Add to Features section and create What's New section

````markdown
<!-- In Features section, add bullet: -->
- **Top-Level Cycle Registration**: Define cycles with `add_cycle()` and `add_cycles()` functions, separate from commands, for cleaner code organisation

<!-- Add new section after Installation: -->
#### What's New in v1.1.0

- **Top-Level Cycle API**: New `add_cycle()` and `add_cycles()` functions allow cycles to be registered as top-level objects, matching the pattern established by `add_param()` and `add_command()`
- **Inline Command Definitions**: The `CYCLE_COMMAND` field now supports both string references and inline command definitions (dicts)
- **Flexible Registration Order**: Cycles can be registered before or after their target commands
- **Equivalency Checking**: Duplicate cycle registrations with identical definitions are silently skipped; different definitions raise errors

See `doc/cycles.md` and `examples/cycles_toplevel_api.py` for details.

<!-- In Examples section, add to list: -->
- `cycles_toplevel_api.py` - Top-level cycle registration with add_cycle() and add_cycles()
````

##### Test 8.2.1: cycles.md includes new top-level API section

**File:** Manual review

```gherkin
Scenario: Review cycles.md for top-level API documentation
  Given the updated cycles.md file
  When reviewing the content
  Then a "Top-Level Cycle Registration" section should exist
  And it should document add_cycle() and add_cycles() functions
  And it should explain CYCLE_COMMAND string vs dict formats
  And it should cover registration order flexibility
  And it should explain duplicate handling behaviour
  
  # Tests: User guide completeness
  # Validates: Developers can learn to use new API
```

**Manual review checklist:**
- [ ] "Top-Level Cycle Registration" section exists
- [ ] Section marked "**Added in v1.1.0**"
- [ ] `add_cycle()` function documented with example
- [ ] `add_cycles()` function documented with example
- [ ] CYCLE_COMMAND string vs dict formats explained
- [ ] Registration order flexibility documented
- [ ] Duplicate handling (equivalency checking) explained
- [ ] Link to `examples/cycles_toplevel_api.py` included
- [ ] UK English spelling throughout (behaviour, organisation, etc.)

##### Test 8.2.2: api-reference.md includes new functions

**File:** Manual review

```gherkin
Scenario: Review api-reference.md for function signatures
  Given the updated api-reference.md file
  When searching for add_cycle() and add_cycles()
  Then both functions should be listed with parameters
  And return types should be documented
  And parameter descriptions should be complete
  
  # Tests: API reference completeness
  # Validates: Developer reference includes new functions
```

**Manual review checklist:**
- [ ] `add_cycle(cycle_def)` documented with full signature
- [ ] `add_cycles(cycle_defs)` documented with full signature
- [ ] Both functions marked "**Added in v1.1.0**"
- [ ] Parameter types specified (dict, list)
- [ ] Required vs optional parameters indicated
- [ ] CYCLE_COMMAND field types documented (str or dict)
- [ ] Return types documented (None)
- [ ] Exceptions documented (ValueError)
- [ ] Code examples provided for both functions
- [ ] UK English spelling throughout

##### Test 8.2.3: README.md features list updated

**File:** Manual review

```gherkin
Scenario: Review README.md features section
  Given the updated README.md file
  When reviewing the features list
  Then top-level cycle registration should be mentioned
  And code example should show new API
  And "What's New in v1.1.0" section should mention this feature
  
  # Tests: README feature visibility
  # Validates: Users discover new feature from README
```

**Manual review checklist:**
- [ ] Features list includes top-level cycle registration bullet
- [ ] "What's New in v1.1.0" section added
- [ ] What's New mentions `add_cycle()` and `add_cycles()`
- [ ] What's New mentions inline CYCLE_COMMAND support
- [ ] What's New mentions flexible registration order
- [ ] What's New mentions equivalency checking
- [ ] Link to `doc/cycles.md` included
- [ ] Examples list includes `cycles_toplevel_api.py`
- [ ] UK English spelling throughout (organisation, behaviour, etc.)

#### Implementation Order

1. Update `doc/cycles.md` (Code 8.1.1)
2. Update `doc/api-reference.md` (Code 8.1.2)
3. Update `README.md` (Code 8.1.3)
4. Manual review of all documentation (Tests 8.2.1-8.2.3)

#### Notes

- All documentation must use UK English spelling (behaviour, organisation, initialise, etc.)
- Mark all new sections with "**Added in v1.1.0**"
- Provide clear code examples in all documentation
- Cross-reference between documents (cycles.md ↔ examples, README ↔ docs)
- Ensure consistent terminology throughout all docs

[↑ Back to top](#table-of-contents)

---

## Further Considerations

### 1. Error handling for duplicate cycle definitions - RESOLVED

([#issuecomment-3692502569](https://github.com/minouris/spafw37/issues/63#issuecomment-3692502569)) ([Resolution](https://github.com/minouris/spafw37/issues/63#issuecomment-3692548285))

**Question:** Should the framework raise an error if a cycle is registered multiple times for the same command (either via multiple `add_cycle()` calls or via both top-level API and inline `COMMAND_CYCLE`)?

**Answer:** Equivalency checking with first-wins behavior

**Rationale:** When a cycle is registered for a command that already has a cycle, compare for deep equality. If exact duplicate (identical structure, values, functions), silently skip (no error). If different definition, raise `ValueError`. This allows the same definition to appear multiple times (useful for modular code, shared test fixtures) while catching true configuration conflicts. Cycles are immutable once registered - no editing capability needed.

**Implementation:** Add equivalency checking helper function for deep equality comparison. In `add_cycle()` and `_store_command()`, compare cycle definitions before raising errors. First definition wins when identical, error raised when different.

[↑ Back to top](#table-of-contents)

---

### 2. Validation of CYCLE_COMMAND field - RESOLVED

([#issuecomment-3692534496](https://github.com/minouris/spafw37/issues/63#issuecomment-3692534496)) ([Resolution](https://github.com/minouris/spafw37/issues/63#issuecomment-3692587601))

**Question:** What validation should be performed on the `CYCLE_COMMAND` field when a cycle is registered via `add_cycle()`?

**Answer:** Immediate validation of cycle structure, deferred validation of command reference

**Rationale:** Validation is performed immediately when a cycle definition is complete. Required fields (like `CYCLE_LOOP`, `CYCLE_NAME`) and cycle structure are validated immediately. However, the `CYCLE_COMMAND` field does NOT require the command to exist yet (deferred validation of reference). This allows flexible registration order (cycles before commands or vice versa) while catching structural errors immediately.

**Implementation:** `add_cycle()` validates cycle definition structure but does NOT check if command exists. When command is registered, cycle is attached and full integration validation occurs via existing `cycle.register_cycle()`.

[↑ Back to top](#table-of-contents)

---

### 3. Priority when both inline and top-level cycles exist - RESOLVED

([#issuecomment-3692535462](https://github.com/minouris/spafw37/issues/63#issuecomment-3692535462)) ([Resolution](https://github.com/minouris/spafw37/issues/63#issuecomment-3692589909))

**Question:** If a cycle is defined both via top-level `add_cycle()` AND via inline `COMMAND_CYCLE` for the same command, which should take precedence?

**Answer:** First definition wins with equivalency checking (same as Q1)

**Rationale:** When a cycle is registered for a command that already has a cycle (either via another `add_cycle()` call or inline `COMMAND_CYCLE`), compare for deep equality. If exact duplicate, silently skip (no error). If different definition, raise `ValueError` with clear message. This provides consistent behavior regardless of whether the duplicate comes from multiple `add_cycle()` calls or from inline vs top-level definitions.

**Implementation:** Same equivalency checking logic applies whether comparing two top-level cycles or comparing top-level vs inline cycle. First registration wins when identical, error raised when different. Integration point in `_store_command()` checks both inline and top-level cycles and applies equivalency checking.

[↑ Back to top](#table-of-contents)

---

### 4. Related Issue: Commands and params validation

**Issue #87:** Add equivalency checking validation to add_command() and add_param()

The design decisions for cycles (equivalency checking, immutable definitions) revealed that commands and params currently lack this validation. Issue #87 has been created to address this separately from the cycle implementation.

[↑ Back to top](#table-of-contents)

---

## Success Criteria

This issue is considered successfully implemented when:

**Functional Requirements:**
- [ ] `add_cycle()` function accepts a single cycle definition dict and registers it correctly
- [ ] `add_cycles()` function accepts a list of cycle definition dicts and registers all of them
- [ ] Cycles registered via top-level API attach to commands during command registration
- [ ] Cycles defined with `CYCLE_COMMAND` property correctly identify their target command
- [ ] Commands with top-level cycles execute cycle functions (init, loop, loop_start, loop_end, end) correctly
- [ ] Cycle commands remain non-invocable from CLI when registered via top-level API
- [ ] Cycle parameter merging works correctly for top-level cycles (params from cycle commands merge into parent)
- [ ] Phase consistency validation applies to top-level cycles (all cycle commands same phase as parent)
- [ ] Top-level cycle API follows existing validation rules from inline cycles (required fields, nesting depth, etc.)

**Integration Requirements:**
- [ ] Inline `COMMAND_CYCLE` definitions continue to work unchanged (backward compatibility)
- [ ] Both inline and top-level cycle definition methods can coexist in same application
- [ ] Error handling for duplicate/conflicting cycle definitions works as designed (per Further Considerations resolution)
- [ ] Validation of `CYCLE_COMMAND` field works as designed (per Further Considerations resolution)
- [ ] Priority between inline and top-level cycles works as designed (per Further Considerations resolution)

**API Consistency Requirements:**
- [ ] `add_cycle()` and `add_cycles()` are exposed through `core.py` facade (public API)
- [ ] Function signatures and behaviour match patterns from `add_param()`/`add_params()` and `add_command()`/`add_commands()`
- [ ] `CYCLE_COMMAND` constant is properly exported from `constants.cycle` module
- [ ] Error messages are clear and actionable

**Testing Requirements:**
- [ ] Unit tests cover `add_cycle()` and `add_cycles()` functions in `cycle.py`
- [ ] Unit tests cover cycle-command association logic in `command.py`
- [ ] Unit tests cover public API functions in `core.py`
- [ ] Integration tests demonstrate top-level cycle execution
- [ ] Tests verify backward compatibility with inline cycle definitions
- [ ] Tests cover error cases per Further Considerations resolutions
- [ ] Test coverage remains at or above 80%

**Documentation Requirements:**
- [ ] API reference documents new `add_cycle()` and `add_cycles()` functions
- [ ] Cycles user guide updated with top-level API examples
- [ ] New example file demonstrates top-level cycle registration
- [ ] README updated with new API in features list
- [ ] Code examples show both inline and top-level approaches

**Compatibility Requirements:**
- [ ] Works with Python 3.7.0+
- [ ] All existing tests continue to pass
- [ ] No breaking changes to existing cycle functionality

[↑ Back to top](#table-of-contents)

---

## Planning Checklist

This checklist tracks completion of this planning document.

**Plan Structure:**
- [x] Overview section complete with architectural decisions
- [ ] Program Flow Analysis complete (if applicable)
- [x] All implementation steps identified and outlined
- [x] Further Considerations documented (all marked PENDING or RESOLVED)
  - [x] Q1: Error handling for duplicate cycle definitions answered and resolved (Comment #3692502569)
  - [x] Q2: Validation of CYCLE_COMMAND field answered and resolved (Comment #3692534496)
  - [x] Q3: Priority when both inline and top-level cycles exist answered and resolved (Comment #3692535462)
- [x] Success Criteria defined (feature outcomes)
- [x] Implementation Checklist created (TDD workflow)
- [ ] CHANGES section populated for release
- [x] Table of Contents updated to reflect all sections

**Implementation Details:**
- [x] All implementation steps have detailed code blocks (in scratch files, now merged)
- [x] All functions have corresponding test specifications
- [x] All code blocks follow X.Y.Z numbering scheme
- [x] All tests written in Gherkin + Python format
- [x] Module-level imports consolidated in Step 1
- [x] No nesting violations (max 2 levels)
- [x] No nested blocks exceeding 2 lines
- [x] All helper functions extracted and documented

**Documentation:**
- [ ] All affected documentation files identified (Step 7)
- [ ] Example files planned (cycles_top_level.py)
- [ ] API reference updates planned (doc/api-reference.md)
- [ ] User guide updates planned (doc/cycles.md, README.md)

**Quality Verification:**
- [ ] All code follows Python 3.7.0 compatibility requirements
- [ ] All code follows UK English spelling conventions
- [ ] No lazy naming (tmp, data, result, i, j, etc.)
- [ ] All functions have proper docstrings
- [ ] Regression tests planned for modified functions

**Ready for Implementation:**
- [ ] Plan reviewed and approved
- [ ] All Further Considerations resolved
- [ ] Success Criteria agreed upon
- [ ] Implementation Checklist ready to execute

[↑ Back to top](#table-of-contents)

---

## Implementation Log

This section will record any errors, deviations, or unexpected issues encountered during implementation (Step 8).

**This section will be populated during Step 8: Implement from Plan.**

[↑ Back to top](#table-of-contents)

---

## Implementation Checklist

This checklist tracks the test-driven development workflow for implementing issue #63.

Each line item that requires action must have a checkbox [ ].

---

### Step 1: Add cycle storage and registration functions to cycle.py

#### 1.1: Module-level `_cycles` storage

- [ ] Write test for module-level storage initialisation
  - [ ] Patch: Add `test_cycles_module_level_storage_initialised()` to `tests/test_cycle.py`
  - [ ] Test run: `pytest tests/test_cycle.py::test_cycles_module_level_storage_initialised -v` (expect FAIL - red)
- [ ] Implement `_cycles` module-level storage
  - [ ] Patch: Add `_cycles = {}` to `src/spafw37/cycle.py` at module level
  - [ ] Test run: `pytest tests/test_cycle.py::test_cycles_module_level_storage_initialised -v` (expect PASS - green)

#### 1.2: `_extract_command_name()` helper

- [ ] Write tests for `_extract_command_name()`
  - [ ] Patch: Add `test_extract_command_name_from_string()` to `tests/test_cycle.py`
  - [ ] Patch: Add `test_extract_command_name_from_dict()` to `tests/test_cycle.py`
  - [ ] Patch: Add `test_extract_command_name_validates_dict_has_command_name()` to `tests/test_cycle.py`
  - [ ] Test run: `pytest tests/test_cycle.py::test_extract_command_name_from_string -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_cycle.py::test_extract_command_name_from_dict -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_cycle.py::test_extract_command_name_validates_dict_has_command_name -v` (expect FAIL - red)
- [ ] Implement `_extract_command_name()`
  - [ ] Patch: Add function to `src/spafw37/cycle.py`
  - [ ] Test run: `pytest tests/test_cycle.py::test_extract_command_name_from_string -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py::test_extract_command_name_from_dict -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py::test_extract_command_name_validates_dict_has_command_name -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py -v` (regression check)

#### 1.3: `_validate_cycle_required_fields()` helper

- [ ] Write tests for `_validate_cycle_required_fields()`
  - [ ] Patch: Add `test_validate_cycle_required_fields_accepts_valid_cycle()` to `tests/test_cycle.py`
  - [ ] Patch: Add `test_validate_cycle_required_fields_rejects_missing_cycle_command()` to `tests/test_cycle.py`
  - [ ] Patch: Add `test_validate_cycle_required_fields_rejects_missing_cycle_name()` to `tests/test_cycle.py`
  - [ ] Patch: Add `test_validate_cycle_required_fields_rejects_missing_cycle_loop()` to `tests/test_cycle.py`
  - [ ] Test run: `pytest tests/test_cycle.py::test_validate_cycle_required_fields_accepts_valid_cycle -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_cycle.py::test_validate_cycle_required_fields_rejects_missing_cycle_command -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_cycle.py::test_validate_cycle_required_fields_rejects_missing_cycle_name -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_cycle.py::test_validate_cycle_required_fields_rejects_missing_cycle_loop -v` (expect FAIL - red)
- [ ] Implement `_validate_cycle_required_fields()`
  - [ ] Patch: Add function to `src/spafw37/cycle.py`
  - [ ] Test run: `pytest tests/test_cycle.py::test_validate_cycle_required_fields_accepts_valid_cycle -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py::test_validate_cycle_required_fields_rejects_missing_cycle_command -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py::test_validate_cycle_required_fields_rejects_missing_cycle_name -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py::test_validate_cycle_required_fields_rejects_missing_cycle_loop -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py -v` (regression check)

#### 1.4: `_cycles_are_equivalent()` helper

- [ ] Write tests for `_cycles_are_equivalent()`
  - [ ] Patch: Add `test_cycles_are_equivalent_returns_true_for_identical_cycles()` to `tests/test_cycle.py`
  - [ ] Patch: Add `test_cycles_are_equivalent_returns_false_for_different_required_fields()` to `tests/test_cycle.py`
  - [ ] Patch: Add `test_cycles_are_equivalent_returns_false_for_different_optional_fields()` to `tests/test_cycle.py`
  - [ ] Patch: Add `test_cycles_are_equivalent_compares_function_references()` to `tests/test_cycle.py`
  - [ ] Test run: `pytest tests/test_cycle.py::test_cycles_are_equivalent_returns_true_for_identical_cycles -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_cycle.py::test_cycles_are_equivalent_returns_false_for_different_required_fields -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_cycle.py::test_cycles_are_equivalent_returns_false_for_different_optional_fields -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_cycle.py::test_cycles_are_equivalent_compares_function_references -v` (expect FAIL - red)
- [ ] Implement `_cycles_are_equivalent()`
  - [ ] Patch: Add function to `src/spafw37/cycle.py`
  - [ ] Test run: `pytest tests/test_cycle.py::test_cycles_are_equivalent_returns_true_for_identical_cycles -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py::test_cycles_are_equivalent_returns_false_for_different_required_fields -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py::test_cycles_are_equivalent_returns_false_for_different_optional_fields -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py::test_cycles_are_equivalent_compares_function_references -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py -v` (regression check)

#### 1.5: `add_cycle()` public function

- [ ] Write tests for `add_cycle()`
  - [ ] Patch: Add `test_add_cycle_registers_single_cycle()` to `tests/test_cycle.py`
  - [ ] Patch: Add `test_add_cycle_with_inline_cycle_command_definition()` to `tests/test_cycle.py`
  - [ ] Patch: Add `test_add_cycle_with_inline_cycle_command_extracts_name()` to `tests/test_cycle.py`
  - [ ] Patch: Add `test_add_cycle_validates_required_cycle_command_field()` to `tests/test_cycle.py`
  - [ ] Patch: Add `test_add_cycle_validates_required_cycle_name_field()` to `tests/test_cycle.py`
  - [ ] Patch: Add `test_add_cycle_validates_required_cycle_loop_field()` to `tests/test_cycle.py`
  - [ ] Patch: Add `test_add_cycle_equivalency_checking_identical_cycles_skip()` to `tests/test_cycle.py`
  - [ ] Patch: Add `test_add_cycle_equivalency_checking_different_cycles_raise_error()` to `tests/test_cycle.py`
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycle_registers_single_cycle -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycle_with_inline_cycle_command_definition -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycle_with_inline_cycle_command_extracts_name -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycle_validates_required_cycle_command_field -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycle_validates_required_cycle_name_field -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycle_validates_required_cycle_loop_field -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycle_equivalency_checking_identical_cycles_skip -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycle_equivalency_checking_different_cycles_raise_error -v` (expect FAIL - red)
- [ ] Implement `add_cycle()`
  - [ ] Patch: Add function to `src/spafw37/cycle.py`
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycle_registers_single_cycle -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycle_with_inline_cycle_command_definition -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycle_with_inline_cycle_command_extracts_name -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycle_validates_required_cycle_command_field -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycle_validates_required_cycle_name_field -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycle_validates_required_cycle_loop_field -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycle_equivalency_checking_identical_cycles_skip -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycle_equivalency_checking_different_cycles_raise_error -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py -v` (regression check)

#### 1.6: `add_cycles()` public function

- [ ] Write tests for `add_cycles()`
  - [ ] Patch: Add `test_add_cycles_registers_multiple_cycles()` to `tests/test_cycle.py`
  - [ ] Patch: Add `test_add_cycles_with_mixed_inline_and_string_cycle_commands()` to `tests/test_cycle.py`
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycles_registers_multiple_cycles -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycles_with_mixed_inline_and_string_cycle_commands -v` (expect FAIL - red)
- [ ] Implement `add_cycles()`
  - [ ] Patch: Add function to `src/spafw37/cycle.py`
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycles_registers_multiple_cycles -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py::test_add_cycles_with_mixed_inline_and_string_cycle_commands -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py -v` (regression check)

#### 1.7: `get_cycle()` public function

- [ ] Write tests for `get_cycle()`
  - [ ] Patch: Add `test_get_cycle_retrieves_registered_cycle()` to `tests/test_cycle.py`
  - [ ] Patch: Add `test_get_cycle_returns_none_for_unregistered_command()` to `tests/test_cycle.py`
  - [ ] Test run: `pytest tests/test_cycle.py::test_get_cycle_retrieves_registered_cycle -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_cycle.py::test_get_cycle_returns_none_for_unregistered_command -v` (expect FAIL - red)
- [ ] Implement `get_cycle()`
  - [ ] Patch: Add function to `src/spafw37/cycle.py`
  - [ ] Test run: `pytest tests/test_cycle.py::test_get_cycle_retrieves_registered_cycle -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py::test_get_cycle_returns_none_for_unregistered_command -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_cycle.py -v` (regression check)

### Step 2: Add support for inline command definitions in cycles

#### 2.1: `_register_inline_command()` helper in command.py

- [ ] Write tests for `_register_inline_command()`
  - [ ] Patch: Add `test_register_inline_command_with_valid_dict()` to `tests/test_command.py`
  - [ ] Patch: Add `test_register_inline_command_validates_command_name()` to `tests/test_command.py`
  - [ ] Patch: Add `test_register_inline_command_prevents_overwrite()` to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_register_inline_command_with_valid_dict -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_command.py::test_register_inline_command_validates_command_name -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_command.py::test_register_inline_command_prevents_overwrite -v` (expect FAIL - red)
- [ ] Implement `_register_inline_command()`
  - [ ] Patch: Add function to `src/spafw37/command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_register_inline_command_with_valid_dict -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_command.py::test_register_inline_command_validates_command_name -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_command.py::test_register_inline_command_prevents_overwrite -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_command.py -v` (regression check)

### Step 3: Modify command registration to check for top-level cycles

#### 3.1: Update `add_command()` to attach top-level cycles

- [ ] Write tests for top-level cycle attachment in `add_command()`
  - [ ] Patch: Add `test_add_command_attaches_top_level_cycle()` to `tests/test_command.py`
  - [ ] Patch: Add `test_add_command_prefers_inline_cycle_over_top_level()` to `tests/test_command.py`
  - [ ] Patch: Add `test_add_command_with_no_cycle()` to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_add_command_attaches_top_level_cycle -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_command.py::test_add_command_prefers_inline_cycle_over_top_level -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_command.py::test_add_command_with_no_cycle -v` (expect FAIL - red)
- [ ] Update `add_command()` implementation
  - [ ] Patch: Modify `add_command()` in `src/spafw37/command.py` to check `cycle.get_cycle()`
  - [ ] Test run: `pytest tests/test_command.py::test_add_command_attaches_top_level_cycle -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_command.py::test_add_command_prefers_inline_cycle_over_top_level -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_command.py::test_add_command_with_no_cycle -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_command.py -v` (regression check)

### Step 4: Expose new functions through core.py facade

#### 4.1: Export `add_cycle()` and `add_cycles()` from core.py

- [ ] Write tests for core.py exports
  - [ ] Patch: Add `test_core_exports_add_cycle()` to `tests/test_core.py`
  - [ ] Patch: Add `test_core_exports_add_cycles()` to `tests/test_core.py`
  - [ ] Test run: `pytest tests/test_core.py::test_core_exports_add_cycle -v` (expect FAIL - red)
  - [ ] Test run: `pytest tests/test_core.py::test_core_exports_add_cycles -v` (expect FAIL - red)
- [ ] Update core.py to export functions
  - [ ] Patch: Add `add_cycle` and `add_cycles` to `src/spafw37/core.py`
  - [ ] Test run: `pytest tests/test_core.py::test_core_exports_add_cycle -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_core.py::test_core_exports_add_cycles -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_core.py -v` (regression check)

### Step 5: Update constants file with CYCLE_COMMAND property

#### 5.1: Add CYCLE_COMMAND constant

- [ ] Write test for CYCLE_COMMAND constant
  - [ ] Patch: Add `test_cycle_command_constant_exists()` to `tests/test_constants_cycle.py`
  - [ ] Test run: `pytest tests/test_constants_cycle.py::test_cycle_command_constant_exists -v` (expect FAIL - red)
- [ ] Add constant to constants file
  - [ ] Patch: Add `CYCLE_COMMAND = 'cycle-command'` to `src/spafw37/constants/cycle.py`
  - [ ] Test run: `pytest tests/test_constants_cycle.py::test_cycle_command_constant_exists -v` (expect PASS - green)
  - [ ] Test run: `pytest tests/test_constants_cycle.py -v` (regression check)

### Step 6: Create example demonstrating new API

#### 6.1: Create cycles_top_level.py example

- [ ] Create example file
  - [ ] Patch: Create `examples/cycles_top_level.py` with working example
  - [ ] Test run: `cd examples && python cycles_top_level.py --help` (expect usage output)
  - [ ] Test run: `cd examples && python cycles_top_level.py` (expect successful execution)

### Step 7: Update documentation

#### 7.1: Update API reference

- [ ] Update API reference
  - [ ] Patch: Add `add_cycle()` and `add_cycles()` documentation to `doc/api-reference.md`
  - [ ] Verify: Documentation rendered correctly in markdown preview

#### 7.2: Update cycles user guide

- [ ] Update cycles user guide
  - [ ] Patch: Add top-level API examples to `doc/cycles.md`
  - [ ] Verify: Documentation rendered correctly in markdown preview

#### 7.3: Update README

- [ ] Update README features list
  - [ ] Patch: Add top-level cycles API to features list in `README.md`
  - [ ] Verify: Documentation rendered correctly in markdown preview

### Final Verification

- [ ] All implementation steps completed
- [ ] All tests passing
  - [ ] Test run: `pytest tests/ -v`
- [ ] Coverage target met (80%+)
  - [ ] Test run: `pytest tests/ --cov=spafw37 --cov-report=term-missing`
- [ ] No regressions introduced
- [ ] Code review checklist verified
- [ ] Example file executes successfully
- [ ] Documentation updates complete

[↑ Back to top](#table-of-contents)

---

## CHANGES for v1.1.0 Release

**PLACEHOLDER:** This section will contain the release notes once Step 6 is complete.

[↑ Back to top](#table-of-contents)
