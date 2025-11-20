# SPAFW37 User Guide

[Index](README.md#documentation) | [Parameters Guide →](parameters.md)

**A lightweight Python 3.7+ framework for building command-line applications with advanced configuration management, command orchestration, and execution control.**

## Table of Contents

- [Overview](#overview)
- [Version Changes](#version-changes)
- [Quick Start](#quick-start)
  - [Creating Your First Application](#creating-your-first-application)
  - [Running Your Application](#running-your-application)
- [Key Features](#key-features)
  - [Flexible Parameter System](#flexible-parameter-system)
  - [Declarative Command Definition](#declarative-command-definition)
  - [Command Orchestration](#command-orchestration)
  - [Multi-Phase Execution](#multi-phase-execution)
  - [Cycle Support](#cycle-support)
  - [Configuration Management](#configuration-management)
  - [Integrated Logging](#integrated-logging)
- [Documentation](#documentation)
- [Examples](#examples)
- [Requirements](#requirements)
- [License](#license)

## Overview

SPAFW37 provides a declarative approach to building CLI applications by defining commands and parameters as structured dictionaries. The framework handles:

- **Parameter Management** - Flexible parameter system with aliases, types, and validation
- **Command Registration & Execution** - Define commands with actions, dependencies, and sequencing
- **Configuration Management** - Persistent and runtime configuration with file I/O
- **Command Orchestration** - Automatic dependency resolution and topological sorting
- **Phase-based Execution** - Multi-phase command execution with lifecycle control
- **Cycle Support** - Repeating command sequences with init/loop/end functions
- **Integrated Help System** - Automatic help generation for commands and parameters
- **Logging Framework** - Built-in logging with levels, scopes, and file/console output

## Version Changes

### v1.1.0

**Parameter API Simplification:**
- Introduced unified `get_param()` function for type-safe parameter access
- Added `set_param()` for replacing parameter values with automatic validation
- Added `join_param()` for accumulating values (strings, lists, dicts) with type-specific logic
- Deprecated legacy configuration API functions in favor of the new Parameter API
- All examples and documentation updated to demonstrate the simplified API

**Enhanced Parameter Features:**
- Added `PARAM_JOIN_SEPARATOR` for configurable string concatenation
- Added `PARAM_DICT_MERGE_TYPE` for shallow/deep dictionary merging
- Added `PARAM_DICT_OVERRIDE_STRATEGY` for handling dictionary key conflicts
- Multiple `@file` references now supported for list parameters

**Backward Compatibility:**
- All deprecated functions continue to work with one-time deprecation warnings
- Existing applications continue to function without modification
- Migration path clearly documented in configuration guide

## Quick Start

### Creating Your First Application

Let's build a simple CLI application that greets users by name. We'll walk through each part of the code.

#### Step 1: Import the Framework

Access the framework's core functionality.

```python
"""my_app.py - A simple SPAFW37 application"""
from spafw37 import core as spafw37
```

The `core` module is your main entry point. Import it as `spafw37` for convenience.

#### Step 2: Import Constants

Import the constants needed to define your parameters and commands.

```python
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
    COMMAND_REQUIRED_PARAMS,
)
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_TYPE,
    PARAM_TYPE_TEXT,
)
```

These constants are used as keys in command and parameter dictionaries.

#### Step 3: Define Parameters

Define what command-line arguments your application accepts.

```python
params = [
    {
        PARAM_NAME: 'user-name',
        PARAM_DESCRIPTION: 'Name of the user to greet',
        PARAM_ALIASES: ['--name', '-n'],
        PARAM_TYPE: PARAM_TYPE_TEXT,
    }
]
```

Each parameter definition includes:
- **`PARAM_NAME`** - Internal name used with `get_param()`, `set_param()`, etc.
- **`PARAM_DESCRIPTION`** - Shown in help text
- **`PARAM_ALIASES`** - CLI flags (e.g., `--name` or `-n`)
- **`PARAM_TYPE`** - Type of value (e.g., `PARAM_TYPE_TEXT`, `PARAM_TYPE_NUMBER`, `PARAM_TYPE_TOGGLE`)

When parameter values are set from the command line, they are stored in the configuration store and can be retrieved by commands using the typed getters.

#### Step 4: Define Your Command Action

Write the function that will execute when your command runs.

```python
def greet_action():
    """Greet the user by name."""
    name = spafw37.get_param('user-name')
    spafw37.output(f"Hello, {name}!")
```

Command actions are regular Python functions. Use `get_param()` to retrieve parameter values that were set from the command line. The method automatically returns the correct type based on the parameter's `PARAM_TYPE` definition.

#### Step 5: Define Commands

Define what commands your application provides and link them to their actions.

```python
commands = [
    {
        COMMAND_NAME: 'greet',
        COMMAND_DESCRIPTION: 'Greet the user',
        COMMAND_ACTION: greet_action,
        COMMAND_REQUIRED_PARAMS: ['user-name'],
    }
]
```

Commands specify:
- **`COMMAND_NAME`** - Name used on the CLI (e.g., `python my_app.py greet`)
- **`COMMAND_DESCRIPTION`** - Shown in help listings
- **`COMMAND_ACTION`** - Function to call when command executes
- **`COMMAND_REQUIRED_PARAMS`** - Parameters that must be provided to run this command (uses internal parameter names)

#### Step 6: Register and Run

Register everything with the framework and start processing command-line arguments.

```python
spafw37.add_params(params)
spafw37.add_commands(commands)
spafw37.set_app_name('my-app')

if __name__ == '__main__':
    # Call run_cli() LAST, after all setup is complete
    spafw37.run_cli()
```

**Important:** Call `run_cli()` **after** registering all parameters, commands, cycles, and phases. This function parses command-line arguments and executes commands, so everything must be set up first.

### Running Your Application

```bash
# Display help
python my_app.py help

# Run the greet command
python my_app.py greet --name Alice
# Output: Hello, Alice!

# Get help for a specific command
python my_app.py help greet
```

## Key Features

### Flexible Parameter System

Parameters support multiple aliases, types, and automatic configuration binding:

```python
{
    PARAM_NAME: 'input-file',
    PARAM_DESCRIPTION: 'Input file to process',
    PARAM_ALIASES: ['--input', '-i'],
    PARAM_TYPE: PARAM_TYPE_TEXT,
    PARAM_GROUP: 'Input/Output Options',  # Grouped in help
}
```

### Declarative Command Definition

Commands are defined as dictionaries with clear, self-documenting structure:

```python
{
    COMMAND_NAME: 'build',
    COMMAND_DESCRIPTION: 'Build the project',
    COMMAND_ACTION: build_function,
    COMMAND_REQUIRED_PARAMS: ['build-type', 'target'],
    COMMAND_GOES_AFTER: ['setup'],  # Sequencing
    COMMAND_REQUIRE_BEFORE: ['clean'],  # Dependencies
}
```

### Command Orchestration

Define complex workflows with automatic dependency resolution:

```python
commands = [
    {COMMAND_NAME: 'clean', ...},
    {
        COMMAND_NAME: 'build',
        COMMAND_REQUIRE_BEFORE: ['clean'],  # Auto-queues clean
        COMMAND_NEXT_COMMANDS: ['test'],     # Auto-queues test after
        ...
    },
    {COMMAND_NAME: 'test', ...},
]
```

### Cycle Support

Create repeating command sequences for batch processing:

```python
{
    COMMAND_NAME: 'process-files',
    COMMAND_ACTION: lambda: None,
    COMMAND_CYCLE: {
        CYCLE_NAME: 'file-processing',
        CYCLE_INIT: initialize_files,      # Called once before loop
        CYCLE_LOOP: has_more_files,        # Returns True to continue
        CYCLE_END: finalize_processing,    # Called once after loop
        CYCLE_COMMANDS: ['validate', 'transform', 'save'],
    }
}
```

### Configuration Management

Access configuration values set by parameters or loaded from files:

```python
# In your command action
def process_action():
    input_file = spafw37.get_param('input-file')
    debug_mode = spafw37.get_param('debug-mode')
    # ... process ...
```

Set a central configuration file for your application:

```python
# The framework automatically saves and loads important values to this file
spafw37.set_config_file('my_app_config.json')
```

Save and load configuration files on demand:

```python
# Load configuration from a specific file
python my_app.py --load-user-config custom_config.json

# Save current configuration to a specific file
python my_app.py --save-user-config output_config.json
```

The framework maintains separate persistent and runtime-only configuration, allowing you to control what gets saved.

## Documentation

- **[User Guide](README.md)** - Overview and quick start
- **[Parameters Guide](parameters.md)** - Parameter definition and usage
- **[Commands Guide](commands.md)** - Command system and dependencies
- **[Phases Guide](phases.md)** - Multi-phase execution control
- **[Cycles Guide](cycles.md)** - Repeating command sequences
- **[Configuration Guide](configuration.md)** - Configuration management
- **[Logging Guide](logging.md)** - Built-in logging system
- **[API Reference](api-reference.md)** - Complete API documentation

## Examples

Complete working examples demonstrating each feature are available in the [`examples/`](../examples/) directory:

- **[Examples README](../examples/README.md)** - Overview of all examples with descriptions
- Parameters: basic, toggles, lists, runtime-only
- Commands: basic, sequencing, dependencies
- Cycles: basic, loop_start
- Configuration: basic, persistence

See individual example files for focused demonstrations of specific features.

## What's New in v1.1.0

- **New Parameter API** - Access parameters with the intelligent `get_param()` function that automatically returns the correct type. Set values with `set_param()` or accumulate them with `join_param()`

## Requirements

- Python 3.7.0 or higher
- No external dependencies (uses Python standard library only)

## License

MIT License - See LICENSE.md for details

---

[Index](README.md#documentation) | [Parameters Guide →](parameters.md)
