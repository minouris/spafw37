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
