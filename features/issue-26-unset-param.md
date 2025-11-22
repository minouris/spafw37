# Issue #26: Add Parameter Unset Capability

## Overview

Add the ability to completely unset (remove) and reset parameter values, completing the param-focused API introduced in issue #27. These methods provide a clean, unified interface for parameter lifecycle management without requiring direct config dict manipulation. Includes an optional `PARAM_IMMUTABLE` flag to prevent accidental modification of critical parameters.

**Key architectural decisions:**

- **Part of unified param API:** Extends issue #27's param-focused interface (get/set/unset/reset)
- **Public API methods:** `unset_param()` and `reset_param()` in core.py facade with flexible param resolution
- **Immutability protection:** Optional `PARAM_IMMUTABLE` flag prevents modification/removal of critical params
- **Complete removal:** `unset_param()` removes value from config dict entirely (not just set to None)
- **Smart reset:** `reset_param()` restores default value or unsets if no default exists
- **Backward compatibility:** New functionality, no breaking changes

## Table of Contents

- [Overview](#overview)
- [Implementation Steps](#implementation-steps)
  - [1. Add PARAM_IMMUTABLE constant](#1-add-param_immutable-constant)
  - [2. Create unset_param() in param.py](#2-create-unset_param-in-parampy)
  - [3. Create reset_param() in param.py](#3-create-reset_param-in-parampy)
  - [4. Export unset_param() and reset_param() through core.py facade](#4-export-unset_param-and-reset_param-through-corepy-facade)
  - [5. Update examples](#5-update-examples)
  - [6. Update documentation](#6-update-documentation)
- [Further Considerations](#further-considerations)
  - [1. XOR param interactions](#1-xor-param-interactions)
  - [2. Persistent param handling](#2-persistent-param-handling)
  - [3. Runtime-only param behavior](#3-runtime-only-param-behavior)
  - [4. Reset behavior with defaults](#4-reset-behavior-with-defaults)
- [Success Criteria](#success-criteria)

## Implementation Steps

### 1. Add PARAM_IMMUTABLE constant

**File:** `src/spafw37/constants/param.py`

Add new parameter definition constant:

```python
# Immutability flag - prevents modification and removal after initial value set
PARAM_IMMUTABLE = 'immutable'  # Boolean flag, default: False
```

**Usage in parameter definitions:**

```python
{
    PARAM_NAME: 'app-version',
    PARAM_DESCRIPTION: 'Application version',
    PARAM_IMMUTABLE: True,  # Can be set once, then cannot be changed or unset
    PARAM_DEFAULT: '1.0.0',
}
```

**Semantics:**
- When `PARAM_IMMUTABLE: True`:
  - `set_param()` succeeds if no value exists in config (initial assignment)
  - `set_param()` raises `ValueError` if value already exists (prevent modification)
  - `unset_param()` raises `ValueError` (prevent removal)
- When `PARAM_IMMUTABLE: False` or not specified, both operations succeed normally
- Protects critical framework parameters and user-defined immutable values
- True immutability: write-once, read-many semantics

**Tests:** No tests needed - this is just a constant definition.

[↑ Back to top](#table-of-contents)

### 2. Create unset_param() in param.py

**File:** `src/spafw37/param.py`

Create internal function for unsetting parameter values:

```python
def unset_param(param_name=None, bind_name=None, alias=None):
    """
    Unset (remove) a parameter value from config.
    
    Completely removes the parameter value from the config dictionary.
    Respects PARAM_IMMUTABLE flag - raises ValueError if param is immutable.
    
    Args:
        param_name: Parameter name to unset (flexible resolution).
        bind_name: Config bind name to unset (flexible resolution).
        alias: Parameter alias to unset (flexible resolution).
    
    Raises:
        ValueError: If parameter not found or parameter is immutable.
    
    Example:
        unset_param(param_name='temp-value')
        unset_param(bind_name='runtime_state')
        unset_param(alias='--debug')
    """
    # Resolve param definition using existing helper
    param_def = _resolve_param_definition(param_name=param_name, bind_name=bind_name, alias=alias)
    
    if not param_def:
        # Build error message with what was provided
        identifier = param_name or bind_name or alias
        raise ValueError(f"Parameter '{identifier}' not found")
    
    # Check immutability immediately after resolution
    _check_immutable(param_def)
    
    # Get config bind name
    config_bind_name = _get_bind_name(param_def)
    
    # Remove from config dict
    config.remove_config_value(config_bind_name)
```

**Helper function in config.py:**

```python
def remove_config_value(config_key):
    """
    Remove a configuration value from the config dict.
    
    Args:
        config_key: Configuration key to remove.
    """
    if config_key in _config:
        del _config[config_key]
```

**Create shared immutability check helper in param.py:**

```python
def _check_immutable(param_def):
    """
    Check if parameter is immutable and has a value, raise error if so.
    
    Private helper for set_param() and unset_param() to enforce immutability.
    Blocks modification/removal only if parameter is immutable AND value exists.
    
    Args:
        param_def: Parameter definition dict.
    
    Raises:
        ValueError: If parameter is immutable and value already exists.
    """
    if not param_def.get(PARAM_IMMUTABLE, False):
        return  # Not immutable, allow operation
    
    # Check if value exists
    config_bind_name = _get_bind_name(param_def)
    if not config.has_config_value(config_bind_name):
        return  # No value yet, allow initial assignment
    
    # Immutable and has value - block operation
    param_display_name = param_def.get(PARAM_NAME)
    raise ValueError(f"Cannot modify immutable parameter '{param_display_name}'")
```

**Also update `set_param()` in param.py:**

Add immutability check immediately after resolving param definition:

```python
def set_param(param_name=None, bind_name=None, alias=None, value=None):
    # ... existing resolution code ...
    param_definition = _resolve_param_definition(
        param_name=param_name,
        bind_name=bind_name,
        alias=alias
    )
    
    if param_definition is None:
        raise ValueError("Unknown parameter: '{}'".format(param_name or bind_name or alias))
    
    # Check immutability - allow initial set, block modification
    _check_immutable(param_definition)
    
    # ... rest of existing set_param logic ...
```

**Helper function in config.py:**

```python
def has_config_value(config_key):
    """
    Check if a configuration value exists.
    
    Args:
        config_key: Configuration key to check.
    
    Returns:
        True if key exists in config dict, False otherwise.
    """
    return config_key in _config
```

**Tests:** Create `tests/test_param_unset.py` with:
- `test_unset_param_by_param_name()` - Basic unset using param_name
- `test_unset_param_by_bind_name()` - Basic unset using bind_name
- `test_unset_param_by_alias()` - Basic unset using alias
- `test_unset_param_not_found()` - ValueError when parameter doesn't exist
- `test_unset_param_immutable()` - ValueError when parameter is immutable
- `test_unset_param_immutable_default_false()` - Unset succeeds when PARAM_IMMUTABLE not specified
- `test_unset_param_already_unset()` - No error when unsetting already-unset param (no-op)
- `test_remove_config_value()` - Test config.py helper function directly
- `test_has_config_value()` - Test config.py helper function directly
- `test_check_immutable_not_immutable()` - Helper allows operation when PARAM_IMMUTABLE not set
- `test_check_immutable_no_value()` - Helper allows operation when immutable but no value exists yet
- `test_check_immutable_has_value()` - Helper blocks operation when immutable and value exists

**Add to `tests/test_param.py` (for set_param modifications):**
- `test_set_param_immutable_initial()` - Initial set succeeds when PARAM_IMMUTABLE=True (uses _check_immutable)
- `test_set_param_immutable_modification()` - ValueError when modifying existing immutable param (uses _check_immutable)
- `test_set_param_immutable_default_false()` - Modification succeeds when PARAM_IMMUTABLE not specified

[↑ Back to top](#table-of-contents)

### 3. Create reset_param() in param.py

**File:** `src/spafw37/param.py`

Create internal function for resetting parameter values:

```python
def reset_param(param_name=None, bind_name=None, alias=None):
    """
    Reset a parameter to its default value, or unset it if no default exists.
    
    If the parameter has a PARAM_DEFAULT defined, sets the value to that default.
    If no default exists, removes the parameter value from config (same as unset).
    Respects PARAM_IMMUTABLE flag - raises ValueError if param is immutable.
    
    Args:
        param_name: Parameter name to reset (flexible resolution).
        bind_name: Config bind name to reset (flexible resolution).
        alias: Parameter alias to reset (flexible resolution).
    
    Raises:
        ValueError: If parameter not found or parameter is immutable.
    
    Example:
        reset_param(param_name='counter')  # Resets to PARAM_DEFAULT or unsets
        reset_param(bind_name='log_level')  # Resets to default log level
        reset_param(alias='--verbose')  # Resets verbose flag to default
    """
    # Resolve param definition using existing helper
    param_def = _resolve_param_definition(param_name=param_name, bind_name=bind_name, alias=alias)
    
    if not param_def:
        # Build error message with what was provided
        identifier = param_name or bind_name or alias
        raise ValueError(f"Parameter '{identifier}' not found")
    
    # Reset the parameter - set to default or unset if no default
    # Note: Immutability check done by _check_immutable() via set_param/unset_param
    if PARAM_DEFAULT in param_def:
        # Has default - use set_param to set default value
        default_value = param_def[PARAM_DEFAULT]
        set_param(param_name=param_name, bind_name=bind_name, alias=alias, value=default_value)
    else:
        # No default - use unset_param to remove
        unset_param(param_name=param_name, bind_name=bind_name, alias=alias)
```

**Tests:** Add to `tests/test_param_unset.py`:
- `test_reset_param_with_default()` - Reset param with PARAM_DEFAULT sets to default value
- `test_reset_param_without_default()` - Reset param without PARAM_DEFAULT unsets it
- `test_reset_param_by_param_name()` - Reset using param_name
- `test_reset_param_by_bind_name()` - Reset using bind_name
- `test_reset_param_by_alias()` - Reset using alias
- `test_reset_param_not_found()` - ValueError when parameter doesn't exist
- `test_reset_param_immutable()` - ValueError when parameter is immutable

[↑ Back to top](#table-of-contents)

### 4. Export unset_param() and reset_param() through core.py facade

**File:** `src/spafw37/core.py`

Add public API method:

```python
def unset_param(param_name=None, bind_name=None, alias=None):
    """
    Unset (remove) a parameter value.
    
    Completely removes the parameter value from configuration.
    Useful for clearing temporary state or runtime values.
    
    Args:
        param_name: Parameter name to unset.
        bind_name: Config bind name to unset.
        alias: Parameter alias to unset.
    
    Raises:
        ValueError: If parameter not found or parameter is immutable.
    
    Example:
        # Clear temporary processing state
        spafw37.unset_param('temp-counter')
        
        # Remove runtime flag
        spafw37.unset_param(bind_name='processing_active')
        
        # Clear debug mode
        spafw37.unset_param(alias='--debug')
    """
    from spafw37 import param
    param.unset_param(param_name=param_name, bind_name=bind_name, alias=alias)
```

```

**Also add `reset_param()` public API method:**

```python
def reset_param(param_name=None, bind_name=None, alias=None):
    """
    Reset a parameter to its default value, or unset it if no default exists.
    
    If the parameter has a default value defined, sets it to that default.
    If no default exists, removes the parameter value entirely.
    Useful for restoring initial state or clearing temporary values.
    
    Args:
        param_name: Parameter name to reset.
        bind_name: Config bind name to reset.
        alias: Parameter alias to reset.
    
    Raises:
        ValueError: If parameter not found or parameter is immutable.
    
    Example:
        # Reset counter to default value (or unset if no default)
        spafw37.reset_param('counter')
        
        # Reset log level to default
        spafw37.reset_param(bind_name='log_level')
        
        # Reset debug mode to default (likely False)
        spafw37.reset_param(alias='--debug')
    """
    from spafw37 import param
    param.reset_param(param_name=param_name, bind_name=bind_name, alias=alias)
```

**Tests:** Add to `tests/test_core.py`:
- `test_unset_param_through_core()` - Verify public API delegates to param.unset_param()
- `test_unset_param_immutable_through_core()` - Verify immutable protection works through facade
- `test_set_param_immutable_through_core()` - Verify immutable modification protection works through facade
- `test_reset_param_through_core()` - Verify public API delegates to param.reset_param()
- `test_reset_param_with_default_through_core()` - Verify reset with default through facade
- `test_reset_param_immutable_through_core()` - Verify immutable protection works through facade

[↑ Back to top](#table-of-contents)

### 5. Update examples

**Files:** Create new example, update existing examples if relevant

Create `examples/params_unset.py` with demonstrations of:
- Complete parameter lifecycle (get, set, unset, reset) showcasing unified param API
- Basic unset operations (complete removal)
- Basic reset operations (with and without defaults)
- Immutable parameter protection (set, unset, and reset)
- Initial assignment to immutable param (succeeds)
- Attempted modification of immutable param (fails)
- Attempted unset of immutable param (fails)
- Attempted reset of immutable param (fails)
- Runtime state cleanup patterns
- Comparison of unset vs reset behavior

**Update `examples/README.md`:**

Add entry for new example showing the complete param API lifecycle (issue #27 + issue #26 unified interface).

**Tests:** Manual verification - run each example and verify output matches expected behavior.

[↑ Back to top](#table-of-contents)

### 6. Update documentation

**Files:** `doc/parameters.md`, `doc/api-reference.md`, `doc/README.md`

Add sections covering the complete parameter lifecycle management API:
- **Parameter lifecycle:** get_param(), set_param(), unset_param(), reset_param()
- **Unified param API:** Present as cohesive interface (from issue #27 + issue #26)
- **Unsetting parameters:** Complete removal with `unset_param()`
- **Resetting parameters:** Restore to default or unset with `reset_param()`
- **Difference between unset and reset:** Removal vs. restoration semantics
- **`PARAM_IMMUTABLE` flag:** Write-once, read-many protection for critical params
- **Use cases and best practices:** When to use each method in the param API

**Tests:** Manual review - verify documentation is accurate, complete, and consistent with implementation.

[↑ Back to top](#table-of-contents)

## Further Considerations

### 1. XOR param interactions

**Question:** What happens when unsetting a toggle that has XOR relationships?

**Answer:** XOR handling is a special case that may be covered in a separate issue.

**Rationale:**
- XOR validation logic is complex and may require careful consideration
- This issue focuses on basic unset/reset functionality
- XOR interactions with unset/reset can be addressed separately if needed

**Implementation:**
- No special XOR handling in this issue
- Standard unset/reset behavior applies
- XOR validation remains in `set_param()` only

[↑ Back to top](#table-of-contents)

### 2. Persistent param handling

**Question:** How should unsetting affect persistent configuration?

**Answer:** Unsetting a param removes it from the persisted config dict.

**Rationale:**
- Saving config overwrites the old config file completely
- No special logic needed to remove unset values during save
- When a param is unset, it's removed from the in-memory config dict
- The next save writes the current config dict state (without the unset param)
- Users concerned with data loss should use `PARAM_IMMUTABLE` to protect critical params

**Implementation:**
- `unset_param()` calls `config.remove_config_value()` to remove from config dict
- No additional persistence tracking needed for unset operations
- Standard save behavior handles persistence correctly
- `reset_param()` either sets a new value (persisted if applicable) or unsets (removed from persistence)

**Alternative considered:** Track unset operations explicitly in persistence.
- Pro: More explicit tracking
- Con: Unnecessary complexity - save already overwrites the file
- Con: The absence of a key in the dict is sufficient to indicate it's unset

**Rejected because:** Simple removal from config dict is sufficient and cleaner.

[↑ Back to top](#table-of-contents)

### 3. Runtime-only param behavior

**Question:** Should `PARAM_RUNTIME_ONLY` params be allowed to be unset and reset?

**Answer:** Yes, that's half the point of the exercise.

**Rationale:**
- Runtime-only params are specifically for temporary state
- Unsetting and resetting are natural operations for temporary state management
- This is a primary use case for `unset_param()` and `reset_param()`
- No conflict with `PARAM_IMMUTABLE` - these are orthogonal concerns

**Implementation:**
- No special handling needed
- `unset_param()` and `reset_param()` work normally for runtime-only params
- They won't be persisted due to `PARAM_PERSISTENCE_NEVER`

[↑ Back to top](#table-of-contents)

### 4. Reset behavior with defaults

**Question:** How should `reset_param()` handle resetting to default values?

**Answer:** `reset_param()` should use `set_param()` and `unset_param()` as appropriate.

**Rationale:**
- Using `set_param()` ensures consistent behavior for setting default values
- Type conversion, validation, and persistence tracking happen automatically
- Using `unset_param()` for params without defaults ensures consistent removal logic
- Reuses existing, tested code paths
- Maintains single responsibility - each function does one thing well

**Implementation:**
- When `PARAM_DEFAULT` exists in param definition:
  - Call `set_param()` with the default value
  - This handles type conversion, validation, persistence, immutability checks, etc.
- When `PARAM_DEFAULT` does not exist:
  - Call `unset_param()` to remove the param
  - This handles immutability checks and removal logic
- Both paths benefit from existing error handling and edge case coverage

**Example:**
```python
def reset_param(param_name=None, bind_name=None, alias=None):
    # ... param resolution and immutability check ...
    
    if PARAM_DEFAULT in param_def:
        # Has default - use set_param to set default value
        default_value = param_def[PARAM_DEFAULT]
        set_param(param_name=param_name, bind_name=bind_name, alias=alias, value=default_value)
    else:
        # No default - use unset_param to remove
        unset_param(param_name=param_name, bind_name=bind_name, alias=alias)
```

**Note:** The immutability checks are handled by `set_param()` and `unset_param()`, so `reset_param()` doesn't need its own check. This avoids redundant validation and keeps the code DRY.

[↑ Back to top](#table-of-contents)

## Success Criteria

- [ ] `PARAM_IMMUTABLE` constant added to `constants/param.py`
- [ ] `_check_immutable()` helper implemented in `param.py` for shared immutability validation
- [ ] `unset_param()` implemented in `param.py` with flexible resolution
- [ ] `reset_param()` implemented in `param.py` with default handling
- [ ] `set_param()` updated in `param.py` to call `_check_immutable()` after resolution
- [ ] `remove_config_value()` helper added to `config.py`
- [ ] `has_config_value()` helper added to `config.py`
- [ ] Test file `tests/test_param_unset.py` created with 90%+ coverage (19 test functions: 9 unset + 7 reset + 3 _check_immutable)
- [ ] Immutability tests added to `tests/test_param.py` (3 test functions for set_param)
- [ ] `unset_param()` and `reset_param()` exported through `core.py` facade
- [ ] Core facade tests added to `tests/test_core.py` (6 test functions: 3 unset + 3 reset)
- [ ] Immutable parameter protection working correctly (set, unset, and reset)
- [ ] Initial assignment to immutable param succeeds
- [ ] Modification of immutable param raises ValueError
- [ ] Unset of immutable param raises ValueError
- [ ] Reset of immutable param raises ValueError
- [ ] Reset with PARAM_DEFAULT sets to default value
- [ ] Reset without PARAM_DEFAULT unsets param
- [ ] Example file `examples/params_unset.py` created demonstrating complete param API lifecycle
- [ ] `examples/README.md` updated to present unified param API (issue #27 + issue #26)
- [ ] Documentation updated to present cohesive param lifecycle API in `doc/parameters.md`, `doc/api-reference.md`, `doc/README.md`
- [ ] All 526+ existing tests still passing
- [ ] Overall test coverage remains above 90%
- [ ] Issue #26 closed with reference to implementation

[↑ Back to top](#table-of-contents)
