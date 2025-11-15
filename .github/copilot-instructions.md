# GitHub Copilot Instructions for spafw37

## Project Overview

spafw37 is a lightweight Python 3.7+ framework for building command-line applications with advanced configuration management, command orchestration, multi-phase execution, cycle support, and integrated logging.

**Repository:** https://github.com/minouris/spafw37

## Development Environment

### Python Version
- This project **requires Python 3.7** (Python 3.7.0 or higher, but less than Python 4.0)
- All code must be compatible with Python 3.7.0 syntax and features
- Do not use features introduced in Python 3.8 or later (e.g., walrus operator `:=`, positional-only parameters)

### Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
```

## Project Structure

### Source Code (`src/spafw37/`)
Main package source code with modular architecture:

- `core.py` - **Public API facade** - Main entry point for framework consumers
- `cli.py` - Command-line interface parsing and execution
- `command.py` - Command queue and execution system
- `config.py` - Configuration management and persistence
- `config_func.py` - Configuration utility functions
- `configure.py` - Configuration initialisation and setup
- `param.py` - Parameter definition, parsing, and validation
- `cycle.py` - Cycle (loop) management for repeating command sequences
- `help.py` - Automatic help generation system
- `logging.py` - Logging functionality and scopes
- `logging_config.py` - Logging configuration and setup

#### Constants (`src/spafw37/constants/`)
Configuration constants for framework components:

- `command.py` - Command-related constants (names, actions, dependencies, phases)
- `config.py` - Configuration constants (file paths, modes)
- `cycle.py` - Cycle constants (init, loop, commands)
- `logging.py` - Logging constants (levels, scopes)
- `param.py` - Parameter constants (types, aliases, defaults, validation)
- `phase.py` - Phase constants (setup, cleanup, execution, teardown, end)

### Documentation (`doc/`)
Comprehensive user guides and API reference:

- `README.md` - Framework overview and getting started guide
- `parameters.md` - Parameter types, aliases, persistence, validation
- `commands.md` - Command definition, dependencies, orchestration
- `phases.md` - Multi-phase execution and lifecycle management
- `cycles.md` - Repeating command sequences and iteration patterns
- `configuration.md` - Configuration management and persistence
- `logging.md` - Logging system and configuration
- `api-reference.md` - Complete API documentation

### Examples (`examples/`)
Focused examples demonstrating specific features:

- **Parameters:** `params_basic.py`, `params_toggles.py`, `params_lists.py`, `params_required.py`, `params_runtime.py`, `params_groups.py`
- **Commands:** `commands_basic.py`, `commands_sequencing.py`, `commands_dependencies.py`, `commands_next.py`, `commands_required.py`, `commands_trigger.py`, `commands_visibility.py`
- **Cycles:** `cycles_basic.py`, `cycles_loop_start.py`, `cycles_nested.py`
- **Phases:** `phases_basic.py`, `phases_custom_order.py`, `phases_extended.py`, `phases_custom.py`
- **Configuration:** `config_basic.py`, `config_persistence.py`

### Tests (`tests/`)
Comprehensive test suite with 80%+ coverage requirement:

- `test_cli.py` - CLI parsing and execution tests
- `test_command.py` - Command orchestration tests
- `test_config.py` - Configuration management tests
- `test_cycle.py` - Cycle execution tests
- `test_help.py` - Help generation tests
- `test_logging.py` - Logging system tests
- `test_phase.py` - Phase management tests

### CI/CD (`.github/`)
GitHub Actions workflows and development instructions:

- `workflows/test.yml` - Automated testing on push/PR (reusable workflow)
- `workflows/publish-testpypi.yml` - TestPyPI publishing with auto-versioning
- `scripts/increment_version.py` - Version management script (PEP 440 .devN format)
- `instructions/python37.instructions.md` - Detailed coding standards
- `copilot-instructions.md` - This file

## Testing

### Running Tests
```bash
pytest tests/ -v --cov=spafw37 --cov-report=term-missing
```

### Coverage Requirements
- Minimum test coverage: **80%** (enforced by CI/CD)
- Target test coverage: **90%** (recommended for new code)
- Write unit tests for all new functions and classes
- Do not modify tests to make them pass; fix the underlying code instead

### Test Documentation Standards
- All test functions **MUST** contain a docstring with a minimum of three sentences that:
  1. Describes what the test is for (the specific behavior or functionality being tested)
  2. States what the expected outcome should be
  3. Explains why this outcome is expected (the reasoning or specification it validates)
- This helps in understanding the intent of the test and aids future maintainers

### Test Granularity
- Each test function **MUST** test exactly one outcome or behavior at a time
- Do not combine multiple different assertions or scenarios in a single test function
- If testing multiple related scenarios, create separate test functions for each
- Fine-grained tests make it easier to identify what broke when a test fails
- Tests should follow the same code quality standards as production code (naming, documentation, clarity)

### Naming in Tests
- **Tests are NOT EXEMPT from naming requirements**
- Test code must follow the same naming standards as production code
- Use descriptive names for all variables, even loop indices
- No single-letter variables or lazy placeholders like `tmp`, `data`, `result`

## Code Style and Standards

### General Python Guidelines
- Follow **PEP 8** style guidelines strictly
- Use descriptive names for variables, functions, and classes
- Do not add type hints for function parameters and return types - keep args and return types untyped for Python 3.7 compatibility and simplicity
- Include docstrings for all public functions and classes
- Keep functions small and focused (max 3 steps before breaking into helpers)

### Nested-Structure and Single-Responsibility Rules (Mandatory)

The following rules are part of the repository's coding standards. Apply them to all source files (tests are exempt from extraction rules but not naming/documentation rules):

- **General rule:** If a nested block (the body of an `if`, `elif`, `else`, `for`, `while`, `with`, `try`, etc.) can be refactored into a small helper method, do it. The body of every nested block should be, wherever practical, a single call to a clearly-named helper that performs the work.

- **Single-responsibility:** Each helper method or small class should do one thing and do it well. If a code sequence computes a single value using one or two intermediate variables, extract it to a method like `_compute_foo(...)` and return the final value.

- **Boundary modules/classes:** Large boundary classes or modules that group related but distinct concerns MUST compose smaller helper classes or modules (for example, `BreakpointManager`, `EventManager`, `Evaluator`, `Tracer`). Do not lump multiple separate responsibilities into one giant class.

- **Dependency Injection:** For ALL composition-based classes, use Dependency Injection to provide dependencies via the constructor or factory methods. Avoid hard-coding dependencies inside classes; this improves testability and modularity. Create Factory classes for all classes that have composition-based dependencies.

- **Testing with mocks:** Use mocks for helper classes when unit testing boundary classes. This ensures that tests remain focused on the class under test and do not inadvertently test the behavior of its dependencies, and also reduces the time taken to execute tests with complex behaviors.

- **Readability and testing:** This rule exists to improve readability, reduce cognitive load, and make unit testing easy. Small, focused helpers are easier to test and reason about than long nested blocks.

- **Exceptions and pragmatics:** Very short nested blocks (one or two trivial statements that are obviously cohesive) may remain inline. Use judgement; when in doubt, extract. Tests are allowed to be full subprograms and need not be split.

- **Law of Demeter:** Do not access members of a class directly from outside that class. Always use public methods to interact with class state. Classes that expose operations of their members directly should have delegate methods to encapsulate that behavior. (e.g. Don't use `object.member.method()`; instead, use `object.method_that_uses_member()`).

- **Method naming and responsibility:** Always ensure that methods and functions do what their name suggests. A method that returns content length from a header should be called `get_content_length()`, not `process_header()` or similar. That same method should not be responsible for parsing the header as well as extracting the length; those are two separate concerns and should be handled by separate methods:
    ```python
    headers = parse_header(header_data)
    content_length = get_content_length(headers)
    ```

### Naming Requirements

- All members, from the biggest class to the smallest index variable, must have descriptive, meaningful names that convey their purpose and usage clearly.
- Use full words, not abbreviations in names (e.g., use `message_length` instead of `msg_len`).
- **NEVER** use single-letter names, even for loop indices - loop indexes should be named descriptively, e.g., `line_index`, `item_index`, etc.
- **NEVER** use lazy placeholder names like `tmp`, `data`, `result`, `val` - use specific descriptive names like `parsed_message`, `breakpoint_id`, `validation_result`.
- Use an "owner_item" style of naming for variables and helpers to improve clarity, e.g., `stack_frame` ("This is a frame in a stack") or `thread_id` ("This is the id of a thread"):
    - Do not prefix local variable or helper names with the local module or type name unless the prefix disambiguates across nearby scopes or meaningfully improves readability. For example, prefer `stack_frame` ("We are looping over frames in a stack") or `thread_id` ("This is the id of the thread") over `tracer_stack_frame` or `tracer_thread_id` inside `tracer.py` because the tracer module context is already clear.
    - Use an owner prefix only when it avoids genuine ambiguity (for example, when two different collaborators exposed to the same scope naturally have the same noun and a prefix prevents confusion).
- **Tests are NOT EXEMPT from these naming requirements** - test code must follow the same naming standards as production code.

### Import Rules

- **Prefer absolute imports** for all modules within the package, rather than relative (dot) notation: use `from parent import child` rather than `from .child`.

- **For constants** (UPPER_SNAKE_CASE), import them directly into the module namespace to improve readability: use `from module import CONSTANT_NAME` rather than `import module` followed by `module.CONSTANT_NAME`.

- **For importing multiple items** from the same module, group them in a single import statement using parentheses, with subimports indented on a new line, for clarity:
    ```python
    from module import (
        CONSTANT_ONE,
        CONSTANT_TWO,
        CONSTANT_THREE,
    )
    ```

- **For non-constant imports** (classes, functions), prefer importing the immediate parent module and accessing members via the module namespace to improve clarity: use `from spafw37 import param` followed by `param.ParamClass()` (when used later in code). This ensures references are concise and clear. Only include the top-level namespace in references if ambiguity arises (e.g., when importing `param` from multiple sources). For example:
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

- **When importing modules with common names** (like `core`, `utils`, `config`) that might conflict with application code, use an alias that clearly identifies the package to prevent namespace collisions:
    ```python
    # Preferred for demo/example code to prevent collisions:
    from spafw37 import core as spafw37
    spafw37.run_cli()
    
    # Also acceptable but less clear in user code:
    from spafw37 import core
    core.run_cli()
    ```

### Architectural Patterns

- **Facade Pattern:** The `core.py` module serves as the public API facade for spafw37. Application code should import from `core` (aliased as `spafw37`) and use its delegate methods, not directly import internal modules like `param`, `command`, or `config`.
    ```python
    # Correct - using the facade:
    from spafw37 import core as spafw37
    spafw37.add_params(params)
    spafw37.run_cli()
    
    # Wrong - bypassing the facade:
    from spafw37 import param, command
    param.add_params(params)
    ```

- **Respect Existing Architecture:** When modifying code, always understand the architectural intent before making changes. If a module uses a facade pattern, dependency injection, or other architectural patterns, preserve them. Do not mechanically apply import rules without considering the broader design.

- **Internal vs. Public APIs:** Modules like `param`, `command`, `config`, etc. are internal implementation details. The public API is exposed through `core.py`. Example/demo code should only use the public API to demonstrate the intended usage pattern for framework consumers.

### Documentation Requirements

- Add a one-line docstring to each extracted helper explaining its purpose, inputs, outputs, and side-effects.
- All public functions and classes must have comprehensive docstrings.
- Private/internal helpers require at minimum a one-line docstring.

### Imports
- Group imports: standard library, third-party, local modules
- Avoid external dependencies unless absolutely necessary

### Code Organisation
- Break down complex operations into fine-grained helper functions
- Each function should have a single, clear responsibility
- Use descriptive variable names that indicate purpose

## Pattern-Specific Instructions

For Python files (`**/*.py`), the detailed guidelines in `.github/instructions/python37.instructions.md` are fully incorporated above. Key areas include:
- Python 3.7 compatibility requirements
- Nested-structure and single-responsibility rules
- Function and class design principles
- Naming requirements (no single-letter variables, descriptive names)
- Import rules (absolute imports, module prefixes for functions)
- Architectural patterns (facade, dependency injection)
- Documentation requirements
- Testing standards (granularity, documentation)

## Making Changes

### Before Modifying Code
1. Understand the existing code structure and patterns
2. Check for related tests
3. Verify Python 3.7 compatibility
4. Run existing tests to establish a baseline

### When Adding Features
1. Create fine-grained, focused functions
2. Write docstrings explaining purpose, parameters, and return values
3. Add unit tests with 90%+ coverage
4. Verify PEP 8 compliance

### When Fixing Bugs
1. Identify the root cause
2. Add a test that reproduces the bug
3. Fix the underlying issue (do not modify tests to pass)
4. Verify the fix with tests
5. Check for similar issues elsewhere

## Don't Do

- Don't use Python 3.8+ features (walrus operator, positional-only params, etc.)
- Don't modify existing code outside the scope of your changes
- Don't change test expectations to make them pass
- Don't rename existing functions, classes, or variables without explicit instruction
- Don't add external dependencies without considering standard library alternatives
- Don't remove or modify working code unnecessarily

## Build and CI

The project uses GitHub Actions for continuous integration:
- Workflow file: `.github/workflows/test.yml`
- Builds with Python 3.7.9 specifically
- Runs pytest with coverage checks
- Requires 80% test coverage to pass

### CI/CD Workflows

- **Test Workflow** (`.github/workflows/test.yml`) - Reusable workflow that:
  - Builds Python 3.7.9 from source (with caching)
  - Installs dependencies
  - Runs pytest with 80% coverage requirement
  - Triggered on push/PR to main/develop
  - Can be called by other workflows via `workflow_call`

- **Publish to TestPyPI** (`.github/workflows/publish-testpypi.yml`) - Automated publishing that:
  - Runs test workflow as dependency
  - Increments version using `.github/scripts/increment_version.py`
  - Publishes to TestPyPI with TEST_PYPI_API_TOKEN
  - Commits version bump back to repo with [skip ci]
  - Uses PEP 440 versioning format (X.Y.Z.devN)

- **Release Workflow** (`.github/workflows/release.yml`) - Manual production release that:
  - Triggered manually via `workflow_dispatch` only
  - Reuses test workflow to verify all tests pass
  - Removes `.dev` suffix from version in setup.cfg
  - Creates git tag for release version (e.g., `v1.0.0`)
  - Builds and publishes to PyPI (requires PYPI_API_TOKEN secret)
  - Generates CHANGELOG.md using AI (GitHub Copilot or OpenAI) to create concise, categorized summaries from diffs and commits (falls back to structured list if AI unavailable)
  - Increments patch version and adds `.dev0` suffix for next development cycle
  - All commits use `[skip ci]` to avoid triggering test workflow
  - Creates GitHub Release with install instructions

## License

This project is licensed under the MIT License.
