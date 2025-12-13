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