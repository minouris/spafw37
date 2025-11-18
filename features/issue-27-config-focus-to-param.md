# Issue #27: Pivot from Config Focus to Param Focus

## Overview

Pivot from config dict access to param-focused interface with metadata-driven validation. Users will call `spafw37.set_param()` and `spafw37.get_param_str()` instead of config methods, enabling type validation on write and leveraging parameter metadata. All param logic moves to `param.py` with proper private/public separation, keeping `config.py` primitive. Includes deprecation wrappers for backward compatibility in v1.1.0 milestone.

**Key architectural decisions:**

- **Flexible param resolution:** Public API accepts params by name, bind_name, or alias with failover
- **Internal resolution helper:** `_resolve_param_definition()` encapsulates discovery logic
- **Separation of concerns:** CLI parses → param validates → config stores
- **Type-safe getters:** Typed getter functions with automatic coercion
- **Deprecation strategy:** Old APIs wrapped with warnings, removed in v2.0.0

## Implementation Steps

### 1. Add `PARAM_JOIN_SEPARATOR` constant

**File:** `src/spafw37/constants/param.py`

- Add new constant `PARAM_JOIN_SEPARATOR = 'join-separator'`
- Used in parameter definitions to specify string concatenation separator
- Defaults to `' '` (space) if not specified in param definition
- Used by `join_param_value()` when concatenating multiple string values
- Example: `PARAM_JOIN_SEPARATOR: ','` for CSV-style tags

### 2. Make internal `param.py` helpers private

**File:** `src/spafw37/param.py`

- Rename `get_bind_name()` → `_get_bind_name()`
- Rename `get_param_default()` → `_get_param_default()`
- Rename `param_has_default()` → `_param_has_default()`
- Update 30+ call sites across multiple files:
  - `param.py` internal calls
  - `cli.py` param binding references
  - `config_func.py` config key lookups
  - `help.py` parameter display logic
  - `cycle.py` cycle parameter handling

### 3. Create flexible param resolution system

**File:** `src/spafw37/param.py`

- **Rename metadata accessors to private:**
  - Rename `get_param_by_name()` → `_get_param_definition()`
  - Rename `get_param_by_alias()` → `_get_param_definition_by_alias()`
  - Update 20+ internal call sites in: `param.py`, `cli.py`, `config_func.py`, `help.py`
  - Create public backward-compat wrappers with deprecation warnings

- **Create `_resolve_param_definition()` helper:**
  - Flexible param resolution supporting three address spaces:
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

### 4. Extract type-specific validation helpers

**File:** `src/spafw37/param.py`

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
  - Accept dict directly (return as-is)
  - Handle @file references via `_load_json_file()`
  - Parse JSON strings starting with `{` via `_parse_json_text()`
  - Raise `ValueError` for invalid dict formats
- Create `_validate_text(value)`:
  - Pass-through, return value as-is
  - Simplest validator (text accepts anything)

### 5. Create `_validate_param_value()` orchestrator

**File:** `src/spafw37/param.py`

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

### 6. Refactor `_parse_value()` to delegate

**File:** `src/spafw37/param.py`

- Keep function signature unchanged for backward compatibility
- Become thin wrapper around `_validate_param_value()`
- Preserve CLI token structuring behavior:
  - List-joining for non-list params (already in `_validate_param_value()`)
  - Token normalization for CLI parsing
- Call `_validate_param_value(param, value, strict=True)` internally
- Function remains internal (`_` prefix)
- Used by existing callers during transition period

### 7. Add `set_param_value()` with flexible resolution

**File:** `src/spafw37/param.py`

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

### 8. Add `join_param_value()` with flexible resolution

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
  - `_join_dict_value(existing, new)`:
    - If existing is None/missing, return new dict
    - Shallow merge: `{**existing, **new}`
    - Last value wins for conflicting keys
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

### 10. Add typed param getters with flexible resolution

**File:** `src/spafw37/param.py`

- **Create base getter with flexible resolution:**

  ```python
  def get_param_value(param_name=None, bind_name=None, alias=None, default=None, strict=False):
  ```
  
  - Resolve param: `param_def = _resolve_param_definition(param_name, bind_name, alias)`
  - If not found and `strict=True`: raise `ValueError`
  - If not found and `strict=False`: return default
  - Get config key: `config_key = _get_bind_name(param_def)`
  - Retrieve from config: `config.get_config_value(config_key)`
  - Return raw value or default if missing

- **Create typed getters (all with flexible resolution):**
  
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

### 11. Export param API through `core.py` facade

**File:** `src/spafw37/core.py`

- Create `_deprecated(message)` decorator:
  - Use module-level set to track called functions (singleton pattern)
  - Log warning only once per deprecated function
  - Warning message includes function name and alternative
  - Example: `"get_config_str() is deprecated. Use get_param_str() instead. Will be removed in v2.0.0"`
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

### 14. Deprecate `config.set_config_list_value()`

**File:** `src/spafw37/config.py`

- Mark `set_config_list_value()` with `@_deprecated`:
  - Message: "Use join_param() for accumulation or set_param() for replacement. Will be removed in v2.0.0"
- Function replaced by:
  - `join_param()` for appending to lists (CLI use case)
  - `set_param()` for replacing entire list (user code use case)
- Keep function implementation for backward compatibility
- Remove usage from internal code (replaced by param API)

### 15. Update examples

**Files:** 20+ files in `examples/` directory

- Replace all config API calls with param API:
  - `spafw37.get_config_str()` → `spafw37.get_param_str()`
  - `spafw37.get_config_int()` → `spafw37.get_param_int()`
  - `spafw37.get_config_bool()` → `spafw37.get_param_bool()`
  - `spafw37.get_config_float()` → `spafw37.get_param_float()`
  - `spafw37.get_config_list()` → `spafw37.get_param_list()`
  - `spafw37.get_config_dict()` → `spafw37.get_param_dict()`
- Preserve direct `config.set_config_value()` in cycle examples:
  - `cycles_basic.py` - loop counter management
  - `cycles_loop_start.py` - loop state tracking
  - `cycles_nested.py` - nested loop variables
  - These are runtime state, not params (no validation needed)
- Add new example demonstrating `PARAM_JOIN_SEPARATOR`:
  - Create `examples/params_join_separator.py`
  - Show default space separator behavior
  - Show custom comma separator for CSV tags
  - Demonstrate `join_param()` usage
  - Example: `--tags python --tags cli --tags framework` → `"python,cli,framework"`

### 16. Update documentation

**Files:** `doc/parameters.md`, `doc/configuration.md`, `doc/commands.md`, `doc/api-reference.md`, `doc/README.md`

- `doc/parameters.md`:
  - Replace 18+ config API code examples with param API
  - Add `PARAM_JOIN_SEPARATOR` documentation:
    - Table entry in "Parameter Definition Constants" section
    - Usage examples showing default space separator
    - Usage examples showing custom separators (comma, pipe, newline)
  - Document `join_param()` vs `set_param()` semantics:
    - `set_param()` replaces entire value
    - `join_param()` accumulates/appends to existing value
    - Type-specific join behavior (list append, string concat, dict merge)
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

### 17. Update CHANGELOG.md

**File:** `CHANGELOG.md`

- Add v1.1.0 section with "Breaking Changes" subsection:
  - Title: "## [1.1.0] - 2025-11-XX"
  - Subsection: "### Breaking Changes"
- Document API pivot:
  - Explain shift from config-focused to param-focused API
  - Rationale: leverage parameter metadata for validation
  - Benefits: type safety, required param enforcement, cleaner semantics
- List deprecated methods with removal timeline:
  - `get_config_str/int/bool/float/list/dict()` → removed in v2.0.0
  - `set_config_value()` → removed in v2.0.0
  - `set_config_list_value()` → removed in v2.0.0
  - `config_func.set_config_value()` → removed in v2.0.0
  - `config_func.set_config_value_from_cmdline()` → removed in v2.0.0
- Provide migration examples:
  - Before: `spafw37.get_config_str('input-file')`
  - After: `spafw37.get_param_str('input-file')`
  - Before: `spafw37.set_config_value('count', 5)`
  - After: `spafw37.set_param('count', 5)`
  - Before: Multiple calls to build list
  - After: `spafw37.join_param('files', 'new.txt')`
- Document new features:
  - `strict` mode for getters (missing param and coercion error handling)
  - Type coercion in getters (string→int, int→string, etc.)
  - XOR validation moved to param layer (cleaner toggle handling)
  - `join_param()` for accumulation use cases
  - `PARAM_JOIN_SEPARATOR` for custom string concatenation
- Note backward compatibility:
  - Deprecation warnings logged on first call
  - Old API still works in v1.1.0
  - Allows gradual migration
  - Set `SPAFW37_SUPPRESS_DEPRECATION_WARNINGS` to silence warnings

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

## Further Considerations

### 1. Dict merge semantics for `join_param()`

When calling `join_param('config', {"a": 1})` then `join_param('config', {"b": 2})`:

- **Question:** Should result be `{"a": 1, "b": 2}` (shallow merge)?
- **Key conflicts:** What if calling `join_param('config', {"a": 1})` then `join_param('config', {"a": 2})`?
  - Option A: Last value wins → `{"a": 2}` (simplest, matches Python dict update)
  - Option B: First value wins → `{"a": 1}` (preserves initial state)
  - Option C: Raise error on conflict (strictest, prevents accidental overwrites)
- **Deep merge:** For nested dicts like `{"user": {"name": "Alice"}}`, should merge be deep or shallow?
  - Shallow: Entire `"user"` key replaced
  - Deep: Nested keys merged recursively (more complex, more useful?)
- **Recommendation:** Start with shallow merge, last-wins for conflicts, document clearly

### 2. Deprecation warning verbosity control

Current `@_deprecated` decorator logs once per function (singleton pattern).

- **Environment variable:** Add `SPAFW37_SUPPRESS_DEPRECATION_WARNINGS` to silence all warnings
  - Use case: Users who cannot migrate immediately (legacy codebases)
  - Check: `os.environ.get('SPAFW37_SUPPRESS_DEPRECATION_WARNINGS')` in decorator
- **Verbose mode:** Add `SPAFW37_DEPRECATION_WARNINGS=verbose` to log every call
  - Use case: Testing to ensure all deprecated calls found
  - Helps during migration to identify all usage points
- **Per-function control:** Consider programmatic API like `spafw37.suppress_deprecation_warnings(['get_config_str'])`
  - More granular than environment variable
  - Useful for gradual migration (suppress warnings for already-migrated code)

### 3. Type coercion failure messages

When `get_param_int('foo')` fails to coerce value and `strict=False`:

- **Silent fallback:** Current behavior, returns default without logging
  - Pro: No log noise
  - Con: Hides bugs (typos in param names, wrong types)
- **Warning log:** Log at WARNING level before returning default
  - Pro: Visible in logs for debugging
  - Con: Can be noisy if many coercions fail
- **Debug log:** Log at DEBUG level
  - Pro: Available when needed (verbose mode)
  - Con: Not visible by default
- **Recommendation:** Log at DEBUG level with message like `"Failed to coerce param 'foo' to int, returning default"`

### 4. String join edge cases

`PARAM_JOIN_SEPARATOR` edge cases:

- **Empty string separator:** If `PARAM_JOIN_SEPARATOR: ''`, should concatenate directly?
  - Example: `"hello"` + `"world"` → `"helloworld"`
  - Seems valid, document behavior
- **Whitespace separators:** Allow `\n`, `\t`, etc.?
  - Example: `PARAM_JOIN_SEPARATOR: '\n'` for multi-line text
  - Seems valid, document behavior
- **None separator:** If `PARAM_JOIN_SEPARATOR: None`, use default space?
  - Or treat as error?
  - Recommendation: Use default space
- **Multi-character separators:** Allow `", "` or `" | "`?
  - Seems valid, no technical limitation
  - Document examples

### 5. Private method testing approach

Current tests call `_parse_value()` directly (13 matches).

- **Option A:** Refactor tests to use public `set_param()` and `join_param()` APIs
  - Pro: Tests public behavior, less brittle
  - Con: Less granular, harder to test individual validation logic
- **Option B:** Keep testing private validation helpers directly
  - Pro: Better coverage of internal logic, easier to debug failures
  - Con: Tests tied to implementation details, brittle during refactoring
- **Option C:** Mix of both approaches
  - Public API tests for integration behavior
  - Private helper tests for edge cases and validation rules
  - Recommendation: Use this approach
- **Implementation:** Keep existing `_parse_value()` tests, add new public API tests

### 6. Flexible param resolution usage patterns

The `_resolve_param_definition()` helper enables three levels of specificity:

- **Failover mode (user-friendly):** `set_param_value('database', value='postgres')`
  - Tries param_name → bind_name → alias until match found
  - Best for interactive use and simple scripts
  - Risk: Ambiguity if same string exists in multiple address spaces
  
- **Named argument mode (explicit):** `set_param_value(bind_name='database_host', value='localhost')`
  - Only checks specified address space
  - Best for programmatic use where param identity is certain
  - Prevents unexpected matches from other address spaces
  
- **Mixed usage considerations:**
  - Framework code (cli.py, config_func.py) should use named arguments for clarity
  - Example code should use failover mode to demonstrate user-friendly API
  - Documentation should show both patterns with guidance on when to use each

**Recommendation:** Document both patterns with clear guidelines. Internal framework code uses named arguments, user-facing examples use failover mode.

### 7. Migration path for `set_config_list_value()` users

Current usage analysis:

- Cycle examples use `config.set_config_value()` for loop variables (runtime state)
- These are NOT params (no definition, no validation)
- Distinction: "param values" (validated, typed) vs "config values" (raw runtime state)

**Documentation needed:**

- When to use param API: For defined parameters with types and validation
- When to use config API: For runtime state that's not a parameter
- Examples:
  - Param: `--max-retries` defined with `PARAM_TYPE_NUMBER`
  - Config: `loop-counter` incremented during cycle execution (not a param)
- Keep low-level `config.set_config_value()` for runtime state management
- Document this distinction in `doc/configuration.md`

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
