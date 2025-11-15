# spafw37 Examples

This directory contains focused examples demonstrating specific features of the spafw37 framework.

## Table of Contents

- [Parameters Examples](#parameters-examples)
- [Commands Examples](#commands-examples)
- [Cycles Examples](#cycles-examples)
- [Phases Examples](#phases-examples)
- [Output Examples](#output-examples)
- [Configuration Examples](#configuration-examples)
- [Tips](#tips)

## Parameters Examples

### `params_basic.py` - Basic Parameter Types
- Text parameters
- Number parameters
- Parameter aliases
- Default values

**Run:**
```bash
python params_basic.py process --input data.txt --count 5
```

### `params_toggles.py` - Toggle Parameters & Switch Lists
- Toggle (boolean) parameters
- Mutually exclusive parameters (switch lists)
- Output format selection

**Run:**
```bash
python params_toggles.py process --input data.txt --json
python params_toggles.py process --input data.txt --csv
```

### `params_lists.py` - List Parameters
- Parameters that accept multiple values
- Collecting and processing lists

**Run:**
```bash
python params_lists.py process --file a.txt --file b.txt --tag urgent --tag review
```

### `params_runtime.py` - Runtime-Only Parameters
- Internal state parameters (not exposed to CLI)
- Shared state between commands
- Session management

**Run:**
```bash
python params_runtime.py init process-item process-item summary
```

### `params_groups.py` - Parameter Groups
- Using PARAM_GROUP to organise parameters
- Grouping parameters by functional area
- Improving help output readability
- Organizing large parameter sets

**Run:**
```bash
python params_groups.py --help
python params_groups.py process --input data.txt --threads 4 --strict
```

### `params_required.py` - Required Parameters
- Using PARAM_REQUIRED for globally required parameters
- Framework validation before command execution
- Parameters that must always be set
- Clear error messages for missing parameters

**Run:**
```bash
# Show validation error
python params_required.py status
# Provide required parameters
python params_required.py status --env production --project myapp
python params_required.py deploy --env staging --project api
```

## Commands Examples

### `commands_basic.py` - Basic Commands
- Simple command definition
- Command actions
- Basic execution

**Run:**
```bash
python commands_basic.py hello
python commands_basic.py greet goodbye
```

### `commands_sequencing.py` - Command Sequencing
- `COMMAND_GOES_AFTER` - control execution order
- Sequential command flow
- Natural ordering

**Run:**
```bash
python commands_sequencing.py prepare download process finalise
```

### `commands_dependencies.py` - Command Dependencies
- `COMMAND_REQUIRE_BEFORE` - enforce prerequisites
- Dependency chains
- Automatic dependency resolution

**Run:**
```bash
python commands_dependencies.py deploy
# Automatically runs: setup -> validate -> build -> test -> deploy
```

### `commands_next.py` - Command Next Queuing
- `COMMAND_NEXT_COMMANDS` - automatic command chaining
- Dynamic workflow
- Command pipelines

**Run:**
```bash
python commands_next.py start
# Automatically chains through entire workflow
```

### `commands_required.py` - Command Required Parameters
- Using COMMAND_REQUIRED_PARAMS for command-specific requirements
- Different commands with different parameter requirements
- Validation before command execution
- Clear error messages with parameter details

**Run:**
```bash
# status command has no special requirements
python commands_required.py status
# deploy requires api-key and instance-count
python commands_required.py deploy --key abc123 --count 3
# backup requires backup-path
python commands_required.py backup --backup /backups/app
```

### `commands_trigger.py` - Parameter-Triggered Commands
- Using COMMAND_TRIGGER_PARAM for automatic command invocation
- Commands that run when specific parameters are set
- Initialisation and setup automation
- Loading resources based on parameters

**Run:**
```bash
# Normal processing
python commands_trigger.py process
# Triggers load-plugins command automatically
python commands_trigger.py process --plugin-dir ./plugins
# Triggers both load-plugins and load-config
python commands_trigger.py process --plugin-dir ./plugins --config-file settings.json
```

### `commands_visibility.py` - Command Visibility Control
- Using COMMAND_EXCLUDE_HELP to hide commands from help
- Using COMMAND_FRAMEWORK for framework-internal commands
- Hiding deprecated or internal commands
- Commands remain executable when hidden

**Run:**
```bash
# Show help - only visible commands listed
python commands_visibility.py --help
# Run visible command
python commands_visibility.py build
# Run hidden command - still works
python commands_visibility.py internal-diagnostics
```

## Cycles Examples

### `cycles_basic.py` - Basic Cycles
- `CYCLE_INIT` - initialise before loop
- `CYCLE_LOOP` - iteration condition
- `CYCLE_END` - finalise after loop
- Basic iteration pattern

**Run:**
```bash
python cycles_basic.py run-cycle
```

### `cycles_loop_start.py` - Cycle Loop Start
- `CYCLE_LOOP_START` - prepare each iteration
- Iteration-specific state
- Processing collections

**Run:**
```bash
python cycles_loop_start.py process-items
```

### `cycles_nested.py` - Nested Cycles
- Nested cycle patterns
- Outer and inner cycle coordination
- Multi-level iteration
- Maximum nesting depth (5 levels)

**Run:**
```bash
python cycles_nested.py process-grid
```

## Phases Examples

### `phases_basic.py` - Basic Phase Usage
- Using default phases (SETUP, CLEANUP, EXECUTION, TEARDOWN, END)
- Assigning commands to phases with COMMAND_PHASE
- Automatic phase-based execution ordering
- Dependencies within phases

**Run:**
```bash
python phases_basic.py verify save summary
```

### `phases_custom_order.py` - Custom Phase Order
- Reordering default phases with set_phases_order()
- Controlling execution flow (e.g., CLEANUP before SETUP)
- Understanding phase order impact

**Run:**
```bash
python phases_custom_order.py cleanup setup process teardown report
```

### `phases_extended.py` - Extended Phases (Recommended)
- **BEST PRACTICE:** Extending default phases with custom phases
- Preserving framework functionality (PHASE_EXECUTION)
- Mixed custom and default phases
- Build pipeline with validation, testing, deployment

**Run:**
```bash
python phases_extended.py check-syntax compile unit-tests deploy cleanup
```

### `phases_custom.py` - Completely Custom Phases (Advanced)
- **ADVANCED:** Completely replacing default phases
- Creating application-specific phase names
- Setting custom default phase with set_default_phase()
- **WARNING:** Can break framework features if not careful
- Build pipeline example (VALIDATE, BUILD, TEST, DEPLOY, VERIFY)

**Run:**
```bash
python phases_custom.py check-syntax compile unit-tests deploy-staging verify
```

## Output Examples

### `output_basic.py` - Basic Output Functions
- Using `spafw37.output()` for application output
- Normal vs verbose-only output
- Silent mode suppression
- Checking verbose/silent status with `is_verbose()` and `is_silent()`

**Run:**
```bash
python output_basic.py demo           # Normal output
python output_basic.py demo --verbose # With verbose details
python output_basic.py demo --silent  # Suppressed output
python output_basic.py process        # Progress output
```

### `output_handlers.py` - Custom Output Handlers
- Default console handler
- File output handler
- Dual output (console + file)
- Timestamped output handler
- Per-call handler specification

**Run:**
```bash
python output_handlers.py default     # Console output
python output_handlers.py file        # Write to file
python output_handlers.py dual        # Console + file
python output_handlers.py timestamp   # With timestamps
python output_handlers.py testing     # Per-call handlers
python output_handlers.py all         # Run all demos
```

## Configuration Examples

### `config_basic.py` - Basic Configuration
- Getting configuration values
- Setting configuration values
- Runtime configuration state

**Run:**
```bash
python config_basic.py show
python config_basic.py modify
```

### `config_persistence.py` - Configuration Persistence
- `PARAM_PERSISTENCE_ALWAYS` - auto-save to config.json
- `PARAM_PERSISTENCE_NEVER` - never save
- User config files (--save-config, --load-config)

**Run:**
```bash
python config_persistence.py show --project /my/project
python config_persistence.py show --author "John Doe" --save-config my-config.json
python config_persistence.py show --load-config my-config.json
```

## Tips

- Use `--help` with any example to see available commands and parameters
- Use `--no-logging` to suppress framework diagnostic messages
- Use `--verbose` to see detailed framework logging
- Check the source code of each example for detailed comments
