# GitHub Copilot Instructions for spafw37

## Project Overview

spafw37 is a minimal Python 3.7 package scaffold that provides a framework for building command-line applications with configuration management and command execution capabilities.

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

- `src/spafw37/` - Main package source code
  - `cli.py` - Command-line interface parsing and execution
  - `command.py` - Command queue and execution system
  - `config.py` - Configuration management
  - `param.py` - Parameter definition and parsing
  - `configure.py` - Configuration utilities
  - `config_consts.py` - Configuration constants
- `src/testapp/` - Test application example
- `tests/` - Test suite
- `.github/instructions/` - Pattern-specific coding instructions

## Testing

### Running Tests
```bash
pytest tests/ -v --cov=spafw37 --cov-report=term-missing
```

### Coverage Requirements
- Minimum test coverage: **90%**
- Write unit tests for all new functions and classes
- Do not modify tests to make them pass; fix the underlying code instead

### Known Test Issues
Some tests may have import issues in certain environments. This is a known issue and should not block development unless you are specifically fixing these tests.

## Code Style and Standards

### General Python Guidelines
- Follow **PEP 8** style guidelines strictly
- Use descriptive names for variables, functions, and classes
- Add type hints for function parameters and return types
- Include docstrings for all public functions and classes
- Keep functions small and focused (max 3 steps before breaking into helpers)

### Imports
- Use `from __future__ import annotations` for forward-compatible type hints
- Group imports: standard library, third-party, local modules
- Avoid external dependencies unless absolutely necessary

### Code Organization
- Break down complex operations into fine-grained helper functions
- Each function should have a single, clear responsibility
- Use descriptive variable names that indicate purpose

## Pattern-Specific Instructions

For Python files (`**/*.py`), refer to `.github/instructions/python37.instructions.md` for additional detailed guidelines including:
- Python 3.7 compatibility requirements
- Function and class design principles
- Documentation requirements
- Testing standards

## Making Changes

### Before Modifying Code
1. Understand the existing code structure and patterns
2. Check for related tests
3. Verify Python 3.7 compatibility
4. Run existing tests to establish a baseline

### When Adding Features
1. Create fine-grained, focused functions
2. Add comprehensive type hints
3. Write docstrings explaining purpose, parameters, and return values
4. Add unit tests with 90%+ coverage
5. Verify PEP 8 compliance

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
- Requires 90% test coverage to pass

## License

This project is licensed under the MIT License.
