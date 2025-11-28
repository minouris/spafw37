# Prompt: Generate Implementation

**IMPORTANT:** Do NOT commit or push changes without explicit user permission.

**CRITICAL: NO GUESSING POLICY**

NEVER guess or make assumptions. If you are not certain about something, explicitly state that you don't know rather than guessing. This policy takes absolute precedence.

**If you don't know something:**
1. **Explicitly state that you don't know**
2. **Explain what you would need to know to proceed**
3. **Suggest where the user can find the information**
4. **Ask the user to verify or provide the correct information**

**Never override or second-guess user decisions.** Use exact values, names, and specifications provided by the user without modification.

## Your Task

You are working on issue #{ISSUE_NUMBER} plan document at `features/{FEATURE_NAME}.md`. This is step 4 of 6: generating detailed implementation code with proper block numbering.

## Critical Rules - NO GUESSING POLICY

**NEVER guess or make assumptions about:**
- How external libraries work
- API specifications you haven't verified
- Implementation details not in the codebase
- Function signatures or behaviour you haven't confirmed

**You are not helping by pretending to have information you don't have.**

**If uncertain, explicitly state what you need to verify.**

### Mandatory Source Citation for External Knowledge

When implementing code that uses external libraries or Python standard library:

1. **Check if you have webpage fetching capability** - If you don't have `fetch_webpage`, `curl`, or similar tools, state this immediately
2. **If you can fetch: Retrieve official documentation BEFORE implementing**
3. **Cite the specific URL** you fetched or checked
4. **Quote the relevant section** from the documentation
5. **If you cannot find or access documentation**, state: "I cannot find documentation to verify this" instead of guessing

**Examples requiring documentation fetch:**
- Python standard library module APIs (argparse, logging, etc.)
- External library usage patterns
- File format specifications
- Protocol implementations

All implementation must be based on:
- Actual codebase patterns verified by reading source files
- Explicit test specifications from Step 3
- Implementation plans from Step 2
- Official documentation for libraries/APIs used

If implementation approach is unclear:
1. Read similar existing code
2. Check how related functionality is implemented
3. Verify patterns used elsewhere in the codebase
4. For library/API usage: Fetch official documentation
5. Ask the user for guidance

Do NOT:
- Make up function signatures
- Assume internal implementation details
- Fabricate patterns not used in the codebase
- Pretend to know library APIs without checking documentation
- Assume standard library behaviour without verification

## Python Coding Standards

**From python.instructions.md - ALL code MUST follow these rules:**

### Naming Conventions

1. **Functions and methods:** `lowercase_with_underscores()`
2. **Variables:** `lowercase_with_underscores`
3. **Constants:** `UPPER_CASE_WITH_UNDERSCORES`
4. **Classes:** `CapitalizedWords` (PascalCase)
5. **Private/internal:** Prefix with single underscore `_function_name()`

### No Lazy Naming

**NEVER use these placeholder names:**
- `data`, `result`, `value`, `item`, `element`, `obj`, `tmp`, `temp`
- `foo`, `bar`, `baz`, `thing`, `stuff`
- `x`, `y`, `z` (except in mathematical contexts)
- `i`, `j`, `k` (except as loop counters in simple iterations)

**Use descriptive names:**
- `parsed_config` not `data`
- `validation_result` not `result`
- `user_input` not `value`
- `command_entry` not `item`

### Documentation Requirements

1. **All public functions require comprehensive docstrings:**
   ```python
   def public_function(param1, param2):
       """Brief description of what function does.
       
       More detailed explanation if needed. Describe the purpose,
       inputs, outputs, and any side-effects.
       
       Args:
           param1: Description of first parameter.
           param2: Description of second parameter.
           
       Returns:
           Description of return value.
           
       Raises:
           ValueError: When and why this is raised.
       """
   ```

2. **Private/internal functions require at minimum one-line docstring:**
   ```python
   def _internal_helper(param):
       """Brief description of what this helper does."""
   ```

## Python 3.7.0 Compatibility

**From python37.instructions.md - This project requires Python 3.7.0+:**

### FORBIDDEN Features (Python 3.8+)

❌ **Assignment expressions (walrus operator):**
```python
# WRONG (Python 3.8+)
if (match := pattern.search(text)):
    pass

# CORRECT (Python 3.7)
match = pattern.search(text)
if match:
    pass
```

❌ **Positional-only parameters:**
```python
# WRONG (Python 3.8+)
def func(a, b, /, c):
    pass

# CORRECT (Python 3.7)
def func(a, b, c):
    pass
```

❌ **f-string = specifier:**
```python
# WRONG (Python 3.8+)
print(f"{value=}")

# CORRECT (Python 3.7)
print(f"value={value}")
```

### ALLOWED Features (Python 3.7+)

✅ Type hints, dataclasses, async/await, f-strings, dict ordering

## Hierarchical Block Numbering System

**From planning.instructions.md:**

### Code Block Format

```markdown
**Code X.Y: function_name or description**

```python
# Block X.Y
def function_name(parameters):
    """Docstring here."""
    # Block X.Y.1: Description of this section
    first_statement()
    
    # Block X.Y.2: Description of next section
    if condition:
        # Block X.Y.2.1: Inside if block
        nested_statement()
    else:
        # Block X.Y.2.2: Inside else block
        other_statement()
    
    # Block X.Y.3: Final section
    return result
```
```

### Numbering Rules

- **X** = Implementation step number (1, 2, 3...)
- **Y** = Code block number within step (1, 2, 3...)
- **Odd Y numbers** = Implementation code (functions, classes)
- **Even Y numbers** = Reserved for tests (handled in Step 3)

### Block Hierarchy

- Top-level: `# Block X.Y`
- First nesting: `# Block X.Y.1`, `# Block X.Y.2`
- Second nesting: `# Block X.Y.1.1`, `# Block X.Y.1.2`
- Continue as needed for deeper nesting

### Block Comment Style

**Always include descriptive text:**
```python
# Block 3.4.1: Extract parameter name from definition
param_name = _param.get(PARAM_NAME)

# Block 3.4.2: Determine default value based on param type
if _is_toggle_param(_param):
    # Block 3.4.2.1
    default_value = _get_param_default(_param, False)
```

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

## Code Block Organization

For each implementation step:

### 1. Constants and Module-Level Setup

```markdown
**Code X.1: Module-level constants**

```python
# Block X.1.1: Module-level constant for feature
CONSTANT_NAME = 'value'  # Description of purpose
```
```

### 2. Main Implementation Functions

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
```

### 3. Helper Functions

```markdown
**Code X.3: helper_function_name**

```python
# Block X.3
def _helper_function(parameters):
    """Brief docstring for internal helper."""
    # Implementation with block numbering
```
```

## Table of Contents

Always update the Table of Contents at the end of any changes to the plan document to ensure it accurately reflects the current structure and status of all sections. The ToC should include three levels of depth:
- Level 1: Major sections (##)
- Level 2: Subsections (###)
- Level 3: Individual questions (e.g., Q1, Q2) and sub-items (####)

## UK English Requirements

Use UK spelling: initialise, synchronise, optimise, behaviour, colour

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

## Output Requirements

For EACH implementation step:
1. ✅ Complete "Implementation order" subsection
2. ✅ All code blocks with proper numbering
3. ✅ Full implementations (not pseudocode)
4. ✅ Proper docstrings and comments
5. ✅ Python 3.7 compatible code
6. ✅ UK English spelling
7. ✅ No lazy naming

After completing all steps, confirm:
- Total number of code blocks added
- Total lines of implementation code
- Any concerns about complexity or implementation details

Ask user to review implementation code before proceeding to Step 5 (documentation).
