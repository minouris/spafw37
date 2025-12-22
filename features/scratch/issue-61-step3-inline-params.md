# Step 3: Inline Parameter Processing

This file contains the TDD implementation for extracting inline parameter processing from `add_command()`.

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

See `issue-61-step1-imports.md` for all required imports.

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
    
    result = command._normalise_param_list(param_list)
    
    assert result == ['param1', 'param2']
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
