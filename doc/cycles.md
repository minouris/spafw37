# Cycles Guide

[← Phases Guide](phases.md) | [Index](README.md#documentation) | [Configuration Guide →](configuration.md)

## Table of Contents

- [Overview](#overview)
- [Cycle Constants](#cycle-constants)
- [Defining a Cycle](#defining-a-cycle)
- [Cycle Lifecycle](#cycle-lifecycle)
- [Parameter Validation](#parameter-validation)
- [Nested Cycles](#nested-cycles)
- [Command Invocability](#command-invocability)
- [Best Practices](#best-practices)
- [Documentation](#documentation)

## Overview

Cycles enable you to execute a sequence of commands repeatedly in a loop ([see example](../examples/cycles_basic.py)). A cycle is attached to a parent command and consists of:

- **Initialisation function**: Set up resources before the loop starts
- **Loop condition function**: Called before each iteration; returns `True` to continue, `False` to stop
- **Cycle commands**: List of commands to execute each iteration (respecting dependencies)
- **Finalisation function**: Clean up resources after the loop completes

Cycles support nesting (default: 5 levels deep, configurable via `set_max_cycle_nesting_depth()`), automatic parameter validation across all cycle commands, and full integration with the command dependency system.

## Cycle Constants

### Cycle Definition

| Constant | Description |
|----------|-------------|
| `CYCLE_NAME` | Name of the cycle for logging and debugging |
| `CYCLE_INIT` | Function to initialise resources before loop starts |
| `CYCLE_LOOP` | Function that returns `True` to continue loop, `False` to exit |
| `CYCLE_LOOP_START` | Function to prepare data for the iteration (runs after `CYCLE_LOOP` returns `True`) |
| `CYCLE_END` | Function to finalise resources and perform cleanup after loop |
| `CYCLE_COMMANDS` | List of command definitions or names to execute each iteration |

### Command Integration

| Constant | Description |
|----------|-------------|
| `COMMAND_CYCLE` | Attaches a cycle definition to a command |
| `COMMAND_INVOCABLE` | Set to `False` for cycle-internal commands (not CLI-accessible) |

## Defining a Cycle

A cycle is attached to a parent command using the `COMMAND_CYCLE` key ([see example](../examples/cycles_basic.py)). The cycle definition includes initialisation, loop condition, finalisation functions, and the list of commands to execute each iteration.

### Basic Structure

```python
from spafw37 import core as spafw37
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION, COMMAND_CYCLE
from spafw37.constants.param import PARAM_NAME, PARAM_TYPE, PARAM_TYPE_TEXT, PARAM_RUNTIME_ONLY
from spafw37.constants.cycle import (
    CYCLE_NAME,
    CYCLE_INIT,
    CYCLE_LOOP,
    CYCLE_END,
    CYCLE_COMMANDS
)

# Define runtime params for cycle state
params = [
    {
        PARAM_NAME: 'file-list',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True  # Not exposed to CLI
    },
    {
        PARAM_NAME: 'file-index',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True
    },
    {
        PARAM_NAME: 'current-file',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True
    }
]

spafw37.add_params(params)

commands = [
    {
        COMMAND_NAME: 'parent-command',
        COMMAND_CYCLE: {
            CYCLE_NAME: 'my-cycle',
            CYCLE_INIT: init_function,
            CYCLE_LOOP: loop_condition_function,
            CYCLE_END: finalize_function,
            CYCLE_COMMANDS: [...]
        }
    }
]
```

### State Management

Cycle functions share state to exchange data between control functions and commands. **Use runtime parameters (config system) for state management** - this allows the framework to manage structure and save state when needed.

First, define runtime-only parameters for your cycle state:

```python
params = [
    {
        PARAM_NAME: 'file-list',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True
    },
    {
        PARAM_NAME: 'file-index',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True
    },
    {
        PARAM_NAME: 'current-file',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True
    }
]

spafw37.add_params(params)
```

Then use these parameters in your cycle functions:

```python
def init_files():
    spafw37.set_config_value('file-list', ['file1.txt', 'file2.txt', 'file3.txt'])
    spafw37.set_config_value('file-index', 0)

def has_more_files():
    file_list = spafw37.get_config_value('file-list')
    file_index = spafw37.get_config_value('file-index')
    return file_index < len(file_list)

def prepare_next_file():
    file_list = spafw37.get_config_value('file-list')
    file_index = spafw37.get_config_value('file-index')
    spafw37.set_config_value('current-file', file_list[file_index])

def finalize_files():
    file_index = spafw37.get_config_value('file-index')
    spafw37.output(f"Completed {file_index} files")

def process_file():
    current_file = spafw37.get_config_value('current-file')
    # ... process current_file ...
    file_index = spafw37.get_config_value('file-index')
    spafw37.set_config_value('file-index', file_index + 1)
```

**Only use module-level variables for truly local state** that shouldn't be saved or shared:

```python
_iteration_count = 0  # Module-private

def init_cycle():
    global _iteration_count
    _iteration_count = 0
```

### Initialisation Function

Sets up resources and state before the loop begins:

```python
def init_files():
    spafw37.set_config_value('file-list', ['file1.txt', 'file2.txt', 'file3.txt'])
    spafw37.set_config_value('file-index', 0)
```

### Loop Condition Function

Checks if iteration should continue:

```python
def has_more_files():
    file_list = spafw37.get_config_value('file-list')
    file_index = spafw37.get_config_value('file-index')
    return file_index < len(file_list)
```

### Loop Start Function

Prepares data for the next iteration ([see example](../examples/cycles_loop_start.py)):

```python
def prepare_next_file():
    file_list = spafw37.get_config_value('file-list')
    file_index = spafw37.get_config_value('file-index')
    spafw37.set_config_value('current-file', file_list[file_index])
```

### Finalisation Function

Cleans up resources and reports results after the loop completes:

```python
def finalize_files():
    file_index = spafw37.get_config_value('file-index')
    spafw37.output(f"Completed {file_index} files")
```

### Cycle Commands

Define the commands that execute each iteration:

```python
def process_file():
    current_file = spafw37.get_config_value('current-file')
    # ... process current_file ...
    file_index = spafw37.get_config_value('file-index')
    spafw37.set_config_value('file-index', file_index + 1)

cycle_commands = [
    {
        COMMAND_NAME: 'process-file',
        COMMAND_ACTION: process_file
    }
]
```

### Complete Example

Putting it all together:

```python
from spafw37 import core as spafw37
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION, COMMAND_CYCLE
from spafw37.constants.param import PARAM_NAME, PARAM_TYPE, PARAM_TYPE_TEXT, PARAM_RUNTIME_ONLY
from spafw37.constants.cycle import (
    CYCLE_NAME,
    CYCLE_INIT,
    CYCLE_LOOP,
    CYCLE_LOOP_START,
    CYCLE_END,
    CYCLE_COMMANDS
)

# Define runtime params for cycle state (not exposed to CLI)
params = [
    {
        PARAM_NAME: 'file-list',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True
    },
    {
        PARAM_NAME: 'file-index',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True
    },
    {
        PARAM_NAME: 'current-file',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True
    }
]

spafw37.add_params(params)

# Cycle control functions
def init_files():
    spafw37.set_config_value('file-list', ['file1.txt', 'file2.txt', 'file3.txt'])
    spafw37.set_config_value('file-index', 0)

def has_more_files():
    file_list = spafw37.get_config_value('file-list')
    file_index = spafw37.get_config_value('file-index')
    return file_index < len(file_list)

def prepare_next_file():
    file_list = spafw37.get_config_value('file-list')
    file_index = spafw37.get_config_value('file-index')
    spafw37.set_config_value('current-file', file_list[file_index])

def finalize_files():
    file_index = spafw37.get_config_value('file-index')
    spafw37.output(f"Completed {file_index} files")

def process_file():
    current_file = spafw37.get_config_value('current-file')
    # ... process current_file ...
    file_index = spafw37.get_config_value('file-index')
    spafw37.set_config_value('file-index', file_index + 1)

# Define parent command with cycle
commands = [
    {
        COMMAND_NAME: 'process-all-files',
        COMMAND_CYCLE: {
            CYCLE_NAME: 'file-processing',
            CYCLE_INIT: init_files,
            CYCLE_LOOP: has_more_files,
            CYCLE_LOOP_START: prepare_next_file,
            CYCLE_END: finalize_files,
            CYCLE_COMMANDS: [
                {
                    COMMAND_NAME: 'process-file',
                    COMMAND_ACTION: process_file
                }
            ]
        }
    }
]

spafw37.add_commands(commands)
```

## Cycle Lifecycle

When a cycle command executes:

1. **Parent command action runs** (if defined - optional)
2. **Initialisation function runs** (`CYCLE_INIT`)
3. **Loop begins**:
   - Call loop condition function (`CYCLE_LOOP`) - returns `True` to continue or `False` to stop
   - If `True`: Run loop start function (`CYCLE_LOOP_START`) to prepare data for iteration
   - Execute all cycle commands (respecting dependencies)
   - Repeat from step 1
   - If `False`: Exit loop
4. **Finalisation function runs** (`CYCLE_END`)
5. **Execution continues** to next command in queue

The `CYCLE_LOOP` function checks whether to continue iterating, while `CYCLE_LOOP_START` prepares the data for that iteration (e.g., sets current file path, fetches next database record, advances to next batch).

### Execution Flow Example

```python
from spafw37 import core as spafw37
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION, COMMAND_CYCLE
from spafw37.constants.param import PARAM_NAME, PARAM_TYPE, PARAM_TYPE_TEXT, PARAM_RUNTIME_ONLY
from spafw37.constants.cycle import (
    CYCLE_NAME,
    CYCLE_INIT,
    CYCLE_LOOP,
    CYCLE_LOOP_START,
    CYCLE_END,
    CYCLE_COMMANDS
)

# Define runtime params for cycle state
params = [
    {
        PARAM_NAME: 'iteration-count',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True
    },
    {
        PARAM_NAME: 'max-iterations',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True
    }
]

spafw37.add_params(params)

def init_cycle():
    spafw37.set_config_value('iteration-count', 0)
    spafw37.set_config_value('max-iterations', 3)
    spafw37.output("Cycle initialised")

def should_continue():
    iteration_count = spafw37.get_config_value('iteration-count')
    max_iterations = spafw37.get_config_value('max-iterations')
    return iteration_count < max_iterations

def finalize_cycle():
    iteration_count = spafw37.get_config_value('iteration-count')
    spafw37.output(f"Cycle completed after {iteration_count} iterations")

def do_work():
    iteration_count = spafw37.get_config_value('iteration-count')
    iteration_count += 1
    spafw37.set_config_value('iteration-count', iteration_count)
    spafw37.output(f"Iteration {iteration_count}: doing work")

commands = [
    {
        COMMAND_NAME: 'run-cycle',
        COMMAND_CYCLE: {
            CYCLE_NAME: 'work-cycle',
            CYCLE_INIT: init_cycle,
            CYCLE_LOOP: should_continue,
            CYCLE_END: finalize_cycle,
            CYCLE_COMMANDS: [
                {
                    COMMAND_NAME: 'work',
                    COMMAND_ACTION: do_work
                }
            ]
        }
    }
]

spafw37.add_commands(commands)
```

Output when `run-cycle` executes:
```
Cycle initialised
Iteration 1: doing work
Iteration 2: doing work
Iteration 3: doing work
Cycle completed after 3 iterations
```

## Parameter Validation

The framework **validates all cycle parameters upfront** before executing the parent command. Parameters from all cycle commands (including nested cycles) are merged into the parent command's `COMMAND_REQUIRED_PARAMS`.

```python
from spafw37 import core as spafw37
from spafw37.constants.command import (
    COMMAND_NAME,
    COMMAND_ACTION,
    COMMAND_REQUIRED_PARAMS,
    COMMAND_CYCLE
)
from spafw37.constants.cycle import CYCLE_NAME, CYCLE_LOOP, CYCLE_COMMANDS

# Cycle command requires 'input-file' parameter
cycle_commands = [
    {
        COMMAND_NAME: 'process-input',
        COMMAND_ACTION: lambda: spafw37.output("Processing"),
        COMMAND_REQUIRED_PARAMS: ['input-file']  # Required param
    }
]

# Parent command automatically inherits 'input-file' requirement
commands = [
    {
        COMMAND_NAME: 'batch-process',
        COMMAND_REQUIRED_PARAMS: ['batch-size'],  # Parent's own params
        COMMAND_CYCLE: {
            CYCLE_NAME: 'batch-cycle',
            CYCLE_LOOP: lambda: False,
            CYCLE_COMMANDS: cycle_commands
            # 'input-file' is automatically merged into parent's required params
        }
    }
]

spafw37.add_commands(commands)

# Running 'batch-process' requires both 'batch-size' AND 'input-file'
# Validation happens before execution starts
```

This ensures that if any cycle command needs a parameter, the framework validates it before the cycle begins executing.

## Nested Cycles

Cycles can be nested up to **5 levels deep by default** ([see example](../examples/cycles_nested.py)). The nesting depth limit can be configured using `spafw37.set_max_cycle_nesting_depth(depth)` if you need deeper nesting. Nested cycles work just like regular cycles - they have their own init/loop/end functions and command lists.

```python
from spafw37 import core as spafw37
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION, COMMAND_CYCLE
from spafw37.constants.param import PARAM_NAME, PARAM_TYPE, PARAM_TYPE_TEXT, PARAM_RUNTIME_ONLY
from spafw37.constants.cycle import (
    CYCLE_NAME,
    CYCLE_INIT,
    CYCLE_LOOP,
    CYCLE_LOOP_START,
    CYCLE_END,
    CYCLE_COMMANDS
)

# Define runtime params for nested cycle state
params = [
    {PARAM_NAME: 'batches', PARAM_TYPE: PARAM_TYPE_TEXT, PARAM_RUNTIME_ONLY: True},
    {PARAM_NAME: 'batch-index', PARAM_TYPE: PARAM_TYPE_TEXT, PARAM_RUNTIME_ONLY: True},
    {PARAM_NAME: 'items', PARAM_TYPE: PARAM_TYPE_TEXT, PARAM_RUNTIME_ONLY: True},
    {PARAM_NAME: 'item-index', PARAM_TYPE: PARAM_TYPE_TEXT, PARAM_RUNTIME_ONLY: True}
]

spafw37.add_params(params)

# Outer cycle functions
def init_batches():
    # Initialise batch list and index
    spafw37.set_config_value('batches', ['batch-A', 'batch-B'])
    spafw37.set_config_value('batch-index', 0)

def has_more_batches():
    # Check if more batches remain
    batches = spafw37.get_config_value('batches')
    batch_index = spafw37.get_config_value('batch-index')
    return batch_index < len(batches)

def prepare_next_batch():
    # Set current batch and increment index
    batch_index = spafw37.get_config_value('batch-index')
    spafw37.set_config_value('batch-index', batch_index + 1)

# Inner cycle functions
def init_items():
    # Initialise items for current batch
    spafw37.set_config_value('items', ['item1', 'item2'])
    spafw37.set_config_value('item-index', 0)

def has_more_items():
    # Check if more items remain
    items = spafw37.get_config_value('items')
    item_index = spafw37.get_config_value('item-index')
    return item_index < len(items)

def prepare_next_item():
    # Increment item index
    item_index = spafw37.get_config_value('item-index')
    spafw37.set_config_value('item-index', item_index + 1)

def process_item():
    # Process current item
    item_index = spafw37.get_config_value('item-index')
    spafw37.output(f"Processing item {item_index}")

# Top-level command with nested cycles
commands = [
    {
        COMMAND_NAME: 'process-all',
        COMMAND_CYCLE: {
            CYCLE_NAME: 'batch-cycle',
            CYCLE_INIT: init_batches,
            CYCLE_LOOP: has_more_batches,
            CYCLE_LOOP_START: prepare_next_batch,
            CYCLE_COMMANDS: [
                {
                    COMMAND_NAME: 'process-batch-items',
                    COMMAND_CYCLE: {
                        CYCLE_NAME: 'item-cycle',
                        CYCLE_INIT: init_items,
                        CYCLE_LOOP: has_more_items,
                        CYCLE_LOOP_START: prepare_next_item,
                        CYCLE_COMMANDS: [
                            {
                                COMMAND_NAME: 'process-item',
                                COMMAND_ACTION: process_item
                            }
                        ]
                    }
                }
            ]
        }
    }
]

spafw37.add_commands(commands)
```

## Command Invocability

**Cycle commands are not invocable from the CLI.** The framework automatically marks them with `COMMAND_INVOCABLE: False`. They only execute as part of their parent cycle.

```python
# This cycle command cannot be called directly from CLI
cycle_commands = [
    {
        COMMAND_NAME: 'internal-work',
        COMMAND_ACTION: do_internal_work
        # Automatically marked as COMMAND_INVOCABLE: False
    }
]

commands = [
    {
        COMMAND_NAME: 'run-cycle',  # This IS invocable from CLI
        COMMAND_CYCLE: {
            CYCLE_NAME: 'work-cycle',
            CYCLE_LOOP: lambda: False,
            CYCLE_COMMANDS: cycle_commands
        }
    }
]
```

```bash
# Valid - runs the cycle which internally executes 'internal-work'
python main.py run-cycle

# Invalid - cycle commands cannot be invoked directly
python main.py internal-work  # Error: command not found
```

## Best Practices

### Use Cycles for Iteration

Cycles are ideal when you need to:
- Process multiple files or database records
- Retry operations until success
- Implement polling or monitoring loops
- Batch process data in chunks

```python
# Good - cycle handles iteration
{
    COMMAND_NAME: 'process-files',
    COMMAND_CYCLE: {
        CYCLE_NAME: 'file-loop',
        CYCLE_LOOP: has_more_files,
        CYCLE_COMMANDS: [...]
    }
}

# Avoid - manually calling commands multiple times
# (Defeats the purpose of the cycle system)
```

### Keep Init/Loop/End Functions Simple

Each function should have a single responsibility:

```python
# Good - focused functions
def init_processing():
    """Load file list and reset counter."""
    load_files()
    reset_counter()

def has_more_files():
    """Check if more files remain."""
    return current_index < len(file_list)

def finalize_processing():
    """Report results and cleanup."""
    print_summary()
    cleanup_temp_files()

# Avoid - doing too much in one function
def init_processing():
    load_files()
    validate_files()
    setup_output_dirs()
    initialize_database()
    configure_logging()
    # Too many responsibilities!

# Better - use CYCLE_INIT for state setup, dependency commands for other tasks
def init_state():
    """Initialise cycle state only."""
    spafw37.set_config_value('files', [])
    spafw37.set_config_value('file-index', 0)

# Break complex initialisation into dependency commands
commands = [
    {
        COMMAND_NAME: 'setup-output',
        COMMAND_ACTION: setup_output_dirs
    },
    {
        COMMAND_NAME: 'init-db',
        COMMAND_ACTION: initialize_database,
        COMMAND_GOES_AFTER: ['setup-output']
    },
    {
        COMMAND_NAME: 'process-files',
        COMMAND_ACTION: lambda: None,
        COMMAND_GOES_AFTER: ['init-db'],  # Runs after setup is complete
        COMMAND_CYCLE: {
            CYCLE_INIT: init_state,  # Just initializes cycle state
            CYCLE_LOOP: has_more_files,
            CYCLE_LOOP_START: load_next_file,
            CYCLE_END: finalize_processing,
            CYCLE_COMMANDS: [
                {COMMAND_NAME: 'validate', COMMAND_ACTION: validate_file},
                {COMMAND_NAME: 'process', COMMAND_ACTION: process_file}
            ]
        }
    }
]
```

### Manage State Clearly

**Use the config/runtime params system for cycle state** - this allows the framework to manage structure and save state when needed. Define runtime-only parameters for internal cycle state:

```python
from spafw37 import core as spafw37
from spafw37.constants.param import PARAM_NAME, PARAM_TYPE, PARAM_TYPE_TEXT, PARAM_RUNTIME_ONLY
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION

# Define runtime params for internal cycle state
params = [
    {
        PARAM_NAME: 'batches',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True  # Not exposed to CLI
    },
    {
        PARAM_NAME: 'batch-index',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True
    },
    {
        PARAM_NAME: 'current-batch',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True
    },
    {
        PARAM_NAME: 'processing-results',
        PARAM_TYPE: PARAM_TYPE_TEXT,
        PARAM_RUNTIME_ONLY: True
    }
]

spafw37.add_params(params)

def init_processing():
    """Initialise processing state."""
    batches = load_batches()
    spafw37.set_config_value('batches', batches)
    spafw37.set_config_value('batch-index', 0)
    spafw37.set_config_value('processing-results', [])

def has_more_batches():
    """Check if more batches remain."""
    batches = spafw37.get_config_value('batches')
    batch_index = spafw37.get_config_value('batch-index')
    return batch_index < len(batches)

def prepare_next_batch():
    """Prepare next batch for processing."""
    batches = spafw37.get_config_value('batches')
    batch_index = spafw37.get_config_value('batch-index')
    current_batch = batches[batch_index]
    spafw37.set_config_value('current-batch', current_batch)

def process_batch():
    """Process the current batch."""
    current_batch = spafw37.get_config_value('current-batch')
    results = spafw37.get_config_value('processing-results')
    batch_index = spafw37.get_config_value('batch-index')
    
    result = perform_processing(current_batch)
    results.append(result)
    
    spafw37.set_config_value('processing-results', results)
    spafw37.set_config_value('batch-index', batch_index + 1)
```

**Only use module-level variables for truly local state** that shouldn't be saved or shared outside the module. Never use `global` keyword at function scope - declare variables at module level instead:

```python
# Acceptable for module-private counters/flags only
_iteration_count = 0  # Leading underscore indicates module-private

def init_cycle():
    """Initialise cycle state."""
    global _iteration_count
    _iteration_count = 0
```

### Dependencies Within Cycles

Commands within a cycle can have dependencies using `COMMAND_GOES_AFTER`, `COMMAND_GOES_BEFORE`, etc. Dependencies are resolved each iteration:

```python
from spafw37 import core as spafw37
from spafw37.constants.command import COMMAND_NAME, COMMAND_ACTION, COMMAND_GOES_AFTER

cycle_commands = [
    {
        COMMAND_NAME: 'load-data',
        COMMAND_ACTION: load_data
    },
    {
        COMMAND_NAME: 'validate-data',
        COMMAND_ACTION: validate_data,
        COMMAND_GOES_AFTER: ['load-data']  # Runs after load-data each iteration
    },
    {
        COMMAND_NAME: 'process-data',
        COMMAND_ACTION: process_data,
        COMMAND_GOES_AFTER: ['validate-data']  # Runs after validate-data
    }
]
```

### Phase Consistency

**All commands in a cycle must be in the same phase as the parent command.** The framework validates this when you register the cycle.

```python
from spafw37.constants.phase import PHASE_SETUP, PHASE_EXECUTION

# Valid - all in EXECUTION phase (default)
{
    COMMAND_NAME: 'process-cycle',
    # COMMAND_PHASE defaults to PHASE_EXECUTION
    COMMAND_CYCLE: {
        CYCLE_COMMANDS: [
            {COMMAND_NAME: 'work', COMMAND_ACTION: work}
            # Also defaults to PHASE_EXECUTION
        ]
    }
}

# Invalid - phase mismatch
{
    COMMAND_NAME: 'setup-cycle',
    COMMAND_PHASE: PHASE_SETUP,
    COMMAND_CYCLE: {
        CYCLE_COMMANDS: [
            {
                COMMAND_NAME: 'work',
                COMMAND_ACTION: work,
                COMMAND_PHASE: PHASE_EXECUTION  # Error: different phase!
            }
        ]
    }
}
```

### Optional Parent Action

The parent command's `COMMAND_ACTION` is optional when using a cycle. Use it only if you need setup that runs before `CYCLE_INIT`:

```python
# Action runs before cycle init
{
    COMMAND_NAME: 'process-with-setup',
    COMMAND_ACTION: lambda: spafw37.output("Preparing..."),  # Runs first
    COMMAND_CYCLE: {
        CYCLE_INIT: init_cycle,  # Runs second
        # ...
    }
}

# No action - cycle does everything
{
    COMMAND_NAME: 'process-simple',
    COMMAND_CYCLE: {
        CYCLE_INIT: init_cycle,
        # ...
    }
}
```

---

## Examples

Complete working examples demonstrating cycle features:

- **[cycles_basic.py](../examples/cycles_basic.py)** - Basic cycle with CYCLE_INIT, CYCLE_LOOP, and CYCLE_END for a simple counter
- **[cycles_loop_start.py](../examples/cycles_loop_start.py)** - Using CYCLE_LOOP_START to prepare data for each iteration
- **[cycles_nested.py](../examples/cycles_nested.py)** - Nested cycles for multi-dimensional iteration (processing a grid with outer and inner cycles)

See [examples/README.md](../examples/README.md) for a complete guide to all available examples.

---

## Documentation

- **[User Guide](README.md)** - Overview and quick start
- **[Parameters Guide](parameters.md)** - Parameter definition and usage
- **[Commands Guide](commands.md)** - Command system and dependencies
- **[Phases Guide](phases.md)** - Multi-phase execution control
- **Cycles Guide** - Repeating command sequences
- **[Configuration Guide](configuration.md)** - Configuration management
- **[Logging Guide](logging.md)** - Built-in logging system
- **[API Reference](api-reference.md)** - Complete API documentation

---

[← Phases Guide](phases.md) | [Index](README.md#documentation) | [Configuration Guide →](configuration.md)
