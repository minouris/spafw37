# API Reference

[← Logging Guide](logging.md) | [Index](README.md#documentation)

## Table of Contents

- [Overview](#overview)
- [Version Changes](#version-changes)
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
- [Advanced: Internal Module Functions](#advanced-internal-module-functions)
  - [Parameter Module (spafw37.param)](#parameter-module-spafw37param)
  - [Command Module (spafw37.command)](#command-module-spafw37command)
  - [CLI Module (spafw37.cli)](#cli-module-spafw37cli)

## Overview

The spafw37 framework uses a **facade pattern** where `spafw37.core` provides the primary public API. Application developers should primarily interact with:

1. **`spafw37.core`** - Main API facade
2. **`spafw37.constants.*`** - Constant definitions for dictionaries

This design keeps the API surface clean and shields applications from internal implementation details.

## Version Changes

### v1.1.0

**Parameter API Simplification:**
- Added unified `get_param()` function with automatic type routing based on `PARAM_TYPE`
- Added `set_param()` for setting parameter values with type validation
- Added `unset_param()` for removing parameter values completely
- Added `reset_param()` for restoring default values or unsetting if no default
- Added `join_param()` for accumulating values (strings, lists, dicts) with type-specific logic
- Deprecated legacy configuration API (`get_config_value()`, `get_config_str()`, etc.)

**Parameter Validation:**
- Added `PARAM_ALLOWED_VALUES` for restricting TEXT, NUMBER, and LIST parameters to predefined value sets
- TEXT and LIST parameters use case-insensitive matching with automatic normalisation to canonical case
- Provides clear error messages when invalid values are provided

**Parameter Protection:**
- Added `PARAM_IMMUTABLE` for write-once, read-many semantics
- Immutable parameters cannot be modified, unset, or reset once they have a value

**Join and Merge Configuration:**
- Added `PARAM_JOIN_SEPARATOR` for configurable string concatenation
- Added `PARAM_DICT_MERGE_TYPE` for shallow/deep dictionary merging
- Added `PARAM_DICT_OVERRIDE_STRATEGY` for conflict resolution

**Advanced Parameter Features:**
- Added `PARAM_INPUT_FILTER` for custom input transformation functions
- Dict parameters support multiple JSON blocks (automatically merged)
- Dict parameters support file references within JSON (e.g., `{'data': @file.json}`)

**Interactive Prompts:**
- Added `PARAM_PROMPT` for interactive user input when parameters are unset
- Added `PARAM_PROMPT_ON` for controlling prompt timing (ON_START, ON_COMMAND, NEVER)
- Added `PARAM_PROMPT_REPEAT` for repeated prompts during cycles
- Added `PARAM_PROMPT_SENSITIVE` for hiding sensitive input (passwords, tokens)
- Added `set_prompt_handler()` for custom prompt implementations
- Added `set_max_prompt_retries()` for configurable retry limits
- Added `set_output_handler()` for custom message output

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

### Quick Reference

| Function | Added | Description |
|----------|-------|-------------|
| **Application Control** | | |
| [`run_cli()`](#run_cli) | v1.0.0 | Run the command-line interface (call this last) |
| **Application Configuration** | | |
| [`set_app_name(name)`](#set_app_namename) | v1.0.0 | Set the application name |
| [`get_app_name()`](#get_app_name) | v1.0.0 | Get the application name |
| [`set_config_file(file_path)`](#set_config_filefile_path) | v1.0.0 | Set the path to the persistent configuration file |
| **Parameter Management** | | |
| [`add_params(params)`](#add_paramsparams) | v1.0.0 | Add multiple parameter definitions |
| [`add_param(param)`](#add_paramparam) | v1.0.0 | Add a single parameter definition |
| **Command Management** | | |
| [`add_commands(commands)`](#add_commandscommands) | v1.0.0 | Add multiple command definitions |
| [`add_command(command)`](#add_commandcommand) | v1.0.0 | Add a single command definition |
| [`set_phases_order(phase_order)`](#set_phases_orderphase_order) | v1.0.0 | Set the execution order for phases |
| **Runtime Configuration** | | |
| [`get_param(...)`](#get_paramparam_namenone-bind_namenone-aliasnone-defaultnone-strictfalse) | v1.1.0 | Get parameter value with automatic type conversion |
| [`set_param(...)`](#set_paramparam_namенone-bind_namenone-aliasnone-valuenone) | v1.1.0 | Set parameter value with type validation |
| [`join_param(...)`](#join_paramparam_namenone-bind_namenone-aliasnone-valuenone) | v1.1.0 | Accumulate parameter value using type-specific logic |
| [`unset_param(...)`](#unset_paramparam_namenone-bind_namenone-aliasnone) | v1.1.0 | Remove parameter value completely |
| [`reset_param(...)`](#reset_paramparam_namenone-bind_namenone-aliasnone) | v1.1.0 | Reset parameter to default value or unset if no default |
| [`is_verbose()`](#is_verbose) | v1.0.0 | Check if verbose mode is enabled |
| [`is_silent()`](#is_silent) | v1.0.0 | Check if silent mode is enabled |
| [`get_max_cycle_nesting_depth()`](#get_max_cycle_nesting_depth) | v1.0.0 | Get maximum allowed cycle nesting depth |
| [`set_max_cycle_nesting_depth(depth)`](#set_max_cycle_nesting_depthdepth) | v1.0.0 | Set maximum allowed cycle nesting depth |
| **Output Functions** | | |
| [`output(message, verbose, output_handler)`](#outputmessage-verbosefalse-output_handlernone) | v1.0.0 | Output message respecting silent/verbose modes |
| [`set_output_handler(handler)`](#set_output_handlerhandler) | v1.0.0 | Set custom output handler function |
| **Logging Functions** | | |
| [`set_log_dir(log_dir)`](#set_log_dirlog_dir) | v1.0.0 | Set the directory for log files |
| [`set_current_scope(scope)`](#set_current_scopescope) | v1.0.0 | Set the current logging scope |
| [`log_trace(_scope, _message)`](#log_trace_scopenone-_message) | v1.0.0 | Log message at TRACE level (5) |
| [`log_debug(_scope, _message)`](#log_debug_scopenone-_message) | v1.0.0 | Log message at DEBUG level (10) |
| [`log_info(_scope, _message)`](#log_info_scopenone-_message) | v1.0.0 | Log message at INFO level (20) |
| [`log_warning(_scope, _message)`](#log_warning_scopenone-_message) | v1.0.0 | Log message at WARNING level (30) |
| [`log_error(_scope, _message)`](#log_error_scopenone-_message) | v1.0.0 | Log message at ERROR level (40) |
| **Deprecated Functions** | | |
| [`get_config_value(config_key)`](#get_config_valueconfig_key-deprecated) | v1.0.0 | ⚠️ **Deprecated** - Use `get_param()` instead |
| [`get_config_int(config_key, default)`](#get_config_intconfig_key-default0-deprecated) | v1.0.0 | ⚠️ **Deprecated** - Use `get_param()` instead |
| [`get_config_str(config_key, default)`](#get_config_strconfig_key-default-deprecated) | v1.0.0 | ⚠️ **Deprecated** - Use `get_param()` instead |
| [`get_config_bool(config_key, default)`](#get_config_boolconfig_key-defaultfalse-deprecated) | v1.0.0 | ⚠️ **Deprecated** - Use `get_param()` instead |
| [`get_config_float(config_key, default)`](#get_config_floatconfig_key-default00-deprecated) | v1.0.0 | ⚠️ **Deprecated** - Use `get_param()` instead |
| [`get_config_list(config_key, default)`](#get_config_listconfig_key-defaultnone-deprecated) | v1.0.0 | ⚠️ **Deprecated** - Use `get_param()` instead |
| [`get_config_dict(config_key, default)`](#get_config_dictconfig_key-defaultnone-deprecated) | v1.0.0 | ⚠️ **Deprecated** - Use `get_param()` instead |
| [`set_config_value(config_key, value)`](#set_config_valueconfig_key-value-deprecated) | v1.0.0 | ⚠️ **Deprecated** - Use `set_param()` or `join_param()` instead |

---

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

The framework provides two APIs for accessing configuration values:

1. **Parameter API (v1.1.0, Recommended)** - Parameter-focused with typed getters, flexible resolution, and type-specific operations
2. **Configuration API (Deprecated)** - Legacy config-focused API, still supported for backward compatibility

#### Parameter API (v1.1.0)

The parameter API provides simple access to parameter values with automatic type handling. Use `get_param()` to retrieve values, `set_param()` to replace them, `unset_param()` to remove them, `reset_param()` to restore defaults, and `join_param()` to accumulate them.

##### `get_param(param_name=None, bind_name=None, alias=None, default=None, strict=False)`

Get a parameter value with automatic type conversion based on the parameter's `PARAM_TYPE`. This intelligent method examines the parameter definition and returns the correctly-typed value without requiring separate getter functions for each type ([see example](../examples/params_basic.py)).

```python
# Automatically returns the correct type based on parameter definition
input_file = spafw37.get_param('input-file')  # Returns string for PARAM_TYPE_TEXT
max_workers = spafw37.get_param('max-workers', 4)  # Returns int for PARAM_TYPE_NUMBER
debug_mode = spafw37.get_param('debug-mode')  # Returns bool for PARAM_TYPE_TOGGLE
tags = spafw37.get_param('tags')  # Returns list for PARAM_TYPE_LIST
settings = spafw37.get_param('settings')  # Returns dict for PARAM_TYPE_DICT

# With default values
project_dir = spafw37.get_param('project-dir', './project')
thread_count = spafw37.get_param('threads', 1)

# Advanced: Reference by config binding name
alt_input = spafw37.get_param(bind_name='input-path')

# Advanced: Reference by alias (without -- prefix)
author = spafw37.get_param(alias='author')  # From '--author' alias

# Strict mode raises error if parameter not found
required_value = spafw37.get_param('required-param', strict=True)
```

**Type Routing:**
The method automatically routes to the appropriate typed getter based on `PARAM_TYPE`:
- `PARAM_TYPE_TEXT` → Returns string (default: '')
- `PARAM_TYPE_NUMBER` → Returns int (default: 0)
- `PARAM_TYPE_TOGGLE` → Returns bool (default: False)
- `PARAM_TYPE_LIST` → Returns list (default: [])
- `PARAM_TYPE_DICT` → Returns dict (default: {})

**Args:**
- `param_name` (str, optional) - Parameter's PARAM_NAME
- `bind_name` (str, optional) - Parameter's PARAM_CONFIG_NAME
- `alias` (str, optional) - Any of the parameter's PARAM_ALIASES (without `--` prefix)
- `default` - Default value if not found (type should match parameter's PARAM_TYPE)
- `strict` (bool) - If True, raises ValueError when parameter not found (default: False)

**Returns:**
- Value with correct type based on PARAM_TYPE, or default if not found

**Raises:**
- `ValueError` - If strict=True and parameter definition or value not found

**Note:** Provide exactly one of `param_name`, `bind_name`, or `alias`.

##### `set_param(param_name=None, bind_name=None, alias=None, value=None)`

Set a parameter value, replacing any existing value. Validates that the value type matches the parameter's PARAM_TYPE ([see example](../examples/params_runtime.py)).

```python
# Set by parameter name
spafw37.set_param(param_name='mode', value='default')
spafw37.set_param(param_name='file-index', value=0)

# Set by config binding name
spafw37.set_param(bind_name='output-dir', value='./output')
spafw37.set_param(bind_name='processing-complete', value=True)

# Set by alias
spafw37.set_param(alias='files', value=['file1.txt', 'file2.txt'])
```

**Args:**
- `param_name` (str, optional) - Parameter's PARAM_NAME
- `bind_name` (str, optional) - Parameter's PARAM_CONFIG_NAME
- `alias` (str, optional) - Any of the parameter's PARAM_ALIASES (without `--` prefix)
- `value` - Value to set (must match parameter's PARAM_TYPE)

**Note:** Provide exactly one of `param_name`, `bind_name`, or `alias`.

**Raises:**
- `ValueError` - If value type doesn't match parameter's PARAM_TYPE

**Common usage:**
- Initializing cycle state
- Replacing parameter values during execution
- Resetting parameters to specific values

##### `join_param(param_name=None, bind_name=None, alias=None, value=None)`

Accumulate a parameter value using type-specific logic instead of replacing it ([see example](../examples/params_join.py)). Behavior depends on parameter type:

- **String (PARAM_TYPE_TEXT):** Concatenate with separator (configurable via `PARAM_JOIN_SEPARATOR`)
- **List (PARAM_TYPE_LIST):** Append single values or extend with lists
- **Dict (PARAM_TYPE_DICT):** Merge dictionaries (shallow or deep, configurable via `PARAM_DICT_MERGE_TYPE`)

```python
# String concatenation with default space separator
spafw37.join_param(param_name='message', value='First')
spafw37.join_param(param_name='message', value='Second')
# Result: 'First Second'

# List accumulation
spafw37.join_param(param_name='files', value='file1.txt')
spafw37.join_param(param_name='files', value='file2.txt')
spafw37.join_param(param_name='files', value=['file3.txt', 'file4.txt'])
# Result: ['file1.txt', 'file2.txt', 'file3.txt', 'file4.txt']

# Dictionary merging
spafw37.join_param(param_name='config', value={'db': 'postgres', 'port': 5432})
spafw37.join_param(param_name='config', value={'db': 'mysql'})
# Result: {'db': 'mysql', 'port': 5432}
```

**Args:**
- `param_name` (str, optional) - Parameter's PARAM_NAME
- `bind_name` (str, optional) - Parameter's PARAM_CONFIG_NAME
- `alias` (str, optional) - Any of the parameter's PARAM_ALIASES (without `--` prefix)
- `value` - Value to accumulate (must match parameter's PARAM_TYPE)

**Note:** Provide exactly one of `param_name`, `bind_name`, or `alias`.

**Raises:**
- `ValueError` - If value type doesn't match parameter's PARAM_TYPE
- `ValueError` - If PARAM_DICT_OVERRIDE_STRATEGY is 'error' and key conflict occurs

**Common usage:**
- Building up lists incrementally
- Accumulating error messages or log entries
- Merging configuration dictionaries
- Concatenating multi-part strings

**See:** [Parameters Guide - Accumulating Parameter Values](parameters.md#accumulating-parameter-values) for detailed type-specific behavior and configuration options.

##### `unset_param(param_name=None, bind_name=None, alias=None)`

Remove a parameter value completely from the configuration ([see example](../examples/params_unset.py)). After unsetting, the parameter behaves as if it was never set.

```python
# Remove temporary processing state
spafw37.unset_param(param_name='temp-data')
spafw37.unset_param(param_name='current-file')
spafw37.unset_param(param_name='progress')

# After unset, parameter has no value
value = spafw37.get_param('temp-data', default='<not set>')  # Returns '<not set>'
```

**Args:**
- `param_name` (str, optional) - Parameter's PARAM_NAME
- `bind_name` (str, optional) - Parameter's PARAM_CONFIG_NAME
- `alias` (str, optional) - Any of the parameter's PARAM_ALIASES (without `--` prefix)

**Note:** Provide exactly one of `param_name`, `bind_name`, or `alias`.

**Raises:**
- `ValueError` - If parameter is immutable (`PARAM_IMMUTABLE: True`) and has a value

**Common usage:**
- Cleaning up temporary runtime state
- Removing processing artifacts
- Clearing session-specific data
- Resetting state between processing cycles

##### `reset_param(param_name=None, bind_name=None, alias=None)`

Reset a parameter to its default value, or unset it if no default exists ([see example](../examples/params_unset.py)).

```python
# Reset parameter with default value - restores the default
spafw37.reset_param(param_name='counter')  # If PARAM_DEFAULT is 0, sets to 0

# Reset parameter without default value - unsets the parameter
spafw37.reset_param(param_name='runtime-state')  # If no PARAM_DEFAULT, removes value
```

**Args:**
- `param_name` (str, optional) - Parameter's PARAM_NAME
- `bind_name` (str, optional) - Parameter's PARAM_CONFIG_NAME
- `alias` (str, optional) - Any of the parameter's PARAM_ALIASES (without `--` prefix)

**Behavior:**
- **With PARAM_DEFAULT:** Sets parameter to its default value (calls `set_param()`)
- **Without PARAM_DEFAULT:** Removes parameter value (calls `unset_param()`)

**Note:** Provide exactly one of `param_name`, `bind_name`, or `alias`.

**Raises:**
- `ValueError` - If parameter is immutable (`PARAM_IMMUTABLE: True`) and has a value

**Common usage:**
- Restoring parameters to initial state
- Implementing reset/clear functionality
- Reverting user changes to defaults
- Cleaning up between test runs

**See:** [Parameters Guide - Unsetting and Resetting Parameter Values](parameters.md#unsetting-and-resetting-parameter-values) for when to use unset vs reset.

##### `set_prompt_handler(handler_function)`

**Added in v1.1.0**

Set a custom prompt handler function for interactive parameter prompts ([see example](../examples/params_prompt_handlers.py)).

```python
def my_prompt_handler(param_config):
    """Custom handler with validation and formatting."""
    prompt_text = param_config.get('PARAM_PROMPT', 'Enter value: ')
    while True:
        value = input(prompt_text)
        if value:
            return value
        print("Value cannot be empty. Please try again.")

# Register custom handler
spafw37.set_prompt_handler(my_prompt_handler)
```

**Args:**
- `handler_function` (callable) - Function that accepts `param_config` dict and returns user input string

**Handler Function Contract:**
- **Input:** `param_config` (dict) - Complete parameter configuration dictionary
- **Output:** User input value as string (will be processed by PARAM_INPUT_FILTER if configured)
- **Behavior:** Should handle prompting, validation, retries internally
- **Exceptions:** Should not raise exceptions for validation failures (handle internally or return empty string)

**Common usage:**
- Custom prompt formatting (colours, styles, rich UI)
- Built-in validation before returning value
- Integration with third-party input libraries (e.g., `prompt_toolkit`)
- Logging or auditing user inputs
- Different prompts for different environments (terminal types, CI/CD)

**Default handler:** Uses Python's built-in `input()` function with configurable retry logic

**See:** [Parameters Guide - Interactive Prompts](parameters.md#interactive-prompts) for complete prompt handler documentation.

##### `set_max_prompt_retries(max_retries)`

**Added in v1.1.0**

Set the maximum number of retry attempts for invalid inputs when using the default prompt handler ([see example](../examples/params_prompt_handlers.py)).

```python
# Allow 5 attempts for complex validations
spafw37.set_max_prompt_retries(5)

# Infinite retries (loop until valid input or Ctrl+C)
spafw37.set_max_prompt_retries(None)

# Fail immediately on first invalid input
spafw37.set_max_prompt_retries(0)
```

**Args:**
- `max_retries` (int or None) - Maximum retry attempts, or `None` for infinite retries

**Default:** `3` retry attempts

**Behavior:**
- Only affects the **default prompt handler** (not custom handlers)
- Counts invalid inputs returned by `PARAM_INPUT_FILTER`
- When limit reached, framework raises `ValueError` with all validation errors
- Custom handlers manage their own retry logic

**Common usage:**
- Strict validation requiring immediate failure (`max_retries=0`)
- Complex validations needing more attempts (`max_retries=5`)
- Development/debugging with infinite retries (`max_retries=None`)
- Production systems with controlled retry limits

**Note:** This setting is global and affects all parameters using the default prompt handler.

**See:** [Parameters Guide - Interactive Prompts](parameters.md#interactive-prompts) for retry behaviour details.

##### `set_output_handler(handler_function)`

**Added in v1.1.0**

Set a custom output handler function for displaying prompt messages and errors ([see example](../examples/params_prompt_handlers.py)).

```python
import logging

def logging_output_handler(message):
    """Send prompt output to logger instead of stdout."""
    logging.info(message)

# Register custom output handler
spafw37.set_output_handler(logging_output_handler)
```

**Args:**
- `handler_function` (callable) - Function that accepts a message string and handles output

**Handler Function Contract:**
- **Input:** `message` (str) - Formatted message text (prompt text, validation errors, retry messages)
- **Output:** None
- **Behavior:** Should handle message display (stdout, stderr, logging, UI, etc.)
- **Exceptions:** Should not raise exceptions (swallow errors or log internally)

**Common usage:**
- Redirecting output to logging system
- Suppressing output in automated environments
- Custom formatting or colouring
- Integration with UI frameworks
- Capturing output for testing

**Default handler:** Uses `print()` to write to stdout

**Messages sent to output handler:**
- Prompt text (from `PARAM_PROMPT`)
- Validation error messages (from `PARAM_INPUT_FILTER`)
- Retry attempt messages
- Final failure messages (after max retries exceeded)

**See:** [Parameters Guide - Interactive Prompts](parameters.md#interactive-prompts) for complete output handler documentation.

#### Configuration API (Deprecated)

**⚠️ Deprecated as of v1.1.0** - The following functions are maintained for backward compatibility but will show a one-time deprecation warning. Use the Parameter API functions instead.

##### `get_config_value(config_key)` (Deprecated)

**⚠️ Deprecated:** Use `get_param(bind_name=config_key)` instead.

Get a configuration value.

```python
# Deprecated
input_file = spafw37.get_config_value('input-file')
debug_mode = spafw37.get_config_value('debug-mode')

# Recommended replacement
input_file = spafw37.get_param('input-file')
debug_mode = spafw37.get_param('debug-mode')
```

**Args:**
- `config_key` (str) - Configuration key (typically the `PARAM_CONFIG_NAME` or `PARAM_NAME`)

**Returns:**
- Configuration value, or `None` if not set

**Common usage:**
- Accessing parameter values in command actions
- Reading cycle state in CYCLE_LOOP functions
- Getting user preferences

##### Typed Configuration Getters (Deprecated)

**⚠️ Deprecated:** Use the new parameter API `get_param()` function instead.

For better type safety and linter support, use typed getters that cast values to specific types:

##### `get_config_int(config_key, default=0)` (Deprecated)

**⚠️ Deprecated:** Use `get_param(bind_name=config_key, default=default)` instead.

Get a configuration value as integer.

```python
# Deprecated
max_workers = spafw37.get_config_int('max-workers', 4)
file_index = spafw37.get_config_int('file-index')

# Recommended replacement
max_workers = spafw37.get_param(bind_name='max-workers', default=4)
file_index = spafw37.get_param(bind_name='file-index')
```

**Args:**
- `config_key` (str) - Configuration key
- `default` (int) - Default value if not found (default: 0)

**Returns:**
- Integer value or default

##### `get_config_str(config_key, default='')` (Deprecated)

**⚠️ Deprecated:** Use `get_param(bind_name=config_key, default=default)` instead.

Get a configuration value as string.

```python
# Deprecated
project_dir = spafw37.get_config_str('project-dir', './project')
author = spafw37.get_config_str('author')

# Recommended replacement
project_dir = spafw37.get_param(bind_name='project-dir', default='./project')
author = spafw37.get_param(bind_name='author')
```

**Args:**
- `config_key` (str) - Configuration key
- `default` (str) - Default value if not found (default: '')

**Returns:**
- String value or default

##### `get_config_bool(config_key, default=False)` (Deprecated)

**⚠️ Deprecated:** Use `get_param(bind_name=config_key, default=default)` instead.

Get a configuration value as boolean.

```python
# Deprecated
debug_mode = spafw37.get_config_bool('debug-mode')
is_enabled = spafw37.get_config_bool('feature-enabled', True)

# Recommended replacement
debug_mode = spafw37.get_param('debug-mode')
is_enabled = spafw37.get_param('feature-enabled', True)
```

**Args:**
- `config_key` (str) - Configuration key
- `default` (bool) - Default value if not found (default: False)

**Returns:**
- Boolean value or default

##### `get_config_float(config_key, default=0.0)` (Deprecated)

**⚠️ Deprecated:** Use `get_param(bind_name=config_key, default=default)` instead.

Get a configuration value as float.

```python
# Deprecated
timeout = spafw37.get_config_float('timeout', 30.0)
threshold = spafw37.get_config_float('threshold')

# Recommended replacement
timeout = spafw37.get_param(bind_name='timeout', default=30.0)
threshold = spafw37.get_param(bind_name='threshold')
```

**Args:**
- `config_key` (str) - Configuration key
- `default` (float) - Default value if not found (default: 0.0)

**Returns:**
- Float value or default

##### `get_config_list(config_key, default=None)` (Deprecated)

**⚠️ Deprecated:** Use `get_param(bind_name=config_key, default=default)` instead.

Get a configuration value as list.

```python
# Deprecated
tags = spafw37.get_config_list('tags')
files = spafw37.get_config_list('files', [])

# Recommended replacement
tags = spafw37.get_param(bind_name='tags')
files = spafw37.get_param(bind_name='files', default=[])
```

**Args:**
- `config_key` (str) - Configuration key
- `default` (list) - Default value if not found (default: empty list)

**Returns:**
- List value or default. Single values are automatically wrapped in a list.

##### `get_config_dict(config_key, default=None)` (Deprecated)

**⚠️ Deprecated:** Use `get_param(bind_name=config_key, default=default)` instead.

Get a configuration value as dictionary.

```python
# Deprecated
settings = spafw37.get_config_dict('settings')
metadata = spafw37.get_config_dict('metadata', {})

# Recommended replacement
settings = spafw37.get_param(bind_name='settings')
metadata = spafw37.get_param(bind_name='metadata', default={})
```

**Args:**
- `config_key` (str) - Configuration key
- `default` (dict) - Default value if not found (default: empty dict)

**Returns:**
- Dictionary value or default

##### `set_config_value(config_key, value)` (Deprecated)

**⚠️ Deprecated:** Use `set_param(bind_name=config_key, value=value)` to replace values, or `join_param(bind_name=config_key, value=value)` to accumulate them.

Set a configuration value.

```python
# Deprecated
spafw37.set_config_value('file-index', 0)
spafw37.set_config_value('processing-complete', True)

# Recommended replacement
spafw37.set_param(bind_name='file-index', value=0)
spafw37.set_param(bind_name='processing-complete', value=True)
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
| `PARAM_ALLOWED_VALUES` | list | Allowed values for TEXT/NUMBER/LIST params. For TEXT/LIST, case-insensitive matching with normalisation. See [Parameters Guide - Allowed Values](parameters.md#allowed-values) and [example](../examples/params_allowed_values.py) |
| `PARAM_IMMUTABLE` | bool | Prevents modification or removal once set. See [Parameters Guide - Immutable Parameters](parameters.md#immutable-parameters) and [example](../examples/params_immutable.py) |

#### Configuration Binding

| Constant | Type | Description |
|----------|------|-------------|
| `PARAM_CONFIG_NAME` | str | Internal config key (defaults to PARAM_NAME) |
| `PARAM_REQUIRED` | bool | Whether param must be set |
| `PARAM_RUNTIME_ONLY` | bool | Not persisted, only for runtime use |

#### Persistence Control

| Constant | Type | Description |
|----------|------|-------------|
| `PARAM_PERSISTENCE` | str | Persistence behavior (see values below) |

**Persistence Values:**

| Constant | Value | Description |
|----------|-------|-------------|
| `PARAM_PERSISTENCE_ALWAYS` | `'always'` | Save to main config |
| `PARAM_PERSISTENCE_NEVER` | `'never'` | Never save |

#### Organisation

| Constant | Type | Description |
|----------|------|-------------|
| `PARAM_SWITCH_LIST` | list[str] | Mutually exclusive params |
| `PARAM_SWITCH_CHANGE_BEHAVIOR` | str | Controls what happens to other switches in the group when one is set. Values: `SWITCH_UNSET`, `SWITCH_RESET`, `SWITCH_REJECT` (default). See [Parameters Guide - Switch Change Behaviour](parameters.md#switch-change-behaviour) and [example](../examples/params_switch_behavior.py). Added in v1.1.0. |
| `PARAM_GROUP` | str | Group name for help display |

#### Advanced Configuration

| Constant | Type | Description |
|----------|------|-------------|
| `PARAM_INPUT_FILTER` | callable | Custom function to transform CLI string input before validation. See [Parameters Guide - Custom Input Filters](parameters.md#custom-input-filters) and [example](../examples/params_input_filter.py) |

#### Parameter Types

| Constant | Value | Description |
|----------|-------|-------------|
| `PARAM_TYPE_TEXT` | `'text'` | Text string |
| `PARAM_TYPE_NUMBER` | `'number'` | Numeric value |
| `PARAM_TYPE_TOGGLE` | `'toggle'` | Boolean flag |
| `PARAM_TYPE_LIST` | `'list'` | List of values |
| `PARAM_TYPE_DICT` | `'dict'` | Dictionary/object value |

#### Switch Change Behaviour Constants (v1.1.0)

**v1.1.0** These constants control what happens to other parameters in a switch group when one parameter is set ([see example](../examples/params_switch_behavior.py)).

| Constant | Value | Description |
|----------|-------|-------------|
| `SWITCH_UNSET` | `'switch-unset'` | Automatically unset other switches in the same group when one is set. Uses `unset_param()` to remove conflicting switches from configuration. Useful for mode switching where previous mode should be cleared. |
| `SWITCH_RESET` | `'switch-reset'` | Reset other switches in the same group to their default values when one is set. Uses `reset_param()` to restore conflicting switches to defaults. Useful when switches have meaningful default states that should be preserved. |
| `SWITCH_REJECT` | `'switch-reject'` | Raise `ValueError` if another switch in the group is already set (default behaviour). Maintains backward compatibility with existing behaviour. Useful for strict validation where only one switch should ever be set. |

**See:** [Parameters Guide - Switch Change Behaviour](parameters.md#switch-change-behaviour) for detailed usage patterns and examples.

#### Join and Merge Configuration (v1.1.0)

**v1.1.0** These constants configure type-specific behavior when accumulating parameter values with `join_param()` ([see example](../examples/params_join.py)).

| Constant | Type | Description |
|----------|------|-------------|
| `PARAM_JOIN_SEPARATOR` | str | Separator for joining string values (default: `SEPARATOR_SPACE`). Common options: `SEPARATOR_SPACE`, `SEPARATOR_COMMA`, `SEPARATOR_COMMA_SPACE`, `SEPARATOR_PIPE`, or custom string |
| `PARAM_DICT_MERGE_TYPE` | str | Dictionary merge strategy (default: `DICT_MERGE_SHALLOW`). Options: `DICT_MERGE_SHALLOW` (top-level) or `DICT_MERGE_DEEP` (recursive) |
| `PARAM_DICT_OVERRIDE_STRATEGY` | str | Conflict resolution for dict keys (default: `DICT_OVERRIDE_RECENT`). Options: `DICT_OVERRIDE_RECENT`, `DICT_OVERRIDE_OLDEST`, or `DICT_OVERRIDE_ERROR` |

**Example:**

```python
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
    PARAM_TYPE_DICT,
    PARAM_JOIN_SEPARATOR,
    PARAM_DICT_MERGE_TYPE,
    PARAM_DICT_OVERRIDE_STRATEGY,
    SEPARATOR_COMMA_SPACE,
    DICT_MERGE_DEEP,
    DICT_OVERRIDE_RECENT,
)

params = [
    {
        PARAM_NAME: 'tags-string',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_JOIN_SEPARATOR: SEPARATOR_COMMA_SPACE,  # Comma-space separator
    },
    {
        PARAM_NAME: 'settings',
        PARAM_TYPE: PARAM_TYPE_DICT,
        PARAM_DICT_MERGE_TYPE: DICT_MERGE_DEEP,  # Recursive merge
        PARAM_DICT_OVERRIDE_STRATEGY: DICT_OVERRIDE_RECENT,  # New values overwrite
    },
]
```

**See:** [Parameters Guide - Accumulating Parameter Values](parameters.md#accumulating-parameter-values) for detailed usage patterns.

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
| `CYCLE_LOOP_END` | `'cycle-loop-end-function'` | Iteration cleanup function (runs after commands complete) |
| `CYCLE_END` | `'cycle-end-function'` | Finalisation function (runs once after loop) |
| `CYCLE_COMMANDS` | `'cycle-commands'` | List of command definitions for each iteration |

**Execution order:**
```
CYCLE_INIT
while CYCLE_LOOP returns True:
    CYCLE_LOOP_START (optional)
    execute CYCLE_COMMANDS
    CYCLE_LOOP_END (optional)
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

## Advanced: Internal Module Functions

**⚠️ WARNING: These functions are for advanced use only.**

The functions documented below are from internal framework modules (`spafw37.param`, `spafw37.command`, `spafw37.cli`, etc.). Unlike the `spafw37.core` facade API:

- **No backward compatibility guarantees** - Function signatures, behavior, and availability may change between minor or patch versions
- **Direct usage discouraged** - Most applications should use the `spafw37.core` facade instead
- **Advanced scenarios only** - Use these when extending the framework or implementing complex custom behaviors

**When to use these:**
- Building framework extensions
- Implementing custom CLI parsing logic
- Advanced command queue manipulation
- Low-level parameter inspection
- Framework debugging and diagnostics

**Recommendation:** Stick to `spafw37.core` API unless you have a specific advanced requirement.

### Parameter Module (spafw37.param)

Advanced parameter inspection and management functions.

#### Quick Reference

| Function | Description |
|----------|-------------|
| **Type Checking** | |
| [`is_toggle_param(...)`](#is_toggle_paramparam_namenone-bind_namenone-aliasnone) | Check if parameter is a toggle type |
| [`is_list_param(...)`](#is_list_paramparam_namenone-bind_namenone-aliasnone) | Check if parameter is a list type |
| [`is_dict_param(...)`](#is_dict_paramparam_namenone-bind_namenone-aliasnone) | Check if parameter is a dict type |
| [`is_number_param(...)`](#is_number_paramparam_namenone-bind_namenone-aliasnone) | Check if parameter is a number type |
| [`is_text_param(...)`](#is_text_paramparam_namenone-bind_namenone-aliasnone) | Check if parameter is a text type |
| **Parameter Definition Access** | |
| [`get_param_by_name(param_name)`](#get_param_by_nameparam_name) | Get parameter definition by PARAM_NAME |
| [`get_param_by_alias(alias)`](#get_param_by_aliasalias) | Get parameter definition by alias |
| [`get_all_param_definitions()`](#get_all_param_definitions) | Get list of all parameter definitions |
| [`is_param_alias(_param, alias)`](#is_param_alias_param-alias) | Check if alias belongs to parameter |
| [`param_in_args(param_name, args)`](#param_in_argsparam_name-args) | Check if parameter appears in argument list |
| **Alias Format Checking** | |
| [`is_long_alias(arg)`](#is_long_aliasarg) | Check if arg is a long alias (e.g., `--verbose`) |
| [`is_short_alias(arg)`](#is_short_aliasarg) | Check if arg is a short alias (e.g., `-v`) |
| [`is_long_alias_with_value(arg)`](#is_long_alias_with_valuearg) | Check if arg is long alias with `=` value (e.g., `--key=value`) |
| [`is_alias(alias)`](#is_aliasalias) | Check if string is a valid alias format |
| **Persistence Functions** | |
| [`is_persistence_always(param)`](#is_persistence_alwaysparam) | Check if parameter has PARAM_PERSISTENCE_ALWAYS |
| [`is_persistence_never(param)`](#is_persistence_neverparam) | Check if parameter has PARAM_PERSISTENCE_NEVER |
| [`is_runtime_only_param(_param)`](#is_runtime_only_param_param) | Check if parameter is runtime-only |
| [`get_non_persisted_config_names()`](#get_non_persisted_config_names) | Get list of non-persisted config names |
| [`notify_persistence_change(param_name, value)`](#notify_persistence_changeparam_name-value) | Notify that persistent parameter changed |
| **Mutually Exclusive Parameters** | |
| [`get_xor_params(param_name)`](#get_xor_paramsparam_name) | Get mutually exclusive params for given param |
| [`has_xor_with(param_name, other_param_name)`](#has_xor_withparam_name-other_param_name) | Check if two params are mutually exclusive |
| **Pre-Parse Arguments** | |
| [`add_pre_parse_args(preparse_args)`](#add_pre_parse_argspreparse_args) | Register arguments for pre-parsing (used by framework) |
| [`get_pre_parse_args()`](#get_pre_parse_args) | Get list of pre-parse argument definitions |

---

#### Type Checking Functions

##### `is_toggle_param(param_name=None, bind_name=None, alias=None)`

Check if a parameter is a toggle type.

```python
from spafw37 import param

if param.is_toggle_param(param_name='debug'):
    print("debug is a toggle parameter")
    
# Check by alias
if param.is_toggle_param(alias='verbose'):
    print("verbose is a toggle parameter")
```

**Args:**
- `param_name` (str, optional) - Parameter's PARAM_NAME
- `bind_name` (str, optional) - Parameter's PARAM_CONFIG_NAME
- `alias` (str, optional) - Any of the parameter's PARAM_ALIASES

**Returns:**
- `bool` - `True` if parameter is PARAM_TYPE_TOGGLE, `False` otherwise

**Note:** Provide exactly one of `param_name`, `bind_name`, or `alias`.

##### `is_list_param(param_name=None, bind_name=None, alias=None)`

Check if a parameter is a list type.

```python
from spafw37 import param

if param.is_list_param(param_name='tags'):
    print("tags is a list parameter")
```

**Args:**
- `param_name` (str, optional) - Parameter's PARAM_NAME
- `bind_name` (str, optional) - Parameter's PARAM_CONFIG_NAME
- `alias` (str, optional) - Any of the parameter's PARAM_ALIASES

**Returns:**
- `bool` - `True` if parameter is PARAM_TYPE_LIST, `False` otherwise

##### `is_dict_param(param_name=None, bind_name=None, alias=None)`

Check if a parameter is a dict type.

```python
from spafw37 import param

if param.is_dict_param(param_name='config'):
    print("config is a dict parameter")
```

**Args:**
- `param_name` (str, optional) - Parameter's PARAM_NAME
- `bind_name` (str, optional) - Parameter's PARAM_CONFIG_NAME
- `alias` (str, optional) - Any of the parameter's PARAM_ALIASES

**Returns:**
- `bool` - `True` if parameter is PARAM_TYPE_DICT, `False` otherwise

##### `is_number_param(param_name=None, bind_name=None, alias=None)`

Check if a parameter is a number type.

```python
from spafw37 import param

if param.is_number_param(param_name='max-workers'):
    print("max-workers is a number parameter")
```

**Args:**
- `param_name` (str, optional) - Parameter's PARAM_NAME
- `bind_name` (str, optional) - Parameter's PARAM_CONFIG_NAME
- `alias` (str, optional) - Any of the parameter's PARAM_ALIASES

**Returns:**
- `bool` - `True` if parameter is PARAM_TYPE_NUMBER, `False` otherwise

##### `is_text_param(param_name=None, bind_name=None, alias=None)`

Check if a parameter is a text type.

```python
from spafw37 import param

if param.is_text_param(param_name='input-file'):
    print("input-file is a text parameter")
```

**Args:**
- `param_name` (str, optional) - Parameter's PARAM_NAME
- `bind_name` (str, optional) - Parameter's PARAM_CONFIG_NAME
- `alias` (str, optional) - Any of the parameter's PARAM_ALIASES

**Returns:**
- `bool` - `True` if parameter is PARAM_TYPE_TEXT, `False` otherwise

#### Parameter Definition Access

##### `get_param_by_name(param_name)`

Get a parameter definition dictionary by its PARAM_NAME.

```python
from spafw37 import param

param_def = param.get_param_by_name('input-file')
if param_def:
    print(f"Type: {param_def[PARAM_TYPE]}")
    print(f"Aliases: {param_def.get(PARAM_ALIASES, [])}")
```

**Args:**
- `param_name` (str) - Parameter's PARAM_NAME

**Returns:**
- `dict` - Parameter definition dictionary, or `None` if not found

**Common usage:**
- Inspecting parameter configuration
- Validating parameter properties
- Building custom help or diagnostic tools

##### `get_param_by_alias(alias)`

Get a parameter definition dictionary by any of its aliases.

```python
from spafw37 import param

param_def = param.get_param_by_alias('--input')
if param_def:
    print(f"Parameter name: {param_def[PARAM_NAME]}")
```

**Args:**
- `alias` (str) - Any alias from parameter's PARAM_ALIASES (with or without `--` prefix)

**Returns:**
- `dict` - Parameter definition dictionary, or `None` if not found

##### `get_all_param_definitions()`

Get all registered parameter definitions.

```python
from spafw37 import param

all_params = param.get_all_param_definitions()
print(f"Total parameters: {len(all_params)}")

for param_def in all_params:
    print(f"- {param_def[PARAM_NAME]}: {param_def[PARAM_TYPE]}")
```

**Returns:**
- `list[dict]` - List of all parameter definition dictionaries

**Common usage:**
- Building custom help displays
- Validating application configuration
- Generating documentation
- Parameter introspection tools

##### `is_param_alias(_param, alias)`

Check if an alias belongs to a specific parameter.

```python
from spafw37 import param

param_def = param.get_param_by_name('input-file')
if param.is_param_alias(param_def, '--input'):
    print("--input is an alias for input-file")
```

**Args:**
- `_param` (dict) - Parameter definition dictionary
- `alias` (str) - Alias to check (with or without `--` prefix)

**Returns:**
- `bool` - `True` if alias belongs to parameter, `False` otherwise

##### `param_in_args(param_name, args)`

Check if a parameter appears in an argument list.

```python
from spafw37 import param
import sys

if param.param_in_args('verbose', sys.argv):
    print("Verbose mode requested")
```

**Args:**
- `param_name` (str) - Parameter's PARAM_NAME
- `args` (list[str]) - List of command-line arguments

**Returns:**
- `bool` - `True` if any parameter alias appears in args, `False` otherwise

**Common usage:**
- Pre-processing command-line arguments
- Conditional logic before main CLI parsing
- Custom argument validation

#### Alias Format Checking

##### `is_long_alias(arg)`

Check if an argument string is a long alias format (e.g., `--verbose`).

```python
from spafw37 import param

if param.is_long_alias('--verbose'):
    print("This is a long alias")
    
if not param.is_long_alias('-v'):
    print("This is not a long alias")
```

**Args:**
- `arg` (str) - Argument string to check

**Returns:**
- `bool` - `True` if arg matches `--name` pattern, `False` otherwise

##### `is_short_alias(arg)`

Check if an argument string is a short alias format (e.g., `-v`).

```python
from spafw37 import param

if param.is_short_alias('-v'):
    print("This is a short alias")
    
if not param.is_short_alias('--verbose'):
    print("This is not a short alias")
```

**Args:**
- `arg` (str) - Argument string to check

**Returns:**
- `bool` - `True` if arg matches `-x` pattern, `False` otherwise

##### `is_long_alias_with_value(arg)`

Check if an argument string is a long alias with `=` value (e.g., `--key=value`).

```python
from spafw37 import param

if param.is_long_alias_with_value('--output=file.txt'):
    print("This is a long alias with value")
```

**Args:**
- `arg` (str) - Argument string to check

**Returns:**
- `bool` - `True` if arg matches `--key=value` pattern, `False` otherwise

**Common usage:**
- Custom CLI parsing
- Argument preprocessing
- Validation of command-line format

##### `is_alias(alias)`

Check if a string is a valid alias format (long or short).

```python
from spafw37 import param

if param.is_alias('--verbose'):
    print("Valid alias format")
    
if param.is_alias('-v'):
    print("Valid alias format")
```

**Args:**
- `alias` (str) - String to check

**Returns:**
- `bool` - `True` if alias matches `--name` or `-x` pattern, `False` otherwise

#### Persistence Functions

##### `is_persistence_always(param)`

Check if a parameter has PARAM_PERSISTENCE_ALWAYS set.

```python
from spafw37 import param
from spafw37.constants.param import PARAM_PERSISTENCE_ALWAYS

param_def = param.get_param_by_name('api-key')
if param.is_persistence_always(param_def):
    print("This parameter will always be saved to config")
```

**Args:**
- `param` (dict) - Parameter definition dictionary

**Returns:**
- `bool` - `True` if parameter should always be persisted, `False` otherwise

##### `is_persistence_never(param)`

Check if a parameter has PARAM_PERSISTENCE_NEVER set.

```python
from spafw37 import param

param_def = param.get_param_by_name('password')
if param.is_persistence_never(param_def):
    print("This parameter will never be saved to config")
```

**Args:**
- `param` (dict) - Parameter definition dictionary

**Returns:**
- `bool` - `True` if parameter should never be persisted, `False` otherwise

##### `is_runtime_only_param(_param)`

Check if a parameter is runtime-only (PARAM_RUNTIME_ONLY: True).

```python
from spafw37 import param

param_def = param.get_param_by_name('temp-state')
if param.is_runtime_only_param(param_def):
    print("This parameter is for runtime use only")
```

**Args:**
- `_param` (dict) - Parameter definition dictionary

**Returns:**
- `bool` - `True` if parameter is runtime-only, `False` otherwise

##### `get_non_persisted_config_names()`

Get list of config bind names that should never be persisted.

```python
from spafw37 import param

non_persisted = param.get_non_persisted_config_names()
print(f"Non-persisted parameters: {non_persisted}")
```

**Returns:**
- `list[str]` - List of config bind names with PARAM_PERSISTENCE_NEVER

**Common usage:**
- Building persistence logic
- Config file management
- Filtering parameters for saving

##### `notify_persistence_change(param_name, value)`

Notify config_func module about parameter value changes for persistence tracking.

```python
from spafw37 import param

# Framework calls this internally when setting parameter values
param.notify_persistence_change('api-key', 'new-key-value')
```

**Args:**
- `param_name` (str) - Parameter's PARAM_NAME
- `value` - New value for the parameter

**Note:** This is called automatically by the framework when parameter values are set. Only use this directly if implementing custom parameter setting logic.

#### Mutually Exclusive Parameters

##### `get_xor_params(param_name)`

Get list of parameters that are mutually exclusive with the given parameter.

```python
from spafw37 import param

xor_params = param.get_xor_params('format-json')
if xor_params:
    print(f"Cannot use with: {', '.join(xor_params)}")
```

**Args:**
- `param_name` (str) - Parameter's PARAM_NAME

**Returns:**
- `list[str]` - List of mutually exclusive parameter names (from PARAM_SWITCH_LIST)

**Common usage:**
- Validating parameter combinations
- Building custom help displays
- Implementing parameter conflict detection

##### `has_xor_with(param_name, other_param_name)`

Check if two parameters are mutually exclusive.

```python
from spafw37 import param

if param.has_xor_with('format-json', 'format-xml'):
    print("These parameters cannot be used together")
```

**Args:**
- `param_name` (str) - First parameter's PARAM_NAME
- `other_param_name` (str) - Second parameter's PARAM_NAME

**Returns:**
- `bool` - `True` if parameters are mutually exclusive, `False` otherwise

#### Pre-Parse Arguments

##### `add_pre_parse_args(preparse_args)`

Register arguments for pre-parsing (used internally by framework).

```python
from spafw37 import param

# Framework uses this to register logging params for pre-parsing
preparse_args = [
    {'alias': '--verbose', 'has_value': False},
    {'alias': '--log-level', 'has_value': True}
]
param.add_pre_parse_args(preparse_args)
```

**Args:**
- `preparse_args` (list[dict]) - List of pre-parse argument definitions

**Note:** This is used internally by the framework to handle parameters that need early processing (like logging configuration). Most applications should not need to call this directly.

##### `get_pre_parse_args()`

Get list of registered pre-parse argument definitions.

```python
from spafw37 import param

preparse_args = param.get_pre_parse_args()
for arg in preparse_args:
    print(f"Pre-parse: {arg['alias']}")
```

**Returns:**
- `list[dict]` - List of pre-parse argument definitions

### Command Module (spafw37.command)

Advanced command queue and execution management.

#### Quick Reference

| Function | Description |
|----------|-------------|
| **Command Definition Access** | |
| [`get_command(name)`](#get_commandname) | Get command definition by name |
| [`get_all_commands()`](#get_all_commands) | Get dictionary of all command definitions |
| [`is_command(arg)`](#is_commandarg) | Check if argument is a registered command name |
| **Command Queue Management** | |
| [`queue_command(name)`](#queue_commandname) | Manually add command to execution queue |
| [`queue_commands(names)`](#queue_commandsnames) | Manually add multiple commands to queue |
| [`has_app_commands_queued()`](#has_app_commands_queued) | Check if non-framework commands are queued |
| [`get_first_queued_command_name()`](#get_first_queued_command_name) | Get name of first queued command |
| [`run_command_queue()`](#run_command_queue) | Execute all queued commands (called by framework) |

---

#### Command Definition Access

##### `get_command(name)`

Get a command definition dictionary by name.

```python
from spafw37 import command

cmd_def = command.get_command('process')
if cmd_def:
    print(f"Description: {cmd_def.get(COMMAND_DESCRIPTION, 'N/A')}")
    print(f"Required params: {cmd_def.get(COMMAND_REQUIRED_PARAMS, [])}")
```

**Args:**
- `name` (str) - Command name (COMMAND_NAME)

**Returns:**
- `dict` - Command definition dictionary, or `None` if not found

**Common usage:**
- Inspecting command configuration
- Validating command properties
- Building custom command logic

##### `get_all_commands()`

Get all registered command definitions.

```python
from spafw37 import command

all_commands = command.get_all_commands()
for cmd_name, cmd_def in all_commands.items():
    print(f"Command: {cmd_name}")
    if COMMAND_PHASE in cmd_def:
        print(f"  Phase: {cmd_def[COMMAND_PHASE]}")
```

**Returns:**
- `dict` - Dictionary mapping command names to their definitions

**Common usage:**
- Building custom help displays
- Command introspection
- Generating documentation

##### `is_command(arg)`

Check if an argument string is a registered command name.

```python
from spafw37 import command
import sys

first_arg = sys.argv[1] if len(sys.argv) > 1 else None
if first_arg and command.is_command(first_arg):
    print(f"{first_arg} is a valid command")
```

**Args:**
- `arg` (str) - Argument string to check

**Returns:**
- `bool` - `True` if arg is a registered command name, `False` otherwise

**Common usage:**
- Pre-processing arguments
- Custom CLI parsing
- Command validation

#### Command Queue Management

##### `queue_command(name)`

Manually add a command to the execution queue.

```python
from spafw37 import command

# Queue a command programmatically
command.queue_command('setup')
command.queue_command('process')
command.queue_command('cleanup')
```

**Args:**
- `name` (str) - Command name to queue

**Note:** The framework automatically queues commands from CLI arguments. Use this for programmatic command execution or custom command sequences.

##### `queue_commands(names)`

Manually add multiple commands to the execution queue.

```python
from spafw37 import command

# Queue multiple commands at once
command.queue_commands(['setup', 'process', 'validate', 'cleanup'])
```

**Args:**
- `names` (list[str]) - List of command names to queue

##### `has_app_commands_queued()`

Check if any non-framework commands are queued.

```python
from spafw37 import command

if command.has_app_commands_queued():
    print("Application commands are queued for execution")
else:
    print("No application commands queued")
```

**Returns:**
- `bool` - `True` if non-framework commands are in queue, `False` otherwise

**Note:** Framework commands (like help, save-config) are excluded from this check.

##### `get_first_queued_command_name()`

Get the name of the first command in the execution queue.

```python
from spafw37 import command

first_cmd = command.get_first_queued_command_name()
if first_cmd:
    print(f"Next command to execute: {first_cmd}")
```

**Returns:**
- `str` - Name of first queued command, or `None` if queue is empty

**Common usage:**
- Inspecting command queue
- Custom execution logic
- Debugging command sequencing

##### `run_command_queue()`

Execute all queued commands in order.

```python
from spafw37 import command

# Queue commands
command.queue_commands(['setup', 'process', 'cleanup'])

# Execute the queue
command.run_command_queue()
```

**Note:** This is called automatically by `spafw37.run_cli()`. Only call this directly if implementing custom CLI processing.

**Behavior:**
- Resolves command dependencies
- Orders commands by phase
- Handles COMMAND_REQUIRE_BEFORE and COMMAND_NEXT_COMMANDS
- Executes each command's COMMAND_ACTION
- Manages cycle commands

### CLI Module (spafw37.cli)

Advanced CLI parsing and pre/post-parse action management.

#### Quick Reference

| Function | Description |
|----------|-------------|
| **Parse Actions** | |
| [`add_pre_parse_action(action)`](#add_pre_parse_actionaction) | Register function to run before CLI parsing |
| [`add_pre_parse_actions(actions)`](#add_pre_parse_actionsactions) | Register multiple pre-parse actions |
| [`add_post_parse_action(action)`](#add_post_parse_actionaction) | Register function to run after CLI parsing |
| [`add_post_parse_actions(actions)`](#add_post_parse_actionsactions) | Register multiple post-parse actions |
| **CLI Parsing** | |
| [`handle_cli_args(args)`](#handle_cli_argsargs) | Parse and process CLI arguments (called by `run_cli()`) |

---

#### Parse Actions

##### `add_pre_parse_action(action)`

Register a function to run before CLI parsing.

```python
from spafw37 import cli

def load_external_config():
    # Load configuration from external source
    print("Loading external configuration...")

cli.add_pre_parse_action(load_external_config)
```

**Args:**
- `action` (callable) - Function to call before parsing (no arguments)

**Common usage:**
- Loading configuration files
- Setting up logging early
- Initializing resources before parsing

**Note:** The framework uses this to load persistent config and pre-parse logging parameters. Pre-parse actions run before main argument parsing.

##### `add_pre_parse_actions(actions)`

Register multiple functions to run before CLI parsing.

```python
from spafw37 import cli

def load_config():
    print("Loading config...")

def setup_logging():
    print("Setting up logging...")

cli.add_pre_parse_actions([load_config, setup_logging])
```

**Args:**
- `actions` (list[callable]) - List of functions to call before parsing

##### `add_post_parse_action(action)`

Register a function to run after CLI parsing.

```python
from spafw37 import cli

def save_runtime_state():
    # Save state after parsing completes
    print("Saving runtime state...")

cli.add_post_parse_action(save_runtime_state)
```

**Args:**
- `action` (callable) - Function to call after parsing (no arguments)

**Common usage:**
- Saving configuration
- Validating parsed values
- Setting up resources based on parameters

**Note:** The framework uses this to save persistent config. Post-parse actions run after all argument parsing is complete but before command execution.

##### `add_post_parse_actions(actions)`

Register multiple functions to run after CLI parsing.

```python
from spafw37 import cli

def validate_config():
    print("Validating configuration...")

def save_config():
    print("Saving configuration...")

cli.add_post_parse_actions([validate_config, save_config])
```

**Args:**
- `actions` (list[callable]) - List of functions to call after parsing

#### CLI Parsing

##### `handle_cli_args(args)`

Parse and process command-line arguments.

```python
from spafw37 import cli
import sys

# Process command-line arguments
cli.handle_cli_args(sys.argv[1:])
```

**Args:**
- `args` (list[str]) - List of command-line argument strings

**Behavior:**
- Runs pre-parse actions
- Sets parameter defaults
- Tokenizes and parses arguments
- Sets parameter values
- Runs post-parse actions
- Queues commands for execution

**Note:** This is called automatically by `spafw37.run_cli()`. Only call this directly if implementing custom CLI entry points.

**Common usage:**
- Custom CLI entry points
- Testing CLI parsing
- Non-standard argument sources

---

## Examples

For complete working examples demonstrating these API functions and constants, see the **[examples directory](https://github.com/minouris/spafw37/tree/main/examples)**:

- **Parameters** (11 files): Basic usage, toggles, lists, dicts, file loading, required validation, runtime modification, grouping, **v1.1.0:** join accumulation, custom input filters
- **Commands** (7 files): Basic definition, sequencing, dependencies, chaining, required validation, triggering, visibility
- **Cycles** (3 files): Basic usage, custom loop initialisation, nested patterns
- **Phases** (4 files): Basic usage, custom ordering, extended lifecycle, custom definitions
- **Output** (2 files): Basic output with verbose/silent modes, custom handlers (file, dual, timestamped)
- **Configuration** (2 files): Basic usage, persistence patterns
- **Inline Definitions** (2 files): Basic inline parameter definitions, advanced patterns (nested, mixed)

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
