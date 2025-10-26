# Buffered Parameter Registration and Run-Levels

The buffered parameter registration and run-level system allows you to:

1. **Register parameters before parser construction** - No need to have a live parser at import time
2. **Define named run-levels** - Ship and combine sets of parameter defaults
3. **Merge configurations** - Combine base defaults, run-levels, and CLI arguments with clear precedence

## Quick Start

### Basic Usage

```python
from spafw37 import register_param, register_run_level, build_parser, get_effective_config

# Register parameters (buffered until build_parser is called)
register_param(
    name='timeout',
    aliases=['--timeout', '-t'],
    type='number',
    default=30
)

# Define run-levels
register_run_level('dev', {'timeout': 10})
register_run_level('prod', {'timeout': 60})

# Build parser from buffered registrations
build_parser()

# Get effective configuration with run-level merging
import sys
config = get_effective_config(sys.argv[1:])
```

### Running with Run-Levels

```bash
# Use development configuration
python myapp.py -R dev

# Use production configuration
python myapp.py --run-levels prod

# Combine multiple run-levels (later overrides earlier)
python myapp.py -R dev,prod

# Override run-level values with CLI arguments
python myapp.py -R prod --timeout 45
```

## API Reference

### Parameter Registration

#### `register_param(**kwargs)`

Buffer a parameter definition for later parser construction.

**Arguments:**
- `name` (str): Unique parameter identifier
- `aliases` (list): CLI aliases (e.g., `['--timeout', '-t']`)
- `type` (str): Parameter type - `'text'`, `'number'`, `'toggle'`, or `'list'`
- `default` (any): Default value
- `description` (str): Help text
- Additional options: `bind_to`, `persistence`, `switch_list`, etc.

**Example:**
```python
register_param(
    name='log-level',
    aliases=['--log-level', '-l'],
    type='text',
    default='info',
    description='Logging level'
)
```

#### `build_parser()`

Process all buffered parameter registrations and prepare for parsing.

**Returns:** Number of parameters registered from buffer

**Example:**
```python
count = build_parser()
print(f"Registered {count} parameters")
```

### Run-Level Management

#### `register_run_level(name, defaults)`

Define a named run-level with default parameter values.

**Arguments:**
- `name` (str): Name of the run-level
- `defaults` (dict): Dictionary mapping parameter names to values

**Example:**
```python
register_run_level('dev', {
    'host': 'localhost',
    'port': 3000,
    'debug': True,
    'log-level': 'debug'
})

register_run_level('prod', {
    'host': 'prod.example.com',
    'port': 443,
    'debug': False,
    'log-level': 'error'
})
```

### Configuration Access

#### `get_effective_config(args)`

Compute the effective configuration by merging run-levels and CLI arguments.

**Arguments:**
- `args` (list): Command-line argument strings

**Returns:** Dictionary with effective configuration values

**Merge Order:**
1. Base parameter defaults (lowest precedence)
2. Run-levels in specified order (later overrides earlier)
3. Explicit CLI arguments (highest precedence)

**Example:**
```python
# With args: ['-R', 'dev,prod', '--timeout', '45']
config = get_effective_config(['-R', 'dev,prod', '--timeout', '45'])
# Result: dev defaults → prod defaults → CLI timeout=45
```

#### `parse_args(args, merge_run_levels=True)`

Parse command-line arguments with optional run-level support.

**Arguments:**
- `args` (list or None): Argument strings, or None for `sys.argv[1:]`
- `merge_run_levels` (bool): Whether to apply run-level merging

**Returns:** Tuple of (namespace_dict, effective_config_dict)

**Example:**
```python
config, effective = parse_args(None, merge_run_levels=True)
```

### Conflict Resolution

#### `set_conflict_policy(policy)`

Set the policy for handling duplicate parameter registrations.

**Arguments:**
- `policy` (str): One of `'first'`, `'last'`, or `'error'`
  - `'first'`: Keep first registration, warn about duplicates (default)
  - `'last'`: Use last registration, warn about duplicates
  - `'error'`: Raise ValueError on duplicate

**Example:**
```python
from spafw37.config_consts import CONFLICT_POLICY_ERROR
from spafw37.param import set_conflict_policy

set_conflict_policy(CONFLICT_POLICY_ERROR)
```

## Run-Level Syntax

Run-levels can be specified using either:
- **Long form:** `--run-levels LEVEL`
- **Short form:** `-R LEVEL`

### Single Run-Level

```bash
python myapp.py -R dev
python myapp.py --run-levels prod
```

### Multiple Run-Levels (Comma-Separated)

```bash
python myapp.py -R base,dev,feature
```

### Multiple Run-Levels (Multiple Flags)

```bash
python myapp.py -R base -R dev -R feature
```

### Mixed Syntax

```bash
python myapp.py -R base,dev --run-levels feature
```

All of these merge run-levels in the order specified: `base` → `dev` → `feature`

## Configuration Precedence

The effective configuration is computed by merging values in this order:

```
Base Defaults
    ↓ (overridden by)
Run-Level 1
    ↓ (overridden by)
Run-Level 2
    ↓ (overridden by)
...
    ↓ (overridden by)
CLI Arguments
```

**Example:**

```python
# Parameter definition
register_param(name='timeout', default=30)

# Run-levels
register_run_level('dev', {'timeout': 10})
register_run_level('prod', {'timeout': 60})

build_parser()

# Scenario 1: No run-levels
get_effective_config([])
# Result: timeout=30 (base default)

# Scenario 2: Single run-level
get_effective_config(['-R', 'dev'])
# Result: timeout=10 (dev run-level)

# Scenario 3: Multiple run-levels
get_effective_config(['-R', 'dev,prod'])
# Result: timeout=60 (prod overrides dev)

# Scenario 4: Run-level + CLI override
get_effective_config(['-R', 'prod', '--timeout', '45'])
# Result: timeout=45 (CLI overrides prod)
```

## Common Patterns

### Module-Level Registration

Modules can register parameters at import time without needing a live parser:

```python
# module_a.py
from spafw37 import register_param

register_param(name='module-a-option', aliases=['--mod-a'], default='value')
```

```python
# module_b.py
from spafw37 import register_param

register_param(name='module-b-option', aliases=['--mod-b'], default='value')
```

```python
# main.py
import module_a
import module_b
from spafw37 import build_parser, handle_cli_args

build_parser()  # Flushes buffered registrations from both modules
handle_cli_args(sys.argv[1:])
```

### Environment-Specific Configurations

Define run-levels for different deployment environments:

```python
register_run_level('local', {
    'host': 'localhost',
    'port': 8000,
    'debug': True,
    'workers': 1
})

register_run_level('ci', {
    'host': '0.0.0.0',
    'port': 8080,
    'debug': False,
    'workers': 2
})

register_run_level('staging', {
    'host': 'staging.example.com',
    'port': 443,
    'debug': False,
    'workers': 4
})

register_run_level('prod', {
    'host': 'prod.example.com',
    'port': 443,
    'debug': False,
    'workers': 8
})
```

### Layered Configurations

Build configurations from multiple layers:

```python
# Base settings common to all environments
register_run_level('base', {
    'timeout': 30,
    'retries': 3
})

# Security settings
register_run_level('secure', {
    'ssl': True,
    'verify': True
})

# Development-specific overrides
register_run_level('dev', {
    'debug': True,
    'ssl': False
})

# Usage: python myapp.py -R base,secure,dev
# Result: base + secure + dev (dev's ssl=False overrides secure's ssl=True)
```

## Backward Compatibility

The new API is fully backward compatible with existing code:

- `add_param()` continues to work and immediately registers parameters
- `handle_cli_args()` continues to work with immediately-registered parameters
- Buffered registration is optional - use it when you need deferred registration

**Existing code (still works):**
```python
from spafw37 import add_param, handle_cli_args

add_param({'name': 'test', 'aliases': ['--test']})
handle_cli_args(sys.argv[1:])
```

**New buffered approach:**
```python
from spafw37 import register_param, build_parser, handle_cli_args

register_param(name='test', aliases=['--test'])
build_parser()
handle_cli_args(sys.argv[1:])
```

## Error Handling

### Missing Run-Level

If a run-level doesn't exist, a warning is logged and it's ignored:

```python
get_effective_config(['-R', 'nonexistent'])
# Warning: Unknown run-level 'nonexistent', ignoring
# Continues with base defaults
```

### Duplicate Registrations

Behavior depends on the conflict policy:

```python
register_param(name='test', default='first')
register_param(name='test', default='second')

# With CONFLICT_POLICY_FIRST (default):
build_parser()
# Warning: Duplicate registration for 'test', keeping first
# Result: default='first'

# With CONFLICT_POLICY_ERROR:
set_conflict_policy(CONFLICT_POLICY_ERROR)
build_parser()
# Raises: ValueError: Duplicate parameter registration for dest 'test'
```

### Missing Parameter Name

Buffered registrations without a `name` are skipped with a warning:

```python
register_param(aliases=['--test'])  # Missing 'name'
build_parser()
# Warning: Buffered registration missing 'name', skipping
```

## Examples

See the `examples/` directory for complete working examples:

- `simple_run_levels.py` - Basic usage pattern
- `run_level_demo.py` - Comprehensive demonstration of all features

Run the demo:
```bash
python examples/run_level_demo.py
```
