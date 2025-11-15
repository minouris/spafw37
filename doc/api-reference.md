# API Reference

[← Logging Guide](logging.md) | [Index](README.md#documentation)

## Table of Contents

- [Overview](#overview)
- [Import Pattern](#import-pattern)
- [Core Module (spafw37.core)](#core-module-spafw37core)
  - [Application Control](#application-control)
  - [Application Configuration](#application-configuration)
  - [Parameter Management](#parameter-management)
  - [Command Management](#command-management)
  - [Runtime Configuration](#runtime-configuration)
  - [Output Functions](#output-functions)
  - [Logging Functions](#logging-functions)
- [Constants Modules](#constants-modules)
  - [Parameter Constants](#parameter-constants-spafw37constantsparam)
  - [Command Constants](#command-constants-spafw37constantscommand)
  - [Cycle Constants](#cycle-constants-spafw37constantscycle)
  - [Phase Constants](#phase-constants-spafw37constantsphase)
  - [Logging Constants](#logging-constants-spafw37constantslogging)
  - [Configuration Constants](#configuration-constants-spafw37constantsconfig)

## Overview

The spafw37 framework uses a **facade pattern** where `spafw37.core` provides the primary public API. Application developers should primarily interact with:

1. **`spafw37.core`** - Main API facade
2. **`spafw37.constants.*`** - Constant definitions for dictionaries

This design keeps the API surface clean and shields applications from internal implementation details.

## Import Pattern

**Recommended import pattern for all applications:**

```python
# Import the facade
from spafw37 import core as spafw37

# Import constants needed for your definitions
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_ALIASES,
    # ... other constants as needed
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_ACTION,
    COMMAND_REQUIRED_PARAMS,
    # ... other constants as needed
)
```

**Key principles:**
- Import `core` as `spafw37` for all API calls (facade pattern)
- Import only the specific constants you need from `constants.*` modules
- Group constants from the same module in parentheses
- Avoid wildcard imports (`import *`)
- Avoid direct imports of internal modules (`param`, `command`, `config`, `logging`)

**Example:**

```python
from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_ALIASES,
    PARAM_DESCRIPTION,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_ACTION,
    COMMAND_REQUIRED_PARAMS,
)

params = [
    {
        PARAM_NAME: 'input-file',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--input', '-i'],
        PARAM_DESCRIPTION: 'Input file path'
    }
]

spafw37.add_params(params)
spafw37.run_cli()
```

**Avoid:**

```python
# Don't use wildcard imports
from spafw37.constants.param import *

# Don't bypass the facade
from spafw37 import param, command, config, logging
```

## Core Module (spafw37.core)

The `core` module is the primary facade for all framework functionality.

### Application Control

#### `run_cli()`

Run the command-line interface for the application.

**⚠️ IMPORTANT:** Call this function **last**, after all application setup is complete (parameters, commands, cycles, phases, etc.).

```python
from spafw37 import core as spafw37

if __name__ == '__main__':
    # Set up application
    spafw37.set_app_name('my-app')
    spafw37.add_params(params)
    spafw37.add_commands(commands)
    
    # Run CLI - CALL THIS LAST
    spafw37.run_cli()
```

**Behavior:**
- Parses command-line arguments from `sys.argv[1:]`
- Applies pre-parse actions (loads persistent config, pre-parses logging params)
- Sets parameter defaults
- Parses main command-line arguments
- Executes queued commands
- Applies post-parse actions (saves persistent config)
- Handles errors and displays help when appropriate

**Exceptions:**
- `CommandParameterError` - When required command parameters are missing
- `ValueError` - For general validation errors

### Application Configuration

#### `set_app_name(name)`

Set the application name.

```python
spafw37.set_app_name('file-processor')
```

**Args:**
- `name` (str) - Application name

**Used for:**
- Default logging scope
- Help display
- Log file naming
- Error messages

#### `get_app_name()`

Get the application name.

```python
app_name = spafw37.get_app_name()
```

**Returns:**
- `str` - Application name (default: `'spafw37'`)

#### `set_config_file(file_path)`

Set the path to the persistent configuration file.

```python
spafw37.set_config_file('~/.config/my-app/settings.json')
```

**Args:**
- `file_path` (str) - Path to configuration file

**Default:** `config.json` in current directory

**Note:** Parameters with `PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS` are automatically saved to this file.

### Parameter Management

#### `add_params(params)`

Add multiple parameter definitions.

```python
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_NUMBER,
    PARAM_ALIASES,
    PARAM_DESCRIPTION,
)

params = [
    {
        PARAM_NAME: 'input-file',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_ALIASES: ['--input', '-i'],
        PARAM_DESCRIPTION: 'Input file path'
    },
    {
        PARAM_NAME: 'max-retries',
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_ALIASES: ['--max-retries', '-r'],
        PARAM_DESCRIPTION: 'Maximum retry attempts'
    }
]

spafw37.add_params(params)
```

**Args:**
- `params` (list[dict]) - List of parameter definition dictionaries

**Important:** Do NOT duplicate framework parameters like `--verbose`, `--silent`, `--help`, `--log-level`, etc. The framework already provides these. See [Parameters Guide - Best Practices](parameters.md#best-practices-and-anti-patterns) for details.

**See:** [Parameters Guide](parameters.md) for complete parameter definition reference.

#### `add_param(param)`

Add a single parameter definition.

```python
spafw37.add_param({
    PARAM_NAME: 'output-dir',
    PARAM_TYPE: PARAM_TYPE_TEXT,
    PARAM_ALIASES: ['--output', '-o']
})
```

**Args:**
- `param` (dict) - Parameter definition dictionary

### Command Management

#### `add_commands(commands)`

Add multiple command definitions.

```python
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_ACTION,
    COMMAND_REQUIRED_PARAMS,
    COMMAND_DESCRIPTION,
    COMMAND_GOES_AFTER,
)

commands = [
    {
        COMMAND_NAME: 'process',
        COMMAND_ACTION: process_files,
        COMMAND_REQUIRED_PARAMS: ['input-file'],
        COMMAND_DESCRIPTION: 'Process input files'
    },
    {
        COMMAND_NAME: 'validate',
        COMMAND_ACTION: validate_files,
        COMMAND_GOES_AFTER: ['process']
    }
]

spafw37.add_commands(commands)
```

**Args:**
- `commands` (list[dict]) - List of command definition dictionaries

**See:** [Commands Guide](commands.md) for complete command definition reference.

#### `add_command(command)`

Add a single command definition.

```python
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_ACTION,
    COMMAND_PHASE,
)
from spafw37.constants.phase import PHASE_TEARDOWN

spafw37.add_command({
    COMMAND_NAME: 'cleanup',
    COMMAND_ACTION: cleanup_temp_files,
    COMMAND_PHASE: PHASE_TEARDOWN
})
```

**Args:**
- `command` (dict) - Command definition dictionary

#### `set_phases_order(phase_order)`

Set the execution order for phases.

```python
from spafw37.constants.phase import (
    PHASE_SETUP,
    PHASE_EXECUTION,
    PHASE_TEARDOWN,
)

# Custom phase order
spafw37.set_phases_order([
    PHASE_SETUP,
    PHASE_EXECUTION,
    PHASE_TEARDOWN
])
```

**Args:**
- `phase_order` (list[str]) - List of phase names in execution order

**Default:** `[PHASE_SETUP, PHASE_CLEANUP, PHASE_EXECUTION, PHASE_TEARDOWN, PHASE_END]`

**Note:** The framework sets a 5-phase default automatically via `configure.py`.

### Runtime Configuration

#### `get_config_value(config_key)`

Get a configuration value.

```python
input_file = spafw37.get_config_value('input-file')
verbose = spafw37.get_config_value('verbose')
```

**Args:**
- `config_key` (str) - Configuration key (typically the `PARAM_CONFIG_NAME` or `PARAM_NAME`)

**Returns:**
- Configuration value, or `None` if not set

**Common usage:**
- Accessing parameter values in command actions
- Reading cycle state in CYCLE_LOOP functions
- Getting user preferences

#### Typed Configuration Getters

For better type safety and linter support, use typed getters that cast values to specific types:

#### `get_config_int(config_key, default=0)`

Get a configuration value as integer.

```python
max_workers = spafw37.get_config_int('max-workers', 4)
file_index = spafw37.get_config_int('file-index')
```

**Args:**
- `config_key` (str) - Configuration key
- `default` (int) - Default value if not found (default: 0)

**Returns:**
- Integer value or default

#### `get_config_str(config_key, default='')`

Get a configuration value as string.

```python
project_dir = spafw37.get_config_str('project-dir', './project')
author = spafw37.get_config_str('author')
```

**Args:**
- `config_key` (str) - Configuration key
- `default` (str) - Default value if not found (default: '')

**Returns:**
- String value or default

#### `get_config_bool(config_key, default=False)`

Get a configuration value as boolean.

```python
verbose = spafw37.get_config_bool('verbose')
is_enabled = spafw37.get_config_bool('feature-enabled', True)
```

**Args:**
- `config_key` (str) - Configuration key
- `default` (bool) - Default value if not found (default: False)

**Returns:**
- Boolean value or default

#### `get_config_float(config_key, default=0.0)`

Get a configuration value as float.

```python
timeout = spafw37.get_config_float('timeout', 30.0)
threshold = spafw37.get_config_float('threshold')
```

**Args:**
- `config_key` (str) - Configuration key
- `default` (float) - Default value if not found (default: 0.0)

**Returns:**
- Float value or default

#### `get_config_list(config_key, default=None)`

Get a configuration value as list.

```python
tags = spafw37.get_config_list('tags')
files = spafw37.get_config_list('files', [])
```

**Args:**
- `config_key` (str) - Configuration key
- `default` (list) - Default value if not found (default: empty list)

**Returns:**
- List value or default. Single values are automatically wrapped in a list.

#### `set_config_value(config_key, value)`

Set a configuration value.

```python
spafw37.set_config_value('file-index', 0)
spafw37.set_config_value('processing-complete', True)
```

**Args:**
- `config_key` (str) - Configuration key
- `value` - Value to set (any JSON-serializable type)

**Common usage:**
- Initialising cycle state in CYCLE_INIT
- Updating state during command execution
- Setting runtime parameters

**Note:** Use runtime-only parameters (`PARAM_RUNTIME_ONLY: True`) for temporary state that shouldn't be persisted.

#### `is_verbose()`

Check if verbose mode is enabled.

```python
if spafw37.is_verbose():
    spafw37.output(f"Detailed processing info: {details}")
```

**Returns:**
- `bool` - `True` if `--verbose` flag is set, `False` otherwise

**Common usage:**
- Conditional output for detailed information
- Adjusting command behavior based on verbosity level
- Combining with `output()` for verbose-only messages

#### `is_silent()`

Check if silent mode is enabled.

```python
if not spafw37.is_silent():
    spafw37.output("Processing complete")
```

**Returns:**
- `bool` - `True` if `--silent` flag is set, `False` otherwise

**Common usage:**
- Conditional output suppression
- Adjusting command behavior for silent operation
- Checking before expensive output formatting

**Note:** The `output()` function already respects silent mode, so explicit checks are often unnecessary.

#### `get_max_cycle_nesting_depth()`

Get the maximum allowed nesting depth for cycles.

```python
current_max = spafw37.get_max_cycle_nesting_depth()
print(f"Maximum cycle nesting depth: {current_max}")
```

**Returns:**
- `int` - Maximum nesting depth (default: 5)

**Common usage:**
- Checking current configuration before defining deeply nested cycles
- Diagnostic output for debugging cycle structures

#### `set_max_cycle_nesting_depth(depth)`

Set the maximum allowed nesting depth for cycles.

```python
# Allow deeper nesting for complex cycle structures
spafw37.set_max_cycle_nesting_depth(10)
```

**Args:**
- `depth` (int) - Maximum nesting depth (must be positive integer)

**Raises:**
- `ValueError` - If depth is not a positive integer

**Common usage:**
- Configuring framework before defining deeply nested cycles
- Adjusting limits based on application requirements

**Note:** The default value of 5 is sufficient for most use cases. Increase this value only if you need deeply nested cycle structures. This setting helps prevent infinite recursion from misconfigured cycles.

### Output Functions

The output functions provide framework-managed application output that respects silent/verbose modes.

#### `output(message="", verbose=False, output_handler=None)`

Output a message to the user, respecting silent/verbose modes.

```python
# Normal output
spafw37.output("Processing complete!")
spafw37.output(f"Processed {count} items")

# Verbose-only output (requires --verbose flag)
spafw37.output(f"Debug details: {info}", verbose=True)

# Empty line
spafw37.output()

# Custom handler for this specific call
spafw37.output("Special message", output_handler=my_custom_handler)
```

**Args:**
- `message` (str) - Message to output (default: empty string for blank line)
- `verbose` (bool) - If `True`, only outputs when `--verbose` is set (default: `False`)
- `output_handler` (callable) - Optional custom handler for this specific call. If `None`, uses the global handler set by `set_output_handler()` (default: `None`)

**Behavior:**
- **Normal mode:** Outputs message to console
- **Silent mode (`--silent`):** Suppresses all output
- **Verbose-only (`verbose=True`):** Only outputs when `--verbose` is set

**Use `output()` instead of `print()` for:**
- Application results and status messages
- Progress indicators
- User-facing output
- Any output that should respect `--silent` flag

**Continue using `print()` for:**
- Error messages in exception handlers
- Output that must always display regardless of flags

**Per-call handler usage:**
```python
# Route specific messages to different destinations
spafw37.output("Normal message")  # Uses global handler
spafw37.output("Error details", output_handler=error_logger)  # Specific handler
spafw37.output("Audit entry", output_handler=audit_writer)  # Different handler
```

#### `set_output_handler(handler)`

Set a custom output handler function.

```python
def my_handler(message):
    with open('output.txt', 'a') as f:
        f.write(message + '\n')

spafw37.set_output_handler(my_handler)
```

**Args:**
- `handler` (callable) - Function that takes a message string

**Default handler:** Uses built-in `print()` function

**Common usage:**
- Testing: Capture output for assertions
- File redirection: Write output to file instead of console
- GUI applications: Route output to UI components
- Logging: Send output through logging system
- Custom formatting: Add timestamps, colours, etc.

**Example - Dual output (console + file):**

```python
def dual_handler(message):
    print(message)  # Console
    with open('app.log', 'a') as f:
        f.write(f"{message}\n")  # File

spafw37.set_output_handler(dual_handler)
```

**Example - Reset to default:**

```python
spafw37.set_output_handler()  # Resets to built-in print()
```

**Note:** The handler is called for all `output()` calls, but only after silent/verbose checks pass.

### Logging Functions

All logging functions support optional scope and message parameters.

#### `set_log_dir(log_dir)`

Set the directory for log files.

```python
spafw37.set_log_dir('/var/log/my-app')
```

**Args:**
- `log_dir` (str) - Path to log directory

**Default:** `logs/` in current directory

**Note:** Log directory is persistent (saved to `config.json`).

#### `set_current_scope(scope)`

Set the current logging scope for subsequent log messages.

```python
spafw37.set_current_scope('initialisation')
spafw37.log_info(_message="Starting initialisation")
```

**Args:**
- `scope` (str) - Scope name

**Default scope:** Application name (from `get_app_name()`)

#### `log_trace(_scope=None, _message='')`

Log a message at TRACE level (5).

```python
spafw37.log_trace(_message="Detailed execution trace")
spafw37.log_trace(_scope='parser', _message="Token details")
```

**Args:**
- `_scope` (str, optional) - Scope for this message (defaults to current scope)
- `_message` (str) - Message to log

**Default output:** File only (requires `--trace` to see on console)

#### `log_debug(_scope=None, _message='')`

Log a message at DEBUG level (10).

```python
spafw37.log_debug(_message=f"Processing batch {batch_id}")
```

**Args:**
- `_scope` (str, optional) - Scope for this message
- `_message` (str) - Message to log

**Default output:** File only (requires `--verbose` to see on console)

#### `log_info(_scope=None, _message='')`

Log a message at INFO level (20).

```python
spafw37.log_info(_message="Processing complete")
```

**Args:**
- `_scope` (str, optional) - Scope for this message
- `_message` (str) - Message to log

**Default output:** File and console

#### `log_warning(_scope=None, _message='')`

Log a message at WARNING level (30).

```python
spafw37.log_warning(_message="Timeout occurred, retrying")
```

**Args:**
- `_scope` (str, optional) - Scope for this message
- `_message` (str) - Message to log

**Default output:** File and console

#### `log_error(_scope=None, _message='')`

Log a message at ERROR level (40).

```python
spafw37.log_error(_message=f"Failed to process file: {error}")
```

**Args:**
- `_scope` (str, optional) - Scope for this message
- `_message` (str) - Message to log

**Default output:** File, console, and stderr

## Constants Modules

Constants modules provide dictionary keys for defining parameters, commands, cycles, and phases.

### Parameter Constants (spafw37.constants.param)

#### Basic Properties

| Constant | Type | Description |
|----------|------|-------------|
| `PARAM_NAME` | str | Parameter name (required) |
| `PARAM_DESCRIPTION` | str | Long description for help |
| `PARAM_TYPE` | str | Data type (required, see types below) |
| `PARAM_ALIASES` | list[str] | CLI aliases (e.g., `['--input', '-i']`) |
| `PARAM_DEFAULT` | any | Default value |

#### Configuration Binding

| Constant | Type | Description |
|----------|------|-------------|
| `PARAM_CONFIG_NAME` | str | Internal config key (defaults to PARAM_NAME) |
| `PARAM_REQUIRED` | bool | Whether param must be set |
| `PARAM_RUNTIME_ONLY` | bool | Not persisted, only for runtime use |

#### Persistence Control

| Constant | Type | Description |
|----------|------|-------------|
| `PARAM_PERSISTENCE` | str | Persistence behavior (see options below) |
| `PARAM_PERSISTENCE_ALWAYS` | str | Value: `'always'` - save to main config |
| `PARAM_PERSISTENCE_NEVER` | str | Value: `'never'` - never save |
| `PARAM_PERSISTENCE_USER_ONLY` | None | Value: `None` - user configs only (default) |

#### Organisation

| Constant | Type | Description |
|----------|------|-------------|
| `PARAM_SWITCH_LIST` | list[str] | Mutually exclusive params |
| `PARAM_GROUP` | str | Group name for help display |

#### Parameter Types

| Constant | Value | Description |
|----------|-------|-------------|
| `PARAM_TYPE_TEXT` | `'text'` | Text string |
| `PARAM_TYPE_NUMBER` | `'number'` | Numeric value |
| `PARAM_TYPE_TOGGLE` | `'toggle'` | Boolean flag |
| `PARAM_TYPE_LIST` | `'list'` | List of values |

#### Internal Use

| Constant | Type | Description |
|----------|------|-------------|
| `PARAM_HAS_VALUE` | bool | For pre-parse params: True if takes value |

### Command Constants (spafw37.constants.command)

#### Basic Properties

| Constant | Type | Description |
|----------|------|-------------|
| `COMMAND_NAME` | str | Command name (required) |
| `COMMAND_DESCRIPTION` | str | Description for help |
| `COMMAND_ACTION` | callable | Function to execute |
| `COMMAND_REQUIRED_PARAMS` | list[str] | Required parameter names |

#### Sequencing and Dependencies

| Constant | Type | Description |
|----------|------|-------------|
| `COMMAND_GOES_BEFORE` | list[str] | Commands this must run before |
| `COMMAND_GOES_AFTER` | list[str] | Commands this must run after |
| `COMMAND_REQUIRE_BEFORE` | list[str] | Automatically enqueue these before |
| `COMMAND_NEXT_COMMANDS` | list[str] | Automatically enqueue these after |

#### Phase Control

| Constant | Type | Description |
|----------|------|-------------|
| `COMMAND_PHASE` | str | Phase this command belongs to |

#### Advanced Features

| Constant | Type | Description |
|----------|------|-------------|
| `COMMAND_CYCLE` | dict | Cycle definition (see Cycle Constants) |
| `COMMAND_TRIGGER_PARAM` | str | Parameter that triggers this command |
| `COMMAND_FRAMEWORK` | bool | Marks framework-internal commands |
| `COMMAND_EXCLUDE_HELP` | bool | Exclude from help display |
| `COMMAND_HELP` | str | Custom help text |

### Cycle Constants (spafw37.constants.cycle)

| Constant | Value | Description |
|----------|-------|-------------|
| `CYCLE_INIT` | `'cycle-init-function'` | Initialisation function (runs once before loop) |
| `CYCLE_LOOP` | `'cycle-loop-function'` | Loop condition function (returns True/False) |
| `CYCLE_LOOP_START` | `'cycle-loop-start-function'` | Iteration prep function (runs after loop returns True) |
| `CYCLE_END` | `'cycle-end-function'` | Finalisation function (runs once after loop) |
| `CYCLE_COMMANDS` | `'cycle-commands'` | List of command definitions for each iteration |

**Execution order:**
```
CYCLE_INIT
while CYCLE_LOOP returns True:
    CYCLE_LOOP_START
    execute CYCLE_COMMANDS
CYCLE_END
```

### Phase Constants (spafw37.constants.phase)

| Constant | Value | Description |
|----------|-------|-------------|
| `PHASE_SETUP` | `'phase-setup'` | Setup operations |
| `PHASE_CLEANUP` | `'phase-cleanup'` | Pre-execution cleanup |
| `PHASE_EXECUTION` | `'phase-execution'` | Main execution (default) |
| `PHASE_TEARDOWN` | `'phase-teardown'` | Post-execution teardown |
| `PHASE_END` | `'phase-end'` | Final cleanup |

**Default order:**
```python
PHASE_ORDER = [
    PHASE_SETUP,
    PHASE_CLEANUP,
    PHASE_EXECUTION,
    PHASE_TEARDOWN,
    PHASE_END
]
```

### Logging Constants (spafw37.constants.logging)

The logging system is automatically configured via CLI parameters. See the [Logging Guide](logging.md) for details on using `--verbose`, `--trace`, `--silent`, and other logging options.

### Configuration Constants (spafw37.constants.config)

User configuration files can be loaded and saved via CLI parameters:
- Load: `--load-config <file>`, `-l <file>`
- Save: `--save-config <file>`, `-s <file>`

See the [Configuration Guide](configuration.md) for details on configuration file management.

---

## Examples

For complete working examples demonstrating these API functions and constants, see the **[examples directory](https://github.com/minouris/spafw37/tree/main/examples)**:

- **Parameters** (6 files): Basic usage, toggles, lists, required validation, runtime modification, grouping
- **Commands** (7 files): Basic definition, sequencing, dependencies, chaining, required validation, triggering, visibility
- **Cycles** (3 files): Basic usage, custom loop initialisation, nested patterns
- **Phases** (4 files): Basic usage, custom ordering, extended lifecycle, custom definitions
- **Output** (2 files): Basic output with verbose/silent modes, custom handlers (file, dual, timestamped)
- **Configuration** (2 files): Basic usage, persistence patterns

Each example demonstrates specific API functions and constants in working code that you can run and modify.

---

## Documentation

- **[User Guide](README.md)** - Overview and quick start
- **[Parameters Guide](parameters.md)** - Parameter definition and usage
- **[Commands Guide](commands.md)** - Command system and dependencies
- **[Phases Guide](phases.md)** - Multi-phase execution control
- **[Cycles Guide](cycles.md)** - Repeating command sequences
- **[Configuration Guide](configuration.md)** - Configuration management
- **[Logging Guide](logging.md)** - Built-in logging system
- **API Reference** - Complete API documentation

---

[← Logging Guide](logging.md) | [Index](README.md#documentation)
