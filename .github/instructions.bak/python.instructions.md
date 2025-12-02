---
applyTo: "**/*.py"
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

These rules enforce code clarity, reduce cognitive load, and ensure all code is thoroughly tested.

### Nesting Depth and Block Size Limits

**Maximum nesting depth:** Code must never be nested more than **two levels** below the top-level function or method declaration.

- Level 0: Function/method declaration
- Level 1: First nested block (e.g., `if`, `for`, `while`, `with`, `try`)
- Level 2: Second nested block inside the first
- Level 3+: **PROHIBITED** - extract to helper method

**Maximum nested block size:** The body of any nested block (inside `if`, `elif`, `else`, `for`, `while`, `with`, `try`, etc.) must not exceed **two lines**.

**Mandatory extraction:** Any code that violates either limit above MUST be extracted to a helper method with a descriptive name that clearly indicates its purpose.

**Testing requirement:** ALL helper methods must have their own dedicated unit tests that verify their behaviour independently.

### Examples of Correct Code Structure

**Example 1: Nesting depth limit**
```python
# WRONG - three levels of nesting:
def handle_request(request):
    """Handle incoming request."""
    if request.is_authenticated():              # Level 1
        if request.has_permission('write'):     # Level 2
            for item in request.items:          # Level 3 - PROHIBITED
                process_item(item)

# CORRECT - maximum two levels:
def handle_request(request):
    """Handle incoming request."""
    if request.is_authenticated():              # Level 1
        handle_authenticated_request(request)   # Level 2

def handle_authenticated_request(request):
    """Handle an authenticated request.
    
    Args:
        request: The authenticated request to handle
    """
    if request.has_permission('write'):         # Level 1
        process_request_items(request.items)    # Level 2

def process_request_items(items):
    """Process items from request.
    
    Args:
        items: List of items to process
    """
    for item in items:                          # Level 1
        process_item(item)                      # Level 2
```

**Example 2: Block size limit**
```python
# WRONG - nested block exceeds two lines:
def process_items(items):
    """Process a list of items."""
    for item in items:
        if item.is_valid():
            result = compute_value(item)
            store_result(result)
            log_success(item)

# CORRECT - extract to helper:
def process_items(items):
    """Process a list of items."""
    for item in items:
        if item.is_valid():
            process_valid_item(item)

def process_valid_item(item):
    """Process a single valid item.
    
    Computes value, stores result, and logs success.
    
    Args:
        item: The item to process
    """
    result = compute_value(item)
    store_result(result)
    log_success(item)
```

**Example 3: Combining both rules**
```python
# WRONG - violates both rules:
def synchronise_data(sources):
    """Synchronise data from multiple sources."""
    for source in sources:
        if source.is_available():
            data = source.fetch_data()
            if data.is_valid():
                for record in data.records:
                    process_record(record)
                    update_cache(record)

# CORRECT - extract helpers:
def synchronise_data(sources):
    """Synchronise data from multiple sources."""
    for source in sources:
        if source.is_available():
            synchronise_source(source)

def synchronise_source(source):
    """Synchronise data from a single source.
    
    Args:
        source: The data source to synchronise
    """
    data = source.fetch_data()
    if data.is_valid():
        process_data_records(data.records)

def process_data_records(records):
    """Process and cache data records.
    
    Args:
        records: List of records to process
    """
    for record in records:
        process_and_cache_record(record)

def process_and_cache_record(record):
    """Process a single record and update cache.
    
    Args:
        record: The record to process
    """
    process_record(record)
    update_cache(record)
```

### Single-Responsibility Principle

**Each helper method must do one thing:** Extract code blocks that have a single, clear purpose into named helper functions. The helper's name must precisely describe what it does.

**Method naming and responsibility:** A method must do exactly what its name suggests, nothing more, nothing less. A method called `get_content_length()` should only return the content length, not parse headers and extract length. Separate concerns into separate methods.

```python
# CORRECT - separate concerns:
headers = parse_header(header_data)
content_length = get_content_length(headers)

# WRONG - mixed concerns:
content_length = process_header(header_data)  # Does too much
```

**Computing values:** If a code sequence computes a single value using intermediate variables, extract it to a method like `_compute_foo(...)` that returns the final value.

### Architecture and Composition

**Boundary modules/classes:** Large boundary classes or modules that group related but distinct concerns MUST compose smaller helper classes or modules (for example, `BreakpointManager`, `EventManager`, `Evaluator`, `Tracer`). Do not lump multiple separate responsibilities into one giant class.

**Dependency Injection:** For ALL composition-based classes, use Dependency Injection to provide dependencies via the constructor or factory methods. Avoid hard-coding dependencies inside classes; this improves testability and modularity. Create Factory classes for all classes that have composition-based dependencies.

**Testing with mocks:** Use mocks for helper classes when unit testing boundary classes. This ensures that tests remain focused on the class under test and do not inadvertently test the behaviour of its dependencies, and also reduces the time taken to execute tests with complex behaviours.

**Law of Demeter:** Do not access members of a class directly from outside that class. Always use public methods to interact with class state. Classes that expose operations of their members directly should have delegate methods to encapsulate that behaviour.

```python
# WRONG:
length = object.member.get_length()

# CORRECT:
length = object.get_member_length()
```

### Pragmatic Exceptions

**Very short nested blocks:** One or two trivial statements that are obviously cohesive and fit within the two-line limit may remain inline without extraction. Use judgement; when in doubt, extract.

**Test code:** Tests are allowed to be full subprograms and need not be split into helpers, though extracting test helpers for repeated setup or verification logic is encouraged.

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

**Function responsibilities:**
- Each function should have a single, clear responsibility
- Keep functions small and focused (max 3 distinct steps before extracting helpers)
- Use descriptive variable names that indicate purpose
- Extract complex logic into named helper functions

**Refer to "Nested-Structure and Single-Responsibility Rules" section above for:**
- Maximum nesting depth limits (2 levels)
- Maximum nested block size limits (2 lines)
- Mandatory extraction requirements
- Testing requirements for all helper methods
- Detailed examples of correct code structure
