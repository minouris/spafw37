# Issue #33: Param Allowed Values

## Overview

Add support for restricting parameter values to a predefined set of allowed values through a new `PARAM_ALLOWED_VALUES` constant. This feature enables parameter validation against an explicit whitelist, rejecting any values not in the allowed set. The restriction applies to TEXT, NUMBER, and LIST parameter types. For TEXT parameters, validation is case-insensitive with automatic normalization to the canonical case from the allowed values list. For LIST parameters, each element is validated individually against the allowed values.

When `PARAM_ALLOWED_VALUES` is specified, any value set for that parameter must be a member of the allowed values list (or for LIST params, all elements must be members). This validation occurs during `set_param()` operations and when defaults are applied. If `PARAM_DEFAULT` is specified, it must also be a member of `PARAM_ALLOWED_VALUES` to prevent configuration errors at parameter definition time.

This feature integrates with the existing validation pipeline in `_validate_param_value()`, adding an allowed values check after type validation but before storing the value. Input filters run before all validation, allowing transformation of raw input before validation occurs. The validation provides clear error messages indicating which values are acceptable when a disallowed value is provided.

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

Create helper functions to validate values against allowed values list with support for case-insensitive TEXT matching and LIST element validation.

**Location:** After `_validate_text()` function (around line 360), before the input filter functions.

**Implementation:**

```python
def _normalise_text_to_allowed_case(value, allowed_values):
    """Match value case-insensitively against allowed_values and return canonical case.
    
    Performs case-insensitive comparison between value and each item in allowed_values.
    Returns the canonical case from allowed_values if a match is found, None otherwise.
    
    Args:
        value: String value to normalise
        allowed_values: List of allowed string values in canonical case
        
    Returns:
        String in canonical case if match found, None otherwise
        
    Example:
        If allowed_values contains 'DEBUG' and value is 'debug', returns 'DEBUG'
    """
    value_lower = value.lower()
    for allowed in allowed_values:
        if allowed.lower() == value_lower:
            return allowed
    return None


def _validate_allowed_values(param_definition, value):
    """Validate value against allowed values list if specified.
    
    Checks if the parameter has PARAM_ALLOWED_VALUES defined and validates
    that the provided value is in the allowed list. For TEXT parameters,
    performs case-insensitive matching. For NUMBER parameters, performs 
    exact match. For LIST parameters, validates each element individually.
    
    Does not modify the value - raises ValueError if validation fails.
    
    Args:
        param_definition: Parameter definition dict
        value: Value to validate (single value for TEXT/NUMBER, list for LIST)
        
    Raises:
        ValueError: If value is not in allowed values list
    """
    allowed_values = param_definition.get(PARAM_ALLOWED_VALUES)
    if allowed_values is None:
        return
    
    param_type = param_definition.get(PARAM_TYPE, PARAM_TYPE_TEXT)
    param_name = param_definition.get(PARAM_NAME, 'unknown')
    
    # Only validate TEXT, NUMBER, and LIST params
    if param_type not in (PARAM_TYPE_TEXT, PARAM_TYPE_NUMBER, PARAM_TYPE_LIST):
        return
    
    # Handle LIST parameters - validate each element
    if param_type == PARAM_TYPE_LIST:
        # Empty lists are invalid when allowed values specified
        if not value:
            allowed_str = ', '.join(str(av) for av in allowed_values)
            raise ValueError(
                f"Empty list not allowed for parameter '{param_name}'. "
                f"Must provide at least one value from: {allowed_str}"
            )
        
        for element in value:
            if _normalise_text_to_allowed_case(element, allowed_values) is None:
                allowed_str = ', '.join(str(av) for av in allowed_values)
                raise ValueError(
                    f"List element '{element}' not allowed for parameter '{param_name}'. "
                    f"Allowed values: {allowed_str}"
                )
        return
    
    # Handle TEXT parameters - case-insensitive matching
    if param_type == PARAM_TYPE_TEXT:
        if _normalise_text_to_allowed_case(value, allowed_values) is None:
            allowed_str = ', '.join(str(av) for av in allowed_values)
            raise ValueError(
                f"Value '{value}' not allowed for parameter '{param_name}'. "
                f"Allowed values: {allowed_str}"
            )
        return
    
    # Handle NUMBER parameters - exact match
    if value not in allowed_values:
        allowed_str = ', '.join(str(av) for av in allowed_values)
        raise ValueError(
            f"Value {value} not allowed for parameter '{param_name}'. "
            f"Allowed values: {allowed_str}"
        )


def _normalise_allowed_value(param_definition, value):
    """Normalise value to canonical case from allowed values list.
    
    For TEXT parameters, returns the canonical case from PARAM_ALLOWED_VALUES.
    For LIST parameters, returns list with each element normalised to canonical case.
    For NUMBER parameters and others, returns value unchanged.
    
    Should only be called after _validate_allowed_values() has confirmed the value is valid.
    
    Args:
        param_definition: Parameter definition dict
        value: Value to normalise (must be valid)
        
    Returns:
        Normalised value with canonical case
    """
    allowed_values = param_definition.get(PARAM_ALLOWED_VALUES)
    if allowed_values is None:
        return value
    
    param_type = param_definition.get(PARAM_TYPE, PARAM_TYPE_TEXT)
    
    # Normalise LIST elements to canonical case
    if param_type == PARAM_TYPE_LIST:
        normalised_list = []
        for element in value:
            canonical = _normalise_text_to_allowed_case(element, allowed_values)
            normalised_list.append(canonical)
        return normalised_list
    
    # Normalise TEXT to canonical case
    if param_type == PARAM_TYPE_TEXT:
        return _normalise_text_to_allowed_case(value, allowed_values)
    
    # NUMBER and others - no normalisation needed
    return value
```

**Tests:**
- `test_validate_allowed_values_text_valid()` - Valid TEXT value passes validation
- `test_validate_allowed_values_number_valid()` - Valid NUMBER value passes validation
- `test_validate_allowed_values_list_valid()` - Valid LIST elements pass validation
- `test_validate_allowed_values_list_empty()` - Empty LIST raises ValueError
- `test_validate_allowed_values_text_invalid()` - Invalid TEXT value raises ValueError
- `test_validate_allowed_values_number_invalid()` - Invalid NUMBER value raises ValueError
- `test_validate_allowed_values_list_invalid_element()` - Invalid LIST element raises ValueError
- `test_validate_allowed_values_not_specified()` - No validation when not specified
- `test_validate_allowed_values_toggle_ignored()` - TOGGLE params skip validation
- `test_validate_allowed_values_dict_ignored()` - DICT params skip validation
- `test_normalise_allowed_value_text()` - TEXT value normalised to canonical case
- `test_normalise_allowed_value_text_mixed_case()` - Mixed-case canonical values preserved
- `test_normalise_allowed_value_list()` - LIST elements normalised to canonical case
- `test_normalise_allowed_value_list_mixed_case()` - Mixed-case canonical values preserved in lists
- `test_normalise_allowed_value_number()` - NUMBER values returned unchanged
- `test_normalise_allowed_value_not_specified()` - Value returned unchanged when no allowed values

[↑ Back to top](#table-of-contents)

### 3. Integrate validation into set_param pipeline

**File:** `src/spafw37/param.py`

Modify `_validate_param_value()` to call `_validate_allowed_values()` after type validation, then call `_normalise_allowed_value()` to get the normalised value.

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
    
    # Allowed values validation (TEXT/NUMBER/LIST)
    _validate_allowed_values(param_definition, validated_value)
    
    # Normalisation to canonical case (TEXT/LIST only)
    normalised_value = _normalise_allowed_value(param_definition, validated_value)
    
    return normalised_value
```

**Tests:**
- `test_set_param_with_allowed_values_valid()` - Setting valid value succeeds
- `test_set_param_with_allowed_values_case_insensitive()` - TEXT value normalised to canonical case
- `test_set_param_list_with_allowed_values_valid()` - Setting valid LIST succeeds with normalisation
- `test_set_param_list_empty()` - Setting empty LIST raises ValueError
- `test_set_param_with_allowed_values_invalid()` - Setting invalid value raises ValueError
- `test_set_param_allowed_values_with_coercion()` - Type coercion happens before allowed values check
- `test_set_param_list_invalid_element()` - LIST with invalid element raises ValueError

[↑ Back to top](#table-of-contents)

### 4. Validate defaults against allowed values

**File:** `src/spafw37/param.py`

Add validation in `add_param()` to check that `PARAM_DEFAULT` is in `PARAM_ALLOWED_VALUES` when both are specified. Use the normalised value returned by the validator.

**Location:** In `add_param()` function, after parameter definition is constructed but before it's added to `_PARAMS`.

**Add validation logic:**

```python
# Validate default value is in allowed values and store normalised value
default_value = param.get(PARAM_DEFAULT)
if default_value is not None:
    _validate_allowed_values(param, default_value)
    normalised_default = _normalise_allowed_value(param, default_value)
    # Update param with normalised default (canonical case for TEXT, normalised list for LIST)
    param[PARAM_DEFAULT] = normalised_default
```

**Tests:**
- `test_add_param_default_in_allowed_values()` - Valid default accepted
- `test_add_param_default_normalised()` - TEXT default normalised to canonical case
- `test_add_param_list_default_normalised()` - LIST default elements normalised to canonical case
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
        """Test that the _validate_allowed_values helper accepts valid TEXT parameter values.
        
        This test verifies that when a TEXT parameter has PARAM_ALLOWED_VALUES defined,
        values that are members of the allowed list pass validation without raising errors.
        This behaviour is expected because valid values should not be rejected by the whitelist.
        """
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
        """Test that the _validate_allowed_values helper rejects invalid TEXT parameter values.
        
        This test verifies that when a TEXT parameter has PARAM_ALLOWED_VALUES defined,
        values that are not in the allowed list are rejected with a clear ValueError.
        This behaviour is expected because invalid values must be rejected to enforce the whitelist constraint.
        """
        setup_function()
        param_def = {
            PARAM_NAME: 'environment',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALLOWED_VALUES: ['dev', 'staging', 'production']
        }
        with pytest.raises(ValueError, match="Value 'test' not allowed for parameter 'environment'"):
            param._validate_allowed_values(param_def, 'test')
    
    def test_validate_allowed_values_list_valid(self):
        """Test that the _validate_allowed_values helper accepts valid LIST parameter elements.
        
        This test verifies that when a LIST parameter has PARAM_ALLOWED_VALUES defined,
        lists where all elements are members of the allowed list pass validation without errors.
        This behaviour is expected because valid list elements should not be rejected by the whitelist.
        """
        setup_function()
        param_def = {
            PARAM_NAME: 'features',
            PARAM_TYPE: PARAM_TYPE_LIST,
            PARAM_ALLOWED_VALUES: ['auth', 'api', 'database', 'cache']
        }
        # Should not raise
        param._validate_allowed_values(param_def, ['auth', 'api'])
        param._validate_allowed_values(param_def, ['database'])
    
    def test_validate_allowed_values_list_invalid_element(self):
        """Test that the _validate_allowed_values helper rejects LIST parameters with invalid elements.
        
        This test verifies that when a LIST parameter has PARAM_ALLOWED_VALUES defined,
        lists containing any element not in the allowed list are rejected with a clear ValueError.
        This behaviour is expected because all elements must be valid to enforce the whitelist constraint.
        """
        setup_function()
        param_def = {
            PARAM_NAME: 'features',
            PARAM_TYPE: PARAM_TYPE_LIST,
            PARAM_ALLOWED_VALUES: ['auth', 'api', 'database', 'cache']
        }
        with pytest.raises(ValueError, match="List element 'invalid' not allowed for parameter 'features'"):
            param._validate_allowed_values(param_def, ['auth', 'invalid'])
    
    def test_validate_allowed_values_list_empty(self):
        """Test that the _validate_allowed_values helper rejects empty LIST parameters.
        
        This test verifies that when a LIST parameter has PARAM_ALLOWED_VALUES defined,
        empty lists are rejected with a clear ValueError indicating at least one valid value must be provided.
        This behaviour is expected because empty lists provide no valid configuration when allowed values are specified.
        """
        setup_function()
        param_def = {
            PARAM_NAME: 'features',
            PARAM_TYPE: PARAM_TYPE_LIST,
            PARAM_ALLOWED_VALUES: ['auth', 'api', 'database', 'cache']
        }
        with pytest.raises(ValueError, match="Empty list not allowed for parameter 'features'"):
            param._validate_allowed_values(param_def, [])
    
    def test_validate_allowed_values_number_valid(self):
        """Test that the _validate_allowed_values helper accepts valid NUMBER parameter values.
        
        This test verifies that when a NUMBER parameter has PARAM_ALLOWED_VALUES defined,
        values that are members of the allowed list pass validation without raising errors.
        This behaviour is expected because valid numeric values should not be rejected by the whitelist.
        """
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
        """Test that the _validate_allowed_values helper rejects invalid NUMBER parameter values.
        
        This test verifies that when a NUMBER parameter has PARAM_ALLOWED_VALUES defined,
        values that are not in the allowed list are rejected with a clear ValueError.
        This behaviour is expected because invalid numeric values must be rejected to enforce the whitelist constraint.
        """
        setup_function()
        param_def = {
            PARAM_NAME: 'port',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_ALLOWED_VALUES: [80, 443, 8080, 8443]
        }
        with pytest.raises(ValueError, match="Value 3000 not allowed for parameter 'port'"):
            param._validate_allowed_values(param_def, 3000)
    
    def test_validate_allowed_values_not_specified(self):
        """Test that the _validate_allowed_values helper skips validation when PARAM_ALLOWED_VALUES is not specified.
        
        This test verifies that when a parameter does not have PARAM_ALLOWED_VALUES defined,
        any value is accepted without validation or errors being raised.
        This behaviour is expected because the allowed values constraint is optional and should not affect parameters that don't use it.
        """
        setup_function()
        param_def = {
            PARAM_NAME: 'value',
            PARAM_TYPE: PARAM_TYPE_TEXT
        }
        # Should not raise - no allowed values constraint
        param._validate_allowed_values(param_def, 'anything')
    
    def test_validate_allowed_values_toggle_ignored(self):
        """Test that the _validate_allowed_values helper skips validation for TOGGLE parameters.
        
        This test verifies that TOGGLE parameters do not have allowed values validation applied,
        even when PARAM_ALLOWED_VALUES is specified in the parameter definition.
        This behaviour is expected because TOGGLE parameters have implicit allowed values (True/False) and do not require explicit validation.
        """
        setup_function()
        param_def = {
            PARAM_NAME: 'flag',
            PARAM_TYPE: PARAM_TYPE_TOGGLE,
            PARAM_ALLOWED_VALUES: [True]  # This should be ignored
        }
        # Should not raise - toggles skip validation
        param._validate_allowed_values(param_def, False)
    
    def test_normalise_allowed_value_text(self):
        """Test that the _normalise_allowed_value helper normalises TEXT values to canonical case.
        
        This test verifies that TEXT parameter values are normalised to the exact canonical case
        from the PARAM_ALLOWED_VALUES list, regardless of input case.
        This behaviour is expected to provide consistent canonical case storage for TEXT parameters.
        """
        setup_function()
        param_def = {
            PARAM_NAME: 'log_level',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALLOWED_VALUES: ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        }
        assert param._normalise_allowed_value(param_def, 'debug') == 'DEBUG'
        assert param._normalise_allowed_value(param_def, 'INFO') == 'INFO'
        assert param._normalise_allowed_value(param_def, 'WaRnInG') == 'WARNING'
    
    def test_normalise_allowed_value_text_mixed_case(self):
        """Test that the _normalise_allowed_value helper preserves mixed-case canonical values.
        
        This test verifies that when allowed values contain mixed-case strings (e.g., 'Alice'),
        any case variant of the input is normalised to the exact canonical case from the allowed list.
        This behaviour is expected to preserve proper names and other case-sensitive display values.
        """
        setup_function()
        param_def = {
            PARAM_NAME: 'username',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALLOWED_VALUES: ['Alice', 'Bob', 'Charlie', 'Dave']
        }
        assert param._normalise_allowed_value(param_def, 'alice') == 'Alice'
        assert param._normalise_allowed_value(param_def, 'DAVE') == 'Dave'
        assert param._normalise_allowed_value(param_def, 'BoB') == 'Bob'
    
    def test_normalise_allowed_value_list(self):
        """Test that the _normalise_allowed_value helper normalises LIST elements to canonical case.
        
        This test verifies that LIST parameter elements are normalised to the exact canonical case
        from the PARAM_ALLOWED_VALUES list, returning a list with normalised elements.
        This behaviour is expected to provide consistent canonical case storage for LIST elements.
        """
        setup_function()
        param_def = {
            PARAM_NAME: 'features',
            PARAM_TYPE: PARAM_TYPE_LIST,
            PARAM_ALLOWED_VALUES: ['AUTH', 'API', 'DATABASE', 'CACHE']
        }
        result = param._normalise_allowed_value(param_def, ['auth', 'database'])
        assert result == ['AUTH', 'DATABASE']
    
    def test_normalise_allowed_value_list_mixed_case(self):
        """Test that the _normalise_allowed_value helper preserves mixed-case canonical values in lists.
        
        This test verifies that when LIST allowed values contain mixed-case strings,
        list elements are normalised to the exact canonical case from the allowed list.
        This behaviour is expected to preserve proper names and other case-sensitive display values in lists.
        """
        setup_function()
        param_def = {
            PARAM_NAME: 'team_members',
            PARAM_TYPE: PARAM_TYPE_LIST,
            PARAM_ALLOWED_VALUES: ['Alice', 'Bob', 'Charlie', 'Dave']
        }
        result = param._normalise_allowed_value(param_def, ['alice', 'DAVE', 'BoB'])
        assert result == ['Alice', 'Dave', 'Bob']
    
    def test_normalise_allowed_value_number(self):
        """Test that the _normalise_allowed_value helper returns NUMBER values unchanged.
        
        This test verifies that NUMBER parameter values are returned without modification
        since numeric values do not require case normalisation.
        This behaviour is expected because NUMBER values are exact matches and need no transformation.
        """
        setup_function()
        param_def = {
            PARAM_NAME: 'port',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_ALLOWED_VALUES: [80, 443, 8080, 8443]
        }
        assert param._normalise_allowed_value(param_def, 80) == 80
        assert param._normalise_allowed_value(param_def, 443) == 443
    
    def test_normalise_allowed_value_not_specified(self):
        """Test that the _normalise_allowed_value helper returns values unchanged when no allowed values specified.
        
        This test verifies that when PARAM_ALLOWED_VALUES is not defined,
        values are returned without any transformation.
        This behaviour is expected because normalisation only applies when allowed values are specified.
        """
        setup_function()
        param_def = {
            PARAM_NAME: 'value',
            PARAM_TYPE: PARAM_TYPE_TEXT
        }
        assert param._normalise_allowed_value(param_def, 'anything') == 'anything'
        assert param._normalise_allowed_value(param_def, 'AnyCase') == 'AnyCase'
    
    def test_set_param_with_allowed_values_valid(self):
        """Test that set_param successfully sets a parameter when the value is in the allowed values list.
        
        This test verifies that the set_param function accepts and stores valid values when
        a parameter has PARAM_ALLOWED_VALUES defined and the provided value is in that list.
        This behaviour is expected because valid values should pass through the validation pipeline and be stored correctly.
        """
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
    
    def test_set_param_with_allowed_values_case_insensitive(self):
        """Test that set_param normalises TEXT parameter values to canonical case.
        
        This test verifies that the set_param function performs case-insensitive matching and stores
        values in the canonical case from the allowed values list for TEXT parameters.
        This behaviour is expected because users should not need to match exact case, and canonical case ensures consistency.
        """
        setup_function()
        param.add_param({
            PARAM_NAME: 'log_level',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALLOWED_VALUES: ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        })
        # lowercase input normalised to uppercase canonical case
        param.set_param(param_name='log_level', value='debug')
        assert param.get_param(param_name='log_level') == 'DEBUG'
        
        param.set_param(param_name='log_level', value='WaRnInG')
        assert param.get_param(param_name='log_level') == 'WARNING'
    
    def test_set_param_list_with_allowed_values_valid(self):
        """Test that set_param successfully sets a LIST parameter when all elements are in the allowed values list.
        
        This test verifies that the set_param function validates and normalises LIST parameter elements,
        accepting lists where all elements are members of the allowed values list.
        This behaviour is expected because valid list elements should pass validation and be stored with normalised case.
        """
        setup_function()
        param.add_param({
            PARAM_NAME: 'features',
            PARAM_TYPE: PARAM_TYPE_LIST,
            PARAM_ALLOWED_VALUES: ['AUTH', 'API', 'DATABASE', 'CACHE']
        })
        # lowercase elements normalised to uppercase
        param.set_param(param_name='features', value=['auth', 'database'])
        result = param.get_param(param_name='features')
        assert result == ['AUTH', 'DATABASE']
    
    def test_set_param_list_invalid_element(self):
        """Test that set_param raises a ValueError when a LIST parameter contains an invalid element.
        
        This test verifies that the set_param function rejects lists containing any element not in the allowed values list,
        providing a clear error message indicating which element was invalid.
        This behaviour is expected because all list elements must be valid to enforce the whitelist constraint.
        """
        setup_function()
        param.add_param({
            PARAM_NAME: 'features',
            PARAM_TYPE: PARAM_TYPE_LIST,
            PARAM_ALLOWED_VALUES: ['auth', 'api', 'database', 'cache']
        })
        with pytest.raises(ValueError, match="List element 'invalid' not allowed for parameter 'features'"):
            param.set_param(param_name='features', value=['auth', 'invalid'])
    
    def test_set_param_list_empty(self):
        """Test that set_param raises a ValueError when a LIST parameter is set to an empty list.
        
        This test verifies that the set_param function rejects empty lists with a clear error message
        when a parameter has PARAM_ALLOWED_VALUES defined.
        This behaviour is expected because empty lists provide no valid configuration when allowed values are specified.
        """
        setup_function()
        param.add_param({
            PARAM_NAME: 'features',
            PARAM_TYPE: PARAM_TYPE_LIST,
            PARAM_ALLOWED_VALUES: ['auth', 'api', 'database', 'cache']
        })
        with pytest.raises(ValueError, match="Empty list not allowed for parameter 'features'"):
            param.set_param(param_name='features', value=[])
    
    def test_set_param_with_allowed_values_invalid(self):
        """Test that set_param raises a ValueError when the value is not in the allowed values list.
        
        This test verifies that the set_param function rejects invalid values with a clear error message
        when a parameter has PARAM_ALLOWED_VALUES defined and the provided value is not in that list.
        This behaviour is expected because invalid values must be rejected to enforce the whitelist constraint in the full parameter pipeline.
        """
        setup_function()
        param.add_param({
            PARAM_NAME: 'mode',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALLOWED_VALUES: ['fast', 'normal', 'slow']
        })
        with pytest.raises(ValueError, match="Value 'turbo' not allowed for parameter 'mode'"):
            param.set_param(param_name='mode', value='turbo')
    
    def test_add_param_default_in_allowed_values(self):
        """Test that add_param successfully registers a parameter when PARAM_DEFAULT is in the allowed values list.
        
        This test verifies that parameter registration succeeds when both PARAM_DEFAULT and PARAM_ALLOWED_VALUES
        are specified and the default value is a member of the allowed values list.
        This behaviour is expected because valid default values should not prevent parameter registration.
        """
        setup_function()
        # Should not raise
        param.add_param({
            PARAM_NAME: 'level',
            PARAM_TYPE: PARAM_TYPE_NUMBER,
            PARAM_ALLOWED_VALUES: [1, 2, 3, 4, 5],
            PARAM_DEFAULT: 3
        })
    
    def test_add_param_default_normalised(self):
        """Test that add_param normalises TEXT default values to canonical case.
        
        This test verifies that when registering a parameter with both PARAM_DEFAULT and PARAM_ALLOWED_VALUES,
        the default value is normalised to the canonical case from the allowed values list.
        This behaviour is expected because consistent canonical case should be stored for TEXT defaults.
        """
        setup_function()
        param.add_param({
            PARAM_NAME: 'log_level',
            PARAM_TYPE: PARAM_TYPE_TEXT,
            PARAM_ALLOWED_VALUES: ['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            PARAM_DEFAULT: 'info'  # lowercase
        })
        # Should be normalised to uppercase
        assert param.get_param(param_name='log_level') == 'INFO'
    
    def test_add_param_list_default_normalised(self):
        """Test that add_param normalises LIST default element values to canonical case.
        
        This test verifies that when registering a LIST parameter with both PARAM_DEFAULT and PARAM_ALLOWED_VALUES,
        all default list elements are normalised to the canonical case from the allowed values list.
        This behaviour is expected because consistent canonical case should be stored for LIST defaults.
        """
        setup_function()
        param.add_param({
            PARAM_NAME: 'features',
            PARAM_TYPE: PARAM_TYPE_LIST,
            PARAM_ALLOWED_VALUES: ['AUTH', 'API', 'DATABASE', 'CACHE'],
            PARAM_DEFAULT: ['auth', 'database']  # lowercase
        })
        # Should be normalised to uppercase
        result = param.get_param(param_name='features')
        assert result == ['AUTH', 'DATABASE']
    
    def test_add_param_default_not_in_allowed_values(self):
        """Test that add_param raises a ValueError when PARAM_DEFAULT is not in the allowed values list.
        
        This test verifies that parameter registration fails with a clear error message when both PARAM_DEFAULT
        and PARAM_ALLOWED_VALUES are specified but the default value is not in the allowed list.
        This behaviour is expected because misconfigured defaults should be detected early at registration time to prevent runtime errors.
        """
        setup_function()
        with pytest.raises(ValueError, match="Value 10 not allowed for parameter 'level'"):
            param.add_param({
                PARAM_NAME: 'level',
                PARAM_TYPE: PARAM_TYPE_NUMBER,
                PARAM_ALLOWED_VALUES: [1, 2, 3, 4, 5],
                PARAM_DEFAULT: 10
            })
    
    def test_set_param_allowed_values_with_number_coercion(self):
        """Test that allowed values validation occurs after type coercion for NUMBER parameters.
        
        This test verifies that when setting a NUMBER parameter with a string value, the value is first
        coerced to an integer and then validated against the allowed values list.
        This behaviour is expected because type coercion must occur before validation to ensure string inputs from CLI are properly converted.
        """
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
- Only TEXT, NUMBER, and LIST params support allowed values
- TOGGLE params have implicit allowed values (True/False)
- DICT params not supported (use custom validation)
- TEXT and LIST validation uses case-insensitive matching with normalisation to canonical case

See [examples/params_allowed_values.py](../examples/params_allowed_values.py) for complete usage examples.
```

Add `PARAM_ALLOWED_VALUES` to Parameter Definition Constants table in the "Configuration Binding" section:

| Constant | Description |
|----------|-------------|
| `PARAM_ALLOWED_VALUES` | List of allowed values for TEXT, NUMBER, and LIST params. Value must be in this list. For TEXT and LIST, matching is case-insensitive with normalisation to canonical case. See [Allowed Values](#allowed-values) and [examples/params_allowed_values.py](../examples/params_allowed_values.py) for usage. |

**`doc/api-reference.md` updates:**

Add `PARAM_ALLOWED_VALUES` to Parameter Constants "Configuration Binding" table:

| Constant | Type | Description |
|----------|------|-------------|
| `PARAM_ALLOWED_VALUES` | list | Allowed values for TEXT/NUMBER/LIST params. For TEXT/LIST, case-insensitive matching with normalisation. See [Parameters Guide - Allowed Values](parameters.md#allowed-values) and [example](../examples/params_allowed_values.py) |

**`README.md` updates:**

Update "What's New in v1.1.0" section:

```markdown
- **Allowed Values Validation** - New `PARAM_ALLOWED_VALUES` constant restricts TEXT, NUMBER, and LIST parameters to predefined value sets. TEXT and LIST parameters use case-insensitive matching with automatic normalisation to canonical case. Provides clear error messages when invalid values are provided.
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

**Answer:** Yes, LIST params should support allowed values with element-wise validation.

**Rationale:**
- Common use case: restrict list elements to known set (e.g., tags must be from predefined list)
- Validates each element individually against allowed values
- Clear error messaging indicates which element failed validation
- Consistent with TEXT and NUMBER validation patterns

**Implementation:**
- Modify `_validate_allowed_values()` to handle LIST params
- When param type is LIST, iterate through list elements
- Validate each element against allowed values
- Raise `ValueError` identifying the invalid element: `f"List element '{element}' not allowed for parameter '{param_name}'. Allowed values: {allowed_values}"`
- Empty lists fail validation (no valid elements provided)

**Example:**
```python
{
    PARAM_NAME: 'tags',
    PARAM_TYPE: PARAM_TYPE_LIST,
    PARAM_ALLOWED_VALUES: ['python', 'cli', 'framework', 'testing'],
}
# Valid: --tags python cli framework
# Invalid: --tags python invalid_tag  # Error: element 'invalid_tag' not allowed
```

[↑ Back to top](#table-of-contents)

### 2. Case sensitivity for TEXT params

**Question:** Should allowed values validation be case-sensitive for TEXT parameters?

**Answer:** No, validation should be case-insensitive with automatic normalization to canonical case.

**Rationale:**
- User-friendly: Users don't need to remember exact casing ('prod' vs 'Prod' vs 'PROD')
- Common pattern: Environment names and config values typically case-insensitive
- Clear behavior: Input normalized to match allowed value's case
- Predictable: Always get canonical case from allowed values list

**Implementation:**
- Build case-insensitive lookup dict mapping lowercase → canonical value
- When validating, convert input to lowercase and look up canonical form
- Store canonical value (from allowed values list) in config
- Only applies when `PARAM_ALLOWED_VALUES` is specified
- Works for TEXT and LIST element validation

**Example:**
```python
{
    PARAM_NAME: 'environment',
    PARAM_TYPE: PARAM_TYPE_TEXT,
    PARAM_ALLOWED_VALUES: ['dev', 'staging', 'production'],
}
# Input: --env PROD → Stored: 'production' (normalized)
# Input: --env Dev → Stored: 'dev' (normalized)
```

[↑ Back to top](#table-of-contents)

### 3. Interaction with input filters

**Question:** How does `PARAM_ALLOWED_VALUES` interact with `PARAM_INPUT_FILTER`?

**Answer:** Input filters run first, then type validation, then allowed values validation.

**Rationale:**
- Input filters transform raw CLI strings to appropriate types
- Type validation coerces values to correct type
- Allowed values check validates the final typed value
- This order ensures consistency (e.g., filter transforms → type coerces → validate against allowed values)

**Implementation:**
- Order in `set_param_value()` / `join_param_value()`:
  1. Apply `PARAM_INPUT_FILTER` if specified (transforms raw input)
  2. Call `_validate_param_value()` for type validation
  3. Call `_validate_allowed_values()` for allowed values check
- Input filter can transform before allowed values validation runs
- Allows custom transformations before validation (e.g., strip whitespace, normalize format)

**Example:**

```python
def normalize_env(value):
    """Strip whitespace and convert to lowercase."""
    return value.strip().lower()

{
    PARAM_NAME: 'environment',
    PARAM_TYPE: PARAM_TYPE_TEXT,
    PARAM_INPUT_FILTER: normalize_env,
    PARAM_ALLOWED_VALUES: ['dev', 'staging', 'production'],
}
# CLI: --env " PROD " → filter → "prod" → case-insensitive match → stored: "production"
```

[↑ Back to top](#table-of-contents)

## Success Criteria

- [ ] `PARAM_ALLOWED_VALUES` constant added to `src/spafw37/constants/param.py`
- [ ] `_normalise_text_to_allowed_case()` helper function implemented in `src/spafw37/param.py`
- [ ] `_validate_allowed_values()` helper function implemented with TEXT case-insensitive matching and LIST element validation
- [ ] `_normalise_allowed_value()` helper function implemented to normalise values to canonical case after validation
- [ ] `_validate_param_value()` modified to call `_validate_allowed_values()` then `_normalise_allowed_value()`
- [ ] Default value validation added to `add_param()` with validation and normalisation for TEXT and LIST defaults
- [ ] Test class `TestParamAllowedValues` added with 26+ tests covering:
  - Valid TEXT/NUMBER/LIST validation
  - Invalid TEXT/NUMBER/LIST validation
  - Empty LIST rejection
  - TEXT value normalisation to canonical case
  - TEXT mixed-case canonical value preservation
  - LIST element normalisation to canonical case
  - LIST mixed-case canonical value preservation
  - NUMBER values returned unchanged by normalisation
  - No allowed values specified
  - TOGGLE/DICT params skip validation
  - Integration with `set_param()` for TEXT, NUMBER, and LIST
  - Default value validation and normalisation for TEXT and LIST
  - Type coercion before validation
- [ ] Example `params_allowed_values.py` created demonstrating usage with TEXT, NUMBER, and LIST parameters
- [ ] `examples/README.md` updated with new example entry
- [ ] `doc/parameters.md` updated with "Allowed Values" section noting TEXT/NUMBER/LIST support and case-insensitivity
- [ ] `doc/api-reference.md` updated with `PARAM_ALLOWED_VALUES` constant entry noting case-insensitive matching
- [ ] `README.md` updated with "What's New" entry mentioning TEXT/NUMBER/LIST support and case-insensitivity
- [ ] All existing tests still passing
- [ ] Overall test coverage remains above 80%
- [ ] Issue #33 closed with reference to implementation

[↑ Back to top](#table-of-contents)

---

## CHANGES for v1.1.0 Release

Issue #33: Param Allowed Values

### Issues Closed

- #33: Param Allowed Values

### Additions

- `PARAM_ALLOWED_VALUES` constant restricts TEXT, NUMBER, and LIST parameter values to predefined sets. For TEXT and LIST parameters, matching is case-insensitive with automatic normalisation to the canonical case from the allowed values list. Values not in the allowed list are rejected with clear error messages. Default values are validated and normalised at parameter registration time.
- `_normalise_text_to_allowed_case()` helper function performs case-insensitive matching against allowed values and returns the canonical case. Uses linear search through allowed values list for simplicity and low memory overhead.
- `_validate_allowed_values()` helper function validates that parameter value is in allowed values list. For TEXT parameters, performs case-insensitive matching. For LIST parameters, validates each element individually. For NUMBER parameters, performs exact match. Does not modify values - raises ValueError if validation fails.
- `_normalise_allowed_value()` helper function normalises validated values to canonical case. For TEXT parameters, returns canonical case from allowed values. For LIST parameters, returns list with each element normalised to canonical case. For NUMBER parameters, returns value unchanged. Should only be called after validation passes.
- `_TYPE_VALIDATORS` module-level dict maps parameter types to validation functions.

### Removals

None.

### Changes

- `_validate_param_value()` refactored to use `_TYPE_VALIDATORS` dict lookup instead of if-elif chain. Calls `_validate_allowed_values()` after type validation, then `_normalise_allowed_value()` to get canonical case values.
- `add_param()` validates that `PARAM_DEFAULT` is in `PARAM_ALLOWED_VALUES` when both are specified, then normalises and stores the canonical case default for TEXT and LIST parameters.

### Migration

No migration required. New functionality only.

### Documentation

- `doc/parameters.md` added "Allowed Values" section with usage examples covering TEXT, NUMBER, and LIST parameters. Notes case-insensitive matching for TEXT and LIST.
- `doc/parameters.md` added `PARAM_ALLOWED_VALUES` to Parameter Definition Constants table, noting TEXT/NUMBER/LIST support and case-insensitivity.
- `doc/api-reference.md` added `PARAM_ALLOWED_VALUES` to Parameter Constants table, noting case-insensitive matching for TEXT/LIST.
- `README.md` added "Allowed Values Validation" to "What's New in v1.1.0" section, mentioning TEXT/NUMBER/LIST support and case-insensitive normalisation.
- `README.md` added `params_allowed_values.py` to examples list.
- `examples/README.md` added `params_allowed_values.py` entry.
- `examples/params_allowed_values.py` demonstrates usage with environment, region, port, size, and features parameters, including case-insensitive matching and LIST validation.

### Testing

- 26+ new tests in `tests/test_param_validation.py`
- Tests cover valid/invalid values for TEXT, NUMBER, and LIST types
- Tests verify validation correctly rejects invalid values
- Tests verify normalisation correctly converts to canonical case
- Tests verify mixed-case canonical value preservation (e.g., 'dave' → 'Dave')
- Tests verify element-wise validation and normalisation for LIST parameters
- Tests verify mixed-case canonical value preservation in LIST elements
- Tests verify empty LIST rejection when allowed values specified
- Tests verify TOGGLE/DICT types skip validation
- Tests verify integration with `set_param()` and `add_param()`
- Tests verify type coercion occurs before validation
- Tests verify default value validation and normalisation at registration time

---

Full changelog: https://github.com/minouris/spafw37/compare/v1.0.0...v1.1.0  
Issues: https://github.com/minouris/spafw37/issues/33

[↑ Back to top](#table-of-contents)
