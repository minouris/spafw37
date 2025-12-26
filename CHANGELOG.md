# Changelog

## [1.1.0] - 2025-12-26

### Issues Closed

- #15: User Input Params
- #26: Add Parameter Unset Capability
- #27: Pivot from Config Focus to Param Focus
- #32: Switch Param Grouped Behaviour
- #33: Param Allowed Values
- #35: Add CYCLE_LOOP_END to Cycles
- #48: Param Defaults are set after pre-parse args
- #61: Refactor command.add_command() into focused helper methods

### Additions

**Issue #15:**

- *Constants in `src/spafw37/constants/param.py`:**
- `PARAM_PROMPT` - Prompt text to display when soliciting user input.
- `PARAM_PROMPT_HANDLER` - Custom handler function for parameter-specific prompt behaviour.
- `PARAM_PROMPT_TIMING` - Controls when prompts appear (start or command execution).
- `PARAM_PROMPT_REPEAT` - Controls repeat behaviour in cycles and multiple commands.
- `PARAM_SENSITIVE` - Boolean flag to suppress terminal echo for sensitive data.
- `PROMPT_ON_START` - Timing constant for prompting at application start.
- `PROMPT_ON_COMMAND` - Timing constant for prompting before specific commands.
- `PROMPT_ON_COMMANDS` - Property containing list of commands that trigger prompts.
- `PROMPT_REPEAT_NEVER` - Repeat behaviour constant for prompting only once.
- `PROMPT_REPEAT_IF_BLANK` - Repeat behaviour constant for prompting when value becomes blank.
- `PROMPT_REPEAT_ALWAYS` - Repeat behaviour constant for prompting every time.
- *Constants in `src/spafw37/constants/command.py`:**
- `COMMAND_PROMPT_PARAMS` - Command property for inline prompt parameter definitions.
- *Module `src/spafw37/input_prompt.py`:**
- `prompt_for_value()` function provides default terminal-based prompt handling using `input()` for regular parameters and `getpass.getpass()` for sensitive parameters, with support for multiple choice display and validation retry.
- *Functions in `src/spafw37/param.py`:**
- `set_prompt_handler()` function sets global prompt handler for all parameters.
- `_get_prompt_handler()` internal function resolves handler precedence (param-level → global → default).
- `_global_prompt_handler` module-level variable stores global prompt handler.
- `_prompted_params` module-level set tracks prompt history for `PROMPT_REPEAT_NEVER` behaviour.
- `_param_value_is_set()` internal function checks if parameter has a value (CLI override detection).
- `_timing_matches_context()` internal function verifies timing configuration matches execution context.
- `_should_prompt_param()` internal function orchestrates all prompt decision logic.
- `set_max_prompt_retries()` function configures maximum retry attempts for invalid input.
- `set_allowed_values()` function dynamically updates allowed values at runtime.
- *Integration in `src/spafw37/cli.py` and `src/spafw37/command.py`:**
- Prompt execution integrated at application start for `PROMPT_ON_START` timing.
- Prompt execution integrated before command execution for `PROMPT_ON_COMMAND` timing.
- `COMMAND_PROMPT_PARAMS` inline definitions processed during command registration.
- `PROMPT_ON_COMMANDS` property auto-populated from `COMMAND_REQUIRED_PARAMS`.
- Reciprocal `COMMAND_PROMPT_PARAMS` list built on commands for O(1) lookup.
- *Examples:**
- `examples/params_prompt_basic.py` - Basic parameter prompting with `PROMPT_ON_START` timing.
- `examples/params_prompt_timing.py` - Prompt timing control (`PROMPT_ON_START` vs `PROMPT_ON_COMMAND`).
- `examples/params_prompt_repeat.py` - Repeat behaviour modes (NEVER, IF_BLANK, ALWAYS).
- `examples/params_prompt_sensitive.py` - Sensitive parameter handling with suppressed echo.
- `examples/params_prompt_choices.py` - Multiple choice prompts with static and dynamic options.
- `examples/params_prompt_handlers.py` - Custom prompt handlers (global and per-param).
- `examples/params_prompt_validation.py` - Validation integration and retry logic.

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

**Issue #61:**

- `_validate_command_name()` internal function validates command has non-empty name during registration.
- `_validate_command_action()` internal function validates command has action function during registration.
- `_validate_command_references()` internal function validates no self-references or conflicting sequencing constraints.
- `_normalise_param_list()` internal function converts list of parameter definitions to parameter names (extracts loop logic to avoid nesting violations).
- `_process_inline_params()` internal function processes inline parameter definitions in `COMMAND_REQUIRED_PARAMS` and `COMMAND_TRIGGER_PARAM`.
- `_normalise_command_list()` internal function converts list of command definitions to command names (extracts loop logic to avoid nesting violations).
- `_process_inline_commands()` internal function processes inline command definitions in all dependency/sequencing fields.
- `_assign_command_phase()` internal function assigns default phase from config when not specified in command definition.
- `_store_command()` internal function stores command in registry and registers cycle if present.

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

**Issue #15:**

- Parameters can now solicit interactive user input at runtime using the `PARAM_PROMPT` property and associated timing/repeat controls.
- Prompts integrate with existing parameter validation, type handling, and required parameter checking.
- Prompts respect CLI-provided values (prompting skipped entirely if user already supplied value via `--param-name`).
- Multiple choice prompts automatically enabled when `PARAM_ALLOWED_VALUES` is present, displaying numbered options.
- Sensitive parameters suppress terminal echo and hide default values when `PARAM_SENSITIVE` is `True`.
- Custom prompt handlers supported via per-param `PARAM_PROMPT_HANDLER` property or global `set_prompt_handler()` method.
- Prompt timing controlled via `PARAM_PROMPT_TIMING` property with `PROMPT_ON_START` (at application start) or `PROMPT_ON_COMMAND` (before specific commands) options.
- Repeat behaviour in cycles controlled via `PARAM_PROMPT_REPEAT` property with `PROMPT_REPEAT_NEVER` (prompt once), `PROMPT_REPEAT_IF_BLANK` (prompt if blank), or `PROMPT_REPEAT_ALWAYS` (prompt every time) options.
- Commands can define prompt parameters inline using `COMMAND_PROMPT_PARAMS` field, consistent with existing inline definition patterns.
- `PROMPT_ON_COMMANDS` property automatically populated from `COMMAND_REQUIRED_PARAMS` if not explicitly set.
- Invalid input triggers re-prompting with error message displayed, up to configurable maximum retry limit (default 3 attempts).

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

**Issue #61:**

- `add_command()` function refactored from monolithic 54-line function to clean orchestrator that delegates to 7 focused helper functions.
- Command validation logic extracted into three focused validators for better testability and maintainability.
- Inline parameter processing logic extracted into separate helper with normalisation sub-helper to comply with nesting requirements.
- Inline command processing logic extracted into separate helper with normalisation sub-helper to comply with nesting requirements.
- Phase assignment logic extracted into dedicated helper for clarity.
- Command storage logic extracted into dedicated helper that encapsulates registry mutation and cycle registration.
- All helpers follow single-responsibility principle with clear naming and focused behaviour.
- Code nesting depth reduced throughout refactored implementation (max 2-level nesting maintained).

### Migration

**Issue #27:**

- Change `get_config_str('key')` to `get_param('key')`
- Change `get_config_int('key', 0)` to `get_param('key', 0)`
- Change `set_config_value('key', value)` to `set_param(param_name='key', value=value)` for replacement
- Change `set_config_value('key', value)` to `join_param(param_name='key', value=value)` for accumulation

### Documentation

**Issue #15:**

- `doc/parameters.md` - Added "Interactive Prompts" section with comprehensive usage guide covering basic usage, timing control, repeat behaviour, sensitive data, multiple choice, custom handlers, CLI override, inline definitions, and validation/retry. Updated Parameter Definition Constants table with new prompt-related constants. Updated Table of Contents to include new Interactive Prompts section with all subsections.
- `doc/api-reference.md` - Added documentation for `param.set_prompt_handler()`, `param.set_max_prompt_retries()`, and `param.set_allowed_values()` functions. Updated Table of Contents (if present) to include new API functions.
- `README.md` - Updated Features list with interactive parameter prompts entry. Added 7 new example files to Examples list. Added "What's New in v1.1.0" section with 6 bullet points covering prompt functionality.

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

**Issue #61:**

- No documentation changes required. This is an internal implementation refactoring with no user-facing API changes. All helpers are private (prefixed with `_`) and not part of the public API.

## [1.0.1] - 2025-11-15

Initial release

