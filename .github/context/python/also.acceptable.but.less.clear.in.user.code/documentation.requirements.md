## Documentation Requirements

**All Python code requires documentation:**
- Public functions and classes: Comprehensive docstrings with purpose, parameters, returns, raises
- Private/internal helpers: Minimum one-line docstring explaining purpose, inputs, outputs, and side-effects
- Module-level docstring: Describe the module's purpose and key components
- Complex algorithms: Inline comments explaining non-obvious logic

**Docstring format:**
```python
def function_name(param1, param2):
    """Brief one-line summary.
    
    Detailed explanation if needed. Describe what the function does,
    any important behaviours, and how it fits into the larger system.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ExceptionType: When and why this exception is raised
    """
    pass
```