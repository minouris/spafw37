# Issue #33: Param Allowed Values

## Overview

Add support for restricting parameter values to a predefined set of allowed values through a new `PARAM_ALLOWED_VALUES` constant. This feature enables parameter validation against an explicit whitelist, rejecting any values not in the allowed set. The restriction applies only to TEXT and NUMBER parameter types, as TOGGLE parameters have implicit allowed values (True/False), LIST parameters are collections that would require element-wise validation (outside the scope of this issue), and DICT parameters have complex structure unsuitable for simple value constraints.

When `PARAM_ALLOWED_VALUES` is specified, any value set for that parameter must be a member of the allowed values list. This validation occurs during `set_param()` operations and when defaults are applied. If `PARAM_DEFAULT` is specified, it must also be a member of `PARAM_ALLOWED_VALUES` to prevent configuration errors at parameter definition time.

This feature integrates with the existing validation pipeline in `_validate_param_value()`, adding an allowed values check after type validation but before storing the value. The validation provides clear error messages indicating which values are acceptable when a disallowed value is provided.

**Key architectural decisions:**

- **Type restriction:** Only TEXT and NUMBER params support allowed values (TOGGLE has implicit values, LIST/DICT require different validation approaches)
- **Validation placement:** Check allowed values in `_validate_param_value()` after type validation, ensuring type coercion happens before value checking
- **Default validation:** Validate `PARAM_DEFAULT` against allowed values at parameter registration time to fail fast on misconfiguration
- **Error messaging:** Provide clear error messages showing the rejected value and the list of allowed values

## Table of Contents

- [Overview](#overview)
- [Implementation Steps](#implementation-steps)
  - [1. Add PARAM_ALLOWED_VALUES constant](#1-add-param_allowed_values-constant)
  - [2. Add allowed values validation helper](#2-add-allowed-values-validation-helper)
  - [3. Integrate validation into set_param pipeline](#3-integrate-validation-into-set_param-pipeline)
  - [4. Validate defaults against allowed values](#4-validate-defaults-against-allowed-values)
  - [5. Add comprehensive tests](#5-add-comprehensive-tests)
  - [6. Add example demonstrating allowed values](#6-add-example-demonstrating-allowed-values)
  - [7. Update documentation](#7-update-documentation)
- [Further Considerations](#further-considerations)
  - [1. Should LIST params support allowed values?](#1-should-list-params-support-allowed-values)
  - [2. Case sensitivity for TEXT params](#2-case-sensitivity-for-text-params)
  - [3. Interaction with input filters](#3-interaction-with-input-filters)
- [Success Criteria](#success-criteria)
- [CHANGES for v1.1.0 Release](#changes-for-v110-release)

## Implementation Steps

### 1. Add PARAM_ALLOWED_VALUES constant

**File:** `src/spafw37/constants/param.py`

Add the `PARAM_ALLOWED_VALUES` constant to the parameter definition constants section.

**Location:** After `PARAM_IMMUTABLE` (line 20), before the "Param Persistence Options" section.

**Addition:**

```python
PARAM_ALLOWED_VALUES = 'allowed-values'  # List of allowed values for TEXT and NUMBER params. Value must be in this list.
```

**Tests:** Manual verification - constant is accessible and has correct value.

[↑ Back to top](#table-of-contents)

### 2. Add allowed values validation helper

**File:** `src/spafw37/param.py`

Create a helper function `_validate_allowed_values()` to check if a value is in the allowed values list.

**Location:** After `_validate_text()` function (around line 360), before the input filter functions.

**Implementation:**

```python
def _validate_allowed_values(param_definition, value):
    """Validate value against allowed values list if specified.
    
    Checks if the parameter has PARAM_ALLOWED_VALUES defined and validates
    that the provided value is in the allowed list. Only applies to TEXT
    and NUMBER parameter types.
    
    Args:
        param_definition: Parameter definition dict
        value: Value to validate
        
    Raises:
        ValueError: If value is not in allowed values list
    """
    from spafw37.constants.param import PARAM_ALLOWED_VALUES, PARAM_TYPE, PARAM_NAME
    
    allowed_values = param_definition.get(PARAM_ALLOWED_VALUES)
    if allowed_values is None:
        return
    
    param_type = param_definition.get(PARAM_TYPE, PARAM_TYPE_TEXT)
    param_name = param_definition.get(PARAM_NAME, 'unknown')
    
    # Only validate TEXT and NUMBER params
    if param_type not in (PARAM_TYPE_TEXT, PARAM_TYPE_NUMBER):
        return
    
    # Check if value is in allowed list
    if value not in allowed_values:
        allowed_str = ', '.join(str(allowed_value) for allowed_value in allowed_values)
        raise ValueError(
            f"Invalid value '{value}' for parameter '{param_name}'. "
            f"Allowed values: {allowed_str}"
        )
```

**Tests:**
- `test_validate_allowed_values_text_valid()` - Valid TEXT value passes
- `test_validate_allowed_values_number_valid()` - Valid NUMBER value passes
- `test_validate_allowed_values_text_invalid()` - Invalid TEXT value raises ValueError
- `test_validate_allowed_values_number_invalid()` - Invalid NUMBER value raises ValueError
- `test_validate_allowed_values_not_specified()` - No validation when not specified
- `test_validate_allowed_values_toggle_ignored()` - TOGGLE params skip validation
- `test_validate_allowed_values_list_ignored()` - LIST params skip validation
- `test_validate_allowed_values_dict_ignored()` - DICT params skip validation

[↑ Back to top](#table-of-contents)

### 3. Integrate validation into set_param pipeline

**File:** `src/spafw37/param.py`

Modify `_validate_param_value()` to call `_validate_allowed_values()` after type validation.

**Location:** In `_validate_param_value()` function (around line 1230), after type validation, before returning the validated value.

**Also add module-level type validator dict** before `_validate_param_value()` function:

```python
# Type validator lookup dict - maps param types to validation functions
_TYPE_VALIDATORS = {
    PARAM_TYPE_NUMBER: _validate_number,
    PARAM_TYPE_TOGGLE: lambda value: bool(value),
    PARAM_TYPE_LIST: _validate_list,
    PARAM_TYPE_DICT: _validate_dict,
    PARAM_TYPE_TEXT: _validate_text,
}
```

**Current code structure:**

```python
def _validate_param_value(param_definition, value, strict=True):
    """Validate and coerce value according to parameter type definition."""
    param_type = param_definition.get(PARAM_TYPE, PARAM_TYPE_TEXT)
    
    if param_type == PARAM_TYPE_NUMBER:
        return _validate_number(value)
    elif param_type == PARAM_TYPE_TOGGLE:
        return bool(value)
    elif param_type == PARAM_TYPE_LIST:
        return _validate_list(value)
    elif param_type == PARAM_TYPE_DICT:
        return _validate_dict(value)
    elif param_type == PARAM_TYPE_TEXT:
        return _validate_text(value)
    else:
        return value
```

**Updated code:**

```python
def _validate_param_value(param_definition, value, strict=True):
    """Validate and coerce value according to parameter type definition."""
    param_type = param_definition.get(PARAM_TYPE, PARAM_TYPE_TEXT)
    
    # Type validation using lookup dict
    validator = _TYPE_VALIDATORS.get(param_type)
    if validator:
        validated_value = validator(value)
    else:
        validated_value = value
    
    # Allowed values validation (only for TEXT and NUMBER)
    _validate_allowed_values(param_definition, validated_value)
    
    return validated_value
```

**Tests:**
- `test_set_param_with_allowed_values_valid()` - Setting valid value succeeds
- `test_set_param_with_allowed_values_invalid()` - Setting invalid value raises ValueError
- `test_set_param_allowed_values_with_coercion()` - Type coercion happens before allowed values check

[↑ Back to top](#table-of-contents)

### 4. Validate defaults against allowed values

**File:** `src/spafw37/param.py`

Add validation in `add_param()` to check that `PARAM_DEFAULT` is in `PARAM_ALLOWED_VALUES` when both are specified.

**Location:** In `add_param()` function, after parameter definition is constructed but before it's added to `_PARAMS`.

**Add validation logic:**

```python
# Validate default value is in allowed values
from spafw37.constants.param import PARAM_DEFAULT, PARAM_ALLOWED_VALUES, PARAM_TYPE, PARAM_NAME
allowed_values = param.get(PARAM_ALLOWED_VALUES)
default_value = param.get(PARAM_DEFAULT)
param_type = param.get(PARAM_TYPE, PARAM_TYPE_TEXT)
param_name = param.get(PARAM_NAME, 'unknown')

if allowed_values is not None and default_value is not None:
    # Only check for TEXT and NUMBER types
    if param_type in (PARAM_TYPE_TEXT, PARAM_TYPE_NUMBER):
        if default_value not in allowed_values:
            allowed_str = ', '.join(str(allowed_value) for allowed_value in allowed_values)
            raise ValueError(
                f"Default value '{default_value}' for parameter '{param_name}' "
                f"is not in allowed values: {allowed_str}"
            )
```

**Tests:**
- `test_add_param_default_in_allowed_values()` - Valid default accepted
- `test_add_param_default_not_in_allowed_values()` - Invalid default raises ValueError
- `test_add_param_no_default_with_allowed_values()` - No error when default not specified
- `test_add_param_no_allowed_values_with_default()` - No error when allowed values not specified

[↑ Back to top](#table-of-contents)

### 5. Add comprehensive tests

**File:** `tests/test_param_validation.py`

Add test class `TestParamAllowedValues` with comprehensive test cases.

**Test implementations:**

```python
class TestParamAllowedValues:
    """Tests for PARAM_ALLOWED_VALUES validation."""
    
    def test_validate_allowed_values_text_valid(self):
        """Test allowed values validation accepts valid TEXT value."""
        setup_function()
        param_def = {
            PARAM_NAME: 'environment',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALLOWED_VALUES: ['dev', 'staging', 'production']
        }
        # Should not raise
        param._validate_allowed_values(param_def, 'dev')
        param._validate_allowed_values(param_def, 'staging')
        param._validate_allowed_values(param_def, 'production')
    
    def test_validate_allowed_values_text_invalid(self):
        """Test allowed values validation rejects invalid TEXT value."""
        setup_function()
        param_def = {
            PARAM_NAME: 'environment',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALLOWED_VALUES: ['dev', 'staging', 'production']
        }
        with pytest.raises(ValueError, match="Invalid value 'test' for parameter 'environment'"):
            param._validate_allowed_values(param_def, 'test')
    
    def test_validate_allowed_values_number_valid(self):
        """Test allowed values validation accepts valid NUMBER value."""
        setup_function()
        param_def = {
            PARAM_NAME: 'port',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_ALLOWED_VALUES: [80, 443, 8080, 8443]
        }
        # Should not raise
        param._validate_allowed_values(param_def, 80)
        param._validate_allowed_values(param_def, 443)
    
    def test_validate_allowed_values_number_invalid(self):
        """Test allowed values validation rejects invalid NUMBER value."""
        setup_function()
        param_def = {
            PARAM_NAME: 'port',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_ALLOWED_VALUES: [80, 443, 8080, 8443]
        }
        with pytest.raises(ValueError, match="Invalid value '3000' for parameter 'port'"):
            param._validate_allowed_values(param_def, 3000)
    
    def test_validate_allowed_values_not_specified(self):
        """Test no validation when PARAM_ALLOWED_VALUES not specified."""
        setup_function()
        param_def = {
            PARAM_NAME: 'value',
            PARAM_TYPE: PARAM_TYPE_TEXT
        }
        # Should not raise - no allowed values constraint
        param._validate_allowed_values(param_def, 'anything')
    
    def test_validate_allowed_values_toggle_ignored(self):
        """Test TOGGLE params skip allowed values validation."""
        setup_function()
        param_def = {
            PARAM_NAME: 'flag',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALLOWED_VALUES: [True]  # This should be ignored
        }
        # Should not raise - toggles skip validation
        param._validate_allowed_values(param_def, False)
    
    def test_set_param_with_allowed_values_valid(self):
        """Test set_param succeeds with valid allowed value."""
        setup_function()
        param.add_param({
            PARAM_NAME: 'mode',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALLOWED_VALUES: ['fast', 'normal', 'slow'],
            PARAM_DEFAULT: 'normal'
        })
        # Should not raise
        param.set_param(param_name='mode', value='fast')
        assert param.get_param(param_name='mode') == 'fast'
    
    def test_set_param_with_allowed_values_invalid(self):
        """Test set_param raises error with invalid allowed value."""
        setup_function()
        param.add_param({
            PARAM_NAME: 'mode',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALLOWED_VALUES: ['fast', 'normal', 'slow']
        })
        with pytest.raises(ValueError, match="Invalid value 'turbo' for parameter 'mode'"):
            param.set_param(param_name='mode', value='turbo')
    
    def test_add_param_default_in_allowed_values(self):
        """Test add_param accepts default that is in allowed values."""
        setup_function()
        # Should not raise
        param.add_param({
            PARAM_NAME: 'level',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_ALLOWED_VALUES: [1, 2, 3, 4, 5],
            PARAM_DEFAULT: 3
        })
    
    def test_add_param_default_not_in_allowed_values(self):
        """Test add_param raises error when default not in allowed values."""
        setup_function()
        with pytest.raises(ValueError, match="Default value '10' for parameter 'level'"):
            param.add_param({
                PARAM_NAME: 'level',
                PARAM_TYPE: PARAM_TYPE_NUMBER,
                PARAM_ALLOWED_VALUES: [1, 2, 3, 4, 5],
                PARAM_DEFAULT: 10
            })
    
    def test_set_param_allowed_values_with_number_coercion(self):
        """Test allowed values check happens after type coercion."""
        setup_function()
        param.add_param({
            PARAM_NAME: 'count',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_ALLOWED_VALUES: [1, 2, 3]
        })
        # String "2" should be coerced to int 2, then validated
        param.set_param(param_name='count', value='2')
        result = param.get_param(param_name='count')
        assert result == 2
        assert isinstance(result, int)
```

**Tests:** All tests in TestParamAllowedValues class passing.

[↑ Back to top](#table-of-contents)

### 6. Add example demonstrating allowed values

**File:** `examples/params_allowed_values.py`

Create a new example demonstrating `PARAM_ALLOWED_VALUES` usage with TEXT and NUMBER parameters.

**Implementation:**

```python
"""Allowed Values Example - Restricting parameter values.

This example demonstrates PARAM_ALLOWED_VALUES for constraining
parameter values to a predefined set. Useful for:
- Environment names (dev, staging, production)
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Enumerated options (small, medium, large)
- Port selections (80, 443, 8080)

Run this example:
    python examples/params_allowed_values.py deploy --env production
    python examples/params_allowed_values.py deploy --env invalid  # Error!
    python examples/params_allowed_values.py start --port 8080
    python examples/params_allowed_values.py start --port 9999  # Error!
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_DEFAULT,
    PARAM_ALLOWED_VALUES,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)


def deploy_action():
    """Deploy to specified environment."""
    env = spafw37.get_param('environment')
    region = spafw37.get_param('region')
    
    spafw37.output(f"Deploying to environment: {env}")
    spafw37.output(f"Region: {region}")


def start_action():
    """Start server on specified port."""
    port = spafw37.get_param('port')
    size = spafw37.get_param('size')
    
    spafw37.output(f"Starting server on port {port}")
    spafw37.output(f"Instance size: {size}")


def setup():
    """Configure parameters and commands."""
    
    # Define parameters with allowed values
    params = [
        {
            PARAM_NAME: 'environment',
            PARAM_DESCRIPTION: 'Target environment',
            PARAM_ALIASES: ['--env', '-e'],
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALLOWED_VALUES: ['dev', 'staging', 'production'],
            PARAM_DEFAULT: 'dev',
        },
        {
            PARAM_NAME: 'region',
            PARAM_DESCRIPTION: 'Target region',
            PARAM_ALIASES: ['--region', '-r'],
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALLOWED_VALUES: ['north', 'south', 'east', 'west'],
            PARAM_DEFAULT: 'north',
        },
        {
            PARAM_NAME: 'port',
            PARAM_DESCRIPTION: 'Server port',
            PARAM_ALIASES: ['--port', '-p'],
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_ALLOWED_VALUES: [80, 443, 8080, 8443],
            PARAM_DEFAULT: 8080,
        },
        {
            PARAM_NAME: 'size',
            PARAM_DESCRIPTION: 'Instance size',
            PARAM_ALIASES: ['--size', '-s'],
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALLOWED_VALUES: ['small', 'medium', 'large', 'xlarge'],
            PARAM_DEFAULT: 'medium',
        },
    ]
    
    # Define commands
    commands = [
        {
            COMMAND_NAME: 'deploy',
            COMMAND_DESCRIPTION: 'Deploy application',
            COMMAND_ACTION: deploy_action,
        },
        {
            COMMAND_NAME: 'start',
            COMMAND_DESCRIPTION: 'Start server',
            COMMAND_ACTION: start_action,
        },
    ]
    
    spafw37.add_params(params)
    spafw37.add_commands(commands)


if __name__ == '__main__':
    setup()
    spafw37.run_cli()
```

**File:** `examples/README.md`

Add entry for the new example in the Parameters section:

```markdown
- `params_allowed_values.py` - Restrict parameter values to allowed set
```

**Tests:** Manual execution - verify example runs correctly and rejects invalid values.

[↑ Back to top](#table-of-contents)

### 7. Update documentation

**Files:** `doc/parameters.md`, `doc/api-reference.md`, `README.md`

Update documentation to include `PARAM_ALLOWED_VALUES` in parameter definition constants and add usage examples.

**Important:** 
- Add version note ("**Added in v1.1.0**") at the start of any new documentation sections
- Update main `README.md` to reflect new functionality in relevant sections (features list, code examples, examples list, "What's New in v1.1.0")

**`doc/parameters.md` updates:**

Add new section "Allowed Values" after "Immutable Parameters" section:

```markdown
### Allowed Values

**Added in v1.1.0**

Restrict parameter values to a predefined set using `PARAM_ALLOWED_VALUES`. Only applies to TEXT and NUMBER parameter types.

```python
from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_ALIASES,
    PARAM_ALLOWED_VALUES,
    PARAM_DEFAULT,
)

params = [
    {
        PARAM_NAME: 'environment',
        PARAM_DESCRIPTION: 'Target environment',
        PARAM_ALIASES: ['--env'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALLOWED_VALUES: ['dev', 'staging', 'production'],
        PARAM_DEFAULT: 'dev',
    },
    {
        PARAM_NAME: 'port',
        PARAM_DESCRIPTION: 'Server port',
        PARAM_ALIASES: ['--port'],
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_ALLOWED_VALUES: [80, 443, 8080, 8443],
        PARAM_DEFAULT: 8080,
    },
]
```

**Validation:**
- Values must be in the allowed list
- Type coercion happens before validation
- Default value must be in allowed values list
- Clear error messages show allowed values

**Restrictions:**
- Only TEXT and NUMBER params support allowed values
- TOGGLE params have implicit allowed values (True/False)
- LIST and DICT params not supported (use custom validation)

See [examples/params_allowed_values.py](../examples/params_allowed_values.py) for complete usage examples.
```

Add `PARAM_ALLOWED_VALUES` to Parameter Definition Constants table in the "Configuration Binding" section:

| Constant | Description |
|----------|-------------|
| `PARAM_ALLOWED_VALUES` | List of allowed values for TEXT and NUMBER params. Value must be in this list. See [Allowed Values](#allowed-values) and [examples/params_allowed_values.py](../examples/params_allowed_values.py) for usage. |

**`doc/api-reference.md` updates:**

Add `PARAM_ALLOWED_VALUES` to Parameter Constants "Configuration Binding" table:

| Constant | Type | Description |
|----------|------|-------------|
| `PARAM_ALLOWED_VALUES` | list | Allowed values for TEXT/NUMBER params. See [Parameters Guide - Allowed Values](parameters.md#allowed-values) and [example](../examples/params_allowed_values.py) |

**`README.md` updates:**

Update "What's New in v1.1.0" section:

```markdown
- **Allowed Values Validation** - New `PARAM_ALLOWED_VALUES` constant restricts TEXT and NUMBER parameters to predefined value sets with clear error messages.
```

Add `params_allowed_values.py` to examples list in the Parameters section:

```markdown
- `params_allowed_values.py` - Restrict parameter values to allowed set
```

**Tests:** Manual review - verify documentation is accurate and consistent.

[↑ Back to top](#table-of-contents)

## Further Considerations

### 1. Should LIST params support allowed values?

**Question:** Should `PARAM_ALLOWED_VALUES` support LIST parameters with element-wise validation?

**Answer:** No, not in this issue. LIST params require different validation logic.

**Rationale:**
- LIST params contain multiple values, requiring element-wise validation
- Validation complexity increases significantly (validate each element vs single value)
- Error messaging becomes more complex (which element failed?)
- Use cases are less common than TEXT/NUMBER constraints
- Can be added in a future enhancement if needed

**Implementation:**
- Skip LIST params in `_validate_allowed_values()`
- Document that LIST params are not supported
- Future enhancement could add `PARAM_ALLOWED_LIST_ELEMENTS` for element-wise validation

[↑ Back to top](#table-of-contents)

### 2. Case sensitivity for TEXT params

**Question:** Should allowed values validation be case-sensitive for TEXT parameters?

**Answer:** Yes, validation should be case-sensitive.

**Rationale:**
- Consistent with standard Python equality semantics
- Environment names like 'Dev' vs 'dev' may have different meanings
- Application code can normalize values using `PARAM_INPUT_FILTER` if needed
- Clear and predictable behavior
- Simpler implementation without additional configuration

**Implementation:**
- Use direct `in` operator for membership check
- Document case-sensitive behavior
- Users can add input filters for case normalization if needed

[↑ Back to top](#table-of-contents)

### 3. Interaction with input filters

**Question:** How does `PARAM_ALLOWED_VALUES` interact with `PARAM_INPUT_FILTER`?

**Answer:** Allowed values validation occurs after input filter processing and type validation.

**Rationale:**
- Input filters transform string values from CLI to proper types
- Type validation coerces values to the correct type
- Allowed values check validates the final typed value
- This order ensures consistency (e.g., "2" filtered to 2, then validated)

**Implementation:**
- Input filter in `set_param()` runs first
- Type validation in `_validate_param_value()` runs second
- Allowed values check in `_validate_param_value()` runs third
- Order: CLI string → input filter → type validation → allowed values check

**Example:**

```python
{
    PARAM_NAME: 'port',
    PARAM_TYPE: PARAM_TYPE_NUMBER,
    PARAM_INPUT_FILTER: lambda v: int(v),
    PARAM_ALLOWED_VALUES: [80, 443, 8080],
}
# CLI: --port "443" → input filter → 443 (int) → allowed values check → valid
```

[↑ Back to top](#table-of-contents)

## Success Criteria

- [ ] `PARAM_ALLOWED_VALUES` constant added to `src/spafw37/constants/param.py`
- [ ] `_validate_allowed_values()` helper function implemented in `src/spafw37/param.py`
- [ ] `_validate_param_value()` modified to call `_validate_allowed_values()`
- [ ] Default value validation added to `add_param()`
- [ ] Test class `TestParamAllowedValues` added with 12+ tests covering:
  - Valid TEXT values
  - Invalid TEXT values
  - Valid NUMBER values
  - Invalid NUMBER values
  - No allowed values specified
  - TOGGLE/LIST/DICT params skip validation
  - Integration with `set_param()`
  - Default value validation
  - Type coercion before validation
- [ ] Example `params_allowed_values.py` created demonstrating usage
- [ ] `examples/README.md` updated with new example entry
- [ ] `doc/parameters.md` updated with "Allowed Values" section and constant table entry
- [ ] `doc/api-reference.md` updated with `PARAM_ALLOWED_VALUES` constant entry
- [ ] `README.md` updated with "What's New" entry and example entry
- [ ] All existing tests still passing
- [ ] Overall test coverage remains above 80%
- [ ] Issue #33 closed with reference to implementation

[↑ Back to top](#table-of-contents)

---

## CHANGES for v1.1.0 Release

### New Features

- **Parameter Allowed Values:** Added `PARAM_ALLOWED_VALUES` constant to restrict TEXT and NUMBER parameter values to predefined sets. Values not in the allowed list are rejected with clear error messages. Default values are validated at parameter registration time.

[↑ Back to top](#table-of-contents)
