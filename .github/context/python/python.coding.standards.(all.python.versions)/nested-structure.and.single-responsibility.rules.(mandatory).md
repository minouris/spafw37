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
