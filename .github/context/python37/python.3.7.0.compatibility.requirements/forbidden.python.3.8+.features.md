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
