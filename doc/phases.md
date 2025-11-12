# Phases

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

Phases provide a structured way to organize command execution into distinct lifecycle stages. Commands are assigned to phases, and the framework executes all commands in one phase before moving to the next. This ensures proper sequencing of setup, execution, and cleanup operations.

By default, all commands run in the `PHASE_EXECUTION` phase. You can customize the phase order and assign commands to specific phases to control execution flow.

## Phase Constants

### Phase Definitions

| Constant | Value | Purpose |
|----------|-------|---------|
| `PHASE_SETUP` | `"phase-setup"` | Initialize resources, establish connections, validate preconditions |
| `PHASE_CLEANUP` | `"phase-cleanup"` | Prepare environment, remove temporary artifacts, reset state |
| `PHASE_EXECUTION` | `"phase-execution"` | Run primary application logic and main operations |
| `PHASE_TEARDOWN` | `"phase-teardown"` | Release resources, close connections, finalize operations |
| `PHASE_END` | `"phase-end"` | Perform final shutdown tasks and reporting |

### Configuration

| Constant | Value | Description |
|----------|-------|-------------|
| `PHASE_DEFAULT` | `PHASE_EXECUTION` | Default phase assigned to commands without explicit phase |
| `PHASE_ORDER` | `[PHASE_SETUP, PHASE_CLEANUP, PHASE_EXECUTION, PHASE_TEARDOWN, PHASE_END]` | Recommended execution order for all phases |

## Phase Lifecycle

The phase system executes commands in order through each configured phase:

1. **All commands in phase 1** execute (respecting dependencies)
2. **Phase 1 completes** - no more commands can be added
3. **All commands in phase 2** execute (respecting dependencies)
4. **Phase 2 completes** - no more commands can be added
5. Continue until all phases complete

Within each phase, commands execute in dependency order (via topological sort).

## Setting Phase Order

**By default, the framework uses all five phases** in the recommended order: SETUP → CLEANUP → EXECUTION → TEARDOWN → END. You only need to call `set_phases_order()` if you want to use a different subset or order of phases.

To customize which phases your application uses:

```python
from spafw37 import core as spafw37
from spafw37.constants.phase import PHASE_SETUP, PHASE_EXECUTION, PHASE_TEARDOWN

# Simple three-phase execution
spafw37.set_phases_order([PHASE_SETUP, PHASE_EXECUTION, PHASE_TEARDOWN])
```

You can use any combination of the available phases:

```python
# Just execution phase (simplest)
from spafw37.constants.phase import PHASE_EXECUTION
spafw37.set_phases_order([PHASE_EXECUTION])

# Setup and main execution only
spafw37.set_phases_order([PHASE_SETUP, PHASE_EXECUTION])

# Reset to default (all five phases)
from spafw37.constants.phase import PHASE_ORDER
spafw37.set_phases_order(PHASE_ORDER)
```

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
        COMMAND_NAME: "load-config",
        COMMAND_ACTION: load_configuration,
        COMMAND_PHASE: PHASE_SETUP
    },
    {
        COMMAND_NAME: "connect-api",
        COMMAND_ACTION: connect_to_api,
        COMMAND_PHASE: PHASE_SETUP
    }
]

# Execution phase: Main work
execution_commands = [
    {
        COMMAND_NAME: "process-data",
        COMMAND_ACTION: process_data,
        COMMAND_PHASE: PHASE_EXECUTION
    }
]

# Teardown phase: Cleanup
teardown_commands = [
    {
        COMMAND_NAME: "close-api",
        COMMAND_ACTION: close_api_connection,
        COMMAND_PHASE: PHASE_TEARDOWN
    },
    {
        COMMAND_NAME: "save-results",
        COMMAND_ACTION: save_results,
        COMMAND_PHASE: PHASE_TEARDOWN
    }
]

spafw37.add_commands(setup_commands + execution_commands + teardown_commands)
```

When executed, this will run:
1. `load-config` and `connect-api` (SETUP phase)
2. `process-data` (EXECUTION phase)
3. `close-api` and `save-results` (TEARDOWN phase)

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

Once a phase completes, you cannot add more commands to it. The framework raises an error if you try. Queue all necessary commands before execution begins:

```python
from spafw37 import core as spafw37

# Good - all commands registered before running
spafw37.add_commands(all_commands)
spafw37.run_cli()

# Bad - trying to queue commands after phase starts
spafw37.run_cli()
queue_command("late-setup")  # Error if SETUP phase already completed
```

## Documentation

- **[Parameters Guide](parameters.md)** - Parameter definition and usage
- **[Commands Guide](commands.md)** - Detailed command system documentation
- **[Configuration Guide](configuration.md)** - Configuration management
- **[Cycles Guide](cycles.md)** - Repeating command sequences
- **[Phases Guide](phases.md)** - Multi-phase execution control
- **[Logging Guide](logging.md)** - Built-in logging system
- **[API Reference](api-reference.md)** - Complete API documentation

---

**Previous:** [← Commands Guide](commands.md)  
**Next:** [Cycles Guide →](cycles.md)
