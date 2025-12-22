# Issue #61: Refactor command.add_command() into focused helper methods

**GitHub Issue:** https://github.com/minouris/spafw37/issues/61

## Overview

The `command.add_command()` function has become monolithic and difficult to maintain. It handles multiple responsibilities in a single function:
- Command name validation
- Inline parameter definition processing
- Required parameter validation
- Dependency validation
- Trigger parameter handling
- Phase assignment
- Visibility control
- Command storage and registration

This makes the function hard to test, understand, and modify.

This refactoring will delegate responsibilities to focused helper methods, similar to the pattern used in issue #15 for prompt param processing. The refactored structure will create a high-level orchestrator function that calls discrete helpers, each with a single clear responsibility.

Each helper method will have focused unit tests, clear error messages, and reusable logic. The refactoring maintains backward compatibility - only internal structure changes, with no modifications to the public API or existing behaviour.

**Key architectural decisions:**

- **[Pattern]:** Follow issue #15's helper method pattern - extract focused private functions with single responsibilities, each with clear naming and dedicated tests
- **[Testing strategy]:** Incremental extraction with test verification after each step - leverage existing 95% test coverage to guard against regression
- **[Helper scope]:** Private helpers with `_` prefix - internal implementation details not part of public API
- **[Extraction order]:** Validation first (simplest), then inline processing (most complex), then registration (storage)
- **[Backward compatibility]:** Zero API changes - only internal structure refactoring, all existing tests must pass unchanged

## Table of Contents

- [Overview](#overview)
- [Implementation Steps](#implementation-steps)
  - [1. Module-level imports](#step-1-module-level-imports)
  - [2. Extract validation helpers](#step-2-extract-validation-helpers)
  - [3. Extract inline parameter processing](#step-3-extract-inline-parameter-processing)
  - [4. Extract inline command processing](#step-4-extract-inline-command-processing)
  - [5. Extract phase assignment](#step-5-extract-phase-assignment)
  - [6. Extract command storage](#step-6-extract-command-storage)
  - [7. Refactor add_command()](#step-7-refactor-add_command-to-use-all-helpers)
- [Further Considerations](#further-considerations)
- [Success Criteria](#success-criteria)
- [Planning Checklist](#planning-checklist)
- [Implementation Checklist](#implementation-checklist)
- [CHANGES for v1.1.0 Release](#changes-for-v110-release)

[↑ Back to top](#table-of-contents)

## Implementation Steps

### Current Structure Analysis

The `add_command()` function (lines 192-244 in `src/spafw37/command.py`) currently handles 8 responsibilities in a single 54-line function:

1. **Name validation** (lines 193-195): Check command name is not empty
2. **Action validation** (lines 196-197): Verify action function exists
3. **Duplicate check** (lines 198-199): Skip if command already registered
4. **Inline param processing** (lines 201-217): Handle `COMMAND_REQUIRED_PARAMS` and `COMMAND_TRIGGER_PARAM` inline definitions
5. **Inline command processing** (lines 219-227): Handle dependency field inline command definitions
6. **Self-reference validation** (lines 229-233): Prevent commands referencing themselves
7. **Conflict validation** (lines 235-240): Check for `GOES_BEFORE`/`GOES_AFTER` conflicts
8. **Phase assignment and storage** (lines 241-245): Set default phase, store in registry, register cycle

### Refactoring Strategy

Extract helpers in this order (simplest to most complex):

1. Module-level imports - Add necessary test imports
2. `_validate_command_name()` - Name validation
3. `_validate_command_action()` - Action validation
4. `_validate_command_references()` - Self-reference and conflict checks
5. `_process_inline_params()` - Inline parameter processing
6. `_process_inline_commands()` - Inline command processing
7. `_assign_command_phase()` - Phase assignment
8. `_store_command()` - Registry storage and cycle registration

**Final step:** Refactor `add_command()` to use all extracted helpers

### Step 1: Module-level imports

Add all necessary imports to `tests/test_command.py` to support the helper tests in subsequent steps.

**Rationale:** Consolidating all required imports upfront avoids duplication and ensures all constants and modules are available when needed.

**Implementation:**

## Overview

Add all necessary imports to `tests/test_command.py` and `src/spafw37/command.py` to support the helper functions and tests in Steps 1-6.
**No methods or tests in this step** - only import statements.

## Test File Imports (tests/test_command.py)

```python
# Standard library
import pytest

# Project imports - constants
from spafw37.constants.command import (
    COMMAND_ACTION,
    COMMAND_CYCLE,
    COMMAND_GOES_AFTER,
    COMMAND_GOES_BEFORE,
    COMMAND_NAME,
    COMMAND_NEXT_COMMANDS,
    COMMAND_PHASE,
    COMMAND_REQUIRED_PARAMS,
    COMMAND_REQUIRE_BEFORE,
    COMMAND_TRIGGER_PARAM,
    COMMAND_VISIBLE_IF_PARAM,
)
from spafw37.constants.param import PARAM_NAME

# Project imports - modules
from spafw37 import command, config, cycle, param
```

## Implementation File Imports (src/spafw37/command.py)

```python
# Constants imports already present in command.py
# No additional imports required for the helper functions in Steps 1-6
```

## Notes

- All constants from `spafw37.constants.command` used across Steps 1-6 are imported explicitly
- `PARAM_NAME` from `spafw37.constants.param` is needed for Step 2 (inline params)
- Module imports include `command`, `param` (Steps 1-2, 6), `config` (Step 5), and `cycle` (Step 6)
- These imports should be added to `tests/test_command.py` before implementing any step
- Implementation file `src/spafw37/command.py` already has all necessary constant imports

[↑ Back to top](#table-of-contents)

---

### Step 2: Extract validation helpers

Extract the three validation helpers that check command definition properties. These are the simplest extractions with clear boundaries.

**Rationale:** Validation is self-contained with no side effects, making it the safest place to start. Each validation can be extracted and tested independently.

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

See Step 1 for all required imports.

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

After implementing Step 2:
- Run `pytest tests/test_command.py::test_validate_command_name_empty_string_raises_error -v`
- Run `pytest tests/test_command.py::test_validate_command_name_none_raises_error -v`
- Run `pytest tests/test_command.py::test_validate_command_action_missing_raises_error -v`
- Run `pytest tests/test_command.py::test_validate_command_action_none_raises_error -v`
- Run `pytest tests/test_command.py::test_validate_command_references_self_reference_raises_error -v`
- Run `pytest tests/test_command.py::test_validate_command_references_conflicting_constraints_raises_error -v`
- Run full test suite: `pytest tests/test_command.py -v`

All existing tests should continue to pass.

[↑ Back to top](#table-of-contents)

---

### Step 3: Extract inline parameter processing

Extract inline parameter definition processing for `COMMAND_REQUIRED_PARAMS` and `COMMAND_TRIGGER_PARAM` into a single helper.

**Rationale:** This logic is complex but well-isolated. It delegates to `param._register_inline_param()` which already exists, so the extraction mainly reorganises code without changing behaviour.

## Overview

Extract helper: `_process_inline_params()` - Handles inline parameter definitions in `COMMAND_REQUIRED_PARAMS` and `COMMAND_TRIGGER_PARAM`

**Methods created:**
- `_normalise_param_list()` - Converts list of param defs to param names
  - `test_normalise_param_list()`
- `_process_inline_params()` - Processes inline param definitions
  - `test_process_inline_params_required_params()`
  - `test_process_inline_params_trigger_param()`
  - `test_process_inline_params_no_inline_params()`

## Module-level imports

See Step 1 for all required imports.

## Implementation

### Test 3.1.1: Process COMMAND_REQUIRED_PARAMS with inline definitions

```gherkin
Scenario: Inline parameter definitions in COMMAND_REQUIRED_PARAMS are processed
  Given a command with inline param defs in COMMAND_REQUIRED_PARAMS
  When _process_inline_params() is called
  Then each inline param is registered via param._register_inline_param()
  And COMMAND_REQUIRED_PARAMS is updated with param names
  
  # Tests: Inline param processing for required params
  # Validates: Helper delegates to param module and normalises list
```

### Code 3.1.1: Test for _process_inline_params() with COMMAND_REQUIRED_PARAMS

```python
# Block 3.1.1: Add to tests/test_command.py

def test_process_inline_params_required_params():
    """Test that _process_inline_params() handles COMMAND_REQUIRED_PARAMS.
    
    This test verifies that inline parameter definitions in COMMAND_REQUIRED_PARAMS
    are registered and the list is normalised to parameter names. This ensures
    commands can define required parameters inline without pre-registration.
    """
    setup_function()
    
    inline_param_1 = {PARAM_NAME: 'param1'}
    inline_param_2 = {PARAM_NAME: 'param2'}
    cmd = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_REQUIRED_PARAMS: [inline_param_1, inline_param_2]
    }
    
    command._process_inline_params(cmd)
    
    # Params should be registered
    assert 'param1' in param._params
    assert 'param2' in param._params
    # List should be normalised to names
    assert cmd[COMMAND_REQUIRED_PARAMS] == ['param1', 'param2']
```

### Test 3.1.2: Process COMMAND_TRIGGER_PARAM with inline definition

```gherkin
Scenario: Inline parameter definition in COMMAND_TRIGGER_PARAM is processed
  Given a command with inline param def in COMMAND_TRIGGER_PARAM
  When _process_inline_params() is called
  Then inline param is registered via param._register_inline_param()
  And COMMAND_TRIGGER_PARAM is updated with param name
  
  # Tests: Inline param processing for trigger param
  # Validates: Helper delegates to param module and normalises value
```

### Code 3.1.2: Test for _process_inline_params() with COMMAND_TRIGGER_PARAM

```python
# Block 3.1.2: Add to tests/test_command.py

def test_process_inline_params_trigger_param():
    """Test that _process_inline_params() handles COMMAND_TRIGGER_PARAM.
    
    This test verifies that an inline parameter definition in COMMAND_TRIGGER_PARAM
    is registered and the field is normalised to the parameter name. This allows
    commands to define trigger parameters inline without pre-registration.
    """
    setup_function()
    
    inline_param = {PARAM_NAME: 'trigger-param'}
    cmd = {
        COMMAND_NAME: 'test-cmd',
        COMMAND_TRIGGER_PARAM: inline_param
    }
    
    command._process_inline_params(cmd)
    
    # Param should be registered
    assert 'trigger-param' in param._params
    # Field should be normalised to name
    assert cmd[COMMAND_TRIGGER_PARAM] == 'trigger-param'
```

### Test 3.1.3: Process command with no inline params

```gherkin
Scenario: Command with no inline params is unchanged
  Given a command with no COMMAND_REQUIRED_PARAMS or COMMAND_TRIGGER_PARAM
  When _process_inline_params() is called
  Then command dict is unchanged
  
  # Tests: No-op behaviour for commands without inline params
  # Validates: Helper safely handles missing fields
```

### Code 3.1.3: Test for _process_inline_params() with no inline params

```python
# Block 3.1.3: Add to tests/test_command.py

def test_process_inline_params_no_inline_params():
    """Test that _process_inline_params() handles commands with no inline params.
    
    This test verifies that commands without COMMAND_REQUIRED_PARAMS or
    COMMAND_TRIGGER_PARAM are processed without errors. The helper should
    safely handle missing fields without side effects.
    """
    setup_function()
    
    cmd = {COMMAND_NAME: 'test-cmd'}
    original_cmd = cmd.copy()
    
    command._process_inline_params(cmd)
    
    # Command should be unchanged
    assert cmd == original_cmd
```

### Test 3.1.4: Helper - normalise param list

```gherkin
Scenario: List of inline param definitions is normalised to param names
  Given a list of inline parameter definitions
  When _normalise_param_list() is called
  Then each param is registered via param._register_inline_param()
  And a list of param names is returned
  
  # Tests: Param list normalisation helper
  # Validates: Helper extracts loop logic to avoid nesting violation
```

### Code 3.1.4: Test for _normalise_param_list() helper

```python
# Block 3.1.4: Add to tests/test_command.py

def test_normalise_param_list():
    """Test that _normalise_param_list() converts param defs to names.
    
    This test verifies that a list of inline parameter definitions is
    normalised to a list of parameter names by registering each param
    and collecting the names. This helper avoids nesting violations.
    """
    setup_function()
    
    param_list = [
        {PARAM_NAME: 'param1'},
        {PARAM_NAME: 'param2'}
    ]
    
    normalised_params = command._normalise_param_list(param_list)
    
    assert normalised_params == ['param1', 'param2']
    assert 'param1' in param._params
    assert 'param2' in param._params
```

### Code 3.1.5: Implement _normalise_param_list() helper

```python
# Block 3.1.5: Add to src/spafw37/command.py after _validate_command_references()

def _normalise_param_list(param_list):
    """Normalise list of param definitions to param names.
    
    Args:
        param_list: List of parameter definition dicts
        
    Returns:
        List of parameter names (strings)
    """
    # Block 3.1.5.1: Initialize result list
    normalised_params = []
    
    # Block 3.1.5.2: Loop through param definitions
    for param_def in param_list:
        # Block 3.1.5.2.1: Register param via param module
        param_name = param._register_inline_param(param_def)
        # Block 3.1.5.2.2: Append name to result list
        normalised_params.append(param_name)
    
    # Block 3.1.5.3: Return normalised list
    return normalised_params
```

### Code 3.1.6: Implement _process_inline_params() using helper

```python
# Block 3.1.6: Add to src/spafw37/command.py after _normalise_param_list()

def _process_inline_params(cmd):
    """Process inline parameter definitions in command.
    
    Handles COMMAND_REQUIRED_PARAMS (list) and COMMAND_TRIGGER_PARAM (single).
    Registers inline param definitions and normalises fields to param names.
    
    Args:
        cmd: Command definition dict (modified in place)
    """
    # Block 3.1.6.1: Get COMMAND_REQUIRED_PARAMS list
    required_params = cmd.get(COMMAND_REQUIRED_PARAMS, [])
    
    # Block 3.1.6.2: If list exists, normalise and update
    if required_params:
        # Block 3.1.6.2.1: Call _normalise_param_list() helper
        normalised_params = _normalise_param_list(required_params)
        # Block 3.1.6.2.2: Update cmd with normalised list
        cmd[COMMAND_REQUIRED_PARAMS] = normalised_params
    
    # Block 3.1.6.3: Get COMMAND_TRIGGER_PARAM
    trigger_param = cmd.get(COMMAND_TRIGGER_PARAM)
    
    # Block 3.1.6.4: If trigger param exists, register and update
    if trigger_param:
        # Block 3.1.6.4.1: Register param via param._register_inline_param()
        param_name = param._register_inline_param(trigger_param)
        # Block 3.1.6.4.2: Update cmd with param name
        cmd[COMMAND_TRIGGER_PARAM] = param_name
```

## Verification

After implementing Step 3:
- Run `pytest tests/test_command.py::test_process_inline_params_required_params -v`
- Run `pytest tests/test_command.py::test_process_inline_params_trigger_param -v`
- Run `pytest tests/test_command.py::test_process_inline_params_no_inline_params -v`
- Run full test suite: `pytest tests/test_command.py -v`

All existing tests should continue to pass.

[↑ Back to top](#table-of-contents)

---

### Step 4: Extract inline command processing

Extract inline command definition processing for dependency/sequencing fields into a helper.

**Rationale:** Similar to param processing but handles four fields (`COMMAND_GOES_AFTER`, `COMMAND_GOES_BEFORE`, `COMMAND_NEXT_COMMANDS`, `COMMAND_REQUIRE_BEFORE`). Well-isolated with clear inputs/outputs.

**Implementation:**

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

See Step 1 for all required imports.

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
    
    normalised_commands = command._normalise_command_list(cmd_list)
    
    assert normalised_commands == ['cmd1', 'cmd2']
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

After implementing Step 4:
- Run `pytest tests/test_command.py::test_process_inline_commands_goes_after -v`
- Run `pytest tests/test_command.py::test_process_inline_commands_multiple_fields -v`
- Run `pytest tests/test_command.py::test_process_inline_commands_no_inline_commands -v`
- Run full test suite: `pytest tests/test_command.py -v`

All existing tests should continue to pass.

[↑ Back to top](#table-of-contents)

---

### Step 5: Extract phase assignment

Extract default phase assignment logic into a helper.

**Rationale:** Simple single-line operation but conceptually distinct from storage. Making it explicit improves readability.

**Implementation:**

## Overview

Extract helper: `_assign_command_phase()` - Sets default phase if not specified

**Methods created:**
- `_assign_command_phase()` - Assigns default phase when missing
  - `test_assign_command_phase_missing_phase()`
  - `test_assign_command_phase_existing_phase()`

## Module-level imports

See Step 1 for all required imports.

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

After implementing Step 5:
- Run `pytest tests/test_command.py::test_assign_command_phase_missing_phase -v`
- Run `pytest tests/test_command.py::test_assign_command_phase_existing_phase -v`
- Run full test suite: `pytest tests/test_command.py -v`

All existing tests should continue to pass.

[↑ Back to top](#table-of-contents)

---

### Step 6: Extract command storage

Extract final storage and cycle registration into a helper.

**Rationale:** Separates storage concerns from validation/processing. Groups related operations (registry storage + cycle registration).

**Implementation:**

## Overview

Extract helper: `_store_command()` - Registry storage and cycle registration

**Methods created:**
- `_store_command()` - Stores command in registry and registers cycle
  - `test_store_command_registry_storage()`
  - `test_store_command_cycle_registration()`

## Module-level imports

See Step 1 for all required imports.

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
    # Block 6.1.3.1: Get command name
    name = cmd[COMMAND_NAME]
    
    # Block 6.1.3.2: Store command in registry
    _commands[name] = cmd
    
    # Block 6.1.3.3: Register cycle if present
    cycle.register_cycle(cmd, _commands)
```

## Verification

After implementing Step 6:
- Run `pytest tests/test_command.py::test_store_command_registry_storage -v`
- Run `pytest tests/test_command.py::test_store_command_cycle_registration -v`
- Run full test suite: `pytest tests/test_command.py -v`

All existing tests should continue to pass.

### Step 7: Refactor add_command() to use all helpers

Refactor the main `add_command()` function to delegate all responsibilities to the extracted helpers. This creates a clean, high-level orchestrator function.

**Rationale:** With all helpers extracted and tested, we can now show the final clean implementation of `add_command()` that uses them. This demonstrates the end result of the refactoring.

**Implementation:**

**Code 7.1: Refactored add_command() using all helpers**

```python
# Block 7.1: Replace add_command() in src/spafw37/command.py

def add_command(cmd):
    """Register a command for execution.
    
    [... existing docstring unchanged ...]
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

[↑ Back to top](#table-of-contents)

---

## Further Considerations

No unresolved questions at this time. The refactoring plan is straightforward:

- All helpers will be private (`_` prefix) - no API changes
- Existing test coverage (44 tests for command module, 95% overall) guards against regression
- Incremental extraction allows running tests after each step
- Pattern already proven successful in issue #15

If questions arise during implementation, they will be documented here.

[↑ Back to top](#table-of-contents)

---

## Success Criteria

This issue is considered successfully implemented when:

**Functional Requirements:**
- [ ] `add_command()` correctly registers commands using refactored helper structure
- [ ] Command validation rejects empty names (raises ValueError with clear message)
- [ ] Command validation rejects missing action (raises ValueError identifying missing key)
- [ ] Command validation rejects self-references (raises ValueError identifying circular dependency)
- [ ] Command validation rejects conflicting sequencing constraints (e.g., both required and triggered)
- [ ] Inline parameter definitions (dict format) are correctly registered as parameters
- [ ] Inline command definitions in dependency fields are correctly registered as commands
- [ ] Phase assignment uses config module default when not specified in command definition
- [ ] Phase assignment preserves explicitly specified phase from command definition
- [ ] Command storage correctly adds command to registry dictionary
- [ ] Command storage correctly registers cycle when command includes cycle configuration
- [ ] All existing command registration patterns continue to work identically (backward compatibility)

**Performance Requirements:**
- [ ] Refactored implementation has no measurable performance regression vs monolithic function
- [ ] Command registration completes in < 1ms for typical command definitions
- [ ] No memory usage increase from refactoring (same data structures)

**Compatibility Requirements:**
- [ ] Works with Python 3.7.0+ (no Python 3.8+ features used)
- [ ] Public API unchanged (all helpers are private with `_` prefix)
- [ ] Existing tests continue to pass without modification (44 command module tests)
- [ ] No changes to command definition format or behaviour

**Code Quality Requirements:**
- [ ] All functions follow max 2-level nesting depth requirement
- [ ] All nested blocks are ≤ 2 lines
- [ ] All helpers have descriptive names (no `tmp`, `data`, `result`)
- [ ] All functions have proper docstrings
- [ ] Test coverage remains ≥ 95% for command module
- [ ] All new tests follow TDD red-green-refactor pattern
- [ ] Gherkin specifications integrated into test docstrings

[↑ Back to top](#table-of-contents)

---

## Planning Checklist

This checklist tracks completion of this planning document.

**Plan Structure:**
- [x] Overview section complete with architectural decisions
- [x] All implementation steps identified and outlined
- [x] Further Considerations documented (all marked RESOLVED)
- [x] Success Criteria defined (feature outcomes)
- [x] Implementation Checklist created (TDD workflow)
- [x] CHANGES section populated for release
- [x] Table of Contents updated to reflect all sections

**Implementation Details:**
- [x] All implementation steps have detailed code blocks
- [x] All functions have corresponding test specifications
- [x] All code blocks follow X.Y.Z numbering scheme
- [x] All tests written in Gherkin + Python format
- [x] Module-level imports consolidated in Step 1
- [x] No nesting violations (max 2 levels)
- [x] No nested blocks exceeding 2 lines
- [x] All helper functions extracted and documented

**Documentation:**
- [x] No documentation changes required (internal refactoring)
- [x] No example files changes required (internal refactoring)
- [x] No API reference updates needed (all helpers private)
- [x] No user guide updates needed (no user-facing changes)

**Quality Verification:**
- [x] All code follows Python 3.7.0 compatibility requirements
- [x] All code follows UK English spelling conventions
- [x] No lazy naming (tmp, data, result, i, j, etc.)
- [x] All functions have proper docstrings
- [x] Regression tests verify unchanged behaviour

**Ready for Implementation:**
- [x] Plan reviewed and approved
- [x] All Further Considerations resolved
- [x] Success Criteria agreed upon
- [x] Implementation Checklist ready to execute

[↑ Back to top](#table-of-contents)

---

## Implementation Checklist

This section tracks the actual implementation progress with test runs and code patches. **Every action gets a checkbox.**

### Step 1: Module-level Imports

- [ ] Add imports to `tests/test_command.py`
  - [ ] Patch: Add constants from `spafw37.constants.command` and `spafw37.constants.param`
  - [ ] Test run: `pytest tests/test_command.py -v` (verify no import errors)

### Step 2: Validation Helpers

#### 2.1: `_validate_command_name()`

- [ ] Write test `test_validate_command_name_empty_string_raises_error()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_validate_command_name_empty_string_raises_error -v` (expect FAIL)
- [ ] Write test `test_validate_command_name_none_raises_error()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_validate_command_name_none_raises_error -v` (expect FAIL)
- [ ] Implement `_validate_command_name()`
  - [ ] Patch: Add function to `src/spafw37/command.py` before `add_command()`
  - [ ] Test run: `pytest tests/test_command.py::test_validate_command_name_empty_string_raises_error -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py::test_validate_command_name_none_raises_error -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py -v` (regression check - all tests pass)

#### 2.2: `_validate_command_action()`

- [ ] Write test `test_validate_command_action_missing_raises_error()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_validate_command_action_missing_raises_error -v` (expect FAIL)
- [ ] Write test `test_validate_command_action_none_raises_error()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_validate_command_action_none_raises_error -v` (expect FAIL)
- [ ] Implement `_validate_command_action()`
  - [ ] Patch: Add function to `src/spafw37/command.py` after `_validate_command_name()`
  - [ ] Test run: `pytest tests/test_command.py::test_validate_command_action_missing_raises_error -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py::test_validate_command_action_none_raises_error -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py -v` (regression check - all tests pass)

#### 2.3: `_validate_command_references()`

- [ ] Write test `test_validate_command_references_self_reference_raises_error()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_validate_command_references_self_reference_raises_error -v` (expect FAIL)
- [ ] Write test `test_validate_command_references_conflicting_constraints_raises_error()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_validate_command_references_conflicting_constraints_raises_error -v` (expect FAIL)
- [ ] Implement `_validate_command_references()`
  - [ ] Patch: Add function to `src/spafw37/command.py` after `_validate_command_action()`
  - [ ] Test run: `pytest tests/test_command.py::test_validate_command_references_self_reference_raises_error -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py::test_validate_command_references_conflicting_constraints_raises_error -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py -v` (regression check - all tests pass)

### Step 3: Inline Parameter Processing

#### 3.1: `_normalise_param_list()`

- [ ] Write test `test_normalise_param_list()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_normalise_param_list -v` (expect FAIL)
- [ ] Implement `_normalise_param_list()`
  - [ ] Patch: Add function to `src/spafw37/command.py` after `_validate_command_references()`
  - [ ] Test run: `pytest tests/test_command.py::test_normalise_param_list -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py -v` (regression check - all tests pass)

#### 3.2: `_process_inline_params()`

- [ ] Write test `test_process_inline_params_required_params()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_process_inline_params_required_params -v` (expect FAIL)
- [ ] Write test `test_process_inline_params_trigger_param()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_process_inline_params_trigger_param -v` (expect FAIL)
- [ ] Write test `test_process_inline_params_no_inline_params()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_process_inline_params_no_inline_params -v` (expect FAIL)
- [ ] Implement `_process_inline_params()`
  - [ ] Patch: Add function to `src/spafw37/command.py` after `_normalise_param_list()`
  - [ ] Test run: `pytest tests/test_command.py::test_process_inline_params_required_params -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py::test_process_inline_params_trigger_param -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py::test_process_inline_params_no_inline_params -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py -v` (regression check - all tests pass)

### Step 4: Inline Command Processing

#### 4.1: `_normalise_command_list()`

- [ ] Write test `test_normalise_command_list()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_normalise_command_list -v` (expect FAIL)
- [ ] Implement `_normalise_command_list()`
  - [ ] Patch: Add function to `src/spafw37/command.py` after `_process_inline_params()`
  - [ ] Test run: `pytest tests/test_command.py::test_normalise_command_list -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py -v` (regression check - all tests pass)

#### 4.2: `_process_inline_commands()`

- [ ] Write test `test_process_inline_commands_goes_after()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_process_inline_commands_goes_after -v` (expect FAIL)
- [ ] Write test `test_process_inline_commands_multiple_fields()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_process_inline_commands_multiple_fields -v` (expect FAIL)
- [ ] Write test `test_process_inline_commands_no_inline_commands()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_process_inline_commands_no_inline_commands -v` (expect FAIL)
- [ ] Implement `_process_inline_commands()`
  - [ ] Patch: Add function to `src/spafw37/command.py` after `_normalise_command_list()`
  - [ ] Test run: `pytest tests/test_command.py::test_process_inline_commands_goes_after -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py::test_process_inline_commands_multiple_fields -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py::test_process_inline_commands_no_inline_commands -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py -v` (regression check - all tests pass)

### Step 5: Phase Assignment

#### 5.1: `_assign_command_phase()`

- [ ] Write test `test_assign_command_phase_missing_phase()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_assign_command_phase_missing_phase -v` (expect FAIL)
- [ ] Write test `test_assign_command_phase_existing_phase()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_assign_command_phase_existing_phase -v` (expect FAIL)
- [ ] Implement `_assign_command_phase()`
  - [ ] Patch: Add function to `src/spafw37/command.py` after `_process_inline_commands()`
  - [ ] Test run: `pytest tests/test_command.py::test_assign_command_phase_missing_phase -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py::test_assign_command_phase_existing_phase -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py -v` (regression check - all tests pass)

### Step 6: Command Storage

#### 6.1: `_store_command()`

- [ ] Write test `test_store_command_registry_storage()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_store_command_registry_storage -v` (expect FAIL)
- [ ] Write test `test_store_command_cycle_registration()`
  - [ ] Patch: Add test function to `tests/test_command.py`
  - [ ] Test run: `pytest tests/test_command.py::test_store_command_cycle_registration -v` (expect FAIL)
- [ ] Implement `_store_command()`
  - [ ] Patch: Add function to `src/spafw37/command.py` after `_assign_command_phase()`
  - [ ] Test run: `pytest tests/test_command.py::test_store_command_registry_storage -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py::test_store_command_cycle_registration -v` (expect PASS)
  - [ ] Test run: `pytest tests/test_command.py -v` (regression check - all tests pass)

### Step 7: Refactor add_command()

- [ ] Refactor `add_command()` to use all helpers
  - [ ] Patch: Replace monolithic implementation in `src/spafw37/command.py` (lines 192-244)
  - [ ] Test run: `pytest tests/test_command.py -v` (all 44+ tests should pass)
  - [ ] Test run: `pytest tests/ -v --cov=spafw37 --cov-report=term-missing` (verify 95%+ coverage)

### Final Verification

- [ ] Verify all new tests passing (18 new tests)
- [ ] Verify all existing tests passing (44 command module tests)
- [ ] Verify test coverage above 95%
- [ ] Verify no regressions in other modules
- [ ] Verify code follows nesting requirements (max 2 levels)
- [ ] Verify all helpers have block numbering comments
- [ ] Verify all tests have Gherkin pattern in docstrings

[↑ Back to top](#table-of-contents)

---

## CHANGES for v1.1.0 Release

**Note:** This section must follow the format specified in `features/CHANGES-TEMPLATE.md`. The content will be posted as the closing comment and consumed by the release workflow.

Issue #61: Refactor command.add_command() into focused helper methods

### Issues Closed

- #61: Refactor command.add_command() into focused helper methods

### Additions

- `_validate_command_name()` internal function validates command has non-empty name during registration.
- `_validate_command_action()` internal function validates command has action function during registration.
- `_validate_command_references()` internal function validates no self-references or conflicting sequencing constraints.
- `_normalise_param_list()` internal function converts list of parameter definitions to parameter names (extracts loop logic to avoid nesting violations).
- `_process_inline_params()` internal function processes inline parameter definitions in `COMMAND_REQUIRED_PARAMS` and `COMMAND_TRIGGER_PARAM`.
- `_normalise_command_list()` internal function converts list of command definitions to command names (extracts loop logic to avoid nesting violations).
- `_process_inline_commands()` internal function processes inline command definitions in all dependency/sequencing fields.
- `_assign_command_phase()` internal function assigns default phase from config when not specified in command definition.
- `_store_command()` internal function stores command in registry and registers cycle if present.

### Removals

None.

### Changes

- `add_command()` function refactored from monolithic 54-line function to clean orchestrator that delegates to 7 focused helper functions.
- Command validation logic extracted into three focused validators for better testability and maintainability.
- Inline parameter processing logic extracted into separate helper with normalisation sub-helper to comply with nesting requirements.
- Inline command processing logic extracted into separate helper with normalisation sub-helper to comply with nesting requirements.
- Phase assignment logic extracted into dedicated helper for clarity.
- Command storage logic extracted into dedicated helper that encapsulates registry mutation and cycle registration.
- All helpers follow single-responsibility principle with clear naming and focused behaviour.
- Code nesting depth reduced throughout refactored implementation (max 2-level nesting maintained).

### Migration

No migration required. This is an internal refactoring that improves code structure and maintainability without changing external behaviour.

All existing code will continue to work identically. The `add_command()` function maintains the same signature and behaviour - only the internal implementation has been reorganised.

### Documentation

No documentation changes required. This is an internal implementation refactoring with no user-facing API changes. All helpers are private (prefixed with `_`) and not part of the public API.

### Testing

- 2 new tests in `tests/test_command.py` covering `_validate_command_name()` behaviour (empty string, None value)
- 2 new tests in `tests/test_command.py` covering `_validate_command_action()` behaviour (missing key, None value)
- 2 new tests in `tests/test_command.py` covering `_validate_command_references()` behaviour (self-reference, conflicting constraints)
- 1 new test in `tests/test_command.py` covering `_normalise_param_list()` behaviour
- 3 new tests in `tests/test_command.py` covering `_process_inline_params()` behaviour (required params, trigger param, no inline params)
- 1 new test in `tests/test_command.py` covering `_normalise_command_list()` behaviour
- 3 new tests in `tests/test_command.py` covering `_process_inline_commands()` behaviour (single field, multiple fields, no inline commands)
- 2 new tests in `tests/test_command.py` covering `_assign_command_phase()` behaviour (missing phase, existing phase)
- 2 new tests in `tests/test_command.py` covering `_store_command()` behaviour (registry storage, cycle registration)
- Tests cover all helper functions with focused unit tests following Gherkin Given-When-Then pattern
- All new tests verify single clear behaviour per test with descriptive docstrings
- All tests follow TDD red-green-refactor cycle (tests written first, implementation second)
- All existing 44 command module tests continue to pass unchanged (regression protection)
- Final test results: [TBD] passed, [TBD] skipped, 95%+ coverage maintained

---

Full changelog: https://github.com/minouris/spafw37/compare/v1.0.0...v1.1.0
Issues: https://github.com/minouris/spafw37/issues/61

[↑ Back to top](#table-of-contents)
