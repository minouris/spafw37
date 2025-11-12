# Commands Guide

## Table of Contents

- [Overview](#overview)
- [Command Definition Constants](#command-definition-constants)
- [Basic Command Definition](#basic-command-definition)
- [Command Actions](#command-actions)
- [Required Parameters](#required-parameters)
- [Extended Help Text](#extended-help-text)
- [Command Sequencing](#command-sequencing)
- [Automatic Dependencies](#automatic-dependencies)
- [Parameter-Triggered Commands](#parameter-triggered-commands)
- [Command Visibility](#command-visibility)

## Overview

Commands define the actions your application can perform. They encapsulate functionality with automatic dependency resolution, parameter validation, topological sorting, and flexible execution control. Commands can be invoked from the CLI, triggered by parameters, or automatically queued based on dependencies.

Key capabilities:
- Declarative action definition with Python functions
- Automatic parameter validation before execution
- Dependency management and automatic queueing
- Sequencing constraints for execution order
- Phase-based execution control
- Parameter-triggered automatic invocation
- Integration with cycles for repeated execution
- Automatic help generation

## Command Definition Constants

Commands are defined as dictionaries using these constants as keys:

### Basic Command Properties

| Constant | Description |
|----------|-------------|
| `COMMAND_NAME` | Used on the CLI to queue the command |
| `COMMAND_DESCRIPTION` | Description of the command |
| `COMMAND_HELP` | Extended help text for the command |
| `COMMAND_ACTION` | Function to call when the command is run |
| `COMMAND_REQUIRED_PARAMS` | List of param bind names that are required for this command |

### Sequencing and Dependencies

| Constant | Description |
|----------|-------------|
| `COMMAND_GOES_BEFORE` | List of command names that will be sequenced before this in a queue - user queued |
| `COMMAND_GOES_AFTER` | List of command names that will be sequenced after this in a queue - user queued |
| `COMMAND_REQUIRE_BEFORE` | List of command names that must be completed before this in a queue - automatically queued if this command is invoked |
| `COMMAND_NEXT_COMMANDS` | List of command names that will be automatically queued after this command is run |

### Advanced Features

| Constant | Description |
|----------|-------------|
| `COMMAND_TRIGGER_PARAM` | Param bind name that triggers this command when set |
| `COMMAND_PHASE` | Phase in which this command should be run |
| `COMMAND_CYCLE` | Attaches a cycle to a command, from the command side |

### Command Visibility and Behavior

| Constant | Description |
|----------|-------------|
| `COMMAND_FRAMEWORK` | True if this is a framework-defined command (vs app-defined) |
| `COMMAND_EXCLUDE_FROM_HELP` | True if this command should be excluded from help displays |
| `COMMAND_INVOCABLE` | Marks a command as invocable by a param-trigger, or a CLI command. Default true for regular commands, false for cycle-internal commands. |

## Basic Command Definition

The minimum viable command requires only a name, description, and action:

```python
from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)

def hello_action():
    """Print a greeting."""
    print("Hello, World!")

commands = [
    {
        COMMAND_NAME: 'hello',
        COMMAND_DESCRIPTION: 'Print a greeting',
        COMMAND_ACTION: hello_action,
    }
]

spafw37.add_commands(commands)
```

Usage:
```bash
python my_app.py hello
# Output: Hello, World!
```

## Command Actions

Command actions are regular Python functions called when the command executes:

```python
def build_action():
    """Build the project."""
    print("Building project...")
    # Build logic here
    print("Build complete!")

{
    COMMAND_NAME: 'build',
    COMMAND_DESCRIPTION: 'Build the project',
    COMMAND_ACTION: build_action,
}
```

Actions can be:
- Named functions (recommended for clarity)
- Lambda functions for simple commands
- Any callable Python object

```python
# Lambda example for simple commands
{
    COMMAND_NAME: 'version',
    COMMAND_DESCRIPTION: 'Display version',
    COMMAND_ACTION: lambda: print("v1.0.0"),
}
```

## Required Parameters

Specify parameters that must be provided before the command can execute:

```python
from spafw37.constants.command import COMMAND_REQUIRED_PARAMS

def deploy_action():
    """Deploy to target environment."""
    target = spafw37.get_config('target-env')
    api_key = spafw37.get_config('api-key')
    print(f"Deploying to {target}...")
    # Deploy logic using api_key

{
    COMMAND_NAME: 'deploy',
    COMMAND_DESCRIPTION: 'Deploy to target environment',
    COMMAND_ACTION: deploy_action,
    COMMAND_REQUIRED_PARAMS: ['target-env', 'api-key'],
}
```

The framework validates required parameters just before command execution. If any are missing, an error is raised with helpful information.

Usage:
```bash
# Missing parameters - will show error and help
python my_app.py deploy

# Correct usage
python my_app.py deploy --target-env production --api-key abc123
```

## Extended Help Text

Provide detailed help information for commands:

```python
from spafw37.constants.command import COMMAND_HELP

{
    COMMAND_NAME: 'build',
    COMMAND_DESCRIPTION: 'Build the project',
    COMMAND_HELP: """
Build the project using the specified configuration.

The build process will:
  1. Compile all source files
  2. Link dependencies
  3. Generate output in the specified directory

Build types:
  - debug: Includes debug symbols and assertions
  - release: Optimized build for production
    """.strip(),
    COMMAND_ACTION: build_action,
    COMMAND_REQUIRED_PARAMS: ['build-type', 'target'],
}
```

Extended help is displayed when using `help <command>`:
```bash
python my_app.py help build
```

## Command Sequencing

Control the order in which commands execute using sequencing constraints.

### COMMAND_GOES_AFTER

Ensure this command runs after specified commands (if they're queued):

```python
commands = [
    {
        COMMAND_NAME: 'clean',
        COMMAND_DESCRIPTION: 'Clean build artifacts',
        COMMAND_ACTION: clean_action,
    },
    {
        COMMAND_NAME: 'build',
        COMMAND_DESCRIPTION: 'Build the project',
        COMMAND_ACTION: build_action,
        COMMAND_GOES_AFTER: ['clean'],  # Build runs after clean (if clean is queued)
    },
]
```

Usage:
```bash
# Queues both, executes: clean → build
python my_app.py build clean

# Only queues build
python my_app.py build
```

### COMMAND_GOES_BEFORE

Ensure this command runs before specified commands (if they're queued):

```python
{
    COMMAND_NAME: 'setup',
    COMMAND_DESCRIPTION: 'Set up environment',
    COMMAND_ACTION: setup_action,
    COMMAND_GOES_BEFORE: ['build', 'test'],  # Setup runs before build or test
}
```

Usage:
```bash
# Queues both, executes: setup → build
python my_app.py build setup
```

## Automatic Dependencies

Automatically queue prerequisite commands using `COMMAND_REQUIRE_BEFORE`:

```python
commands = [
    {
        COMMAND_NAME: 'configure',
        COMMAND_DESCRIPTION: 'Configure build system',
        COMMAND_ACTION: configure_action,
    },
    {
        COMMAND_NAME: 'build',
        COMMAND_DESCRIPTION: 'Build the project',
        COMMAND_ACTION: build_action,
        COMMAND_REQUIRE_BEFORE: ['configure'],  # Auto-queues configure
    },
]
```

When `build` is invoked, `configure` is automatically added to the queue if not already present:

```bash
# Automatically runs: configure → build
python my_app.py build
```

### Chaining with COMMAND_NEXT_COMMANDS

Automatically queue follow-up commands after execution:

```python
{
    COMMAND_NAME: 'build',
    COMMAND_DESCRIPTION: 'Build the project',
    COMMAND_ACTION: build_action,
    COMMAND_NEXT_COMMANDS: ['test'],  # Auto-queues test after build
}
```

Usage:
```bash
# Automatically runs: build → test
python my_app.py build
```

### Complex Dependency Chains

Combine constraints for complex workflows:

```python
commands = [
    {
        COMMAND_NAME: 'clean',
        COMMAND_ACTION: clean_action,
    },
    {
        COMMAND_NAME: 'configure',
        COMMAND_ACTION: configure_action,
        COMMAND_REQUIRE_BEFORE: ['clean'],
    },
    {
        COMMAND_NAME: 'build',
        COMMAND_ACTION: build_action,
        COMMAND_REQUIRE_BEFORE: ['configure'],
        COMMAND_NEXT_COMMANDS: ['test'],
    },
    {
        COMMAND_NAME: 'test',
        COMMAND_ACTION: test_action,
    },
]
```

Invoking `build` automatically creates the chain: `clean → configure → build → test`

## Parameter-Triggered Commands

Commands can be automatically invoked when a parameter is set:

```python
def load_plugins_action():
    """Load plugins from a specified directory."""
    plugin_dir = spafw37.get_config('plugin-dir')
    print(f"Loading plugins from {plugin_dir}...")
    # Plugin loading logic here

{
    COMMAND_NAME: 'load-plugins',
    COMMAND_DESCRIPTION: 'Load application plugins',
    COMMAND_ACTION: load_plugins_action,
    COMMAND_TRIGGER_PARAM: 'plugin-dir',  # Triggered when --plugin-dir is set
    COMMAND_REQUIRED_PARAMS: ['plugin-dir'],
}
```

Usage:
```bash
# load-plugins command runs automatically before other commands
python my_app.py process --plugin-dir ./plugins
```

This is useful for:
- Loading configuration or resources before other commands execute
- Initialization commands (loading plugins, connecting to databases)
- Setup tasks that depend on specific parameters being provided

## Command Visibility

### Framework Commands

Mark commands as framework-internal (vs application commands):

```python
{
    COMMAND_NAME: 'internal-config',
    COMMAND_ACTION: internal_action,
    COMMAND_FRAMEWORK: True,  # Not counted as app command
}
```

This helps distinguish between framework utilities and application functionality.

### Excluding from Help

Hide commands from the main help listing:

```python
{
    COMMAND_NAME: 'deprecated-command',
    COMMAND_ACTION: old_action,
    COMMAND_EXCLUDE_FROM_HELP: True,  # Hidden from help listing
}
```

The command is still executable but doesn't clutter help output. Useful for:
- Deprecated commands
- Internal/advanced commands
- Framework utilities

## Advanced Topics

For more advanced command features, see:

- **[Cycles Guide](cycles.md)** - Repeating command sequences with init/loop/end functions
- **[Phases Guide](phases.md)** - Multi-phase execution control and lifecycle management

---

## Documentation

- **[Parameters Guide](parameters.md)** - Parameter definition and usage
- **[Commands Guide](commands.md)** - Detailed command system documentation
- **[Configuration Guide](configuration.md)** - Configuration management
- **[Cycles Guide](cycles.md)** - Repeating command sequences
- **[Phases Guide](phases.md)** - Multi-phase execution control
- **[Logging Guide](logging.md)** - Built-in logging system
- **[API Reference](api-reference.md)** - Complete API documentation

---

**Previous:** [← Parameters Guide](parameters.md)  
**Next:** [Configuration Guide →](configuration.md)
