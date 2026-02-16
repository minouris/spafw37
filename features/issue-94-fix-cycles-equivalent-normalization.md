# Issue #94: Bug: _cycles_are_equivalent() does not normalize CYCLE_COMMAND for comparison

**GitHub Issue:** https://github.com/minouris/spafw37/issues/94

## Overview

## Problem Statement

The `_cycles_are_equivalent()` function in `src/spafw37/cycle.py` performs direct value comparison for all cycle fields, including CYCLE_COMMAND. This means it does not normalize CYCLE_COMMAND values before comparing them.

As a result, semantically equivalent cycles are incorrectly flagged as conflicting when one uses a string reference and the other uses an inline command dict.

## Current Behaviour

Two cycles that reference the same command are considered **different** if they use different formats for CYCLE_COMMAND:

```python
# Cycle 1: String reference
cycle1 = {
    CYCLE_COMMAND: 'my-cmd',
    CYCLE_NAME: 'test-cycle',
    CYCLE_LOOP: loop_func
}

# Cycle 2: Inline dict reference (same command)
cycle2 = {
    CYCLE_COMMAND: {'command-name': 'my-cmd'},
    CYCLE_NAME: 'test-cycle', 
    CYCLE_LOOP: loop_func
}

# Result: False (incorrectly flagged as different)
_cycles_are_equivalent(cycle1, cycle2)  # Returns False
```

This would raise a "Conflicting cycle definitions" ValueError when registering a command.

## Expected Behaviour

The function should normalize CYCLE_COMMAND values to command names before comparison, allowing semantic equivalence:

```python
# Should return True because both reference 'my-cmd'
_cycles_are_equivalent(cycle1, cycle2)  # Should return True
```

## Root Cause

The equivalency function (lines 132-157 in `src/spafw37/cycle.py`) performs simple value comparison:

```python
for key in cycle1:
    cycle1_field_value = cycle1[key]
    cycle2_field_value = cycle2[key]
    
    if callable(cycle1_field_value) and callable(cycle2_field_value):
        if cycle1_field_value is not cycle2_field_value:
            return False
    elif cycle1_field_value != cycle2_field_value:  # String != Dict -> False
        return False
```

## Suggested Fix

Use `_extract_command_name()` to normalize CYCLE_COMMAND values before comparison:

```python
def _fields_are_equivalent(field_key, cycle1_field_value, cycle2_field_value):
    """Check if two cycle field values are semantically equivalent.
    
    Normalises CYCLE_COMMAND values to command names and uses object identity
    for callable comparisons.
    """
    # Handle CYCLE_COMMAND with normalisation
    if field_key == CYCLE_COMMAND:
        return _cycle_commands_match(cycle1_field_value, cycle2_field_value)
    
    # Handle callables with identity comparison
    if callable(cycle1_field_value) and callable(cycle2_field_value):
        return cycle1_field_value is cycle2_field_value
    
    # Handle regular values with equality comparison
    return cycle1_field_value == cycle2_field_value


def _cycles_are_equivalent(cycle1, cycle2):
    if set(cycle1.keys()) != set(cycle2.keys()):
        return False
    
    for key in cycle1:
        if not _fields_are_equivalent(key, cycle1[key], cycle2[key]):
            return False
    
    return True
```

## Impact

**Priority:** High - This is a semantic correctness issue in the new add_cycle() API introduced in v1.1.0.

**Likelihood:** Low - In typical usage, both top-level and inline cycles would use the same format (usually strings).

**Why blocker for v1.1.0:**
- This bug exists in new API code being released in v1.1.0
- It violates the principle of semantic equivalence
- It could cause confusing "conflicting cycles" errors in edge cases
- Better to fix before the API is released than maintain incorrect behaviour

## Related

- Introduced in: Issue #63 (Add top-level add_cycles() API)
- Discovered in: Implementation Step 3.1 (command registration integration)
- Documented in: `features/scratch/issue-63/implementation-log.md` as Error #4

## Acceptance Criteria

- [ ] `_cycles_are_equivalent()` normalizes CYCLE_COMMAND values using `_extract_command_name()`
- [ ] Test added: String CYCLE_COMMAND vs inline dict CYCLE_COMMAND are equivalent
- [ ] Test added: Different command names (regardless of format) are not equivalent  
- [ ] All existing tests continue to pass
- [ ] Test coverage remains above 95%

**Key architectural decisions:**

- **Semantic equivalence:** CYCLE_COMMAND values must be normalised to command names before comparison, allowing string references and inline dict definitions to be recognised as equivalent when they reference the same command
- **Reuse existing logic:** The `_extract_command_name()` helper already handles normalisation for all CYCLE_COMMAND formats, ensuring consistent behaviour across the cycle API
- **Minimal scope:** Only the comparison logic in `_cycles_are_equivalent()` needs modification. The function already handles callable comparisons specially; this extends special handling to CYCLE_COMMAND fields
- **Backward compatibility:** Existing cycles using consistent formats (all strings or all dicts) continue to work unchanged. This fix only affects mixed-format scenarios that currently (incorrectly) fail

## Table of Contents

- [Overview](#overview)
- [Implementation Steps](#implementation-steps)
  - [1. Modify _cycles_are_equivalent() to normalize CYCLE_COMMAND values](#1-modify-_cycles_are_equivalent-to-normalize-cycle_command-values)
    - [Algorithm](#algorithm)
    - [Implementation order](#implementation-order)
    - [Code 1.1.1: Add _cycle_commands_match() helper to src/spafw37/cycle.py](#code-111-add-_cycle_commands_match-helper-to-srcspafw37cyclepy)
    - [Test 1.1.2: test_cycle_commands_match_with_same_string](#test-112-test_cycle_commands_match_with_same_string)
    - [Code 1.1.2: Test for _cycle_commands_match() with same string references](#code-112-test-for-_cycle_commands_match-with-same-string-references)
    - [Test 1.1.3: test_cycle_commands_match_with_string_and_dict_same_command](#test-113-test_cycle_commands_match_with_string_and_dict_same_command)
    - [Code 1.1.3: Test for _cycle_commands_match() with string and dict same command](#code-113-test-for-_cycle_commands_match-with-string-and-dict-same-command)
    - [Test 1.1.4: test_cycle_commands_match_with_different_commands](#test-114-test_cycle_commands_match_with_different_commands)
    - [Code 1.1.4: Test for _cycle_commands_match() with different commands](#code-114-test-for-_cycle_commands_match-with-different-commands)
    - [Code 1.2.1: Modify _cycles_are_equivalent() in src/spafw37/cycle.py](#code-121-modify-_cycles_are_equivalent-in-srcspafw37cyclepy)
  - [2. Add tests for CYCLE_COMMAND normalisation in equivalence checks](#2-add-tests-for-cycle_command-normalisation-in-equivalence-checks)
    - [Implementation order](#implementation-order-1)
    - [Test 2.1.1: test_cycles_are_equivalent_normalizes_string_vs_dict_same_command](#test-211-test_cycles_are_equivalent_normalizes_string_vs_dict_same_command)
    - [Code 2.1.1: Test for _cycles_are_equivalent() with string vs dict same command](#code-211-test-for-_cycles_are_equivalent-with-string-vs-dict-same-command)
    - [Test 2.1.2: test_cycles_are_equivalent_normalizes_dict_vs_string_same_command](#test-212-test_cycles_are_equivalent_normalizes_dict_vs_string_same_command)
    - [Code 2.1.2: Test for _cycles_are_equivalent() with dict vs string same command](#code-212-test-for-_cycles_are_equivalent-with-dict-vs-string-same-command)
    - [Test 2.1.3: test_cycles_are_equivalent_normalizes_string_vs_dict_different_commands](#test-213-test_cycles_are_equivalent_normalizes_string_vs_dict_different_commands)
    - [Code 2.1.3: Test for _cycles_are_equivalent() with string vs dict different commands](#code-213-test-for-_cycles_are_equivalent-with-string-vs-dict-different-commands)
    - [Test 2.1.4: test_cycles_are_equivalent_normalizes_dict_vs_dict_same_command](#test-214-test_cycles_are_equivalent_normalizes_dict_vs_dict_same_command)
    - [Code 2.1.4: Test for _cycles_are_equivalent() with dict vs dict same command (regression)](#code-214-test-for-_cycles_are_equivalent-with-dict-vs-dict-same-command-regression)
    - [Test 2.1.5: test_cycles_are_equivalent_normalizes_dict_vs_dict_different_commands](#test-215-test_cycles_are_equivalent_normalizes_dict_vs_dict_different_commands)
    - [Code 2.1.5: Test for _cycles_are_equivalent() with dict vs dict different commands (regression)](#code-215-test-for-_cycles_are_equivalent-with-dict-vs-dict-different-commands-regression)
  - [3. Documentation Updates](#3-documentation-updates)
- [Further Considerations](#further-considerations)
- [Success Criteria](#success-criteria)
- [Planning Checklist](#planning-checklist)
- [Implementation Log](#implementation-log)
- [Implementation Checklist](#implementation-checklist)
- [CHANGES for v1.1.0 Release](#changes-for-v110-release)

## Implementation Steps

### 1. Modify _cycles_are_equivalent() to normalize CYCLE_COMMAND values

**File:** `src/spafw37/cycle.py`

Modify the `_cycles_are_equivalent()` function to use `_extract_command_name()` for normalizing CYCLE_COMMAND values before comparison. This allows cycles that reference the same command via different formats (string vs inline dict) to be recognised as equivalent.

The comparison should extract command names from both CYCLE_COMMAND values and compare the normalised names, rather than comparing the raw values directly.

#### Algorithm

The function currently performs direct value comparison for all cycle fields:

```python
for key in cycle1:
    cycle1_field_value = cycle1[key]
    cycle2_field_value = cycle2[key]
    
    if callable(cycle1_field_value) and callable(cycle2_field_value):
        if cycle1_field_value is not cycle2_field_value:
            return False
    elif cycle1_field_value != cycle2_field_value:  # Direct comparison - fails for string vs dict
        return False
```

The modified algorithm extracts the field comparison logic to a helper function, allowing CYCLE_COMMAND normalisation without violating nesting limits:

```python
for key in cycle1:
    if not _fields_are_equivalent(key, cycle1[key], cycle2[key]):
        return False
```

Helper functions:

```python
def _fields_are_equivalent(field_key, cycle1_field_value, cycle2_field_value):
    """Check if two cycle field values are semantically equivalent."""
    # Handle CYCLE_COMMAND with normalisation
    if field_key == CYCLE_COMMAND:
        return _cycle_commands_match(cycle1_field_value, cycle2_field_value)
    
    # Handle callables with identity comparison
    if callable(cycle1_field_value) and callable(cycle2_field_value):
        return cycle1_field_value is cycle2_field_value
    
    # Handle regular values with equality comparison
    return cycle1_field_value == cycle2_field_value


def _cycle_commands_match(command_ref1, command_ref2):
    """Check if two CYCLE_COMMAND references are semantically equivalent.
    
    Normalises both values to command names and compares them.
    """
    command_name1 = _extract_command_name(command_ref1)
    command_name2 = _extract_command_name(command_ref2)
    return command_name1 == command_name2
```

This approach:
1. Extracts field comparison logic to `_fields_are_equivalent` helper (respects 2-line nested block limit)
2. Helper delegates CYCLE_COMMAND comparison to `_cycle_commands_match` for normalisation
3. `_cycle_commands_match` uses existing `_extract_command_name()` for normalisation
4. Compares normalised command names instead of raw values
5. Preserves existing behaviour for callables (identity check) and primitives (equality check)
6. Maintains max 2-level nesting throughout (no nested blocks exceed 2 lines)

#### Implementation order

1. Add helper function `_cycle_commands_match()` (Code 1.1.1)
2. Add tests for `_cycle_commands_match()` (Code 1.1.2, 1.1.3, 1.1.4)
3. Modify `_cycles_are_equivalent()` to use helper (Code 1.2.1)
4. Existing tests verify unchanged behaviour for non-CYCLE_COMMAND fields

#### Code 1.1.1: Add _cycle_commands_match() helper to src/spafw37/cycle.py

```python
# Block 1.1.1: Add helper to check if two CYCLE_COMMAND references match (insert before _cycles_are_equivalent)

def _cycle_commands_match(command_ref1, command_ref2):
    """Check if two CYCLE_COMMAND references are semantically equivalent.
    
    Normalises both command references to their command names and compares them.
    This allows string references and inline dict definitions to be recognised as
    equivalent when they reference the same command.
    
    Args:
        command_ref1: First command reference (string or dict)
        command_ref2: Second command reference (string or dict)
    
    Returns:
        True if both references point to the same command name, False otherwise
    """
    command_name1 = _extract_command_name(command_ref1)
    command_name2 = _extract_command_name(command_ref2)
    return command_name1 == command_name2
```

#### Test 1.1.2: test_cycle_commands_match_with_same_string

```gherkin
Scenario: Two string command references with same name match
  Given two CYCLE_COMMAND values both as string 'my-command'
  When _cycle_commands_match is called
  Then it should return True
  
  # Tests: Helper correctly compares two string references
  # Validates: String-to-string comparison works
```

#### Code 1.1.2: Test for _cycle_commands_match() with same string references

```python
# Block 1.1.2: Test _cycle_commands_match with same string references
def test_cycle_commands_match_with_same_string():
    """Test that two string command references with same name match.
    
    This test verifies that the helper correctly identifies two string command
    references as matching when they have the same name.
    
    This behaviour is expected to ensure string-to-string comparison works.
    """
    commands_match = cycle._cycle_commands_match('my-command', 'my-command')
    
    assert commands_match is True
```

#### Test 1.1.3: test_cycle_commands_match_with_string_and_dict_same_command

```gherkin
Scenario: String and dict command references with same name match
  Given CYCLE_COMMAND as string 'my-command'
  And CYCLE_COMMAND as dict {COMMAND_NAME: 'my-command'}
  When _cycle_commands_match is called
  Then it should return True
  
  # Tests: Helper normalises mixed formats correctly
  # Validates: String and dict references to same command are recognised as matching
```

#### Code 1.1.3: Test for _cycle_commands_match() with string and dict same command

```python
# Block 1.1.3: Test _cycle_commands_match with string and dict same command
def test_cycle_commands_match_with_string_and_dict_same_command():
    """Test that string and dict command references with same name match.
    
    This test verifies that the helper normalises both string and dict formats
    and correctly identifies them as matching when they reference the same command.
    
    This behaviour is expected to support semantic equivalence across formats.
    """
    string_ref = 'my-command'
    dict_ref = {COMMAND_NAME: 'my-command'}
    
    commands_match = cycle._cycle_commands_match(string_ref, dict_ref)
    
    assert commands_match is True
```

#### Test 1.1.4: test_cycle_commands_match_with_different_commands

```gherkin
Scenario: Command references with different names do not match
  Given CYCLE_COMMAND as string 'command-one'
  And CYCLE_COMMAND as dict {COMMAND_NAME: 'command-two'}
  When _cycle_commands_match is called
  Then it should return False
  
  # Tests: Helper detects different command names
  # Validates: Different commands are not incorrectly matched
```

#### Code 1.1.4: Test for _cycle_commands_match() with different commands

```python
# Block 1.1.4: Test _cycle_commands_match with different commands
def test_cycle_commands_match_with_different_commands():
    """Test that command references with different names do not match.
    
    This test verifies that the helper correctly identifies command references
    as non-matching when they refer to different command names.
    
    This behaviour is expected to prevent false positives in equivalence checking.
    """
    string_ref = 'command-one'
    dict_ref = {COMMAND_NAME: 'command-two'}
    
    commands_match = cycle._cycle_commands_match(string_ref, dict_ref)
    
    assert commands_match is False
```

#### Code 1.2.1: Modify _cycles_are_equivalent() in src/spafw37/cycle.py

```python
# Block 1.2.1: Modify _cycles_are_equivalent() to use helper for CYCLE_COMMAND comparison (lines 126-157)

def _fields_are_equivalent(field_key, cycle1_field_value, cycle2_field_value):
    """Check if two cycle field values are semantically equivalent.
    
    Normalises CYCLE_COMMAND values to command names before comparison. Uses object
    identity for callable comparisons and equality for regular values.
    
    Args:
        field_key: The cycle field key being compared
        cycle1_field_value: Field value from first cycle
        cycle2_field_value: Field value from second cycle
    
    Returns:
        True if field values are equivalent, False otherwise
    """
    # Block 1.2.1.1: Handle CYCLE_COMMAND with normalisation
    if field_key == CYCLE_COMMAND:
        return _cycle_commands_match(cycle1_field_value, cycle2_field_value)
    
    # Block 1.2.1.2: Handle callables with identity comparison
    if callable(cycle1_field_value) and callable(cycle2_field_value):
        return cycle1_field_value is cycle2_field_value
    
    # Block 1.2.1.3: Handle regular values with equality comparison
    return cycle1_field_value == cycle2_field_value


def _cycles_are_equivalent(cycle1, cycle2):
    """Check if two cycle definitions are equivalent.
    
    Performs deep equality comparison including:
    - All keys (required and optional fields)
    - Primitive values (strings, numbers, bools)
    - Function references (using object identity)
    - Nested structures (lists, dicts)
    - CYCLE_COMMAND values (normalized to command names)
    
    Args:
        cycle1: First cycle definition dict
        cycle2: Second cycle definition dict
    
    Returns:
        True if cycles are equivalent, False otherwise
    """
    if set(cycle1.keys()) != set(cycle2.keys()):
        return False
    
    # Block 1.2.1.4: Check each field using helper (max 2-line loop body)
    for key in cycle1:
        if not _fields_are_equivalent(key, cycle1[key], cycle2[key]):
            return False
    
    return True
```

**Tests:** Unit tests already exist for `_cycles_are_equivalent()` in `tests/test_cycle.py`. The existing tests cover:
- Identical cycles (both string format)
- Different required fields
- Different optional fields
- Function reference comparison

These tests will continue to pass after the modification, confirming backward compatibility. New tests will be added in Step 2 to verify normalisation behaviour.

[↑ Back to top](#table-of-contents)

### 2. Add tests for CYCLE_COMMAND normalisation in equivalence checks

**File:** `tests/test_cycle.py`

Add comprehensive tests to verify that `_cycles_are_equivalent()` correctly normalises CYCLE_COMMAND values:

1. **Equivalent cycles with different formats:** String CYCLE_COMMAND vs inline dict CYCLE_COMMAND referencing the same command name should return True
2. **Different commands regardless of format:** String vs inline dict referencing different command names should return False
3. **Edge case validation:** Ensure function handles both string-to-string and dict-to-dict comparisons correctly (regression tests)

#### Implementation order

1. Add module-level imports (already present in `tests/test_cycle.py`)
2. Add test function 2.1.1 - String vs dict same command (Test 2.1.1)
3. Add test function 2.1.2 - Dict vs string same command (Test 2.1.2)
4. Add test function 2.1.3 - String vs dict different commands (Test 2.1.3)
5. Add test function 2.1.4 - Dict vs dict same command regression (Test 2.1.4)
6. Add test function 2.1.5 - Dict vs dict different commands regression (Test 2.1.5)

**Module-level imports:** Already present in `tests/test_cycle.py`:

```python
# Existing imports in tests/test_cycle.py (no changes needed)
import pytest
from spafw37 import cycle
from spafw37.constants.cycle import (
    CYCLE_COMMAND,
    CYCLE_NAME,
    CYCLE_LOOP,
    CYCLE_INIT,
    CYCLE_LOOP_START,
    CYCLE_LOOP_END,
    CYCLE_END,
    CYCLE_COMMANDS
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_ACTION,
    COMMAND_PHASE,
    COMMAND_INVOCABLE
)
```

**Tests:** This step adds new test functions to validate CYCLE_COMMAND normalisation.

#### Test 2.1.1: test_cycles_are_equivalent_normalizes_string_vs_dict_same_command

```gherkin
Scenario: String and dict CYCLE_COMMAND with same command name are equivalent
  Given a cycle with CYCLE_COMMAND as string 'my-command'
  And another cycle with CYCLE_COMMAND as inline dict {'command-name': 'my-command'}
  And both cycles have identical CYCLE_NAME and CYCLE_LOOP
  When _cycles_are_equivalent is called with both cycles
  Then it should return True
  
  # Tests: CYCLE_COMMAND normalisation for semantic equivalence
  # Validates: Cycles referencing the same command via different formats are recognised as equivalent
```

#### Code 2.1.1: Test for _cycles_are_equivalent() with string vs dict same command

```python
# Block 2.1.1: Test string vs dict CYCLE_COMMAND with same command name
def test_cycles_are_equivalent_normalizes_string_vs_dict_same_command():
    """Test that string and dict CYCLE_COMMAND with same name are equivalent.
    
    This test verifies that _cycles_are_equivalent normalises CYCLE_COMMAND values
    before comparison, recognising a string reference and inline dict definition as
    equivalent when they reference the same command name.
    
    This behaviour is expected because the framework should support semantic
    equivalence regardless of CYCLE_COMMAND format.
    """
    loop_function = lambda: True
    
    cycle_with_string = {
        CYCLE_COMMAND: 'my-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    cycle_with_dict = {
        CYCLE_COMMAND: {COMMAND_NAME: 'my-command'},
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    are_equivalent = cycle._cycles_are_equivalent(cycle_with_string, cycle_with_dict)
    
    assert are_equivalent is True
```

#### Test 2.1.2: test_cycles_are_equivalent_normalizes_dict_vs_string_same_command

```gherkin
Scenario: Dict and string CYCLE_COMMAND with same command name are equivalent (order reversed)
  Given a cycle with CYCLE_COMMAND as inline dict {'command-name': 'my-command'}
  And another cycle with CYCLE_COMMAND as string 'my-command'
  And both cycles have identical CYCLE_NAME and CYCLE_LOOP
  When _cycles_are_equivalent is called with both cycles
  Then it should return True
  
  # Tests: CYCLE_COMMAND normalisation is symmetric (order independent)
  # Validates: Comparison works regardless of which cycle has string vs dict format
```

#### Code 2.1.2: Test for _cycles_are_equivalent() with dict vs string same command

```python
# Block 2.1.2: Test dict vs string CYCLE_COMMAND with same command name (symmetric)
def test_cycles_are_equivalent_normalizes_dict_vs_string_same_command():
    """Test that dict and string CYCLE_COMMAND with same name are equivalent.
    
    This test verifies that the normalisation is symmetric - it works correctly
    regardless of which cycle has the string format and which has the dict format.
    
    This behaviour is expected because equality should be commutative.
    """
    loop_function = lambda: True
    
    cycle_with_dict = {
        CYCLE_COMMAND: {COMMAND_NAME: 'my-command'},
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    cycle_with_string = {
        CYCLE_COMMAND: 'my-command',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    are_equivalent = cycle._cycles_are_equivalent(cycle_with_dict, cycle_with_string)
    
    assert are_equivalent is True
```

#### Test 2.1.3: test_cycles_are_equivalent_normalizes_string_vs_dict_different_commands

```gherkin
Scenario: String and dict CYCLE_COMMAND with different command names are not equivalent
  Given a cycle with CYCLE_COMMAND as string 'command-one'
  And another cycle with CYCLE_COMMAND as inline dict {'command-name': 'command-two'}
  And both cycles have identical CYCLE_NAME and CYCLE_LOOP
  When _cycles_are_equivalent is called with both cycles
  Then it should return False
  
  # Tests: CYCLE_COMMAND normalisation detects different command names
  # Validates: Cycles referencing different commands are recognised as non-equivalent regardless of format
```

#### Code 2.1.3: Test for _cycles_are_equivalent() with string vs dict different commands

```python
# Block 2.1.3: Test string vs dict CYCLE_COMMAND with different command names
def test_cycles_are_equivalent_normalizes_string_vs_dict_different_commands():
    """Test that string and dict CYCLE_COMMAND with different names are not equivalent.
    
    This test verifies that normalisation still correctly identifies cycles with
    different command names as non-equivalent, even when comparing mixed formats.
    
    This behaviour is expected because semantically different cycles should not
    be treated as equivalent.
    """
    loop_function = lambda: True
    
    cycle_with_string = {
        CYCLE_COMMAND: 'command-one',
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    cycle_with_dict = {
        CYCLE_COMMAND: {COMMAND_NAME: 'command-two'},
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    are_equivalent = cycle._cycles_are_equivalent(cycle_with_string, cycle_with_dict)
    
    assert are_equivalent is False
```

#### Test 2.1.4: test_cycles_are_equivalent_normalizes_dict_vs_dict_same_command

```gherkin
Scenario: Two dict CYCLE_COMMAND values with same command name are equivalent (regression)
  Given a cycle with CYCLE_COMMAND as inline dict {'command-name': 'my-command'}
  And another cycle with CYCLE_COMMAND as inline dict {'command-name': 'my-command'}
  And both cycles have identical CYCLE_NAME and CYCLE_LOOP
  When _cycles_are_equivalent is called with both cycles
  Then it should return True
  
  # Tests: Dict-to-dict comparison still works after normalisation changes
  # Validates: Regression test confirming dict comparison unchanged
```

#### Code 2.1.4: Test for _cycles_are_equivalent() with dict vs dict same command (regression)

```python
# Block 2.1.4: Test dict vs dict CYCLE_COMMAND with same command name (regression)
def test_cycles_are_equivalent_normalizes_dict_vs_dict_same_command():
    """Test that two dict CYCLE_COMMAND values with same name are equivalent.
    
    This test verifies that dict-to-dict comparison continues to work correctly
    after adding normalisation logic.
    
    This behaviour is expected as a regression test to confirm existing functionality
    is preserved.
    """
    loop_function = lambda: True
    
    cycle1 = {
        CYCLE_COMMAND: {COMMAND_NAME: 'my-command'},
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    cycle2 = {
        CYCLE_COMMAND: {COMMAND_NAME: 'my-command'},
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    are_equivalent = cycle._cycles_are_equivalent(cycle1, cycle2)
    
    assert are_equivalent is True
```

#### Test 2.1.5: test_cycles_are_equivalent_normalizes_dict_vs_dict_different_commands

```gherkin
Scenario: Two dict CYCLE_COMMAND values with different command names are not equivalent (regression)
  Given a cycle with CYCLE_COMMAND as inline dict {'command-name': 'command-one'}
  And another cycle with CYCLE_COMMAND as inline dict {'command-name': 'command-two'}
  And both cycles have identical CYCLE_NAME and CYCLE_LOOP
  When _cycles_are_equivalent is called with both cycles
  Then it should return False
  
  # Tests: Dict-to-dict comparison detects different command names
  # Validates: Regression test confirming dict comparison unchanged
```

#### Code 2.1.5: Test for _cycles_are_equivalent() with dict vs dict different commands (regression)

```python
# Block 2.1.5: Test dict vs dict CYCLE_COMMAND with different command names (regression)
def test_cycles_are_equivalent_normalizes_dict_vs_dict_different_commands():
    """Test that two dict CYCLE_COMMAND values with different names are not equivalent.
    
    This test verifies that dict-to-dict comparison correctly detects different
    command names after adding normalisation logic.
    
    This behaviour is expected as a regression test to confirm existing functionality
    is preserved.
    """
    loop_function = lambda: True
    
    cycle1 = {
        CYCLE_COMMAND: {COMMAND_NAME: 'command-one'},
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    cycle2 = {
        CYCLE_COMMAND: {COMMAND_NAME: 'command-two'},
        CYCLE_NAME: 'test-cycle',
        CYCLE_LOOP: loop_function
    }
    
    are_equivalent = cycle._cycles_are_equivalent(cycle1, cycle2)
    
    assert are_equivalent is False
```

[↑ Back to top](#table-of-contents)

### 3. Documentation Updates

**Files:** None

**No documentation updates required.**

This is an internal bug fix in a private helper function (`_cycles_are_equivalent()`) within the cycle module. The fix corrects semantic equivalence checking to properly handle mixed CYCLE_COMMAND formats (string vs inline dict).

**Why no documentation updates:**
- No user-facing behaviour changes - the bug affects only internal equivalence checking
- No new public APIs - all changes are to private functions (prefixed with `_`)
- No user-visible functionality added or modified
- The fix makes `add_cycle()` work correctly for edge cases that currently fail
- Users cannot directly call `_cycles_are_equivalent()` or `_cycle_commands_match()`

**Impact on users:**
- Transparent fix - users will not notice any difference in normal usage
- Prevents potential "Conflicting cycle definitions" errors in mixed-format scenarios
- Existing code continues to work identically

**Implementation order:**

No implementation steps required - documentation section exists only to explicitly document that no updates are needed.

[↑ Back to top](#table-of-contents)

## Further Considerations

**No further considerations identified.** 

The issue provides a complete problem statement, root cause analysis, and suggested fix. The implementation is straightforward:
- Reuse existing `_extract_command_name()` function for normalisation
- Add special handling for CYCLE_COMMAND key in the comparison loop
- Add comprehensive tests for mixed format scenarios

The fix follows existing patterns in the codebase and requires no architectural decisions beyond what is already specified in the issue.

[↑ Back to top](#table-of-contents)

## Success Criteria

This issue is considered successfully implemented when:

**Functional Requirements:**
- [ ] `_cycles_are_equivalent()` normalises CYCLE_COMMAND values using `_extract_command_name()` before comparison
- [ ] String CYCLE_COMMAND and inline dict CYCLE_COMMAND referencing the same command name are recognised as equivalent (returns True)
- [ ] String CYCLE_COMMAND and inline dict CYCLE_COMMAND referencing different command names are recognised as not equivalent (returns False)
- [ ] Cycles using identical formats (both strings or both dicts) continue to work correctly (regression test)
- [ ] Function handles edge cases without errors (malformed command references handled by `_extract_command_name()`)

**Compatibility Requirements:**
- [ ] All existing tests continue to pass
- [ ] Test coverage remains at or above 95%
- [ ] No changes to public API or user-facing behaviour
- [ ] Python 3.7.0+ compatibility maintained

**Quality Requirements:**
- [ ] Code follows Python 3.7.0 compatibility requirements (no walrus operator, no positional-only params)
- [ ] Test specifications follow Gherkin + Python format
- [ ] All code follows UK English spelling conventions
- [ ] No nesting violations (max 2 levels below function declaration)

[↑ Back to top](#table-of-contents)

---

## Planning Checklist

This checklist tracks completion of this planning document.

**Plan Structure:**
- [x] Overview section complete with architectural decisions
- [x] Program Flow Analysis not applicable (straightforward bug fix)
- [x] All implementation steps identified and outlined
- [x] Further Considerations documented (all marked PENDING or RESOLVED)
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
- [x] All affected documentation files identified (none - internal bug fix)
- [x] Example files planned (if needed) (none needed)
- [x] API reference updates planned (if needed) (none needed)
- [x] User guide updates planned (if needed) (none needed)

**Quality Verification:**
- [x] All code follows Python 3.7.0 compatibility requirements
- [x] All code follows UK English spelling conventions
- [x] No lazy naming (tmp, data, result, i, j, etc.)
- [x] All functions have proper docstrings
- [x] Regression tests planned for modified functions

**Ready for Implementation:**
- [x] Plan reviewed and approved (Step 7 complete - all standards met)
- [x] All Further Considerations resolved (none identified)
- [x] Success Criteria agreed upon
- [x] Implementation Checklist ready to execute

[↑ Back to top](#table-of-contents)

---

## Implementation Log

This section will record any errors, deviations, or unexpected issues encountered during implementation (Step 8).

**This section will be populated during Step 8: Implement from Plan.**

[↑ Back to top](#table-of-contents)

---

## Implementation Checklist

This checklist tracks the test-driven development workflow for implementing issue #94.

Each line item that requires action must have a checkbox [ ].

### Step 1: Modify _cycles_are_equivalent() to normalize CYCLE_COMMAND values

#### 1.1: `_cycle_commands_match()` helper

- [x] Write tests for `_cycle_commands_match()`
  - [x] Patch: Add `test_cycle_commands_match_with_same_string()` to `tests/test_cycle.py`
  - [x] Patch: Add `test_cycle_commands_match_with_string_and_dict_same_command()` to `tests/test_cycle.py`
  - [x] Patch: Add `test_cycle_commands_match_with_different_commands()` to `tests/test_cycle.py`
  - [x] Test run: `pytest tests/test_cycle.py::test_cycle_commands_match_with_same_string -v` (expect FAIL - red)
  - [x] Test run: `pytest tests/test_cycle.py::test_cycle_commands_match_with_string_and_dict_same_command -v` (expect FAIL - red)
  - [x] Test run: `pytest tests/test_cycle.py::test_cycle_commands_match_with_different_commands -v` (expect FAIL - red)
- [x] Implement `_cycle_commands_match()`
  - [x] Patch: Add `_cycle_commands_match()` to `src/spafw37/cycle.py` (before `_cycles_are_equivalent()`)
  - [x] Test run: `pytest tests/test_cycle.py::test_cycle_commands_match_with_same_string -v` (expect PASS - green)
  - [x] Test run: `pytest tests/test_cycle.py::test_cycle_commands_match_with_string_and_dict_same_command -v` (expect PASS - green)
  - [x] Test run: `pytest tests/test_cycle.py::test_cycle_commands_match_with_different_commands -v` (expect PASS - green)

#### 1.2: `_cycles_are_equivalent()` modification

- [x] Modify `_cycles_are_equivalent()` to use helper
  - [x] Patch: Modify `_cycles_are_equivalent()` in `src/spafw37/cycle.py` to use `_cycle_commands_match()` for CYCLE_COMMAND comparison
  - [x] Test run: `pytest tests/test_cycle.py::test_cycles_are_equivalent_returns_true_for_identical_cycles -v` (expect PASS - regression check)
  - [x] Test run: `pytest tests/test_cycle.py::test_cycles_are_equivalent_returns_false_for_different_required_fields -v` (expect PASS - regression check)
  - [x] Test run: `pytest tests/test_cycle.py::test_cycles_are_equivalent_returns_false_for_different_optional_fields -v` (expect PASS - regression check)
  - [x] Test run: `pytest tests/test_cycle.py::test_cycles_are_equivalent_compares_function_references -v` (expect PASS - regression check)

### Step 2: Add tests for CYCLE_COMMAND normalisation in equivalence checks

#### 2.1.1: `test_cycles_are_equivalent_normalizes_string_vs_dict_same_command()`

- [x] Write test for string vs dict same command
  - [x] Patch: Add `test_cycles_are_equivalent_normalizes_string_vs_dict_same_command()` to `tests/test_cycle.py`
  - [x] Test run: `pytest tests/test_cycle.py::test_cycles_are_equivalent_normalizes_string_vs_dict_same_command -v` (expect PASS after Step 1 implementation)

#### 2.1.2: `test_cycles_are_equivalent_normalizes_dict_vs_string_same_command()`

- [x] Write test for dict vs string same command (symmetric)
  - [x] Patch: Add `test_cycles_are_equivalent_normalizes_dict_vs_string_same_command()` to `tests/test_cycle.py`
  - [x] Test run: `pytest tests/test_cycle.py::test_cycles_are_equivalent_normalizes_dict_vs_string_same_command -v` (expect PASS after Step 1 implementation)

#### 2.1.3: `test_cycles_are_equivalent_normalizes_string_vs_dict_different_commands()`

- [x] Write test for string vs dict different commands
  - [x] Patch: Add `test_cycles_are_equivalent_normalizes_string_vs_dict_different_commands()` to `tests/test_cycle.py`
  - [x] Test run: `pytest tests/test_cycle.py::test_cycles_are_equivalent_normalizes_string_vs_dict_different_commands -v` (expect PASS after Step 1 implementation)

#### 2.1.4: `test_cycles_are_equivalent_normalizes_dict_vs_dict_same_command()`

- [x] Write test for dict vs dict same command (regression)
  - [x] Patch: Add `test_cycles_are_equivalent_normalizes_dict_vs_dict_same_command()` to `tests/test_cycle.py`
  - [x] Test run: `pytest tests/test_cycle.py::test_cycles_are_equivalent_normalizes_dict_vs_dict_same_command -v` (expect PASS after Step 1 implementation)

#### 2.1.5: `test_cycles_are_equivalent_normalizes_dict_vs_dict_different_commands()`

- [x] Write test for dict vs dict different commands (regression)
  - [x] Patch: Add `test_cycles_are_equivalent_normalizes_dict_vs_dict_different_commands()` to `tests/test_cycle.py`
  - [x] Test run: `pytest tests/test_cycle.py::test_cycles_are_equivalent_normalizes_dict_vs_dict_different_commands -v` (expect PASS after Step 1 implementation)

### Final Verification

- [x] All implementation steps completed
- [x] All tests passing
  - [x] Test run: `pytest tests/test_cycle.py -v`
  - [x] Test run: `pytest tests/ -v`
- [x] Coverage target met
  - [x] Test run: `pytest tests/ --cov=spafw37 --cov-report=term-missing` (expect ≥95%)
- [x] No regressions introduced
  - [x] Verify all existing `test_cycles_are_equivalent_*` tests still pass
  - [x] Verify existing cycle functionality unchanged
- [x] Code review checklist verified
  - [x] No inline imports (all imports at module level)
  - [x] No nesting violations (max 2 levels)
  - [x] No lazy naming
  - [x] UK English spelling throughout

[↑ Back to top](#table-of-contents)

## Implementation Log

### Error: 2026-02-16T16:30:00Z
**Checklist Item:** Write tests for `_cycle_commands_match()` - Add test_cycle_commands_match_with_same_string()
**Error:** `AttributeError: module 'spafw37.cycle' has no attribute 'setup_function'`
**Cause:** Plan document included `cycle.setup_function()` calls in test code, but this function doesn't exist in the codebase. The existing test suite uses a pytest fixture `reset_state()` with `autouse=True` instead, which runs automatically.
**Resolution:** Removed `cycle.setup_function()` calls from all three `_cycle_commands_match()` tests. The pytest fixture handles setup automatically.
**Deviation from Plan:** Test code modified - removed non-existent setup calls. No functional change to test logic.

[↑ Back to top](#table-of-contents)

---

## CHANGES for v1.1.0 Release

Issue #94: Bug: _cycles_are_equivalent() does not normalize CYCLE_COMMAND for comparison

### Issues Closed

- #94: Bug: _cycles_are_equivalent() does not normalize CYCLE_COMMAND for comparison

### Additions

- `_fields_are_equivalent()` internal helper function checks if two cycle field values are semantically equivalent, handling CYCLE_COMMAND normalisation, callable identity comparison, and regular value equality (internal use only).
- `_cycle_commands_match()` internal helper function checks if two CYCLE_COMMAND references are semantically equivalent by normalising both to command names (internal use only).

### Removals

None.

### Changes

- **Bug fix:** `_cycles_are_equivalent()` now normalises CYCLE_COMMAND values to command names before comparison, allowing cycles that reference the same command via different formats (string vs inline dict) to be recognised as equivalent.
- Cycles with string CYCLE_COMMAND `'my-command'` and inline dict CYCLE_COMMAND `{COMMAND_NAME: 'my-command'}` are now correctly identified as equivalent instead of incorrectly flagged as conflicting.
- Field comparison logic extracted to `_fields_are_equivalent()` helper to maintain 2-level nesting limit and improve code clarity.
- Comparison logic delegates to `_cycle_commands_match()` helper which uses existing `_extract_command_name()` function for normalisation.

### Migration

No migration required. This is a bug fix that corrects semantic equivalence checking in the cycle registration system. Existing code will continue to work identically.

The bug affected only edge cases where the same command was referenced using different formats (string reference vs inline dict definition) when registering multiple cycles. In typical usage, all cycles use consistent formats (usually strings), so most applications were unaffected.

### Documentation

No documentation changes required. This is an internal implementation fix in private helper functions with no user-facing API changes.

### Testing

- 3 new tests in `tests/test_cycle.py` covering `_cycle_commands_match()` helper behaviour:
  - `test_cycle_commands_match_with_same_string` - Verifies string-to-string comparison
  - `test_cycle_commands_match_with_string_and_dict_same_command` - Verifies mixed format with same command matches
  - `test_cycle_commands_match_with_different_commands` - Verifies different commands don't match
- 5 new tests in `tests/test_cycle.py` verifying `_cycles_are_equivalent()` normalisation:
  - `test_cycles_are_equivalent_normalizes_string_vs_dict_same_command` - String vs dict same command returns True
  - `test_cycles_are_equivalent_normalizes_dict_vs_string_same_command` - Dict vs string same command returns True (symmetric)
  - `test_cycles_are_equivalent_normalizes_string_vs_dict_different_commands` - String vs dict different commands returns False
  - `test_cycles_are_equivalent_normalizes_dict_vs_dict_same_command` - Dict vs dict same command returns True (regression)
  - `test_cycles_are_equivalent_normalizes_dict_vs_dict_different_commands` - Dict vs dict different commands returns False (regression)
- 4 existing tests in `tests/test_cycle.py` continue to pass as regression verification:
  - `test_cycles_are_equivalent_returns_true_for_identical_cycles` - Verifies string comparison unchanged
  - `test_cycles_are_equivalent_returns_false_for_different_required_fields` - Verifies field comparison unchanged
  - `test_cycles_are_equivalent_returns_false_for_different_optional_fields` - Verifies optional field comparison unchanged
  - `test_cycles_are_equivalent_compares_function_references` - Verifies callable comparison unchanged
- Tests cover string-to-string, dict-to-dict, and mixed format comparisons for both matching and non-matching command names
- All existing cycle equivalence tests pass unchanged, confirming backward compatibility
- Target: 95%+ coverage maintained

---

Full changelog: https://github.com/minouris/spafw37/compare/v1.0.1...v1.1.0
Issues: https://github.com/minouris/spafw37/issues/94

[↑ Back to top](#table-of-contents)
