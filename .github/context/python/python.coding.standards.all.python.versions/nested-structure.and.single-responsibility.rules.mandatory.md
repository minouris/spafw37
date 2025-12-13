## Nested-Structure and Single-Responsibility Rules (Mandatory)

These rules enforce code clarity, reduce cognitive load, and ensure all code is thoroughly tested.

### Nesting Depth and Block Size Limits

**Maximum nesting depth:** Code must never be nested more than **two levels** below the top-level function or method declaration.

- Level 0: Function/method declaration
- Level 1: First nested block (e.g., `if`, `for`, `while`, `with`, `try`)
- Level 2: Second nested block inside the first
- Level 3+: **PROHIBITED** - extract to helper method

**Maximum nested block size:** The body of any nested block (inside `if`, `elif`, `else`, `for`, `while`, `with`, `try`, etc.) must not exceed **two lines**.

**Mandatory extraction:** Any code that violates either limit above MUST be extracted to a helper method with a descriptive name that clearly indicates its purpose.

**Testing requirement:** ALL helper methods must have their own dedicated unit tests that verify their behaviour independently.

### Examples of Correct Code Structure

**Example 1: Nesting depth limit**
```python