---
applyTo: "features/**/*.md"
---

# Plan Document Structure Rules

These rules define the standard structure for implementation plan documents in the `features/` directory.

## ANTI-PATTERN: Step X-a/X-b Structure (PROHIBITED)

**NEVER organise steps as "Step Xa: Implementation" / "Step Xb: Tests".**

This groups all code together and all tests together, violating the fundamental principle that each function must be immediately followed by its tests.

**Example of PROHIBITED structure:**
```markdown
**Step 5a: Implement helpers**
Code 5.1.1: helper_one
Code 5.1.2: helper_two  
Code 5.1.3: helper_three

**Step 5b: Test helpers**
Test 5.1.4: test_helper_one
Test 5.1.5: test_helper_two
Test 5.1.6: test_helper_three
```

**Correct structure - REQUIRED:**
```markdown
**Step 5: Implement and test helpers**
Code 5.1.1: helper_one
Test 5.1.2: test_helper_one (scenario 1)
Test 5.1.3: test_helper_one (scenario 2)
Code 5.2.1: helper_two
Test 5.2.2: test_helper_two (scenario 1)
Code 5.3.1: helper_three
Test 5.3.2: test_helper_three (scenario 1)
```

**Red flag detection:** If you see or create section headers containing "Step Xa" or "Step Xb" where X is a number, you have violated this rule.

## CRITICAL: Code Quality Rules Apply to All Code

**ALL code in plan documents MUST comply with the code quality rules defined in `python.instructions.md`.**

This includes:
- **Maximum nesting depth: 2 levels below function declaration**
- **Maximum nested block size: 2 lines**
- **Single responsibility principle**
- **Descriptive naming requirements**
- **All other Python coding standards**

**Why this matters:** If planned code violates quality rules, the implemented code will inherit those violations. Design the architecture correctly from the start.

**What this means for plan documents:**
- When planning a function, design it with proper helper method extraction
- Show the helper methods in the plan, not just monolithic code
- Include helper method signatures, docstrings, and purposes
- Plan for testing each helper independently
- Apply the same nesting and complexity limits as production code

**Example - WRONG way to plan (violates nesting depth):**
```python
def process_items(items):
    """Process items from request."""
    for item in items:                          # Level 1
        if item.is_valid():                     # Level 2
            for record in item.records:         # Level 3 - PROHIBITED
                process_record(record)
                update_cache(record)
```

**Example - CORRECT way to plan (respects nesting limits):**
```python
def process_items(items):
    """Process a list of items."""
    for item in items:                          # Level 1
        if item.is_valid():                     # Level 2
            process_valid_item(item)

def process_valid_item(item):
    """Process a single valid item.
    
    Args:
        item: The item to process
    """
    for record in item.records:                 # Level 1
        process_and_cache_record(record)        # Level 2

def process_and_cache_record(record):
    """Process a record and update cache.
    
    Args:
        record: The record to process
    """
    process_record(record)
    update_cache(record)
```

**See `python.instructions.md` for complete rules and more examples.**

## Block Numbering in Code Specifications

**Purpose:** Block numbering (X.Y.Z.N format) serves as line number substitutes in fenced code blocks within markdown, where actual line numbers are unreliable.

**CRITICAL: Block numbers must be COMMENTS in the code, not markdown headings or docstring content.**

**Correct usage:**
```python
# Block 2.1.3: Add to src/spafw37/command.py after _validate_command_name()

def _validate_command_action(cmd):
    """Validate that command has an action function.
    
    Args:
        cmd: Command definition dict
    """
    # Block 2.1.3.1: Check if action exists
    if not cmd.get(COMMAND_ACTION):
        # Block 2.1.3.2: Raise error if missing
        raise ValueError("Command action is required")
```

**WRONG - numbers in docstring:**
```python
def _validate_command_action(cmd):
    """Validate that command has an action function.
    
    Block 2.1.3.1: Check if action exists
    Block 2.1.3.2: Raise error if missing
    """
    if not cmd.get(COMMAND_ACTION):
        raise ValueError("Command action is required")
```

**Benefits:**
1. Enables precise references without relying on line numbers
2. Numbering depth (X.Y.Z.N vs X.Y.Z.N.M) hints at nesting depth
3. Makes it easy to identify and discuss specific code sections
4. Helps expose nesting violations (deep numbering = deep nesting)

**Usage in reviews:** "Block 3.2.4.3 has 2-level nesting with a 3-line nested block" is precise and unambiguous.

## CRITICAL: Module-Level Imports in Plan Documents

**ALL imports MUST be shown at module level, NOT inside test functions.**

When writing test code blocks in plan documents:
1. Show a "Module-level imports" section at the start of the test file
2. List ALL imports that the test file will need
3. Test functions reference already-imported modules, NOT import them again

**Example - WRONG way (inline imports in tests):**
```python
# Test 3.1.2: Add to tests/test_param.py
def test_param_registration():
    """Test param registration works."""
    # Block 3.1.2.1: Import required modules ❌ WRONG
    from spafw37 import param
    from spafw37.constants.param import PARAM_NAME
    
    # Block 3.1.2.2: Register param
    param.add_param({PARAM_NAME: 'test'})
```

**Example - CORRECT way (module-level imports):**
```markdown
**Tests for Step 3: Param registration**

**File:** `tests/test_param.py`

Module-level imports:
```python
# Module-level imports for tests/test_param.py
from spafw37 import param
from spafw37.constants.param import PARAM_NAME, PARAM_TYPE
import pytest
```

**Test 3.1.2: Test param registration**

```python
# Test 3.1.2: Add to tests/test_param.py
def test_param_registration():
    """Test param registration works."""
    # Block 3.1.2.1: Clear existing params
    param._params = {}
    
    # Block 3.1.2.2: Register param
    param.add_param({PARAM_NAME: 'test'})
```
```

**Why this matters:**
- Violates Python coding standards (see `python.instructions.md` § ANTI-PATTERN: Inline Imports)
- Makes final implementation incorrect
- Tests are NOT exempt from import rules

**See `python.instructions.md` § ANTI-PATTERN: Inline Imports (PROHIBITED) for complete details.**

## Hierarchical Block Numbering System

### Code Block Format

```markdown
**Code X.Y.Z: function_name or description**

```python
# Block X.Y.Z
def function_name(parameters):
    """Docstring here."""
    # Block X.Y.Z.1: Description of this section
    first_statement()
    
    # Block X.Y.Z.2: Description of next section
    if condition:
        # Block X.Y.Z.2.1: Inside if block
        nested_statement()
    else:
        # Block X.Y.Z.2.2: Inside else block
        other_statement()
    
    # Block X.Y.Z.3: Final section
    return result
```

### Numbering Rules

- **X** = Implementation step number (1, 2, 3...)
- **Y** = Member within step (1, 2, 3...)
- **Z** = Code block within member
- **Test X.Y.Z** = Test for Code X.Y.Z

### Block Hierarchy

- Top-level: `# Block X.Y.Z`
- First nesting: `# Block X.Y.Z.1`, `# Block X.Y.Z.2`
- Second nesting: `# Block X.Y.Z.1.1`, `# Block X.Y.Z.1.2`
- Continue as needed for deeper nesting

### Block Comment Style

**Always include descriptive text:**

```python
# Block 3.4.1: Extract parameter name from definition
param_name = _param.get(PARAM_NAME)

# Block 3.4.2: Determine default value based on param type
if _is_toggle_param(_param):
    # Block 3.4.2.1: Handle toggle param default
    default_value = _get_param_default(_param, False)
```

## Implementation and Test Interweaving

**CRITICAL: This structure applies to plan documents (`features/**/*.md`) during the planning phase.**

Do not group all implementations together and then all tests together. Each function must be immediately followed by its tests before the next function is defined.

Code in implementation plan files should be split into a **single** code block per **function**, followed by one-to-many **single** Gherkin tests **immediately followed by their implementations**, proving that function works (function, gherkin 1, unit test 1, gherkin 2, unit test 2).

### Test Section Heading Format

**Test section headings must describe what is being tested, NOT the format of the test.**

- ✅ Correct: `**Test 2.6.3: Multiple choice selection by exact text**`
- ✅ Correct: `**Test 2.6.3: Tests for multiple choice selection by text**`
- ❌ Wrong: `**Test 2.6.3: Gherkin for multiple choice by text**`
- ❌ Wrong: `**Test 2.6.3: Python test for multiple choice**`

**Rationale:** Each test section contains BOTH Gherkin specification and Python implementation. The heading should describe the test scenario, not the format.

### Structure Pattern

````markdown
**Code X.Y.Z: function_name**

```python
# Block X.Y.Z
def function_name(parameters):
    """Implementation here."""
    pass
```

**Test X.Y.(Z+1): Test scenario for function_name**

```gherkin
Scenario: Description of test case
  Given some precondition
  When action is performed
  Then expected result occurs
  
  # Tests: What is being tested
  # Validates: What is being validated
```

```python
# Test X.Y.(Z+1)
def test_function_name_scenario_1():
    """Test description."""
    # Test implementation
    assert something
```

**Test X.Y.(Z+2): Another scenario for function_name**

```gherkin
Scenario: Another test case
  Given different precondition
  When different action
  Then different result
```

```python
# Test X.Y.(Z+2)
def test_function_name_scenario_2():
    """Test description."""
    # Test implementation
    assert something_else
```

**Code X.(Y+1).Z: next_function**

```python
# Block X.(Y+1).Z
def next_function(parameters):
    """Next function implementation."""
    pass
```
````

### Complete Example

````markdown
**Code 3.1.1: validate_input**

```python
# Block 3.1.1
def validate_input(user_input):
    """Validate user input meets requirements.
    
    Args:
        user_input: The input string to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Block 3.1.1.1: Check input is not empty
    if not user_input:
        return False
    
    # Block 3.1.1.2: Check input length is within bounds
    return len(user_input) <= 100
```

**Test 3.1.2: Tests for validate_input with valid input**

```gherkin
Scenario: Valid input
  Given user input "hello"
  When validate_input is called
  Then it returns True
  
  # Tests: Basic validation with valid input
  # Validates: Function accepts valid strings
```

```python
# Test 3.1.2
def test_validate_input_with_valid_input():
    """Test validation succeeds with valid input."""
    assert validate_input("hello") is True
```

**Test 3.1.3: Tests for validate_input with empty input**

```gherkin
Scenario: Empty input
  Given user input ""
  When validate_input is called
  Then it returns False
  
  # Tests: Validation rejection of empty input
  # Validates: Function rejects empty strings
```

```python
# Test 3.1.3
def test_validate_input_with_empty_input():
    """Test validation fails with empty input."""
    assert validate_input("") is False
```

**Code 3.2.1: process_input**

```python
# Block 3.2.1
def process_input(user_input):
    """Process validated input."""
    return user_input.upper()
```
````

## Implementation Order Section

**For each implementation step, add "Implementation order" subsection:**

```markdown
**Implementation order:**

1. [First sub-step with clear description]
2. [Second sub-step]
3. [Continue numbering all sub-steps]
4. [Include verification steps]
```

**Purpose:** Show the logical sequence for implementing the step, making it easier to follow and verify each piece is complete.

## Key Principles

1. **One function per code block**: Each Code X.Y.Z block contains exactly one function definition
2. **Tests immediately follow**: All tests for a function appear immediately after the function, before the next function
3. **Gherkin + implementation pairs**: Each test has both Gherkin specification and Python implementation
4. **Sequential numbering**: Y increments for each new function/member within a step
5. **Z increments for tests**: Z increments for each test of the same function
6. **Descriptive block comments**: Every block comment explains what that code does

## Benefits of This Structure

- **Traceability**: Easy to see which tests prove which functions
- **Incremental validation**: Each function is tested before moving to the next
- **Clear organization**: Functions and their tests are kept together
- **Reviewability**: Reviewers can verify implementation and tests in one place
- **Documentation**: Gherkin scenarios serve as executable specifications
