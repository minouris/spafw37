---
applyTo: '**/*.py'
---

# Python Coding Standards (All Python Versions)

These instructions apply to all Python files regardless of Python version. For version-specific requirements, see `python37.instructions.md`, `python38.instructions.md`, etc.

## General Python Guidelines

- Follow **PEP 8** style guidelines strictly
- Use descriptive names for variables, functions, and classes
- Include docstrings for all public functions and classes
- Group imports: standard library, third-party, local modules
- Avoid external dependencies unless absolutely necessary

## Nested-Structure and Single-Responsibility Rules (Mandatory)

The following rules improve readability, reduce cognitive load, and make unit testing easier:

**General rule:** If a nested block (the body of an `if`, `elif`, `else`, `for`, `while`, `with`, `try`, etc.) can be refactored into a small helper method, do it. The body of every nested block should be, wherever practical, a single call to a clearly-named helper that performs the work.

**Example:**
```python
# Instead of:
if condition:
    step1()
    step2()
    step3()

# Do this:
if condition:
    handle_condition()

def handle_condition():
    """Handle the condition by performing three steps."""
    step1()
    step2()
    step3()
```

**Single-responsibility:** Each helper method or small class should do one thing and do it well. If a code sequence computes a single value using one or two intermediate variables, extract it to a method like `_compute_foo(...)` and return the final value.

**Boundary modules/classes:** Large boundary classes or modules that group related but distinct concerns MUST compose smaller helper classes or modules (for example, `BreakpointManager`, `EventManager`, `Evaluator`, `Tracer`). Do not lump multiple separate responsibilities into one giant class.

**Dependency Injection:** For ALL composition-based classes, use Dependency Injection to provide dependencies via the constructor or factory methods. Avoid hard-coding dependencies inside classes; this improves testability and modularity. Create Factory classes for all classes that have composition-based dependencies.

**Testing with mocks:** Use mocks for helper classes when unit testing boundary classes. This ensures that tests remain focused on the class under test and do not inadvertently test the behaviour of its dependencies, and also reduces the time taken to execute tests with complex behaviours.

**Exceptions and pragmatics:** Very short nested blocks (one or two trivial statements that are obviously cohesive) may remain inline. Use judgement; when in doubt, extract. Tests are allowed to be full subprograms and need not be split.

**Law of Demeter:** Do not access members of a class directly from outside that class. Always use public methods to interact with class state. Classes that expose operations of their members directly should have delegate methods to encapsulate that behaviour.

**Example:**
```python
# Wrong:
length = object.member.get_length()

# Correct:
length = object.get_member_length()
```

**Method naming and responsibility:** Always ensure that methods and functions do what their name suggests. A method that returns content length from a header should be called `get_content_length()`, not `process_header()` or similar. That same method should not be responsible for parsing the header as well as extracting the length; those are two separate concerns:

```python
# Correct - separate concerns:
headers = parse_header(header_data)
content_length = get_content_length(headers)

# Wrong - mixed concerns:
content_length = process_header(header_data)  # Does too much
```

## Naming Requirements

All members, from the biggest class to the smallest index variable, must have descriptive, meaningful names that convey their purpose and usage clearly.

**Rules:**
- Use full words, not abbreviations (e.g., `message_length` not `msg_len`)
- **NEVER** use single-letter names, even for loop indices - use `line_index`, `item_index`, etc.
- **NEVER** use lazy placeholder names like `tmp`, `data`, `result`, `val` - use specific descriptive names like `parsed_message`, `breakpoint_id`, `validation_result`
- Use an "owner_item" style of naming for clarity, e.g., `stack_frame` ("This is a frame in a stack") or `thread_id` ("This is the id of a thread")
- Do not prefix local variable or helper names with the local module or type name unless the prefix disambiguates across nearby scopes or meaningfully improves readability
- Use an owner prefix only when it avoids genuine ambiguity
- **Tests are NOT EXEMPT from these naming requirements** - test code must follow the same naming standards as production code

**Examples:**
```python
# Good:
for line_index in range(len(lines)):
    current_line = lines[line_index]
    parsed_result = parse_line(current_line)

# Bad:
for i in range(len(lines)):
    l = lines[i]
    result = parse_line(l)
```

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

## Architectural Patterns

**Facade Pattern:** If a project uses a facade module (e.g., `core.py`) as the public API, application code should import from the facade and use its delegate methods, not directly import internal modules.

**Respect Existing Architecture:** When modifying code, always understand the architectural intent before making changes. If a module uses a facade pattern, dependency injection, or other architectural patterns, preserve them. Do not mechanically apply import rules without considering the broader design.

**Internal vs. Public APIs:** Internal implementation modules should not be imported directly by external code. The public API should be clearly documented and separated from internal implementation details.

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

## Code Organisation

**Break down complex operations:**
- Each function should have a single, clear responsibility
- Keep functions small and focused (max 3 steps before breaking into helpers)
- Use descriptive variable names that indicate purpose
- Extract complex logic into named helper functions

**Function size guideline:**
- If a function does more than 3 distinct steps, consider extracting helpers
- If a function has more than 2 levels of nesting, extract helpers
- If a code block has a clear single purpose, extract it to a named helper
