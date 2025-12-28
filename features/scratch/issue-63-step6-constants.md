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
