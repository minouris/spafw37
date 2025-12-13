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