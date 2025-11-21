---
applyTo: '**/*.py'
---

## CRITICAL: NO GUESSING POLICY

**NEVER guess or make assumptions about:**
- External API specifications, endpoints, or data structures
- Third-party library behavior or usage patterns
- File formats, protocols, or standards you're not certain about
- Configuration requirements for external services

**If you don't know something:**
1. **Explicitly state that you don't know**
2. **Explain what you would need to know to proceed**
3. **Suggest where the user can find the information**
4. **Ask the user to verify or provide the correct information**

**Example of correct behavior:**
"I don't have access to the Patreon API v2 documentation, so I cannot verify the correct endpoint structure. You should check https://docs.patreon.com/ for the official API specification. Once you confirm the endpoint and data structure, I can implement it correctly."

**This applies to ALL work - code, configuration, documentation, and any other task.**

## Python 3.7 Compatibility

- Ensure that all generated Python 3.7 code is compatible with Python 3.7.0 syntax and features.
- When creating new functions or classes, be as fine-grained as possible. If an operation requires more than three steps, it should be broken down into smaller helper functions or classes.
 - When creating new functions or classes, be as fine-grained as possible. If an operation requires more than three steps, it should be broken down into smaller helper functions or classes.
 - Avoid placing large blocks of logic directly inside conditional branches. The body of an `if`/`elif`/`else` should be a single method call that encapsulates that branch's behaviour (for example: `if cond: return self._handle_cond(frame)`). This improves readability, reduces nesting, and makes unit testing of each branch simpler.
 - Prefer small helper classes or modules for separate concerns (e.g., breakpoint storage, event dispatch, expression evaluation, tracer). Keep the public host API stable and provide compatibility proxies where needed.

### Nested-structure and single-responsibility rules (mandatory)

The following rules are part of the repository's coding standards. Apply them to all source files (tests are exempt):

- General rule: If a nested block (the body of an `if`, `elif`, `else`, `for`, `while`, `with`, `try`, etc.) can be refactored into a small helper method, do it. The body of every nested block should be, wherever practical, a single call to a clearly-named helper that performs the work.

- Single-responsibility: Each helper method or small class should do one thing and do it well. If a code sequence computes a single value using one or two intermediate variables, extract it to a method like `_compute_foo(...)` and return the final value.

- Boundary modules/classes: Large boundary classes or modules that group related but distinct concerns MUST compose smaller helper classes or modules (for example, `BreakpointManager`, `EventManager`, `Evaluator`, `Tracer`). Do not lump multiple separate responsibilities into one giant class.

- For ALL composition-based classes, use Dependency Injection to provide dependencies via the constructor or factory methods. Avoid hard-coding dependencies inside classes; this improves testability and modularity. Create Factory classes for all classes that have composition-based dependencies.

- Readability and testing: This rule exists to improve readability, reduce cognitive load, and make unit testing easy. Small, focused helpers are easier to test and reason about than long nested blocks.

- Use mocks for helper classes when unit testing boundary classes. This ensures that tests remain focused on the class under test and do not inadvertently test the behavior of its dependencies, and also reduced the time taken to execute tests with complex behaviours.

- Exceptions and pragmatics: Very short nested blocks (one or two trivial statements that are obviously cohesive) may remain inline. Use judgement; when in doubt, extract. Tests are allowed to be full subprograms and need not be split.

- Observe the law of damocles: Do not access members of a class directly from outside that class. Always use public methods to interact with class state. Classes that expose operations of their members directly should have delegate methods to encapsulate that behavior. (e.g. Don't use object.member.method(); instead, use object.method_that_uses_member()).

- Always ensure that methods and functions do what their name suggests - a method that returns content length from a header should be called get_content_length(), not process_header() or similar. That same method should not be responsible for parsing the header as well as extracting the length; those are two separate concerns and should be handled by separate methods: it should be:
    ```python
    headers = parse_header(header_data)
    content_length = get_content_length(headers)
    ```

### Documentation requirements

- Documentation: Add a one-line docstring to each extracted helper explaining its purpose, inputs, outputs, and side-effects.

### Test documentation requirements

- All test functions MUST contain a docstring with a minimum of three sentences that:
  1. Describes what the test is for (the specific behavior or functionality being tested)
  2. States what the expected outcome should be
  3. Explains why this outcome is expected (the reasoning or specification it validates)
- This helps in understanding the intent of the test and aids future maintainers in comprehending the test suite.
- Test docstrings should be as detailed and clear as production code docstrings.

### Test granularity requirements

- Each test function MUST test exactly one outcome or behavior at a time
- Do not combine multiple different assertions or scenarios in a single test function
- If testing multiple related scenarios, create separate test functions for each
- Fine-grained tests make it easier to identify what broke when a test fails
- Tests should follow the same code quality standards as production code (naming, documentation, clarity)

### Naming requirements

- All members, from the biggest class to the smallest index variable, must have descriptive, meaningful names that convey their purpose and usage clearly.
- Use full words, not abbreviations in names (e.g., use `message_length` instead of `msg_len`).
- NEVER use single-letter names, even for loop indices - loop indexes should be named descriptively, eg _line_index, _item_index, etc.
- NEVER use lazy placeholder names like `tmp`, `data`, `result`, `val` - use specific descriptive names like `parsed_message`, `breakpoint_id`, `validation_result`.
- Use an "owner_item" style of naming for variables and helpers to improve clarity, e.g. `stack_frame` ("This is a frame in a stack") or `thread_id` ("This is the id of a thread"):
    - Do not prefix local variable or helper names with the local module or type name unless the prefix disambiguates across nearby scopes or meaningfully improves readability. For example, prefer `stack_frame` ("We are looping over frames in a stack") or `thread_id` ("This is the id of the thread") over `tracer_stack_frame` or `tracer_thread_id` inside `tracer.py` because the tracer module context is already clear.
- Use an owner prefix only when it avoids genuine ambiguity (for example, when two different collaborators exposed to the same scope naturally have the same noun and a prefix prevents confusion).
- **Tests are NOT EXEMPT from these naming requirements** - test code must follow the same naming standards as production code.

### Import Rules
- Prefer absolute imports for all modules within the package, rather than relative (dot) notation: use `from parent import child` rather than `from .child`.
- For constants (UPPER_SNAKE_CASE), import them directly into the module namespace to improve readability: use `from module import CONSTANT_NAME` rather than `import module` followed by `module.CONSTANT_NAME`.
- For importing multiple items from the same module, group them in a single import statement using parentheses, with subimports indented on a new line, for clarity:
    ```python
    from module import (
        CONSTANT_ONE,
        CONSTANT_TWO,
        CONSTANT_THREE,
    )
    ```
- For non-constant imports (classes, functions), prefer importing the immediate parent module and accessing members via the module namespace to improve clarity: use `from spafw37 import param` followed by `param.ParamClass()` (when used later in code). This ensures references are concise and clear. Only include the top-level namespace in references if ambiguity arises (e.g., when importing `param` from multiple sources). For example:
    ```python
    # Preferred:
    from spafw37 import param
    param_instance = param.ParamClass()

    # Avoid:
    from spafw37.param import ParamClass
    param_instance = ParamClass()

    # If ambiguity arises:
    import spafw37.param
    param_instance = spafw37.param.ParamClass()
    ```
- **NEVER import functions directly** - always import the module and call functions with the module prefix. Imported functions must never appear to be local functions. This prevents namespace collisions and makes it immediately clear where each function originates. For example:
    ```python
    # Correct:
    from spafw37 import param
    param.add_param(my_param)
    
    # Wrong - function appears to be local:
    from spafw37.param import add_param
    add_param(my_param)
    ```
- When importing modules with common names (like `core`, `utils`, `config`) that might conflict with application code, use an alias that clearly identifies the package to prevent namespace collisions:
    ```python
    # Preferred for demo/example code to prevent collisions:
    from spafw37 import core as spafw37
    spafw37.run_cli()
    
    # Also acceptable but less clear in user code:
    from spafw37 import core
    core.run_cli()
    ```

### Architectural Patterns

- **Facade Pattern**: The `core.py` module serves as the public API facade for spafw37. Application code should import from `core` (aliased as `spafw37`) and use its delegate methods, not directly import internal modules like `param`, `command`, or `config`.
    ```python
    # Correct - using the facade:
    from spafw37 import core as spafw37
    spafw37.add_params(params)
    spafw37.run_cli()
    
    # Wrong - bypassing the facade:
    from spafw37 import param, command
    param.add_params(params)
    ```
- **Respect Existing Architecture**: When modifying code, always understand the architectural intent before making changes. If a module uses a facade pattern, dependency injection, or other architectural patterns, preserve them. Do not mechanically apply import rules without considering the broader design.
- **Internal vs. Public APIs**: Modules like `param`, `command`, `config`, etc. are internal implementation details. The public API is exposed through `core.py`. Example/demo code should only use the public API to demonstrate the intended usage pattern for framework consumers.

### Framework-Reserved Parameters and Commands

**NEVER** define parameters or commands in examples that conflict with framework-provided functionality. The following are reserved:

**Reserved Parameter Names:**
- `help` - Display help information
- `config-infile` - Load configuration from file  
- `config-outfile` - Save configuration to file
- `log-verbose` - Enable verbose logging
- `log-trace` - Set log level to TRACE
- `log-trace-console` - Set console log level to TRACE
- `log-silent` - Suppress console logging
- `log-no-logging` - Suppress all logging
- `log-no-file-logging` - Suppress file logging
- `log-suppress-errors` - Disable error logging
- `log-dir` - Set log directory
- `log-level` - Set overall log level
- `log-phase-log-level` - Set phase-specific log level

**Reserved Parameter Aliases:**
- `--help`, `-h` - Help
- `--load-config`, `-l` - Load config
- `--save-config`, `-s` - Save config
- `--verbose`, `-v` - Verbose logging
- `--trace` - Trace logging
- `--trace-console` - Trace console logging
- `--silent` - Silent mode
- `--no-logging` - No logging
- `--no-file-logging` - No file logging
- `--suppress-errors` - Suppress errors
- `--log-dir` - Log directory
- `--log-level` - Log level
- `--phase-log-level` - Phase log level

**Reserved Command Names:**
- `help` - Display help
- `save-user-config` - Save user configuration
- `load-user-config` - Load user configuration

Use application-specific names in examples (e.g., `database`, `input-file`, `output-format`, `deployment-target`, `workers`) instead of generic names that might conflict with framework features.

### Additional coding standards
These rules are enforced by code review and should guide refactorings and new code. If a proposed extraction would introduce excessive API churn or duplicate logic, prefer small, well-documented helpers and add a short comment describing the reason.
- Use descriptive names for variables, functions, and classes to enhance code readability.
- Do not include type hints for function parameters and return types - keep args and return types untyped for Python 3.7 compatibility and simplicity.
- Add docstrings to all functions and classes to explain their purpose, parameters, and return values
- Do not make any changes to existing code outside of the generated sections.
- Avoid using external libraries unless absolutely necessary. Prefer standard library solutions when available.
- Write unit tests for all new functions and classes, ensuring at least 90% code coverage.
- Do not change failing tests to make them pass; instead, fix the underlying issues in the code.
- Do not change the names of existing functions, classes, or variables unless told to do so.
- Ensure that all code adheres to PEP 8 style guidelines.

- Naming clarity rule (avoid redundant owner prefixes):
    - Do not prefix local variable or helper names with the local module or type name unless the prefix disambiguates across nearby scopes or meaningfully improves readability. For example, prefer `stack_frame` or `thread_id` over `tracer_stack_frame` or `tracer_thread_id` inside `tracer.py` because the tracer module context is already clear.
    - Use an owner prefix only when it avoids genuine ambiguity (for example, when two different collaborators exposed to the same scope naturally have the same noun and a prefix prevents confusion).
    - When applying renames, update only comments that are in the same lexical scope as the renamed token (the comment-aware renaming rule). Do not perform global free-text comment rewrites; change comments in the same function/class/module scope where the token is referenced.

### Bash scripting style

- Don't use exclamation points when echoing in bash scripts. You don't need to shout anyway.
- Keep output messages professional and subdued.
