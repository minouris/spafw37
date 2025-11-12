# Parameters Guide

[← README](README.md) | [Index](README.md#documentation) | [Commands Guide →](commands.md)

## Table of Contents

- [Overview](#overview)
- [Parameter Definition Constants](#parameter-definition-constants)
- [Basic Parameter Definition](#basic-parameter-definition)
- [Parameter Types](#parameter-types)
- [Default Values](#default-values)
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
| `PARAM_REQUIRED` | Whether this param always needs to be set, either by the user or in the config file. |

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

## Basic Parameter Definition

Define a simple text parameter:

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

Boolean flags that flip from their default value when present on the command line.

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

Accept multiple values, such as file paths, tags, or options:

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

Parameters saved to the main config file automatically:

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

Ensure only one parameter from a group can be set. Each parameter lists the other parameters it's mutually exclusive with:

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

Organize related parameters in help display:

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

Parameters are grouped under their `PARAM_GROUP` heading in help output.

## Runtime-Only Parameters

Parameters for storing internal state that are set programmatically by commands or the framework, not from the command line:

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
    print(f"Session started: {session_id}")

def use_session_command():
    """Use the current session."""
    session_id = spafw37.get_config('session-id')
    print(f"Using session: {session_id}")
    # ... work with session ...
```

Runtime-only parameters are useful for:
- Session identifiers
- Temporary file paths generated during execution
- Data set by one command and read by another
- Internal counters or tracking values

## Accessing Parameter Values

In command actions, retrieve parameter values from configuration:

```python
def process_command():
    input_file = spafw37.get_config('input-file')
    verbose = spafw37.get_config('verbose', default=False)
    thread_count = spafw37.get_config('thread-count', default=1)
    
    if verbose:
        print(f"Processing {input_file} with {thread_count} threads")
    
    # ... process ...
```

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
