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