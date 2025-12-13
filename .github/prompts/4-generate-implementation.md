# Prompt: Generate Implementation Code Blocks for Plan Document

# ⚠️ WARNING: YOU ARE EDITING A PLAN DOCUMENT, NOT SOURCE CODE FILES ⚠️

**DO NOT modify files in `src/`, `tests/`, or any Python source files.**
**YOU ARE ONLY EDITING: `features/{FEATURE_NAME}.md`**

**IMPORTANT:** Do NOT commit or push changes without explicit user permission.

## Your Task

**CRITICAL: You are ONLY editing the plan document.**

- **File to edit:** `features/{FEATURE_NAME}.md`
- **Files NOT to edit:** Any files in `src/`, `tests/`, or other directories
- **Your job:** Add detailed code specifications to the plan document
- **You are NOT implementing the feature** - you are documenting HOW to implement it

You are working on issue #{ISSUE_NUMBER} plan document at `features/{FEATURE_NAME}.md`. This is step 4 of 6: generating detailed implementation code with proper block numbering.

## Before You Start - Verify Understanding

Before making any changes, confirm:
- [ ] I am editing ONLY the plan document at `features/{FEATURE_NAME}.md`
- [ ] I am NOT touching any files in `src/` or `tests/`
- [ ] I am adding code block specifications to the plan
- [ ] The code I write goes IN THE MARKDOWN, not in separate Python files

## CRITICAL: NO GUESSING POLICY

**See `.github/instructions/accuracy.instructions.md` for the complete NO GUESSING POLICY.**

Key points for implementation:
- NEVER guess how external libraries or APIs work
- Retrieve and cite official documentation before implementing
- Base all code on verified patterns from the codebase or official sources
- If uncertain, read existing code or ask for clarification
- Do NOT fabricate function signatures or assume behaviour

## Python Coding Standards

**See `.github/instructions/python.instructions.md` for complete Python coding standards**, including:
- Nested-Structure and Single-Responsibility Rules (max 2-level nesting, 2-line nested blocks)
- Naming Requirements (no lazy naming like `data`, `result`, `tmp`)
- Documentation Requirements (comprehensive docstrings for public functions, minimum one-line for helpers)
- Import Rules (absolute imports, module-level access for functions)
- Architecture and Composition patterns

**See `.github/instructions/python37.instructions.md` for Python 3.7.0 compatibility requirements**, including:
- Forbidden Python 3.8+ features (walrus operator, positional-only params, f-string = specifier)
- Type hints policy (DO NOT USE for this project)
- Standard library differences

**See `.github/instructions/python-tests.instructions.md` for test standards** (applies when generating test code), including:
- Test structure (module-level functions, NOT classes)
- Test documentation (minimum 3-sentence docstrings: What, Outcome, Why)
- Test granularity (one outcome per test function)
- Test naming conventions

### Key Reminders for Implementation

**Critical rules to remember:**
- Maximum 2-level nesting depth
- Maximum 2-line nested block size
- Extract helpers with descriptive names
- ALL helpers must have dedicated unit tests
- No lazy placeholder names (`data`, `result`, `tmp`, `i`, `j`, etc.)
- Python 3.7.0 compatible only (no walrus operator, no positional-only params)
- Use UK English spelling (initialise, synchronise, behaviour, colour)

## CRITICAL: Plan File Implementation Code Structure

**All plan documents in `features/` directory must follow the structure rules defined in:**
**`.github/instructions/plan-structure.instructions.md`**

Key requirements:
- Hierarchical block numbering (X.Y.Z)
- Implementation + tests interweaved (each function immediately followed by its tests)
- Gherkin + Python pairs (each test has both specification and implementation)
- Test headings describe what's being tested (not "Gherkin for...")

**See the instruction file for complete details, examples, and rationale.**

## CRITICAL: Module-Level Imports in Plan Documents

**ALL imports MUST be shown at module level, NOT inside test functions.**

**See `.github/instructions/plan-structure.instructions.md` § CRITICAL: Module-Level Imports in Plan Documents for complete details.**

Key requirements:
- Show a "Module-level imports" section at the start of each test file
- List ALL imports that the test file will need
- Test functions reference already-imported modules, NOT import them again
- **Inline imports inside test functions are PROHIBITED** (see `python.instructions.md` § ANTI-PATTERN: Inline Imports)

**Example - WRONG way (inline imports in tests):**
```python
def test_something():
    """Test something."""
    from spafw37 import param  # ❌ WRONG
    param.add_param({})
```

**Example - CORRECT way (module-level imports):**
```markdown
**File:** `tests/test_param.py`

Module-level imports:
```python
# Module-level imports for tests/test_param.py
from spafw37 import param
from spafw37.constants.param import PARAM_NAME
import pytest
```

**Test 3.1.2:**

```python
def test_something():
    """Test something."""
    param.add_param({PARAM_NAME: 'test'})  # ✅ Correct - uses already-imported module
```
```

## Algorithm

if there is not an Algorithm section here, add one. If there is, do not remove it. This contains developer details for maintenance.

## Implementation Order Section

**For each implementation step, add "Implementation order" subsection** as defined in `.github/instructions/plan-structure.instructions.md`. This shows the logical sequence for implementing the step.

## Code Block Organization

**CRITICAL RULE: Each function (main or helper) MUST be in its own separate fenced code block, immediately followed by its own test blocks, before the next function appears.**

This applies to:
- Main implementation functions
- All helper functions (no matter how small)
- Private functions (prefixed with `_`)

**See `.github/instructions/plan-structure.instructions.md` § "One function per code block" for complete details.**

### Structure Pattern: Main Function → Tests → Helpers → Tests

For each implementation step, follow this pattern:

1. **Algorithm section** (if not already present)
2. **Implementation order section** 
3. **Main function** in separate code block
4. **Tests for main function** (one or more test blocks)
5. **First helper function** in separate code block
6. **Tests for first helper** (one or more test blocks)
7. **Second helper function** in separate code block
8. **Tests for second helper** (one or more test blocks)
9. Continue pattern for remaining helpers

**Each function gets:**
- Its own `**Code X.Y.Z: function_name**` heading
- Its own fenced Python code block
- Immediately following test blocks before next function

### Module-Level Setup (Exception to Pattern)

Constants and module-level variables are shown first:

```markdown
**Code X.1: Module-level constants**

```python
# Block X.1.1: Module-level constant for feature
CONSTANT_NAME = 'value'  # Description of purpose
```
```

### Anti-Pattern Example: WRONG vs RIGHT

#### ❌ WRONG: Bundled helpers without individual tests

```markdown
**Code 3.2: Helper functions**

```python
# Block 3.2.1
def _validate_input(value):
    """Validate input."""
    return value is not None

# Block 3.2.2  
def _process_input(value):
    """Process input."""
    return value.upper()

# Block 3.2.3
def _store_result(value):
    """Store result."""
    _results.append(value)
```

**Test 3.3: Test helper functions**
(Tests for all helpers grouped together)
```

**Problems with this approach:**
- Multiple functions in one code block violates "one function per block" rule
- Tests are not immediately after each function
- Cannot trace which test validates which helper
- Violates plan structure rules

#### ✅ CORRECT: Each helper in separate block with immediate tests

```markdown
**Code 3.2.1: _validate_input**

```python
# Block 3.2.1
def _validate_input(value):
    """Validate input returns True if value is not None."""
    return value is not None
```

**Test 3.2.2: Tests for _validate_input with valid value**

```gherkin
Scenario: Valid value returns True
  Given value is not None
  When _validate_input is called
  Then it returns True
```

```python
# Test 3.2.2
def test_validate_input_with_valid_value():
    """Test validation succeeds with valid value."""
    assert _validate_input("test") is True
```

**Test 3.2.3: Tests for _validate_input with None**

```gherkin
Scenario: None value returns False
  Given value is None
  When _validate_input is called
  Then it returns False
```

```python
# Test 3.2.3
def test_validate_input_with_none():
    """Test validation fails with None."""
    assert _validate_input(None) is False
```

**Code 3.3.1: _process_input**

```python
# Block 3.3.1
def _process_input(value):
    """Process input by converting to uppercase."""
    return value.upper()
```

**Test 3.3.2: Tests for _process_input**

```gherkin
Scenario: Input is converted to uppercase
  Given value is "hello"
  When _process_input is called
  Then it returns "HELLO"
```

```python
# Test 3.3.2
def test_process_input_converts_to_uppercase():
    """Test input is converted to uppercase."""
    assert _process_input("hello") == "HELLO"
```

**Code 3.4.1: _store_result**

```python
# Block 3.4.1
def _store_result(value):
    """Store result in module-level results list."""
    _results.append(value)
```

**Test 3.4.2: Tests for _store_result**

```gherkin
Scenario: Result is appended to list
  Given _results is empty
  When _store_result is called with "test"
  Then _results should contain "test"
```

```python
# Test 3.4.2
def test_store_result_appends_to_list():
    """Test result is appended to results list."""
    _results.clear()
    _store_result("test")
    assert "test" in _results
```
```

**Why this is correct:**
- Each function in its own code block
- Tests immediately follow each function
- Clear traceability: Test X.Y.Z tests Code X.Y.(Z-1)
- Follows plan structure rules exactly

## Table of Contents

Always update the Table of Contents at the end of any changes to the plan document to ensure it accurately reflects the current structure and status of all sections. The ToC should include three levels of depth:
- Level 1: Major sections (##)
- Level 2: Subsections (###)
- Level 3: Individual questions (e.g., Q1, Q2) and sub-items (####)

## UK English Requirements

Use UK spelling: initialise, synchronise, optimise, behaviour, colour

## CRITICAL: Regression Tests for Modified Functions

**When any step modifies an existing function:**
- Add regression tests immediately after the modification
- Regression tests verify that existing behaviour is unchanged for code paths not related to the new feature
- Test that parameters/inputs without new properties work identically to before
- Test that return values and side effects remain unchanged for existing use cases

**Example:** If modifying `add_param()` to handle new `PARAM_PROMPT` properties:
- Add regression test verifying params **without** `PARAM_PROMPT` register identically to before
- Add regression test verifying all existing param properties still work unchanged
- Add regression test verifying existing validation behaviour is preserved

**Rationale:** Modifications to existing functions risk breaking current functionality. Regression tests prove existing behaviour is preserved whilst new behaviour is added.

## Your Task for Each Implementation Step

For EACH step in the plan:

1. **Add "Implementation order" subsection** after the step description
2. **Add main function code block** with proper numbering
3. **Add tests for main function** (one or more test blocks)
4. **CRITICAL: For each helper function:**
   - Add separate code block with heading `**Code X.Y.Z: helper_name**`
   - Add fenced Python code block with the helper implementation
   - Immediately add test blocks for that helper (Gherkin + Python)
   - **BEFORE** moving to next helper or next step
5. **Verify structure:** Each function appears in this order:
   - Code block for function
   - Test block(s) for that function
   - Code block for next function
   - Test block(s) for next function
   - (repeat)

**Each code block must contain:**
- Proper hierarchical numbering (X.Y, X.Y.1, X.Y.2, etc.)
- Complete, working code (not pseudocode)
- Comprehensive docstrings for public functions
- Minimum one-line docstrings for private functions
- Descriptive block comments
- Proper Python 3.7 compatibility
- UK English in comments and docstrings

**Follow naming standards** - no lazy placeholder names
**Add regression tests** if modifying existing functions (verify unchanged behaviour)

## Output Requirements

For EACH implementation step:
1. ✅ Complete "Implementation order" subsection
2. ✅ All code blocks with proper numbering
3. ✅ Full implementations (not pseudocode)
4. ✅ Proper docstrings and comments
5. ✅ Python 3.7 compatible code
6. ✅ UK English spelling
7. ✅ No lazy naming
8. ✅ Regression tests if modifying existing functions

After completing all steps, confirm:
- Total number of code blocks added
- Total lines of implementation code
- Any concerns about complexity or implementation details

## CRITICAL: Pre-Submission Verification

**Before completing your response, verify ALL code against the mandatory checklist:**

**See `.github/instructions/code-review-checklist.instructions.md` for the complete checklist.**

Specifically verify:
1. ✅ **NO inline imports** - all imports at module/file level
2. ✅ **NO nesting beyond 2 levels** below function declaration
3. ✅ **NO nested blocks exceeding 2 lines**
4. ✅ **NO lazy naming** (`tmp`, `data`, `result`, `i`, `j`)
5. ✅ **NO Step Xa/Xb structure** in plan documents
6. ✅ **Each function immediately followed by its tests**
7. ✅ **Each helper in separate code block** (not bundled with other helpers)
8. ✅ **Each helper has its own test blocks** immediately following it
9. ✅ **Regression tests included** if modifying existing functions

**If any violations found, fix them before submitting your response.**

Ask user to review implementation code before proceeding to Step 5 (documentation).
