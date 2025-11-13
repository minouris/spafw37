# Parameters Guide

[← README](README.md) | [Index](README.md#documentation) | [Commands Guide →](commands.md)

## Table of Contents

- [Overview](#overview)
- [Parameter Definition Constants](#parameter-definition-constants)
- [Basic Parameter Definition](#basic-parameter-definition)
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

Parameters define the command-line arguments your application accepts. They provide a flexible system for capturing user input with multiple aliases, type validation, default values, and automatic persistence. Parameters are stored in the configuration system and can be accessed by commands during execution.

Key capabilities:
- Multiple CLI aliases for the same parameter (e.g., `--verbose`, `-v`)
- Type validation (text, number, toggle, list)
- Default values
- Persistence control (always saved, never saved, or user-config only)
- Mutual exclusion (switch lists)
- Parameter grouping for organized help display
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
    path = spafw37.get_config('input-file-path')  # Use config name
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

For larger groups, each parameter lists all others in the group:

```python
params = [
    {
        PARAM_NAME: 'format-json',
        PARAM_ALIASES: ['--json'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_SWITCH_LIST: ['format-xml', 'format-yaml'],
    },
    {
        PARAM_NAME: 'format-xml',
        PARAM_ALIASES: ['--xml'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_SWITCH_LIST: ['format-json', 'format-yaml'],
    },
    {
        PARAM_NAME: 'format-yaml',
        PARAM_ALIASES: ['--yaml'],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_SWITCH_LIST: ['format-json', 'format-xml'],
    },
]
```

## Parameter Groups

Organize related parameters in help display ([see example](../examples/params_groups.py)):

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
    """Initialize a new session."""
    import uuid
    session_id = str(uuid.uuid4())
    spafw37.set_config('session-id', session_id)
    spafw37.output(f"Session started: {session_id}")

def use_session_command():
    """Use the current session."""
    session_id = spafw37.get_config('session-id')
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
    verbose = spafw37.get_config_bool('verbose-mode')
    quiet = spafw37.get_config_bool('quiet-mode')
    
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

## Accessing Parameter Values

In command actions, retrieve parameter values from configuration:

```python
def process_command():
    input_file = spafw37.get_config('input-file')
    verbose = spafw37.get_config('verbose', default=False)
    thread_count = spafw37.get_config('thread-count', default=1)
    
    if verbose:
        spafw37.output(f"Processing {input_file} with {thread_count} threads")
    
    # ... process ...
```

---

## Examples

Complete working examples demonstrating parameter features:

- **[params_basic.py](../examples/params_basic.py)** - Basic text and number parameters with default values
- **[params_toggles.py](../examples/params_toggles.py)** - Toggle parameters and mutual exclusion (switch lists) with output format selection
- **[params_lists.py](../examples/params_lists.py)** - List parameters for handling multiple values (files and tags)
- **[params_groups.py](../examples/params_groups.py)** - Parameter groups for organizing parameters in help display
- **[params_runtime.py](../examples/params_runtime.py)** - Runtime-only parameters for session state and internal values

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
