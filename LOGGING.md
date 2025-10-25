# Logging in spafw37

The spafw37 framework includes comprehensive logging functionality with support for custom log levels, scope-based logging, and configurable output destinations.

## Features

### Log Levels

- **TRACE** (5): Most detailed logging level, below DEBUG
- **DEBUG** (10): Detailed information for debugging
- **INFO** (20): General informational messages (default for console)
- **WARNING** (30): Warning messages
- **ERROR** (40): Error messages
- **CRITICAL** (50): Critical error messages

### Log Format

All log messages follow this format:
```
[{MM-dd hh:mm:ss.sss}][{scope}][{log_level}] {message}
```

Example:
```
[10-24 22:42:24.764][phase-setup][INFO] Starting command: setup
```

Note: When using command.py delegate functions, the current phase is automatically passed as the scope.

### Log Outputs

1. **File Logging**: 
   - Log files are created in the `logs/` directory (configurable)
   - File naming pattern: `log-{yyyy-MM-dd-hh.mm.ss}.log`
   - Default level: DEBUG and above
   
2. **Console Logging**:
   - Outputs to stdout
   - Default level: INFO and above
   
3. **Error Logging**:
   - Outputs to stderr
   - Level: ERROR and above

## Command-Line Parameters

### Logging Control Parameters

- `--verbose`, `-v`: Enable verbose console logging (DEBUG level)
- `--trace`: Set file log level to TRACE
- `--trace-console`: Set console log level to TRACE
- `--silent`: Suppress all console logging (errors to stderr only)
- `--no-logging`: Suppress all logging to console and file (errors to stderr only)
- `--suppress-errors`: Disable error logging completely

### Configuration Parameters

- `--log-dir <dir>`: Set the log directory (default: `logs/`, **persistent**)
- `--log-level <level>`: Set overall log level (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--phase-log-level <phase> <level>`: Set log level for a specific scope (e.g., phase name)

### Persistence

Most logging parameters are **not persistent** (they apply only to the current run):
- `--verbose`, `-v`
- `--trace`
- `--trace-console`
- `--silent`
- `--no-logging`
- `--suppress-errors`
- `--log-level`
- `--phase-log-level`

Only `--log-dir` is **persistent** (saved to configuration).

## Usage Examples

### Basic Usage

```python
from spafw37 import logging

# Simple logging
logging.log_info(_message="Application started")
logging.log_debug(_message="Debug information")
logging.log_error(_message="An error occurred")
```

### Scope-Based Logging

The logging module uses a generic `scope` parameter that can be any string identifier. When using the logging module directly:

```python
from spafw37 import logging

# Set current scope
logging.set_current_scope("initialization")
logging.log_info(_message="Initializing resources")

# Log with explicit scope
logging.log_info(_scope="custom-scope", _message="Processing data")
```

When using command.py delegate functions, the current phase is automatically passed as the scope:

```python
from spafw37 import command

# Within a command execution context, phase is automatically used as scope
command.log_info(_message="This will use the current phase as scope")
```

### Configuration

```python
from spafw37 import logging, param, config
from spafw37.logging import LOGGING_PARAMS

# Register logging parameters
param.add_params(LOGGING_PARAMS)

# Configure logging via params
verbose_param = param.get_param_by_name('log-verbose')
config.set_config_value(verbose_param, True)

# Apply logging configuration
logging.apply_logging_config()
```

### Custom Log Directory

```python
from spafw37 import logging

logging.set_log_dir('/var/log/myapp')
```

## Integration with Commands

The framework automatically logs command execution:

```
[10-24 22:42:24.764][phase-setup][INFO] Starting command: setup
[10-24 22:42:24.764][phase-setup][INFO] Completed command: setup
```

And parameter value changes (at DEBUG level):

```
[10-24 22:42:24.764][spafw37][DEBUG] Set param 'log-verbose' = True
```

## Running the Demo

A demonstration script is included to show the logging functionality:

```bash
python3 demo_logging.py
```

This will:
1. Set up logging with verbose mode
2. Execute commands across multiple phases (setup, execution, cleanup)
3. Generate log files in the `logs/` directory
4. Display log messages on the console

## API Reference

### Main Functions (logging module)

- `log(_level=INFO, _scope=None, _message='')`: Log a message at specified level
- `log_trace(_scope=None, _message='')`: Log at TRACE level
- `log_debug(_scope=None, _message='')`: Log at DEBUG level
- `log_info(_scope=None, _message='')`: Log at INFO level
- `log_warning(_scope=None, _message='')`: Log at WARNING level
- `log_error(_scope=None, _message='')`: Log at ERROR level

### Delegate Functions (command module)

These functions automatically inject the current phase as the scope:

- `command.log_trace(_message='')`: Log at TRACE level with current phase as scope
- `command.log_debug(_message='')`: Log at DEBUG level with current phase as scope
- `command.log_info(_message='')`: Log at INFO level with current phase as scope
- `command.log_warning(_message='')`: Log at WARNING level with current phase as scope
- `command.log_error(_message='')`: Log at ERROR level with current phase as scope

### Configuration Functions

- `set_current_scope(scope)`: Set current scope for logging context
- `set_log_dir(log_dir)`: Set log directory
- `set_file_level(level)`: Set file handler log level
- `set_console_level(level)`: Set console handler log level
- `set_silent_mode(silent)`: Enable/disable silent mode
- `set_no_logging_mode(no_logging)`: Enable/disable no-logging mode
- `set_suppress_errors(suppress)`: Enable/disable error suppression
- `set_scope_log_level(scope, level)`: Set log level for specific scope
- `apply_logging_config()`: Apply logging configuration from config values

### Config Functions

- `config.set_app_name(name)`: Set application name (used as default scope)
- `config.get_app_name()`: Get application name

## Notes

- The logger is initialized automatically on first use
- Log files are created with a unique timestamp
- The `logs/` directory is automatically created if it doesn't exist
- The logger is private to the module (`_logger`) and should not be accessed directly
- Always use the public `log()` function or convenience functions for logging
