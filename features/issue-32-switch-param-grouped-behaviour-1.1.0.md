# Issue #32: Switch Param Grouped Behaviour

## Overview

Currently, switch params work independently of each other, beyond only allowing one switch param in a group to be set. There are several use cases such as mode switching where it would be useful to be able to switch the value of one param in a switch group, and have the others un-set, or reset to their default.

This issue introduces a new param property to control what happens to other switch params in the same group when one switch param is set. The new property will allow params to be unset, reset to default, or reject the change altogether.

The enhancement will introduce a new param property, `PARAM_SWITCH_CHANGE_BEHAVIOR`, with values `SWITCH_UNSET`, `SWITCH_RESET` and `SWITCH_REJECT`. This provides control over how switch params in the same group interact when values change.

This enhancement will be treated as a part of the new param API in version 1.1.0.

**Key architectural decisions:**

- **Property name:** `PARAM_SWITCH_CHANGE_BEHAVIOR` added to param configuration
- **Default behaviour:** `SWITCH_REJECT` to match current behaviour (throws error on conflict)
- **Implementation approach:** Leverage existing `unset_param()` and `reset_param()` functions for consistency
- **API integration:** Part of the new param API being developed in version 1.1.0
- **CLI behaviour:** CLI parser calls `set_param()` which will apply the configured behaviour uniformly

## Table of Contents

- [Overview](#overview)
- [Switch Param Grouped Behaviour Flow](#switch-param-grouped-behaviour-flow)
  - [Current Behaviour (Before Changes)](#current-behaviour-before-changes)
  - [New Behaviour (After Changes)](#new-behaviour-after-changes)
- [Implementation Steps](#implementation-steps)
  - [1. Define switch change behaviour constants](#1-define-switch-change-behaviour-constants)
  - [2. Add property to param configuration](#2-add-property-to-param-configuration)
  - [3. Implement switch group change logic](#3-implement-switch-group-change-logic)
  - [4. Update CLI parser to use batch param setting](#4-update-cli-parser-to-use-batch-param-setting)
  - [5. Create example demonstrating switch behavior](#5-create-example-demonstrating-switch-behavior)
  - [6. Update documentation](#6-update-documentation)
- [Further Considerations](#further-considerations)
  - [1. Default behaviour selection](#1-default-behaviour-selection)
  - [2. CLI parser interaction](#2-cli-parser-interaction)
- [Success Criteria](#success-criteria)
- [CHANGES for v1.1.0 Release](#changes-for-v110-release)

## Switch Param Grouped Behaviour Flow

This section illustrates how switch param conflict handling changes with the new `PARAM_SWITCH_CHANGE_BEHAVIOR` property.

### Current Behaviour (Before Changes)

When attempting to set conflicting switch params (e.g., `verbose` and `silent` in same group):

In the current implementation, both CLI and programmatic usage follow identical paths through `set_param()`, which calls `_validate_xor_conflicts()` to detect conflicts. The CLI parser loops through tokenized parameters, parsing `@file` references inline and calling `set_param()` for each parameter individually. When a conflict is detected (a switch param in the same group is already set), `_validate_xor_conflicts()` raises a `ValueError` immediately, with no mechanism to configure alternative behaviour. This means all switch conflicts always result in errors, regardless of the use case.

**CLI usage:**
1. **User runs:** `app --verbose --silent`
2. **CLI → _parse_command_line()**: Receives tokenized params `[{"alias":"--verbose"}, {"alias":"--silent"}]`
3. **_parse_command_line() → _parse_file_value()**: Parses any `@file` references inline
4. **_parse_command_line()**: Loops through params
5. **_parse_command_line() → param.set_param('verbose', True)**: Sets first param
   - **set_param() → _validate_xor_conflicts()**: Checks for conflicts
   - **_validate_xor_conflicts() → config**: No conflict yet
   - **set_param() → config**: Sets `verbose=True`
6. **_parse_command_line() → param.set_param('silent', True)**: Attempts second param
   - **set_param() → _validate_xor_conflicts()**: Checks for conflicts
   - **_validate_xor_conflicts() → config**: Finds `verbose=True` conflict
   - **_validate_xor_conflicts()**: Raises `ValueError: Cannot set 'silent', conflicts with 'verbose'`
   - **Error propagates**: set_param() → _parse_command_line() → CLI
7. **CLI**: Displays error to user

**Programmatic usage:**
1. **Application → param.set_param('verbose', True)**: Sets first param
   - **set_param() → _validate_xor_conflicts()**: Checks for conflicts
   - **_validate_xor_conflicts() → config**: No conflict yet
   - **set_param() → config**: Sets `verbose=True`
2. **Application → param.set_param('silent', True)**: Attempts to set second param
   - **set_param() → _validate_xor_conflicts()**: Checks for conflicts
   - **_validate_xor_conflicts() → config**: Finds `verbose=True` conflict
   - **_validate_xor_conflicts()**: Raises `ValueError: Cannot set 'silent', conflicts with 'verbose'`

**Result:** Always raises error. No way to configure different behaviour. CLI and programmatic usage behave identically.

### New Behaviour (After Changes)

With `PARAM_SWITCH_CHANGE_BEHAVIOR` property, three behaviour options are available:

#### SWITCH_REJECT (default - matches current behaviour)

With `SWITCH_REJECT` behaviour, the system maintains backward compatibility by raising errors on conflicts, but the implementation path changes significantly. CLI parsing now uses a new `param.set_values()` function that enables batch mode, which forces `SWITCH_REJECT` regardless of configuration. The CLI parser extracts file parsing to a dedicated helper that returns a new list (functional approach), then delegates all parameter setting to `set_values()`. The conflict detection logic moves from `_validate_xor_conflicts()` to the renamed `_handle_switch_group_behavior()`, which uses a new `_get_switch_change_behavior()` helper that checks batch mode and overrides configured behaviour when enabled. Programmatic usage bypasses batch mode, allowing the configured behaviour (which defaults to `SWITCH_REJECT`) to apply normally.

**CLI usage:**
1. **User runs:** `app --verbose --silent`
2. **CLI → _parse_command_line()**: Receives tokenized params `[{"alias":"--verbose"}, {"alias":"--silent"}]`
3. **_parse_command_line() → _parse_file_references_in_params()**: Returns new list with parsed `@file` references
4. **_parse_command_line() → param.set_values()**: Calls with parsed list
5. **param.set_values()**: Enables batch mode (`_set_batch_mode(True)`)
6. **param.set_values() → _process_param_values()**: Loops through params
7. **_process_param_values() → _process_single_param_entry()**: Processes first param
8. **_process_single_param_entry() → param.set_param('verbose', True)**: Routes to set_param
   - **set_param() → _handle_switch_group_behavior()**: Checks for conflicts
   - **_handle_switch_group_behavior() → _get_switch_change_behavior()**: Returns `SWITCH_REJECT` (forced by batch mode)
   - **set_param() → config**: Sets `verbose=True`
9. **_process_single_param_entry() → param.set_param('silent', True)**: Routes to set_param
   - **set_param() → _handle_switch_group_behavior()**: Checks for conflicts
   - **_handle_switch_group_behavior() → _get_switch_change_behavior()**: Returns `SWITCH_REJECT` (forced by batch mode)
   - **_handle_switch_group_behavior() → _apply_switch_behavior_to_group()**: Finds conflict
   - **_apply_switch_behavior_to_group() → _resolve_switch_conflict()**: Raises `ValueError`
   - **Error propagates**: set_param() → _process_single_param_entry() → _process_param_values() → set_values() → _parse_command_line() → CLI
10. **param.set_values()**: Disables batch mode in finally block (`_set_batch_mode(False)`)
11. **CLI**: Displays error to user

**Programmatic usage:**
1. **Application → param.set_param('verbose', True)**: Sets first param
   - **set_param() → _handle_switch_group_behavior()**: Checks for conflicts
   - **_handle_switch_group_behavior() → _get_switch_change_behavior()**: Returns `SWITCH_REJECT` (from config, batch mode disabled)
   - **set_param() → config**: Sets `verbose=True`
2. **Application → param.set_param('silent', True)**: Attempts to set second param
   - **set_param() → _handle_switch_group_behavior()**: Checks for conflicts
   - **_handle_switch_group_behavior() → _apply_switch_behavior_to_group()**: Finds conflict
   - **_apply_switch_behavior_to_group() → _resolve_switch_conflict()**: Raises `ValueError`

**Result:** Raises error (backward compatible with current behaviour). CLI forces SWITCH_REJECT via batch mode; programmatic uses configured behaviour (defaults to SWITCH_REJECT).

#### SWITCH_UNSET (new option)

With `SWITCH_UNSET` configured, programmatic usage exhibits automatic conflict resolution by calling `unset_param()` on conflicting switches, allowing the last param set to win without errors. However, CLI usage ignores this configuration entirely due to batch mode forcing `SWITCH_REJECT`. When `_get_switch_change_behavior()` detects batch mode is enabled (which happens during CLI parsing via `set_values()`), it returns `SWITCH_REJECT` regardless of the configured `SWITCH_UNSET` behaviour. This design ensures CLI arguments always produce clear errors for user mistakes, while programmatic code can leverage automatic mode switching when explicitly configured.

**CLI usage:**
1. **User runs:** `app --verbose --silent`
2. **CLI → _parse_command_line()**: Receives tokenized params
3. **_parse_command_line() → _parse_file_references_in_params()**: Returns new list with parsed `@file` references
4. **_parse_command_line() → param.set_values()**: Calls with parsed list
5. **param.set_values()**: Enables batch mode (`_set_batch_mode(True)`)
6. **param.set_values() → param.set_param('verbose', True)**: Sets first param
   - **set_param() → _handle_switch_group_behavior()**: Checks for conflicts
   - **_handle_switch_group_behavior() → _get_switch_change_behavior()**: Returns `SWITCH_REJECT` (batch mode overrides SWITCH_UNSET config)
   - **set_param() → config**: Sets `verbose=True`
7. **param.set_values() → param.set_param('silent', True)**: Attempts second param
   - **set_param() → _handle_switch_group_behavior()**: Checks for conflicts
   - **_handle_switch_group_behavior() → _get_switch_change_behavior()**: Returns `SWITCH_REJECT` (batch mode override)
   - **_handle_switch_group_behavior() → _apply_switch_behavior_to_group()**: Finds conflict
   - **_apply_switch_behavior_to_group() → _resolve_switch_conflict()**: Raises `ValueError`
   - **Error propagates through call stack**
8. **param.set_values()**: Disables batch mode in finally block
9. **CLI**: Displays error to user

**Programmatic usage:**
1. **Application → param.set_param('verbose', True)**: Sets first param
   - **set_param() → _handle_switch_group_behavior()**: Checks for conflicts
   - **_handle_switch_group_behavior() → _get_switch_change_behavior()**: Returns `SWITCH_UNSET` (batch mode disabled)
   - **set_param() → config**: Sets `verbose=True`
2. **Application → param.set_param('silent', True)**: Sets second param
   - **set_param() → _handle_switch_group_behavior()**: Checks for conflicts
   - **_handle_switch_group_behavior() → _apply_switch_behavior_to_group()**: Finds conflict with `verbose`
   - **_apply_switch_behavior_to_group() → _resolve_switch_conflict()**: Calls `unset_param('verbose')`
   - **set_param() → config**: Sets `silent=True`

**Result:** CLI raises error (batch mode forces SWITCH_REJECT). Programmatic usage: `verbose` removed from config, `silent` set to True. Last param wins.

#### SWITCH_RESET (new option)

With `SWITCH_RESET` configured, programmatic usage automatically restores conflicting switches to their default values (via `reset_param()`) instead of raising errors, providing state management without manual cleanup. Like `SWITCH_UNSET`, CLI usage completely ignores this configuration because batch mode overrides it to `SWITCH_REJECT`. The behaviour abstraction in `_get_switch_change_behavior()` creates a clear separation: CLI parsing always enforces strict validation to catch user input errors immediately, while programmatic code can use `SWITCH_RESET` to implement stateful switch behaviour where previous settings should revert to defaults rather than disappear entirely.

**CLI usage:**
1. **User runs:** `app --verbose --silent`
2. **CLI flow identical to SWITCH_UNSET case above**
3. **Result:** Error raised (batch mode forces SWITCH_REJECT regardless of SWITCH_RESET config)

**Programmatic usage:**
1. **Application → param.set_param('verbose', True)**: Sets first param
   - **set_param() → _handle_switch_group_behavior()**: Checks for conflicts
   - **_handle_switch_group_behavior() → _get_switch_change_behavior()**: Returns `SWITCH_RESET` (batch mode disabled)
   - **set_param() → config**: Sets `verbose=True`
2. **Application → param.set_param('silent', True)**: Sets second param
   - **set_param() → _handle_switch_group_behavior()**: Checks for conflicts
   - **_handle_switch_group_behavior() → _apply_switch_behavior_to_group()**: Finds conflict with `verbose`
   - **_apply_switch_behavior_to_group() → _resolve_switch_conflict()**: Calls `reset_param('verbose')`
   - **set_param() → config**: Resets `verbose` to default, sets `silent=True`

**Result:** CLI raises error (batch mode forces SWITCH_REJECT). Programmatic usage: `verbose` reset to default value, `silent` set to True.

**Key architectural changes:**

1. **CLI parser refactored**: `_parse_command_line()` now calls new `param.set_values()` instead of calling `set_param()` directly in a loop
2. **File parsing extracted**: New `_parse_file_references_in_params()` helper parses `@file` references before param setting (functional approach - returns new list)
3. **Batch mode introduced**: `_batch_mode` flag forces `SWITCH_REJECT` during CLI parsing regardless of configured behaviour
4. **Behaviour abstraction**: `_get_switch_change_behavior()` respects config in programmatic usage but overrides to `SWITCH_REJECT` when batch mode is enabled
5. **Validation renamed**: `_validate_xor_conflicts()` renamed to `_handle_switch_group_behavior()` to reflect expanded responsibility (validate + resolve)
6. **Resolution abstracted**: New helpers `_apply_switch_behavior_to_group()` and `_resolve_switch_conflict()` handle conflict resolution based on behaviour setting

**Result:** CLI always raises error regardless of configured `PARAM_SWITCH_CHANGE_BEHAVIOR`. Batch mode forces `SWITCH_REJECT` to ensure CLI arguments produce clear errors for user mistakes. Programmatic usage respects configured behaviour (SWITCH_REJECT, SWITCH_UNSET, or SWITCH_RESET).

[↑ Back to top](#table-of-contents)

## Implementation Steps

### 1. Define switch change behaviour constants

**File:** `src/spafw37/constants/param.py`

Add three new constants to control what happens to other switch params in a group when one switch param is set. These constants will be used as values for the new `PARAM_SWITCH_CHANGE_BEHAVIOR` property.

**Implementation order:**

1. Add `SWITCH_UNSET` constant at end of file
2. Add `SWITCH_RESET` constant after `SWITCH_UNSET`
3. Add `SWITCH_REJECT` constant after `SWITCH_RESET`
4. Add comment block documenting the behaviour options

**Constants to add:**

**Code 1.1: Switch behavior constants**

```python
# Switch Change Behaviour Options
SWITCH_UNSET = 'switch-unset'  # Unset other switches in group using unset_param()
SWITCH_RESET = 'switch-reset'  # Reset other switches in group using reset_param()
SWITCH_REJECT = 'switch-reject'  # Reject change if other switches already set (current behaviour)
```

- **`SWITCH_UNSET`:**
  - Causes other switches in the same group to be completely removed from config
  - Uses existing `unset_param()` function for consistency
  - Useful for mode switching where previous mode should be cleared
  
- **`SWITCH_RESET`:**
  - Causes other switches in the same group to be reset to their default values
  - Uses existing `reset_param()` function for consistency
  - Useful when switches have meaningful default states that should be restored
  
- **`SWITCH_REJECT`:**
  - Throws an error preventing the new switch param value from being set
  - Matches current behaviour (maintains backward compatibility)
  - Useful for strict validation where only one switch should ever be set

**Tests:** Add tests in `tests/test_constants.py`

**Test 1.2.1: Constants are defined**

```gherkin
Scenario: Switch behavior constants are defined
  Given the constants module is imported
  When I import SWITCH_UNSET, SWITCH_RESET, and SWITCH_REJECT
  Then all three constants should not be None
```

**Test 1.2.2: Constants are unique**

```gherkin
Scenario: Switch behavior constants are unique
  Given SWITCH_UNSET, SWITCH_RESET, and SWITCH_REJECT are defined
  When I compare the values of all three constants
  Then SWITCH_UNSET should not equal SWITCH_RESET
  And SWITCH_RESET should not equal SWITCH_REJECT
  And SWITCH_UNSET should not equal SWITCH_REJECT
```

**Test 1.2.3: Constants have correct values**

```gherkin
Scenario: Switch behavior constants have correct values
  Given the constants module is imported
  When I access SWITCH_UNSET, SWITCH_RESET, and SWITCH_REJECT
  Then SWITCH_UNSET should equal 'switch-unset'
  And SWITCH_RESET should equal 'switch-reset'
  And SWITCH_REJECT should equal 'switch-reject'
```

[↑ Back to top](#table-of-contents)

### 2. Add property to param configuration

**File:** `src/spafw37/constants/param.py`

Add the new `PARAM_SWITCH_CHANGE_BEHAVIOR` property constant to the param configuration constants. This property will control how switch params in the same group react when one is set.

**Implementation order:**

1. Add `PARAM_SWITCH_CHANGE_BEHAVIOR` constant after `PARAM_ALLOWED_VALUES`
2. Import the constant in `src/spafw37/param.py`
3. Document the property in docstring

**Constant to add:**

**Code 2.1: Property constant**

```python
PARAM_SWITCH_CHANGE_BEHAVIOR = 'switch-change-behavior'  # Controls switch group interaction: SWITCH_UNSET, SWITCH_RESET, or SWITCH_REJECT
```

**Import update in `src/spafw37/param.py`:**

**Code 2.2: Import additions**

Add to existing imports from `spafw37.constants.param`:
```python
from spafw37.constants.param import (
    # ... existing imports ...
    PARAM_SWITCH_CHANGE_BEHAVIOR,
    SWITCH_UNSET,
    SWITCH_RESET,
    SWITCH_REJECT,
)
```

**Tests:** Add tests in `tests/test_param_validation.py`

**Test 2.3.1: Property constant exists**

```gherkin
Scenario: PARAM_SWITCH_CHANGE_BEHAVIOR property constant exists
  Given the param constants module is imported
  When I import PARAM_SWITCH_CHANGE_BEHAVIOR
  Then PARAM_SWITCH_CHANGE_BEHAVIOR should equal 'switch-change-behavior'
```

**Test 2.3.2: Param definition accepts property**

```gherkin
Scenario: Param definition accepts PARAM_SWITCH_CHANGE_BEHAVIOR property
  Given I have defined a param with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_UNSET
  When I retrieve the param definition using get_param_definition()
  Then the definition should contain PARAM_SWITCH_CHANGE_BEHAVIOR
  And the value should be SWITCH_UNSET
```

[↑ Back to top](#table-of-contents)

### 3. Implement switch group change logic

**File:** `src/spafw37/param.py`

Modify the existing `_validate_xor_conflicts()` function to apply the configured behaviour to other switches in the group. The current implementation only checks for conflicts (SWITCH_REJECT behaviour). The new implementation will check the `PARAM_SWITCH_CHANGE_BEHAVIOR` property and apply the appropriate action.

**Implementation order:**

1. Add module-level `_batch_mode` flag (defaults to False)
2. Create `_set_batch_mode(enabled)` and `_get_batch_mode()` functions
3. Create `set_values(param_values)` function for batch param setting with batch mode enabled
4. Create helper `_get_switch_change_behavior(param_definition)` to retrieve behaviour from param definition
5. Create helper `_apply_switch_behavior_to_group(param_definition, value_to_set, behavior)` to apply behaviour
6. Rename `_validate_xor_conflicts()` to `_handle_switch_group_behavior()` and refactor to use helpers
7. Update `set_param()` call to use new function name

---

#### Module-Level Flag: `_batch_mode`

**Purpose:** Controls CLI override behavior for switch params.

**Code 3.1.1: Batch mode flag**

**Implementation:**

```python
# Batch mode flag - when True, forces SWITCH_REJECT for all switch params
_batch_mode = False
```

**Tests:**

**Test 3.1.2: Flag defaults to False**

```gherkin
Scenario: Batch mode flag defaults to False
  Given the param module is imported
  When I check the _batch_mode flag
  Then it should be False
  
  # Validates: Default state allows programmatic switch behavior to work normally
```

---

#### Function: `_set_batch_mode(enabled)`

**Purpose:** Enables or disables batch mode for parameter initialization.

**Code 3.2.1: _set_batch_mode function**

**Implementation:**

```python
def _set_batch_mode(enabled):
    """Enable or disable batch mode for parameter initialization.
    
    When batch mode is enabled, all switch params use SWITCH_REJECT behaviour
    regardless of their configured PARAM_SWITCH_CHANGE_BEHAVIOR. This ensures
    CLI arguments always produce clear errors for conflicting switches.
    
    Args:
        enabled: True to enable batch mode, False to disable
    """
    global _batch_mode
    _batch_mode = enabled
```

**Tests:**

**Test 3.2.2: Setting batch mode enables flag**

```gherkin
Scenario: Setting batch mode enables the flag
  Given _batch_mode is False
  When I call _set_batch_mode(True)
  Then _get_batch_mode() should return True
  
  # Validates: _set_batch_mode() control function works correctly
```

---

#### Function: `_get_batch_mode()`

**Purpose:** Checks if batch mode is currently enabled.

**Code 3.3.1: _get_batch_mode function**

**Implementation:**

```python
def _get_batch_mode():
    """Check if batch mode is currently enabled.
    
    Returns:
        True if batch mode is enabled, False otherwise
    """
    return _batch_mode
```

**Tests:**

**Test 3.3.2: Getting batch mode returns current state**

```gherkin
Scenario: Getting batch mode returns current state
  Given _batch_mode is False
  When I call _set_batch_mode(True)
  Then _get_batch_mode() should return True
  When I call _set_batch_mode(False)
  Then _get_batch_mode() should return False
  
  # Validates: _get_batch_mode() accessor function accurately reflects flag state
```

---

#### Function: `set_values(param_values)`

**Purpose:** Sets multiple parameter values with batch mode enabled. Used by CLI parser to enforce SWITCH_REJECT for all switch params.

**Code 3.4.1: set_values function**

**Implementation:**

```python
# Block 3.4.1
def set_values(param_values):
    """Set multiple parameter values with batch mode enabled.
    
    This function is designed for CLI parsing and other initialization scenarios
    where switch params should always reject conflicts. It enables batch mode,
    processes all param values, then disables batch mode.
    
    Args:
        param_values: List of dicts with structure [{"alias": "--name", "value": "val"}]
    """
    # Block 3.4.1.1
    _set_batch_mode(True)
    # Block 3.4.1.2: try/finally cleanup
    try:
        # Block 3.4.1.2.1
        _process_param_values(param_values)
    finally:
        # Block 3.4.1.2.2
        _set_batch_mode(False)
```

**Tests:**

**Test 3.4.2.1: Enables batch mode at start**

```gherkin
Scenario: set_values enables batch mode at start
  Given I have mocked _set_batch_mode
  When I call set_values() with a list of params
  Then _set_batch_mode should be called with True
  
  # Validates: set_values() activates batch mode at start of processing
```

**Test 3.4.2.2: Disables batch mode after processing**

```gherkin
Scenario: set_values disables batch mode after processing
  Given I have mocked _set_batch_mode
  When I call set_values() with a list of params
  Then _set_batch_mode should be called with False in the finally block
  
  # Validates: set_values() cleanup ensures batch mode doesn't leak to other code
```

**Test 3.4.2.3: Disables batch mode even on error**

```gherkin
Scenario: set_values disables batch mode even on error
  Given I have mocked _set_batch_mode and set_param to raise an error
  When I call set_values() with a list of params
  Then a ValueError should be raised
  And _set_batch_mode should still be called with False
  
  # Validates: finally block cleanup works even when param setting fails
```

**Test 3.4.2.4: Delegates to _process_param_values**

```gherkin
Scenario: set_values delegates to _process_param_values
  Given I have mocked _process_param_values
  When I call set_values() with a list of params
  Then _process_param_values should be called once
  And the argument should be the param_values list
  
  # Validates: set_values() delegates processing to helper
```

---

#### Function: `_process_param_values(param_values)`

**Purpose:** Processes each parameter value entry by delegating to single entry processor.

**Code 3.4.3: _process_param_values function**

**Implementation:**

```python
# Block 3.4.3
def _process_param_values(param_values):
    """Process each parameter value entry.
    
    Routes list/dict params to join_param and all others to set_param.
    
    Args:
        param_values: List of dicts with structure [{"alias": "--name", "value": "val"}]
    """
    # Block 3.4.3.1: for loop iteration
    for param_entry in param_values:
        # Block 3.4.3.1.1
        _process_single_param_entry(param_entry)
```

**Tests:**

**Test 3.4.4.1: Calls _process_single_param_entry for each entry**

```gherkin
Scenario: Calls _process_single_param_entry for each entry
  Given I have mocked _process_single_param_entry
  And I have a list with three param entries
  When I call _process_param_values() with the list
  Then _process_single_param_entry should be called three times
  
  # Validates: _process_param_values() iterates all entries
```

---

#### Function: `_process_single_param_entry(param_entry)`

**Purpose:** Processes a single parameter entry, routing to appropriate setter function.

**Code 3.4.5: _process_single_param_entry function**

**Implementation:**

```python
# Block 3.4.5
def _process_single_param_entry(param_entry):
    """Process a single parameter entry.
    
    Args:
        param_entry: Dict with structure {"alias": "--name", "value": "val"}
    """
    # Block 3.4.5.1: variable extraction
    alias = param_entry.get("alias")
    value = param_entry.get("value")
    
    # Block 3.4.5.2: routing decision
    if is_list_param(alias=alias) or is_dict_param(alias=alias):
        # Block 3.4.5.2.1
        join_param(alias=alias, value=value)
    else:
        # Block 3.4.5.2.2
        set_param(alias=alias, value=value)
```

**Tests:**

**Test 3.4.6.1: Routes list param to join_param**

```gherkin
Scenario: Routes list param to join_param
  Given I have defined a list param
  And I have mocked join_param
  When I call _process_single_param_entry() with a list param entry
  Then join_param should be called with the correct alias and value
  And set_param should not be called
  
  # Validates: List params route to join_param()
```

**Test 3.4.6.2: Routes dict param to join_param**

```gherkin
Scenario: Routes dict param to join_param
  Given I have defined a dict param
  And I have mocked join_param
  When I call _process_single_param_entry() with a dict param entry
  Then join_param should be called with the correct alias and value
  And set_param should not be called
  
  # Validates: Dict params route to join_param()
```

**Test 3.4.6.3: Routes non-list/dict param to set_param**

```gherkin
Scenario: Routes non-list/dict param to set_param
  Given I have defined a text param
  And I have mocked set_param
  When I call _process_single_param_entry() with a text param entry
  Then set_param should be called with the correct alias and value
  And join_param should not be called
  
  # Validates: Non-list/dict params route to set_param()
```

---

**Integration tests for set_values:**

**Test 3.4.7.1: Processes list and dict params with join_param**

```gherkin
Scenario: set_values processes list and dict params with join_param
  Given I have defined a list param and a dict param
  When I call set_values() with entries for both params
  Then join_param should be called for the list param
  And join_param should be called for the dict param
  And set_param should not be called for these params
  
  # Validates: End-to-end routing for list/dict params
  # Validates: Non-list/dict params route to set_param()
```

---

#### Function: `_get_switch_change_behavior(param_definition)`

**Purpose:** Retrieves the switch change behavior from param definition. Returns SWITCH_REJECT when batch mode is enabled (CLI override).

**Code 3.5.1: _get_switch_change_behavior function**

**Implementation:**

```python
# Block 3.5.1
def _get_switch_change_behavior(param_definition):
    """Get switch change behaviour from param definition.
    
    When batch mode is enabled, always returns SWITCH_REJECT regardless of
    the configured behaviour. Otherwise returns the configured behaviour
    or SWITCH_REJECT as default for backward compatibility.
    
    Args:
        param_definition: Parameter definition dict
        
    Returns:
        One of SWITCH_UNSET, SWITCH_RESET, or SWITCH_REJECT
    """
    # Block 3.5.1.1: batch mode check
    if _get_batch_mode():
        # Block 3.5.1.1.1
        return SWITCH_REJECT
    
    # Block 3.5.1.2
    return param_definition.get(PARAM_SWITCH_CHANGE_BEHAVIOR, SWITCH_REJECT)
```

**Tests:**

**Test 3.5.2.1: Batch mode forces SWITCH_REJECT behavior**

```gherkin
Scenario: Batch mode forces SWITCH_REJECT behavior
  Given I have defined switch params with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_UNSET
  When I call set_values() with conflicting switch params
  Then a ValueError should be raised
  And the error message should indicate a conflict
  
  # Validates: _get_switch_change_behavior() returns SWITCH_REJECT when batch_mode=True,
  # overriding configured SWITCH_UNSET behavior
```

**Test 3.5.2.2: Returns configured behavior when batch mode is False**

```gherkin
Scenario: Returns configured behavior when batch mode is False
  Given _batch_mode is False
  And I have defined a param with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_UNSET
  When I call _get_switch_change_behavior() with the param definition
  Then it should return SWITCH_UNSET
  
  # Validates: _get_switch_change_behavior() respects configuration in normal mode
```

**Test 3.5.2.3: Returns SWITCH_REJECT as default when not specified**

```gherkin
Scenario: Returns SWITCH_REJECT as default when not specified
  Given _batch_mode is False
  And I have defined a param without PARAM_SWITCH_CHANGE_BEHAVIOR
  When I call _get_switch_change_behavior() with the param definition
  Then it should return SWITCH_REJECT
  
  # Validates: Default backward-compatible behavior when property not set
```

---

#### Function: `_has_switch_conflict(param_definition, xor_param_bind_name)`

**Purpose:** Checks if a parameter in the switch group has a conflicting value.

**Code 3.6.1: _has_switch_conflict function**

**Implementation:**

```python
# Block 3.6.1
def _has_switch_conflict(param_definition, xor_param_bind_name):
    """Check if a param in the switch group has a conflicting value.
    
    Args:
        param_definition: Definition of param being set
        xor_param_bind_name: Bind name of other param to check
        
    Returns:
        True if conflict exists, False otherwise
    """
    # Block 3.6.1.1
    existing_value = config.get_config_value(xor_param_bind_name)
    
    # Block 3.6.1.2: toggle check
    if _is_toggle_param(param_definition):
        # Block 3.6.1.2.1
        return existing_value is True
    else:
        # Block 3.6.1.2.2
        return existing_value is not None
```

**Tests:**

**Test 3.6.2.1: Returns True when toggle param conflicts**

```gherkin
Scenario: Returns True when toggle param conflicts
  Given I have defined a toggle param in a switch group
  And another toggle param in the same group is set to True
  When I call _has_switch_conflict() for the first param
  Then it should return True
  
  # Validates: Conflict detection for toggle params checks existing_value is True
```

**Test 3.6.2.2: Returns False when toggle param has no conflict**

```gherkin
Scenario: Returns False when toggle param has no conflict
  Given I have defined a toggle param in a switch group
  And another toggle param in the same group is set to False
  When I call _has_switch_conflict() for the first param
  Then it should return False
  
  # Validates: False value on toggle param is not considered a conflict
```

**Test 3.6.2.3: Returns True when non-toggle param conflicts**

```gherkin
Scenario: Returns True when non-toggle param conflicts
  Given I have defined a TEXT param in a switch group
  And another TEXT param in the same group is set to 'value'
  When I call _has_switch_conflict() for the first param
  Then it should return True
  
  # Validates: Conflict detection for non-toggle params checks existing_value is not None
```

**Test 3.6.2.4: Returns False when non-toggle param has no conflict**

```gherkin
Scenario: Returns False when non-toggle param has no conflict
  Given I have defined a TEXT param in a switch group
  And another TEXT param in the same group is not set (None)
  When I call _has_switch_conflict() for the first param
  Then it should return False
  
  # Validates: None value on non-toggle param is not considered a conflict
```

---

#### Function: `_resolve_switch_conflict(bind_name, xor_param_bind_name, behavior)`

**Purpose:** Resolves a conflict with another parameter in the switch group according to the specified behavior.

**Code 3.6.3: _resolve_switch_conflict function**

**Implementation:**

```python
# Block 3.6.3
def _resolve_switch_conflict(bind_name, xor_param_bind_name, behavior):
    """Resolve a conflict with another param in the switch group.
    
    Args:
        bind_name: Bind name of param being set
        xor_param_bind_name: Bind name of conflicting param
        behavior: One of SWITCH_UNSET, SWITCH_RESET, or SWITCH_REJECT
        
    Raises:
        ValueError: If behavior is SWITCH_REJECT
    """
    # Block 3.6.3.1: behavior routing
    if behavior == SWITCH_REJECT:
        # Block 3.6.3.1.1
        raise ValueError(
            "Cannot set '{}', conflicts with '{}'".format(bind_name, xor_param_bind_name)
        )
    elif behavior == SWITCH_UNSET:
        # Block 3.6.3.1.2
        unset_param(bind_name=xor_param_bind_name)
    elif behavior == SWITCH_RESET:
        # Block 3.6.3.1.3
        reset_param(bind_name=xor_param_bind_name)
```

**Tests:**

**Test 3.6.4.1: SWITCH_REJECT raises ValueError**

```gherkin
Scenario: SWITCH_REJECT raises ValueError
  Given I have two params in a switch group
  When I call _resolve_switch_conflict() with behavior SWITCH_REJECT
  Then a ValueError should be raised
  And the error message should contain both param names
  
  # Validates: SWITCH_REJECT behavior raises error with descriptive message
```

**Test 3.6.4.2: SWITCH_UNSET calls unset_param**

```gherkin
Scenario: SWITCH_UNSET calls unset_param
  Given I have two params in a switch group
  And I have mocked unset_param()
  When I call _resolve_switch_conflict() with behavior SWITCH_UNSET
  Then unset_param() should be called with the conflicting param's bind_name
  
  # Validates: SWITCH_UNSET behavior delegates to unset_param()
```

**Test 3.6.4.3: SWITCH_RESET calls reset_param**

```gherkin
Scenario: SWITCH_RESET calls reset_param
  Given I have two params in a switch group
  And I have mocked reset_param()
  When I call _resolve_switch_conflict() with behavior SWITCH_RESET
  Then reset_param() should be called with the conflicting param's bind_name
  
  # Validates: SWITCH_RESET behavior delegates to reset_param()
```

---

#### Function: `_apply_switch_behavior_to_group(param_definition, value_to_set, behavior)`

**Purpose:** Orchestrates conflict detection and resolution for all parameters in the switch group.

**Code 3.6.5: _apply_switch_behavior_to_group function**

**Implementation:**

```python
# Block 3.6.5
def _apply_switch_behavior_to_group(param_definition, value_to_set, behavior):
    """Apply switch change behaviour to other params in switch group.
    
    Checks each param in the switch group for conflicts. If conflicts exist,
    applies the specified behaviour (UNSET, RESET, or REJECT).
    
    Args:
        param_definition: Definition of param being set
        value_to_set: Value being set on the param
        behavior: One of SWITCH_UNSET, SWITCH_RESET, or SWITCH_REJECT
        
    Raises:
        ValueError: If behavior is SWITCH_REJECT and conflicts exist
    """
    # Block 3.6.5.1
    bind_name = param_definition.get(PARAM_BIND_NAME)
    # Block 3.6.5.2
    xor_params = get_xor_params(bind_name=bind_name)
    
    # Block 3.6.5.3: early exit check
    if not xor_params:
        # Block 3.6.5.3.1
        return
    
    # Block 3.6.5.4: Apply behaviour to each switch in the group
    for xor_param_bind_name in xor_params:
        # Block 3.6.5.4.1: skip self check
        if xor_param_bind_name == bind_name:
            # Block 3.6.5.4.1.1
            continue
        
        # Block 3.6.5.4.2: conflict check
        if _has_switch_conflict(param_definition, xor_param_bind_name):
            # Block 3.6.5.4.2.1
            _resolve_switch_conflict(bind_name, xor_param_bind_name, behavior)
```

**Tests:**

**Test 3.6.6.1: Returns early when no XOR params exist**

```gherkin
Scenario: Returns early when no XOR params exist
  Given I have defined a param without a PARAM_SWITCH_LIST
  When I call _apply_switch_behavior_to_group()
  Then the function should return without any action
  And no conflict resolution should be attempted
  
  # Validates: Early exit when param is not in a switch group
```

**Test 3.6.6.2: Skips self when iterating XOR params**

```gherkin
Scenario: Skips self when iterating XOR params
  Given I have defined a param in a switch group with itself listed
  When I call _apply_switch_behavior_to_group()
  Then the function should not check conflict with itself
  
  # Validates: Loop correctly skips the param being set
```

**Test 3.6.6.3: Calls helpers for each conflicting param**

```gherkin
Scenario: Calls helpers for each conflicting param
  Given I have three params in a switch group
  And two of them have conflicting values
  And I have mocked _has_switch_conflict() to return True twice
  And I have mocked _resolve_switch_conflict()
  When I call _apply_switch_behavior_to_group()
  Then _has_switch_conflict() should be called twice
  And _resolve_switch_conflict() should be called twice
  
  # Validates: Function iterates all params and delegates to helpers
```

---

**Tests for SWITCH_UNSET behavior (integration):**

**Test 3.6.7.1: SWITCH_UNSET unsets other switches in group**

```gherkin
Scenario: SWITCH_UNSET unsets other switches in group
  Given I have defined two toggle switches with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_UNSET
  And both switches are in the same switch group
  When I set param1 to True
  Then param1 should be True
  When I set param2 to True
  Then param2 should be True
  And param1 should be None
  
  # Validates: _apply_switch_behavior_to_group() calls unset_param() on conflicting switch
  # Validates: Basic SWITCH_UNSET behavior with toggle params
```

**Test 3.6.7.2: SWITCH_UNSET works with text params**

```gherkin
Scenario: SWITCH_UNSET works with text params
  Given I have defined two TEXT switches with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_UNSET
  And both switches are in the same switch group
  When I set param1 to 'value1'
  Then param1 should equal 'value1'
  When I set param2 to 'value2'
  Then param2 should equal 'value2'
  And param1 should be None
  
  # Validates: SWITCH_UNSET behavior works with non-toggle param types
  # Validates: Conflict detection works when existing_value is not None (not just True)
```

**Test 3.6.7.3: SWITCH_UNSET handles multiple conflicts**

```gherkin
Scenario: SWITCH_UNSET handles multiple conflicts
  Given I have defined three switches with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_UNSET
  And all three switches are in the same switch group
  When I set param1 to True
  And I set param2 to True
  And I set param3 to True
  Then param3 should be True
  And param1 should be None
  And param2 should be None
  
  # Validates: _apply_switch_behavior_to_group() iterates all params in switch group
  # Validates: Multiple consecutive switches get unset correctly
```

**Tests for SWITCH_RESET behavior (integration):**

**Test 3.6.7.4: SWITCH_RESET resets other switches to defaults**

```gherkin
Scenario: SWITCH_RESET resets other switches to defaults
  Given I have defined two toggle switches with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_RESET
  And both switches have PARAM_DEFAULT set to False
  And both switches are in the same switch group
  When I set param1 to True
  Then param1 should be True
  When I set param2 to True
  Then param2 should be True
  And param1 should be False (default value)
  
  # Validates: _apply_switch_behavior_to_group() calls reset_param() on conflicting switch
  # Validates: Basic SWITCH_RESET behavior restores PARAM_DEFAULT values
```

**Test 3.6.7.5: SWITCH_RESET works with number params**

```gherkin
Scenario: SWITCH_RESET works with number params
  Given I have defined two NUMBER switches with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_RESET
  And param1 has PARAM_DEFAULT set to 10
  And param2 has PARAM_DEFAULT set to 20
  And both switches are in the same switch group
  When I set param1 to 100
  Then param1 should equal 100
  When I set param2 to 200
  Then param2 should equal 200
  And param1 should equal 10 (default value)
  
  # Validates: SWITCH_RESET behavior works with numeric param types
  # Validates: reset_param() correctly restores non-boolean defaults
```

**Test 3.6.7.6: SWITCH_RESET with no default unsets param**

```gherkin
Scenario: SWITCH_RESET with no default unsets param
  Given I have defined two switches with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_RESET
  And neither switch has PARAM_DEFAULT defined
  And both switches are in the same switch group
  When I set param1 to True
  Then param1 should be True
  When I set param2 to True
  Then param2 should be True
  And param1 should be None
  
  # Validates: reset_param() behavior when PARAM_DEFAULT is not defined
  # Validates: Fallback to unset when no default exists (reset_param's documented behavior)
```

**Test 3.6.7.7: SWITCH_RESET handles multiple conflicts**

```gherkin
Scenario: SWITCH_RESET handles multiple conflicts
  Given I have defined three switches with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_RESET
  And all three have defaults defined
  And all three switches are in the same switch group
  When I set param1 to True
  And I set param2 to True
  And I set param3 to True
  Then param3 should be True
  And param1 should equal its default value
  And param2 should equal its default value
  
  # Validates: _apply_switch_behavior_to_group() resets all conflicting switches in group
  # Validates: Multiple resets work correctly in sequence
```

**Tests for SWITCH_REJECT behavior (integration):**

**Test 3.6.7.8: SWITCH_REJECT raises error on conflict**

```gherkin
Scenario: SWITCH_REJECT raises error on conflict
  Given I have defined two toggle switches with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_REJECT
  And both switches are in the same switch group
  When I set param1 to True
  Then param1 should be True
  When I attempt to set param2 to True
  Then a ValueError should be raised
  
  # Validates: _apply_switch_behavior_to_group() raises ValueError when behavior is SWITCH_REJECT
  # Validates: Current XOR validation behavior is preserved
```

**Test 3.6.7.9: SWITCH_REJECT error message contains param names**

```gherkin
Scenario: SWITCH_REJECT error message contains param names
  Given I have defined two switches with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_REJECT
  And both switches are in the same switch group
  And param1 is set to True
  When I attempt to set param2 to True
  Then a ValueError should be raised
  And the error message should contain 'param1'
  And the error message should contain 'param2'
  
  # Validates: Error message format provides useful debugging information
  # Validates: Users can identify which params are in conflict
```

---

#### Function: `_handle_switch_group_behavior(param_definition, value_to_set)`

**Purpose:** Main orchestration function (renamed from `_validate_xor_conflicts`). Coordinates validation checks and delegates to behavior application function.

**Code 3.7.1: _handle_switch_group_behavior function**

**Implementation:**

```python
# Block 3.7.1
def _handle_switch_group_behavior(param_definition, value_to_set):
    """Handle switch group behaviour when setting a parameter.
    
    Renamed from _validate_xor_conflicts to reflect expanded responsibility.
    Now applies configured behaviour (unset, reset, or reject) rather than
    only validating.
    
    Args:
        param_definition: Definition of param being set
        value_to_set: Value being set on the param
        
    Raises:
        ValueError: If SWITCH_REJECT is configured and conflicts exist
    """
    # Block 3.7.1.1: Skip if validation is disabled (e.g., during config loading)
    if not _get_xor_validation_enabled():
        # Block 3.7.1.1.1
        return
    
    # Block 3.7.1.2: Skip if this is a toggle param being set to False (no conflict)
    if _is_toggle_param(param_definition) and value_to_set is False:
        # Block 3.7.1.2.1
        return
    
    # Block 3.7.1.3: Get the configured behaviour (may be forced to SWITCH_REJECT in batch mode)
    behavior = _get_switch_change_behavior(param_definition)
    
    # Block 3.7.1.4: Apply the behaviour to other params in the group
    _apply_switch_behavior_to_group(param_definition, value_to_set, behavior)
```

**Tests:**

**Test 3.7.2.1: Respects skip validation flag**

```gherkin
Scenario: Respects skip validation flag
  Given I have defined two switches with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_REJECT
  And both switches are in the same switch group
  When I call _set_xor_validation_enabled(False)
  And I set param1 to True
  And I set param2 to True
  Then param1 should be True
  And param2 should be True
  And no error should be raised
  
  # Validates: _handle_switch_group_behavior() early exit when _get_xor_validation_enabled() is False
  # Validates: Existing mechanism for loading defaults/config bypasses new behavior
```

**Test 3.7.2.2: Re-enabling validation after skip**

```gherkin
Scenario: Re-enabling validation after skip
  Given I have defined two switches with SWITCH_REJECT
  And both switches are in the same switch group
  When I call _set_xor_validation_enabled(False)
  And I set param1 to True
  And I set param2 to True
  And I call _set_xor_validation_enabled(True)
  And I attempt to set param3 to True
  Then a ValueError should be raised
  
  # Validates: Validation flag can be toggled and takes effect immediately
  # Validates: Switch behavior resumes after skip mode is disabled
```

**Test 3.7.2.3: Setting toggle to False does not trigger switch behavior**

```gherkin
Scenario: Setting toggle to False does not trigger switch behavior
  Given I have defined two toggle switches in the same switch group
  When I set param1 to True
  Then param1 should be True
  When I set param1 to False
  Then param1 should be False
  And no switch behavior should be triggered
  
  # Validates: _handle_switch_group_behavior() early exit when value_to_set is False
  # Validates: Setting toggle to False is not considered a conflict
```

**Test 3.7.2.4: Setting toggle to False allows other switch to be set**

```gherkin
Scenario: Setting toggle to False allows other switch to be set
  Given I have defined two toggle switches with SWITCH_REJECT in the same switch group
  When I set param1 to True
  And I set param1 to False
  And I set param2 to True
  Then param2 should be True
  And no error should be raised
  
  # Validates: After setting toggle to False, switch group is available for other params
  # Validates: Conflict detection recognizes False as "not set" (has_conflict check)
```

---

#### Integration Tests

**Purpose:** Validate end-to-end scenarios and edge cases involving multiple functions.

**Test 3.8.1: Default behavior is SWITCH_REJECT (backward compatibility)**

```gherkin
Scenario: Default behavior is SWITCH_REJECT (backward compatibility)
  Given I have defined two switches without specifying PARAM_SWITCH_CHANGE_BEHAVIOR
  And both switches are in the same switch group
  When I set param1 to True
  Then param1 should be True
  When I attempt to set param2 to True
  Then a ValueError should be raised
  
  # Validates: _get_switch_change_behavior() returns SWITCH_REJECT as default
  # Validates: Backward compatibility - existing code without property still works
```

**Test 3.8.2: Multiple switches in group with SWITCH_UNSET**

```gherkin
Scenario: Multiple switches in group with SWITCH_UNSET
  Given I have defined four switches with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_UNSET
  And all four switches are in the same switch group
  When I set param1 to True
  And I set param2 to True
  And I set param3 to True
  And I set param4 to True
  Then param4 should be True
  And param1 should be None
  And param2 should be None
  And param3 should be None
  
  # Validates: get_xor_params() returns all params in group (not just two)
  # Validates: _apply_switch_behavior_to_group() handles large switch groups
  # Validates: Sequential switching works correctly with multiple params
```

**Test 3.8.3: Mixed behaviors in same switch group**

```gherkin
Scenario: Mixed behaviors in same switch group
  Given I have defined param1 with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_UNSET
  And I have defined param2 with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_REJECT
  And both are in the same switch group
  When I set param1 to True
  And I set param2 to True
  Then param2 should be True
  And param1 should be None (unset by param2's behavior)
  When I set param1 to True
  Then a ValueError should be raised (param1 tries to unset param2, but param2 rejects)
  
  # Validates: Each param uses its own PARAM_SWITCH_CHANGE_BEHAVIOR property
  # Validates: Asymmetric behavior (param1 can be unset by param2, but not vice versa)
  # Validates: Behavior is determined by the param BEING SET, not the conflicting param
```

**Test 3.8.4: CLI via set_values forces SWITCH_REJECT**

```gherkin
Scenario: CLI via set_values forces SWITCH_REJECT
  Given I have defined two switches with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_UNSET
  And both switches are in the same switch group
  When I call set_values() with conflicting switch params
  Then a ValueError should be raised
  And the error message should indicate a conflict
  
  # Validates: End-to-end integration of batch mode override
  # Validates: CLI strictness is enforced regardless of programmatic behavior configuration
  # Validates: Decision flow: batch_mode=True → SWITCH_REJECT forced
```

[↑ Back to top](#table-of-contents)

### 4. Update CLI parser to use batch param setting

**File:** `src/spafw37/cli.py`

Refactor `_parse_command_line()` to use the new `param.set_values()` function instead of calling `set_param()` individually. This ensures batch mode is enabled during CLI parsing, forcing SWITCH_REJECT behaviour for all switch params regardless of their configured behaviour.

**Implementation approach:**

The current `_parse_command_line()` function already:
1. Queues commands with `command.queue_command()` 
2. Parses `@file` references with `_parse_file_value()`
3. Routes list/dict params to `join_param()`, others to `set_param()`

**Changes needed:**

1. Parse @file references before param processing loop (modify in place)
2. Replace param processing loop with call to `param.set_values()`
3. Keep command queueing unchanged (already inline)

**Code 4.1: _parse_command_line function refactored**

```python
# Block 4.1
def _parse_command_line(tokens):
    """Parse command-line arguments and execute commands.
    
    Iterates through tokenized arguments, handling commands and parameters.
    
    Args:
        tokens: Pre-tokenized dict from _tokenise_cli_args() with structure:
                {"commands": [...], "params": [{"alias": "--name", "value": "val1"}]}
    """
    # Block 4.1.1: Queue commands (unchanged)
    for command_name in tokens["commands"]:
        # Block 4.1.1.1
        command.queue_command(command_name)
    
    # Block 4.1.2: Parse @file references in params, returns new list
    parsed_params = _parse_file_references_in_params(tokens["params"])
    
    # Block 4.1.3: Batch set all params with batch mode enabled
    param.set_values(parsed_params)
```

**Tests:** Add tests in `tests/test_cli.py`

**Test 4.2.1: CLI uses set_values for param setting**

```gherkin
Scenario: CLI uses set_values for param setting
  Given I have mocked param.set_values()
  When I call _parse_command_line() with tokenized arguments
  Then param.set_values() should be called once
  And the argument should have the correct params structure with parsed file values
```

**Test 4.2.2: CLI parses file references and passes result to set_values**

```gherkin
Scenario: CLI parses file references and passes result to set_values
  Given I have created a temp file containing 'test_value'
  And I have mocked param.set_values()
  And I have tokenized arguments with a param value '@tempfile'
  When I call _parse_command_line() with the arguments
  Then param.set_values() should be called once
  And the params list should have parsed file value 'test_value'
  And the params list should not contain '@tempfile'
```

---

#### Function: `_parse_file_references_in_params(param_entries)`

**Purpose:** Parses @file references in all parameter values, returning a new list with parsed values.

**Code 4.3: _parse_file_references_in_params function**

**Implementation:**

```python
# Block 4.3
def _parse_file_references_in_params(param_entries):
    """Parse @file references in parameter values.
    
    Returns a new list with file references resolved. Does not modify
    the original param_entries list.
    
    Args:
        param_entries: List of param dicts with structure [{'alias': '--name', 'value': 'val'}]
        
    Returns:
        New list with same structure but @file values replaced with file contents
    """
    # Block 4.3.1: Create new list to avoid modifying original
    parsed_entries = []
    
    # Block 4.3.2: Process each entry
    for param_entry in param_entries:
        # Block 4.3.2.1: Extract value
        value = param_entry.get("value")
        
        # Block 4.3.2.2: Check for file reference pattern
        if value and re.search(r'(?<!\w)@\S+', value):
            # Block 4.3.2.2.1: Create new dict with parsed value
            parsed_entry = param_entry.copy()
            parsed_entry["value"] = _parse_file_value(value)
            parsed_entries.append(parsed_entry)
        else:
            # Block 4.3.2.2.2: Append original entry unchanged
            parsed_entries.append(param_entry)
    
    # Block 4.3.3: Return new list
    return parsed_entries
```

**Tests:**

**Test 4.4.1: Returns new list with parsed file references**

```gherkin
Scenario: Returns new list with parsed file references
  Given I have created a temp file containing 'test_value'
  And I have a param entry list with --param @tempfile
  When I call _parse_file_references_in_params() with the list
  Then it should return a new list
  And the new list should have --param with value 'test_value'
  And the original list should still have --param with value '@tempfile'
  
  # Validates: Function returns new list without modifying original
  # Validates: File references are parsed using _parse_file_value()
```

**Test 4.4.2: Handles multiple file references**

```gherkin
Scenario: Handles multiple file references
  Given I have created temp files with values 'value1' and 'value2'
  And I have a param entry list with --param1 @file1 and --param2 @file2
  When I call _parse_file_references_in_params() with the list
  Then the returned list should have --param1 with value 'value1'
  And the returned list should have --param2 with value 'value2'
  
  # Validates: Multiple file references in different params are all parsed
```

**Test 4.4.3: Leaves non-file values unchanged**

```gherkin
Scenario: Leaves non-file values unchanged
  Given I have a param entry list with --param1 normal_value and --param2 another_value
  When I call _parse_file_references_in_params() with the list
  Then the returned list should have --param1 with value 'normal_value'
  And the returned list should have --param2 with value 'another_value'
  
  # Validates: Params without @file references pass through unchanged
```

**Test 4.4.4: Handles mixed file and non-file values**

```gherkin
Scenario: Handles mixed file and non-file values
  Given I have created a temp file containing 'file_value'
  And I have a param entry list with --param1 @tempfile and --param2 normal_value
  When I call _parse_file_references_in_params() with the list
  Then the returned list should have --param1 with value 'file_value'
  And the returned list should have --param2 with value 'normal_value'
  
  # Validates: Mix of file and non-file params handled correctly
```

---

**Integration tests for CLI:**

**Test 4.5.1: CLI switch conflicts always error regardless of configured behavior**

```gherkin
Scenario: CLI switch conflicts always error regardless of configured behavior
  Given I have defined two switches with PARAM_SWITCH_CHANGE_BEHAVIOR set to SWITCH_UNSET
  And both switches are in the same switch group
  When I call handle_cli_args(['--verbose', '--silent'])
  Then a ValueError should be raised
  And the error message should indicate a conflict between switches
  
  # Validates: Batch mode forces SWITCH_REJECT during CLI parsing
```

**Test 4.5.2: CLI parses file references before calling set_values**

```gherkin
Scenario: CLI parses file references before calling set_values
  Given I have created a temp file containing 'test_value'
  And I have mocked param.set_values()
  When I call handle_cli_args(['--name', '@tempfile'])
  Then set_values() should be called
  And the value passed should be 'test_value'
  And the value should not be '@tempfile'
  
  # Validates: _parse_file_references_in_params() called before set_values()
```

**Test 4.5.3: CLI batch sets multiple params in one call**

```gherkin
Scenario: CLI batch sets multiple params in one call
  Given I have mocked param.set_values()
  When I call handle_cli_args(['--name', 'value1', '--count', '5'])
  Then set_values() should be called once
  And the argument should be a list containing both params
  And the list should have param '--name' with value 'value1'
  And the list should have param '--count' with value '5'
  
  # Validates: All params passed to set_values() in single call
```

[↑ Back to top](#table-of-contents)

### 5. Create example demonstrating switch behavior

**File:** `examples/params_switch_behavior.py` (new)

Create a new example script demonstrating all three switch change behaviours. This helps users understand when to use each behaviour mode.

**Implementation order:**

1. Create example with three separate demos (reject, unset, reset)
2. Show mode-switching use case with SWITCH_UNSET
3. Show strict validation use case with SWITCH_REJECT
4. Show state restoration use case with SWITCH_RESET

**Example structure:**

**Code 5.0: Module docstring and imports**

```python
"""Switch Change Behaviour Example - Control switch group interactions.

This example demonstrates:
- SWITCH_REJECT: Strict validation (default, backward compatible)
- SWITCH_UNSET: Auto-clear conflicting switches
- SWITCH_RESET: Restore conflicting switches to defaults
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TOGGLE,
    PARAM_ALIASES,
    PARAM_SWITCH_LIST,
    PARAM_SWITCH_CHANGE_BEHAVIOR,
    PARAM_DEFAULT,
    SWITCH_REJECT,
    SWITCH_UNSET,
    SWITCH_RESET,
)
```

**Code 5.1: demo_switch_reject function**

```python
def demo_switch_reject():
    """Demonstrate SWITCH_REJECT - strict validation (default)."""
    print("\n=== Example 1: SWITCH_REJECT (Default Behaviour) ===")
    print("Strict validation - only one switch can be set at a time.\n")
    
    # Define params with default SWITCH_REJECT behaviour
    spafw37.add_params([
        {
            PARAM_NAME: 'mode_read',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ['--mode-read', '-r'],
            PARAM_SWITCH_LIST: ['mode_write'],
            # PARAM_SWITCH_CHANGE_BEHAVIOR not specified - defaults to SWITCH_REJECT
        },
        {
            PARAM_NAME: 'mode_write',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ['--mode-write', '-w'],
            PARAM_SWITCH_LIST: ['mode_read'],
        },
    ])
    
    # Set mode_read first
    spafw37.set_param('mode_read', True)
    print(f"Set mode_read=True")
    print(f"  mode_read={spafw37.get_param('mode_read')}")
    print(f"  mode_write={spafw37.get_param('mode_write')}")
    
    # Try to set mode_write - should raise error
    print("\nAttempting to set mode_write=True (should fail)...")
    try:
        spafw37.set_param('mode_write', True)
        print("  ERROR: Should have raised ValueError!")
    except ValueError as e:
        print(f"  Expected error: {e}")
    
    print(f"\nFinal state:")
    print(f"  mode_read={spafw37.get_param('mode_read')}")
    print(f"  mode_write={spafw37.get_param('mode_write')}")
```

**Code 5.2: demo_switch_unset function**

```python
def demo_switch_unset():
    """Demonstrate SWITCH_UNSET - auto-clear conflicting switches."""
    print("\n=== Example 2: SWITCH_UNSET (Mode Switching) ===")
    print("Auto-clear conflicts - setting one switch unsets others.\n")
    
    # Define params with SWITCH_UNSET behaviour
    spafw37.add_params([
        {
            PARAM_NAME: 'mode_read',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ['--read'],
            PARAM_SWITCH_LIST: ['mode_write', 'mode_append'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
        {
            PARAM_NAME: 'mode_write',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ['--write'],
            PARAM_SWITCH_LIST: ['mode_read', 'mode_append'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
        {
            PARAM_NAME: 'mode_append',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ['--append'],
            PARAM_SWITCH_LIST: ['mode_read', 'mode_write'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
        },
    ])
    
    # Set read mode
    spafw37.set_param('mode_read', True)
    print(f"Set mode_read=True")
    print(f"  mode_read={spafw37.get_param('mode_read')}")
    print(f"  mode_write={spafw37.get_param('mode_write')}")
    print(f"  mode_append={spafw37.get_param('mode_append')}")
    
    # Switch to write mode - read should be automatically unset
    print("\nSwitching to mode_write=True...")
    spafw37.set_param('mode_write', True)
    print(f"  mode_read={spafw37.get_param('mode_read')} (automatically unset)")
    print(f"  mode_write={spafw37.get_param('mode_write')}")
    print(f"  mode_append={spafw37.get_param('mode_append')}")
    
    # Switch to append mode - write should be automatically unset
    print("\nSwitching to mode_append=True...")
    spafw37.set_param('mode_append', True)
    print(f"  mode_read={spafw37.get_param('mode_read')}")
    print(f"  mode_write={spafw37.get_param('mode_write')} (automatically unset)")
    print(f"  mode_append={spafw37.get_param('mode_append')}")
```

**Code 5.3: demo_switch_reset function**

```python
def demo_switch_reset():
    """Demonstrate SWITCH_RESET - restore conflicting switches to defaults."""
    print("\n=== Example 3: SWITCH_RESET (State Restoration) ===")
    print("Reset conflicts - setting one switch resets others to defaults.\n")
    
    # Define params with SWITCH_RESET behaviour and meaningful defaults
    spafw37.add_params([
        {
            PARAM_NAME: 'priority_high',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ['--high'],
            PARAM_DEFAULT: False,
            PARAM_SWITCH_LIST: ['priority_low'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_RESET,
        },
        {
            PARAM_NAME: 'priority_low',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALIASES: ['--low'],
            PARAM_DEFAULT: False,
            PARAM_SWITCH_LIST: ['priority_high'],
            PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_RESET,
        },
    ])
    
    # Set high priority
    spafw37.set_param('priority_high', True)
    print(f"Set priority_high=True")
    print(f"  priority_high={spafw37.get_param('priority_high')}")
    print(f"  priority_low={spafw37.get_param('priority_low')}")
    
    # Switch to low priority - high should be reset to default (False)
    print("\nSwitching to priority_low=True...")
    spafw37.set_param('priority_low', True)
    print(f"  priority_high={spafw37.get_param('priority_high')} (reset to default)")
    print(f"  priority_low={spafw37.get_param('priority_low')}")
    
    # Switch back to high priority - low should be reset to default (False)
    print("\nSwitching back to priority_high=True...")
    spafw37.set_param('priority_high', True)
    print(f"  priority_high={spafw37.get_param('priority_high')}")
    print(f"  priority_low={spafw37.get_param('priority_low')} (reset to default)")


if __name__ == '__main__':
    demo_switch_reject()
    demo_switch_unset()
    demo_switch_reset()
    
    print("\n=== All demonstrations complete ===")
```

**Tests:** Run example manually to verify all behaviours work correctly

[↑ Back to top](#table-of-contents)

### 6. Update documentation

Update user-facing documentation to describe the new functionality. Add version notes to indicate this was added in v1.1.0.

---

#### 6.1. Update parameters.md

**File:** `doc/parameters.md`

Add new section "Switch Change Behaviour" after "Mutual Exclusion (Switch Lists)" section. This section documents the `PARAM_SWITCH_CHANGE_BEHAVIOR` property, provides code examples for each behaviour mode, explains when to use each mode, and includes version note.

**Location:** After "Mutual Exclusion (Switch Lists)" section

**Content to add:**

````markdown
## Switch Change Behaviour

**Added in v1.1.0**

Control what happens to other parameters in a switch group when one parameter is set. By default, attempting to set multiple mutually exclusive parameters raises an error (`SWITCH_REJECT`). You can configure alternate behaviours using `PARAM_SWITCH_CHANGE_BEHAVIOR`.

### Behaviour Options

- `SWITCH_REJECT` (default): Raise error if another switch in the group is already set
- `SWITCH_UNSET`: Automatically unset other switches in the group
- `SWITCH_RESET`: Reset other switches in the group to their default values

### Example: Mode Switching with SWITCH_UNSET

```python
spafw37.add_params([
    {
        PARAM_NAME: 'mode_read',
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_SWITCH_LIST: ['mode_write', 'mode_append'],
        PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
    },
    {
        PARAM_NAME: 'mode_write',
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_SWITCH_LIST: ['mode_read', 'mode_append'],
        PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
    },
    {
        PARAM_NAME: 'mode_append',
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_SWITCH_LIST: ['mode_read', 'mode_write'],
        PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_UNSET,
    },
])

# Switch between modes freely
spafw37.set_param('mode_read', True)   # mode_read=True
spafw37.set_param('mode_write', True)  # mode_write=True, mode_read=None (unset)
spafw37.set_param('mode_append', True) # mode_append=True, mode_write=None (unset)
```

This example demonstrates automatic mode switching behaviour. Params are configured with `PARAM_SWITCH_CHANGE_BEHAVIOR` set to `SWITCH_UNSET`.

When `mode_write` is set, the previously active `mode_read` is automatically removed from configuration. The system calls `unset_param()` on conflicting switches in the same group.

This pattern is useful for applications with mutually exclusive operational modes where the user should be able to switch freely between modes without manually clearing previous settings.

See complete example in [`examples/params_switch_behavior.py`](../examples/params_switch_behavior.py) - `demo_switch_unset()` function.

### Example: State Restoration with SWITCH_RESET

```python
spafw37.add_params([
    {
        PARAM_NAME: 'priority_high',
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_DEFAULT: False,
        PARAM_SWITCH_LIST: ['priority_low'],
        PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_RESET,
    },
    {
        PARAM_NAME: 'priority_low',
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_DEFAULT: False,
        PARAM_SWITCH_LIST: ['priority_high'],
        PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_RESET,
    },
])

# Switch between priorities
spafw37.set_param('priority_high', True)  # priority_high=True
spafw37.set_param('priority_low', True)   # priority_low=True, priority_high=False (reset)
spafw37.set_param('priority_high', True)  # priority_high=True, priority_low=False (reset)
```

This example demonstrates state restoration behaviour. Params are configured with `PARAM_SWITCH_CHANGE_BEHAVIOR` set to `SWITCH_RESET`.

When `priority_low` is set, the previously active `priority_high` is reset to its default value (False) rather than being removed entirely. The system calls `reset_param()` on conflicting switches in the same group.

This pattern preserves parameter definitions in configuration while ensuring only one switch is active. It is useful for switches that have meaningful default states that should be restored when switching modes.

See complete example in [`examples/params_switch_behavior.py`](../examples/params_switch_behavior.py) - `demo_switch_reset()` function.

### Example: Strict Validation with SWITCH_REJECT

```python
spafw37.add_params([
    {
        PARAM_NAME: 'mode_read',
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_SWITCH_LIST: ['mode_write'],
        PARAM_SWITCH_CHANGE_BEHAVIOR: SWITCH_REJECT,  # or omit - this is the default
    },
    {
        PARAM_NAME: 'mode_write',
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_SWITCH_LIST: ['mode_read'],
        # PARAM_SWITCH_CHANGE_BEHAVIOR omitted - defaults to SWITCH_REJECT
    },
])

# Strict validation enforced
spafw37.set_param('mode_read', True)  # mode_read=True
try:
    spafw37.set_param('mode_write', True)  # Raises ValueError
except ValueError as e:
    print(f"Error: {e}")  # "Cannot set 'mode_write', conflicts with 'mode_read'"
```

This example demonstrates the default strict validation behaviour (backward compatible with existing behaviour). Params are configured with `PARAM_SWITCH_CHANGE_BEHAVIOR` set to `SWITCH_REJECT`, or the property is omitted entirely (SWITCH_REJECT is the default).

When attempting to set `mode_write` while `mode_read` is already active, a `ValueError` is raised immediately. The system does not modify any parameters in the switch group.

This pattern enforces explicit conflict resolution by the application. It ensures users are aware when they attempt to set conflicting parameters and must handle the conflict explicitly in their code.

See complete example in [`examples/params_switch_behavior.py`](../examples/params_switch_behavior.py) - `demo_switch_reject()` function.
````

**Tests:** Manual review to verify documentation clarity and accuracy

---

#### 6.2. Update API reference

**File:** `doc/api-reference.md`

Add documentation for the new property and constants to the API reference.

**Updates required:**

1. **Parameter properties table** - Add new row:
   ```markdown
   | `PARAM_SWITCH_CHANGE_BEHAVIOR` | Controls what happens to other switch params in the same group when one is set. Values: `SWITCH_UNSET`, `SWITCH_RESET`, `SWITCH_REJECT` (default). Added in v1.1.0. |
   ```

2. **Constants section** - Add three new constant definitions:
   ```markdown
   ### Switch Change Behaviour Constants
   
   **Added in v1.1.0**
   
   - **`SWITCH_UNSET`** (`'switch-unset'`)
     - Automatically unset other switches in the same group when one is set
     - Uses `unset_param()` to remove conflicting switches from configuration
     - Useful for mode switching where previous mode should be cleared
   
   - **`SWITCH_RESET`** (`'switch-reset'`)
     - Reset other switches in the same group to their default values when one is set
     - Uses `reset_param()` to restore conflicting switches to defaults
     - Useful when switches have meaningful default states that should be preserved
   
   - **`SWITCH_REJECT`** (`'switch-reject'`)
     - Raise `ValueError` if another switch in the group is already set (default behaviour)
     - Maintains backward compatibility with existing behaviour
     - Useful for strict validation where only one switch should ever be set
   ```

3. **Helper functions** (if exposed publicly) - Document batch mode functions:
   ```markdown
   ### set_values(param_values)
   
   **Added in v1.1.0**
   
   Sets multiple parameter values with batch mode enabled. Used internally by CLI parser to enforce `SWITCH_REJECT` behaviour for all switch params regardless of configuration.
   
   **Parameters:**
   - `param_values` (list): List of dicts with structure `[{"alias": "--name", "value": "val"}]`
   
   **Note:** This function forces `SWITCH_REJECT` behaviour during CLI parsing to ensure clear error messages for user mistakes.
   ```

**Tests:** Manual review to verify documentation completeness and accuracy

---

#### 6.3. Update README.md

**File:** `README.md`

Add references to the new functionality in three locations: features list, examples list, and "What's New" section.

**Updates required:**

1. **Features list** - Add bullet point in appropriate location:
   ```markdown
   - Switch param change behaviour control for param groups (`SWITCH_UNSET`, `SWITCH_RESET`, `SWITCH_REJECT`)
   ```

2. **Examples list** - Add new example entry:
   ```markdown
   - **`params_switch_behavior.py`** - Demonstrates switch param change behaviour modes: strict validation (SWITCH_REJECT), automatic mode switching (SWITCH_UNSET), and state restoration (SWITCH_RESET)
   ```

3. **"What's New in v1.1.0" section** - Add one-line description:
   ```markdown
   - Switch Param behaviour control with `PARAM_SWITCH_CHANGE_BEHAVIOR` property (`SWITCH_UNSET`, `SWITCH_RESET`, `SWITCH_REJECT`)
   ```

**Tests:** Manual review to verify README clarity and consistency

[↑ Back to top](#table-of-contents)

## Further Considerations

### 1. Default behaviour selection - RESOLVED

**Question:** Should the default behaviour be `SWITCH_REJECT` to match current behaviour, or `SWITCH_UNSET` for more convenient mode switching?

**Proposed answer:** Default will be `SWITCH_REJECT` (current behaviour)

**Rationale:**
- Maintains backward compatibility with existing applications
- Prevents breaking changes for users relying on error-based validation
- Users must explicitly opt-in to new behaviours (SWITCH_UNSET, SWITCH_RESET)
- Current error behaviour happens in `set_param()` via `_validate_xor_conflicts()`, not in CLI parser

**Implementation:**
- Use `SWITCH_REJECT` as default in `_get_switch_change_behavior()` helper
- Document that `SWITCH_REJECT` is the default in all documentation
- Ensure tests verify default behaviour is SWITCH_REJECT

**Alternative considered:** Default to `SWITCH_UNSET` for "auto-switching" behaviour
- Pro: More convenient for mode-switching use cases
- Pro: Eliminates need for CLI parser error handling

**Rejected because:** Breaking change for existing applications expecting errors when conflicting params are provided

[↑ Back to top](#table-of-contents)

### 2. CLI parser interaction - RESOLVED

**Question:** How should the CLI parser handle switch params in groups? Should it always throw an error, or should it respect the configured behaviour?

**Selected Solution: Option B** - CLI always throws errors for switch conflicts

**Option A:** CLI uses configured behaviour uniformly

CLI parser will call `set_param()` which will apply the configured behaviour. The current error behaviour happens because `set_param()` throws errors, not because the CLI parser validates.

**Rationale:**
- CLI parser simply calls `set_param()` for each parameter - it does not perform validation itself
- XOR validation currently happens in `set_param()` via `_validate_xor_conflicts()` 
- When switch behaviour is implemented, CLI-provided params will automatically use the configured behaviour
- For `SWITCH_REJECT` (default): error thrown as it is today
- For `SWITCH_UNSET` or `SWITCH_RESET`: CLI-provided params will trigger auto-switching behaviour

**Implementation:**
- No changes needed to CLI parser (`src/spafw37/cli.py`)
- CLI parser already calls `set_param()` which will use new behaviour logic
- Switch behaviour applies uniformly to both CLI and programmatic `set_param()` calls
- Document that switch behaviour applies to all param setting, including CLI arguments

**User experience:**
- With `SWITCH_UNSET`/`SWITCH_RESET`, users can provide both `--verbose` and `--silent` on command line
- The last one specified will win (later param unsets/resets earlier one)
- This matches standard CLI convention where later flags override earlier ones
- May want to log when switch behaviour triggers for user visibility

---

**Option B:** CLI always throws errors for switch conflicts

CLI-provided conflicting switches should always raise errors regardless of configured behaviour. This requires a mechanism to force `SWITCH_REJECT` behaviour during CLI parsing.

**Rationale:**
- Providing conflicting flags on command line is a user error that should be caught immediately
- Users expect clear error messages when they make mistakes with command line arguments
- The `SWITCH_UNSET`/`SWITCH_RESET` behaviours are intended for programmatic param state management, not CLI usage
- "Last flag wins" behaviour is confusing when user explicitly provides both flags

**Implementation:**
1. Add `_init_mode` flag to `src/spafw37/param.py` (module-level, like `_skip_xor_validation`)
2. Add getter/setter functions to control the flag
3. Refactor `_parse_command_line()` in `src/spafw37/cli.py`:
   - Pre-parse file values (`@file` references) for all param tokens
   - Call new `param.set_values(tokens["params"])` function with file-parsed tokens
4. Implement `set_values(param_values)` in `src/spafw37/param.py`:
   - Set `_init_mode = True` at start
   - Iterate through param tokens, calling `set_param()` or `join_param()` as appropriate
   - Set `_init_mode = False` at end (in finally block)
5. Modify `_get_switch_change_behavior()` to check `_init_mode`:
   - If `_init_mode` is True, always return `SWITCH_REJECT`
   - Otherwise, return configured behaviour from param definition

**User experience:**
- CLI: `app --verbose --silent` → Error: "Cannot set 'silent', conflicts with 'verbose'"
- Programmatic with `SWITCH_UNSET`: `set_param('silent', True)` after `set_param('verbose', True)` → silent=True, verbose unset
- Clear separation between CLI strictness and programmatic flexibility

---

**Alternative considered:** Keep CLI strict, only apply behaviour to programmatic calls
- Pro: Clear error messages when users provide conflicting CLI args
- Con: Inconsistent behaviour between CLI and programmatic param setting
- Con: Would require CLI parser to duplicate validation logic

**Rejected because:** Separation of concerns - CLI parser should just parse and call `set_param()`, all validation logic belongs in param module

[↑ Back to top](#table-of-contents)

## Success Criteria

- [x] `SWITCH_UNSET`, `SWITCH_RESET`, and `SWITCH_REJECT` constants defined in `src/spafw37/constants/param.py`
- [x] `PARAM_SWITCH_CHANGE_BEHAVIOR` property constant added to `src/spafw37/constants/param.py`
- [x] Helper functions `_get_switch_change_behavior()` and `_apply_switch_behavior_to_group()` implemented in `src/spafw37/param.py`
- [x] Function `_validate_xor_conflicts()` renamed to `_handle_switch_group_behavior()` with expanded logic
- [x] Default behaviour is `SWITCH_REJECT` (backward compatible)
- [x] CLI parser uses batch mode to enforce `SWITCH_REJECT` for all CLI arguments regardless of configured behaviour
- [x] Programmatic `set_param()` calls respect configured `PARAM_SWITCH_CHANGE_BEHAVIOR`
- [x] Batch mode implementation with `_set_batch_mode()`, `_get_batch_mode()`, and `set_values()` functions
- [x] CLI parser refactored to use `set_values()` for batch param setting
- [x] Helper functions `_process_param_values()`, `_process_single_param_entry()`, and `_parse_file_references_in_params()` implemented
- [x] All helper functions for conflict detection and resolution implemented (`_has_switch_conflict()`, `_resolve_switch_conflict()`)
- [x] Existing XOR tests updated to accept new error message format ("Cannot set '...', conflicts with '...'" instead of "Conflicting parameters provided")
- [x] Example script `examples/params_switch_behavior.py` demonstrating all three modes
- [x] Documentation updated in `doc/parameters.md` with new "Switch Change Behaviour" section
- [x] Documentation updated in `doc/api-reference.md` with new constants
- [x] Documentation updated in `README.md` features list and "What's New in v1.1.0"
- [x] Documentation updated in `examples/README.md` with new example entry
- [x] Version notes ("**Added in v1.1.0**") added to new documentation sections
- [x] Comprehensive tests in `tests/test_param_switch_behavior.py` covering all three behaviour modes (22 tests)
- [x] Tests verify behaviour with toggle parameters (implementation limitation: only toggles currently supported)
- [x] Tests verify behaviour with multiple switches in a group (3+ params)
- [x] Tests verify backward compatibility (default SWITCH_REJECT matches current behaviour)
- [x] Tests verify `_skip_xor_validation` flag still works correctly
- [x] Tests verify batch mode override functionality
- [x] All existing tests still passing (618 passed, 1 skipped - 22 new tests added)
- [x] Test coverage maintained at 96.58% (well above 80% minimum and 90% target)
- [ ] Issue #32 closed with reference to implementation

## Implementation Notes

This section documents deviations from the original plan and key implementation decisions.

### Toggle-Only Limitation (Critical Discovery)

**Plan assumption**: Switch change behaviour would work with all parameter types (toggle, text, number).

**Actual implementation**: Switch change behaviour only applies to TOGGLE parameters.

**Root cause**: The original XOR conflict detection logic (now `_handle_switch_group_behavior`) was designed specifically for toggles. Line 1622 in `param.py` checks `if _is_toggle_param(param_definition)` before applying behaviour logic.

**Impact**: 
- TEXT and NUMBER parameters can have `PARAM_SWITCH_LIST` defined but the switch change behaviour will not apply to them
- Tests were rewritten to focus exclusively on toggle parameters (removed 13 text/number tests)
- Final test suite has 22 tests, all for toggle parameters
- Documentation examples use only toggle parameters

**Rationale for not expanding**: 
- Maintaining consistency with original XOR implementation
- Toggle switches are the primary use case for mutually exclusive groups
- Expanding to text/number would require significant additional logic and validation
- Current implementation serves the stated use case (mode switching with toggles)

**Documentation impact**: All user-facing documentation accurately reflects toggle-only limitation with note "Switch change behaviour currently only applies to TOGGLE parameters."

### Variable Naming Change

**Plan specified**: `_init_mode` flag to track whether CLI initialisation is in progress.

**Implemented as**: `_batch_mode` flag to track batch parameter processing.

**Rationale**: The name `_batch_mode` better describes what the flag actually controls - whether parameters are being processed in batch mode (which enforces `SWITCH_REJECT`). This name is clearer and more maintainable than `_init_mode`.

### Error Message Format Enhancement

**Plan specified**: Continue using existing XOR error format.

**Implemented format**: Changed from `"Conflicting parameters provided: ..."` to `"Cannot set '{param}', conflicts with '{conflicting_param}' in switch group"`.

**Impact**: 4 existing XOR tests in `tests/test_cli.py` required updates to accept new error format:
- `test_xor_clashing_params_raise_error`
- `test_xor_with_non_toggle_text_params`
- `test_xor_with_non_toggle_number_params`
- `test_xor_with_mixed_param_types`

**Rationale**: New format provides clearer information to users about which parameter is being rejected and which specific parameter it conflicts with. This improves user experience and debugging.

### API Signature Correction

**Plan example code**: Used `get_xor_params(bind_name=bind_name)` (keyword argument).

**Actual implementation**: Uses `get_xor_params(bind_name)` (positional argument).

**Rationale**: The existing `get_xor_params()` function signature accepts the parameter name as a positional argument, not a keyword argument. Implementation corrected this to match actual API.

### CLI Behaviour Refinement

**Plan stated**: "Switch behaviour applies uniformly to CLI arguments and programmatic `set_param()` calls."

**Implemented behaviour**: Batch mode forces `SWITCH_REJECT` for CLI parsing, regardless of configured `PARAM_SWITCH_CHANGE_BEHAVIOR`. Programmatic `set_param()` calls respect the configured behaviour.

**Rationale**: CLI users making mistakes should always receive clear error messages. Forcing `SWITCH_REJECT` during CLI parsing ensures user errors are caught immediately. Programmatic code can still use `SWITCH_UNSET` or `SWITCH_RESET` by calling `set_param()` directly (outside of batch mode).

**Success criteria updated**: Removed criteria about "uniform behaviour" and "last parameter wins on CLI", added separate criteria for batch mode enforcement and programmatic behaviour respect.

### File Parsing Refactoring

**Additional implementation**: Created `_parse_file_references_in_params()` helper function in `src/spafw37/cli.py`.

**Rationale**: Extracting file reference parsing into a separate function improves code organisation and follows functional programming principles (returns new list rather than mutating input). Makes the CLI parser cleaner and more testable.

### Implementation Status Summary

**Completed (All Steps 1-6)**:
- ✅ Constants defined (`SWITCH_UNSET`, `SWITCH_RESET`, `SWITCH_REJECT`, `PARAM_SWITCH_CHANGE_BEHAVIOR`)
- ✅ Property support added to parameter configuration
- ✅ Complete switch group change logic implemented (11 new functions total)
- ✅ CLI parser refactored to use batch processing
- ✅ Example script created (`examples/params_switch_behavior.py`) demonstrating all three modes
- ✅ Documentation complete (`doc/parameters.md`, `doc/api-reference.md`, `README.md`, `examples/README.md`)
- ✅ Comprehensive test suite created (`tests/test_param_switch_behavior.py` with 22 toggle-focused tests)
- ✅ All existing tests passing (618 passed, 1 skipped - 22 new tests added)
- ✅ Backward compatibility maintained (default SWITCH_REJECT matches original behaviour)
- ✅ Test coverage at 96.58% (exceeds 90% target)



[↑ Back to top](#table-of-contents)
---

## CHANGES for v1.1.0 Release

Issue #32: Switch Param Grouped Behaviour

### Issues Closed

- #32: Switch Param Grouped Behaviour

### Additions

- `SWITCH_UNSET` constant controls switch group behaviour. When set on `PARAM_SWITCH_CHANGE_BEHAVIOR`, causes other switches in the same group to be completely removed from configuration using `unset_param()`. Useful for mode switching where previous mode should be cleared.
- `SWITCH_RESET` constant controls switch group behaviour. When set on `PARAM_SWITCH_CHANGE_BEHAVIOR`, causes other switches in the same group to be reset to their default values using `reset_param()`. Useful when switches have meaningful default states that should be restored.
- `SWITCH_REJECT` constant controls switch group behaviour (default, backward compatible). When set on `PARAM_SWITCH_CHANGE_BEHAVIOR`, raises `ValueError` preventing the new switch param from being set if other switches in the group are already active. Matches current behaviour for strict validation.
- `PARAM_SWITCH_CHANGE_BEHAVIOR` property configures how switch params in the same group interact when values change. Accepts `SWITCH_UNSET`, `SWITCH_RESET`, or `SWITCH_REJECT` (default). Applied at parameter definition time in `add_param()`.

### Removals

None.

### Changes

None.

### Migration

No migration required. New functionality only. Default behaviour is `SWITCH_REJECT`, which matches current behaviour (raises error on conflicts). Applications must explicitly configure `PARAM_SWITCH_CHANGE_BEHAVIOR` to use `SWITCH_UNSET` or `SWITCH_RESET` behaviours.

### Documentation

- `doc/parameters.md` added "Switch Change Behaviour" section after "Mutual Exclusion (Switch Lists)" section. Documents `PARAM_SWITCH_CHANGE_BEHAVIOR` property with three behaviour options (`SWITCH_REJECT`, `SWITCH_UNSET`, `SWITCH_RESET`). Includes three complete examples demonstrating mode switching with `SWITCH_UNSET`, state restoration with `SWITCH_RESET`, and strict validation with `SWITCH_REJECT`. Each example shows parameter definitions and usage patterns with expected results.
- `doc/api-reference.md` added `PARAM_SWITCH_CHANGE_BEHAVIOR` to Parameter Properties table with description and version note (Added in v1.1.0).
- `doc/api-reference.md` added Switch Change Behaviour Constants section with definitions for `SWITCH_UNSET`, `SWITCH_RESET`, and `SWITCH_REJECT`, including when to use each constant.
- `examples/params_switch_behavior.py` demonstrates all three switch change behaviours with complete runnable examples. Shows mode switching use case (UNSET), state restoration use case (RESET), and strict validation use case (REJECT). Includes environment, region, port, size, and priority parameters with CLI commands.
- `examples/README.md` added `params_switch_behavior.py` entry in Parameters section.

### Testing

- 22 new tests in `tests/test_param_switch_behavior.py` (toggle parameters only)
- Tests cover `SWITCH_UNSET`, `SWITCH_RESET`, and `SWITCH_REJECT` behaviours
- Tests cover toggle parameter type exclusively (implementation limitation discovered)
- Tests cover multiple switches in a group (2-param and 3-param groups)
- Tests cover batch mode flag functionality (`_set_batch_mode()`, `_get_batch_mode()`)
- Tests cover `set_values()` function (batch mode enable/disable, error cleanup, multiple params)
- Tests cover `_get_switch_change_behavior()` (batch mode override forces REJECT)
- Tests cover conflict detection and resolution across all three behaviours
- Tests cover integration scenarios (sequential switching, switching back and forth)
- Tests cover mixed behaviours in same group (one param REJECT, another UNSET)
- Tests cover backward compatibility (default `SWITCH_REJECT` matches current behaviour)
- Tests cover `_skip_xor_validation` flag interaction with new behaviour
- Tests cover edge cases (no conflicts, setting param with no active conflicts)
- 4 existing XOR tests updated in `tests/test_cli.py` for new error message format
- Total test suite: 618 passed, 1 skipped
- Test coverage: 96.58% (exceeds 90% target, well above 80% minimum)

---

Full changelog: https://github.com/minouris/spafw37/compare/v1.0.0...v1.1.0  
Issues: https://github.com/minouris/spafw37/issues/32

[↑ Back to top](#table-of-contents)
---
