# Issue #27: Pivot from Config Focus to Param Focus

## Overview

Pivot from config dict access to param-focused interface with metadata-driven validation. Users will call `spafw37.set_param()` and `spafw37.get_param_str()` instead of config methods, enabling type validation on write and leveraging parameter metadata. All param logic moves to `param.py` with proper private/public separation, keeping `config.py` primitive. Includes deprecation wrappers for backward compatibility in v1.1.0 milestone.

**Key architectural decisions:**

- **Multiple parameter identifiers:** Public API accepts params by name, bind_name, or alias
- **Internal resolution helper:** `_resolve_param_definition()` encapsulates lookup logic
- **Separation of concerns:** CLI parses → param validates → config stores
- **Type-safe getters:** Typed getter functions with automatic coercion
- **Deprecation strategy:** Old APIs wrapped with warnings, removed in v2.0.0

## Implementation Methodology

**Phased build-test-refactor approach:**

Each implementation step follows this pattern:

1. **Add helpers** - Create new helper functions/methods
2. **Test helpers** - Write unit tests for new helpers in isolation
3. **Refactor code** - Update existing code to use new helpers
4. **Verify existing tests** - Ensure all original tests still pass
5. **Add coverage tests** - Write additional tests for new behavior/edge cases

This ensures:

- No regressions (existing tests validate refactored code)
- Full coverage (new tests validate new helpers)
- Incremental progress (each step is independently testable)
- Safe refactoring (always have working baseline)

## Table of Contents

- [Overview](#overview)
- [Implementation Steps](#implementation-steps)
  - [1. Add parameter configuration constants](#1-add-parameter-configuration-constants)
  - [2. Make internal `param.py` helpers private and reorganize modules](#2-make-internal-parampy-helpers-private-and-reorganize-modules)
  - [3. Create parameter lookup system](#3-create-parameter-lookup-system)
  - [4. Extract type-specific validation helpers](#4-extract-type-specific-validation-helpers)
  - [5. Create `_validate_param_value()` orchestrator](#5-create-_validate_param_value-orchestrator)
  - [6. Refactor CLI parsing to use structured dict approach](#6-refactor-cli-parsing-to-use-structured-dict-approach)
  - [7. Add `set_param_value()` function](#7-add-set_param_value-function)
  - [8. Add `join_param_value()` function](#8-add-join_param_value-function)
  - [9. Add XOR validation for toggle params](#9-add-xor-validation-for-toggle-params)
  - [10. Add typed param getters](#10-add-typed-param-getters)
  - [11. Export param API through `core.py` facade](#11-export-param-api-through-corepy-facade)
  - [12. Refactor CLI layer](#12-refactor-cli-layer)
  - [13. Deprecate and refactor `config_func.py` param-setting functions](#13-deprecate-and-refactor-config_funcpy-param-setting-functions)
  - [14. Deprecate `config.set_config_list_value()`](#14-deprecate-configset_config_list_value)
  - [15. Update examples](#15-update-examples)
  - [16. Update documentation](#16-update-documentation)
  - [17. Create CHANGES.md for issue closing comment](#17-create-changesmd-for-issue-closing-comment)
  - [18. Update tests](#18-update-tests)
- [Further Considerations](#further-considerations)
  - [1. Dict merge semantics for `join_param()` - RESOLVED](#1-dict-merge-semantics-for-join_param---resolved)
  - [2. Deprecation warning verbosity control - RESOLVED](#2-deprecation-warning-verbosity-control---resolved)
  - [3. Type coercion failure messages - RESOLVED](#3-type-coercion-failure-messages---resolved)
  - [4. String join edge cases - RESOLVED](#4-string-join-edge-cases---resolved)
  - [5. Private method testing approach - RESOLVED](#5-private-method-testing-approach---resolved)
  - [6. Parameter lookup usage patterns - RESOLVED](#6-parameter-lookup-usage-patterns---resolved)
  - [7. Migration path for `set_config_list_value()` users - RESOLVED](#7-migration-path-for-set_config_list_value-users---resolved)
- [Success Criteria](#success-criteria)

## Implementation Steps

### 1. Add parameter configuration constants

**File:** `src/spafw37/constants/param.py`

- Add new constant `PARAM_JOIN_SEPARATOR = 'join-separator'`
- Used in parameter definitions to specify string concatenation separator
- Defaults to `' '` (space) if not specified in param definition
- Used by `join_param_value()` when concatenating multiple string values
- Example: `PARAM_JOIN_SEPARATOR: ','` for CSV-style tags

- Add common separator constants for convenience:
  - `SEPARATOR_SPACE = ' '` - default space separator
  - `SEPARATOR_COMMA = ','` - comma separator
  - `SEPARATOR_COMMA_SPACE = ', '` - comma with space
  - `SEPARATOR_PIPE = '|'` - pipe separator
  - `SEPARATOR_PIPE_PADDED = ' | '` - pipe with padding
  - `SEPARATOR_NEWLINE = '\n'` - newline separator
  - `SEPARATOR_TAB = '\t'` - tab separator
  - Note: Any string value allowed, constants are for convenience only

- Add dict merge type constants:
  - `PARAM_DICT_MERGE_TYPE = 'dict-merge-type'` - parameter definition key
  - `DICT_MERGE_SHALLOW = 'shallow'` - shallow merge (default)
  - `DICT_MERGE_DEEP = 'deep'` - recursive deep merge

- Add dict override strategy constants:
  - `PARAM_DICT_OVERRIDE_STRATEGY = 'dict-override-strategy'` - parameter definition key
  - `DICT_OVERRIDE_RECENT = 'recent'` - last value wins (default)
  - `DICT_OVERRIDE_OLDEST = 'oldest'` - first value wins
  - `DICT_OVERRIDE_ERROR = 'error'` - raise error on key conflict

[↑ Back to top](#table-of-contents)

### 2. Make internal `param.py` helpers private and reorganize modules

**Files:** `src/spafw37/param.py`, `src/spafw37/file.py` (new), `src/spafw37/cli.py`, `src/spafw37/core.py`

- **Create `_deprecated()` decorator in core.py:**
  - Add module-level set to track called functions: `_deprecated_warnings_shown = set()`
  - Add module-level flag for suppression: `_suppress_deprecation_warnings = False`
  - Create decorator that logs warning only once per deprecated function
  - Signature: `def _deprecated(message):`
  - Implementation:
  
    ```python
    def _deprecated(message):
        """Decorator to mark functions as deprecated with one-time warning."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not _suppress_deprecation_warnings:
                    func_name = func.__name__
                    if func_name not in _deprecated_warnings_shown:
                        _deprecated_warnings_shown.add(func_name)
                        logging.warning(f"{func_name}() is deprecated. {message}")
                return func(*args, **kwargs)
            return wrapper
        return decorator
    ```
  
  - Available for Steps 3, 11, 13, and 14 deprecation needs

- **Rename param.py helpers to private:**
  - Rename `get_bind_name()` → `_get_bind_name()`
  - Rename `get_param_default()` → `_get_param_default()`
  - Rename `param_has_default()` → `_param_has_default()`
  - Update 30+ call sites across multiple files:
    - `param.py` internal calls
    - `cli.py` param binding references
    - `config_func.py` config key lookups
    - `help.py` parameter display logic
    - `cycle.py` cycle parameter handling

- **Create file.py for file utilities:**
  - Create new `src/spafw37/file.py` module
  - Move from param.py: `_validate_file_for_reading()`, `_read_file_raw()`
  - Used by both cli.py (`@file` loading) and config_func.py (config file loading)
  - Update imports in param.py, cli.py, config_func.py

- **Move CLI-specific functions from param.py to cli.py:**
  - Move `is_long_alias_with_value()` → `cli._is_long_alias_with_value()` (private)
  - Move `param_in_args()` → `cli._param_in_args()` (private)
  - These are pure CLI token parsing concerns
  - Update call sites in cli.py

- **Module organization summary after Step 2:**
  - **file.py** - File I/O utilities (no domain logic)
    - `_validate_file_for_reading()`, `_read_file_raw()`
  - **param.py** - Parameter metadata and validation
    - Metadata: `is_alias()`, `is_toggle_param()`, `is_list_param()`, `is_dict_param()`, `is_param_alias()`
    - Registry: `get_all_param_definitions()`, `get_pre_parse_args()`
    - Validation: `has_xor_with()`, `get_xor_params()`
  - **cli.py** - CLI token parsing
    - `_is_long_alias_with_value()`, `_param_in_args()`
    - After refactoring: CLI only calls `param.is_alias()` and `param.set_param_value()`

[↑ Back to top](#table-of-contents)

### 3. Create parameter lookup system

**File:** `src/spafw37/param.py`

- **Rename metadata accessors to private:**
  - Rename `get_param_by_name()` → `_get_param_definition()`
  - Rename `get_param_by_alias()` → `_get_param_definition_by_alias()`
  - Update 20+ internal call sites in: `param.py`, `cli.py`, `config_func.py`, `help.py`
  - Create public backward-compat wrappers with deprecation warnings

- **Create `_resolve_param_definition()` helper:**
  - Lookup parameter by name, bind_name, or alias:
    1. **param_name** - parameter name (e.g., `'database-host'`)
    2. **bind_name** - config key (e.g., `'database_host'`)
    3. **alias** - CLI alias (e.g., `'--db-host'`, `-d`)
  
  - **Signature:**
  
    ```python
    def _resolve_param_definition(param_name=None, bind_name=None, alias=None):
    ```
  
  - **Behavior:**
    - **Named argument usage:** Only check specified address space
      - `_resolve_param_definition(param_name='database')` → only check param names
      - `_resolve_param_definition(bind_name='database_host')` → only check bind names
      - `_resolve_param_definition(alias='--db-host')` → only check aliases
    
    - **Positional argument usage:** Use failover pattern (user-friendly)
      - `_resolve_param_definition('database')` → try param_name, then bind_name, then alias
      - Python 3.7 limitation: First positional arg always maps to `param_name`
      - Failover order: name → bind → alias
    
    - **Implementation:**
      - If only `param_name` provided and matches: return `_get_param_definition(param_name)`
      - If only `param_name` provided and no match: try `_get_param_definition_by_bind_name(param_name)`
      - If still no match: try `_get_param_definition_by_alias(param_name)`
      - If `bind_name` provided: only check bind name lookup
      - If `alias` provided: only check alias lookup
      - Return `None` if param not found in specified address space(s)
    
    - **New helper needed:** `_get_param_definition_by_bind_name(bind_name)`
      - Search `_params` list for param where `_get_bind_name(param_def) == bind_name`
      - Return matching param definition or `None`

- **Update public API functions to use `_resolve_param_definition()` internally:**
  - Public functions in `param.py`: `set_param_value()`, `join_param_value()`, all `get_param_*()` functions
  - These functions accept three optional keyword arguments: `param_name=None, bind_name=None, alias=None`
  - First positional arg maps to `param_name` for failover behavior
  - **Call chain:** User calls `set_param_value('database', value='postgres')` → function calls `_resolve_param_definition('database')` → returns param_def → function uses it
  - Example: `set_param_value('database', 'postgres')` → internally tries all three address spaces
  - Example: `set_param_value(bind_name='database_host', value='localhost')` → internally checks only bind names
  - The `_resolve_param_definition()` helper is an internal implementation detail, not exposed to users

[↑ Back to top](#table-of-contents)

### 4. Extract type-specific validation helpers

**File:** `src/spafw37/param.py`

**Implementation order:**

1. Create all validation helper functions
2. Write unit tests for each validator with edge cases
3. Keep existing `_parse_value()` unchanged initially
4. Run existing tests to establish baseline

**Validation helpers to create:**

- Create `_validate_number(value)`:
  - Replace `_parse_number()` silent 0 return
  - Raise `ValueError` for invalid numbers
  - Try `int()` first, then `float()`
  - Return coerced numeric value
- Create `_validate_toggle(param_def)`:
  - Return flipped default: `not bool(param_def.get(PARAM_DEFAULT, False))`
  - No value parameter needed (toggles flip on presence)
- Create `_validate_list(value)`:
  - If value is not a list, wrap in `[value]`
  - Return list as-is if already list
- Create `_validate_dict(value)`:
  - Accept dict directly (return as-is if already dict)
  - Parse JSON strings starting with `{` via `_parse_json_text()`
  - Raise `ValueError` for invalid dict formats (non-dict, non-parseable JSON)
  - **Note:** `@file` loading is CLI concern, not validation concern
  - By the time value reaches validation, CLI has already loaded file contents
- Create `_validate_text(value)`:
  - Pass-through, return value as-is
  - Simplest validator (text accepts anything)

[↑ Back to top](#table-of-contents)

### 5. Create `_validate_param_value()` orchestrator

**File:** `src/spafw37/param.py`

**Implementation order:**

1. Create `_validate_param_value()` using helpers from Step 4
2. Write unit tests for orchestration logic and edge cases
3. Refactor existing code to call `_validate_param_value()` instead of inline validation
4. Run all existing tests to verify no regressions
5. Can optionally deprecate old `_parse_value()` if fully replaced

**Orchestrator function:**

- Private function coordinating validation
- Accept parameters:
  - `param_def` - parameter definition dict
  - `value` - raw value to validate
  - `strict=False` - controls error handling
- Preserve list-joining logic from current `_parse_value()`:
  - If value is list and param is not list type, join with spaces
- Dispatch to type-specific validators:
  - Number params → `_validate_number(value)`
  - Toggle params → `_validate_toggle(param_def)`
  - List params → `_validate_list(value)`
  - Dict params → `_validate_dict(value)`
  - Text params (default) → `_validate_text(value)`
- Handle `strict` mode:
  - When `strict=True`: raise `ValueError` on validation failure
  - When `strict=False`: return default value on validation failure
- Return validated/coerced value

[↑ Back to top](#table-of-contents)

### 6. Refactor CLI parsing to use structured dict approach

**File:** `src/spafw37/cli.py`

**Implementation order:**

1. Create all pattern detection helpers (`_is_command_token()`, etc.)
2. Write unit tests for each detection helper
3. Create all pattern handler helpers (`_handle_command_token()`, etc.)
4. Write unit tests for each handler helper
5. Create new `_parse_cli_args()` function using helpers
6. Write integration tests for `_parse_cli_args()`
7. Update `handle_cli_args()` to use new `_parse_cli_args()`
8. Run all existing CLI tests to verify no regressions
9. Remove old functions (`_parse_command_line()`, `capture_param_values()`, etc.)
10. Verify tests still pass after cleanup

**Note:** file.py module created in Step 2, file utilities already moved

- **Create new `_parse_cli_args()` function:**
  - Simplified parsing logic focused on three token patterns
  - Returns structured dict with commands and params
  
  ```python
  def _parse_cli_args(argv):
      """Parse CLI arguments and return structured dict of commands and params.
      
      Returns:
          dict: {
              'commands': [list of command names],
              'params': {param_name: parsed_value, ...}
          }
      """
  ```

- **Three token patterns to handle:**
  
  1. **Single unquoted string (command):**
     - Check: `command.is_command(token)` AND not prefixed with `-` or `--` AND not quoted
     - **Quoted strings are values:** Check via `_is_quoted_token()` helper
     - Action: Add to `commands` list
     - Example: `build` → `{'commands': ['build']}`
     - Example: `"build"` → NOT a command (quoted value)
  
  2. **Recognized unquoted alias + value tokens:**
     - Check: `param.is_alias(token)` returns True (e.g., `--input`, `-i`) AND not quoted
     - **Quoted aliases are values:** `"--input"` is a value, not an alias
     - Action: Consume following tokens until next **unquoted** alias/command or end
     - Handle `@file` loading for any consumed token starting with `@`
     - **Return raw value (string or list of strings)** - NO type conversion here
     - Type conversion (list→list, string→dict) happens in `set_param_value()`
     - Example: `--files a.txt b.txt` → `{'params': {'--files': ['a.txt', 'b.txt']}}`
     - Example: `--config @settings.json` → `{'params': {'--config': '{"database": "postgres"}'}}`
     - **Key insight:** Use the **CLI identifier** (alias) as dict key, not param name
  
  3. **Long alias with embedded value:**
     - Check: Token matches `--\w+=.+` pattern AND not quoted
     - Action: Split on first `=`, parse alias and value
     - Handle `@file` in value part if present
     - **Use alias (before `=`) as dict key**
     - Example: `--input=data.txt` → `{'params': {'--input': 'data.txt'}}`
     - Example: `--config=@settings.json` → `{'params': {'--config': '{"db": "pg"}'}}`

- **Helper functions to extract/refactor:**
  
  - `_is_quoted_token(token)`:
    - Already exists in cli.py
    - Check if token is wrapped in quotes (`"..."` or `'...'`)
    - Returns True for quoted strings (these are VALUES, not terminators)
  
  - `_load_file_contents(token)`:
    - Check if token starts with `@`
    - Use `file._validate_file_for_reading()` (from new file.py module)
    - Use `file._read_file_raw()` (from new file.py module)
    - Read raw file contents as string
    - Return loaded string (replacing `@filename`)
    - This is the ONLY place `@file` syntax should be handled
  
  - `_parse_token_list_to_value(tokens)`:
    - Simple helper: converts token list to appropriate raw value
    - If 0 tokens: return empty string or None
    - If 1 token: return the single string
    - If multiple tokens: return list of strings
    - **NO type conversion** - just raw strings or list of strings
    - Example: `['a.txt', 'b.txt']` → `['a.txt', 'b.txt']`
    - Example: `['data.txt']` → `'data.txt'`

- **Pattern detection helpers (extract from conditions):**
  
  - `_is_command_token(token)`:
    - Check: `command.is_command(token)` AND not prefixed with `-` AND not quoted
    - Returns True if token is a valid unquoted command
  
  - `_is_long_alias_with_value(token)`:
    - Check: Contains `=` AND starts with `--` AND not quoted
    - Returns True if token matches `--alias=value` pattern
  
  - `_is_alias_token(token)`:
    - Check: `param.is_alias(token)` AND not quoted
    - Returns True if token is a valid unquoted alias
  
  - `_is_terminator_token(token)`:
    - Check: Unquoted AND (is alias OR is command)
    - Returns True if token should stop value consumption
    - Used when consuming value tokens for Pattern 2

- **Pattern handler helpers (extract from nested blocks):**
  
  - `_handle_command_token(token, commands)`:
    - Append token to commands list
    - Return: 1 (tokens consumed)
  
  - `_handle_long_alias_token(token, params)`:
    - Split on first `=` into alias and value
    - Load file contents if value starts with `@`
    - Store in params dict using alias as key
    - Return: 1 (tokens consumed)
  
  - `_handle_alias_with_values(argv, token_index, params)`:
    - Extract alias from argv[token_index]
    - Consume following value tokens until terminator or end
    - Load file contents for any `@file` tokens
    - Convert token list to appropriate value
    - Store in params dict using alias as key
    - Return: number of tokens consumed (1 + value token count)

- **Main parsing loop logic (refactored):**

  ```python
  commands = []
  params = {}
  token_index = 0
  
  while token_index < len(argv):
      token = argv[token_index]
      
      if _is_command_token(token):
          consumed = _handle_command_token(token, commands)
          token_index += consumed
      
      elif _is_long_alias_with_value(token):
          consumed = _handle_long_alias_token(token, params)
          token_index += consumed
      
      elif _is_alias_token(token):
          consumed = _handle_alias_with_values(argv, token_index, params)
          token_index += consumed
      
      else:
          raise ValueError(f"Unknown argument: {token}")
  
  return {'commands': commands, 'params': params}
  ```

- **Implementation notes:**
  - Each pattern handled by single-purpose helper following coding standards
  - Detection logic extracted to clearly-named predicates
  - Nested blocks replaced with focused helper calls
  - Each helper has single responsibility (detect OR handle, not both)
  - Main loop remains clean and readable with flat structure

- **Refactor `handle_cli_args()` to use new approach:**
  
  ```python
  def handle_cli_args(args):
      # Check for help command before processing (KEEP)
      from spafw37 import help as help_module
      if help_module.handle_help_with_arg(args):
          return
      
      # Execute pre-parse actions (e.g., load persistent config) (KEEP)
      _do_pre_parse_actions()
      
      # Pre-parse specific params (e.g., logging/verbosity controls) (REFACTOR)
      # before main parsing to configure behavior
      _pre_parse_params(args)  # Still needed, will use new helpers internally
      
      # Apply logging configuration based on pre-parsed params (KEEP)
      logging_module.apply_logging_config()
      
      # Set defaults for all parameters (KEEP)
      _set_defaults()
      
      # Parse CLI into structured dict (NEW - replaces _parse_command_line)
      parsed = _parse_cli_args(args)
      
      # Process params (NEW - replaces config.set_config_value_from_cmdline)
      # set_param_value() does param resolution from alias
      # set_param_value() also handles list/dict conversion and XOR validation
      for identifier, value in parsed['params'].items():
          param.set_param_value(identifier, value=value, strict=True)
      
      # Execute queued commands (KEEP)
      command.run_command_queue()
      
      # Execute post-parse actions (e.g., save persistent config) (KEEP)
      _do_post_parse_actions()
      
      # After all run-levels, display help if no app-defined commands (KEEP)
      if not command.has_app_commands_queued():
          help_module.display_all_help()
          return
  ```

- **Refactor `_pre_parse_params()` to use new helpers:**
  - Currently uses `_parse_long_alias_with_embedded_value()` and `_parse_short_alias_argument()`
  - These will be replaced by new pattern handlers: `_is_long_alias_with_value()`, `_handle_long_alias_token()`
  - Pre-parse still calls `config.set_config_value_from_cmdline()` → change to `param.set_param_value()`
  - Keep pre-parse functionality intact (logging params must be set early)
  - No need for separate pre-parse parsing logic - can reuse new helpers

- **Keep `_set_defaults()` function:**
  - Currently iterates param definitions and calls `config.set_config_value(param_def, value)`
  - Change to call `param.set_param_value(param_name=name, value=value, strict=False)`
  - Extract param name from definition for new API
  - Keep toggle default logic (get_param_default with False fallback)

- **Keep pre/post-parse action hooks:**
  - `_do_pre_parse_actions()` - unchanged
  - `_do_post_parse_actions()` - unchanged
  - These are extension points for persistence, logging setup, etc.

- **Critical dependencies to preserve:**
  - Help command check MUST happen before any parsing (`help_module.handle_help_with_arg(args)`)
  - Pre-parse actions MUST run before param parsing (loads persistent config)
  - Pre-parse params MUST be processed before logging config (sets log levels)
  - Logging config MUST be applied before main parsing (enables proper logging)
  - Defaults MUST be set before parsing (provides fallback values)
  - Post-parse actions MUST run after commands (saves persistent config)
  - Help display MUST be last (only if no app commands queued)
  - Command queueing happens during parsing, execution happens after all params set

- **Functions to deprecate/remove:**
  - `_parse_command_line()` - replaced by `_parse_cli_args()` with helper-based structure
  - `capture_param_values()` - replaced by `_handle_alias_with_values()` helper
  - `_handle_alias_param()` - replaced by `_handle_alias_with_values()` and `_is_alias_token()` helpers
  - `_handle_long_alias_param()` - replaced by `_handle_long_alias_token()` and `_is_long_alias_with_value()` helpers
  - `_handle_command()` - replaced by `_handle_command_token()` and `_is_command_token()` helpers
  - `test_switch_xor()` - **REMOVE** XOR validation moved to param layer (`_validate_xor_conflicts()`)
  - `_current_args` global - **REMOVE** no longer needed with new parsing approach
  - `_accumulate_json_for_dict_param()` - **REMOVE** dict parsing handled by param layer validation

- **Result of CLI cleanup:**
  - CLI no longer needs XOR functions (has_xor_with, get_xor_params, param_in_args)
  - CLI no longer needs type checking (is_toggle_param, is_list_param, is_dict_param)
  - CLI only needs: `param.is_alias()` to detect param aliases during parsing
  - All validation, type conversion, and XOR checking happens in param.set_param_value()

- **Create new `file.py` module for file I/O utilities:**
  - Create `src/spafw37/file.py` for file operations shared across modules
  - Move file helpers here:
    - `_validate_file_for_reading(file_path)` - used by cli.py (for `@file` loading) AND config_func.py (for config file loading)
    - `_read_file_raw(file_path)` - used by cli.py for `@file` token expansion
  - These are generic file I/O utilities with no domain-specific logic
  - Both cli.py and config_func.py will import from file.py

- **CLI-specific helper functions (keep/move to cli.py):**
  - `is_long_alias_with_value(arg)` → **MOVE to cli.py** as `_is_long_alias_with_value()`
    - Pure CLI token parsing concern - checks if token matches `--alias=value` pattern
    - Param module never needs to parse tokens this way
    - Currently used in: cli.py capture_param_values, _pre_parse_params
  - `param_in_args(param_name, args)` → **MOVE to cli.py** as `_param_in_args()`
    - Searches CLI args list for param presence
    - Only used by CLI's `test_switch_xor()` function
    - Pure CLI concern, param module doesn't work with raw args lists

- **Param-specific helper functions (stay in param.py):**
  - `is_alias(alias)` - checks if string is registered param alias (param registry concern)
  - `is_toggle_param(param_def)` - checks param type (param metadata concern)
  - `is_list_param(param_def)` - checks param type (param metadata concern)
  - `is_dict_param(param_def)` - checks param type (param metadata concern)
  - `is_param_alias(param_def, alias)` - checks if alias belongs to param (param metadata concern)
  - `get_xor_params(param_name)` - gets conflicting params (param validation concern)
  - `has_xor_with(param_name, other)` - checks XOR relationship (param validation concern)
  - `get_all_param_definitions()` - retrieves all params (param registry concern)
  - `get_pre_parse_args()` - retrieves pre-parse params (param registry concern)
  - **NOTE:** XOR functions (has_xor_with, get_xor_params) used by CLI's test_switch_xor()
  - **AFTER REFACTORING:** test_switch_xor() will be REMOVED (XOR moves to param layer)
  - **RESULT:** All these functions become internal param concerns only

- **Functions CLI uses that will remain in param.py:**
  - `is_alias(alias)` - CLI needs to detect if token is a param alias
  - Type checking functions (is_toggle_param, is_list_param, is_dict_param) - CLI uses during capture_param_values
  - **AFTER REFACTORING:** CLI won't need type checkers (no type-specific logic in CLI)
  - **RESULT:** CLI only calls param.set_param_value() which handles all type logic internally

- **Helper functions being RENAMED in Step 2/3 (CLI must use new names):**
  - `get_bind_name()` → `_get_bind_name()` - CLI uses this in test_switch_xor, _set_defaults
  - `get_param_default()` → `_get_param_default()` - CLI uses in _set_defaults, _extract_param_value_from_next_argument
  - `param_has_default()` → `_param_has_default()` - CLI uses in _set_defaults
  - `get_param_by_alias()` → kept public (CLI needs it for pre-parse)
  - `get_param_by_name()` → kept public (not currently used by CLI directly)

- **Remove config_func from CLI flow:**
  - Remove all calls to `config_func.set_config_value_from_cmdline()`
  - CLI calls `param.set_param_value()` directly for all param setting
  - XOR validation happens automatically in param layer via `_validate_xor_conflicts()`
  - Persistence management happens in param layer via config_func helper call

[↑ Back to top](#table-of-contents)

### 7. Add `set_param_value()` function

**File:** `src/spafw37/param.py`

**Implementation order:**

1. Create `set_param_value()` function
2. Write unit tests for all resolution modes (name/bind/alias/failover)
3. Write tests for validation integration and error handling
4. Update internal code to use `set_param_value()` where appropriate
5. Run all existing tests to verify behavior
6. Add edge case tests (unknown params, XOR conflicts, etc.)

**Function specification:**

- Public function for setting param values
- **Signature:**

  ```python
  def set_param_value(param_name=None, bind_name=None, alias=None, value=None, strict=True):
  ```

- **Parameters:**
  - First three are mutually exclusive identifiers (one required)
  - `value` - value to set (required)
  - `strict` - validation mode (default True for programmatic correctness)

- **Implementation:**
  - Resolve param: `param_def = _resolve_param_definition(param_name, bind_name, alias)`
  - Raise `ValueError` if param not found: `f"Unknown parameter"`
  - Check XOR conflicts for toggles: `_validate_xor_conflicts(param_def)` (see Step 9)
  - Validate value: `validated_value = _validate_param_value(param_def, value, strict)`
  - Get config key: `config_key = _get_bind_name(param_def)`
  - Store value: `config.set_config_value(config_key, validated_value)`
  - Log: `f"Set param '{config_key}' = {validated_value}"`
  - Manage persistence: Call config_func helper (see Step 13)

- **Usage examples:**
  - `set_param_value('database', value='postgres')` → failover resolution
  - `set_param_value(param_name='database-host', value='localhost')` → name only
  - `set_param_value(bind_name='database_host', value='localhost')` → bind only
  - `set_param_value(alias='--db-host', value='localhost')` → alias only

[↑ Back to top](#table-of-contents)

### 8. Add `join_param_value()` function

**File:** `src/spafw37/param.py`

- Public function for accumulating/appending values
- **Signature:**

  ```python
  def join_param_value(param_name=None, bind_name=None, alias=None, value=None):
  ```

- **Parameters:**
  - First three are mutually exclusive identifiers (one required)
  - `value` - value to join/append (required)

- Create type-specific join helpers:
  - `_deep_merge_dicts(dict1, dict2, override_strategy)`:
    - Helper for deep dict merging
    - Recursively merge nested dictionaries
    - Apply override_strategy at each level when keys conflict
    - If value is dict in both: recurse
    - If value is not dict: apply override_strategy
    - Return merged dict
  
  - `_join_list_value(existing, new)`:
    - If existing is None/missing, create new list
    - If new is list, extend existing list
    - If new is single value, append to existing list
    - Return updated list
  - `_join_string_value(existing, new, separator)`:
    - Get separator from `param_def.get(PARAM_JOIN_SEPARATOR, ' ')`
    - If existing is None/missing, return new value
    - Concatenate: `existing + separator + new`
    - Return concatenated string
  - `_join_dict_value(existing, new, param_def)`:
    - If existing is None/missing, return new dict
    - Get merge type: `param_def.get(PARAM_DICT_MERGE_TYPE, DICT_MERGE_SHALLOW)` (default: SHALLOW)
    - Get override strategy: `param_def.get(PARAM_DICT_OVERRIDE_STRATEGY, DICT_OVERRIDE_RECENT)` (default: RECENT)
    - **Shallow merge (default):** `{**existing, **new}` for top-level keys only
    - **Deep merge:** Recursively merge nested dicts using `_deep_merge_dicts(existing, new, override_strategy)`
    - **Override handling:**
      - `DICT_OVERRIDE_RECENT` (default): Last value wins (standard dict update behavior)
      - `DICT_OVERRIDE_OLDEST`: Keep existing values, only add new keys
      - `DICT_OVERRIDE_ERROR`: Raise `ValueError` if any keys conflict
    - Return merged dict

- **Implementation:**
  - Resolve param: `param_def = _resolve_param_definition(param_name, bind_name, alias)`
  - Raise `ValueError` if param not found
  - Raise `ValueError` for number/toggle params (cannot join)
  - Get current value from config
  - Dispatch to type-specific joiner based on param type
  - Store updated value via `config.set_config_value()`

- Used by CLI during parsing for multiple param occurrences
- Available for user code to incrementally build values

[↑ Back to top](#table-of-contents)

### 9. Add XOR validation for toggle params

**File:** `src/spafw37/param.py`

- Create `_validate_xor_conflicts(param_def)`:
  - Get param bind name via `_get_bind_name(param_def)`
  - Get conflicting params: `xor_params = get_xor_params(bind_name)`
  - Check if any conflicting toggle already set in config
  - Raise `ValueError` if conflict: `f"Cannot set '{bind_name}', conflicts with '{xor_param}'"`
- Integrate into `set_param_value()`:
  - Call before validation for toggle params
  - If `is_toggle_param(param_def)`: `_validate_xor_conflicts(param_def)`
- Move XOR unsetting logic from `config_func.set_config_value_from_cmdline()`:
  - Remove XOR handling from CLI layer
  - Consolidate toggle mutual exclusion in param layer
- Simplifies CLI code by centralizing toggle logic

[↑ Back to top](#table-of-contents)

### 10. Add typed param getters

**File:** `src/spafw37/param.py`

- **Create base getter:**

  ```python
  def get_param_value(param_name=None, bind_name=None, alias=None, default=None, strict=False):
  ```
  
  - Resolve param: `param_def = _resolve_param_definition(param_name, bind_name, alias)`
  - If not found and `strict=True`: raise `ValueError`
  - If not found and `strict=False`: return default
  - Get config key: `config_key = _get_bind_name(param_def)`
  - Retrieve from config: `config.get_config_value(config_key)`
  - Return raw value or default if missing

- **Create typed getters:**
  
  - `get_param_str(param_name=None, bind_name=None, alias=None, default='', strict=False)`:
    - Get value via `get_param_value()`
    - Coerce to string: `str(value)`
    - Examples: `123.0` → `"123.0"`, `['a', 'b']` → `"['a', 'b']"`
    - Handle coercion errors per `strict` mode
  
  - `get_param_int(param_name=None, bind_name=None, alias=None, default=0, strict=False)`:
    - Get value via `get_param_value()`
    - Coerce to int via truncation: `int(float(value))`
    - Examples: `"123"` → `123`, `"3.14"` → `3`, `3.99` → `3`
    - If `strict=True` and coercion fails: raise `ValueError`
    - If `strict=False` and coercion fails: return default
  
  - `get_param_bool(param_name=None, bind_name=None, alias=None, default=False, strict=False)`:
    - Get value via `get_param_value()`
    - Coerce using Python's `bool()` (truthy/falsy)
    - Examples: `"yes"` → `True`, `0` → `False`, `[]` → `False`
  
  - `get_param_float(param_name=None, bind_name=None, alias=None, default=0.0, strict=False)`:
    - Get value via `get_param_value()`
    - Coerce to float: `float(value)`
    - Examples: `"123"` → `123.0`, `"3.14"` → `3.14`
  
  - `get_param_list(param_name=None, bind_name=None, alias=None, default=None, strict=False)`:
    - Get value via `get_param_value()`
    - Return as-is (no coercion)
    - Default to empty list if default is None
  
  - `get_param_dict(param_name=None, bind_name=None, alias=None, default=None, strict=False)`:
    - Get value via `get_param_value()`
    - Return as-is (no coercion)
    - Default to empty dict if default is None

- **Usage examples:**
  - `get_param_str('database')` → failover resolution
  - `get_param_int(bind_name='max_connections', default=100)` → bind only
  - `get_param_bool(alias='--verbose')` → alias only

[↑ Back to top](#table-of-contents)

### 11. Export param API through `core.py` facade

**File:** `src/spafw37/core.py`

- Create `_deprecated(message)` decorator:
  - Use module-level set to track called functions (singleton pattern)
  - Log warning only once per deprecated function
  - Warning message includes function name and alternative
  - Example: `"get_config_str() is deprecated. Use get_param_str() instead. Will be removed in v2.0.0"`

- Add deprecation control API:
  - `suppress_deprecation(suppress=True)` → public function to control warning display
  - Sets module-level `_suppress_deprecation_warnings` flag
  - Developer calls this at app startup to silence warnings during migration
  - Example: `spafw37.suppress_deprecation()` to silence all
  - Example: `spafw37.suppress_deprecation(False)` to re-enable

- Add new public param API methods:
  - `set_param(param_name, value)` → wraps `param.set_param_value()`
  - `join_param(param_name, value)` → wraps `param.join_param_value()`
  - `get_param_str(param_name, default='', strict=False)` → wraps `param.get_param_str()`
  - `get_param_int(param_name, default=0, strict=False)` → wraps `param.get_param_int()`
  - `get_param_bool(param_name, default=False, strict=False)` → wraps `param.get_param_bool()`
  - `get_param_float(param_name, default=0.0, strict=False)` → wraps `param.get_param_float()`
  - `get_param_list(param_name, default=None, strict=False)` → wraps `param.get_param_list()`
  - `get_param_dict(param_name, default=None, strict=False)` → wraps `param.get_param_dict()`
- Mark old config API as deprecated:
  - `@_deprecated("Use get_param_str() instead. Will be removed in v2.0.0")` on `get_config_str()`
  - `@_deprecated("Use get_param_int() instead. Will be removed in v2.0.0")` on `get_config_int()`
  - `@_deprecated("Use get_param_bool() instead. Will be removed in v2.0.0")` on `get_config_bool()`
  - `@_deprecated("Use get_param_float() instead. Will be removed in v2.0.0")` on `get_config_float()`
  - `@_deprecated("Use get_param_list() instead. Will be removed in v2.0.0")` on `get_config_list()`
  - `@_deprecated("Use get_param_dict() instead. Will be removed in v2.0.0")` on `get_config_dict()`
  - `@_deprecated("Use set_param() instead. Will be removed in v2.0.0")` on `set_config_value()`

[↑ Back to top](#table-of-contents)

### 12. Refactor CLI layer

**File:** `src/spafw37/cli.py`

- Replace all `config_func.set_config_value()` calls with `param.join_param_value()`:
  - Line 184: Setting parsed param from command line
  - Line 248: Setting toggle defaults
  - Line 251: Setting param defaults
  - Line 368: Setting pre-parsed param values
- Keep `_parse_value()` for structuring CLI tokens:
  - Still needed to convert CLI token arrays into proper values
  - Example: `['hello', 'world']` → `'hello world'` for text params
  - Example: `['a.txt', 'b.txt']` → `['a.txt', 'b.txt']` for list params
- Remove XOR handling from CLI layer:
  - Delete XOR conflict checking code
  - XOR validation now handled in `param.set_param_value()`
- Update pre-parse flow:
  - Use `param.join_param_value()` for early param setting
  - Maintain same behavior for logging config

[↑ Back to top](#table-of-contents)

### 13. Deprecate and refactor `config_func.py` param-setting functions

**File:** `src/spafw37/config_func.py`

- Mark `set_config_value(param_def, value)` as deprecated:
  - Add `@_deprecated("Internal function deprecated. Will be removed in 2.0.0. Use param.set_param_value() instead.")`
  - Refactor body to thin wrapper calling `param.set_param_value(param_name, value)` once it exists
  - Extract param name from `param_def[PARAM_NAME]` to pass to new function
  - Maintains backward compatibility during transition
- Mark `set_config_value_from_cmdline(param_def, value)` as deprecated:
  - Add `@_deprecated("Internal function deprecated. Will be removed in 2.0.0. Use param.set_param_value() with strict=True instead.")`
  - Refactor body to thin wrapper calling `param.set_param_value(param_name, value, strict=True)`
  - Remove XOR handling code (now handled in param layer)
  - Extract param name from `param_def[PARAM_NAME]`
- Refactor `_manage_config_persistence()` signature and implementation:
  - Change signature from `_manage_config_persistence(param_def, value)` to `_manage_config_persistence(param_name, value)`
  - Remove internal `get_bind_name()` calls
  - Delegate persistence type checking to new public param.py functions:
    - Call `param.is_persistence_never(param_name)` instead of checking param_def
    - Call `param.is_persistence_always(param_name)` instead of checking param_def
  - Get bind name via `param._get_bind_name()` (after looking up param) for storing in tracking lists
  - Will be called by `param.set_param_value()` after successfully setting value
- Make persistence checkers in `param.py` public and param-name-based:
  - Change `is_persistence_never(param_def)` to accept `param_name` string
  - Change `is_persistence_always(param_def)` to accept `param_name` string
  - Both functions internally call `_get_param_definition(param_name)` then check the param dict
  - Allows config_func to check persistence without having param definition
- Keep config persistence management:
  - `load_persistent_config()` - loads config.json at startup
  - `save_persistent_config()` - saves config.json at shutdown
- Keep config file operations:
  - `load_config()` - loads JSON config file
  - `save_config()` - saves JSON config file
  - `load_user_config()` - loads user-specified config
  - `save_user_config()` - saves user-specified config
  - `get_filtered_config_copy()` - excludes non-persistent params
- Keep application metadata:
  - `set_app_name()` / `get_app_name()` - application name management
  - `set_config_file()` - sets persistent config file path

[↑ Back to top](#table-of-contents)

### 14. Deprecate `config.set_config_list_value()`

**File:** `src/spafw37/config.py`

- Mark `set_config_list_value()` with `@_deprecated`:
  - Message: "Use join_param() for accumulation or set_param() for replacement. Will be removed in v2.0.0"
- Function replaced by:
  - `join_param()` for appending to lists (CLI use case)
  - `set_param()` for replacing entire list (user code use case)
- Keep function implementation for backward compatibility
- Remove usage from internal code (replaced by param API)

[↑ Back to top](#table-of-contents)

### 15. Update examples

**Files:** 20+ files in `examples/` directory

- Replace all config API calls with param API:
  - `spafw37.get_config_str()` → `spafw37.get_param_str()`
  - `spafw37.get_config_int()` → `spafw37.get_param_int()`
  - `spafw37.get_config_bool()` → `spafw37.get_param_bool()`
  - `spafw37.get_config_float()` → `spafw37.get_param_float()`
  - `spafw37.get_config_list()` → `spafw37.get_param_list()`
  - `spafw37.get_config_dict()` → `spafw37.get_param_dict()`

- Update cycle examples to use param API:
  - `cycles_basic.py` - Use `spafw37.set_param('loop-counter', value)` for loop counter management
  - `cycles_loop_start.py` - Use `spafw37.set_param()` for loop state tracking
  - `cycles_nested.py` - Use `spafw37.set_param()` for nested loop variables
  - Replace all `config.set_config_value()` with `spafw37.set_param()`
  - Demonstrates best practice: param API for all user-facing code

- Add new example demonstrating `PARAM_JOIN_SEPARATOR`:
  - Create `examples/params_join_separator.py`
  - Show default space separator behavior
  - Show custom comma separator for CSV tags
  - Demonstrate `join_param()` usage
  - Example: `--tags python --tags cli --tags framework` → `"python,cli,framework"`

[↑ Back to top](#table-of-contents)

### 16. Update documentation

**Files:** `doc/parameters.md`, `doc/configuration.md`, `doc/commands.md`, `doc/api-reference.md`, `doc/README.md`

- `doc/parameters.md`:
  - Replace 18+ config API code examples with param API
  - Add `PARAM_JOIN_SEPARATOR` documentation:
    - Table entry in "Parameter Definition Constants" section
    - Usage examples showing default space separator
    - Usage examples showing custom separators (comma, pipe, newline)
  - Add `PARAM_TEXT_FILTER` documentation:
    - Table entry in "Parameter Definition Constants" section
    - Explain purpose: custom input processing before validation
    - Show example with dict params accepting shell-friendly single quotes
    - Document that framework provides sensible defaults for each param type
  - Document `join_param()` vs `set_param()` semantics:
    - `set_param()` replaces entire value
    - `join_param()` accumulates/appends to existing value
    - Type-specific join behavior (list append, string concat, dict merge)
  - Add dict parameter advanced features:
    - Multiple dict blocks: `--config {"a":1} {"b":2}` merges into single dict
    - File references in JSON: `--config {'data': @file.json}` loads file content into JSON structure
    - Shell-friendly quotes: Single quotes `{'key':'value'}` automatically converted to valid JSON
    - Note: email addresses like `user@example.com` correctly ignored (not treated as file references)
  - Document `strict` parameter for getters:
    - `strict=False` (default): returns default on missing param or coercion error
    - `strict=True`: raises `ValueError` on missing param or coercion error
    - When to use each mode
- `doc/configuration.md`:
  - Replace 10+ config API references with param API
  - Update configuration binding examples
  - Clarify distinction between params (validated, typed) and config (raw storage)
- `doc/commands.md`:
  - Replace 8+ command implementation examples with param API
  - Update examples showing param access in command actions
  - Show `strict=True` usage for required params in commands
- `doc/api-reference.md`:
  - Add new "Parameter API" section with tables:
    - `set_param(param_name, value)` - Set parameter value (replacement)
    - `join_param(param_name, value)` - Accumulate parameter value
    - `get_param_str/int/bool/float/list/dict()` - Typed getters
  - Move old config API to "Deprecated API" section:
    - Mark as deprecated with removal timeline (v2.0.0)
    - Link to new param API equivalents
    - Migration examples showing before/after
  - Document type coercion rules:
    - Int truncation: `int(float(value))` for `"3.14"` → `3`
    - Bool truthy/falsy: Python's `bool()` semantics
    - String conversion: `str(value)` for all types
    - Float conversion: `float(value)` with error handling
  - Document `strict` parameter behavior in detail
- `doc/README.md`:
  - Update quick start examples with param API
  - Update "Getting Started" code samples
  - Add note about backward compatibility via deprecation warnings

[↑ Back to top](#table-of-contents)

### 17. Create CHANGES.md for issue closing comment

**File:** `features/issue-27-config-focus-to-param/CHANGES.md`

This file will be posted as the closing comment on Issue #27 and consumed by the release workflow.

- Create structured changes document for v1.1.0:
  - **Breaking Changes** section:
    - API pivot from config-focused to param-focused
    - Rationale: leverage parameter metadata for validation
    - Benefits: type safety, required param enforcement, cleaner semantics
  
  - **Deprecated APIs** section with removal timeline:
    - `get_config_str/int/bool/float/list/dict()` → removed in v2.0.0
    - `set_config_value()` → removed in v2.0.0
    - `set_config_list_value()` → removed in v2.0.0
    - `config_func.set_config_value()` → removed in v2.0.0
    - `config_func.set_config_value_from_cmdline()` → removed in v2.0.0
  
  - **Migration Examples** section:
    - Before: `spafw37.get_config_str('input-file')`
    - After: `spafw37.get_param_str('input-file')`
    - Before: `spafw37.set_config_value('count', 5)`
    - After: `spafw37.set_param('count', 5)`
    - Before: Multiple calls to build list
    - After: `spafw37.join_param('files', 'new.txt')`
  
  - **New Features** section:
    - `strict` mode for getters (missing param and coercion error handling)
    - Type coercion in getters (string→int, int→string, etc.)
    - XOR validation moved to param layer (cleaner toggle handling)
    - `join_param()` for accumulation use cases
    - `PARAM_JOIN_SEPARATOR` for custom string concatenation
    - Dict merge configuration (`PARAM_DICT_MERGE_TYPE`, `PARAM_DICT_OVERRIDE_STRATEGY`)
    - Common separator constants (SEPARATOR_COMMA, SEPARATOR_NEWLINE, etc.)
    - `suppress_deprecation()` API for migration control
  
  - **Backward Compatibility** section:
    - Deprecation warnings logged on first call
    - Old API still works in v1.1.0
    - Allows gradual migration
    - Use `spafw37.suppress_deprecation()` to silence warnings during migration

- **Workflow:**
  1. Post CHANGES.md content as closing comment on Issue #27
  2. Release workflow fetches closing comments from issues in the release
  3. AI generates CHANGELOG.md from issue closing comments + commit diffs
  4. Human-written migration examples preserved in final changelog
  5. Issue serves as source of truth for what changed and why

[↑ Back to top](#table-of-contents)

### 18. Update tests

**Files:** 11 test files in `tests/` directory

- Refactor existing tests to use new param API:
  - `test_cli.py` - CLI parsing and param setting
  - `test_config.py` - Config persistence and loading
  - `test_param_dict.py` - Dict parameter handling
  - `test_cycle.py` - Cycle execution with params
- Add new validation tests in `test_param.py`:
  - `test_validate_number_strict_invalid` - `ValueError` on invalid number with `strict=True`
  - `test_validate_number_strict_valid` - Successful coercion with `strict=True`
  - `test_validate_dict_invalid_json` - `ValueError` on malformed JSON
  - `test_validate_toggle_default_flip` - Toggle flips default correctly
- Add new getter tests in `test_param.py`:
  - `test_get_param_strict_mode_missing` - `ValueError` on unknown param with `strict=True`
  - `test_get_param_strict_mode_found` - Successful retrieval with `strict=True`
  - `test_get_param_int_coercion` - `"123"` → `123`, `"3.14"` → `3`
  - `test_get_param_str_coercion` - `123` → `"123"`, `3.14` → `"3.14"`
  - `test_get_param_bool_truthy` - `"yes"` → `True`, `1` → `True`, `"true"` → `True`
  - `test_get_param_bool_falsy` - `""` → `False`, `0` → `False`, `[]` → `False`
  - `test_get_param_float_coercion` - `"3.14"` → `3.14`, `"123"` → `123.0`
- Add XOR validation tests in `test_param.py`:
  - `test_xor_validation_conflict` - Toggle mutual exclusion raises `ValueError`
  - `test_xor_validation_no_conflict` - Non-conflicting toggles work
- Add setter tests in `test_param.py`:
  - `test_set_param_value_unknown_param` - Unknown param raises `ValueError`
  - `test_set_param_value_replaces` - `set_param()` replaces value
  - `test_set_param_value_list_replaces` - List params replaced, not appended
- Add join tests in `test_param.py`:
  - `test_join_param_string_default_separator` - Space separator by default
  - `test_join_param_string_custom_separator` - `PARAM_JOIN_SEPARATOR` respected
  - `test_join_param_list_accumulation` - Multiple `join_param()` calls append
  - `test_join_param_dict_merge` - Dict merging behavior (last wins)
  - `test_join_param_number_error` - `ValueError` on join attempt for number
  - `test_join_param_toggle_error` - `ValueError` on join attempt for toggle
- Ensure 80%+ coverage per `setup.cfg` pytest config:
  - Run `pytest --cov=spafw37 --cov-report=term-missing`
  - Add tests for any uncovered branches
  - Focus on error handling paths (strict mode, validation failures)

[↑ Back to top](#table-of-contents)

## Further Considerations

### 1. Dict merge semantics for `join_param()` - RESOLVED

**Decision:** Configurable via parameter definition constants (Step 1).
**Defaults:** `DICT_MERGE_SHALLOW` + `DICT_OVERRIDE_RECENT`

When calling `join_param('config', {"a": 1})` then `join_param('config', {"b": 2})`:

- **Merge type** controlled by `PARAM_DICT_MERGE_TYPE`:
  - `DICT_MERGE_SHALLOW` (default): Top-level keys only, entire nested dicts replaced
  - `DICT_MERGE_DEEP`: Recursive merge of nested dictionaries

- **Key conflicts** controlled by `PARAM_DICT_OVERRIDE_STRATEGY`:
  - `DICT_OVERRIDE_RECENT` (default): Last value wins → `{"a": 2}`
  - `DICT_OVERRIDE_OLDEST`: First value wins → `{"a": 1}`
  - `DICT_OVERRIDE_ERROR`: Raise `ValueError` on any key conflict

- **Example parameter definitions:**

  ```python
  # Default behavior: shallow merge, recent wins
  {PARAM_NAME: 'config', PARAM_TYPE: PARAM_TYPE_DICT}
  
  # Deep merge with error on conflicts
  {PARAM_NAME: 'settings', PARAM_TYPE: PARAM_TYPE_DICT,
   PARAM_DICT_MERGE_TYPE: DICT_MERGE_DEEP,
   PARAM_DICT_OVERRIDE_STRATEGY: DICT_OVERRIDE_ERROR}
  
  # Shallow merge, preserve first values
  {PARAM_NAME: 'defaults', PARAM_TYPE: PARAM_TYPE_DICT,
   PARAM_DICT_OVERRIDE_STRATEGY: DICT_OVERRIDE_OLDEST}
  ```

- **Implementation:** `_join_dict_value()` and `_deep_merge_dicts()` in Step 8

[↑ Back to top](#table-of-contents)

### 2. Deprecation warning verbosity control - RESOLVED

**Decision:** Developer-facing API in `core.py` (Step 11).

Current `@_deprecated` decorator logs once per function (singleton pattern).

- **Public API control:** `spafw37.suppress_deprecation(suppress=True)`
  - Developer responsibility: Control warnings at application level
  - Called at app startup before using deprecated APIs
  - Example:

    ```python
    import spafw37
    spafw37.suppress_deprecation()  # Silence all deprecation warnings
    # ... rest of app code using deprecated APIs during migration
    ```

  - Use case: Applications mid-migration that can't update all code immediately
  - Not end-user facing: No environment variables, no user configuration

- **Rationale:**
  - Developer problem: Deprecation warnings are for developers, not end users
  - Migration control: Allows gradual migration without warning spam
  - Professional UX: End users shouldn't see framework deprecation warnings
  - Clear ownership: Developer explicitly opts out, not end user configuration

- **Verbose mode (future consideration):**
  - Could add `suppress_deprecation(verbose=True)` mode
  - Logs every call instead of once per function
  - Useful during testing to identify all deprecated usage points
  - Not in v1.1.0 scope

[↑ Back to top](#table-of-contents)

### 3. Type coercion failure messages - RESOLVED

**Decision:** Log at DEBUG level (Step 10).

When `get_param_int('foo')` fails to coerce value and `strict=False`:

- **Log at DEBUG level** before returning default
  - Message format: `"Failed to coerce param '{param_name}' to {type}, returning default: {error_msg}"`
  - Example: `"Failed to coerce param 'port' to int, returning default: invalid literal for int() with base 10: 'abc'"`
  - Visible when logging level set to DEBUG or lower
  - Not visible by default (INFO level)
  - Available for debugging when needed

- **Rationale:**
  - No log noise: Doesn't spam logs in production
  - Available when needed: Visible in verbose/debug mode
  - Helps debugging: Shows why default was returned
  - Respects strict mode: If developer wants errors, they use `strict=True`

- **Implementation:** Add debug logging in typed getters (Step 10)

[↑ Back to top](#table-of-contents)

### 4. String join edge cases - RESOLVED

**Decision:** Flexible separator support with sensible defaults (Steps 1, 8).

`PARAM_JOIN_SEPARATOR` edge case handling:

- **Empty string separator (`''`):** Concatenate directly
  - Example: `"hello"` + `"world"` → `"helloworld"`
  - Valid use case

- **Whitespace separators:** Allow `\n`, `\t`, `\r`, etc.
  - Example: `PARAM_JOIN_SEPARATOR: '\n'` for multi-line text
  - Example: `PARAM_JOIN_SEPARATOR: '\t'` for tab-separated values
  - Valid use case

- **None separator:** Use default space `' '`
  - If `PARAM_JOIN_SEPARATOR` not in param definition: default to `' '`
  - If `PARAM_JOIN_SEPARATOR: None`: treat as missing, default to `' '`

- **Multi-character separators:** Fully supported
  - Example: `', '` for CSV with space
  - Example: `' | '` for pipe-separated with padding
  - Example: `' :: '` for double-colon separator
  - No technical limitation

- **Common separator constants (Step 1):**
  - Add to `constants/param.py` for convenience
  - `SEPARATOR_SPACE = ' '` (default)
  - `SEPARATOR_COMMA = ','`
  - `SEPARATOR_COMMA_SPACE = ', '`
  - `SEPARATOR_PIPE = '|'`
  - `SEPARATOR_PIPE_PADDED = ' | '`
  - `SEPARATOR_NEWLINE = '\n'`
  - `SEPARATOR_TAB = '\t'`
  - Note in docs: Any string value allowed, constants are for convenience only

- **Documentation (Step 16):**
  - Show examples with common separators
  - Clarify that any string is valid
  - Show empty string and multi-character examples

[↑ Back to top](#table-of-contents)

### 5. Private method testing approach - RESOLVED

**Decision:** Test everything - both isolated and integrated (Step 18).

Current tests call `_parse_value()` directly (13 matches).

- **Test private methods in isolation:**
  - Pro: Better coverage of internal logic, easier to debug failures
  - Pro: Tests edge cases and error paths thoroughly
  - Pro: Documents expected behavior of internal helpers
  - Example: Test `_validate_number()` with various invalid inputs
  - Example: Test `_deep_merge_dicts()` with complex nested structures

- **Test public API for integration:**
  - Pro: Tests public behavior, less brittle during refactoring
  - Pro: Validates end-to-end workflows
  - Example: Test `set_param()` → validates → stores correctly
  - Example: Test `get_param_int()` → retrieves → coerces correctly

- **Implementation strategy:**
  - Keep existing `_parse_value()` tests (isolated helper tests)
  - Add new public API tests (integration tests)
  - Add isolated tests for new helpers (`_validate_number()`, `_deep_merge_dicts()`, etc.)
  - Test both normal paths and error handling
  - Test edge cases in isolation, common cases in integration

- **Coverage target:**
  - 80% minimum (enforced by CI/CD)
  - 90% target for new code
  - Focus on error paths and edge cases

[↑ Back to top](#table-of-contents)

### 6. Parameter lookup usage patterns - RESOLVED

**Decision:** Document both patterns with clear guidelines (Step 16).

The `_resolve_param_definition()` helper supports three lookup methods:

- **Failover mode (user-friendly):** `set_param_value('database', value='postgres')`
  - Tries param_name → bind_name → alias until match found
  - Best for: Interactive use and simple scripts
  - Best for: Example code demonstrating user-friendly API
  - Risk: Ambiguity if same string exists in multiple address spaces
  
- **Named argument mode (explicit):** `set_param_value(bind_name='database_host', value='localhost')`
  - Only checks specified address space
  - Best for: Programmatic use where param identity is certain
  - Best for: Internal framework code (cli.py, config_func.py)
  - Prevents unexpected matches from other address spaces
  
- **Usage guidelines (documented in Step 16):**
  - **Framework code:** Use named arguments for clarity and correctness
    - Example: `cli.py` uses `param.set_param_value(alias='--db-host', value=...)`
    - Example: `config_func.py` uses `param.set_param_value(bind_name='database_host', value=...)`
  - **Example code:** Use failover mode to demonstrate user-friendly API
    - Example: `examples/params_basic.py` shows `spafw37.set_param('database', 'postgres')`
  - **User code:** Developers choose based on their needs
    - Failover mode: Quick scripts, prototypes, when identifier is unambiguous
    - Named mode: Production code, when precision is required

- **Documentation (Step 16):**
  - Show both patterns with examples
  - Explain when to use each
  - Note framework code consistency (always uses named arguments internally)

[↑ Back to top](#table-of-contents)

### 7. Migration path for `set_config_list_value()` users - RESOLVED

**Decision:** All non-framework code uses param API exclusively (Steps 15, 16).

Current usage analysis:

- Cycle examples use `config.set_config_value()` for loop variables (runtime state)
- These ARE params if they need to be set/retrieved by user code
- Distinction: All user-accessible values should go through param API

**Updated approach:**

- **Use param API everywhere in examples and documentation:**
  - `spafw37.set_param()` for setting any value (including loop counters, runtime state)
  - `spafw37.get_param_int()`, `spafw37.get_param_str()`, etc. for getting values
  - Cycles examples: Use `set_param('loop-counter', value)` not `config.set_config_value()`
  - All 20+ examples updated to use param API consistently

- **Rationale:**
  - **Consistency:** One API for all user-facing code
  - **Validation:** Even runtime state benefits from type checking
  - **Best practices:** Examples should show the recommended way, not internal implementation
  - **Future-proof:** If config API becomes truly private, examples won't break

- **Internal framework use only:**
  - Low-level `config.set_config_value()` remains for internal framework use
  - CLI layer, config persistence, internal state management
  - Not exposed in examples or documentation as recommended practice

- **Documentation (Step 16):**
  - Clarify: "Use param API for all application code"
  - Note: "Config API is for internal framework use"
  - Examples:
    - ✅ Param API: `spafw37.set_param('loop-counter', count)` in cycle action
    - ❌ Config API: `config.set_config_value('loop-counter', count)` - internal only
  - Migration guide: Replace all `set_config_value()` with `set_param()` in application code

[↑ Back to top](#table-of-contents)

## Success Criteria

- [ ] All 18 implementation steps completed
- [ ] All examples updated and working
- [ ] All documentation updated
- [ ] All tests passing with 80%+ coverage
- [ ] No regressions in existing functionality
- [ ] Deprecation warnings work correctly
- [ ] New param API exported through `core.py`
- [ ] Migration guide in CHANGELOG.md
- [ ] Issue #27 closed

[↑ Back to top](#table-of-contents)

## Implementation Changes

This section documents significant deviations from the original implementation plan that were discovered or decided during implementation.

### API Simplification: Unified `get_param()` Instead of Typed Getters

**Original Plan:** Step 10 specified six typed getters (`get_param_str()`, `get_param_int()`, `get_param_bool()`, `get_param_float()`, `get_param_list()`, `get_param_dict()`), each accepting name, bind_name, or alias with type coercion logic.

**Actual Implementation:** Created a single unified `get_param()` function that automatically routes to the appropriate typed getter based on `PARAM_TYPE` from the parameter definition.

**Rationale:**
- **Simpler user API:** Users call one function (`get_param()`) instead of remembering which typed getter matches their parameter
- **Automatic type handling:** The framework knows the parameter type from its definition, so users don't need to specify it
- **Reduced API surface:** From 6 typed functions to 1 unified function in the public API
- **Internal typed getters preserved:** All original typed getters (`_get_param_str()`, `_get_param_int()`, etc.) remain as private helpers with full validation and coercion logic
- **Backward compatibility maintained:** All functionality from Step 10 implemented, just organized differently

**Code Changes:**
- Created `get_param()` in `param.py` that resolves parameter and dispatches to private typed getters
- Renamed all typed getters to private (`_get_param_str()`, `_get_param_int()`, etc.)
- Exposed only `get_param()`, `set_param()`, and `join_param()` through `core.py` facade
- Updated all examples to use unified `get_param()` instead of typed variants
- Updated all documentation to demonstrate unified API

**Benefits:**
- **User experience:** "Just call `get_param('database-host')`" instead of "Remember to use `get_param_str()` for text params"
- **Type safety:** Framework enforces correct type based on definition
- **Maintainability:** One public function to document and support
- **Flexibility:** Internal typed getters still available for framework use

**Documentation Impact:**
- All examples show `spafw37.get_param(param_name, default)` pattern
- Parameter API section simplified to three core functions instead of eight
- Migration guide updated to show config getters → unified `get_param()`

### Documentation Version Summaries Added

**Original Plan:** Step 16 specified updating documentation with new API examples and migration guides, but did not include version-specific change summaries.

**Actual Implementation:** Added "Version Changes" sections to all 8 documentation files after the Overview section, tailored to each file's subject matter.

**Rationale:**
- **User navigation:** Helps users quickly understand what's new in v1.1.0 for each topic area
- **Contextual documentation:** Changes described in the context of the specific feature (parameters, commands, cycles, etc.)
- **Discoverability:** Version information immediately visible after reading Overview
- **Structured history:** Establishes pattern for documenting changes in future versions

**Implementation Details:**
- Added "## Version Changes" section to all documentation files:
  - `api-reference.md`: Parameter API simplification details
  - `parameters.md`: Simplified parameter access and manipulation
  - `configuration.md`: New Parameter API and legacy API deprecation
  - `commands.md`: Parameter access in command actions
  - `cycles.md`: Parameter access in cycle functions
  - `phases.md`: Parameter access in phase commands
  - `logging.md`: Notes no changes (stable API)
  - `README.md`: Comprehensive v1.1.0 overview

- Updated Table of Contents in all files to include "Version Changes" entry

- Standardized "Key Capabilities" section naming across all documentation files

**Benefits:**
- **Version awareness:** Users immediately understand what version introduced which features
- **Migration clarity:** Clear documentation of what changed and why
- **Professional documentation:** Industry-standard practice for versioned APIs
- **Future-proofing:** Template for documenting v1.2.0, v2.0.0, etc.

### Documentation Structure Improvements

**Original Plan:** Step 16 focused on API migration examples and replacing config API references with param API.

**Actual Implementation:** Beyond API updates, improved documentation structure and consistency:

**Changes Made:**
1. **Consistent section naming:** Standardized "Key Capabilities" heading across all documentation files (previously mixed "Key Features"/"Key Capabilities")
2. **ToC updates:** Added "Version Changes" and "Key Capabilities" entries to all Table of Contents
3. **Overview clarity:** Simplified Overview sections to focus on core concepts before diving into version changes
4. **Version marker accuracy:** Fixed incorrect v1.2.0 markers (changed to v1.1.0) throughout documentation

**Benefits:**
- **Consistency:** Professional, consistent structure across all documentation
- **Navigation:** Complete and accurate Table of Contents in every file
- **Clarity:** Clear separation between timeless concepts (Overview) and version-specific changes (Version Changes)
- **Accuracy:** Version markers correctly reflect development timeline

### Multiple File Inputs for List Parameters

**Original Plan:** Step 6 mentioned `@file` loading but didn't explicitly address multiple file inputs in a single parameter occurrence (e.g., `--files @list1.txt @list2.txt @list3.txt`).

**Actual Implementation:** Enhanced CLI file handling to support multiple `@file` arguments for list parameters in a single occurrence.

**Rationale:**
- **User convenience:** Users can specify multiple file lists in one command: `--files @batch1.txt @batch2.txt @batch3.txt`
- **Consistency:** Matches expected behavior - all files loaded and combined into one list
- **CLI responsibility:** File loading is entirely a CLI concern; `param.py` remains ignorant of file loading mechanism

**Code Changes:**
- Moved file loading (`@file` detection and content loading) earlier in `capture_param_values()` loop
- Extracted list argument processing into `_process_list_argument()` helper for clarity
- Continue loop after processing each file argument for list params instead of returning early
- Updated function docstring to document multiple file reference support

**Test Coverage:**
- Added `test_capture_param_values_list_param_multiple_file_references()` to verify behavior
- Test validates three separate files are loaded, contents split on whitespace, and combined into single list
- All 97 existing CLI tests continue to pass

**Benefits:**
- **Better UX:** `--files @a.txt @b.txt @c.txt` works as users would expect
- **Architectural correctness:** File handling stays in CLI layer, param layer unaware
- **Maintainability:** Clean separation of concerns with focused helper function

### Advanced Parameter Input Filtering and Dict Enhancements

**Original Plan:** Steps 1 and 4 specified basic type validation for dict parameters with JSON parsing, but did not include advanced input filtering or enhanced dict handling capabilities.

**Actual Implementation:** Added `PARAM_TEXT_FILTER` configuration and comprehensive dict parameter enhancements including multi-block merging, file references within JSON, and sophisticated quote normalization.

#### PARAM_TEXT_FILTER: Customizable Input Processing

**Functionality:**
- **Configurable text processing:** Each parameter can define custom input filter function via `PARAM_TEXT_FILTER` key in parameter definition
- **Applied before validation:** Filter runs on raw string input before type validation/coercion
- **Type-specific defaults:** Framework provides default filters for each param type (e.g., `_default_filter_dict()` for dict params)
- **User override capability:** Applications can provide custom filters for specialized parsing needs

**Implementation:**
- Added `PARAM_TEXT_FILTER` constant to `constants/param.py`
- Integrated filter application in `join_param_value()` before validation
- Created `_default_filter_dict()` with quote normalization and JSON parsing
- Filter receives raw string value, returns processed value ready for validation

**Use Cases:**
- **Dict params:** Normalize shell-friendly `{'key':'value'}` to valid JSON `{"key":"value"}`
- **List params:** Custom delimiter handling beyond default whitespace splitting
- **Text params:** Input sanitization, format conversion, template expansion
- **Custom formats:** Domain-specific parsing (e.g., connection strings, DSL syntax)

**Example:**
```python
def custom_csv_filter(value):
    """Split CSV input and trim whitespace."""
    return [item.strip() for item in value.split(',')]

param.add_param({
    'name': 'tags',
    'type': 'list',
    'text-filter': custom_csv_filter  # Override default whitespace splitting
})
```

#### Enhanced Dict Parameter Handling

**Multi-Block Dict Merging:**
- **Multiple JSON objects:** Support `--config {"a":1} {"b":2}` syntax for merging multiple dict blocks
- **Intelligent splitting:** `_split_top_level_json_objects()` uses brace-depth tracking to identify top-level objects
- **Recursive processing:** Each detected block processed individually then merged via `join_param_value()`
- **Nested structure preservation:** Complex nested JSON like `{"users":[{"x":1}]}` correctly treated as single block
- **Array detection:** JSON arrays `[1,2,3]` correctly identified as non-dict for proper error reporting

**File References in JSON:**
- **Embedded @file syntax:** Support `{'data': @file.json}` for file references within JSON structures
- **Smart regex pattern:** `(?<!\w)@([^\s\}\]\),]+)` matches file refs but excludes email addresses
- **Delimiter awareness:** Stops at JSON structural characters `}`, `]`, `)`, `,` for correct path extraction
- **CLI layer responsibility:** `_parse_file_value()` handles file loading before param layer sees value
- **Multiple files:** Support multiple file refs in one value: `{"a": @file1.json, "b": @file2.json}`

**Quote Normalization:**
- **Shell-friendly syntax:** Accept single quotes `{'key':'value'}` in addition to standard JSON double quotes
- **Smart conversion:** `_normalize_json_quotes()` converts structural quotes while preserving apostrophes in strings
- **String delimiter tracking:** Maintains state to only convert quotes outside string literals
- **Escape handling:** Properly escapes internal quotes when converting: `'O'Brien'` → `"O\"Brien"`
- **Applied automatically:** All dict input normalized before JSON parsing via `_default_filter_dict()`

**Key Collision Handling:**
- **Default strategy:** Recent wins - later values override earlier ones when same key appears
- **Merge semantics:** Consistent with existing `DICT_OVERRIDE_RECENT` behavior from Step 1
- **Example:** `{"x":1} {"x":99}` → `{"x":99}` (second value wins)

**Implementation Details:**

1. **`_split_top_level_json_objects(text)`:**
   - Scans string character-by-character tracking brace/bracket depth
   - Only splits at depth 0 when complete object finished (brace closes)
   - Filters out non-object results (arrays, primitives) as single blocks
   - Returns list of JSON object strings for individual processing

2. **`_normalize_json_quotes(text)`:**
   - Iterates through string maintaining string delimiter state
   - Converts single quotes to double quotes only outside strings
   - Escapes existing double quotes found inside single-quoted strings
   - Preserves apostrophes in string values (e.g., `"don't"`)

3. **`_parse_file_value(value)`:**
   - Uses regex to find `@filepath` patterns while excluding `user@domain.com`
   - Negative lookbehind `(?<!\w)` ensures @ not preceded by word character
   - Character class `[^\s\}\]\),]` stops at whitespace and JSON delimiters
   - Calls `spafw37_file._read_file_raw()` to load each file
   - Returns value with all `@file` tokens replaced by file contents

4. **Multi-block detection in `join_param_value()`:**
   - Runs before input filter to catch multiple blocks early
   - Checks dict params: splits value if multiple top-level objects detected
   - Recursively calls `join_param_value()` for each block individually
   - Each block goes through full filter → validate → merge pipeline

**Test Coverage:**
- `test_dict_param_multiple_inline_json_objects()` - Multiple `{"a":1} {"b":2}` merging
- `test_dict_param_multiple_objects_with_key_collision()` - Override strategy validation
- `test_dict_param_complex_nested_json()` - Nested structures remain intact
- `test_parse_file_value_inside_json_structure()` - File refs within JSON objects
- `test_parse_file_value_ignores_email_addresses()` - Email address exclusion
- `test_parse_file_value_with_parentheses()` - Delimiter handling
- `test_dict_file_not_dict()` - Proper error for non-dict JSON (arrays)
- All 509 tests passing with 94.46% coverage

**Benefits:**
- **User flexibility:** Multiple ways to specify dict values (inline, files, mixed)
- **Shell ergonomics:** Single quotes work without escaping in shell commands
- **Composition:** Build complex configs from multiple sources naturally
- **Correctness:** Proper handling of nested JSON, arrays, file paths
- **Type safety:** Non-dict JSON (arrays, primitives) properly rejected with clear errors
- **Maintainability:** Clean separation - CLI handles files, param handles validation

---

## CHANGES for v1.1.0 Release

Issue #27: Pivot from Config Focus to Param Focus

### Issues Closed

- #27: Pivot from Config Focus to Param Focus

### Additions

- `get_param()` retrieves parameter value with automatic type conversion based on PARAM_TYPE field in parameter definition.
- `set_param()` stores parameter value after validating against parameter definition. Raises error if parameter not found or value invalid.
- `join_param()` adds to existing parameter value. Appends to lists, concatenates strings, merges dicts. Raises error for number and toggle types.
- `PARAM_JOIN_SEPARATOR` constant sets delimiter for string concatenation. Default is space character.
- `PARAM_DICT_MERGE_TYPE` constant controls whether dict merging recurses into nested dicts or only merges top-level keys.
- `PARAM_DICT_OVERRIDE_STRATEGY` constant determines which value wins when same key appears in multiple dicts being merged.
- `PARAM_INPUT_FILTER` constant specifies function to transform raw CLI input before type validation runs.
- Multiple JSON blocks in one parameter occurrence get merged.
- File reference syntax in JSON values loads file content.
- Multiple file references for list parameters load all files into one list.
- Parameters can be referenced by name, bind_name, or alias.

### Removals

These functions removed in v2.0.0 (emit deprecation warnings in v1.1.0):

- `get_config_value()`
- `get_config_str()`
- `get_config_int()`
- `get_config_bool()`
- `get_config_float()`
- `get_config_list()`
- `get_config_dict()`
- `set_config_value()`
- `set_config_list_value()`

### Changes

- Parameter getters consolidated from seven type-specific functions to single `get_param()` function.
- Parameter setters split into two functions: `set_param()` for replacement, `join_param()` for accumulation.

### Migration

- Change `get_config_str('key')` to `get_param('key')`
- Change `get_config_int('key', 0)` to `get_param('key', 0)`
- Change `set_config_value('key', value)` to `set_param(param_name='key', value=value)` for replacement
- Change `set_config_value('key', value)` to `join_param(param_name='key', value=value)` for accumulation

### Documentation

- `doc/parameters.md` added parameter API section
- `doc/configuration.md` clarified config vs param distinction
- `doc/commands.md` changed command implementation examples
- `doc/api-reference.md` added Parameter API section
- `doc/README.md` changed quick start examples
- `doc/cycles.md` changed cycle examples to param API
- `doc/phases.md` changed phase examples to param API
- `doc/logging.md` changed logging examples to param API
- `examples/params_join.py` demonstrates join operations
- `examples/params_input_filter.py` demonstrates input transformation
- 11 parameter examples changed
- 10+ command examples changed
- 3 cycle examples changed

### Testing

- 509 tests pass
- 94.46% code coverage
- New tests for parameter lookup by name, bind_name, and alias
- New tests for typed getters with coercion
- New tests for join operations (list, string, dict)
- Deprecated function backward compatibility tests
- No failures from existing test suite

---

Full changelog: https://github.com/minouris/spafw37/compare/v1.0.0...v1.1.0  
Issues: https://github.com/minouris/spafw37/issues/27
