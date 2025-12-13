## CRITICAL: Test Structure

**Use module-level functions, NOT test classes:**
- All test functions must be defined at module level: `def test_something():`
- **DO NOT** wrap tests in classes: `class TestSomething:` is forbidden
- **DO NOT** use `self` parameter in test functions
- Call `setup_function()` or equivalent setup explicitly at the start of each test if needed

**Why this matters:**
- Consistency across the test suite
- Simpler test discovery and execution
- Clearer test isolation
- Easier to understand test structure

**Correct pattern:**
```python
def setup_function():
    """Reset global state before each test."""
    clear_state()

def test_feature_works_correctly():
    """Test that feature X works correctly.
    
    This test verifies that when condition Y is met, the system produces
    result Z. This behaviour is expected because specification W requires it.
    """
    setup_function()
    result = perform_action()
    assert result == expected_value
```

**WRONG pattern (DO NOT USE):**
```python
class TestFeature:
    def test_feature_works_correctly(self):
        """Test that feature works."""
        result = perform_action()
        assert result == expected_value
```