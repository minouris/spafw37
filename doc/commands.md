# Commands Guide

[← Parameters Guide](parameters.md) | [Index](README.md#documentation) | [Phases Guide →](phases.md)

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
| `COMMAND_REQUIRED_PARAMS` | List of param bind names that are required for this command. See [examples/commands_required.py](../examples/commands_required.py) for usage. |

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
| `COMMAND_TRIGGER_PARAM` | Param bind name that triggers this command when set. See [examples/commands_trigger.py](../examples/commands_trigger.py) for usage. |
| `COMMAND_PHASE` | Phase in which this command should be run |
| `COMMAND_CYCLE` | Attaches a cycle to a command, from the command side |

### Command Visibility and Behavior

| Constant | Description |
|----------|-------------|
| `COMMAND_FRAMEWORK` | True if this is a framework-defined command (vs app-defined). See [examples/commands_visibility.py](../examples/commands_visibility.py) for usage. |
| `COMMAND_EXCLUDE_HELP` | True if this command should be excluded from help displays. See [examples/commands_visibility.py](../examples/commands_visibility.py) for usage. |
| `COMMAND_INVOCABLE` | Marks a command as invocable by a param-trigger, or a CLI command. Default true for regular commands, false for cycle-internal commands. |

## Basic Command Definition

The minimum viable command requires only a name, description, and action ([see example](../examples/commands_basic.py)):

```python
from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)

def hello_action():
    """Print a greeting."""
    spafw37.output("Hello, World!")

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
    spafw37.output("Building project...")
    # Build logic here
    spafw37.output("Build complete!")

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
    COMMAND_ACTION: lambda: spafw37.output("v1.0.0"),
}
```

## Required Parameters

Specify parameters that must be provided before a specific command can execute ([see example](../examples/commands_required.py)):

```python
from spafw37.constants.command import COMMAND_REQUIRED_PARAMS

def deploy_action():
    """Deploy to target environment."""
    target = spafw37.get_config('environment')
    api_key = spafw37.get_config('api-key')
    instance_count = spafw37.get_config('instance-count')
    spafw37.output(f"Deploying to {target}...")
    spafw37.output(f"Instances: {instance_count}")
    # Deploy logic using api_key

{
    COMMAND_NAME: 'deploy',
    COMMAND_DESCRIPTION: 'Deploy application',
    COMMAND_ACTION: deploy_action,
    COMMAND_REQUIRED_PARAMS: ['api-key', 'instance-count'],
}
```

The framework validates required parameters just before command execution. If any are missing, an error is raised with helpful information showing which parameters are needed.

Usage:
```bash
# Missing parameters - will show error and help
python my_app.py deploy
# Error: Missing required parameter 'api-key' for command 'deploy'

# Correct usage
python my_app.py deploy --key abc123 --count 3
```

**Key Points:**
- `COMMAND_REQUIRED_PARAMS` is command-specific (only required for that command)
- Different commands can have different parameter requirements
- Validation happens just before the command executes
- Error messages show exactly which parameters are needed

**Note:** For globally required parameters (required for all commands), see [Required Parameters](parameters.md#required-parameters) in the Parameters Guide.

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

Control the order in which commands execute using sequencing constraints ([see example](../examples/commands_sequencing.py)).

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

Automatically queue prerequisite commands using `COMMAND_REQUIRE_BEFORE` ([see example](../examples/commands_dependencies.py)):

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

Commands can be automatically invoked when a parameter is set ([see example](../examples/commands_trigger.py)):

```python
from spafw37.constants.command import COMMAND_TRIGGER_PARAM

def load_plugins_action():
    """Load plugins from a specified directory."""
    plugin_dir = spafw37.get_config('plugin-dir')
    spafw37.output(f"Loading plugins from {plugin_dir}...")
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
# load-plugins command runs automatically when plugin-dir is set
python my_app.py process --plugin-dir ./plugins
```

This is useful for:
- Loading configuration or resources before other commands execute
- Initialization commands (loading plugins, connecting to databases)
- Setup tasks that depend on specific parameters being provided

**Key Points:**
- Triggered commands are queued automatically when their trigger parameter is set
- Can be combined with COMMAND_REQUIRED_PARAMS for validation
- Multiple commands can be triggered by different parameters
- Useful for setup and initialization workflows

## Command Visibility

### Framework Commands

Mark commands as framework-internal (vs application commands) ([see example](../examples/commands_visibility.py)):

```python
from spafw37.constants.command import COMMAND_FRAMEWORK

{
    COMMAND_NAME: 'internal-config',
    COMMAND_ACTION: internal_action,
    COMMAND_FRAMEWORK: True,  # Not counted as app command
}
```

This helps distinguish between framework utilities and application functionality.

### Excluding from Help

Hide commands from the main help listing ([see example](../examples/commands_visibility.py)):

```python
from spafw37.constants.command import COMMAND_EXCLUDE_HELP

{
    COMMAND_NAME: 'deprecated-command',
    COMMAND_ACTION: old_action,
    COMMAND_EXCLUDE_HELP: True,  # Hidden from help listing
}
```

The command is still executable but doesn't clutter help output. Useful for:
- Deprecated commands
- Internal/advanced commands
- Framework utilities

**Key Points:**
- Hidden commands remain fully functional
- Can still be invoked by name on the command line
- Useful for maintaining backward compatibility
- Helps keep help output clean and focused

## Advanced Topics

For more advanced command features, see:

- **[Cycles Guide](cycles.md)** - Repeating command sequences with init/loop/end functions
- **[Phases Guide](phases.md)** - Multi-phase execution control and lifecycle management

---

## Examples

Complete working examples demonstrating command features:

- **[commands_basic.py](../examples/commands_basic.py)** - Basic command definition and actions (greet, hello, goodbye)
- **[commands_sequencing.py](../examples/commands_sequencing.py)** - Command execution order with GOES_BEFORE and GOES_AFTER constraints
- **[commands_dependencies.py](../examples/commands_dependencies.py)** - Automatic dependency resolution with REQUIRE_BEFORE and NEXT_COMMANDS
- **[commands_required.py](../examples/commands_required.py)** - Command-specific required parameters with COMMAND_REQUIRED_PARAMS
- **[commands_trigger.py](../examples/commands_trigger.py)** - Parameter-triggered commands with COMMAND_TRIGGER_PARAM
- **[commands_visibility.py](../examples/commands_visibility.py)** - Command visibility control with COMMAND_FRAMEWORK and COMMAND_EXCLUDE_HELP

See [examples/README.md](../examples/README.md) for a complete guide to all available examples.

---

## Documentation

- **[User Guide](README.md)** - Overview and quick start
- **[Parameters Guide](parameters.md)** - Parameter definition and usage
- **Commands Guide** - Command system and dependencies
- **[Phases Guide](phases.md)** - Multi-phase execution control
- **[Cycles Guide](cycles.md)** - Repeating command sequences
- **[Configuration Guide](configuration.md)** - Configuration management
- **[Logging Guide](logging.md)** - Built-in logging system
- **[API Reference](api-reference.md)** - Complete API documentation

---

[← Parameters Guide](parameters.md) | [Index](README.md#documentation) | [Phases Guide →](phases.md)
