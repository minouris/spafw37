---
applyTo: '**/*.py'
---

# Python 3.7.0 Compatibility Requirements

These instructions apply to all Python projects that must maintain Python 3.7.0 compatibility.

**These rules build upon the general Python coding standards in `python.instructions.md`.** All rules from that file apply unless explicitly overridden here. This file only contains Python 3.7.0-specific compatibility requirements and forbidden features.

## Python Version Constraint

**This project requires Python 3.7.0+:**
- All code must be compatible with Python 3.7.0 syntax and features
- Do not use features introduced in Python 3.8 or later
- Target maximum compatibility: Python 3.7.0 through Python 3.7.x
- Code should work on Python 3.7.0 without modification

## Forbidden Python 3.8+ Features

The following features are NOT available in Python 3.7 and must NOT be used:

### Walrus Operator (`:=`)
```python
# Python 3.8+ - DO NOT USE:
if (item_count := len(items)) > 10:
    print(f"List is too long ({item_count} elements)")

# Python 3.7 compatible:
item_count = len(items)
if item_count > 10:
    print(f"List is too long ({item_count} elements)")
```

### Positional-Only Parameters (`/`)
```python
# Python 3.8+ - DO NOT USE:
def process_values(first_param, second_param, /, third_param, fourth_param):
    pass

# Python 3.7 compatible:
def process_values(first_param, second_param, third_param, fourth_param):
    pass
```

### f-string `=` Specifier for Debugging
```python
# Python 3.8+ - DO NOT USE:
print(f"{user_input=}")

# Python 3.7 compatible:
print(f"user_input={user_input}")
```

### `math.prod()`
```python
# Python 3.8+ - DO NOT USE:
product_result = math.prod(numbers)

# Python 3.7 compatible:
from functools import reduce
from operator import mul
product_result = reduce(mul, numbers, 1)
```

### `typing.Literal`, `typing.TypedDict`, `typing.Final`
```python
# Python 3.8+ - DO NOT USE:
from typing import Literal, TypedDict, Final

# Python 3.7 compatible:
# Avoid using these types, or use typing_extensions backport if absolutely necessary
```

### Assignment Expressions in Comprehensions
```python
# Python 3.8+ - DO NOT USE:
[transformed_value for item in input_data if (transformed_value := transform(item)) > 0]

# Python 3.7 compatible:
[transform(item) for item in input_data if transform(item) > 0]
# Or if transform is expensive:
transformed_values = [transform(item) for item in input_data]
filtered_values = [value for value in transformed_values if value > 0]
```

## Type Hints Policy for Python 3.7

**Do not add type hints for function parameters and return types:**
- Keep arguments and return types untyped for Python 3.7 compatibility and simplicity
- Python 3.7's typing module has limitations compared to later versions
- Avoiding type hints reduces complexity and improves readability for this version
- Focus on clear naming and comprehensive docstrings instead

```python
# Preferred for Python 3.7 projects:
def calculate_total(item_prices, tax_rate):
    """Calculate the total price including tax.
    
    Args:
        item_prices: List of item prices
        tax_rate: Tax rate as a decimal (e.g., 0.1 for 10%)
    
    Returns:
        Total price including tax
    """
    subtotal = sum(item_prices)
    return subtotal * (1 + tax_rate)

# Avoid (unless project specifically requires type hints):
def calculate_total(item_prices: List[float], tax_rate: float) -> float:
    subtotal = sum(item_prices)
    return subtotal * (1 + tax_rate)
```

## Standard Library Differences

**Be aware of differences in Python 3.7 vs. later versions:**

### `dict` preserves insertion order
- Python 3.7+ guarantees dict insertion order
- This is a language feature, not just an implementation detail
- Safe to rely on dict ordering in Python 3.7+

### `asyncio` differences
- Python 3.7 has older asyncio API
- `asyncio.run()` exists but may behave differently than 3.8+
- `asyncio.create_task()` exists in 3.7
- Some asyncio features from 3.8+ are not available

### `dataclasses` available but limited
- `dataclasses` module exists in Python 3.7
- Some features added in 3.8+ (like `frozen=True` on fields) are not available
- Use with caution if targeting strict 3.7.0 compatibility

### String methods
- Most string methods work the same
- Some edge cases may differ from 3.8+

## Best Practices for Python 3.7 Projects

**Write code that's obviously compatible:**
- Prefer explicit, verbose code over clever shortcuts that might use new features
- Test with Python 3.7.0 specifically, not just 3.7.x
- Use CI/CD to enforce Python 3.7.0 compatibility
- Document any version-specific workarounds with comments

**When in doubt:**
- Check the Python 3.7 documentation specifically
- Test the feature in a Python 3.7.0 environment
- Prefer standard library features that existed in Python 3.6 (guaranteed to work in 3.7)

## Dependency Management

**Be careful with external dependencies:**
- Many packages have dropped Python 3.7 support
- Pin dependency versions to ensure Python 3.7 compatibility
- Test all dependencies with Python 3.7.0
- Consider vendoring critical dependencies if they drop 3.7 support

## Testing Requirements

**Always test with Python 3.7.0:**
- CI/CD must run on Python 3.7.0 specifically (not 3.7.x)
- Build Python 3.7.0 from source if not available in CI environment
- Run full test suite on Python 3.7.0 before releasing
