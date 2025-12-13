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