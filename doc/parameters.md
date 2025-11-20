# Parameters Guide

[← README](README.md) | [Index](README.md#documentation) | [Commands Guide →](commands.md)

## Table of Contents

- [Overview](#overview)
- [Version Changes](#version-changes)
- [Key Capabilities](#key-capabilities)
- [Parameter Definition Constants](#parameter-definition-constants)
- [Basic Parameter Definition](#basic-parameter-definition)
- [Inline Parameter Definitions](#inline-parameter-definitions)
- [Parameter Types](#parameter-types)
- [Default Values](#default-values)
- [Required Parameters](#required-parameters)
- [Configuration Binding](#configuration-binding)
- [Persistence Control](#persistence-control)
- [Mutual Exclusion (Switch Lists)](#mutual-exclusion-switch-lists)
- [Parameter Groups](#parameter-groups)
- [Runtime-Only Parameters](#runtime-only-parameters)
- [Accessing Parameter Values](#accessing-parameter-values)

## Overview

Parameters are the foundation of spafw37 applications. They define command-line arguments, store runtime configuration, and provide type-safe access to user input. This guide covers parameter definition, types, validation, resolution, and runtime manipulation.

## Version Changes

### v1.1.0

**Simplified Parameter Access:**
- Introduced unified `get_param()` function that automatically returns the correct type based on `PARAM_TYPE`
- No need to use different functions for different types - one function handles all parameter types

**Enhanced Parameter Manipulation:**
- Added `set_param()` for replacing parameter values with automatic type validation
- Added `join_param()` for accumulating values with type-specific behavior:
  - Strings: Concatenate with configurable separator (`PARAM_JOIN_SEPARATOR`)
  - Lists: Append or extend with automatic list wrapping
  - Dicts: Merge with configurable strategy (`PARAM_DICT_MERGE_TYPE`, `PARAM_DICT_OVERRIDE_STRATEGY`)

**New Configuration Constants:**
- `PARAM_JOIN_SEPARATOR` - Control string concatenation separators
- `PARAM_DICT_MERGE_TYPE` - Choose shallow or deep dictionary merging
- `PARAM_DICT_OVERRIDE_STRATEGY` - Handle dictionary key conflicts

**File Loading Improvements:**
- Multiple `@file` references now supported for list parameters (e.g., `--files @batch1.txt @batch2.txt @batch3.txt`)
- All files are loaded and their contents combined into a single list

## Key Capabilities
- Multiple CLI aliases for the same parameter (e.g., `--verbose`, `-v`)
- Type validation (text, number, toggle, list)
- Default values
- Persistence control (always saved, never saved, or user-config only)
- Mutual exclusion (switch lists)
- Parameter grouping for organised help display
- Runtime-only parameters for shared internal state that commands can read and write during execution

## Parameter Definition Constants

Parameters are defined as dictionaries using these constants as keys:

### Basic Parameter Properties

| Constant | Description |
|----------|-------------|
| `PARAM_NAME` | Name of the param |
| `PARAM_DESCRIPTION` | Long description of the param |
| `PARAM_ALIASES` | List of identifiers for this param on the CLI (e.g. --verbose, -v). Params without aliases cannot be set from the command line. |
| `PARAM_TYPE` | The data type of this param (one of PARAM_TYPE_TEXT, PARAM_TYPE_NUMBER, PARAM_TYPE_TOGGLE, PARAM_TYPE_LIST) |
| `PARAM_DEFAULT` | Default value for the param if not set. A param with a default value will always be considered "set" (will be present in config) |

### Configuration Binding

| Constant | Description |
|----------|-------------|
| `PARAM_CONFIG_NAME` | The internal name this param is bound to in the config dict. Defaults to PARAM_NAME if not specified. |
| `PARAM_REQUIRED` | Whether this param always needs to be set, either by the user or in the config file. See [examples/params_required.py](../examples/params_required.py) for usage. |

### Persistence Control

| Constant | Description |
|----------|-------------|
| `PARAM_PERSISTENCE` | Identifies how/if the param is persisted between runs. PARAM_PERSISTENCE_ALWAYS means always saved to the main config file, PARAM_PERSISTENCE_NEVER means never saved to any config file. Blank or unset means that this param is only saved to User Config files. |
| `PARAM_RUNTIME_ONLY` | Not persisted, only for runtime use, not checked at start of queue, but checked when a command that uses them is run |

### Parameter Organization

| Constant | Description |
|----------|-------------|
| `PARAM_SWITCH_LIST` | Identifies a list of params that are mutually exclusive with this one - only one param in this list can be set at a time. |
| `PARAM_GROUP` | Group name for organizing parameters in help display |

### Persistence Options

| Constant | Description |
|----------|-------------|
| `PARAM_PERSISTENCE_ALWAYS` | Param is always persisted to main config file |
| `PARAM_PERSISTENCE_NEVER` | Param is never persisted to any config file |
| `PARAM_PERSISTENCE_USER_ONLY` | Param is only persisted to user config files (default if not specified) |

### Parameter Types

| Constant | Description |
|----------|-------------|
| `PARAM_TYPE_TEXT` | Text string value |
| `PARAM_TYPE_NUMBER` | Numeric value (int or float) |
| `PARAM_TYPE_TOGGLE` | Boolean flag that flips from its default value (typically False by default, True when present) |
| `PARAM_TYPE_LIST` | List of values (e.g., multiple file paths, tags, or options) |
| `PARAM_TYPE_DICT` | Dictionary/object value (JSON format) |

## Basic Parameter Definition

Define a simple text parameter ([see example](../examples/params_basic.py)):

```python
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
)

params = [
    {
        PARAM_NAME: 'input-file',
        PARAM_DESCRIPTION: 'Path to input file',
        PARAM_ALIASES: ['--input', '-i'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
    }
]

spafw37.add_params(params)
```

Usage:
```bash
python my_app.py command --input data.txt
python my_app.py command -i data.txt
```

## Inline Parameter Definitions

Instead of separately defining and registering parameters, you can define them inline wherever they're referenced. This is especially useful for:
- Quick prototyping
- Command-specific parameters that aren't reused
- Keeping related definitions together

### Inline in Command Required Params

Define parameters directly in a command's `COMMAND_REQUIRED_PARAMS` list ([see example](../examples/inline_definitions_basic.py)):

```python
from spafw37.constants.command import COMMAND_REQUIRED_PARAMS

commands = [
    {
        COMMAND_NAME: "greet",
        COMMAND_ACTION: lambda: spafw37.output(
            f"Hello, {spafw37.get_param('user-name')}!"
        ),
        # Define parameter inline - no separate add_param() needed!
        COMMAND_REQUIRED_PARAMS: [
            {
                PARAM_NAME: "user-name",
                PARAM_TYPE: PARAM_TYPE_TEXT,
                PARAM_ALIASES: ["--name", "-n"],
            }
        ]
    }
]
```

### Inline in Switch Lists

Define mutually exclusive parameters inline in `PARAM_SWITCH_LIST`:

```python
params = [
    {
        PARAM_NAME: "verbose",
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_ALIASES: ["--verbose", "-v"],
        # Define mutually exclusive params inline
        PARAM_SWITCH_LIST: [
            {
                PARAM_NAME: "quiet",
                PARAM_TYPE: PARAM_TYPE_TOGGLE,
                PARAM_ALIASES: ["--quiet", "-q"],
            },
            {
                PARAM_NAME: "silent",
                PARAM_TYPE: PARAM_TYPE_TOGGLE,
                PARAM_ALIASES: ["--silent", "-s"],
            }
        ]
    }
]
```

**Note:** The system automatically creates bidirectional XOR relationships. In the example above:
- `verbose` excludes `quiet` and `silent`
- `quiet` excludes `verbose`
- `silent` excludes `verbose`

### Mixing Inline and Named References

You can freely mix inline definitions with references to pre-registered parameters ([see example](../examples/inline_definitions_advanced.py)):

```python
# Pre-register some common parameters
spafw37.add_params([
    {
        PARAM_NAME: "config-file",
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ["--config", "-c"],
    }
])

# Mix named and inline references
commands = [
    {
        COMMAND_NAME: "process",
        COMMAND_REQUIRED_PARAMS: [
            "config-file",  # Reference to pre-registered param
            {
                # Inline parameter definition
                PARAM_NAME: "input-file",
                PARAM_TYPE: PARAM_TYPE_TEXT,
                PARAM_ALIASES: ["--input", "-i"],
            }
        ]
    }
]
```

### Nested Inline Definitions

Inline parameters can themselves contain inline definitions (e.g., inline switch lists):

```python
commands = [
    {
        COMMAND_NAME: "deploy",
        COMMAND_REQUIRED_PARAMS: [
            {
                PARAM_NAME: "log-level",
                PARAM_TYPE: PARAM_TYPE_TEXT,
                # Inline param with its own inline switch list!
                PARAM_SWITCH_LIST: [
                    {
                        PARAM_NAME: "quiet-mode",
                        PARAM_TYPE: PARAM_TYPE_TOGGLE,
                        PARAM_ALIASES: ["--quiet"],
                    }
                ]
            }
        ]
    }
]
```

### Benefits and Best Practices

**When to use inline definitions:**
- Small, command-specific parameters not reused elsewhere
- Rapid prototyping and experimentation
- Keeping related definitions together for clarity
- Defining mutually exclusive parameter groups

**When to pre-register separately:**
- Parameters used by multiple commands
- Application-wide configuration parameters
- Complex parameter definitions you want to document separately

## Parameter Types

### Text Parameters

Accept string values:

```python
{
    PARAM_NAME: 'output-dir',
    PARAM_DESCRIPTION: 'Output directory path',
    PARAM_ALIASES: ['--output', '-o'],
    PARAM_TYPE: PARAM_TYPE_TEXT,
}
```

### Number Parameters

Accept numeric values (integers or floats):

```python
{
    PARAM_NAME: 'thread-count',
    PARAM_DESCRIPTION: 'Number of threads to use',
    PARAM_ALIASES: ['--threads', '-t'],
    PARAM_TYPE: PARAM_TYPE_NUMBER,
}
```

Usage:
```bash
python my_app.py command --threads 4
```

### Toggle Parameters

Boolean flags that flip from their default value when present on the command line ([see example](../examples/params_toggles.py)).

**Default False (most common):**

```python
{
    PARAM_NAME: 'verbose',
    PARAM_DESCRIPTION: 'Enable verbose output',
    PARAM_ALIASES: ['--verbose', '-v'],
    PARAM_TYPE: PARAM_TYPE_TOGGLE,
    PARAM_DEFAULT: False,  # Optional, False is default
}
```

Without the flag: `verbose = False`  
With the flag: `verbose = True`

```bash
python my_app.py command --verbose  # verbose becomes True
```

**Default True (less common):**

```python
{
    PARAM_NAME: 'use-cache',
    PARAM_DESCRIPTION: 'Disable cache usage',
    PARAM_ALIASES: ['--no-cache'],
    PARAM_TYPE: PARAM_TYPE_TOGGLE,
    PARAM_DEFAULT: True,
}
```

Without the flag: `use-cache = True`  
With the flag: `use-cache = False`

```bash
python my_app.py command --no-cache  # use-cache becomes False
```

### List Parameters

Accept multiple values, such as file paths, tags, or options ([see example](../examples/params_lists.py)):

```python
{
    PARAM_NAME: 'input-files',
    PARAM_DESCRIPTION: 'Input files to process',
    PARAM_ALIASES: ['--file', '-f'],
    PARAM_TYPE: PARAM_TYPE_LIST,
}
```

Usage:
```bash
python my_app.py command --file data1.txt --file data2.txt -f data3.txt
```

### Dict Parameters

Accept dictionary/object values in JSON format. Useful for API payloads, database query filters, or structured test data:

```python
{
    PARAM_NAME: 'payload',
    PARAM_DESCRIPTION: 'API request payload',
    PARAM_ALIASES: ['--payload', '-p'],
    PARAM_TYPE: PARAM_TYPE_DICT,
}
```

**Inline JSON:**
```bash
python my_app.py api-call --payload '{"user":"alice","action":"login"}'
python my_app.py api-call --payload={"key":"value"}
```

**Multi-token JSON** (when shell splits the JSON):
```bash
python my_app.py api-call --payload { "user":"alice" "action":"login" }
```

**From file** (see [@file Syntax](#file-syntax) below):
```bash
python my_app.py api-call --payload @request.json
```

The value must be a valid JSON object (dictionary). Arrays, primitives, and invalid JSON will cause an error.

## @file Syntax

All parameter types (except toggles) support loading values from files using the `@file` syntax. This is useful for:
- Large or complex values that are unwieldy on the command line
- Reusing the same values across multiple runs
- Version controlling parameter values
- Sensitive data that shouldn't appear in shell history

### Text Parameters with @file

Load text content from a file:

```bash
# Create a file with the content
echo "SELECT * FROM users WHERE active = true" > query.sql

# Load it as a parameter value
python my_app.py execute-query --sql @query.sql
```

The entire file content becomes the parameter value.

### Number Parameters with @file

Load numeric values from files:

```bash
echo "42" > count.txt
python my_app.py process --count @count.txt
```

### List Parameters with @file

Load list items from a file. The file contents are split on whitespace, with support for quoted strings:

```bash
# File: items.txt
one two three
four five

# Usage
python my_app.py process --items @items.txt
# Result: ['one', 'two', 'three', 'four', 'five']
```

**Quoted strings with spaces are preserved:**

```bash
# File: files.txt
file1.txt "my document.pdf" file2.txt "another file.doc"

# Usage
python my_app.py process --files @files.txt
# Result: ['file1.txt', 'my document.pdf', 'file2.txt', 'another file.doc']
```

**Multiple file references (v1.1.0):**

You can specify multiple `@file` references in a single parameter occurrence. All files will be loaded and their contents combined:

```bash
# File: batch1.txt
file1.txt file2.txt

# File: batch2.txt
file3.txt file4.txt

# File: batch3.txt
file5.txt

# Usage - all three files loaded and combined
python my_app.py process --files @batch1.txt @batch2.txt @batch3.txt
# Result: ['file1.txt', 'file2.txt', 'file3.txt', 'file4.txt', 'file5.txt']
```

This is particularly useful for organizing file lists into logical groups or combining multiple sources.

### Dict Parameters with @file

Load JSON objects from files:

```bash
# File: payload.json
{
  "user": "alice",
  "action": "create_order",
  "data": {
    "items": [
      {"product_id": "PROD-123", "quantity": 2}
    ]
  }
}

# Usage
python my_app.py api-call --payload @payload.json
```

### @file with --param=value Syntax

The `@file` syntax works with both separated and embedded value formats:

```bash
# Separated
python my_app.py command --input @data.txt

# Embedded with equals
python my_app.py command --input=@data.txt
python my_app.py command --config=@settings.json
```

### Best Practices for @file

- **Use absolute paths or paths relative to CWD** - The framework expands `~` for home directory
- **Quote file paths with spaces** - `python my_app.py --data @"my file.txt"`
- **Version control your files** - Great for config files, SQL queries, templates
- **Don't use @file for sensitive data in production** - File paths appear in logs; use environment variables or secure vaults instead

## Default Values

Parameters can have default values:

```python
{
    PARAM_NAME: 'log-level',
    PARAM_DESCRIPTION: 'Logging level',
    PARAM_ALIASES: ['--log-level'],
    PARAM_TYPE: PARAM_TYPE_TEXT,
    PARAM_DEFAULT: 'INFO',
}
```

Parameters with defaults are always considered "set" in configuration.

## Required Parameters

Parameters can be marked as required, meaning they must be set either by the user on the command line or in a configuration file before commands execute ([see example](../examples/params_required.py)):

```python
from spafw37.constants.param import PARAM_REQUIRED

params = [
    {
        PARAM_NAME: 'environment',
        PARAM_DESCRIPTION: 'Target environment (dev, staging, production)',
        PARAM_ALIASES: ['--env', '-e'],
        PARAM_REQUIRED: True,
    },
    {
        PARAM_NAME: 'project',
        PARAM_DESCRIPTION: 'Project name',
        PARAM_ALIASES: ['--project', '-p'],
        PARAM_REQUIRED: True,
    },
]
```

When a required parameter is not set, the framework will display a clear error message before executing any commands:

```bash
# Missing required parameters
python my_app.py deploy
# Error: Missing required parameter 'environment'

# Provide required parameters
python my_app.py deploy --env production --project myapp
# Success: Command executes
```

**Key Points:**
- Required parameters apply globally to all commands
- Validation happens before any command execution
- Can be satisfied by command-line arguments or config file values
- Parameters with `PARAM_DEFAULT` are automatically considered set

**Note:** For command-specific parameter requirements, see [Command Required Parameters](commands.md#required-parameters) in the Commands Guide.

## Configuration Binding

By default, parameters are stored in configuration using `PARAM_NAME`. Use `PARAM_CONFIG_NAME` to bind to a different config key:

```python
{
    PARAM_NAME: 'input',  # Used in documentation
    PARAM_CONFIG_NAME: 'input-file-path',  # Key in config store
    PARAM_DESCRIPTION: 'Input file',
    PARAM_ALIASES: ['--input', '-i'],
    PARAM_TYPE: PARAM_TYPE_TEXT,
}
```

Access in commands:
```python
def my_command():
    path = spafw37.get_param('input')  # Use parameter name
```

## Persistence Control

### Always Persist

Parameters saved to the main config file automatically ([see example](../examples/config_persistence.py)):

```python
{
    PARAM_NAME: 'api-key',
    PARAM_DESCRIPTION: 'API key for service',
    PARAM_ALIASES: ['--api-key'],
    PARAM_TYPE: PARAM_TYPE_TEXT,
    PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS,
}
```

### Never Persist

Temporary parameters that are never saved:

```python
{
    PARAM_NAME: 'temp-dir',
    PARAM_DESCRIPTION: 'Temporary directory',
    PARAM_ALIASES: ['--temp'],
    PARAM_TYPE: PARAM_TYPE_TEXT,
    PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER,
}
```

### User Config Only (Default)

Parameters saved only when explicitly saving user config:

```python
{
    PARAM_NAME: 'theme',
    PARAM_DESCRIPTION: 'UI theme',
    PARAM_ALIASES: ['--theme'],
    PARAM_TYPE: PARAM_TYPE_TEXT,
    # PARAM_PERSISTENCE not set = user config only
}
```

Save and load user configuration files on demand:

```bash
# Set parameters and save to a user config file
python my_app.py command --theme dark --save-user-config my_settings.json

# Load parameters from a user config file
python my_app.py command --load-user-config my_settings.json

# Parameters with user-config-only persistence will be in these files
```

## Mutual Exclusion (Switch Lists)

Ensure only one parameter from a group can be set ([see example](../examples/params_toggles.py)). Each parameter lists the other parameters it's mutually exclusive with:

```python
params = [
    {
        PARAM_NAME: 'mode-fast',
        PARAM_ALIASES: ['--fast'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_SWITCH_LIST: ['mode-thorough'],  # Mutually exclusive with mode-thorough
    },
    {
        PARAM_NAME: 'mode-thorough',
        PARAM_ALIASES: ['--thorough'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_SWITCH_LIST: ['mode-fast'],  # Mutually exclusive with mode-fast
    },
]
```

Using both `--fast` and `--thorough` will raise an error.

For larger groups, only one parameter needs to declare the list (relationships are bidirectional):

```python
params = [
    {
        PARAM_NAME: 'format-json',
        PARAM_ALIASES: ['--json'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_SWITCH_LIST: ['format-xml', 'format-yaml'],  # Creates bidirectional links
    },
    {
        PARAM_NAME: 'format-xml',
        PARAM_ALIASES: ['--xml'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        # No PARAM_SWITCH_LIST needed - already linked via format-json
    },
    {
        PARAM_NAME: 'format-yaml',
        PARAM_ALIASES: ['--yaml'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        # No PARAM_SWITCH_LIST needed - already linked via format-json
    },
]
```

**Note:** `PARAM_SWITCH_LIST` automatically creates bidirectional mutual exclusion relationships. When you add `format-xml` to `format-json`'s switch list, the framework automatically ensures `format-xml` excludes `format-json` as well. You only need to declare the relationship once.

## Parameter Groups

Organise related parameters in help display ([see example](../examples/params_groups.py)):

```python
params = [
    {
        PARAM_NAME: 'input-file',
        PARAM_ALIASES: ['--input', '-i'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_GROUP: 'Input/Output Options',
    },
    {
        PARAM_NAME: 'output-file',
        PARAM_ALIASES: ['--output', '-o'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_GROUP: 'Input/Output Options',
    },
    {
        PARAM_NAME: 'verbose',
        PARAM_ALIASES: ['--verbose', '-v'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_GROUP: 'General Options',
    },
]
```

Parameters are grouped under their `PARAM_GROUP` heading in help output. This is especially useful for applications with many parameters - grouping by functional area makes the help text much more readable.

## Runtime-Only Parameters

Parameters for storing internal state that are set programmatically by commands or the framework, not from the command line ([see example](../examples/params_runtime.py)):

```python
{
    PARAM_NAME: 'session-id',
    PARAM_DESCRIPTION: 'Current session ID',
    PARAM_ALIASES: [],  # No aliases - not settable from CLI
    PARAM_TYPE: PARAM_TYPE_TEXT,
    PARAM_RUNTIME_ONLY: True,
}
```

These parameters:
- Are not validated when commands are queued (only when actually needed)
- Are never persisted to config files
- Are typically set by the framework or other commands during execution
- Used for passing state between commands or storing dynamic values

Example usage:

```python
def init_session_command():
    """Initialise a new session."""
    import uuid
    session_id = str(uuid.uuid4())
    spafw37.set_param(param_name='session-id', value=session_id)
    spafw37.output(f"Session started: {session_id}")

def use_session_command():
    """Use the current session."""
    session_id = spafw37.get_param('session-id')
    spafw37.output(f"Using session: {session_id}")
    # ... work with session ...
```

Runtime-only parameters are useful for:
- Session identifiers
- Temporary file paths generated during execution
- Data set by one command and read by another
- Internal counters or tracking values

## Best Practices and Anti-Patterns

### DO: Use Framework Features

The framework provides built-in parameters for common needs. **Always use these instead of creating your own:**

| Framework Parameter | Purpose | Details |
|---------------------|---------|---------|
| `--verbose`, `-v` | Enable verbose mode | Shows DEBUG-level framework logging (console + file); enables `spafw37.output(verbose=True)` messages |
| `--silent` | Suppress all output | Hides framework logging (console + file); suppresses all `spafw37.output()` calls |
| `--no-logging` | Disable all framework logging | Turns off file and console logging completely |
| `--log-level LEVEL` | Set framework log level | Controls which framework messages appear (TRACE/DEBUG/INFO/WARNING/ERROR) |
| `--help`, `-h` | Display help | Automatically generated help for commands and parameters |
| `--save-config FILE` | Save user config | Persists parameters with `PARAM_PERSISTENCE_USER` to specified file |
| `--load-config FILE` | Load user config | Loads previously saved configuration from file |

### DON'T: Duplicate Framework Functionality

**Anti-Pattern Example:**
```python
# ❌ WRONG: Duplicating framework logging control
params = [
    {
        PARAM_NAME: 'verbose-mode',
        PARAM_ALIASES: ['--verbose', '-v'],  # Conflicts with framework!
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
    },
    {
        PARAM_NAME: 'quiet-mode',
        PARAM_ALIASES: ['--quiet', '-q'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
    }
]

def my_command():
    verbose = spafw37.get_param('verbose-mode')
    quiet = spafw37.get_param('quiet-mode')
    
    if verbose:
        spafw37.output("[VERBOSE] Processing...")  # Don't do this!
    if not quiet:
        spafw37.output("Processing...")  # Overly complex!
```

**Correct Pattern:**
```python
# ✅ CORRECT: Simple application output, let framework handle logging
# No custom verbose/quiet parameters needed!

def my_command():
    # Just print application output normally
    spafw37.output("Processing...")
    spafw37.output("  Item 1 complete")
    spafw37.output("Done!")
    
    # Users control framework logging independently:
    # --verbose shows framework DEBUG messages
    # --silent suppresses framework console output
    # Application output (print) is unaffected
```

### Key Principles

1. **Application Output vs. Framework Logging**
   - Use `spafw37.output()` for application output (results, progress, user-facing messages)
   - Framework logging (`--verbose`, `--silent`) controls diagnostic framework messages
   - These are independent - users can suppress framework logging while seeing application output

2. **Don't Reinvent Built-In Parameters**
   - Check existing framework parameters before creating new ones
   - Reuse established patterns (e.g., `--input`, `--output` common aliases)
   - Avoid conflicts with framework parameter aliases

3. **Keep Parameters Application-Specific**
   - Define parameters for domain-specific needs (e.g., `--max-retries`, `--timeout`)
   - Don't create parameters for cross-cutting concerns the framework already handles
   - Focus on what makes your application unique

## Advanced: Parameter Resolution Modes

**Note:** This section covers advanced internal functionality. Most users should simply use `param_name` (the parameter's `PARAM_NAME`) when calling parameter API functions.

### The Three Resolution Modes

All parameter API functions (`get_param_*()`, `set_param()`, `join_param()`) accept three optional keyword arguments for identifying parameters:

- **`param_name`** - The parameter's `PARAM_NAME` (e.g., `'input-file'`)
- **`bind_name`** - The parameter's `PARAM_CONFIG_NAME` if set, otherwise falls back to `PARAM_NAME`
- **`alias`** - Any of the parameter's `PARAM_ALIASES` without the `--` or `-` prefix

**Important:** While all three resolution parameters are technically optional, you must provide at least one of `param_name`, `bind_name`, or `alias` for the function to work.

### When Each Mode is Used

**`param_name` (Recommended for all user code):**
- Use this in your application code
- Most straightforward and matches the parameter definition
- Example: `spafw37.get_param('input-file')` or `spafw37.set_param(param_name='mode', value='default')`

**`bind_name` (Advanced use):**
- Allows accessing parameters via their internal config storage key
- Useful when `PARAM_CONFIG_NAME` differs from `PARAM_NAME`
- Example: `spafw37.get_param(bind_name='input_path')` (when `PARAM_CONFIG_NAME` is set to `'input_path'`)

**`alias` (Advanced use):**
- Resolves parameters using any of their command-line aliases
- Example: `spafw37.get_param(alias='input')` (resolves from `'--input'` alias)

### Positional Argument Behavior

When using a positional argument (e.g., `get_param('input-file')`), the value is mapped to the `param_name` parameter:

```python
# These are equivalent:
value = spafw37.get_param('input-file')
value = spafw37.get_param(param_name='input-file')
```

**Best practice:** Always use the positional form or explicit `param_name=` for clarity in application code.

### Example Parameter with All Three Identifiers

```python
# Parameter definition
{
    PARAM_NAME: 'input-file',           # Use this in your code
    PARAM_CONFIG_NAME: 'input_path',    # Internal storage key
    PARAM_ALIASES: ['--input', '-i'],   # CLI aliases
    PARAM_TYPE: PARAM_TYPE_TEXT
}

# All three resolve to the same parameter (but use positional/param_name in your code):
value = spafw37.get_param('input-file')              # ✓ Recommended (positional)
value = spafw37.get_param(param_name='input-file')   # ✓ Also fine (explicit)
value = spafw37.get_param(bind_name='input_path')    # Framework internal
value = spafw37.get_param(alias='input')             # Framework internal
```

## Accessing Parameter Values

**v1.1.0** The framework now provides a dedicated parameter-focused API for accessing and modifying parameter values. This API offers better type safety, flexible resolution, and supports both replacing and accumulating parameter values.

### Getting Parameter Values

Use the typed getters to retrieve parameter values with automatic type conversion and sensible defaults:

```python
from spafw37 import core as spafw37

def process_command():
    # Get string values (automatically typed based on PARAM_TYPE)
    input_file = spafw37.get_param('input-file')
    project_dir = spafw37.get_param('project-dir', './project')
    
    # Get integer values (automatically typed based on PARAM_TYPE)
    thread_count = spafw37.get_param('thread-count', 1)
    max_retries = spafw37.get_param('max-retries', 3)
    
    # Get boolean values (automatically typed based on PARAM_TYPE)
    verbose = spafw37.get_param('verbose')
    enable_cache = spafw37.get_param('enable-cache', True)
    
    # Get float values (automatically typed based on PARAM_TYPE)
    timeout = spafw37.get_param('timeout', 30.0)
    threshold = spafw37.get_param('threshold', 0.5)
    
    # Get list values (automatically typed based on PARAM_TYPE)
    input_files = spafw37.get_param('input-files')
    tags = spafw37.get_param('tags', [])
    
    # Get dict values (automatically typed based on PARAM_TYPE)
    settings = spafw37.get_param('settings')
    metadata = spafw37.get_param('metadata', {})
    
    if verbose:
        spafw37.output(f"Processing {input_file} with {thread_count} threads")
```

**Getting parameter values:**

**v1.1.0** Use `get_param()` to retrieve parameter values with automatic type conversion based on the parameter's `PARAM_TYPE`:

```python
# get_param() automatically returns the correct type
value = spafw37.get_param('input-file')  # Returns string, int, bool, list, or dict based on PARAM_TYPE
value = spafw37.get_param('input-file', 'default.txt')  # With default value
```

**Note:** You must provide at least one of `param_name`, `bind_name`, or `alias` for the function to work. In most cases, use positional arguments with `param_name` (e.g., `get_param('input-file')`). The `bind_name` and `alias` parameters are for advanced use cases. See [Advanced: Parameter Resolution Modes](#advanced-parameter-resolution-modes) for details.

### Setting Parameter Values

**v1.1.0** Use `set_param()` to replace parameter values with type validation:

```python
from spafw37 import core as spafw37

def init_command():
    # Set string values
    spafw37.set_param(param_name='mode', value='default')
    spafw37.set_param(param_name='output-dir', value='./output')
    
    # Set numeric values
    spafw37.set_param(param_name='file-index', value=0)
    spafw37.set_param(param_name='threshold', value=3.14)
    
    # Set boolean values
    spafw37.set_param(param_name='processing-complete', value=True)
    
    # Set list values
    spafw37.set_param(param_name='files', value=['file1.txt', 'file2.txt'])
    
    # Set dict values
    spafw37.set_param(param_name='settings', value={'key': 'value'})
```

The `set_param()` function **replaces** the existing value and validates that the type matches the parameter's PARAM_TYPE definition.

### Accumulating Parameter Values

**v1.1.0** Use `join_param()` to accumulate values instead of replacing them. The behavior depends on the parameter type:

**String parameters:** Concatenate with a separator (configurable via `PARAM_JOIN_SEPARATOR`):

```python
from spafw37.constants.param import (
    PARAM_JOIN_SEPARATOR,
    SEPARATOR_COMMA_SPACE,
)

# Default separator is space
spafw37.join_param(param_name='message', value='First')
spafw37.join_param(param_name='message', value='Second')
value = spafw37.get_param('message')  # 'First Second'

# Custom separator in parameter definition
{
    PARAM_NAME: 'tags-string',
    PARAM_TYPE: PARAM_TYPE_TEXT,
    PARAM_JOIN_SEPARATOR: SEPARATOR_COMMA_SPACE,  # Comma-space separator
}
spafw37.join_param(param_name='tags-string', value='python')
spafw37.join_param(param_name='tags-string', value='cli')
value = spafw37.get_param('tags-string')  # 'python, cli'
```

**Available separator constants:** `SEPARATOR_SPACE` (default), `SEPARATOR_COMMA`, `SEPARATOR_COMMA_SPACE`, `SEPARATOR_PIPE`, `SEPARATOR_PIPE_PADDED`, `SEPARATOR_NEWLINE`, `SEPARATOR_TAB`, or any custom string.

**List parameters:** Append single values or extend with lists:

```python
# Append single values
spafw37.join_param(param_name='files', value='file1.txt')
spafw37.join_param(param_name='files', value='file2.txt')
files = spafw37.get_param('files')  # ['file1.txt', 'file2.txt']

# Extend with a list
spafw37.join_param(param_name='files', value=['file3.txt', 'file4.txt'])
files = spafw37.get_param('files')  # ['file1.txt', 'file2.txt', 'file3.txt', 'file4.txt']
```

**Dict parameters:** Merge dictionaries with configurable merge strategy:

```python
from spafw37.constants.param import (
    PARAM_DICT_MERGE_TYPE,
    PARAM_DICT_OVERRIDE_STRATEGY,
    DICT_MERGE_SHALLOW,
    DICT_MERGE_DEEP,
    DICT_OVERRIDE_RECENT,
)

# Shallow merge (default) - top-level keys only
{
    PARAM_NAME: 'config',
    PARAM_TYPE: PARAM_TYPE_DICT,
    PARAM_DICT_MERGE_TYPE: DICT_MERGE_SHALLOW,  # Default
}
spafw37.join_param(param_name='config', value={'db': 'postgres', 'port': 5432})
spafw37.join_param(param_name='config', value={'db': 'mysql'})
config = spafw37.get_param('config')  # {'db': 'mysql', 'port': 5432}

# Deep merge - recursively merge nested dicts
{
    PARAM_NAME: 'settings',
    PARAM_TYPE: PARAM_TYPE_DICT,
    PARAM_DICT_MERGE_TYPE: DICT_MERGE_DEEP,
}
spafw37.join_param(param_name='settings', value={'api': {'timeout': 30, 'retries': 3}})
spafw37.join_param(param_name='settings', value={'api': {'timeout': 60}})
settings = spafw37.get_param('settings')  # {'api': {'timeout': 60, 'retries': 3}}

# Override strategies for conflicting keys
{
    PARAM_NAME: 'metadata',
    PARAM_TYPE: PARAM_TYPE_DICT,
    PARAM_DICT_OVERRIDE_STRATEGY: DICT_OVERRIDE_RECENT,  # Options: DICT_OVERRIDE_RECENT, DICT_OVERRIDE_OLDEST, DICT_OVERRIDE_ERROR
}
```

**Override strategies:**
- `DICT_OVERRIDE_RECENT` (default) - New value overwrites existing value
- `DICT_OVERRIDE_OLDEST` - Keep existing value, ignore new value
- `DICT_OVERRIDE_ERROR` - Raise error if key already exists

### Legacy Configuration API (Deprecated)

The older configuration-focused API (`get_config_value()`, `set_config_value()`, etc.) is **deprecated as of v1.1.0**. These functions still work for backward compatibility but will show a one-time deprecation warning.

**Migration guide:**

| Deprecated Function | New Function | Notes |
|---------------------|--------------|-------|
| `get_config_value(key)` | `get_param(key)` | Use new getter for automatic type handling |
| `get_config_str(key, default)` | `get_param(key, default)` | Direct replacement |
| `get_config_int(key, default)` | `get_param(key, default)` | Direct replacement |
| `get_config_bool(key, default)` | `get_param(key, default)` | Direct replacement |
| `get_config_float(key, default)` | `get_param(key, default)` | Direct replacement |
| `get_config_list(key, default)` | `get_param(key, default)` | Direct replacement |
| `get_config_dict(key, default)` | `get_param(key, default)` | Direct replacement |
| `set_config_value(key, value)` | `set_param(param_name=key, value=value)` | Use for replacing values |
| `set_config_list_value(key, value)` | `join_param(param_name=key, value=value)` | Use for accumulating list values |

**Example migration:**

```python
# Old (deprecated):
def old_process():
    input_file = spafw37.get_config_str('input-file')
    max_workers = spafw37.get_config_int('max-workers', 4)
    spafw37.set_config_value('file-index', 0)
    
    files = spafw37.get_config_list('files', [])
    files.append('newfile.txt')
    spafw37.set_config_value('files', files)

# New (recommended):
def new_process():
    input_file = spafw37.get_param('input-file')
    max_workers = spafw37.get_param_int('max-workers', 4)
    spafw37.set_param(param_name='file-index', value=0)
    
    # join_param() handles list accumulation automatically
    spafw37.join_param(param_name='files', value='newfile.txt')
```

**Why migrate?**
- **Better type safety:** Typed getters eliminate None-type issues
- **Clearer intent:** `join_param()` vs `set_param()` makes accumulation vs replacement explicit
- **Flexible resolution:** Reference parameters by name, binding, or alias
- **Type-specific behavior:** Automatic string concatenation, list appending, dict merging
- **Future-proof:** New features will use the param API

---

## Examples

Complete working examples demonstrating parameter features:

- **[params_basic.py](../examples/params_basic.py)** - Basic text and number parameters with default values
- **[params_toggles.py](../examples/params_toggles.py)** - Toggle parameters and mutual exclusion (switch lists) with output format selection
- **[params_lists.py](../examples/params_lists.py)** - List parameters for handling multiple values (files and tags)
- **[params_groups.py](../examples/params_groups.py)** - Parameter groups for organizing parameters in help display
- **[params_runtime.py](../examples/params_runtime.py)** - Runtime-only parameters for session state and internal values
- **[inline_definitions_basic.py](../examples/inline_definitions_basic.py)** - Inline parameter definitions in commands
- **[inline_definitions_advanced.py](../examples/inline_definitions_advanced.py)** - Advanced inline patterns (nested, mixed)

See [examples/README.md](../examples/README.md) for a complete guide to all available examples.

---

## Documentation

- **[User Guide](README.md)** - Overview and quick start
- **Parameters Guide** - Parameter definition and usage
- **[Commands Guide](commands.md)** - Command system and dependencies
- **[Phases Guide](phases.md)** - Multi-phase execution control
- **[Cycles Guide](cycles.md)** - Repeating command sequences
- **[Configuration Guide](configuration.md)** - Configuration management
- **[Logging Guide](logging.md)** - Built-in logging system
- **[API Reference](api-reference.md)** - Complete API documentation

---

[← README](README.md) | [Index](README.md#documentation) | [Commands Guide →](commands.md)
