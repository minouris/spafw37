# Phases

[← Commands Guide](commands.md) | [Index](README.md#documentation) | [Cycles Guide →](cycles.md)

## Table of Contents

- [Overview](#overview)
- [Phase Constants](#phase-constants)
- [Phase Lifecycle](#phase-lifecycle)
- [Setting Phase Order](#setting-phase-order)
- [Assigning Commands to Phases](#assigning-commands-to-phases)
- [Default Phase](#default-phase)
- [Best Practices](#best-practices)
- [Documentation](#documentation)

## Overview

Phases provide a structured way to organize command execution into distinct lifecycle stages ([see example](../examples/phases_basic.py)). Commands are assigned to phases, and the framework executes all commands in one phase before moving to the next. This ensures proper sequencing of setup, execution, and cleanup operations.

By default, all commands run in the `PHASE_EXECUTION` phase. You can customize the phase order and assign commands to specific phases to control execution flow.

## Phase Constants

### Phase Definitions

| Constant | Purpose |
|----------|---------|
| `PHASE_SETUP` | Initialize resources, establish connections, validate preconditions. Framework: help, load-config |
| `PHASE_CLEANUP` | Prepare environment, remove temporary artifacts, reset state |
| `PHASE_EXECUTION` | Run primary application logic and main operations |
| `PHASE_TEARDOWN` | Release resources, close connections, finalize operations. Framework: save-config |
| `PHASE_END` | Perform final shutdown tasks and reporting |

## Phase Lifecycle

The phase system executes commands in order through each configured phase:

1. **All commands in phase 1** execute (respecting dependencies)
2. **Phase 1 completes** - no more commands can be added
3. **All commands in phase 2** execute (respecting dependencies)
4. **Phase 2 completes** - no more commands can be added
5. Continue until all phases complete

Within each phase, commands execute in dependency order (via topological sort).

## Setting Phase Order

**By default, the framework uses all five phases** in the recommended order: SETUP → CLEANUP → EXECUTION → TEARDOWN → END. You only need to call `set_phases_order()` if you want to use a different subset or order of phases ([see examples](../examples/phases_custom_order.py)).

To customize which phases your application uses:

```python
from spafw37 import core as spafw37
from spafw37.constants.phase import PHASE_SETUP, PHASE_EXECUTION, PHASE_TEARDOWN

# Simple three-phase execution
spafw37.set_phases_order([PHASE_SETUP, PHASE_EXECUTION, PHASE_TEARDOWN])
```

You can also create custom phases with any names you choose ([see example](../examples/phases_custom.py)):

```python
# Define custom phase names for your application
PHASE_VALIDATE = "phase-validate"
PHASE_BUILD = "phase-build"
PHASE_TEST = "phase-test"
PHASE_DEPLOY = "phase-deploy"

# Set your custom phase order
spafw37.set_phases_order([PHASE_VALIDATE, PHASE_BUILD, PHASE_TEST, PHASE_DEPLOY])
```

**Important:** When creating completely custom phase orders, framework commands have explicit phase assignments:
- `help` command: `PHASE_SETUP` (`"phase-setup"`)
- `load-config` command: `PHASE_SETUP` (`"phase-setup"`)
- `save-config` command: `PHASE_TEARDOWN` (`"phase-teardown"`)

Your custom phase order **must** include phases with these exact string values, or framework commands will fail. The recommended approach is to alias the framework constants to custom names ([see phases_extended.py example](../examples/phases_extended.py)):

```python
from spafw37.constants.phase import PHASE_SETUP, PHASE_EXECUTION, PHASE_TEARDOWN

# Alias framework phases to custom names
PHASE_START = PHASE_SETUP      # Resolves to "phase-setup"
PHASE_RUN = PHASE_EXECUTION    # Resolves to "phase-execution"  
PHASE_FINISH = PHASE_TEARDOWN  # Resolves to "phase-teardown"

# Now you can use your custom names, but framework commands still work
spafw37.set_phases_order([PHASE_START, PHASE_VALIDATE, PHASE_BUILD, PHASE_RUN, PHASE_FINISH])
```

Or use any combination of the default phases:

```python
# Just execution phase (simplest)
from spafw37.constants.phase import PHASE_EXECUTION
spafw37.set_phases_order([PHASE_EXECUTION])

# Setup and main execution only
spafw37.set_phases_order([PHASE_SETUP, PHASE_EXECUTION])

# Extend default phases with custom phases
PHASE_VALIDATE = "phase-validate"
spafw37.set_phases_order([PHASE_SETUP, PHASE_VALIDATE, PHASE_EXECUTION, PHASE_TEARDOWN])

# Reset to default (all five phases)
from spafw37.constants.phase import PHASE_ORDER
spafw37.set_phases_order(PHASE_ORDER)
```

**Best Practice:** When adding custom phases, **extend** the default phases rather than completely replacing them. This ensures framework commands (which run in `PHASE_EXECUTION`) continue to work correctly. Insert your custom phases at appropriate points in the default order rather than creating an entirely new phase system.

**Important:** Call `set_phases_order()` early in your application initialization, before registering commands, to ensure phase queues are properly configured.

## Assigning Commands to Phases

Assign a command to a phase using the `COMMAND_PHASE` constant:

```python
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION, COMMAND_PHASE
from spafw37.constants.phase import PHASE_SETUP, PHASE_TEARDOWN

# Setup phase command
connect_cmd = {
    COMMAND_NAME: "connect-db",
    COMMAND_ACTION: connect_to_database,
    COMMAND_PHASE: PHASE_SETUP
}

# Teardown phase command
disconnect_cmd = {
    COMMAND_NAME: "disconnect-db",
    COMMAND_ACTION: disconnect_from_database,
    COMMAND_PHASE: PHASE_TEARDOWN
}
```

### Phase Execution Example

```python
from spafw37 import core as spafw37
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION, COMMAND_PHASE
from spafw37.constants.phase import PHASE_SETUP, PHASE_EXECUTION, PHASE_TEARDOWN

# Configure phases
spafw37.set_phases_order([PHASE_SETUP, PHASE_EXECUTION, PHASE_TEARDOWN])

# Setup phase: Initialize resources
setup_commands = [
    {
        COMMAND_NAME: "create-workspace",
        COMMAND_ACTION: create_temp_workspace,
        COMMAND_PHASE: PHASE_SETUP
    },
    {
        COMMAND_NAME: "download-assets",
        COMMAND_ACTION: download_required_assets,
        COMMAND_PHASE: PHASE_SETUP
    }
]

# Execution phase: Main work
execution_commands = [
    {
        COMMAND_NAME: "process-files",
        COMMAND_ACTION: process_data_files,
        COMMAND_PHASE: PHASE_EXECUTION
    }
]

# Teardown phase: Cleanup
teardown_commands = [
    {
        COMMAND_NAME: "archive-results",
        COMMAND_ACTION: save_output_archive,
        COMMAND_PHASE: PHASE_TEARDOWN
    },
    {
        COMMAND_NAME: "cleanup-workspace",
        COMMAND_ACTION: remove_temp_files,
        COMMAND_PHASE: PHASE_TEARDOWN
    }
]

spafw37.add_commands(setup_commands + execution_commands + teardown_commands)
```

When executed, this will run:
1. `create-workspace` and `download-assets` (SETUP phase)
2. `process-files` (EXECUTION phase)
3. `archive-results` and `cleanup-workspace` (TEARDOWN phase)

## Default Phase

Commands without an explicit `COMMAND_PHASE` are assigned to `PHASE_DEFAULT` (which equals `PHASE_EXECUTION`):

```python
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION, COMMAND_PHASE
from spafw37.constants.phase import PHASE_EXECUTION

# These two are equivalent
command1 = {
    COMMAND_NAME: "run-task",
    COMMAND_ACTION: run_task
    # No COMMAND_PHASE specified - defaults to PHASE_EXECUTION
}

command2 = {
    COMMAND_NAME: "run-task",
    COMMAND_ACTION: run_task,
    COMMAND_PHASE: PHASE_EXECUTION  # Explicit assignment
}
```

**The framework uses all five phases by default.** Commands without an explicit phase assignment will run in the EXECUTION phase, which comes after SETUP and CLEANUP but before TEARDOWN and END.

### Setting a Custom Default Phase

The default phase is `PHASE_EXECUTION`, which is where user commands run when they don't specify `COMMAND_PHASE`. Framework commands are explicitly assigned to specific phases:
- `help` and `load-config` run in `PHASE_SETUP`
- `save-config` runs in `PHASE_TEARDOWN`

When using custom phase names, you **must** ensure your phase order includes phases with the same string values as `PHASE_SETUP` and `PHASE_TEARDOWN`, or framework commands will fail.

**Recommended Approach:** Alias the framework phase constants to your custom names:

```python
from spafw37 import core as spafw37
from spafw37.constants.phase import PHASE_SETUP, PHASE_EXECUTION, PHASE_TEARDOWN

# Alias framework phases to custom names that make sense for your application
PHASE_START = PHASE_SETUP          # "phase-setup" - framework needs this
PHASE_VALIDATE = "phase-validate"  # Custom phase
PHASE_BUILD = "phase-build"        # Custom phase
PHASE_TEST = "phase-test"          # Custom phase
PHASE_RUN = PHASE_EXECUTION        # "phase-execution" - default for user commands
PHASE_FINISH = PHASE_TEARDOWN      # "phase-teardown" - framework needs this

# Set phase order using your custom names
# Framework commands work because the string values match PHASE_SETUP and PHASE_TEARDOWN
spafw37.set_phases_order([
    PHASE_START,     # Actually "phase-setup" - framework: help, load-config
    PHASE_VALIDATE,  # Custom: validation
    PHASE_BUILD,     # Custom: build
    PHASE_TEST,      # Custom: testing
    PHASE_RUN,       # Actually "phase-execution" - default for user commands
    PHASE_FINISH     # Actually "phase-teardown" - framework: save-config
])
```

**Alternative:** Use framework constants directly with custom phases:

```python
# Mix framework constants with custom phases
spafw37.set_phases_order([
    PHASE_SETUP,      # Framework: help, load-config
    PHASE_VALIDATE,   # Custom: validation
    PHASE_BUILD,      # Custom: build
    PHASE_TEST,       # Custom: testing
    PHASE_EXECUTION,  # Default: user commands without explicit phase
    PHASE_TEARDOWN    # Framework: save-config
])
```

**Critical:** Your phase order must include phases with these exact string values:
- `"phase-setup"` (the value of `PHASE_SETUP`) - required for help and load-config commands
- `"phase-teardown"` (the value of `PHASE_TEARDOWN`) - required for save-config command

If you omit these phases, framework commands will fail with a "Phase not recognized" error.

## Best Practices

### Choose Appropriate Phases

- **PHASE_SETUP**: Database connections, API authentication, resource allocation, configuration loading
- **PHASE_CLEANUP**: Remove temporary files, reset test data, clear caches before main work
- **PHASE_EXECUTION**: Core application logic, data processing, user-facing operations
- **PHASE_TEARDOWN**: Close connections, release locks, flush buffers, finalize outputs
- **PHASE_END**: Generate reports, send notifications, final logging

### Keep It Simple

For simple applications, you can use just the default phase and ignore the phase system entirely:

```python
from spafw37 import core as spafw37
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION

# Simple - commands run in EXECUTION phase by default
commands = [{COMMAND_NAME: "work", COMMAND_ACTION: do_work}]
spafw37.add_commands(commands)
```

For complex applications that need explicit setup/teardown sequencing, assign commands to specific phases:

```python
from spafw37 import core as spafw37
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION, COMMAND_PHASE
from spafw37.constants.phase import PHASE_SETUP, PHASE_EXECUTION, PHASE_TEARDOWN

commands = [
    {COMMAND_NAME: "init-db", COMMAND_ACTION: init_db, COMMAND_PHASE: PHASE_SETUP},
    {COMMAND_NAME: "process", COMMAND_ACTION: process, COMMAND_PHASE: PHASE_EXECUTION},
    {COMMAND_NAME: "close-db", COMMAND_ACTION: close_db, COMMAND_PHASE: PHASE_TEARDOWN}
]
spafw37.add_commands(commands)
```

### Dependencies Within Phases

Use `COMMAND_REQUIRED_COMMANDS` for dependencies within a phase. Dependencies across phases are handled automatically by phase order:

```python
# Within a phase - use dependencies
{
    COMMAND_NAME: "migrate-db",
    COMMAND_ACTION: migrate_schema,
    COMMAND_PHASE: PHASE_SETUP,
    COMMAND_REQUIRED_COMMANDS: ["connect-db"]  # Run after connect-db in same phase
}

# Across phases - phase order handles it
{
    COMMAND_NAME: "connect-db",
    COMMAND_PHASE: PHASE_SETUP  # Always runs before EXECUTION phase
}
{
    COMMAND_NAME: "query-db",
    COMMAND_PHASE: PHASE_EXECUTION  # No dependency needed - phase order ensures setup completes first
}
```

### Phase Completion

Once a phase completes, you cannot add more commands to it. The framework raises an error if you try to queue a command to a completed phase:

```python
from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_ACTION,
    COMMAND_PHASE,
    COMMAND_NEXT,
)
from spafw37.constants.phase import PHASE_SETUP, PHASE_EXECUTION

def execution_action():
    """Runs in PHASE_EXECUTION."""
    spafw37.output("Running execution...")

commands = [
    {
        COMMAND_NAME: 'setup-db',
        COMMAND_ACTION: lambda: spafw37.output("Setting up database"),
        COMMAND_PHASE: PHASE_SETUP,
    },
    {
        COMMAND_NAME: 'process',
        COMMAND_ACTION: execution_action,
        COMMAND_PHASE: PHASE_EXECUTION,
        # Bad - trying to queue a command to PHASE_SETUP after it's completed
        COMMAND_NEXT: ['setup-db']  # Error: PHASE_SETUP already finished
    }
]

spafw37.add_commands(commands)
spafw37.run_cli()
```

All commands must be registered upfront with `add_commands()` before calling `run_cli()`.

---

## Examples

Complete working examples demonstrating phase features:

- **[phases_basic.py](../examples/phases_basic.py)** - Using default phases (SETUP, CLEANUP, EXECUTION, TEARDOWN, END) for organized command execution
- **[phases_custom_order.py](../examples/phases_custom_order.py)** - Customizing phase execution order with set_phases_order()
- **[phases_extended.py](../examples/phases_extended.py)** - **RECOMMENDED:** Extending default phases with custom phases while preserving framework functionality
- **[phases_custom.py](../examples/phases_custom.py)** - **ADVANCED:** Creating completely custom phases (use with caution - can break framework features)

See [examples/README.md](../examples/README.md) for a complete guide to all available examples.

---

## Documentation

- **[User Guide](README.md)** - Overview and quick start
- **[Parameters Guide](parameters.md)** - Parameter definition and usage
- **[Commands Guide](commands.md)** - Command system and dependencies
- **Phases Guide** - Multi-phase execution control
- **[Cycles Guide](cycles.md)** - Repeating command sequences
- **[Configuration Guide](configuration.md)** - Configuration management
- **[Logging Guide](logging.md)** - Built-in logging system
- **[API Reference](api-reference.md)** - Complete API documentation

---

[← Commands Guide](commands.md) | [Index](README.md#documentation) | [Cycles Guide →](cycles.md)
