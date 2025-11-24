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
- Using `get_param()` for automatic type handling

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

### `params_allowed_values.py` - Restrict parameter values to allowed set
- Constraining TEXT, NUMBER, and LIST parameters to predefined values
- Case-insensitive matching for TEXT parameters
- Clear error messages for invalid values

**Run:**
```bash
python params_allowed_values.py deploy --env production
python params_allowed_values.py start --port 8080 --size large
```

### `params_dict.py` - Dict (JSON) Parameters
- Dict/object parameters with JSON data
- Inline JSON, multi-token JSON, file loading
- **v1.1.0:** Multiple JSON blocks (automatically merged)
- **v1.1.0:** File references within JSON

**Run:**
```bash
python params_dict.py api-call --payload '{"user":"alice","action":"login"}'
python params_dict.py api-call --payload @examples/sample_payload.json
# v1.1.0 features:
python params_dict.py api-call --payload '{"user":"alice"}' '{"action":"login"}'
python params_dict.py api-call --payload '{"data": @examples/sample_payload.json}'
```

### `params_file.py` - File Loading with @file Syntax
- Loading parameter values from files using `@file.txt`
- Works with all parameter types (text, number, list, dict)
- Multiple file references for list parameters

**Run:**
```bash
python params_file.py read-query --sql @examples/sample_query.sql
python params_file.py process-count --count @examples/sample_count.txt
python params_file.py process-files --files @examples/sample_files.txt
python params_file.py send-payload --payload @examples/sample_payload.json
```

### `params_join.py` - Accumulating Values (v1.1.0)
- **NEW:** Using `join_param()` to accumulate values
- String concatenation with custom separators
- List accumulation (append/extend)
- Dict merging (shallow/deep, collision strategies)

**Run:**
```bash
python params_join.py demo-string
python params_join.py demo-list
python params_join.py demo-dict
```

### `params_input_filter.py` - Custom Input Filters (v1.1.0)
- **NEW:** Using `PARAM_INPUT_FILTER` for custom parsing
- CSV to list conversion
- Connection string parsing
- Key=value pair parsing

**Run:**
```bash
python params_input_filter.py parse-csv --tags "python, cli, framework"
python params_input_filter.py connect --db "host=localhost;port=5432;database=myapp"
python params_input_filter.py parse-kv --settings "debug=true timeout=30 retries=3"
```

### `params_runtime.py` - Runtime-Only Parameters
- Internal state parameters (not exposed to CLI)
- Shared state between commands
- Session management
- Using `set_param()` and `get_param()` for runtime state

**Run:**
```bash
python params_runtime.py init process-item process-item summary
```

### `params_immutable.py` - Immutable Parameters
- Using `PARAM_IMMUTABLE` for write-once protection
- Protecting critical configuration from accidental modification
- Use cases: configuration lock, runtime constants
- Comparison of mutable vs immutable behavior

**Run:**
```bash
python params_immutable.py
```

### `params_unset.py` - Parameter Unset and Reset
- `unset_param()` - Remove parameter values completely
- `reset_param()` - Reset to default or unset if no default
- Runtime state cleanup patterns
- How immutable parameters block unset and reset operations

**Run:**
```bash
python params_unset.py
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

### `cycles_loop_end.py` - Cycle Loop End
- `CYCLE_LOOP_END` - cleanup at end of each iteration
- Counter increment patterns
- Accumulating results across iterations
- Symmetry with `CYCLE_LOOP_START`

**Run:**
```bash
python cycles_loop_end.py run-cycle
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
