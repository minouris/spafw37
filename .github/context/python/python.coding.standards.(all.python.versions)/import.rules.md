## Import Rules

**Prefer absolute imports** for all modules within the package, rather than relative (dot) notation:
```python
# Preferred:
from parent import child

# Avoid:
from .child import something
```

**For constants** (UPPER_SNAKE_CASE), import them directly into the module namespace to improve readability:
```python
# Preferred:
from module import CONSTANT_NAME

# Avoid:
import module
... module.CONSTANT_NAME ...
```

**For importing multiple items** from the same module, group them in a single import statement using parentheses, with subimports indented on a new line:
```python
from module import (
    CONSTANT_ONE,
    CONSTANT_TWO,
    CONSTANT_THREE,
)
```

**For non-constant imports** (classes, functions), prefer importing the immediate parent module and accessing members via the module namespace to improve clarity:
```python
# Preferred:
from package import module
instance = module.ClassName()

# Avoid (unless there's ambiguity):
from package.module import ClassName
instance = ClassName()
```

**NEVER import functions directly** - always import the module and call functions with the module prefix. Imported functions must never appear to be local functions. This prevents namespace collisions and makes it immediately clear where each function originates:
```python
# Correct:
from package import module
module.function_name(args)

# Wrong - function appears to be local:
from package.module import function_name
function_name(args)
```

**When importing modules with common names** (like `core`, `utils`, `config`) that might conflict with application code, use an alias that clearly identifies the package to prevent namespace collisions:
```python
# Preferred for demo/example code to prevent collisions:
from mypackage import core as mypackage
mypackage.run()

# Also acceptable but less clear in user code:
from mypackage import core
core.run()
```
