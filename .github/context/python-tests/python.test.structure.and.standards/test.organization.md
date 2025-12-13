## Test Organization

**Group related tests logically:**
- Keep tests for the same module/feature together
- Use clear, descriptive test function names that explain what is being tested
- Order tests from simple to complex when possible

**Test function naming convention:**
```python
def test_<function_or_feature>_<scenario>_<expected_outcome>():
    """..."""
    pass