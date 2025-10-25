# spafw37

A minimal Python 3.7 framework for building command-line applications with configuration management, parameter parsing, and command execution capabilities.

## Features

- **Parameter Management**: Define typed parameters with aliases, defaults, and persistence
- **Command System**: Register commands with actions, dependencies, and execution phases
- **Configuration Store**: Centralized configuration accessible throughout your application
- **Command Sequencing**: Control execution order with dependencies and triggers
- **Phased Execution**: Organize commands into setup, execution, and teardown phases
- **Help System**: Automatic help generation for commands and parameters
- **Logging**: Built-in logging with trace, debug, info, warning, and error levels

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

For development with testing:
```bash
pip install -e .[dev]
pytest
```

## Quick Start

Here's a minimal application:

```python
from spafw37.config import set_config_file
from spafw37.param import add_params
from spafw37.command import add_commands
import spafw37.configure
from spafw37.config_consts import (
    PARAM_NAME, PARAM_DESCRIPTION, PARAM_ALIASES, PARAM_TYPE, PARAM_TYPE_TEXT,
    COMMAND_NAME, COMMAND_DESCRIPTION, COMMAND_ACTION
)

# Set the configuration file
set_config_file('myapp_config.json')

# Define parameters
params = [
    {
        PARAM_NAME: "input-file",
        PARAM_DESCRIPTION: "Input file to process",
        PARAM_ALIASES: ["--input", "-i"],
        PARAM_TYPE: PARAM_TYPE_TEXT
    }
]

# Define commands
def process_action():
    from spafw37.config import get_config_value
    input_file = get_config_value("input-file")
    print(f"Processing {input_file}")

commands = [
    {
        COMMAND_NAME: "process",
        COMMAND_DESCRIPTION: "Process the input file",
        COMMAND_ACTION: process_action
    }
]

# Register parameters and commands
add_params(params)
add_commands(commands)

# Handle command line arguments
if __name__ == "__main__":
    import sys
    import spafw37.cli as cli
    cli.handle_cli_args(sys.argv[1:])
```

Run it:
```bash
python myapp.py process --input myfile.txt
```

## Building Applications

### Defining Parameters

Parameters are defined as dictionaries with the following keys:

#### Parameter Definition Structure

```python
from spafw37.config_consts import (
    PARAM_NAME,           # Required: unique identifier
    PARAM_DESCRIPTION,    # Optional: description shown in help
    PARAM_ALIASES,        # Optional: CLI aliases (e.g., ["--param", "-p"])
    PARAM_TYPE,           # Optional: 'text', 'number', 'toggle', or 'list'
    PARAM_BIND_TO,        # Optional: config key name (defaults to PARAM_NAME)
    PARAM_DEFAULT,        # Optional: default value
    PARAM_PERSISTENCE,    # Optional: 'always' or 'never'
    PARAM_REQUIRED,       # Optional: whether parameter is required
    PARAM_SWITCH_LIST,    # Optional: list of mutually exclusive params
    PARAM_RUNTIME_ONLY,   # Optional: True if not persisted
    PARAM_GROUP           # Optional: group name for help display
)
```

#### Parameter Types

**Text Parameter** (default):
```python
{
    PARAM_NAME: "output-dir",
    PARAM_DESCRIPTION: "Output directory for results",
    PARAM_ALIASES: ["--output", "-o"],
    PARAM_TYPE: PARAM_TYPE_TEXT,
    PARAM_DEFAULT: "./output"
}
```

**Number Parameter**:
```python
{
    PARAM_NAME: "threads",
    PARAM_DESCRIPTION: "Number of threads to use",
    PARAM_ALIASES: ["--threads", "-t"],
    PARAM_TYPE: PARAM_TYPE_NUMBER,
    PARAM_DEFAULT: 4
}
```

**Toggle Parameter** (boolean flag):
```python
{
    PARAM_NAME: "verbose",
    PARAM_DESCRIPTION: "Enable verbose output",
    PARAM_ALIASES: ["--verbose", "-v"],
    PARAM_TYPE: PARAM_TYPE_TOGGLE,
    PARAM_DEFAULT: False
}
```

**List Parameter** (multiple values):
```python
{
    PARAM_NAME: "input-files",
    PARAM_DESCRIPTION: "Input files to process",
    PARAM_ALIASES: ["--input", "-i"],
    PARAM_TYPE: PARAM_TYPE_LIST
}
```

Usage (both syntaxes supported):
- Space-separated: `--input file1.txt file2.txt file3.txt`
- Repeated flags: `-i file1.txt -i file2.txt -i file3.txt`

#### Parameter Aliases

Aliases define how parameters are specified on the command line:

- **Long form**: `--parameter-name` or `--parameter-name=value`
- **Short form**: `-p` (requires space before value: `-p value`)

```python
PARAM_ALIASES: ["--input-file", "--input", "-i"]
```

#### Parameter Persistence

Control how parameters are saved and loaded:

```python
# Always save to persistent config
PARAM_PERSISTENCE: PARAM_PERSISTENCE_ALWAYS

# Never save to persistent config
PARAM_PERSISTENCE: PARAM_PERSISTENCE_NEVER

# Runtime-only (never persisted, not checked at queue start)
PARAM_RUNTIME_ONLY: True
```

#### Mutually Exclusive Parameters

Define parameters that cannot be used together:

```python
{
    PARAM_NAME: "verbose",
    PARAM_ALIASES: ["--verbose", "-v"],
    PARAM_TYPE: PARAM_TYPE_TOGGLE,
    PARAM_SWITCH_LIST: ["quiet", "silent"]  # Can't use with --quiet or --silent
}
```

#### Parameter Groups

Organize parameters in help display:

```python
{
    PARAM_NAME: "input-file",
    PARAM_DESCRIPTION: "Input file to process",
    PARAM_ALIASES: ["--input", "-i"],
    PARAM_TYPE: PARAM_TYPE_TEXT,
    PARAM_GROUP: "Input/Output Options"
}
```

### Defining Commands

Commands are defined as dictionaries with actions and metadata:

#### Command Definition Structure

```python
from spafw37.config_consts import (
    COMMAND_NAME,              # Required: command identifier
    COMMAND_DESCRIPTION,       # Optional: short description
    COMMAND_HELP,              # Optional: extended help text
    COMMAND_ACTION,            # Required: callable function
    COMMAND_REQUIRED_PARAMS,   # Optional: list of required param names
    COMMAND_GOES_BEFORE,       # Optional: sequencing constraint
    COMMAND_GOES_AFTER,        # Optional: sequencing constraint
    COMMAND_REQUIRE_BEFORE,    # Optional: auto-queue dependencies
    COMMAND_NEXT_COMMANDS,     # Optional: auto-queue successors
    COMMAND_TRIGGER_PARAM,     # Optional: param that triggers this command
    COMMAND_PHASE,             # Optional: execution phase
    COMMAND_FRAMEWORK          # Optional: True if framework command
)
```

#### Basic Command

```python
def build_action():
    print("Building project...")

{
    COMMAND_NAME: "build",
    COMMAND_DESCRIPTION: "Build the project",
    COMMAND_ACTION: build_action
}
```

#### Command with Required Parameters

```python
{
    COMMAND_NAME: "build",
    COMMAND_DESCRIPTION: "Build the project",
    COMMAND_ACTION: build_action,
    COMMAND_REQUIRED_PARAMS: ["build-type", "target"]
}
```

The framework will verify required parameters are set before execution and show an error with command-specific help if missing.

#### Command with Extended Help

```python
{
    COMMAND_NAME: "build",
    COMMAND_DESCRIPTION: "Build the project",
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
    COMMAND_REQUIRED_PARAMS: ["build-type", "target"]
}
```

### Command Sequencing and Dependencies

Control the execution order of commands using dependency constraints:

#### COMMAND_GOES_AFTER

Specifies that this command must run after other commands in the queue:

```python
{
    COMMAND_NAME: "test",
    COMMAND_DESCRIPTION: "Run tests",
    COMMAND_ACTION: test_action,
    COMMAND_GOES_AFTER: ["build"]  # test runs after build
}
```

If user queues: `build test`, execution order is: build → test  
If user queues: `test build`, execution order is still: build → test

#### COMMAND_GOES_BEFORE

Specifies that this command must run before other commands in the queue:

```python
{
    COMMAND_NAME: "setup",
    COMMAND_DESCRIPTION: "Setup environment",
    COMMAND_ACTION: setup_action,
    COMMAND_GOES_BEFORE: ["build", "test"]  # setup runs before build or test
}
```

#### COMMAND_REQUIRE_BEFORE

Automatically queues prerequisite commands if not already queued:

```python
{
    COMMAND_NAME: "test",
    COMMAND_DESCRIPTION: "Run tests",
    COMMAND_ACTION: test_action,
    COMMAND_REQUIRE_BEFORE: ["build"]  # Automatically queues 'build' if needed
}
```

If user queues only: `test`, the framework automatically queues: build → test

#### COMMAND_NEXT_COMMANDS

Automatically queues successor commands after this command runs:

```python
{
    COMMAND_NAME: "build",
    COMMAND_DESCRIPTION: "Build the project",
    COMMAND_ACTION: build_action,
    COMMAND_NEXT_COMMANDS: ["test"]  # Automatically queues 'test' after build
}
```

If user queues: `build`, the framework automatically queues: build → test

#### Combining Constraints

You can combine these constraints for complex workflows:

```python
{
    COMMAND_NAME: "deploy",
    COMMAND_DESCRIPTION: "Deploy to production",
    COMMAND_ACTION: deploy_action,
    COMMAND_REQUIRE_BEFORE: ["build", "test"],  # Needs build and test first
    COMMAND_NEXT_COMMANDS: ["notify"],          # Sends notification after
    COMMAND_REQUIRED_PARAMS: ["environment"]
}
```

Queue: `deploy --environment prod`  
Execution: build → test → deploy → notify

#### Circular Dependency Detection

The framework detects circular dependencies and raises a `ValueError`:

```python
# This will raise ValueError with circular dependency message:
cmd_a = {
    COMMAND_NAME: "cmd-a",
    COMMAND_ACTION: lambda: None,
    COMMAND_GOES_AFTER: ["cmd-b"]
}

cmd_b = {
    COMMAND_NAME: "cmd-b",
    COMMAND_ACTION: lambda: None,
    COMMAND_GOES_AFTER: ["cmd-a"]
}
```

### Command Triggers

Commands can be automatically queued when specific parameters are set:

```python
{
    COMMAND_NAME: "auto-format",
    COMMAND_DESCRIPTION: "Format code automatically",
    COMMAND_ACTION: format_action,
    COMMAND_TRIGGER_PARAM: "format"  # Triggers when 'format' param is set
}

# Parameter definition
{
    PARAM_NAME: "format",
    PARAM_DESCRIPTION: "Format code after processing",
    PARAM_ALIASES: ["--format", "-f"],
    PARAM_TYPE: PARAM_TYPE_TOGGLE
}
```

When user runs: `myapp process --format`, the framework automatically queues the `auto-format` command.

### Command Phases

Organize commands into execution phases for better control:

#### Available Phases

```python
from spafw37.config_consts import (
    PHASE_SETUP,      # Configuration and initialization
    PHASE_CLEANUP,    # Pre-execution cleanup
    PHASE_EXECUTION,  # Main execution (default)
    PHASE_TEARDOWN,   # Post-execution cleanup
    PHASE_END         # Final operations
)
```

#### Setting Phase Order

```python
from spafw37.command import set_phases_order
from spafw37.config_consts import (
    PHASE_SETUP,
    PHASE_EXECUTION,
    PHASE_TEARDOWN
)

set_phases_order([
    PHASE_SETUP,
    PHASE_EXECUTION,
    PHASE_TEARDOWN
])
```

#### Assigning Commands to Phases

```python
{
    COMMAND_NAME: "initialize",
    COMMAND_DESCRIPTION: "Initialize environment",
    COMMAND_ACTION: init_action,
    COMMAND_PHASE: PHASE_SETUP
}

{
    COMMAND_NAME: "build",
    COMMAND_DESCRIPTION: "Build project",
    COMMAND_ACTION: build_action,
    COMMAND_PHASE: PHASE_EXECUTION  # Default phase
}

{
    COMMAND_NAME: "cleanup",
    COMMAND_DESCRIPTION: "Clean up resources",
    COMMAND_ACTION: cleanup_action,
    COMMAND_PHASE: PHASE_TEARDOWN
}
```

Phases execute in order, and commands within each phase respect their dependencies.

### Configuration Management

Access and manage configuration values throughout your application:

#### Getting Configuration Values

```python
from spafw37.config import get_config_value

def my_action():
    input_file = get_config_value("input-file")
    verbose = get_config_value("verbose", False)  # With default
    print(f"Processing {input_file}")
```

#### Setting Configuration Values Programmatically

```python
from spafw37.config import set_config_value_by_name

set_config_value_by_name("output-dir", "./build")
```

#### Saving Configuration

The framework provides built-in commands for saving configuration:

```bash
# Save current configuration to file
myapp --output results --threads 8 save-user-config --save-config myconfig.json
```

#### Loading Configuration

```bash
# Load configuration from file
myapp --load-config myconfig.json process
```

Configuration precedence (highest to lowest):
1. Command-line parameters
2. Loaded configuration file
3. Persistent configuration (auto-saved)
4. Parameter defaults

### Complete Example

Here's a complete example showing all features:

```python
from spafw37.config import set_config_file, get_config_value
from spafw37.param import add_params
from spafw37.command import add_commands, set_phases_order
import spafw37.configure
from spafw37.config_consts import (
    PARAM_NAME, PARAM_DESCRIPTION, PARAM_ALIASES, PARAM_TYPE,
    PARAM_TYPE_TEXT, PARAM_TYPE_NUMBER, PARAM_TYPE_TOGGLE,
    PARAM_DEFAULT, PARAM_GROUP, PARAM_REQUIRED,
    COMMAND_NAME, COMMAND_DESCRIPTION, COMMAND_HELP, COMMAND_ACTION,
    COMMAND_REQUIRED_PARAMS, COMMAND_GOES_AFTER, COMMAND_REQUIRE_BEFORE,
    COMMAND_NEXT_COMMANDS, COMMAND_TRIGGER_PARAM, COMMAND_PHASE,
    PHASE_SETUP, PHASE_EXECUTION, PHASE_TEARDOWN
)

# Configure
set_config_file('buildtool_config.json')
set_phases_order([PHASE_SETUP, PHASE_EXECUTION, PHASE_TEARDOWN])

# Define parameters
params = [
    {
        PARAM_NAME: "source-dir",
        PARAM_DESCRIPTION: "Source code directory",
        PARAM_ALIASES: ["--source", "-s"],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DEFAULT: "./src",
        PARAM_GROUP: "Paths"
    },
    {
        PARAM_NAME: "build-dir",
        PARAM_DESCRIPTION: "Build output directory",
        PARAM_ALIASES: ["--build-dir", "-b"],
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_DEFAULT: "./build",
        PARAM_GROUP: "Paths"
    },
    {
        PARAM_NAME: "optimization",
        PARAM_DESCRIPTION: "Optimization level (0-3)",
        PARAM_ALIASES: ["--optimize", "-O"],
        PARAM_TYPE: PARAM_TYPE_NUMBER,
        PARAM_DEFAULT: 2,
        PARAM_GROUP: "Build Options"
    },
    {
        PARAM_NAME: "verbose",
        PARAM_DESCRIPTION: "Enable verbose output",
        PARAM_ALIASES: ["--verbose", "-v"],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_DEFAULT: False,
        PARAM_GROUP: "General"
    },
    {
        PARAM_NAME: "run-tests",
        PARAM_DESCRIPTION: "Run tests after build",
        PARAM_ALIASES: ["--test"],
        PARAM_TYPE: PARAM_TYPE_TOGGLE,
        PARAM_DEFAULT: False
    }
]

# Define command actions
def setup_action():
    build_dir = get_config_value("build-dir")
    print(f"Creating build directory: {build_dir}")

def build_action():
    source_dir = get_config_value("source-dir")
    optimization = get_config_value("optimization")
    print(f"Building from {source_dir} with -O{optimization}")

def test_action():
    print("Running tests...")

def cleanup_action():
    print("Cleaning up temporary files...")

def auto_test_action():
    print("Auto-running tests after build...")

# Define commands
commands = [
    {
        COMMAND_NAME: "setup",
        COMMAND_DESCRIPTION: "Setup build environment",
        COMMAND_ACTION: setup_action,
        COMMAND_PHASE: PHASE_SETUP
    },
    {
        COMMAND_NAME: "build",
        COMMAND_DESCRIPTION: "Build the project",
        COMMAND_HELP: "Compiles source code and generates output",
        COMMAND_ACTION: build_action,
        COMMAND_REQUIRE_BEFORE: ["setup"],  # Auto-queues setup
        COMMAND_REQUIRED_PARAMS: ["source-dir", "build-dir"],
        COMMAND_PHASE: PHASE_EXECUTION
    },
    {
        COMMAND_NAME: "test",
        COMMAND_DESCRIPTION: "Run test suite",
        COMMAND_ACTION: test_action,
        COMMAND_GOES_AFTER: ["build"],  # Runs after build if both queued
        COMMAND_PHASE: PHASE_EXECUTION
    },
    {
        COMMAND_NAME: "cleanup",
        COMMAND_DESCRIPTION: "Clean temporary files",
        COMMAND_ACTION: cleanup_action,
        COMMAND_PHASE: PHASE_TEARDOWN
    },
    {
        COMMAND_NAME: "auto-test",
        COMMAND_DESCRIPTION: "Automatically run tests",
        COMMAND_ACTION: auto_test_action,
        COMMAND_TRIGGER_PARAM: "run-tests",  # Triggered by --test flag
        COMMAND_GOES_AFTER: ["build"]
    }
]

# Register
add_params(params)
add_commands(commands)

# Main entry point
if __name__ == "__main__":
    import sys
    import spafw37.cli as cli
    from spafw37.command import CommandParameterError
    from spafw37.help import display_all_help, display_command_help
    
    try:
        cli.handle_cli_args(sys.argv[1:])
    except CommandParameterError as e:
        print(f"Error: {e}")
        print()
        if e.command_name:
            display_command_help(e.command_name)
        else:
            display_all_help()
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        print()
        display_all_help()
        sys.exit(1)
```

Example usage:

```bash
# Simple build
python buildtool.py build

# Build with custom optimization
python buildtool.py build -O 3

# Build and test (manual)
python buildtool.py build test

# Build with auto-test (triggered)
python buildtool.py build --test

# Save configuration
python buildtool.py -O 3 --build-dir ./release save-user-config --save-config release.json

# Load and build
python buildtool.py --load-config release.json build
```

## Advanced Topics

### Error Handling

The framework provides specific exceptions:

- `CommandParameterError`: Missing required parameters for a command (subclass of ValueError)
- `ValueError`: General validation errors including circular dependencies
- `KeyError`: Command or parameter not found in registry

### Help System

The framework automatically generates help:

```bash
# General help
python myapp.py help

# Command-specific help
python myapp.py help build
```

### Logging

Built-in logging with framework-provided parameters:

```python
from spafw37.command import log_info, log_debug, log_trace, log_warning, log_error

def my_action():
    log_info("Starting processing")
    log_debug("Debug information")
    log_trace("Detailed trace")
```

Enable with command-line flags:
```bash
python myapp.py --verbose build  # Enable verbose logging
python myapp.py --trace build    # Enable trace logging
```

## API Reference

### Core Modules

- `spafw37.param`: Parameter definition and management
- `spafw37.command`: Command registration and execution
- `spafw37.config`: Configuration store access
- `spafw37.cli`: Command-line argument parsing
- `spafw37.help`: Help system
- `spafw37.logging`: Logging utilities

See the [SPEC.md](doc/SPEC.md) for detailed specifications.

## Testing

Run the test suite:

```bash
pytest tests/ -v --cov=spafw37 --cov-report=term-missing
```

## License

MIT License
