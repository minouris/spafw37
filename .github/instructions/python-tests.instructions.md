---
applyTo: 'tests/**/*.py'
---

# Python Test Structure and Standards

These instructions apply to all Python test files.

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

## Test Documentation Standards

**All test functions MUST contain a docstring with a minimum of three sentences:**

1. **What:** Describes what the test is for (the specific behaviour or functionality being tested)
2. **Outcome:** States what the expected outcome should be
3. **Why:** Explains why this outcome is expected (the reasoning or specification it validates)

**This helps in understanding the intent of the test and aids future maintainers.**

**Example:**
```python
def test_validate_email_accepts_valid_addresses():
    """Test that the email validator accepts properly formatted email addresses.
    
    This test verifies that email addresses with valid username@domain.tld format
    pass validation without raising exceptions or returning errors.
    This behaviour is expected because RFC 5322 specifies this as a valid email format.
    """
    setup_function()
    result = validate_email("user@example.com")
    assert result is True
```

## Test Granularity

**Each test function MUST test exactly one outcome or behaviour at a time:**
- Do not combine multiple different assertions or scenarios in a single test function
- If testing multiple related scenarios, create separate test functions for each
- Fine-grained tests make it easier to identify what broke when a test fails
- Tests should follow the same code quality standards as production code (naming, documentation, clarity)

**Good - separate tests:**
```python
def test_parser_handles_valid_json():
    """Test that parser correctly handles valid JSON input."""
    setup_function()
    result = parse('{"key": "value"}')
    assert result == {"key": "value"}

def test_parser_rejects_invalid_json():
    """Test that parser raises ValueError for invalid JSON."""
    setup_function()
    with pytest.raises(ValueError):
        parse('{invalid json}')

def test_parser_handles_empty_string():
    """Test that parser raises ValueError for empty string input."""
    setup_function()
    with pytest.raises(ValueError):
        parse('')
```

**Bad - combined test:**
```python
def test_parser():
    """Test parser."""  # Too vague
    setup_function()
    # Testing multiple scenarios in one test
    result = parse('{"key": "value"}')
    assert result == {"key": "value"}
    
    with pytest.raises(ValueError):
        parse('{invalid}')
    
    with pytest.raises(ValueError):
        parse('')
```

## Coverage Requirements

**Minimum test coverage standards:**
- Write unit tests for all new functions and classes
- Aim for high coverage (80%+ minimum, 90%+ recommended)
- Test both success and failure paths
- Test edge cases and boundary conditions
- Do not modify tests to make them pass; fix the underlying code instead

## Naming in Tests

**Tests are NOT EXEMPT from naming requirements:**
- Test code must follow the same naming standards as production code
- See **`python.instructions.md` § Naming Requirements** for full details
- Use descriptive names for all variables, even loop indices
- No single-letter variables or lazy placeholders like `tmp`, `data`, `result`
- Use specific descriptive names like `parsed_response`, `expected_count`, `validation_error`

**Example:**
```python
def test_batch_processor_handles_multiple_items():
    """Test that batch processor correctly handles lists with multiple items."""
    setup_function()
    
    # Good naming:
    input_items = [1, 2, 3, 4, 5]
    expected_total = 15
    
    actual_total = process_batch(input_items)
    
    assert actual_total == expected_total
    
    # Bad naming (DO NOT DO THIS):
    # data = [1, 2, 3, 4, 5]
    # expected = 15
    # result = process_batch(data)
    # assert result == expected
```

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

# Examples:
def test_validate_email_accepts_valid_addresses():
def test_validate_email_rejects_addresses_without_at_sign():
def test_validate_email_rejects_addresses_without_domain():
```

## Testing Best Practices

**Write clear, maintainable tests:**
- Keep tests simple and focused
- Use descriptive assertion messages when helpful
- Avoid complex logic in tests - tests should be obviously correct
- Use test fixtures and helpers to reduce duplication, but keep tests readable
- Mock external dependencies to keep tests fast and isolated
- Test the public API, not internal implementation details (unless testing internal helpers directly)
