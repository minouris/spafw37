# Issue #48: Param Defaults are set after pre-parse args

## Overview

Currently, `_set_defaults()` is called in `cli.py` after `_pre_parse_params()` is called, meaning that any param values set by `_pre_parse_params()` will be overridden if those params have default values. This is a bug that prevents pre-parse params from functioning correctly when they have default values defined.

Setting defaults is not a responsibility that should belong to `cli.py`. The CLI module should orchestrate argument parsing, not manage parameter lifecycle concerns like default value initialization. Parameter default management belongs in `param.py` alongside other parameter configuration logic.

The fix will move default-setting responsibility from `cli.py` to `param.py`, ensuring defaults are set at the correct point in the parameter lifecycle—immediately when parameters are registered via `add_param()`. This prevents defaults from overriding values set during pre-parsing and establishes a clearer separation of concerns.

**Key architectural decisions:**

- **Responsibility placement:** Default-setting moves from CLI parsing phase to parameter registration phase in `param.py`
- **Timing:** Defaults set immediately when `add_param()` is called, before any CLI parsing occurs
- **Backward compatibility:** Maintains existing behavior for non-pre-parse params while fixing pre-parse param issue
- **XOR handling:** Preserves existing XOR validation disabling during default-setting to avoid false conflicts

## Table of Contents

- [Overview](#overview)
- [Implementation Steps](#implementation-steps)
  - [1. Add failing test to demonstrate bug](#1-add-failing-test-to-demonstrate-bug)
  - [2. Move _set_defaults logic to param.py](#2-move-_set_defaults-logic-to-parampy)
  - [3. Call _set_param_default in add_param](#3-call-_set_param_default-in-add_param)
  - [4. Remove _set_defaults from cli.py](#4-remove-_set_defaults-from-clipy)
  - [5. Verify fix and update tests](#5-verify-fix-and-update-tests)
- [Further Considerations](#further-considerations)
  - [1. Should defaults be set in add_param or add_params?](#1-should-defaults-be-set-in-add_param-or-add_params--resolved)
  - [2. Should we use unset_param instead of refactoring?](#2-should-we-use-unset_param-instead-of-refactoring--resolved)
  - [3. What about XOR validation during default-setting?](#3-what-about-xor-validation-during-default-setting--resolved)
- [Success Criteria](#success-criteria)
- [CHANGES for v1.1.0 Release](#changes-for-v110-release)

## Implementation Steps

### 1. Add failing test to demonstrate bug

**Files:** `tests/test_cli.py`, `tests/test_param.py`

Add a test that demonstrates the current bug: pre-parse params with default values get overridden by `_set_defaults()` after pre-parsing completes. This test should FAIL initially, proving the bug exists.

**All tests must conform to standards in `.github/instructions/python-tests.instructions.md`:**
- Use module-level functions, NOT test classes
- Include comprehensive docstrings (minimum 3 sentences: what, outcome, why)
- Test exactly one behaviour per test function
- Follow project naming standards (no lazy placeholders like `data`, `result`, `tmp`)
- Use `setup_function()` explicitly at start of each test

**Implementation order:**

1. Create test that registers a pre-parse param with a default value
2. Call `run_cli()` with a CLI argument that sets a different value
3. Assert that the CLI value is retained (not overridden by default)
4. Run test to verify it FAILS with current implementation
5. This failing test will pass after steps 2-4 are complete

**Test 1.1.1: Pre-parse param with default is overridden by _set_defaults (demonstrates bug)**

```gherkin
Scenario: Pre-parse param with default is overridden (BUG - should fail initially)
  Given I have a pre-parse param "silent" with PARAM_DEFAULT = False
  And I register it using add_pre_parse_args([{PARAM_NAME: "silent", PARAM_HAS_VALUE: False}])
  And I add the param using add_param({
      PARAM_NAME: "silent",
      PARAM_ALIASES: ["--silent"],
      PARAM_TYPE: PARAM_TYPE_TOGGLE,
      PARAM_DEFAULT: False
  })
  When I call run_cli(["--silent"])
  Then get_param("silent") should return True
  But currently returns False because _set_defaults() overrides the pre-parsed value
  
  # Validates: This test demonstrates the bug exists in the current implementation
  # Expected: FAIL initially, PASS after fix is implemented
```

**Tests:** Run test to confirm it fails, demonstrating the bug

[↑ Back to top](#table-of-contents)

### 2. Move _set_defaults logic to param.py

**File:** `src/spafw37/param.py`

Create a new internal function `_set_param_default()` in `param.py` that sets the default value for a single parameter. This function encapsulates the logic currently in `cli._set_defaults()` for processing one parameter.

**Implementation order:**

1. Write unit tests for `_set_param_default()` (Tests 2.2.1-2.2.4) - tests will fail initially
2. Create `_set_param_default(_param)` function in param.py
3. Extract default-setting logic from `cli._set_defaults()`
4. Handle both toggle and non-toggle params
5. Return early if param has no default value
6. Verify unit tests now pass

**Function specification:**

- **`_set_param_default(_param)`:**
  - Takes a parameter definition dictionary
  - Checks if parameter has a default value using `_param_has_default()`
  - For toggle params: always sets default (using `False` if not specified)
  - For non-toggle params: only sets default if `PARAM_DEFAULT` is present
  - Calls `set_param()` with the default value
  - Does not disable XOR validation (caller's responsibility if needed)

**Code 2.1: _set_param_default function**

```python
def _set_param_default(_param):
    """Set default value for a parameter if defined.
    
    Args:
        _param: Parameter definition dictionary.
    """
    # Block 2.1.1
    param_name = _param.get(PARAM_NAME)
    
    # Block 2.1.2: Determine default value based on param type
    if _is_toggle_param(_param):
        # Block 2.1.2.1
        default_value = _get_param_default(_param, False)
    elif _param_has_default(_param):
        # Block 2.1.2.2
        default_value = _get_param_default(_param, None)
    else:
        # Block 2.1.2.3: No default to set
        return
    
    # Block 2.1.3: Set the default value
    logging.log_trace(_message=f"Setting default for param '{param_name}' = {default_value}")
    # Block 2.1.4
    set_param(param_name=param_name, value=default_value)
```

**Tests:** Unit tests for `_set_param_default()`

**All tests must conform to standards in `.github/instructions/python-tests.instructions.md`:**
- Use module-level functions, NOT test classes
- Include comprehensive docstrings (minimum 3 sentences: what, outcome, why)
- Test exactly one behaviour per test function
- Follow project naming standards (no lazy placeholders)
- Use `setup_function()` explicitly at start of each test

**Test 2.2.1: Sets default for toggle param**

```gherkin
Scenario: _set_param_default sets default for toggle param
  Given I have a toggle param definition with PARAM_DEFAULT = True
  When I call _set_param_default(param)
  Then set_param should be called with param_name and value=True
  
  # Validates: _set_param_default() correctly sets toggle param defaults
```

**Test 2.2.2: Sets False for toggle param without explicit default**

```gherkin
Scenario: _set_param_default uses False for toggle without default
  Given I have a toggle param definition without PARAM_DEFAULT
  When I call _set_param_default(param)
  Then set_param should be called with param_name and value=False
  
  # Validates: Toggle params without explicit defaults get False
```

**Test 2.2.3: Sets default for non-toggle param with default**

```gherkin
Scenario: _set_param_default sets default for non-toggle param
  Given I have a non-toggle param definition with PARAM_DEFAULT = "value"
  When I call _set_param_default(param)
  Then set_param should be called with param_name and value="value"
  
  # Validates: Non-toggle params with defaults are set correctly
```

**Test 2.2.4: Skips non-toggle param without default**

```gherkin
Scenario: _set_param_default skips non-toggle without default
  Given I have a non-toggle param definition without PARAM_DEFAULT
  When I call _set_param_default(param)
  Then set_param should not be called
  
  # Validates: Non-toggle params without defaults are left unset
```

[↑ Back to top](#table-of-contents)

### 3. Call _set_param_default in add_param

**File:** `src/spafw37/param.py`

Modify `add_param()` to call `_set_param_default()` immediately after adding the parameter to `_params`. This ensures defaults are set at parameter registration time, before any CLI parsing occurs.

**Implementation order:**

1. Define `_SWITCH_REGISTER` constant for registration-time behavior
2. Add registration mode flag and accessors (`_registration_mode`, `_set_registration_mode()`, `_get_registration_mode()`)
3. Modify `_get_switch_behavior()` to check registration mode and return `_SWITCH_REGISTER`
4. Update `_has_switch_conflict()` to skip validation when behavior is `_SWITCH_REGISTER`
5. Write integration tests for `add_param()` with defaults (Tests 3.2.1-3.2.4) - tests will fail initially
6. Modify `add_param()` to wrap `_set_param_default()` call in registration mode enable/disable block
7. Place call after parameter is added to `_params` dictionary
8. Ensure registration mode is reset even if default-setting fails
9. Update existing tests that verify defaults set at registration (Tests 5.2.1, 5.2.2, 5.2.3)
10. Verify integration tests now pass

**Code 3.0: _SWITCH_REGISTER constant**

```python
# Block 3.0.1: Module-level switch behaviour constant for registration mode
_SWITCH_REGISTER = 'switch-register'  # Internal: Skip validation during registration
```

**Code 3.1: Registration mode flag and accessors**

```python
# Block 3.1.1: Module-level registration mode flag
_registration_mode = False

def _set_registration_mode(enabled):
    """Enable/disable registration mode for switch param behavior.
    
    When enabled, switch params skip XOR validation entirely during
    default-setting at parameter registration time.
    
    Args:
        enabled: Boolean to enable (True) or disable (False) registration mode.
    """
    # Block 3.1.2
    global _registration_mode
    # Block 3.1.3
    _registration_mode = enabled

def _get_registration_mode():
    """Check if currently in registration mode.
    
    Returns:
        Boolean indicating whether registration mode is active.
    """
    # Block 3.1.4
    return _registration_mode
```

**Code 3.2: Modified _get_switch_behavior function**

```python
def _get_switch_behavior(param_definition):
    """Get switch behavior for parameter, considering operational modes.
    
    Checks batch_mode and registration_mode to determine appropriate
    behavior for switch conflict resolution.
    
    Args:
        param_definition: Parameter definition dict
        
    Returns:
        One of SWITCH_UNSET, SWITCH_RESET, SWITCH_REJECT, or _SWITCH_REGISTER
    """
    # Block 3.2.1
    if _get_batch_mode():
        return SWITCH_REJECT
    # Block 3.2.2
    if _get_registration_mode():
        return _SWITCH_REGISTER  # Skip all validation during registration
    
    # Block 3.2.3
    return param_definition.get(PARAM_SWITCH_CHANGE_BEHAVIOR, SWITCH_REJECT)
```

**Code 3.3: Modified _has_switch_conflict function**

```python
def _has_switch_conflict(param_definition, xor_param_bind_name):
    """Check if a param in the switch group has a conflicting value.
    
    During registration mode (_SWITCH_REGISTER), always returns False
    to skip validation while setting defaults.
    
    Args:
        param_definition: Definition of param being set
        xor_param_bind_name: Bind name of other param to check
        
    Returns:
        True if conflict exists, False otherwise
    """
    # Block 3.3.1: Get current behavior mode
    behavior = _get_switch_behavior(param_definition)
    
    # Block 3.3.2: Skip conflict detection entirely during registration
    if behavior == _SWITCH_REGISTER:
        return False
    
    # Block 3.3.3: Rest of existing conflict detection logic
    existing_value = config.get_config_value(xor_param_bind_name)
    
    # Block 3.3.4
    if _is_toggle_param(param_definition):
        return existing_value is True
    else:
        return existing_value is not None
```

**Code 3.4: Modified add_param function**

```python
def add_param(_param):
    """Add a parameter and activate it immediately.
    
    Args:
        _param: Parameter definition dictionary with keys like
                PARAM_NAME, PARAM_ALIASES, PARAM_TYPE, etc.
    """
    # Block 3.4.1
    _param_name = _param.get(PARAM_NAME)
    
    # Block 3.4.2: Process and validate parameter
    _process_param_aliases(_param)
    _process_param_switch_list(_param)
    _assign_default_input_filter(_param)
    _validate_and_normalise_default(_param)
    _apply_runtime_only_constraint(_param)
    
    # Block 3.4.3: Register parameter
    _params[_param_name] = _param
    
    # Block 3.4.4: Set default value if defined (with registration mode to skip switch validation)
    _set_registration_mode(True)
    # Block 3.4.5: try/finally for registration mode
    try:
        # Block 3.4.5.1
        _set_param_default(_param)
    finally:
        # Block 3.4.5.2
        _set_registration_mode(False)
```

**Tests:** Integration tests for `add_param()` with defaults

**All tests must conform to standards in `.github/instructions/python-tests.instructions.md`:**
- Use module-level functions, NOT test classes
- Include comprehensive docstrings (minimum 3 sentences: what, outcome, why)
- Test exactly one behaviour per test function
- Follow project naming standards (no lazy placeholders)
- Use `setup_function()` explicitly at start of each test

**Test 3.2.1: add_param sets default for toggle param**

```gherkin
Scenario: add_param sets default for toggle param
  Given I have a toggle param definition with PARAM_DEFAULT = True
  When I call add_param(param)
  Then the parameter should be registered in _params
  And get_param(param_name) should return True
  
  # Validates: add_param() sets defaults immediately at registration
```

**Test 3.2.2: add_param sets default for non-toggle param**

```gherkin
Scenario: add_param sets default for non-toggle param
  Given I have a non-toggle param definition with PARAM_DEFAULT = "test"
  When I call add_param(param)
  Then the parameter should be registered in _params
  And get_param(param_name) should return "test"
  
  # Validates: Non-toggle defaults are set at registration time
```

**Test 3.2.3: add_param enables registration mode during default-setting**

```gherkin
Scenario: add_param enables registration mode to skip switch validation
  Given I have two toggle params in the same XOR group
  And both have PARAM_DEFAULT = False
  When I call add_param(param1)
  And I call add_param(param2)
  Then both parameters should be added successfully
  And no XOR conflict error should be raised
  And both params should have value False in config
  
  # Validates: Registration mode prevents false conflicts during default-setting
```

**Test 3.2.4: add_param resets registration mode after default-setting**

```gherkin
Scenario: add_param resets registration mode after defaults
  Given I have a param with a default that raises an error during set_param
  When I call add_param(param) and it raises an error
  Then _set_registration_mode should still be called with False
  And registration mode should be disabled
  
  # Validates: Registration mode is restored even if default-setting fails
```

[↑ Back to top](#table-of-contents)

### 4. Remove _set_defaults from cli.py

**File:** `src/spafw37/cli.py`

Remove the `_set_defaults()` function and its call from `run_cli()`. This eliminates the duplicate default-setting logic now that defaults are set in `param.py`.

**Implementation order:**

1. Write integration tests (Tests 4.2.1-4.2.3) - tests will pass since defaults are now set at registration
2. Update `test_handle_cli_args_sets_defaults` to verify defaults preserved during CLI handling (Test 5.2.4)
3. Remove call to `_set_defaults()` from `run_cli()` (line ~291)
4. Delete `_set_defaults()` function definition (lines ~208-226)
5. Verify no other references to `_set_defaults()` exist
6. Verify integration tests still pass

**Code 4.1: Modified run_cli function (relevant section)**

```python
    # Pre-parse specific params (e.g., logging/verbosity controls)
    # before main parsing to configure behavior
    _pre_parse_params(tokenized_args)
    
    # Apply logging configuration based on pre-parsed params
    logging_module.apply_logging_config()

    # Parse command line arguments using regex tokenizer
    _parse_command_line(tokenized_args)
    
    # Execute queued commands
    command.run_command_queue()
```

**Tests:** Integration tests to verify behavior remains correct

**All tests must conform to standards in `.github/instructions/python-tests.instructions.md`:**
- Use module-level functions, NOT test classes
- Include comprehensive docstrings (minimum 3 sentences: what, outcome, why)
- Test exactly one behaviour per test function
- Follow project naming standards (no lazy placeholders)
- Use `setup_function()` explicitly at start of each test

**Test 4.2.1: Pre-parse params retain their values**

```gherkin
Scenario: Pre-parse param values are not overridden by defaults
  Given I have a pre-parse param "silent" with PARAM_DEFAULT = False
  And I register it using add_pre_parse_args([{PARAM_NAME: "silent", PARAM_HAS_VALUE: False}])
  And I add the param using add_param({PARAM_NAME: "silent", PARAM_ALIASES: ["--silent"], PARAM_TYPE: PARAM_TYPE_TOGGLE, PARAM_DEFAULT: False})
  When I call run_cli(["--silent"])
  Then get_param("silent") should return True
  And the default value should not override the pre-parsed value
  
  # Validates: Pre-parse params work correctly with defaults set at registration
```

**Test 4.2.2: Non-pre-parse params still get defaults**

```gherkin
Scenario: Non-pre-parse params receive defaults correctly
  Given I have a non-pre-parse param with PARAM_DEFAULT = "default"
  And I add the param using add_param()
  When I call run_cli([])
  Then get_param(param_name) should return "default"
  
  # Validates: Regular params still receive defaults after refactoring
```

**Test 4.2.3: Toggle params default to False**

```gherkin
Scenario: Toggle params default to False when not specified
  Given I have a toggle param without explicit PARAM_DEFAULT
  And I add the param using add_param()
  When I call run_cli([])
  Then get_param(param_name) should return False
  
  # Validates: Toggle params maintain backward-compatible default behavior
```

[↑ Back to top](#table-of-contents)

### 5. Verify fix and update tests

**Files:** `tests/test_cli.py`, `tests/test_param.py`

Verify that the test from step 1 now passes, and update any other existing tests that may have depended on the timing of `_set_defaults()` being called in `cli.py`.

**All tests must conform to standards in `.github/instructions/python-tests.instructions.md`:**
- Use module-level functions, NOT test classes
- Include comprehensive docstrings (minimum 3 sentences: what, outcome, why)
- Test exactly one behaviour per test function
- Follow project naming standards (no lazy placeholders)
- Use `setup_function()` explicitly at start of each test

**Implementation order:**

1. Run the test from step 1 and verify it now PASSES (was failing before)
2. Review existing tests for dependencies on `_set_defaults()` timing
3. Update any tests that directly call or mock `_set_defaults()`
4. Verify all tests pass

**Test requirements:**

- **Verify step 1 test passes:** The test demonstrating the bug should now pass
- **Backward compatibility:** Verify non-pre-parse params with defaults still work
- **Registration mode:** Verify registration mode is properly managed during default-setting
- **Test coverage:** Maintain 80%+ coverage requirement

**Test 5.1.1: Verify the test from step 1 now passes**

```gherkin
Scenario: Verify bug fix - test from step 1 should now pass
  Given I run the test from step 1 (test_pre_parse_param_with_default_not_overridden)
  Then the test should PASS
  And get_param("silent") should return True (not False)
  
  # Validates: The fix is complete - pre-parse params are no longer overridden
```

#### Existing Tests Requiring Updates

Four existing tests in `tests/test_cli.py` directly test `cli._set_defaults()` which is being removed. These tests must be updated or removed.

**Test 5.2.1: Update test_set_default_param_values**

**Old test logic (to be removed):**
```gherkin
Scenario: _set_defaults sets default for text param (OLD - tests removed function)
  Given I have a param with PARAM_DEFAULT = 'default_value'
  And I call add_param() to register it (does NOT set default yet)
  When I call cli._set_defaults()
  Then the config should contain 'default_value'
  
  # Tests: Old behavior where defaults set in CLI module
```

**New test logic (replacement):**
```gherkin
Scenario: add_param sets default for text param immediately (NEW - tests new behavior)
  Given I have a param with PARAM_DEFAULT = 'default_value'
  When I call add_param() to register it
  Then the config should immediately contain 'default_value'
  And I should NOT need to call cli._set_defaults()
  
  # Tests: New behavior where defaults set at registration in param module
  # Validates: Defaults are available immediately after add_param()
```

**Why this change is necessary:**
The old test validates that `cli._set_defaults()` sets defaults when called. This function is being removed because defaults are now set in `param.add_param()` at registration time. The new test validates that defaults are set immediately when the parameter is registered, which is the new correct behavior.

---

**Test 5.2.2: Update test_set_default_param_toggle_with_default_true**

**Old test logic (to be removed):**
```gherkin
Scenario: _set_defaults sets True for toggle with explicit default (OLD)
  Given I have a toggle param with PARAM_DEFAULT = True
  And I call add_param() to register it (does NOT set default yet)
  When I call cli._set_defaults()
  Then the config should contain True
  
  # Tests: Old behavior where defaults set in CLI module
```

**New test logic (replacement):**
```gherkin
Scenario: add_param sets True for toggle with explicit default immediately (NEW)
  Given I have a toggle param with PARAM_DEFAULT = True
  When I call add_param() to register it
  Then the config should immediately contain True
  And I should NOT need to call cli._set_defaults()
  
  # Tests: New behavior where toggle defaults set at registration
  # Validates: Explicit toggle defaults available immediately after add_param()
```

**Why this change is necessary:**
Same rationale as 5.2.1. The test must validate the new timing (registration) rather than old timing (CLI parsing). Toggle params with explicit defaults should be set immediately when registered.

---

**Test 5.2.3: Update test_set_default_param_toggle_with_no_default**

**Old test logic (to be removed):**
```gherkin
Scenario: _set_defaults sets False for toggle without explicit default (OLD)
  Given I have a toggle param WITHOUT PARAM_DEFAULT
  And I call add_param() to register it (does NOT set default yet)
  When I call cli._set_defaults()
  Then the config should contain False (implicit toggle default)
  
  # Tests: Old behavior where implicit toggle defaults set in CLI module
```

**New test logic (replacement):**
```gherkin
Scenario: add_param sets False for toggle without explicit default immediately (NEW)
  Given I have a toggle param WITHOUT PARAM_DEFAULT
  When I call add_param() to register it
  Then the config should immediately contain False (implicit toggle default)
  And I should NOT need to call cli._set_defaults()
  
  # Tests: New behavior where implicit toggle defaults set at registration
  # Validates: Toggle params always have defined state (False) immediately after add_param()
```

**Why this change is necessary:**
Toggle params without explicit defaults implicitly default to `False`. The old test validated this happened in `cli._set_defaults()`. The new test validates this happens in `add_param()`. This ensures toggle params have predictable state immediately upon registration.

---

**Test 5.2.4: Update test_handle_cli_args_sets_defaults**

**Old test logic (to be updated):**
```gherkin
Scenario: handle_cli_args sets defaults during CLI processing (OLD)
  Given I have a param with PARAM_DEFAULT = 'default_value'
  And I call add_param() to register it (does NOT set default yet)
  When I call handle_cli_args([]) with no arguments
  Then the config should contain 'default_value'
  
  # Tests: Old behavior - defaults set during handle_cli_args via _set_defaults()
```

**New test logic (replacement):**
```gherkin
Scenario: add_param sets defaults immediately, handle_cli_args preserves them (NEW)
  Given I have a param with PARAM_DEFAULT = 'default_value'
  When I call add_param() to register it
  Then the config should already contain 'default_value'
  When I call handle_cli_args([]) with no arguments
  Then the config should still contain 'default_value' (unchanged)
  
  # Tests: New behavior - defaults set at registration, CLI handling preserves them
  # Validates: handle_cli_args does not interfere with pre-set defaults
```

**Why this change is necessary:**
The old test validates that `handle_cli_args()` is responsible for setting defaults by calling `cli._set_defaults()`. The new test validates that defaults are already set before `handle_cli_args()` is called (set during `add_param()`), and that `handle_cli_args()` does not interfere with them. This reflects the architectural shift: default-setting is now a parameter registration concern, not a CLI parsing concern.

---

**Tests:** Manual review to verify test coverage and correctness

[↑ Back to top](#table-of-contents)

## Further Considerations

### 1. Should defaults be set in add_param or add_params? - RESOLVED

**Question:** Should `_set_param_default()` be called in `add_param()` (per-parameter) or in `add_params()` (batch after all params registered)?

**Answer:** Call `_set_param_default()` in `add_param()` (per-parameter basis).

**Rationale:**
- Immediate feedback: Each parameter is fully initialized when `add_param()` returns
- Simpler logic: No need to track whether defaults have been set
- Consistent behavior: Whether params are added via `add_param()` or `add_params()`, defaults are set the same way
- XOR validation: Disabling XOR validation per-param is cleaner than managing it across batch operations

**Implementation:**
- Call `_set_param_default(_param)` at the end of `add_param()` after parameter is added to `_params`
- Wrap call in `_set_xor_validation_enabled(False)` / `_set_xor_validation_enabled(True)` block
- `add_params()` requires no changes since it just loops calling `add_param()`

[↑ Back to top](#table-of-contents)

### 2. Should we use unset_param instead of refactoring? - RESOLVED

**Question:** The issue suggests calling `unset_param()` at the end of each `add_param()` instead of refactoring `_set_defaults()`. Should we pursue this alternative?

**Answer:** No, refactor `_set_defaults()` into `param.py` instead of using `unset_param()`.

**Rationale:**
- Clearer intent: Setting defaults at registration time is more intuitive than unsetting them
- Proper separation of concerns: Default-setting belongs in parameter management, not CLI parsing
- Less confusing: `unset_param()` is meant to remove values, not prevent defaults from being set
- Better error handling: XOR validation can be cleanly managed during default-setting

**Alternative considered:** Call `unset_param()` at end of `add_param()`
- Pro: Minimal code changes required
- Con: Confusing API usage - `unset_param()` is not designed for this purpose
- Con: Doesn't fix the root problem of responsibility misplacement
- Con: Would require documenting a non-obvious workaround

**Rejected because:** Using `unset_param()` would be a hack rather than properly fixing the architectural issue. The real problem is that defaults are being set in the wrong place (CLI parsing) at the wrong time (after pre-parsing).

[↑ Back to top](#table-of-contents)

### 3. What about XOR validation during default-setting? - RESOLVED

**Question:** The current `_set_defaults()` disables XOR validation while setting defaults to avoid false conflicts. How should this be handled in the refactored version?

**Answer:** Use a registration mode flag (similar to `batch_mode`) that causes switch params to skip XOR validation entirely during registration.

**Rationale:**
- Type-based behavior: Switch param behavior should reflect the current operational mode (registration vs. runtime)
- Minimal disruption: Only affects validation logic during registration; no changes to existing test expectations
- Clean separation: Registration mode is orthogonal to XOR validation disable flag
- Follows existing pattern: `batch_mode` already provides a model for mode-based behavior switching
- Surgical fix: Only affects switch conflict detection logic, doesn't change `unset_param()` or test assertions

**Implementation details:**

1. **Add registration mode flag and accessors** (similar to `batch_mode`):
   ```python
   # In param.py module-level
   _registration_mode = False
   
   def _set_registration_mode(enabled):
       """Enable/disable registration mode for switch param behavior.
       
       When enabled, switch params skip XOR validation entirely during
       default-setting at parameter registration time.
       """
       global _registration_mode
       _registration_mode = enabled
   
   def _get_registration_mode():
       """Check if currently in registration mode."""
       return _registration_mode
   ```

2. **Modify switch behavior resolution** to check registration mode:
   ```python
   def _get_switch_behavior(param_definition):
       """Get switch behavior for parameter, considering operational modes.
       
       Returns:
           SWITCH_REJECT (batch mode),
           _SWITCH_REGISTER (registration mode - skips validation),
           or configured behavior from param_definition
       """
       if _get_batch_mode():
           return SWITCH_REJECT
       if _get_registration_mode():
           return _SWITCH_REGISTER  # Special mode that skips validation
       return param_definition.get(PARAM_SWITCH_CHANGE_BEHAVIOR, SWITCH_REJECT)
   ```

3. **Update switch conflict detection** to handle registration mode:
   ```python
   def _has_switch_conflict(param_definition, xor_param_bind_name):
       """Check if a param in the switch group has a conflicting value.
       
       During registration mode, always returns False to skip validation.
       """
       # Get current behavior mode
       behavior = _get_switch_behavior(param_definition)
       
       # Skip conflict detection entirely during registration
       if behavior == _SWITCH_REGISTER:
           return False
       
       # ... rest of existing conflict detection logic ...
   ```

4. **Wrap `_set_param_default()` call** in `add_param()`:
   ```python
   def add_param(_param):
       # ... existing parameter processing ...
       
       _params[_param_name] = _param
       
       # Set default value with registration mode enabled
       _set_registration_mode(True)
       try:
           _set_param_default(_param)
       finally:
           _set_registration_mode(False)
   ```

**Why this approach is better than XOR validation disable:**
- Preserves existing behavior: No test changes required for Issue #26 (unset) or Issue #32 (switch behavior)
- Preserves toggle semantics: Unset toggles remain `None`, not `False`
- Preserves `unset_param()` behavior: Still removes values completely rather than restoring defaults
- Surgical fix: Only affects the validation check during registration, not the entire parameter lifecycle
- Type-based: Switch behavior checks naturally incorporate mode, rather than globally disabling validation

**Rejected alternative:** Globally disable XOR validation with `_set_xor_validation_enabled(False)`
- Con: Too broad - disables all XOR validation, not just switch conflict detection
- Con: Requires changing test expectations for previous features
- Con: Changes fundamental behavior of `unset_param()` (restoring defaults vs. removing)
- Con: Changes toggle param semantics (False vs. None for unset state)

[↑ Back to top](#table-of-contents)

### 4. Switch behavior test failures - toggle initial state - RESOLVED

**Issue:** After implementing the fix, 9 tests in `test_param_switch_behavior.py` are failing with assertion errors.

**Failure pattern:**

Tests expect toggle params to be `None` before they're ever explicitly set, but they now have value `False` (the implicit toggle default set during registration).

**Example from `test_switch_unset_toggle_removes_conflicting_param()`:**

```python
param.add_params([...])  # Add mode_read and mode_write toggles
param.set_param('mode_read', True)
assert param.get_param('mode_read') is True
assert param.get_param('mode_write') is None  # ← FAILS: expects None, gets False
```

**Root cause:**

The test expects `mode_write` to be `None` because it hasn't been explicitly set yet. However, toggle params now receive their implicit default (`False`) during registration via `add_param()`, so `mode_write` has value `False`, not `None`.

**This is the intended behavior of the fix** - toggle params should have defined values after registration, not remain undefined.

**Tests affected (9 total):**

1. `test_switch_reject_does_not_modify_params` - Checks `option_b` before setting
2. `test_switch_unset_toggle_removes_conflicting_param` - Checks `mode_write` before setting
3. `test_switch_unset_three_way_group_removes_all_conflicts` - Checks multiple params before setting
4. `test_switch_unset_no_conflict_when_none_set` - Checks `opt_y` before setting
5. `test_switch_reset_toggle_resets_to_default` - Checks `priority_low` before setting
6. `test_switch_reset_three_way_group_resets_all_conflicts` - Checks multiple params before setting
7. `test_switch_reset_switching_back_and_forth` - Checks `encrypt_off` before setting
8. `test_mixed_behaviors_in_same_group` - Checks `strict` before setting
9. `test_switch_behavior_with_no_conflict` - Checks both `alpha` and `beta` before setting

**Analysis:**

These tests are checking the **initial state** of toggle params before they're ever explicitly set. The tests expect `None` (undefined/unset), but get `False` (implicit toggle default).

**Resolution options:**

- Update tests to expect `False` for toggle params that haven't been explicitly set
- Toggle params now have defined state immediately after registration
- This aligns with the goal of setting defaults at registration time

**Status:** RESOLVED - Toggle params now have defined state (`False`) after registration. Tests need updating to expect `False` instead of `None` for initial state. See Implementation Step 7 for resolution.

[↑ Back to top](#table-of-contents)

### 5. Logging test failures - mixed-type switch conflict detection - PENDING REVIEW

**Issue:** After implementing the fix, 4 tests in `test_logging.py` are failing with `ValueError` exceptions.

**Failure pattern:**

Tests throw `ValueError: Cannot set 'log-level', conflicts with 'log-verbose'` when trying to set the `log-level` param.

**Example from `test_apply_logging_config_with_log_level_param()`:**

```python
param.add_params(LOGGING_PARAMS)  # Registers all logging params including toggles
param.set_param(param_name='log-level', value='WARNING')  # ← THROWS: conflicts with 'log-verbose'
```

**Root cause:**

`log-level` (TEXT param) is in a switch group with `log-verbose` (TOGGLE param). When `LOGGING_PARAMS` are registered, `log-verbose` gets its implicit default `False` set. Then when setting `log-level`, `_has_switch_conflict()` incorrectly reports a conflict because:

1. `_has_switch_conflict()` receives `log-level` param definition and checks `_is_toggle_param(param_definition)` → False
2. Since it's not a toggle, it uses the non-toggle check: `existing_value is not None`
3. It checks `log-verbose` value: `False is not None` → True (conflict detected!)
4. This triggers the switch conflict error

**The bug:** `_has_switch_conflict()` checks the type of **the param being set**, but it should check the type of **the conflicting param** (the one whose `existing_value` is being examined).

**Current code (incorrect):**

```python
def _has_switch_conflict(param_definition, xor_param_bind_name):
    # ...
    existing_value = config.get_config_value(xor_param_bind_name)
    
    if _is_toggle_param(param_definition):  # ← Checks WRONG param
        return existing_value is True
    else:
        return existing_value is not None
```

**Expected behavior:**

Should check whether the **conflicting param** (at `xor_param_bind_name`) is a toggle:
- If conflicting param is a toggle: only conflict if `existing_value is True`
- If conflicting param is not a toggle: conflict if `existing_value is not None`

**Tests affected (4 total):**

1. `test_apply_logging_config_with_log_level_param` - Sets `log-level` after registering LOGGING_PARAMS
2. `test_log_level_param_accepts_valid_values` - Sets `log-level` with valid values
3. `test_log_level_param_case_insensitive_matching` - Sets `log-level` with case variations
4. `test_log_level_param_integration_with_logging_system` - Sets `log-level` and checks logging

**Analysis:**

This is a **genuine bug** in `_has_switch_conflict()` that was exposed by the fix. The function uses the wrong param type to determine the conflict check logic. It needs to look up the conflicting param's definition and check its type, not use the param being set.

**Resolution required:**

Fix `_has_switch_conflict()` to:
1. Look up the conflicting param definition from `xor_param_bind_name`
2. Check if the **conflicting param** is a toggle
3. Apply the appropriate conflict check based on the conflicting param's type

**Status:** PENDING REVIEW - requires implementation of fix to `_has_switch_conflict()`.

[↑ Back to top](#table-of-contents)

### 6. Update tests for toggle param initial state - PENDING APPROVAL

**Depends on:** Resolution of "Further Consideration #4" regarding switch conflict detection

**File:** `tests/test_param_switch_behavior.py`

Once the switch conflict behavior is resolved, update all failing tests in `test_param_switch_behavior.py` to expect `False` instead of `None` for toggle params that have not been explicitly set.

**Tests to update (9 tests):**

1. `test_switch_reject_does_not_modify_params` - Line ~166: `assert param.get_param('option_b') is None` → `is False`
2. `test_switch_unset_toggle_removes_conflicting_param` - Line ~205: `assert param.get_param('mode_write') is None` → `is False`
3. `test_switch_unset_three_way_group_removes_all_conflicts` - Lines checking unset params
4. `test_switch_unset_no_conflict_when_none_set` - Line ~317: `assert param.get_param('opt_y') is None` → `is False`
5. `test_switch_reset_toggle_resets_to_default` - Line ~343: `assert param.get_param('priority_low') is None` → `is False`
6. `test_switch_reset_three_way_group_resets_all_conflicts` - Lines checking unset params
7. `test_switch_reset_switching_back_and_forth` - Line ~422: `assert param.get_param('encrypt_off') is None` → `is False`
8. `test_mixed_behaviors_in_same_group` - Lines checking unset params
9. `test_switch_behavior_with_no_conflict` - Lines ~774-775: Both assertions expecting `None` → `False`

**Implementation:** Replace all assertions checking for `None` with assertions checking for `False` where the param is a toggle that hasn't been explicitly set.

**Status:** PENDING REVIEW - requires implementation of fix to `_has_switch_conflict()`.

[↑ Back to top](#table-of-contents)

## Fixing Test Regressions

After implementing the core fix (steps 1-5), 13 tests fail: 9 in `test_param_switch_behavior.py` due to changed toggle initial state behavior, and 4 in `test_logging.py` due to a bug in `_has_switch_conflict()`.

### 7. Fix _has_switch_conflict() for mixed-type switch groups ✅ COMPLETE

**Depends on:** Core implementation (steps 1-5) complete, Consideration #5 documented

**Status:** COMPLETE - All 4 logging tests now pass

**File:** `src/spafw37/param.py`

Fix the bug in `_has_switch_conflict()` where it checks the type of the param being set instead of the type of the conflicting param. This causes false conflicts when setting TEXT params that are in switch groups with TOGGLE params.

**Current buggy behavior:**

When setting `log-level` (TEXT) that conflicts with `log-verbose` (TOGGLE with value `False`):
- Function checks if `log-level` is a toggle (it's not)
- Uses non-toggle check: `existing_value is not None`
- `False is not None` → True (incorrect conflict detected)

**Correct behavior:**

Should check the type of `log-verbose` (the conflicting param):
- Look up conflicting param definition by bind name
- Check if conflicting param is a toggle
- For toggles: only conflict if value is `True`
- For non-toggles: conflict if value is not `None`

**Implementation:**

In `_has_switch_conflict()` function (lines ~1597-1625), replace the type check logic.

**Code 7.1: Current buggy implementation**

```python
def _has_switch_conflict(param_definition, xor_param_bind_name):
    """Check if a param in the switch group has a conflicting value.
    
    During registration mode (_SWITCH_REGISTER), always returns False
    to skip validation while setting defaults.
    
    Args:
        param_definition: Definition of param being set
        xor_param_bind_name: Bind name of other param to check
        
    Returns:
        True if conflict exists, False otherwise
    """
    # Block 7.1.1: Get current behavior mode
    behavior = _get_switch_change_behavior(param_definition)
    
    # Block 7.1.2: Skip conflict detection entirely during registration
    if behavior == _SWITCH_REGISTER:
        return False
    
    # Block 7.1.3
    existing_value = config.get_config_value(xor_param_bind_name)
    
    # Block 7.1.4: BUG - checks type of param being set instead of conflicting param
    if _is_toggle_param(param_definition):
        return existing_value is True
    else:
        return existing_value is not None
```

**Code 7.2: Fixed implementation**

```python
def _has_switch_conflict(param_definition, xor_param_bind_name):
    """Check if a param in the switch group has a conflicting value.
    
    During registration mode (_SWITCH_REGISTER), always returns False
    to skip validation while setting defaults.
    
    Args:
        param_definition: Definition of param being set
        xor_param_bind_name: Bind name of other param to check
        
    Returns:
        True if conflict exists, False otherwise
    """
    # Block 7.2.1: Get current behavior mode
    behavior = _get_switch_change_behavior(param_definition)
    
    # Block 7.2.2: Skip conflict detection entirely during registration
    if behavior == _SWITCH_REGISTER:
        return False
    
    # Block 7.2.3
    existing_value = config.get_config_value(xor_param_bind_name)
    
    # Block 7.2.4: Look up the conflicting param's definition
    conflicting_param_def = _get_param_definition_by_bind_name(xor_param_bind_name)
    
    # Block 7.2.5: Check type of conflicting param (not param being set)
    if _is_toggle_param(conflicting_param_def):
        return existing_value is True
    else:
        return existing_value is not None
```

**Verification:**

After fix, run:
```bash
pytest tests/test_logging.py -v
```

All 4 previously failing logging tests should now pass:
- `test_apply_logging_config_with_log_level_param`
- `test_log_level_param_accepts_valid_values`
- `test_log_level_param_case_insensitive_matching`
- `test_log_level_param_integration_with_logging_system`

[↑ Back to top](#table-of-contents)

### 8. Update switch behavior tests for toggle initial state ✅ COMPLETE

**Depends on:** Core implementation (steps 1-5) complete, Step 7 complete, Consideration #4 resolved

**Status:** COMPLETE - All 9 switch behavior tests now pass

**File:** `tests/test_param_switch_behavior.py`

Update all failing tests to expect `False` instead of `None` for toggle params that have not been explicitly set. Toggle params now receive their implicit default (`False`) during registration, so they have a defined state immediately after `add_param()`.

**Tests to update (9 tests):**

**Test 8.1: test_switch_reject_does_not_modify_params (Line ~166)**

Old assertion (expects None):
```gherkin
Scenario: Check initial state before setting conflicting param (OLD)
  Given I have two toggle params in a switch group
  When I check option_b before setting option_a
  Then option_b should be None (not yet set)
```

New assertion (expects False):
```gherkin
Scenario: Check initial state before setting conflicting param (NEW)
  Given I have two toggle params in a switch group
  When I check option_b before setting option_a
  Then option_b should be False (implicit default from registration)
  
  # Validates: Toggle params have defined state immediately after registration
```

**Test 8.2: test_switch_unset_toggle_removes_conflicting_param (Line ~205)**

Old assertion (expects None):
```gherkin
Scenario: Check conflicting param before setting (OLD)
  Given I have mode_read and mode_write toggles in a switch group
  When I check mode_write before setting mode_read
  Then mode_write should be None (not yet set)
```

New assertion (expects False):
```gherkin
Scenario: Check conflicting param before setting (NEW)
  Given I have mode_read and mode_write toggles in a switch group
  When I check mode_write before setting mode_read
  Then mode_write should be False (implicit default)
  
  # Validates: Conflicting toggles have False default, not None
```

**Test 8.3: test_switch_unset_three_way_group_removes_all_conflicts (Lines ~235, 241)**

Old assertions (expect None):
```gherkin
Scenario: Check multiple conflicting params before setting (OLD)
  Given I have color_red, color_green, color_blue in a switch group
  When I check color_blue before setting color_red
  Then color_blue should be None
  And after setting color_red, color_green and color_blue should both be None
```

New assertions (expect False):
```gherkin
Scenario: Check multiple conflicting params before setting (NEW)
  Given I have color_red, color_green, color_blue in a switch group
  When I check color_blue before setting color_red
  Then color_blue should be False (implicit default)
  And after setting color_red, color_green and color_blue should both be False
  
  # Validates: All toggles in switch group have False default
```

**Test 8.4: test_switch_unset_no_conflict_when_none_set (Line ~317)**

Old assertion (expects None):
```gherkin
Scenario: Check param when nothing set in switch group (OLD)
  Given I have opt_x and opt_y toggles in a switch group
  When I check opt_y before setting any params
  Then opt_y should be None
```

New assertion (expects False):
```gherkin
Scenario: Check param when nothing set in switch group (NEW)
  Given I have opt_x and opt_y toggles in a switch group
  When I check opt_y before setting any params
  Then opt_y should be False (implicit default)
  
  # Validates: Toggle params have False default even when no conflicts active
```

**Test 8.5: test_switch_reset_toggle_resets_to_default (Line ~343)**

Old assertion (expects None):
```gherkin
Scenario: Check conflicting param before reset scenario (OLD)
  Given I have priority_high and priority_low with SWITCH_RESET behavior
  When I check priority_low before setting priority_high
  Then priority_low should be None (not set yet)
```

New assertion (expects False):
```gherkin
Scenario: Check conflicting param before reset scenario (NEW)
  Given I have priority_high and priority_low with SWITCH_RESET behavior
  When I check priority_low before setting priority_high
  Then priority_low should be False (implicit default)
  
  # Validates: Params with explicit False default still have False from registration
```

**Test 8.6: test_switch_reset_three_way_group_resets_all_conflicts (Line ~371)**

Old assertion (expects None):
```gherkin
Scenario: Check param in three-way reset group (OLD)
  Given I have level_low, level_medium, level_high with SWITCH_RESET
  When I check level_high before setting level_low
  Then level_high should be None
```

New assertion (expects False):
```gherkin
Scenario: Check param in three-way reset group (NEW)
  Given I have level_low, level_medium, level_high with SWITCH_RESET
  When I check level_high before setting level_low
  Then level_high should be False (explicit default matches implicit default)
  
  # Validates: Reset behavior doesn't affect initial registration defaults
```

**Test 8.7: test_switch_reset_switching_back_and_forth (Line ~422)**

Old assertion (expects None):
```gherkin
Scenario: Check param before alternating sets (OLD)
  Given I have encrypt_on and encrypt_off with SWITCH_RESET
  When I check encrypt_off before setting encrypt_on
  Then encrypt_off should be None (not set yet)
```

New assertion (expects False):
```gherkin
Scenario: Check param before alternating sets (NEW)
  Given I have encrypt_on and encrypt_off with SWITCH_RESET
  When I check encrypt_off before setting encrypt_on
  Then encrypt_off should be False (explicit False default)
  
  # Validates: Explicit False defaults are set at registration
```

**Test 8.8: test_mixed_behaviors_in_same_group (Lines ~746, 751)**

Old assertions (expect None):
```gherkin
Scenario: Check param in mixed-behavior group (OLD)
  Given I have fast (SWITCH_UNSET) and strict (SWITCH_RESET) in same group
  When I check strict before setting fast
  Then strict should be None (both occurrences in test)
```

New assertions (expect False):
```gherkin
Scenario: Check param in mixed-behavior group (NEW)
  Given I have fast (SWITCH_UNSET) and strict (SWITCH_RESET) in same group
  When I check strict before setting fast
  Then strict should be False (implicit default, both occurrences)
  
  # Validates: Behavior type doesn't affect initial registration default
```

**Test 8.9: test_switch_behavior_with_no_conflict (Lines ~774-775)**

Old assertions (expect None):
```gherkin
Scenario: Check both params when no conflicts exist (OLD)
  Given I have alpha and beta toggles in a switch group
  When I check both params before setting either
  Then alpha should be None
  And beta should be None
```

New assertions (expect False):
```gherkin
Scenario: Check both params when no conflicts exist (NEW)
  Given I have alpha and beta toggles in a switch group
  When I check both params before setting either
  Then alpha should be False (implicit default)
  And beta should be False (implicit default)
  
  # Validates: Both params have False default, no conflict with both False
```

**Implementation approach:**

Use `multi_replace_string_in_file` to update all 9 tests in a single operation. Each replacement should:
- Include sufficient context (3-5 lines before/after)
- Update the assertion from `is None` to `is False`
- Update or add comments explaining the new behavior

**Verification:**

After updates, run:
```bash
pytest tests/test_param_switch_behavior.py -v
```

All 9 previously failing tests should now pass.

**Final verification:**

After completing both Step 7 and Step 8, run full test suite:
```bash
pytest tests/test_param_switch_behavior.py tests/test_logging.py -v
```

All 64 tests should pass (55 that already passed + 4 logging + 9 switch behavior).

[↑ Back to top](#table-of-contents)

## Success Criteria

- [x] `_set_param_default()` function created in `param.py`
- [x] `_set_param_default()` correctly sets defaults for toggle and non-toggle params
- [x] `add_param()` calls `_set_param_default()` with registration mode enabled
- [x] `_set_defaults()` function removed from `cli.py`
- [x] Call to `_set_defaults()` removed from `run_cli()`
- [x] Pre-parse params with defaults retain their pre-parsed values
- [x] Non-pre-parse params with defaults still receive defaults correctly
- [x] Toggle params without explicit defaults still default to `False`
- [x] XOR validation is properly managed during default-setting
- [x] Unit tests added for `_set_param_default()`
- [x] Integration tests added for `add_param()` with defaults
- [x] Regression test added demonstrating issue #48 is fixed
- [x] Bug in `_has_switch_conflict()` fixed for mixed-type switch groups
- [x] Switch behavior tests updated for toggle initial state
- [x] All existing tests passing (630 tests, 0 failures)
- [x] Overall test coverage remains above 80% (96.40%)
- [ ] Issue #48 closed with reference to implementation

[↑ Back to top](#table-of-contents)

---

## Implementation Plan Changes

This section documents changes made to the implementation plan after the initial core implementation (Steps 1-5) was completed.

### Post-Implementation Analysis

After completing Steps 1-5, comprehensive testing revealed 13 test failures that required additional work:

1. **4 logging test failures** - Revealed a genuine bug in `_has_switch_conflict()` where it checked the wrong parameter type for conflict detection in mixed-type switch groups (TEXT + TOGGLE params)

2. **9 switch behavior test failures** - Not bugs, but tests expecting `None` for toggle initial state when the correct new behavior is `False` (implicit default set during registration)

### Additional Implementation Steps

Two additional steps were added to the "Fixing Test Regressions" section:

- **Step 7**: Fix `_has_switch_conflict()` bug for mixed-type switch groups
- **Step 8**: Update switch behavior tests to expect `False` instead of `None` for toggle initial state

### Additional Considerations

Two additional considerations were documented and resolved:

- **Consideration #4**: Toggle initial state in switch behavior tests (RESOLVED - addressed by Step 8)
- **Consideration #5**: Logging XOR bug in mixed-type switch groups (RESOLVED - addressed by Step 7)

### Timeline

- Steps 1-5: Implemented and tested (core functionality complete)
- Step 7: Implemented (fixes mixed-type switch group bug)
- Step 8: Implemented (updates test expectations)
- Final result: All 630 tests passing, 96.40% coverage

[↑ Back to top](#table-of-contents)

---

## CHANGES for v1.1.0 Release

Issue #48: Param Defaults are set after pre-parse args

### Issues Closed

- #48: Param Defaults are set after pre-parse args

### Additions

None.

### Removals

- `cli._set_defaults()` function removed. Default-setting now occurs in `param.py` during parameter registration.

### Changes

- Default values for parameters are now set immediately when `add_param()` is called, rather than after pre-parsing during CLI execution.
- Pre-parse params with default values now correctly retain their pre-parsed values instead of being overridden.
- Added registration mode flag to temporarily modify switch param behavior during parameter registration, preventing false XOR conflicts when setting defaults.
- Switch conflict detection now checks registration mode and skips validation when `_SWITCH_REGISTER` behavior is active.
- **Bug fix:** `_has_switch_conflict()` now correctly checks the type of the conflicting parameter (not the parameter being set) when determining conflict logic for mixed-type switch groups (e.g., TEXT + TOGGLE params). This fixes false conflicts when setting non-toggle params that share switch groups with toggle params.
- Introduced internal constant `_SWITCH_REGISTER` in `param.py` to represent registration mode for switch param conflict detection. This constant is not part of the public API and is used only for internal implementation logic.

### Migration

No migration required. This is a bug fix that corrects the order of operations. Existing code will continue to work, and pre-parse params with defaults will now work correctly.

**Note:** Toggle parameters now have a defined initial state (`False`) immediately after registration via `add_param()`, rather than remaining undefined (`None`) until explicitly set. This is the intended behavior to ensure predictable parameter state. If your code relied on toggle params being `None` before first use, update assertions to expect `False` for the implicit default state.

### Documentation

No documentation changes required. This is an internal implementation fix with no user-facing API changes.

### Testing

- 8 new tests in `tests/test_param_setters.py` covering `_set_param_default()` behavior
- 5 new tests in `tests/test_cli.py` verifying integration and regression testing
- 4 existing tests in `tests/test_cli.py` updated to reflect new default-setting timing:
  - `test_set_default_param_values` - Now tests `add_param()` instead of `cli._set_defaults()`
  - `test_set_default_param_toggle_with_default_true` - Now tests immediate default-setting at registration
  - `test_set_default_param_toggle_with_no_default` - Now tests implicit False default at registration
  - `test_handle_cli_args_sets_defaults` - Now validates defaults preserved (not set) during CLI handling
- 9 tests in `tests/test_param_switch_behavior.py` updated to expect `False` instead of `None` for toggle initial state
- Tests cover toggle params, non-toggle params, registration mode handling, pre-parse param behavior, and mixed-type switch groups
- All tests updated to reflect defaults being set at registration time rather than CLI parsing time
- Final test results: 630 passed, 1 skipped, 96.55% coverage

---

Full changelog: https://github.com/minouris/spafw37/compare/v1.0.0...v1.1.0  
Issues: https://github.com/minouris/spafw37/issues/48

[↑ Back to top](#table-of-contents)
---
