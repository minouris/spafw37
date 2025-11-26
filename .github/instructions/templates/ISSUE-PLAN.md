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
- [Success Criteria](#success-criteria)
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

[↑ Back to top](#table-of-contents)

### 6. Update documentation

[If applicable] Update user-facing documentation to describe the new functionality. Add version notes to indicate when features were added.

---

#### 6.1. Update [doc file name]

**File:** `doc/filename.md`

[Description of what to add/change and why. Include context about where in the file and what the section should cover.]

**Location:** [Where in the file to add content - e.g., "After 'Related Section' section" or "In the 'Constants' section"]

**Content to add:**

````markdown
## [Section Heading]

**Added in vX.Y.Z**

[Full markdown content to be added to the documentation file, including:
- Feature description
- Code examples
- Usage explanations
- Links to example files
- Any other relevant content]

### Example: [Use Case Name]

```python
# Complete code example
spafw37.add_params([{
    PARAM_NAME: 'example',
    # Additional configuration
}])
```

[Explanation of the example]

See complete example in [`examples/example_file.py`](../examples/example_file.py).
````

**Tests:** Manual review to verify documentation clarity and accuracy

---

#### 6.2. Update [another doc file]

**File:** `doc/another.md`

[Description of updates needed]

**Updates required:**

1. **[Section/location name]** - [Specific change]:
   ```markdown
   [Content to add - e.g., table row, constant definition, function signature]
   ```

2. **[Another section]** - [Specific change]:
   ```markdown
   [Content to add]
   ```

3. **[Another section]** - [Specific change]:
   ```markdown
   [Content to add]
   ```

**Tests:** Manual review to verify documentation completeness and accuracy

---

#### 6.3. Update README.md

**File:** `README.md`

[Description of README updates]

**Updates required:**

1. **Features list** - Add bullet point:
   ```markdown
   - [Feature description with technical details]
   ```

2. **Examples list** - Add new example entry:
   ```markdown
   - **`example_file.py`** - [Brief description of what example demonstrates]
   ```

3. **"What's New in vX.Y.Z" section** - Add concise one-line bullet:
   ```markdown
   - [Feature summary with key constants/functions in backticks]
   ```

**Tests:** Manual review to verify README clarity and consistency

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

## CHANGES for vX.X.X Release

**Note:** This section must follow the format specified in `features/CHANGES-TEMPLATE.md`. The content will be posted as the closing comment and consumed by the release workflow.

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

### Documentation

- `doc/file.md` [what was added/changed]
- `examples/example.py` [brief description]

### Testing

- [X] new tests in `tests/test_file.py`
- Tests cover [what they cover]

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
