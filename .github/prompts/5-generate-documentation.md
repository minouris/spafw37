# Prompt 5: Generate Documentation Changes and Success Criteria

**IMPORTANT:** Do NOT commit or push changes without explicit user permission.

## CRITICAL: NO GUESSING POLICY

**See `.github/instructions/accuracy.instructions.md` for the complete NO GUESSING POLICY (applies to ALL work).**

Key reminder: NEVER guess documentation structure or content. Base all documentation on actual implementation, verified tests, and working examples. For external tool integration, fetch and cite official documentation.

## Your Task

You are working on issue #{ISSUE_NUMBER} plan document at `features/{FEATURE_NAME}.md`. This is step 5 of 6: generating documentation changes and completing success criteria.

## Documentation Standards

**From documentation.instructions.md:**

### UK English Requirements

**ALWAYS use UK English spelling and conventions:**
- colour, not color
- organise, not organize
- behaviour, not behavior
- centre, not center
- licence, not license
- initialise, not initialize

### Writing Style

1. **Be technical and dispassionate**
   - Use precise technical language
   - Avoid marketing language ("powerful", "flexible", "elegant")
   - State facts without embellishment
   - No exclamation marks

2. **Be specific and concrete**
   - Include exact function names with backticks: `function_name()`
   - Include exact file paths with backticks: `src/module/file.py`
   - Include exact constants with backticks: `CONSTANT_NAME`
   - Provide code examples where helpful

3. **Use present tense for documentation**
   - "The function returns..." not "The function will return..."
   - "This parameter specifies..." not "This parameter will specify..."

### Code References

- Functions: `function_name()` with parentheses
- Classes: `ClassName` in PascalCase
- Constants: `CONSTANT_NAME` in UPPER_CASE
- Variables: `variable_name` in lowercase
- Files: `path/to/file.py` with full or relative path
- Commands: `command --flag` in code blocks

### Code Examples

Always use fenced code blocks with language specification:

````markdown
```python
from spafw37 import core as spafw37

# Example demonstrating feature
spafw37.function_name(param=value)
```
````

## Documentation Update Requirements

**From planning.instructions.md:**

When adding new features, always update:

1. **`README.md`**
   - Features list
   - Code examples
   - Examples list
   - "What's New in vX.Y.Z" section

2. **User guide documentation** (in `doc/` directory)
   - Add "**Added in vX.Y.Z**" notes at start of new sections
   - Update relevant user guides with new functionality
   - Add code examples demonstrating usage

3. **API reference** (if adding new public functions)
   - Document function signatures
   - Describe parameters and return values
   - Include usage examples

## Step 5.1: Add Documentation Update Step

If the implementation adds or changes user-facing functionality, add a new implementation step for documentation:

```markdown
### N. Update Documentation

**Files:** `README.md`, `doc/relevant-guide.md`, `doc/api-reference.md`

Update documentation to reflect new functionality.

**Implementation order:**

1. Add version notes to new documentation sections
2. Update user guide with new functionality
3. Add code examples demonstrating usage
4. Update README with feature summary
5. Add example to examples list
6. Add "What's New" entry

**Documentation specifications:**

**Doc N.1: User guide updates**

Add to `doc/relevant-guide.md`:

````markdown
## New Feature Section

**Added in vX.Y.Z**

[Description of new functionality in 2-3 paragraphs]

### Basic Usage

[Explanation with example]

```python
from spafw37 import core as spafw37

# Example code demonstrating feature
spafw37.function_name(param=value)
```

### Advanced Usage

[More complex example if needed]

```python
# Advanced example
```

---
````

**Doc N.2: API reference updates**

Add to `doc/api-reference.md` (if adding public functions):

````markdown
### `function_name(param1, param2)`

**Added in vX.Y.Z**

Brief description of what function does.

**Parameters:**
- `param1` - Description of first parameter
- `param2` - Description of second parameter

**Returns:** Description of return value

**Example:**
```python
result = spafw37.function_name(param1=value, param2=value)
```
````

**Doc N.3: README updates**

**Features list** - Add bullet point:
```markdown
- Feature description with technical specifics
```

**Examples list** - Add entry:
```markdown
- **`example_file.py`** - Demonstrates feature usage
```

**"What's New in vX.Y.Z" section** - Add concise one-line bullet:
```markdown
- Feature description with key functions (`function1()`, `function2()`)
```

**Tests:** Manual review to verify documentation clarity and consistency

[↑ Back to top](#table-of-contents)
```

## Step 5.2: Create/Update Example File

If adding new user-facing functionality, create an example:

```markdown
### N+1. Create Example File

**File:** `examples/example_name.py`

Create a focused example demonstrating the new feature.

**Implementation order:**

1. Create example file with module docstring
2. Add necessary imports
3. Create demo functions showing different use cases
4. Add main block to run examples
5. Test example runs successfully

**Code N+1.1: Example file structure**

```python
"""Brief description of what this example demonstrates.

This example shows:
- Use case 1
- Use case 2
- Use case 3
"""

from spafw37 import core as spafw37
from spafw37.constants.module import (
    CONSTANT1,
    CONSTANT2,
)


def demo_basic_usage():
    """Demonstrate basic feature usage."""
    # Implementation
    pass


def demo_advanced_usage():
    """Demonstrate advanced feature usage."""
    # Implementation
    pass


if __name__ == '__main__':
    demo_basic_usage()
    demo_advanced_usage()
```

**Tests:** Manual verification that example runs without errors

[↑ Back to top](#table-of-contents)
```



## Table of Contents

Always update the Table of Contents at the end of any changes to the plan document to ensure it accurately reflects the current structure and status of all sections. The ToC should include three levels of depth:
- Level 1: Major sections (##)
- Level 2: Subsections (###)
- Level 3: Individual questions (e.g., Q1, Q2) and sub-items (####)

## UK English Requirements

All documentation content must use UK English spelling and conventions.

## Output Requirements

1. ✅ Add documentation update step (if needed)
2. ✅ Add example creation step (if needed)
3. ✅ All content uses UK English
4. ✅ All code references properly formatted with backticks
5. ✅ All code examples use proper fenced blocks with language

After completion, confirm:
- Number of documentation files to be updated
- Number of examples to be created
- Coverage of all implementation aspects

## Step 5.3: Update Planning Checklist

Mark the Planning Checklist item for this step as complete:
1. Find "Step 5: Generate documentation" in the Planning Checklist
2. Change `- [ ]` to `- [x]`

Ask user to review documentation before proceeding to Step 6 (changelog).
