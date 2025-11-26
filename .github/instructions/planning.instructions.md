---
applyTo: "features/**/*.md"
---

# Issue Planning and Changes Documentation

These instructions apply to issue planning documents and changelog documentation.

## Issue Planning Documents

When creating issue planning documents, follow the structure defined in the ISSUE-PLAN template (see `.github/instructions/templates/ISSUE-PLAN.md`).

**Required sections (in order):**
1. **Overview** - Problem statement, architectural decisions, end result
2. **Implementation Methodology** (optional) - If following a specific pattern
3. **Table of Contents** - Links to all sections
4. **Program Flow Analysis** (when applicable) - Comparison of old vs new program flow
5. **Implementation Steps** - Numbered, detailed steps with files, tests, code examples
6. **Further Considerations** - Questions, decisions, and rationale
7. **Success Criteria** - How to verify the implementation is complete
8. **CHANGES for vX.Y.Z Release** - See Changes Documentation below

**Key principles:**
- Be thorough and specific - include file paths, function names, exact specifications
- Break work into logical, sequential steps
- Include code examples for complex implementations
- Specify test requirements for each step
- Document architectural decisions and trade-offs
- Link back to table of contents from each section

**Reference the template at:** `.github/instructions/templates/ISSUE-PLAN.md`

### Program Flow Analysis Section

**When to include:** For issues that change how code flows through the system (refactorings, architectural changes, new execution paths).

**Position in document:** After Table of Contents, before Implementation Steps.

**Purpose:** Provide high-level understanding of what changes before diving into implementation details.

**Structure:**

1. **Section heading:** Use a descriptive title focused on the primary feature/behaviour being changed (not implementation-specific)
2. **Current Behaviour (Before Changes)** subsection with:
   - One paragraph summary explaining the current flow at a high level
   - Separate breakdowns for each usage scenario (if they differ) showing step-by-step flow
   - Result summary explaining the outcome
3. **New Behaviour (After Changes)** subsection with:
   - One subsection per behaviour mode/option
   - Each mode includes:
     - One paragraph summary explaining how this mode changes the flow
     - Separate breakdowns for each usage scenario (if they differ) showing complete step-by-step flow
     - Result summary explaining the outcome
4. **Key architectural changes** summary (bullet list of major implementation approach changes)

**Flow breakdown format:**

- Use numbered steps showing the complete call chain
- Include function names and module boundaries (e.g., "CLI → _parse_command_line()")
- Show data flowing through the system (e.g., "Receives tokenized params `[...]`")
- Indent sub-steps with bullet points to show nested calls
- Highlight decision points and branching logic
- Show where errors occur and how they propagate
- **Only include multiple usage scenarios if the flow differs between them** (e.g., CLI vs programmatic, synchronous vs asynchronous, different execution modes)

**Example structure:**

````markdown
## Feature Behaviour Flow

### Current Behaviour (Before Changes)

[One paragraph summary of current flow]

**Usage scenario 1 (e.g., CLI usage):**
1. **Entry point:** command example or function call
2. **Module → function()**: What happens
   - **function() → helper()**: Nested call
   - **Result**: What occurs
3. **Next step**: Continues...

**Usage scenario 2 (e.g., Programmatic usage):**
1. **Entry point:** Direct function call
2. **Result**: Outcome

**Result:** Summary of current behaviour limitations.

### New Behaviour (After Changes)

#### OPTION_A (description)

[One paragraph summary of how this option changes the flow]

**Usage scenario 1:**
[Complete flow with new functions/paths]

**Usage scenario 2:**
[Complete flow showing differences]

**Result:** Summary of this option's behaviour.

#### OPTION_B (description)

[One paragraph summary]

**Usage scenario 1:**
[Flow for this option]

**Usage scenario 2:**
[Flow for this option]

**Result:** Summary.

**Key architectural changes:**
- Change 1 description
- Change 2 description
- Change 3 description
````

**Complete example:**

````markdown
## Switch Param Grouped Behaviour Flow

This section illustrates how switch param conflict handling changes with the new `PARAM_SWITCH_CHANGE_BEHAVIOR` property.

### Current Behaviour (Before Changes)

In the current implementation, both CLI and programmatic usage follow identical paths through `set_param()`, which calls `_validate_xor_conflicts()` to detect conflicts. When a conflict is detected (a switch param in the same group is already set), `_validate_xor_conflicts()` raises a `ValueError` immediately, with no mechanism to configure alternative behaviour.

**CLI usage:**
1. **User runs:** `app --mode-read --mode-write`
2. **CLI → _parse_command_line()**: Receives tokenized params
3. **_parse_command_line()**: Loops through params
4. **_parse_command_line() → param.set_param('mode_read', True)**: Sets first param
   - **set_param() → _validate_xor_conflicts()**: Checks for conflicts
   - **set_param() → config**: Sets `mode_read=True`
5. **_parse_command_line() → param.set_param('mode_write', True)**: Attempts second param
   - **set_param() → _validate_xor_conflicts()**: Finds conflict
   - **_validate_xor_conflicts()**: Raises `ValueError`
   - **Error propagates**: set_param() → _parse_command_line() → CLI

**Programmatic usage:**
1. **Application → param.set_param('mode_read', True)**: Sets first param
2. **Application → param.set_param('mode_write', True)**: Attempts second param
   - **set_param() → _validate_xor_conflicts()**: Finds conflict
   - **Raises `ValueError`**

**Result:** Always raises error. No way to configure different behaviour.

### New Behaviour (After Changes)

With `PARAM_SWITCH_CHANGE_BEHAVIOR` property, three behaviour options are available:

#### SWITCH_REJECT (default - backward compatible)

With `SWITCH_REJECT` behaviour, the system maintains backward compatibility by raising errors on conflicts, but the implementation path changes. CLI parsing uses a new `param.set_values()` function that enables batch mode, which forces `SWITCH_REJECT` regardless of configuration. The conflict detection logic moves to the renamed `_handle_switch_group_behavior()`.

**CLI usage:**
1. **User runs:** `app --mode-read --mode-write`
2. **CLI → _parse_command_line()**: Receives tokenized params
3. **_parse_command_line() → param.set_values()**: Calls with parsed list
4. **param.set_values()**: Enables batch mode (`_set_batch_mode(True)`)
5. **param.set_values() → param.set_param('mode_read', True)**: Sets first param
6. **param.set_values() → param.set_param('mode_write', True)**: Attempts second param
   - **set_param() → _handle_switch_group_behavior()**: Checks for conflicts
   - **_handle_switch_group_behavior() → _get_switch_change_behavior()**: Returns `SWITCH_REJECT` (forced by batch mode)
   - **Raises `ValueError`**
7. **param.set_values()**: Disables batch mode in finally block

**Programmatic usage:**
1. **Application → param.set_param('mode_read', True)**: Sets first param
2. **Application → param.set_param('mode_write', True)**: Attempts second param
   - **set_param() → _handle_switch_group_behavior()**: Checks for conflicts
   - **_get_switch_change_behavior()**: Returns `SWITCH_REJECT` (from config)
   - **Raises `ValueError`**

**Result:** CLI forces SWITCH_REJECT via batch mode; programmatic uses configured behaviour (defaults to SWITCH_REJECT).

#### SWITCH_UNSET (new option)

With `SWITCH_UNSET` configured, programmatic usage exhibits automatic conflict resolution by calling `unset_param()` on conflicting switches. However, CLI usage ignores this configuration due to batch mode forcing `SWITCH_REJECT`.

**CLI usage:**
1. **User runs:** `app --mode-read --mode-write`
2. **[Same flow as SWITCH_REJECT - batch mode overrides to REJECT]**
3. **Result:** Error raised

**Programmatic usage:**
1. **Application → param.set_param('mode_read', True)**: Sets first param
2. **Application → param.set_param('mode_write', True)**: Sets second param
   - **set_param() → _handle_switch_group_behavior()**: Checks for conflicts
   - **_get_switch_change_behavior()**: Returns `SWITCH_UNSET` (batch mode disabled)
   - **_handle_switch_group_behavior()**: Calls `unset_param('mode_read')`
   - **set_param() → config**: Sets `mode_write=True`

**Result:** CLI raises error. Programmatic usage: `mode_read` removed, `mode_write` set to True.

**Key architectural changes:**

1. **CLI parser refactored**: `_parse_command_line()` calls new `param.set_values()` instead of looping
2. **Batch mode introduced**: `_batch_mode` flag forces `SWITCH_REJECT` during CLI parsing
3. **Behaviour abstraction**: `_get_switch_change_behavior()` respects config in programmatic usage but overrides when batch mode enabled
4. **Validation renamed**: `_validate_xor_conflicts()` → `_handle_switch_group_behavior()`
````

### Documentation Update Section

**When to include:** For all issues that add or change user-facing functionality.

**Position in document:** After all implementation steps, before "Further Considerations".

**Purpose:** Specify exactly what documentation files need updates and what content to add.

**Structure:**

1. **Main section heading:** Use "X. Update documentation" where X is the step number
2. **Brief intro paragraph:** Summarize what documentation updates are needed and version
3. **Horizontal rule:** `---` to separate intro from subsections
4. **Subsections (X.1, X.2, etc.):** One per documentation file to update
   - Use `####` heading level (e.g., `#### 6.1. Update parameters.md`)
   - **File:** field specifying the file path
   - Description of what to add/change
   - **Location:** (optional) where in the file to add content
   - **Content to add:** or **Updates required:** with full markdown content blocks
   - **Tests:** Concise format "Manual review to verify [aspect]"
5. **Back to top link** at end of main section

**Documentation subsection format:**

Each subsection should include:
- **File:** path to documentation file
- Description paragraph explaining the update
- **Location:** (optional) where to place new content
- **Content to add:** for single additions with full markdown wrapped in ````markdown syntax, or
- **Updates required:** for multiple specific changes (numbered list) with markdown snippets
- **Tests:** Manual review description

**Test format for documentation:**

Documentation tests use a concise, single-line format:
```markdown
**Tests:** Manual review to verify documentation clarity and accuracy
**Tests:** Manual review to verify documentation completeness and accuracy
**Tests:** Manual review to verify README clarity and consistency
```

Do NOT use Gherkin format for documentation tests. Documentation tests are manual reviews focused on quality aspects (clarity, accuracy, completeness, consistency).

**Example structure:**

````markdown
### 6. Update documentation

Update user-facing documentation to describe the new functionality. 
Add version notes to indicate this was added in v1.1.0.

---

#### 6.1. Update parameters.md

**File:** `doc/parameters.md`

Add new section "Feature Name" after "Related Section" section. 
This section documents the new functionality, provides code examples, 
and includes version note.

**Location:** After "Related Section" section

**Content to add:**

````markdown
## Feature Name

**Added in v1.1.0**

[Full markdown content here including examples, explanations, etc.]

### Example: Use Case Description

```python
spafw37.add_params([{
    PARAM_NAME: 'example',
    # ... configuration
}])
```

This example demonstrates [behavior description].

[Additional explanation paragraphs]

See complete example in [`examples/example_file.py`](../examples/example_file.py).
````

**Tests:** Manual review to verify documentation clarity and accuracy

---

#### 6.2. Update API reference

**File:** `doc/api-reference.md`

Add documentation for the new constants and properties.

**Updates required:**

1. **Properties table** - Add new row:
   ```markdown
   | `PROPERTY_NAME` | Description of property. Added in v1.1.0. |
   ```

2. **Constants section** - Add constant definitions:
   ```markdown
   ### Constant Group Name
   
   **Added in v1.1.0**
   
   - **`CONSTANT_NAME`** (`'value'`)
     - Description of what it does
     - When to use it
   ```

3. **Functions section** (if applicable) - Document new functions:
   ```markdown
   ### `function_name(param1, param2)`
   
   **Added in v1.1.0**
   
   [Function description]
   
   **Parameters:**
   - `param1` - Description
   - `param2` - Description
   
   **Returns:**
   - Description of return value
   ```

**Tests:** Manual review to verify documentation completeness and accuracy

---

#### 6.3. Update README.md

**File:** `README.md`

Add references to the new functionality in three locations.

**Updates required:**

1. **Features list** - Add bullet point:
   ```markdown
   - Feature description with technical specifics
   ```

2. **Examples list** - Add new example entry:
   ```markdown
   - **`example_file.py`** - Demonstrates feature usage
   ```

3. **"What's New in v1.1.0" section** - Add concise one-line bullet:
   ```markdown
   - Feature description with key constants/functions (`CONSTANT1`, `CONSTANT2`)
   ```

**Tests:** Manual review to verify README clarity and consistency

[↑ Back to top](#table-of-contents)
````

**Key formatting rules:**

1. **Full markdown content** - When showing complete documentation sections (like parameters.md examples), wrap in ````markdown and include ALL content
2. **Specifications** - When showing specific updates (like API reference table rows), use numbered lists with markdown snippets in ```markdown blocks
3. **Concise for README** - README "What's New" entries should be single-line bullets, not multi-paragraph explanations
4. **Version annotations** - Always include "**Added in vX.Y.Z**" notes in documentation content
5. **Example links** - Link to example files with relative paths: `[examples/file.py](../examples/file.py)`
6. **Horizontal rule** - Always include `---` separator after intro paragraph, before first subsection

## Hierarchical Numbering System for Plans

All code blocks, tests, and examples in planning documents must use a consistent hierarchical numbering system to enable precise referencing and discussion.

### Numbering Structure

**Code blocks use X.Y format:**
- **X** = Implementation step number (1, 2, 3, etc.)
- **Y** = Code block number within that step

**Pattern for implementations and tests:**
- **Code X.Y** (odd Y) = Implementation code (functions, constants, classes)
- **Test X.Y+1.Z** = Tests for Code X.Y (where Z is the test number: 1, 2, 3, etc.)
- **Code X.Y+2** (next odd Y) = Helper functions extracted from Code X.Y
- **Test X.Y+3.Z** = Tests for Code X.Y+2

**Example sequence:**
- Code 3.4.1 = `set_values()` main function
- Test 3.4.2.1-4 = Tests for `set_values()`
- Code 3.4.3 = `_process_param_values()` helper extracted from 3.4.1
- Test 3.4.4.1 = Tests for `_process_param_values()`
- Code 3.4.5 = `_process_single_param_entry()` helper extracted from 3.4.3
- Test 3.4.6.1-3 = Tests for `_process_single_param_entry()`
- Test 3.4.7.1 = Integration tests for the entire `set_values()` flow

### Numbering Within Code Blocks

**Use comment annotations to identify nested blocks:**

Each time code is nested or follows a nested section, it forms a new block. Label blocks with comments on the preceding line.

**Example 1: Simple function with try/finally**

````markdown
**Code 3.4.1: set_values function**

```python
# Block 3.4.1
def set_values(param_values):
    """Set multiple parameter values with batch mode enabled."""
    # Block 3.4.1.1
    _set_batch_mode(True)
    # Block 3.4.1.2: try/finally cleanup
    try:
        # Block 3.4.1.2.1
        _process_param_values(param_values)
    finally:
        # Block 3.4.1.2.2
        _set_batch_mode(False)
```
````

**Example 2: Function with loop**

````markdown
**Code 3.4.2: _process_param_values function**

```python
# Block 3.4.2
def _process_param_values(param_values):
    """Process each parameter value entry."""
    # Block 3.4.2.1: for loop iteration
    for param_entry in param_values:
        # Block 3.4.2.1.1
        _process_single_param_entry(param_entry)
```
````

**Example 3: Function with conditional branching**

````markdown
**Code 3.4.3: _process_single_param_entry function**

```python
# Block 3.4.3
def _process_single_param_entry(param_entry):
    """Process a single parameter entry."""
    # Block 3.4.3.1: variable extraction
    alias = param_entry.get("alias")
    value = param_entry.get("value")
    
    # Block 3.4.3.2: routing decision
    if is_list_param(alias=alias) or is_dict_param(alias=alias):
        # Block 3.4.3.2.1
        join_param(alias=alias, value=value)
    else:
        # Block 3.4.3.2.2
        set_param(alias=alias, value=value)
```
````

**Example 4: Function with multiple sequential sections**

````markdown
**Code 3.4.4: process_batch function**

```python
# Block 3.4.4
def process_batch(items):
    """Process a batch of items and report results."""
    # Block 3.4.4.1
    results = []
    
    # Block 3.4.4.2: Process each item
    for item in items:
        # Block 3.4.4.2.1
        processed = transform_item(item)
        # Block 3.4.4.2.2
        results.append(processed)
    
    # Block 3.4.4.3: After loop completes
    log_summary(len(results))
    # Block 3.4.4.4
    return results
```
````

**Block identification rule:** 
- Each nested statement gets its own hierarchical block number (e.g., Block 3.4.1.4.1 for code nested inside an if statement)
- Code that follows after a nested section completes gets the next sequential number at the parent level (e.g., Block 3.4.1.7 follows Block 3.4.1.6, even though 3.4.1.6 contained nested blocks 3.4.1.6.1 and 3.4.1.6.2)

**Omission notation for long blocks:**

When code blocks are lengthy, use `/* Lines X-Y omitted */` to indicate skipped content:

**Code 4.1: _parse_command_line function**

````markdown
```python
def _parse_command_line(tokens):
    """Parse command-line arguments and execute commands."""
    /* Lines 4.1.1-4.1.15 omitted */
    _queue_commands(tokens["commands"])
    _parse_file_references_in_params(tokens["params"])
    param.set_values(tokens["params"])
```
````

### Code Organization in Plans

**Follow the code structure rules defined in `python.instructions.md`:**
- Maximum nesting depth: 2 levels below function declaration
- Maximum nested block size: 2 lines
- Extract violations to helper methods
- All helpers must have dedicated unit tests

See `python.instructions.md` "Nested-Structure and Single-Responsibility Rules" section for complete details and examples.

**Each implementation function must be followed by its tests:**
- Main function code block (Code X.Y)
- Unit tests for main function (Test X.Y+1.1, X.Y+1.2, etc.)
- First helper function (Code X.Y+2)
- Unit tests for first helper (Test X.Y+3.1, X.Y+3.2, etc.)
- Second helper function (Code X.Y+4)
- Unit tests for second helper (Test X.Y+5.1, X.Y+5.2, etc.)
- Integration tests if needed (Test X.Y+N.1, X.Y+N.2, etc.)

**Do NOT combine multiple functions in a single code block** - extract helpers into separate numbered code blocks with their own tests.

### Test Documentation Format

**Use Gherkin-style scenarios for all tests:**

````markdown
**Test 3.4.2.1: Enables batch mode at start**

```gherkin
Scenario: set_values enables batch mode at start
  Given I have mocked _set_batch_mode
  When I call set_values() with a list of params
  Then _set_batch_mode should be called with True
  
  # Validates: set_values() activates batch mode at start of processing
```
````

**Gherkin test structure:**
- **Scenario:** Brief description matching the test caption
- **Given:** Preconditions and setup
- **When:** Action being tested
- **Then:** Expected outcomes and assertions
- **And:** Additional conditions or assertions (if needed)
- **# Validates:** Comment explaining what behaviour is being verified

**Test types to include:**
- **Unit tests:** Test each function in isolation (mock dependencies)
- **Integration tests:** Test complete workflows end-to-end
- **Edge cases:** Test boundary conditions, error cases, empty inputs
- **Backward compatibility:** Verify default behaviours match existing functionality

### Examples Must Follow Plan Numbering

**Example code blocks use the same numbering system:**

**When creating example files with multiple functions:**

1. **Code X.1** - Module docstring and imports (file header, appears once at top)
2. **Code X.2** - First function definition
3. **Code X.3** - Second function definition
4. **Code X.4** - Third function definition (may include `if __name__ == '__main__':` block)

**Example structure for multi-function demonstration:**

````markdown
**Code 5.1: Module docstring and imports**

```python
"""Module demonstrating feature usage.

This example demonstrates:
- Mode A: Description
- Mode B: Description
- Mode C: Description
"""

from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    /* Lines omitted */
)
```

**Code 5.2: demo_mode_a function**

```python
def demo_mode_a():
    """Demonstrate Mode A behaviour."""
    spafw37.add_param({
        PARAM_NAME: 'example',
        /* Lines omitted */
    })
```

**Code 5.3: demo_mode_b function**

```python
def demo_mode_b():
    """Demonstrate Mode B behaviour."""
    # Implementation
```

**Code 5.4: demo_mode_c function**

```python
def demo_mode_c():
    """Demonstrate Mode C behaviour."""
    # Implementation


if __name__ == '__main__':
    demo_mode_a()
    demo_mode_b()
    demo_mode_c()
```
````

**Examples should demonstrate:**
- Complete, runnable code
- Real-world use cases
- Clear separation between module header and individual functions
- Expected output showing results

### Important: Numbers Are Plan-Only

**The hierarchical numbers are for PLANNING ONLY:**
- ✅ Use numbers in plan documents to reference specific code locations
- ✅ Use numbers in PR reviews to identify specific blocks
- ✅ Use omission notation (`/* Lines X-Y omitted */`) for long blocks
- ❌ DO NOT write numbers into actual source code files
- ❌ DO NOT include line number comments in implementation

**Rationale:** Source code changes constantly. Line numbers in production code become outdated immediately and create maintenance burden. The numbering system exists solely to facilitate detailed planning and review discussions.

## Changes Documentation (CHANGES)

When documenting changes for release, follow the structure defined in the CHANGES template (see `.github/instructions/templates/CHANGES.md`).

**Mandatory sections (in order):**
1. **Issues Closed** - List of issue numbers and titles
2. **Additions** - New functions, constants, features
3. **Removals** - Deprecated or removed functionality
4. **Changes** - Behavioural changes to existing functionality
5. **Migration** - How to update code for breaking changes
6. **Documentation** - Documentation files added or changed
7. **Testing** - Test counts, coverage, new test files
8. **Footer** - Changelog link and issue/PR links

**Critical writing style rules:**

**Use dispassionate, matter-of-fact tone:**
- ✅ `unset_param()` removes parameter value completely from configuration.
- ❌ `unset_param()` provides a flexible way to remove parameter values.
- ✅ `PARAM_IMMUTABLE` constant marks parameter as write-once.
- ❌ `PARAM_IMMUTABLE` is an exciting new constant that gives you powerful protection.

**No marketing language:**
- Avoid: "exciting", "powerful", "elegant", "clever", "beautiful"
- Avoid: "enhanced", "improved", "revolutionary", "innovative"
- Use: factual descriptions of what the code does

**No internal jargon:**
- Avoid: "flexible resolution", "semantic richness", "orthogonal concerns"
- Use: clear, specific technical descriptions users can understand

**Function descriptions format:**
```
function_name() does X. Raises error if Y.
```

**Tense usage:**
- Present tense for what exists: "function returns value"
- Past tense for what was done: "added support for", "fixed issue where"

**Consolidation when merging multiple issues:**
- Consolidate all bullets across issues in each section
- Do not break down per-issue within sections
- Ensure consistent style across all items

**Empty sections:**
- Include section heading
- Write "None." if nothing to report in that section

**Reference the template at:** `.github/instructions/templates/CHANGES.md`

## Documentation Update Requirements

When adding new features, always update:
- `README.md` - Reflect new functionality in features list, code examples, examples list
- Add "What's New in vX.Y.Z" section
- Add "**Added in vX.Y.Z**" notes at the start of new documentation sections
- This helps users discover new features and understand when they were introduced

## Best Practices

**Be specific and factual:**
- State exactly what was added, changed, or removed
- Include function names, file paths, and technical details
- Avoid vague descriptions like "improved performance" without metrics

**Think about the user:**
- What do they need to know to use this feature?
- What will break if they upgrade?
- What do they need to change in their code?

**Maintain consistency:**
- Use the same format for similar items
- Follow the established templates exactly
- Keep tone and style consistent throughout
