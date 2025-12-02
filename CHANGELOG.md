# Changelog

## [1.1.0] - 2025-12-02

### Issues Closed

- #26: Add Parameter Unset Capability
- #27: Pivot from Config Focus to Param Focus
- #32: Switch Param Grouped Behaviour
- #33: Param Allowed Values
- #35: Add CYCLE_LOOP_END to Cycles
- #48: Param Defaults are set after pre-parse args

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

**Issue #32:**

- `SWITCH_UNSET` constant controls switch group behaviour. When set on `PARAM_SWITCH_CHANGE_BEHAVIOR`, causes other switches in the same group to be completely removed from configuration using `unset_param()`. Useful for mode switching where previous mode should be cleared.
- `SWITCH_RESET` constant controls switch group behaviour. When set on `PARAM_SWITCH_CHANGE_BEHAVIOR`, causes other switches in the same group to be reset to their default values using `reset_param()`. Useful when switches have meaningful default states that should be restored.
- `SWITCH_REJECT` constant controls switch group behaviour (default, backward compatible). When set on `PARAM_SWITCH_CHANGE_BEHAVIOR`, raises `ValueError` preventing the new switch param from being set if other switches in the group are already active. Matches current behaviour for strict validation.
- `PARAM_SWITCH_CHANGE_BEHAVIOR` property configures how switch params in the same group interact when values change. Accepts `SWITCH_UNSET`, `SWITCH_RESET`, or `SWITCH_REJECT` (default). Applied at parameter definition time in `add_param()`.

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

**Issue #48:**

- `cli._set_defaults()` function removed. Default-setting now occurs in `param.py` during parameter registration.

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

**Issue #48:**

- Default values for parameters are now set immediately when `add_param()` is called, rather than after pre-parsing during CLI execution.
- Pre-parse params with default values now correctly retain their pre-parsed values instead of being overridden.
- Added registration mode flag to temporarily modify switch param behavior during parameter registration, preventing false XOR conflicts when setting defaults.
- Switch conflict detection now checks registration mode and skips validation when `_SWITCH_REGISTER` behavior is active.
- **Bug fix:** `_has_switch_conflict()` now correctly checks the type of the conflicting parameter (not the parameter being set) when determining conflict logic for mixed-type switch groups (e.g., TEXT + TOGGLE params). This fixes false conflicts when setting non-toggle params that share switch groups with toggle params.
- Introduced internal constant `_SWITCH_REGISTER` in `param.py` to represent registration mode for switch param conflict detection. This constant is not part of the public API and is used only for internal implementation logic.

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

**Issue #32:**

- `doc/parameters.md` added "Switch Change Behaviour" section after "Mutual Exclusion (Switch Lists)" section. Documents `PARAM_SWITCH_CHANGE_BEHAVIOR` property with three behaviour options (`SWITCH_REJECT`, `SWITCH_UNSET`, `SWITCH_RESET`). Includes three complete examples demonstrating mode switching with `SWITCH_UNSET`, state restoration with `SWITCH_RESET`, and strict validation with `SWITCH_REJECT`. Each example shows parameter definitions and usage patterns with expected results.
- `doc/api-reference.md` added `PARAM_SWITCH_CHANGE_BEHAVIOR` to Parameter Properties table with description and version note (Added in v1.1.0).
- `doc/api-reference.md` added Switch Change Behaviour Constants section with definitions for `SWITCH_UNSET`, `SWITCH_RESET`, and `SWITCH_REJECT`, including when to use each constant.
- `examples/params_switch_behavior.py` demonstrates all three switch change behaviours with complete runnable examples. Shows mode switching use case (UNSET), state restoration use case (RESET), and strict validation use case (REJECT). Includes environment, region, port, size, and priority parameters with CLI commands.
- `examples/README.md` added `params_switch_behavior.py` entry in Parameters section.

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

**Issue #48:**

- No documentation changes required. This is an internal implementation fix with no user-facing API changes.

## [1.0.1] - 2025-11-15

Initial release

