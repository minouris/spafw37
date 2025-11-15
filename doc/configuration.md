# Configuration Guide

[← Cycles Guide](cycles.md) | [Index](README.md#documentation) | [Logging Guide →](logging.md)

## Table of Contents

- [Overview](#overview)
- [Configuration Constants](#configuration-constants)
- [Runtime Configuration](#runtime-configuration)
  - [Getting Configuration Values](#getting-configuration-values)
  - [Setting Configuration Values](#setting-configuration-values)
- [Configuration Files](#configuration-files)
  - [Persistent Configuration](#persistent-configuration)
  - [User Configuration Files](#user-configuration-files)
  - [Loading Configuration](#loading-configuration)
  - [Saving Configuration](#saving-configuration)
- [Application Configuration](#application-configuration)
  - [Setting Application Name](#setting-application-name)
  - [Setting Configuration File](#setting-configuration-file)
- [Configuration Persistence](#configuration-persistence)
  - [Persistence Always](#persistence-always)
  - [Persistence Never](#persistence-never)
  - [User Config Only](#user-config-only)
  - [Runtime-Only Parameters](#runtime-only-parameters)
- [Configuration Workflow](#configuration-workflow)
- [Best Practices](#best-practices)

## Overview

The spafw37 framework provides a flexible configuration system for managing application state and user preferences. Configuration values can be:

- **Set at runtime** - From command-line arguments or programmatically
- **Persisted to files** - Saved between application runs
- **Loaded from files** - Restored on startup or on demand
- **Scoped appropriately** - Always saved, never saved, or user-config only

Key capabilities:
- Runtime parameter access via `get_config_value()` and `set_config_value()`
- Automatic persistence for designated parameters
- User config file save/load (`--save-config`, `--load-config`)
- Runtime-only parameters for temporary state
- Type-safe parameter handling (text, number, toggle, list)

## Runtime Configuration

The configuration system stores parameter values in an internal dictionary that's accessible throughout your application ([see example](../examples/config_basic.py)).

### Getting Configuration Values

Use `get_config_value()` to retrieve parameter values:

```python
from spafw37 import core as spafw37

def process_file():
    # Get a configuration value
    input_file = spafw37.get_config_value('input-file')
    verbose = spafw37.get_config_value('verbose')
    
    if verbose:
        spafw37.output(f"Processing {input_file}")
    
    # Configuration values are None if not set
    output_dir = spafw37.get_config_value('output-dir')
    if output_dir is None:
        output_dir = '.'
```

#### Typed Configuration Getters

For better type safety and linter support, use typed getters that cast values to specific types:

```python
from spafw37 import core as spafw37

def process_files():
    # Get integer values with defaults
    max_workers = spafw37.get_config_int('max-workers', 4)
    file_index = spafw37.get_config_int('file-index')  # default: 0
    
    # Get string values
    project_dir = spafw37.get_config_str('project-dir', './project')
    author = spafw37.get_config_str('author')  # default: ''
    
    # Get boolean values
    verbose = spafw37.get_config_bool('verbose')  # default: False
    is_enabled = spafw37.get_config_bool('feature-enabled', True)
    
    # Get float values
    timeout = spafw37.get_config_float('timeout', 30.0)
    threshold = spafw37.get_config_float('threshold')  # default: 0.0
    
    # Get list values
    tags = spafw37.get_config_list('tags')  # default: []
    files = spafw37.get_config_list('files', [])
```

**Available typed getters:**
- `get_config_int(config_key, default=0)` - Returns integer
- `get_config_str(config_key, default='')` - Returns string
- `get_config_bool(config_key, default=False)` - Returns boolean
- `get_config_float(config_key, default=0.0)` - Returns float
- `get_config_list(config_key, default=None)` - Returns list (wraps single values)

**Benefits:**
- Eliminates linter warnings about None types
- Provides sensible defaults automatically
- Makes type expectations explicit
- Simplifies type-dependent operations (arithmetic, string formatting, etc.)

### Setting Configuration Values

Use `set_config_value()` to set parameter values programmatically:

```python
from spafw37 import core as spafw37

def init_cycle():
    # Initialise cycle state
    spafw37.set_config_value('file-index', 0)
    spafw37.set_config_value('files-processed', 0)
    spafw37.set_config_value('errors', [])

def process_batch():
    # Update state during execution
    files_processed = spafw37.get_config_value('files-processed')
    spafw37.set_config_value('files-processed', files_processed + 1)
    
    # Append to list values
    errors = spafw37.get_config_value('errors') or []
    if error_occurred:
        errors.append(error_message)
        spafw37.set_config_value('errors', errors)
```

**Important:** Use runtime-only parameters for temporary state that shouldn't be persisted. See [Runtime-Only Parameters](#runtime-only-parameters).

## Configuration Files

The framework supports two types of configuration files:

1. **Persistent Configuration** - Main config file (default: `config.json`) automatically saved/loaded
2. **User Configuration** - Custom config files for specific scenarios or environments

### Persistent Configuration

Parameters marked with `PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS` are automatically saved to the main configuration file between runs:

```python
from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_ALIASES,
    PARAM_PERSISTENCE,
    PARAM_PERSISTENCE_ALWAYS
)

# This parameter will be saved to config.json automatically
params = [
    {
        PARAM_NAME: 'last-project-dir',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--project-dir'],
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS
    }
]

spafw37.add_params(params)
```

**Lifecycle:**
1. On startup: `config.json` is loaded automatically (if it exists)
2. When parameter is set: Value stored in persistent config
3. On exit: `config.json` is saved automatically

## User Configuration Files

User configuration files provide a convenient way to save and load parameter sets for different use cases or environments.

### CLI Parameters

| Flag | Alias | Description |
|------|-------|-------------|
| `--load-config <file>` | `-l` | Load configuration from a JSON file |
| `--save-config <file>` | `-s` | Save current configuration to a JSON file |

### Saving Configuration

Save your current parameter configuration to a file:

```bash
# Save configuration after setting parameters
myapp --input-file data.txt --output-dir results --save-config my-config.json

# Or save shorthand
myapp --input-file data.txt -s my-config.json
```

**What gets saved:**
- All parameters set by the user (from CLI or programmatically)
- Parameters with default values that were explicitly set
- **Excludes** parameters with `PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER`
- **Excludes** runtime-only parameters (`PARAM_RUNTIME_ONLY: True`)

### Loading Configuration

Load configuration files via CLI:

```bash
myapp --load-config my-config.json
# or
myapp -l my-config.json
```

The loaded configuration values are merged into the runtime config before command execution.

### Saving Configuration

Save configuration files via CLI:

```bash
myapp --input-file data.txt --output-dir results --save-config my-config.json
# or
myapp --input-file data.txt --output-dir results -s my-config.json
```

All user-configurable parameters (excluding `PARAM_PERSISTENCE_NEVER` and runtime-only params) are written to the specified file.

## Application Configuration

### Setting Application Name

Set the application name for logging and display purposes:

```python
from spafw37 import core as spafw37

# Set application name early in your main script
spafw37.set_app_name('my-application')

# Get application name
app_name = spafw37.get_app_name()  # Returns 'my-application'
```

The application name appears in:
- Log file names
- Help output
- Error messages

### Setting Configuration File

Change the default persistent configuration file location:

```python
from spafw37 import core as spafw37

# Set custom config file location
spafw37.set_config_file('~/.config/myapp/settings.json')

# Now PARAM_PERSISTENCE_ALWAYS params save to this file
```

Default is `config.json` in the current directory.

## Configuration Persistence

Parameters have different persistence behaviors based on the `PARAM_PERSISTENCE` property ([see example](../examples/config_persistence.py)):

### Persistence Always

**Use for:** User preferences that should persist between runs (e.g., default directories, theme settings, recent files).

```python
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_PERSISTENCE,
    PARAM_PERSISTENCE_ALWAYS
)

params = [
    {
        PARAM_NAME: 'default-output-dir',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--output-dir', '-o'],
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS
    }
]
```

**Behavior:**
- Automatically saved to main config file (`config.json`)
- Loaded on every application startup
- Survives application restarts

### Persistence Never

**Use for:** Sensitive data, temporary flags, or parameters that should never be saved (e.g., passwords, one-time operations).

```python
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_PERSISTENCE,
    PARAM_PERSISTENCE_NEVER
)

params = [
    {
        PARAM_NAME: 'api-key',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--api-key'],
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
]
```

**Behavior:**
- Never saved to any config file (main or user configs)
- Must be provided each run (via CLI or programmatically)
- Not included in `--save-config` output

### User Config Only

**Use for:** Most application parameters that users might want to save in scenario-specific configs.

```python
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT
)

params = [
    {
        PARAM_NAME: 'input-file',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--input', '-i']
        # No PARAM_PERSISTENCE specified = user config only
    }
]
```

**Behavior:**
- Not saved to main config file automatically
- Included in user config files (`--save-config`)
- Can be loaded from user config files (`--load-config`)

### Runtime-Only Parameters

**Use for:** Internal state management in cycles and complex workflows.

```python
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_RUNTIME_ONLY
)

params = [
    {
        PARAM_NAME: 'current-file-index',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True  # Internal state only
    },
    {
        PARAM_NAME: 'files-remaining',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True
    }
]
```

**Behavior:**
- Never persisted (like `PARAM_PERSISTENCE_NEVER`)
- Not validated at queue start
- Validated only when commands that use them execute
- Perfect for cycle state that changes during execution

**See:** [Cycles Guide - State Management](cycles.md#state-management) for detailed examples.

## Configuration Workflow

Here's how configuration flows through a typical application run:

```python
from spafw37 import core as spafw37
from spafw37.constants.param import *
from spafw37.constants.command import *

# 1. Set application name and config file location
spafw37.set_app_name('file-processor')
spafw37.set_config_file('~/.file-processor/config.json')

# 2. Define parameters with different persistence
params = [
    {
        PARAM_NAME: 'last-directory',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS  # Saved automatically
    },
    {
        PARAM_NAME: 'input-file',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--input', '-i']
        # User config only - not auto-saved
    },
    {
        PARAM_NAME: 'current-index',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True  # Never saved
    }
]

spafw37.add_params(params)

# 3. Define commands that use configuration
def process_files():
    # Get persistent preference
    last_dir = spafw37.get_config_value('last-directory')
    
    # Get current run parameter
    input_file = spafw37.get_config_value('input-file')
    
    # Set runtime state
    spafw37.set_config_value('current-index', 0)
    
    # Update persistent preference for next run
    import os
    new_dir = os.path.dirname(input_file)
    spafw37.set_config_value('last-directory', new_dir)

commands = [
    {
        COMMAND_NAME: 'process',
        COMMAND_ACTION: process_files,
        COMMAND_REQUIRED_PARAMS: ['input-file']
    }
]

spafw37.add_commands(commands)

# 4. Run the CLI
# On startup: config.json loaded automatically (last-directory restored)
# User runs: myapp --input data.txt --save-config scenario1.json
# On execution: process_files() runs, updates last-directory
# On exit: config.json saved (last-directory persisted), scenario1.json saved
spafw37.run_cli()
```

**Execution Flow:**

1. **Startup**
   - `config.json` loaded (persistent config)
   - CLI arguments parsed
   - User config loaded (if `--load-config` specified)

2. **Execution**
   - Commands access config via `get_config_value()`
   - Commands update config via `set_config_value()`
   - Runtime-only params used for temporary state

3. **Shutdown**
   - `config.json` saved (persistent params only)
   - User config saved (if `--save-config` specified)
   - Runtime-only params discarded

## Best Practices

### Use Runtime-Only for Internal State

```python
# Good - cycle state as runtime-only params
params = [
    {
        PARAM_NAME: 'batch-index',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True
    }
]

def init_cycle():
    spafw37.set_config_value('batch-index', 0)

def has_more_batches():
    index = spafw37.get_config_value('batch-index')
    return index < total_batches
```

### Separate Persistent Preferences from Run Parameters

```python
# Persistent - user preferences
params = [
    {
        PARAM_NAME: 'default-format',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS
    },
    # User config only - scenario-specific
    {
        PARAM_NAME: 'input-files',
        PARAM_TYPE: PARAM_TYPE_LIST,
        PARAM_ALIASES: ['--input', '-i']
    }
]
```

### Never Persist Sensitive Data

```python
# Good - sensitive params never saved
params = [
    {
        PARAM_NAME: 'api-key',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--api-key'],
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    },
    {
        PARAM_NAME: 'password',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--password'],
        PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER
    }
]
```

### Use Config Files for Scenarios

```bash
# Save different configurations for different scenarios
myapp --input data/large/*.txt --workers 8 --save-config high-volume.json
myapp --input data/small/*.txt --workers 2 --save-config low-volume.json

# Load appropriate config for each scenario
myapp --load-config high-volume.json
myapp --load-config low-volume.json
```

### Handle Missing Configuration Gracefully

```python
def process():
    # Provide defaults for optional config
    output_dir = spafw37.get_config_value('output-dir') or './output'
    timeout = spafw37.get_config_value('timeout') or 30
    
    # Check required config
    input_file = spafw37.get_config_value('input-file')
    if not input_file:
        raise ValueError("input-file is required")
```

### Organise Configuration in Application Setup

```python
from spafw37 import core as spafw37

def setup():
    # Application identity
    spafw37.set_app_name('my-app')
    spafw37.set_config_file('~/.config/my-app/settings.json')
    
    # Logging
    spafw37.set_log_dir('~/.local/share/my-app/logs')
    
    # Define all parameters
    spafw37.add_params(persistent_params)
    spafw37.add_params(runtime_params)
    spafw37.add_params(scenario_params)
    
    # Define commands
    spafw37.add_commands(commands)

if __name__ == '__main__':
    setup()
    spafw37.run_cli()
```

---

## Examples

Complete working examples demonstrating configuration features:

- **[config_basic.py](../examples/config_basic.py)** - Runtime configuration with get_config_value and set_config_value
- **[config_persistence.py](../examples/config_persistence.py)** - Configuration persistence with PARAM_PERSISTENCE_ALWAYS vs PARAM_PERSISTENCE_NEVER

See [examples/README.md](../examples/README.md) for a complete guide to all available examples.

---

## Documentation

- **[User Guide](README.md)** - Overview and quick start
- **[Parameters Guide](parameters.md)** - Parameter definition and usage
- **[Commands Guide](commands.md)** - Command system and dependencies
- **[Phases Guide](phases.md)** - Multi-phase execution control
- **[Cycles Guide](cycles.md)** - Repeating command sequences
- **Configuration Guide** - Configuration management
- **[Logging Guide](logging.md)** - Built-in logging system
- **[API Reference](api-reference.md)** - Complete API documentation

---

[← Cycles Guide](cycles.md) | [Index](README.md#documentation) | [Logging Guide →](logging.md)
