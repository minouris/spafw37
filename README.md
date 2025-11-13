# spafw37

[![Python 3.7](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight Python 3.7+ framework for building command-line applications with advanced configuration management, command orchestration, and execution control.

**Repository:** https://github.com/minouris/spafw37

## Features

- **Flexible Parameter System** - Typed parameters with aliases, defaults, validation, and persistence
- **Declarative Command Definition** - Define commands with actions, dependencies, and orchestration
- **Command Orchestration** - Automatic dependency resolution, sequencing, and triggers
- **Multi-Phase Execution** - Organize commands into setup, cleanup, execution, teardown, and end phases
- **Cycle Support** - Repeating command sequences with init/loop/finalization hooks
- **Configuration Management** - Persistent and runtime configuration with file I/O
- **Integrated Logging** - Built-in logging with levels, scopes, and file/console output
- **Automatic Help System** - Generated help for commands, parameters, and groups

## Installation

### From TestPyPI (Development Releases)

```bash
pip install -i https://test.pypi.org/simple/ spafw37
```

### From Source

```bash
git clone https://github.com/minouris/spafw37.git
cd spafw37
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Development Installation

```bash
pip install -e .[dev]
pytest
```

## Quick Start

Create a simple CLI application in minutes:

```python
"""greet.py - A simple greeting application"""
from spafw37 import core as spafw37
from spafw37.constants.param import (
    PARAM_NAME,
    PARAM_DESCRIPTION,
    PARAM_ALIASES,
    PARAM_DEFAULT,
)
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_DESCRIPTION,
    COMMAND_ACTION,
)

# Define parameters
params = [
    {
        PARAM_NAME: 'name',
        PARAM_DESCRIPTION: 'Name to greet',
        PARAM_ALIASES: ['--name', '-n'],
        PARAM_DEFAULT: 'World',
    }
]

# Define command action
def greet():
    name = spafw37.get_config_str('name')
    print(f"Hello, {name}!")

# Define commands
commands = [
    {
        COMMAND_NAME: 'greet',
        COMMAND_DESCRIPTION: 'Greet someone',
        COMMAND_ACTION: greet,
    }
]

# Register and run
spafw37.add_params(params)
spafw37.add_commands(commands)

if __name__ == '__main__':
    spafw37.run_cli()
```

Run it:

```bash
python greet.py greet --name Alice
# Output: Hello, Alice!

python greet.py greet
# Output: Hello, World!

python greet.py --help
# Shows available commands and parameters
```

## Documentation

Comprehensive guides are available in the [`doc/`](doc/) directory:

- **[User Guide](doc/README.md)** - Complete framework overview and getting started
- **[Parameters Guide](doc/parameters.md)** - Parameter types, aliases, persistence, and validation
- **[Commands Guide](doc/commands.md)** - Command definition, dependencies, and orchestration
- **[Phases Guide](doc/phases.md)** - Multi-phase execution and lifecycle management
- **[Cycles Guide](doc/cycles.md)** - Repeating command sequences and iteration patterns
- **[Configuration Guide](doc/configuration.md)** - Configuration management and persistence
- **[Logging Guide](doc/logging.md)** - Logging system and configuration
- **[API Reference](doc/api-reference.md)** - Complete API documentation

## Examples

The [`examples/`](examples/) directory contains focused examples demonstrating specific features:

### Parameters
- [`params_basic.py`](examples/params_basic.py) - Text, number, aliases, defaults
- [`params_toggles.py`](examples/params_toggles.py) - Boolean flags and mutually exclusive options
- [`params_lists.py`](examples/params_lists.py) - Multi-value parameters
- [`params_required.py`](examples/params_required.py) - Globally required parameters
- [`params_runtime.py`](examples/params_runtime.py) - Runtime-only state management
- [`params_groups.py`](examples/params_groups.py) - Organized parameter display

### Commands
- [`commands_basic.py`](examples/commands_basic.py) - Simple command execution
- [`commands_sequencing.py`](examples/commands_sequencing.py) - Execution order control
- [`commands_dependencies.py`](examples/commands_dependencies.py) - Prerequisite enforcement
- [`commands_next.py`](examples/commands_next.py) - Automatic command chaining
- [`commands_required.py`](examples/commands_required.py) - Command-specific required parameters
- [`commands_trigger.py`](examples/commands_trigger.py) - Parameter-triggered commands
- [`commands_visibility.py`](examples/commands_visibility.py) - Hidden and framework commands

### Cycles
- [`cycles_basic.py`](examples/cycles_basic.py) - Simple iteration patterns
- [`cycles_loop_start.py`](examples/cycles_loop_start.py) - Per-iteration preparation
- [`cycles_nested.py`](examples/cycles_nested.py) - Multi-level nested cycles

### Phases
- [`phases_basic.py`](examples/phases_basic.py) - Default phase system
- [`phases_custom_order.py`](examples/phases_custom_order.py) - Custom phase ordering
- [`phases_extended.py`](examples/phases_extended.py) - Extending default phases
- [`phases_custom.py`](examples/phases_custom.py) - Completely custom phases

### Configuration
- [`config_basic.py`](examples/config_basic.py) - Runtime configuration
- [`config_persistence.py`](examples/config_persistence.py) - Persistent configuration

See the [Examples README](examples/README.md) for detailed descriptions and usage instructions.

## Core Concepts

### Parameters

Define parameters as dictionaries with type information, aliases, and behavior:

```python
from spafw37.constants.param import *

{
    PARAM_NAME: 'output-dir',
    PARAM_DESCRIPTION: 'Output directory',
    PARAM_ALIASES: ['--output', '-o'],
    PARAM_TYPE: PARAM_TYPE_TEXT,
    PARAM_DEFAULT: './output',
    PARAM_REQUIRED: False,
}
```

**Types:** `PARAM_TYPE_TEXT`, `PARAM_TYPE_NUMBER`, `PARAM_TYPE_TOGGLE`, `PARAM_TYPE_LIST`

### Commands

Define commands with actions, dependencies, and execution control:

```python
from spafw37.constants.command import *

{
    COMMAND_NAME: 'deploy',
    COMMAND_DESCRIPTION: 'Deploy application',
    COMMAND_ACTION: deploy_function,
    COMMAND_REQUIRED_PARAMS: ['environment'],
    COMMAND_REQUIRE_BEFORE: ['build', 'test'],
    COMMAND_PHASE: PHASE_EXECUTION,
}
```

### Phases

Commands execute in phases (setup → cleanup → execution → teardown → end):

```python
from spafw37.constants.phase import *

spafw37.set_phases_order([
    PHASE_SETUP,
    PHASE_CLEANUP,
    PHASE_EXECUTION,
    PHASE_TEARDOWN,
    PHASE_END,
])
```

### Cycles

Repeat command sequences with loop control:

```python
from spafw37.constants.cycle import *

{
    COMMAND_NAME: 'process-all',
    COMMAND_CYCLE: {
        CYCLE_INIT: init_processing,
        CYCLE_LOOP: has_more_items,
        CYCLE_LOOP_START: prepare_next_item,
        CYCLE_END: finalize_processing,
        CYCLE_COMMANDS: ['validate', 'transform', 'save'],
    }
}
```

## Configuration

Access configuration values in your command actions:

```python
def my_command():
    # Get typed configuration values
    name = spafw37.get_config_str('name')
    count = spafw37.get_config_int('count')
    enabled = spafw37.get_config_bool('enabled')
    items = spafw37.get_config_list('items')
    
    # Set configuration values
    spafw37.set_config_value('status', 'processing')
```

Configuration can be:
- Set via command-line parameters
- Loaded from persistent config files (`config.json`)
- Saved to user config files (`--save-config`, `--load-config`)
- Managed at runtime within commands

## Logging

Built-in logging system with multiple levels:

```python
from spafw37 import core as spafw37

spafw37.log_trace('scope', 'Detailed trace information')
spafw37.log_debug('scope', 'Debug information')
spafw37.log_info('scope', 'General information')
spafw37.log_warning('scope', 'Warning message')
spafw37.log_error('scope', 'Error message')
```

Control logging via built-in parameters:
- `--no-logging` - Disable all logging
- `--verbose` - Enable verbose output
- `--log-dir` - Specify log directory

## Testing

Run the test suite:

```bash
pytest tests/ -v --cov=spafw37 --cov-report=term-missing
```

Requires 80% test coverage to pass.

## Requirements

- Python 3.7 or higher
- No external dependencies for core functionality
- Development dependencies: pytest, pytest-cov, typing_extensions

## Python 3.7 Compatibility

This framework is specifically designed for Python 3.7 compatibility:
- No type hints on function parameters or return types
- No walrus operator (`:=`)
- No positional-only parameters
- Compatible with Python 3.7.0+

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

Copyright (c) 2025 minouris

## CI/CD

The project uses GitHub Actions for continuous integration:

- **Test Workflow** - Runs on every push/PR to main/develop
- **Publish to TestPyPI** - Automatic deployment on push to main with version auto-increment

See [`.github/workflows/README.md`](.github/workflows/README.md) for details.

## Author

**Ciara Norrish** ([@minouris](https://github.com/minouris))

## Links

- **Repository:** https://github.com/minouris/spafw37
- **Issues:** https://github.com/minouris/spafw37/issues
- **TestPyPI:** https://test.pypi.org/project/spafw37/
- **Documentation:** [doc/README.md](doc/README.md)
- **Examples:** [examples/README.md](examples/README.md)
