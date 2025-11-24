# Changelog

## [1.1.0] - 2025-11-24

### Issues Closed

- #26: Add Parameter Unset Capability
- #27: Pivot from Config Focus to Param Focus
- #33: Param Allowed Values
- #35: Add CYCLE_LOOP_END to Cycles

### Additions

**Issue #26:**

- `unset_param()` removes parameter value completely from configuration. Raises error if parameter not found or is immutable.
- `reset_param()` restores parameter to default value. If no default exists, removes parameter value. Raises error if parameter not found or is immutable.
- `PARAM_IMMUTABLE` constant marks parameter as write-once. Initial assignment succeeds. Subsequent modifications, unsets, or resets raise error.
- `config.remove_config_value()` internal helper removes key from configuration dict.
- `config.has_config_value()` internal helper checks if key exists in configuration dict.
- `_check_immutable()` internal helper validates immutability before modifications.

**Issue #27:**

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

**Issue #33:**

- `PARAM_ALLOWED_VALUES` constant restricts TEXT, NUMBER, and LIST parameter values to predefined sets. For TEXT and LIST parameters, matching is case-insensitive with automatic normalisation to the canonical case from the allowed values list. Values not in the allowed list are rejected with clear error messages. Default values are validated and normalised at parameter registration time.
- `_normalise_text_to_allowed_case()` helper function performs case-insensitive matching against allowed values and returns the canonical case. Uses linear search through allowed values list for simplicity and low memory overhead.
- `_validate_allowed_values()` helper function validates that parameter value is in allowed values list. For TEXT parameters, performs case-insensitive matching. For LIST parameters, validates each element individually. For NUMBER parameters, performs exact match. Does not modify values - raises ValueError if validation fails.
- `_normalise_allowed_value()` helper function normalises validated values to canonical case. For TEXT parameters, returns canonical case from allowed values. For LIST parameters, returns list with each element normalised to canonical case. For NUMBER parameters, returns value unchanged. Should only be called after validation passes.
- `_TYPE_VALIDATORS` module-level dict maps parameter types to validation functions.

**Issue #35:**

- `CYCLE_LOOP_END` constant for defining function to run at end of each cycle iteration. Function runs after all cycle commands execute but before next loop condition check. Optional, same as `CYCLE_LOOP_START`.

### Removals

**Issue #27:**

- These functions removed in v2.0.0 (emit deprecation warnings in v1.1.0):
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

**Issue #26:**

- `set_param()` now checks immutability before allowing modifications.

**Issue #27:**

- Parameter getters consolidated from seven type-specific functions to single `get_param()` function.
- Parameter setters split into two functions: `set_param()` for replacement, `join_param()` for accumulation.

**Issue #33:**

- `_validate_param_value()` refactored to use `_TYPE_VALIDATORS` dict lookup instead of if-elif chain. Calls `_validate_allowed_values()` after type validation, then `_normalise_allowed_value()` to get canonical case values.
- `add_param()` validates that `PARAM_DEFAULT` is in `PARAM_ALLOWED_VALUES` when both are specified, then normalises and stores the canonical case default for TEXT and LIST parameters.

**Issue #35:**

- Cycle execution now calls `CYCLE_LOOP_END` function at end of each iteration if defined in cycle definition.

### Migration

**Issue #27:**

- Change `get_config_str('key')` to `get_param('key')`
- Change `get_config_int('key', 0)` to `get_param('key', 0)`
- Change `set_config_value('key', value)` to `set_param(param_name='key', value=value)` for replacement
- Change `set_config_value('key', value)` to `join_param(param_name='key', value=value)` for accumulation

### Documentation

**Issue #26:**

- `doc/parameters.md` added section on unsetting and resetting parameters
- `doc/parameters.md` added section on immutable parameters
- `doc/api-reference.md` added `unset_param()` documentation
- `doc/api-reference.md` added `reset_param()` documentation
- `doc/api-reference.md` added `PARAM_IMMUTABLE` constant
- `doc/api-reference.md` added quick reference tables for internal modules
- `examples/params_immutable.py` demonstrates write-once protection
- `examples/params_unset.py` demonstrates parameter lifecycle management

**Issue #27:**

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

**Issue #33:**

- `doc/parameters.md` added "Allowed Values" section with usage examples covering TEXT, NUMBER, and LIST parameters. Notes case-insensitive matching for TEXT and LIST.
- `doc/parameters.md` added `PARAM_ALLOWED_VALUES` to Parameter Definition Constants table, noting TEXT/NUMBER/LIST support and case-insensitivity.
- `doc/api-reference.md` added `PARAM_ALLOWED_VALUES` to Parameter Constants table, noting case-insensitive matching for TEXT/LIST.
- `README.md` added "Allowed Values Validation" to "What's New in v1.1.0" section, mentioning TEXT/NUMBER/LIST support and case-insensitive normalisation.
- `README.md` added `params_allowed_values.py` to examples list.
- `examples/README.md` added `params_allowed_values.py` entry.
- `examples/params_allowed_values.py` demonstrates usage with environment, region, port, size, and features parameters, including case-insensitive matching and LIST validation.

**Issue #35:**

- `doc/cycles.md` added `CYCLE_LOOP_END` to Cycle Constants table
- `doc/cycles.md` added Loop End Function section with examples
- `doc/cycles.md` updated Cycle Lifecycle section showing complete execution order
- `doc/cycles.md` added best practices for when to use `CYCLE_LOOP_END`
- `doc/api-reference.md` added `CYCLE_LOOP_END` constant documentation
- `examples/cycles_loop_end.py` demonstrates per-iteration cleanup and counter patterns
- `examples/README.md` updated with new example entry

## [1.0.1] - 2025-11-15

Initial release

