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

## Algorithm

if there is not an Algorithm section here, add one. If there is, do not remove it. This contains developer details for maintenance.

## Implementation Order Section

**For each implementation step, add "Implementation order" subsection** as defined in `.github/instructions/plan-structure.instructions.md`. This shows the logical sequence for implementing the step.

## Code Block Organization

For each implementation step:

#### 1. Constants and Module-Level Setup

```markdown
**Code X.1: Module-level constants**

```python
# Block X.1.1: Module-level constant for feature
CONSTANT_NAME = 'value'  # Description of purpose
```

#### 2. Main Implementation Functions

```markdown
**Code X.2: main_function_name**

```python
# Block X.2
def main_function_name(parameters):
    """Comprehensive docstring following standards."""
    # Block X.2.1: First logical section
    setup_code()
    
    # Block X.2.2: Main logic
    process_data()
    
    # Block X.2.3: Return or final actions
    return result
```

#### 3. Helper Functions

```markdown
**Code X.3: helper_function_name**

```python
# Block X.3
def _helper_function(parameters):
    """Brief docstring for internal helper."""
    # Implementation with block numbering
```

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
2. **Add numbered code blocks** with:
   - Proper hierarchical numbering (X.Y, X.Y.1, X.Y.2, etc.)
   - Complete, working code (not pseudocode)
   - Comprehensive docstrings for public functions
   - Minimum one-line docstrings for private functions
   - Descriptive block comments
   - Proper Python 3.7 compatibility
   - UK English in comments and docstrings
3. **Follow naming standards** - no lazy placeholder names
4. **Include helper functions** if needed (separate code blocks)
5. **Add regression tests** if modifying existing functions (verify unchanged behaviour)

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
7. ✅ **Regression tests included** if modifying existing functions

**If any violations found, fix them before submitting your response.**

Ask user to review implementation code before proceeding to Step 5 (documentation).
