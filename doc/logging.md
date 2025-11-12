# Logging Guide

[← Configuration Guide](configuration.md) | [Index](README.md#documentation) | [API Reference →](api-reference.md)

## Table of Contents

- [Overview](#overview)
- [Log Levels](#log-levels)
- [Log Format](#log-format)
- [Log Outputs](#log-outputs)
- [Command-Line Parameters](#command-line-parameters)
  - [Log Level Control](#log-level-control)
  - [Output Control](#output-control)
  - [Configuration](#configuration)
- [Basic Logging](#basic-logging)
- [Scope-Based Logging](#scope-based-logging)
- [Configuration](#configuration-1)
  - [Setting Log Directory](#setting-log-directory)
  - [Applying Configuration](#applying-configuration)
- [Integration with Commands](#integration-with-commands)
- [Best Practices](#best-practices)

## Overview

The spafw37 framework provides comprehensive logging functionality with:

- **Custom TRACE level** - Below DEBUG for ultra-detailed logging
- **Scope-based logging** - Organize logs by module, phase, or feature
- **Multiple outputs** - File, console (stdout), and error (stderr) handlers
- **Flexible control** - CLI parameters for runtime log level adjustment
- **Automatic formatting** - Consistent timestamped log entries
- **Persistent preferences** - Save log directory between runs

Key capabilities:
- Five standard log levels plus custom TRACE level
- Automatic log file creation with timestamp naming
- Scope-specific log level control
- Silent and no-logging modes
- Error suppression for testing
- Integration with command execution and phases

## Log Levels

The framework supports six log levels in ascending order of severity:

| Level | Value | Description | Default Output |
|-------|-------|-------------|----------------|
| `TRACE` | 5 | Most detailed logging, below DEBUG | File only |
| `DEBUG` | 10 | Detailed information for debugging | File only |
| `INFO` | 20 | General informational messages | File + Console |
| `WARNING` | 30 | Warning messages | File + Console |
| `ERROR` | 40 | Error messages | File + Console + Stderr |
| `CRITICAL` | 50 | Critical error messages | File + Console + Stderr |

Access log levels via the logging module:

```python
from spafw37 import logging

logging.TRACE     # 5
logging.DEBUG     # 10
logging.INFO      # 20
logging.WARNING   # 30
logging.ERROR     # 40
logging.CRITICAL  # 50
```

## Log Format

All log messages follow this consistent format:

```
[{MM-dd hh:mm:ss.sss}][{scope}][{log_level}] {message}
```

**Components:**
- **Timestamp** - Month-day hour:minute:second.milliseconds
- **Scope** - Context identifier (phase, module, feature name)
- **Log Level** - TRACE, DEBUG, INFO, WARNING, ERROR, or CRITICAL
- **Message** - The log message text

**Examples:**

```
[11-12 14:23:45.123][myapp][INFO] Application started
[11-12 14:23:45.234][phase-setup][INFO] Starting command: initialize
[11-12 14:23:45.345][file-processor][DEBUG] Processing file: data.txt
[11-12 14:23:45.456][validation][WARNING] Missing optional field
[11-12 14:23:45.567][phase-execution][ERROR] Failed to process batch 3
```

## Log Outputs

The logging system uses three separate handlers:

### 1. File Handler

- **Default Level:** DEBUG (and above)
- **Location:** `logs/` directory (configurable)
- **Filename Pattern:** `log-{yyyy-MM-dd-hh.mm.ss}.log`
- **Auto-created:** Directory and files created automatically
- **Persistent:** File location can be saved between runs

**Example log file:** `logs/log-2025-11-12-14.23.45.log`

### 2. Console Handler (stdout)

- **Default Level:** INFO (and above)
- **Output:** Standard output
- **Use Case:** Normal application messages
- **Control:** `--verbose`, `--trace-console`, `--silent`, etc.

### 3. Error Handler (stderr)

- **Level:** ERROR (and above)
- **Output:** Standard error
- **Use Case:** Error and critical messages
- **Always Active:** Unless `--suppress-errors` is used

## Command-Line Parameters

### CLI Parameters

| Flag | Alias | Description |
|------|-------|-------------|
| `--verbose` | `-v` | Enable verbose console output (DEBUG level) |
| `--trace` | | Enable trace level for both file and console |
| `--trace-console` | | Enable trace level for console only |
| `--log-level <level>` | | Set explicit log level (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `--silent` | | Suppress console output (errors still to stderr) |
| `--no-logging` | | Disable both console and file logging (errors still to stderr) |
| `--suppress-errors` | | Suppress all output including stderr |
| `--log-dir <dir>` | | Set log file directory (default: ./logs) |
| `--log-file <name>` | | Set log file name (default: app.log) |

### Log Level Control

Control console and file logging verbosity:

```bash
# Verbose mode - console shows DEBUG level
myapp --verbose
myapp -v

# Trace mode - both file and console show TRACE level
myapp --trace

# Trace console only - console shows TRACE, file stays at DEBUG
myapp --trace-console

# Set explicit log level for both handlers
myapp --log-level DEBUG
myapp --log-level TRACE
myapp --log-level WARNING
```

**Priority (highest to lowest):**
1. `--log-level` - Explicit level overrides all others
2. `--trace` - Both handlers to TRACE
3. `--trace-console` - Console to TRACE only
4. `--verbose` - Console to DEBUG
5. Default - File: DEBUG, Console: INFO

### Output Control

Control where logs appear:

```bash
# Silent mode - suppress console output (errors still to stderr)
myapp --silent

# No logging - suppress both console and file (errors still to stderr)
myapp --no-logging

# Suppress errors - disable even stderr output
myapp --suppress-errors
```

### Configuration

```bash
# Set log directory (persistent - saved between runs)
myapp --log-dir /var/log/myapp

# Set scope-specific log level
myapp --phase-log-level phase-setup DEBUG --phase-log-level validation TRACE
```

**Persistence:**
- Only `--log-dir` is persistent (saved to `config.json`)
- All other logging parameters are runtime-only (not saved)

## Basic Logging

Use the logging functions from the core facade:

```python
from spafw37 import core as spafw37

def process_data():
    # Log at different levels
    spafw37.log_info(_message="Starting data processing")
    spafw37.log_debug(_message="Loading configuration")
    spafw37.log_warning(_message="Using default timeout value")
    
    try:
        # Process data
        pass
    except Exception as e:
        spafw37.log_error(_message=f"Processing failed: {e}")

# Trace level logging
spafw37.log_trace(_message="Detailed execution trace information")
```

**Available logging functions:**
- `spafw37.log_trace(_scope=None, _message='')` - TRACE level
- `spafw37.log_debug(_scope=None, _message='')` - DEBUG level
- `spafw37.log_info(_scope=None, _message='')` - INFO level
- `spafw37.log_warning(_scope=None, _message='')` - WARNING level
- `spafw37.log_error(_scope=None, _message='')` - ERROR level

## Scope-Based Logging

Scopes organize log messages by context (module, phase, feature, etc.):

### Setting Current Scope

```python
from spafw37 import core as spafw37

def initialize():
    # Set scope for subsequent log messages
    spafw37.set_current_scope('initialization')
    
    spafw37.log_info(_message="Loading configuration")
    # Output: [11-12 14:23:45.123][initialization][INFO] Loading configuration
    
    spafw37.log_info(_message="Connecting to database")
    # Output: [11-12 14:23:45.234][initialization][INFO] Connecting to database
```

### Explicit Scope per Message

```python
from spafw37 import core as spafw37

def process_files():
    # Different scopes for different operations
    spafw37.log_info(_scope='file-loader', _message="Loading file list")
    spafw37.log_debug(_scope='file-validator', _message="Validating file format")
    spafw37.log_info(_scope='file-processor', _message="Processing file batch")
```

### Scope-Specific Log Levels

Control log levels per scope:

```bash
# Show DEBUG for validation, TRACE for file-processor
myapp --phase-log-level validation DEBUG --phase-log-level file-processor TRACE
```

```python
from spafw37 import core as spafw37

# Validation scope - DEBUG and above
spafw37.log_debug(_scope='validation', _message="This will appear")
spafw37.log_trace(_scope='validation', _message="This will be filtered")

# File-processor scope - TRACE and above (all messages)
spafw37.log_trace(_scope='file-processor', _message="This will appear")
```

### Default Scope

If no scope is set, the application name is used:

```python
from spafw37 import core as spafw37

spafw37.set_app_name('my-application')

# No scope specified - uses app name
spafw37.log_info(_message="Application started")
# Output: [11-12 14:23:45.123][my-application][INFO] Application started
```

## Configuration

### Automatic Configuration

The logging system is **automatically configured** during CLI parsing. Logging parameters are parsed early (pre-parse phase) and applied before any commands execute:

```bash
# Logging is automatically set up based on CLI parameters
myapp --verbose --log-dir /var/log/myapp

# No manual configuration needed - just run your app
myapp --trace-console
```

The framework:
1. Registers logging parameters automatically via `configure.py`
2. Pre-parses logging parameters before main CLI parsing
3. Initializes the logger on first use with configured settings
4. Creates log files and directories as needed

### Setting Log Directory

The log directory can be set via CLI parameter (persistent) or programmatically:

```python
from spafw37 import core as spafw37

# Set programmatically before running CLI
spafw37.set_log_dir('/var/log/myapp')

spafw37.run_cli()
```

Or via command line:

```bash
# Persistent - saved to config.json
myapp --log-dir /var/log/myapp
```

**Default:** `logs/` in current directory

**Persistence:** Log directory setting is saved to `config.json` and restored on next run.

## Integration with Commands

The framework automatically logs command execution:

```python
from spafw37 import core as spafw37
from spafw37.constants.command import *
from spafw37.constants.phase import *

commands = [
    {
        COMMAND_NAME: 'setup',
        COMMAND_PHASE: PHASE_SETUP,
        COMMAND_ACTION: lambda: print("Setting up...")
    }
]

spafw37.add_commands(commands)
spafw37.run_cli()
```

**Automatic log output:**

```
[11-12 14:23:45.123][phase-setup][INFO] Starting command: setup
Setting up...
[11-12 14:23:45.234][phase-setup][INFO] Completed command: setup
```

**Key behaviors:**
- Command start/completion logged at INFO level
- Current phase used as scope automatically
- Parameter changes logged at DEBUG level
- Framework operations use appropriate scopes

## Best Practices

### Use Appropriate Log Levels

```python
from spafw37 import core as spafw37

def process_batch():
    # TRACE - Very detailed, usually only needed for deep debugging
    spafw37.log_trace(_message=f"Raw data structure: {raw_data}")
    
    # DEBUG - Detailed information for debugging
    spafw37.log_debug(_message=f"Processing batch {batch_id} with {len(items)} items")
    
    # INFO - General progress and status
    spafw37.log_info(_message=f"Completed processing {count} files")
    
    # WARNING - Recoverable issues or important notices
    spafw37.log_warning(_message="Timeout occurred, retrying...")
    
    # ERROR - Failures that prevent operation
    spafw37.log_error(_message=f"Failed to process file: {filename}")
```

### Organize by Scope

```python
from spafw37 import core as spafw37

def main():
    # Use scopes to organize related operations
    spafw37.set_current_scope('initialization')
    initialize_app()
    
    spafw37.set_current_scope('data-loading')
    load_data()
    
    spafw37.set_current_scope('processing')
    process_data()
    
    spafw37.set_current_scope('cleanup')
    cleanup()
```

### Set Log Directory Early

If you want a custom log directory, set it before running the CLI:

```python
from spafw37 import core as spafw37

def main():
    # Set application identity
    spafw37.set_app_name('my-application')
    
    # Set custom log directory (before CLI runs)
    spafw37.set_log_dir('~/.local/share/my-application/logs')
    
    # Define parameters and commands
    spafw37.add_params(params)
    spafw37.add_commands(commands)
    
    # Run CLI - logging configured automatically from CLI params
    spafw37.run_cli()

if __name__ == '__main__':
    main()
```

**Note:** Logging levels are controlled via CLI parameters (e.g., `--verbose`, `--trace`) and cannot be changed programmatically at runtime.

### Use Silent Mode for Quiet Operations

```bash
# Background jobs or cron tasks
myapp --silent > /dev/null 2>&1

# Testing with minimal output
myapp --silent --suppress-errors
```

### Use Verbose Mode for Debugging

```bash
# Development debugging
myapp --verbose

# Detailed troubleshooting
myapp --trace

# Focus on specific scope
myapp --phase-log-level file-processor TRACE
```

### Keep Messages Informative

```python
from spafw37 import core as spafw37

# Good - specific and actionable
spafw37.log_error(_message=f"Failed to open file '{filename}': {error}")

# Bad - vague
spafw37.log_error(_message="An error occurred")

# Good - includes context
spafw37.log_debug(_scope='validation', _message=f"Validating record {record_id}: {len(fields)} fields")

# Bad - lacks context
spafw37.log_debug(_message="Validating")
```

### Separate Development and Production Logging

```python
from spafw37 import core as spafw37
import os

def main():
    # Set different log directories for different environments
    if os.getenv('ENV') == 'development':
        spafw37.set_log_dir('./logs')
    else:
        spafw37.set_log_dir('/var/log/myapp')
    
    # ... rest of setup ...
    spafw37.run_cli()

if __name__ == '__main__':
    main()
```

**Note:** Use CLI parameters to control log levels:

```bash
# Development - verbose output
./myapp --verbose

# Production - normal output
./myapp

# Debugging production issues
./myapp --trace --log-dir /tmp/debug-logs
```

### Handle Sensitive Data

```python
from spafw37 import core as spafw37

def authenticate(username, password):
    # Never log passwords or tokens
    spafw37.log_debug(_message=f"Authenticating user: {username}")
    # DO NOT: log_debug(f"Password: {password}")
    
    try:
        result = perform_auth(username, password)
        # Log success without sensitive details
        spafw37.log_info(_message=f"User {username} authenticated successfully")
    except AuthError as e:
        # Log error without exposing credentials
        spafw37.log_error(_message=f"Authentication failed for user {username}")
```

### Use Scopes for Feature Toggles

```python
from spafw37 import core as spafw37

def experimental_feature():
    # Use scope-specific logging for experimental features
    spafw37.log_trace(_scope='experimental', _message="Starting experimental processing")
    
    # Enable detailed logging for experiments:
    # myapp --phase-log-level experimental TRACE
```

## Documentation

- **[User Guide](README.md)** - Overview and quick start
- **[Parameters Guide](parameters.md)** - Parameter definition and usage
- **[Commands Guide](commands.md)** - Command system and dependencies
- **[Phases Guide](phases.md)** - Multi-phase execution control
- **[Cycles Guide](cycles.md)** - Repeating command sequences
- **[Configuration Guide](configuration.md)** - Configuration management
- **Logging Guide** - Built-in logging system
- **[API Reference](api-reference.md)** - Complete API documentation

---

[← Configuration Guide](configuration.md) | [Index](README.md#documentation) | [API Reference →](api-reference.md)
