# Issue #[NUMBER]: [Title]

## Overview

[Provide a clear, concise description of the issue and what it aims to accomplish. Include 2-4 paragraphs covering:]

- [What problem this issue solves or what functionality it adds]
- [How it fits into the existing architecture]
- [What the end result will be for users]

**Key architectural decisions:**

- **[Decision category]:** [Brief explanation of architectural choice]
- **[Decision category]:** [Brief explanation of architectural choice]
- **[Decision category]:** [Brief explanation of architectural choice]
- **[Decision category]:** [Brief explanation of architectural choice]

## Implementation Methodology

[Optional section - include if the implementation follows a specific pattern]

**[Methodology name] approach:**

[Describe the implementation pattern, for example:]

Each implementation step follows this pattern:

1. **[Phase 1]** - [Description]
2. **[Phase 2]** - [Description]
3. **[Phase 3]** - [Description]
4. **[Phase 4]** - [Description]
5. **[Phase 5]** - [Description]

This ensures:

- [Benefit 1]
- [Benefit 2]
- [Benefit 3]
- [Benefit 4]

## Table of Contents

- [Overview](#overview)
- [Implementation Methodology](#implementation-methodology)
- [Implementation Steps](#implementation-steps)
  - [1. [Step name]](#1-step-name)
  - [2. [Step name]](#2-step-name)
  - [3. [Step name]](#3-step-name)
  - [Continue numbering...](#continue-numbering)
- [Further Considerations](#further-considerations)
  - [1. [Consideration name]](#1-consideration-name)
  - [2. [Consideration name]](#2-consideration-name)
  - [Continue numbering...](#continue-numbering)
- [Fixing Regressions](#fixing-regressions) (if applicable)
  - [[Step number]. [Regression fix name]](#step-number-regression-fix-name)
- [Success Criteria](#success-criteria)
- [Implementation Plan Changes](#implementation-plan-changes) (if applicable)
- [CHANGES for vX.X.X Release](#changes-for-vxxx-release)

## Implementation Steps

### 1. [Step name]

**File:** `path/to/file.py`

[Provide detailed description of what this step accomplishes]

**Implementation order:**

1. [Sub-step 1]
2. [Sub-step 2]
3. [Sub-step 3]
4. [Continue as needed]

[Include detailed specifications, code examples, or bullet points describing the work:]

- **[Component name]:**
  - [Detail about component]
  - [Additional detail]
  
- **[Another component]:**
  - [Detail about component]
  - [Additional detail]

**Code example (if applicable):**

```python
# Example implementation
def example_function():
    """
    [Docstring explaining the function]
    """
    # Implementation details
    pass
```

**Helper functions to create (if applicable):**

- `function_name(params)`:
  - [Description of what function does]
  - [Behavior details]
  - [Return value]

**Functions to modify (if applicable):**

- `existing_function()`:
  - [What changes need to be made]
  - [Why the changes are needed]
  - [Impact on existing behavior]

**Tests:** [Describe test requirements]
- `test_function_name()` - [What this test validates]
- `test_edge_case()` - [What edge case this covers]
- `test_error_condition()` - [What error handling this tests]

[↑ Back to top](#table-of-contents)

### 2. [Step name]

**Files:** `path/to/file1.py`, `path/to/file2.py`, `path/to/file3.py` (new)

[Repeat the same structure as step 1 for each implementation step]

- [Detail 1]
- [Detail 2]
- [Detail 3]

**Tests:** [Describe test requirements]

[↑ Back to top](#table-of-contents)

### [Continue numbering steps...]

[Add as many steps as needed to complete the implementation]

**Note:** When adding new features:
- Update main `README.md` to reflect new functionality in relevant sections (features list, code examples, examples list, "What's New in vX.X.X")
- Add version notes ("**Added in vX.X.X**") at the start of new documentation sections
- This helps users discover new features and understand when they were introduced

[↑ Back to top](#table-of-contents)

## Further Considerations

### 1. [Consideration name] - [STATUS]

**Question:** [Pose the question or concern]

**Answer:** [Provide the decision or resolution]

**Rationale:**
- [Reason 1]
- [Reason 2]
- [Reason 3]

**Implementation:**
- [Implementation detail 1]
- [Implementation detail 2]
- [Implementation detail 3]

**Alternative considered:** [Describe alternative approach if applicable]
- Pro: [Advantage of alternative]
- Con: [Disadvantage of alternative]

**Rejected because:** [Explain why alternative was not chosen]

[↑ Back to top](#table-of-contents)

### 2. [Consideration name] - [STATUS]

[Repeat the same structure as consideration 1 for each consideration]

**Question:** [Question]

**Answer:** [Answer]

**Rationale:**
- [Reason 1]
- [Reason 2]

**Implementation:**
- [Detail 1]
- [Detail 2]

[↑ Back to top](#table-of-contents)

### [Continue numbering considerations...]

[Add as many considerations as needed]

[↑ Back to top](#table-of-contents)

## Fixing Regressions

**Note:** This section is added post-implementation when testing reveals issues requiring fixes. If core implementation (Steps 1-N) passes all tests, this section may be omitted.

### [N+1]. [Regression fix name] ✅ COMPLETE

**Depends on:** Core implementation (steps 1-N) complete, Consideration #X documented

**Status:** COMPLETE - [Brief status description]

**File:** `path/to/file.py`

[Provide detailed description of the regression and fix]

**Current buggy behavior:**

[Explain the bug or incorrect behavior]

**Correct behavior:**

[Explain what should happen instead]

**Implementation:**

[Detailed fix instructions]

**Code [N+1].1: Current buggy implementation**

```python
def buggy_function():
    """Docstring."""
    # Block [N+1].1.1: Description
    buggy_code_here()
    
    # Block [N+1].1.2: Problem explanation
    incorrect_logic()
```

**Code [N+1].2: Fixed implementation**

```python
def fixed_function():
    """Docstring."""
    # Block [N+1].2.1: Description
    fixed_code_here()
    
    # Block [N+1].2.2: Correct logic
    correct_logic()
```

**Verification:**

After fix, run:
```bash
pytest tests/test_file.py -v
```

[List specific tests that should now pass]

[↑ Back to top](#table-of-contents)

### [N+2]. [Test expectation updates] ✅ COMPLETE

**Depends on:** Core implementation (steps 1-N) complete, Step [N+1] complete, Consideration #X resolved

**Status:** COMPLETE - [Brief status description]

**File:** `tests/test_file.py`

[Provide description explaining why test expectations need updating]

**Tests to update ([X] tests):**

**Test [N+2].1: test_function_name (Line ~XXX)**

Old assertion (expects incorrect behavior):
```gherkin
Scenario: Description of old expectation (OLD)
  Given [precondition]
  When [action]
  Then [old expectation]
```

New assertion (expects correct behavior):
```gherkin
Scenario: Description of new expectation (NEW)
  Given [precondition]
  When [action]
  Then [new expectation]
  
  # Validates: [Why this is the correct behavior]
```

[Repeat for each test requiring updates]

**Implementation approach:**

Use `multi_replace_string_in_file` to update all tests in a single operation. Each replacement should:
- Include sufficient context (3-5 lines before/after)
- Update the assertion to match new behavior
- Update or add comments explaining the change

**Verification:**

After updates, run:
```bash
pytest tests/test_file.py -v
```

All [X] previously failing tests should now pass.

**Final verification:**

After completing all regression fixes, run full test suite:
```bash
pytest tests/ -v --cov=spafw37 --cov-report=term-missing
```

All tests should pass (XXX passed, X skipped).

[↑ Back to top](#table-of-contents)

## Success Criteria

- [ ] [Specific deliverable 1]
- [ ] [Specific deliverable 2]
- [ ] [Specific deliverable 3]
- [ ] [Test coverage requirement]
- [ ] [Documentation requirement]
- [ ] [Example requirement]
- [ ] [Performance requirement if applicable]
- [ ] [Backward compatibility requirement]
- [ ] All existing tests still passing
- [ ] Overall test coverage remains above [X]%
- [ ] Issue #[NUMBER] closed with reference to implementation

[↑ Back to top](#table-of-contents)

---

## Implementation Plan Changes

**Note:** This section documents changes made to the implementation plan after the initial core implementation was completed. Include this section only if the plan evolved during implementation.

This section documents changes made to the implementation plan after the initial core implementation (Steps 1-N) was completed.

### Post-Implementation Analysis

After completing Steps 1-N, comprehensive testing revealed [X] test failures that required additional work:

1. **[X] [category] test failures** - [Brief description of what was discovered]

2. **[X] [category] test failures** - [Brief description of what was discovered]

### Additional Implementation Steps

[X] additional steps were added to the "Fixing Regressions" section:

- **Step [N+1]**: [Brief description of what this step does]
- **Step [N+2]**: [Brief description of what this step does]

### Additional Considerations

[X] additional considerations were documented and resolved:

- **Consideration #X**: [Name] (RESOLVED - addressed by Step [N+1])
- **Consideration #Y**: [Name] (RESOLVED - addressed by Step [N+2])

### Timeline

- Steps 1-N: Implemented and tested (core functionality complete)
- Step [N+1]: Implemented ([brief result])
- Step [N+2]: Implemented ([brief result])
- Final result: All [XXX] tests passing, [XX]% coverage

[↑ Back to top](#table-of-contents)

---

## CHANGES for vX.X.X Release

Issue #[NUMBER]: [Issue Title]

### Issues Closed

- #[NUMBER]: [Issue Title]

### Additions

- `function_name()` [brief description of what it does].
- `CONSTANT_NAME` [brief description].

### Removals

None.

### Changes

None.

### Migration

No migration required. New functionality only.

**Note:** If implementation includes behavior changes that might affect existing code, add explicit warnings:

**[If behavior changed]:** [Component] now [new behavior] instead of [old behavior]. If your code relied on [old behavior], update [what needs updating].

### Documentation

- `doc/file.md` [what was added/changed]
- `examples/example.py` [brief description]

### Testing

- [X] new tests in `tests/test_file.py` covering [specific functionality]
- [X] new tests in `tests/test_other.py` verifying [specific behavior]
- [X] existing tests in `tests/test_file.py` updated to reflect [what changed]:
  - `test_name_1` - [Brief description of update]
  - `test_name_2` - [Brief description of update]
- [If regression fixes] [X] tests in `tests/test_file.py` updated for [reason]
- Tests cover [comprehensive list of what's covered]
- All tests updated to reflect [any timing/behavior changes]
- Final test results: [XXX] passed, [X] skipped, [XX.XX]% coverage

---

Full changelog: https://github.com/minouris/spafw37/compare/vX.Y.Z-1...vX.Y.Z  
Issues: https://github.com/minouris/spafw37/issues/[NUMBER]

[↑ Back to top](#table-of-contents)
---

## Template Usage Instructions

### Writing Style Guidelines

1. **Be technical and dispassionate**
   - Use precise technical language
   - Avoid marketing language or hype
   - State facts without embellishment
   - No exclamation marks or enthusiastic language

2. **Be specific and concrete**
   - Include exact file paths
   - Include exact function names
   - Include code examples where helpful
   - Specify error messages and conditions

3. **Maintain consistent structure**
   - Use the same heading levels throughout
   - Keep bullet point formatting consistent
   - Always include "Back to top" links after sections
   - Number all main sections and subsections

4. **Focus on implementation details**
   - Explain what to build, not why it's exciting
   - Include implementation order when relevant
   - Specify test requirements for each step
   - Document alternatives and decisions

### Section-Specific Guidance

**Overview:**
- 2-4 paragraphs explaining the issue
- List 3-5 key architectural decisions
- Keep it high-level but precise

**Implementation Methodology (Optional):**
- Only include if following a specific pattern
- Explain the approach and its benefits
- Keep it concise (1-2 paragraphs)

**Implementation Steps:**
- Number all steps sequentially
- Start each step with affected file(s)
- Include implementation order if steps have sub-steps
- Provide code examples for complex logic
- Always specify test requirements
- Use "Back to top" links after each step

**Further Considerations:**
- Document design decisions and trade-offs
- Use Q&A format (Question/Answer/Rationale/Implementation)
- Mark status (RESOLVED, PENDING, etc.)
- Include alternatives considered and why they were rejected
- Use "Back to top" links after each consideration

**Success Criteria:**
- Use checkboxes for each criterion
- Be specific and measurable
- Include test coverage requirements
- Include documentation requirements
- Always end with test pass rate and coverage percentage

**Documentation:**
- Add version notes (\"**Added in vX.X.X**\") at the start of any new sections
- This helps users identify when functionality was introduced
- Place version note immediately after section heading, before descriptive text

### Common Patterns to Follow

1. **File references:** Always use backticks and full paths: `src/spafw37/module.py`

2. **Function references:** Always use backticks and parentheses: `function_name()`

3. **Constants:** Always use backticks and UPPER_CASE: `CONSTANT_NAME`

4. **Code blocks:** Always specify language for syntax highlighting:
   ````markdown
   ```python
   def example():
       pass
   ```
   ````

5. **Navigation:** Always include table of contents links and "Back to top" links

6. **Testing:** Always specify what each test validates, not just the test name

### What NOT to Do

❌ Don't use marketing language ("powerful", "flexible", "robust", "elegant")
❌ Don't use internal jargon without explanation
❌ Don't use exclamation marks or enthusiastic language
❌ Don't skip test specifications for implementation steps
❌ Don't forget "Back to top" links after major sections
❌ Don't use vague descriptions - be specific and concrete
❌ Don't deviate from the established section structure
